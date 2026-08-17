"""Scout explorer — visits a never-seen site headfully and captures elements.

For every interactive element it records TWO locators:
  * Primary   -> accessible role, e.g. page.get_by_role("button", name="Search")
  * Fallback  -> CSS selector,      e.g. page.locator("button.search")

Output is logs/{slug}.json:  {url, site, slug, mode, title, elements: [...]}
If no browser is available, a virtual scout falls back to plain-HTTP HTML
parsing (or a generic template offline) so the pipeline always completes.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from typing import Optional

from backend.config import (
    LOGS_DIR,
    SCOUT_INITIAL_WAIT_MS,
    SCOUT_MAX_ELEMENTS,
    SCOUT_SCROLL_DELAY_MS,
    SCOUT_SCROLL_STEPS,
    ensure_dirs,
    normalize_url,
    site_label,
    site_slug,
)

CAPTURE_JS = """
() => {
  const SEL = 'a[href], button, input, select, textarea, form, [role="button"], [role="searchbox"], [role="textbox"], [role="link"], [role="combobox"]';
  const seen = new Set();
  const out = [];

  function roleOf(el) {
    const explicit = el.getAttribute('role');
    if (explicit) return explicit;
    const tag = el.tagName.toLowerCase();
    if (tag === 'a') return 'link';
    if (tag === 'button') return 'button';
    if (tag === 'select') return 'combobox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'form') return 'form';
    if (tag === 'input') {
      const t = (el.getAttribute('type') || 'text').toLowerCase();
      if (t === 'search') return 'searchbox';
      if (t === 'submit' || t === 'button' || t === 'reset') return 'button';
      if (t === 'checkbox') return 'checkbox';
      if (t === 'radio') return 'radio';
      return 'textbox';
    }
    return 'generic';
  }

  function nameOf(el) {
    const n = (el.getAttribute('aria-label') || el.getAttribute('name') ||
               el.getAttribute('placeholder') || el.getAttribute('title') ||
               el.getAttribute('value') || (el.innerText || '').split('\\n')[0] || '').trim();
    return n.replace(/\\s+/g, ' ').slice(0, 60);
  }

  function cssPath(el) {
    if (el.id && /^[A-Za-z][-A-Za-z0-9_]*$/.test(el.id)) return '#' + el.id;
    const tag = el.tagName.toLowerCase();
    const cls = (typeof el.className === 'string' ? el.className : '').trim()
      .split(/\\s+/).filter(Boolean).filter(c => c.length < 40).slice(0, 2);
    if (cls.length) return tag + '.' + cls.map(c => (window.CSS && CSS.escape) ? CSS.escape(c) : c).join('.');
    let n = 1, sib = el.previousElementSibling;
    while (sib) { if (sib.tagName === el.tagName) n++; sib = sib.previousElementSibling; }
    return tag + ':nth-of-type(' + n + ')';
  }

  function score(el, role, name) {
    const nl = name.toLowerCase();
    if (role === 'searchbox') return 100;
    if (role === 'textbox' && /search|query|q/.test(nl)) return 95;
    if (role === 'combobox') return 80;
    if (role === 'button' && /search|go|submit/.test(nl)) return 78;
    if (role === 'button') return 60;
    if (role === 'link') return 40;
    if (role === 'form') return 30;
    return 10;
  }

  for (const el of document.querySelectorAll(SEL)) {
    const rects = el.getClientRects();
    if (!rects.length) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || parseFloat(st.opacity || '1') < 0.05) continue;
    const role = roleOf(el);
    const name = nameOf(el);
    const css = cssPath(el);
    const key = role + '|' + name + '|' + css;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({
      role, name, css, score: score(el, role, name),
      tag: el.tagName.toLowerCase(),
      type: (el.getAttribute('type') || '').toLowerCase(),
      text: (el.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 100),
      href: (el.getAttribute('href') || '').slice(0, 200),
    });
  }
  out.sort((a, b) => b.score - a.score);
  return out.slice(0, """ + str(SCOUT_MAX_ELEMENTS) + """);
}
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def scout_site(
    url: str,
    headful: bool = True,
    out_dir=None,
) -> dict:
    """Scout one site; always writes logs/{slug}.json and returns the payload."""
    url = normalize_url(url)
    slug = site_slug(url)
    label = site_label(url)
    out_dir = out_dir or LOGS_DIR
    ensure_dirs()

    result = _scout_with_browser(url, slug, label, headful=headful)
    if result is None:
        result = _virtual_scout(url, slug, label)

    out_path = out_dir / f"{slug}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")
    result["log_path"] = str(out_path)
    return result


def _scout_with_browser(url: str, slug: str, label: str, headful: bool) -> Optional[dict]:
    try:
        from playwright.sync_api import sync_playwright

        from backend.scout.stealth import launch_stealth_browser, new_stealth_page

        with sync_playwright() as p:
            browser = launch_stealth_browser(p, headful=headful)
            try:
                page = new_stealth_page(browser)
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(SCOUT_INITIAL_WAIT_MS)  # 2s settle
                for _ in range(SCOUT_SCROLL_STEPS):           # human-ish scroll
                    page.mouse.wheel(0, 900)
                    page.wait_for_timeout(SCOUT_SCROLL_DELAY_MS)  # 1s delay
                try:
                    page.evaluate("window.scrollTo(0, 0)")
                except Exception:
                    pass
                elements = page.evaluate(CAPTURE_JS)
                title = page.title()
            finally:
                browser.close()

        if not elements:
            return None
        return {
            "url": url,
            "site": label,
            "slug": slug,
            "mode": "browser",
            "title": (title or label)[:200],
            "scanned_at": _now(),
            "elements": elements,
        }
    except Exception:
        return None


_TAG_RE = re.compile(r"<(a|button|input|select|textarea|form)\b([^>]*)>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')

_GENERIC_ELEMENTS = [
    {"role": "searchbox", "name": "Search", "css": "input[type='search']", "tag": "input", "type": "search", "text": "", "href": ""},
    {"role": "textbox", "name": "Query", "css": "input[name='q']", "tag": "input", "type": "text", "text": "", "href": ""},
    {"role": "button", "name": "Search", "css": "button[type='submit']", "tag": "button", "type": "submit", "text": "Search", "href": ""},
    {"role": "button", "name": "Submit", "css": "button", "tag": "button", "type": "", "text": "Submit", "href": ""},
    {"role": "link", "name": "Home", "css": "a", "tag": "a", "type": "", "text": "Home", "href": "/"},
    {"role": "combobox", "name": "Filter", "css": "select", "tag": "select", "type": "", "text": "", "href": ""},
    {"role": "form", "name": "Search form", "css": "form", "tag": "form", "type": "", "text": "", "href": ""},
]


def _virtual_scout(url: str, slug: str, label: str) -> dict:
    """No-browser fallback: plain HTTP fetch + regex element harvest."""
    mode = "virtual-offline"
    html = ""
    try:
        import httpx

        from backend.scout.stealth import REAL_UA

        resp = httpx.get(
            url, headers={"User-Agent": REAL_UA, "Accept": "text/html"}, timeout=20, follow_redirects=True
        )
        if resp.status_code == 200 and "<" in resp.text[:2000]:
            html = resp.text
            mode = "virtual-http"
    except Exception:
        html = ""

    elements: list[dict] = []
    if html:
        for m in _TAG_RE.finditer(html[:400000]):
            tag, attr_str = m.group(1).lower(), m.group(2)
            attrs = dict(_ATTR_RE.findall(attr_str))
            if tag == "input":
                itype = (attrs.get("type") or "text").lower()
                role = "searchbox" if itype == "search" else ("button" if itype in ("submit", "button", "reset") else "textbox")
                css = f"input[type='{itype}']" if attrs.get("type") else "input[type='text']"
            elif tag == "button":
                role, css = "button", "button"
            elif tag == "a":
                role, css = "link", "a"
            elif tag == "select":
                role, css = "combobox", "select"
            elif tag == "textarea":
                role, css = "textbox", "textarea"
            else:
                role, css = "form", "form"
            name = (
                attrs.get("aria-label") or attrs.get("name") or attrs.get("placeholder")
                or attrs.get("title") or attrs.get("value") or role.capitalize()
            )[:60]
            elements.append(
                {
                    "role": role,
                    "name": name,
                    "css": css,
                    "tag": tag,
                    "type": attrs.get("type", "").lower(),
                    "text": "",
                    "href": attrs.get("href", "")[:200],
                }
            )
            if len(elements) >= SCOUT_MAX_ELEMENTS:
                break

    if len(elements) < 5:
        have = {(e["role"], e["name"], e["css"]) for e in elements}
        for extra in _GENERIC_ELEMENTS:
            if (extra["role"], extra["name"], extra["css"]) not in have:
                elements.append(dict(extra))

    return {
        "url": url,
        "site": label,
        "slug": slug,
        "mode": mode,
        "title": label,
        "scanned_at": _now(),
        "elements": elements[:SCOUT_MAX_ELEMENTS],
    }
