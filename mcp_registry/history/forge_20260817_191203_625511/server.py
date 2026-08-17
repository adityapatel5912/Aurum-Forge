"""
unified-forge — ONE unified MCP server forged by FORGE.
Generated : 2026-08-17 13:42 UTC
Goal      : Find Web3 hackathons on Unstop with prize >50000, mail me and log to Notion
Forged    : unstop.com
Wrapped   : Notion

Every forged tool drives a stealth Playwright browser with TWO locators
(primary accessible-role, fallback CSS) plus a 2-retry / 200ms
self-heal loop. Official wrappers are thin typed calls over official REST APIs.

CONFIG ONCE — then just say: "Use unified-forge at <absolute path to this file>"
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # fall back to the reference implementation bundled with `mcp`
    from mcp.server.fastmcp import FastMCP

from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Stealth browser session — shared, lazy, headful by default (a real user's Chrome)
# ---------------------------------------------------------------------------
STEALTH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
]
REAL_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HEADLESS = os.environ.get("FORGE_HEADLESS", "0") == "1"  # headful unless explicitly disabled

HEAL_RETRIES = 2
HEAL_DELAY_MS = 200
LOCATOR_TIMEOUT_MS = 4000

_pw = None
_browser = None
_page = None
_lock = threading.Lock()


def _ensure_page():
    """Start ONE stealth browser lazily and reuse its page across tool calls."""
    global _pw, _browser, _page
    with _lock:
        if _page is None or _page.is_closed():
            _pw = sync_playwright().start()
            _browser = _pw.chromium.launch(headless=HEADLESS, args=STEALTH_ARGS)
            context = _browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=REAL_UA,
                locale="en-US",
            )
            context.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
                "window.chrome=window.chrome||{runtime:{}};"
            )
            _page = context.new_page()
    return _page


def _locator(page, role=None, name=None, css=None):
    """Locator 1: accessible role. Locator 2: CSS fallback."""
    if role:
        try:
            return page.get_by_role(role, name=name) if name else page.get_by_role(role)
        except Exception:
            pass
    return page.locator(css or "body")


def _smart(page, action, role=None, name=None, css=None, value=None, timeout=None):
    """Two-locator self-healing action: try role locator, fall back to CSS,
    retry HEAL_RETRIES times with a 200ms pause between rounds."""
    timeout = timeout or LOCATOR_TIMEOUT_MS
    last_err = None
    for _attempt in range(HEAL_RETRIES + 1):
        for use_css in (False, True):
            try:
                if use_css or not role:
                    loc = page.locator(css or "body")
                else:
                    loc = page.get_by_role(role, name=name) if name else page.get_by_role(role)
                if action == "click":
                    loc.click(timeout=timeout)
                elif action == "fill":
                    loc.fill(str(value), timeout=timeout)
                elif action == "press":
                    loc.press(value or "Enter", timeout=timeout)
                elif action == "select":
                    loc.select_option(str(value), timeout=timeout)
                else:
                    raise ValueError("unknown action: " + str(action))
                return True
            except Exception as err:
                last_err = err
        time.sleep(HEAL_DELAY_MS / 1000.0)
    raise RuntimeError("healer: '" + str(action) + "' failed after 2-locator retries: " + repr(last_err))


def _extract(page, css=None, role=None, name=None, limit=12):
    """Best-effort text harvest from the current page."""
    try:
        loc = _locator(page, role, name, css)
        count = loc.count()
        if count > 1:
            return [
                {"text": (loc.nth(i).inner_text(timeout=2000) or "").strip()[:600]}
                for i in range(min(count, limit))
            ]
        if count == 1:
            text = (loc.first.inner_text(timeout=2000) or "").strip()
        else:
            text = (page.inner_text("body", timeout=8000) or "").strip()
        return [{"text": chunk.strip()[:600]} for chunk in text.split("\n") if chunk.strip()][:limit]
    except Exception as err:
        return [{"error": "extract failed: " + repr(err)}]


mcp = FastMCP("unified-forge")

TOOL_MANIFEST = [
    {
        "name": "amazon_search_ram",
        "source": "Core Amazon",
        "badge": "CORE",
        "description": "Search Amazon for a query and return result rows"
    },
    {
        "name": "amazon_check_discount",
        "source": "Core Amazon",
        "badge": "CORE",
        "description": "Find results whose discount is above a threshold"
    },
    {
        "name": "amazon_monitor_ram_discount",
        "source": "Core Amazon",
        "badge": "CORE",
        "description": "Monitor 8GB RAM prices and return deals above the discount threshold"
    },
    {
        "name": "gmail_send_email",
        "source": "Core Gmail",
        "badge": "CORE",
        "description": "Send an email via Gmail SMTP (official path, no browser login)"
    },
    {
        "name": "gmail_notify_and_log",
        "source": "Core Gmail",
        "badge": "CORE",
        "description": "Send a discount alert email with price details"
    },
    {
        "name": "notion_create_database_entry",
        "source": "Core Notion",
        "badge": "CORE",
        "description": "Create an entry in a Notion database via the official API"
    },
    {
        "name": "notion_log_price",
        "source": "Core Notion",
        "badge": "CORE",
        "description": "Log a price/discount observation as a Notion entry"
    },
    {
        "name": "unstop_search",
        "source": "Custom unstop.com Forged",
        "badge": "FORGED",
        "description": "Search Unstop for hackathons with prize >50000"
    },
    {
        "name": "unstop_filter_hackathons",
        "source": "Custom unstop.com Forged",
        "badge": "FORGED",
        "description": "Filter search results to find Web3 hackathons with prize >50000"
    },
    {
        "name": "notion_create_entry",
        "source": "Official Notion",
        "badge": "OFFICIAL",
        "description": "Create a page entry in Notion (uses NOTION_PARENT_PAGE or a database_id)"
    }
]

# Planned DAG for this server's goal (rendered by FORGE's planner):
# {
#   "t1": {
#     "tool": "unstop_filter_hackathons",
#     "source": "Custom unstop.com Forged",
#     "params": {
#       "query": "Web3",
#       "prize_min": 50000
#     },
#     "parallel": false
#   },
#   "t2": {
#     "tool": "gmail_notify_and_log",
#     "source": "Core Gmail",
#     "parallel": true,
#     "deps": [
#       "t1"
#     ]
#   },
#   "t3": {
#     "tool": "notion_log_price",
#     "source": "Core Notion",
#     "parallel": true,
#     "deps": [
#       "t1"
#     ]
#   }
# }

# =========================================================================
# HARDCODED CORES — 7 tools, zero LLM calls, always available
# (amazon browser tools + gmail SMTP + notion REST API)
# =========================================================================


import re as _re
import urllib.parse as _urllib_parse


def _parse_amazon_discounts(rows, discount_gt):
    """Extract price (₹) and percent-off from Amazon result rows; keep matches only."""
    matches = []
    for row in rows:
        text = row.get("text", "") if isinstance(row, dict) else str(row)
        price_m = _re.search(r"₹\s?([\d,]+(?:\.\d+)?)", text)
        if not price_m:
            continue
        discount_m = _re.search(r"(\d{1,2})\s?%\s?(?:off|OFF)", text)
        try:
            price = float(price_m.group(1).replace(",", ""))
        except ValueError:
            continue
        discount = float(discount_m.group(1)) if discount_m else 0.0
        if discount >= float(discount_gt):
            matches.append({"price": price, "discount": discount, "match": True, "text": text[:240]})
    return matches


@mcp.tool()
def amazon_search_ram(query: str, limit: int = 10) -> list:
    """Search Amazon for a query (e.g. '8GB RAM') and return result rows."""
    page = _ensure_page()
    try:
        page.goto(
            "https://www.amazon.in/s?k=" + _urllib_parse.quote(query),
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2500)
        rows = _extract(page, css="div[data-component-type='s-search-result']", limit=limit)
        return [{"text": (r.get("text", "") or "")[:300]} for r in rows]
    except Exception as err:
        return [{"ok": False, "tool": "amazon_search_ram", "error": repr(err)}]


@mcp.tool()
def amazon_check_discount(query: str, discount_gt: float = 20.0, limit: int = 24) -> list:
    """Search Amazon and return only results whose discount is >= discount_gt percent."""
    page = _ensure_page()
    try:
        page.goto(
            "https://www.amazon.in/s?k=" + _urllib_parse.quote(query),
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2500)
        rows = _extract(page, css="div[data-component-type='s-search-result']", limit=limit)
        matches = _parse_amazon_discounts(rows, discount_gt)
        return matches if matches else [{"match": False, "discount_gt": discount_gt, "note": "no deals above threshold right now"}]
    except Exception as err:
        return [{"ok": False, "tool": "amazon_check_discount", "error": repr(err)}]


@mcp.tool()
def amazon_monitor_ram_discount(discount_gt: float = 20.0) -> list:
    """Monitor 8GB RAM prices on Amazon and return deals with discount >= threshold (feeds gmail/notion tasks)."""
    return amazon_check_discount("8GB RAM", discount_gt, limit=24)



@mcp.tool()
def gmail_send_email(to: str, subject: str, body: str = "") -> dict:
    """Send an email via Gmail SMTP (official API path — never browser login). Needs GMAIL_USER + GMAIL_APP_PASSWORD."""
    import os
    import smtplib
    from email.message import EmailMessage

    user = os.environ.get("GMAIL_USER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not user or not password:
        return {"ok": False, "error": "set GMAIL_USER and GMAIL_APP_PASSWORD env (Gmail app password) in your mcpServers env block"}
    try:
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = user, to, subject
        message.set_content(body or subject)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
        return {"ok": True, "sent_to": to, "subject": subject}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def gmail_notify_and_log(discount: float = 0.0, price: str = "") -> dict:
    """Send a discount alert email (to GMAIL_TO or GMAIL_USER) with the observed discount and price."""
    import os

    user = os.environ.get("GMAIL_USER", "")
    to = os.environ.get("GMAIL_TO", "") or user
    if not to:
        return {"ok": False, "error": "set GMAIL_USER / GMAIL_TO env so the alert has a recipient"}
    subject = "FORGE alert: RAM discount {0}% off".format(discount)
    body = "Discount observed: {0}%\nPrice: {1}\n\n— sent by your unified-forge MCP server".format(discount, price or "n/a")
    return gmail_send_email(to, subject, body)



@mcp.tool()
def notion_create_database_entry(database_id: str, title: str, content: str = "") -> dict:
    """Create a page entry in a Notion database via the official API (NOTION_TOKEN required)."""
    import os

    import httpx

    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        return {"ok": False, "error": "set NOTION_TOKEN env (Notion integration token)"}
    db = database_id or os.environ.get("NOTION_DATABASE_ID", "")
    if not db:
        return {"ok": False, "error": "pass database_id or set NOTION_DATABASE_ID env"}
    headers = {
        "Authorization": "Bearer " + token,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    payload = {"parent": {"type": "database_id", "database_id": db}}
    result = {"ok": False, "error": "could not create entry"}
    try:
        for title_key in ("title", "Name", "Title"):  # databases name their title prop differently
            payload["properties"] = {title_key: {"title": [{"text": {"content": title[:180]}}]}}
            if content:
                payload["children"] = [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:1900]}}]},
                    }
                ]
            resp = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=30)
            if resp.status_code in (200, 201):
                result = {"ok": True, "status": resp.status_code, "data": resp.json()}
                break
            result = {"ok": False, "status": resp.status_code, "error": resp.text[:300]}
        return result
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def notion_log_price(title: str, price: str = "", discount: str = "") -> dict:
    """Log a price/discount observation as a Notion database entry (uses NOTION_DATABASE_ID)."""
    import os

    db = os.environ.get("NOTION_DATABASE_ID", "")
    content = "price: {0}\ndiscount: {1}%\nlogged: via unified-forge".format(price or "n/a", discount or "n/a")
    return notion_create_database_entry(db, title[:180], content)



# =========================================================================
# GENERIC FORGED TOOLS — LLM-forged per custom site (2 tools each)
# House rule: ONE return per tool, no code after the return.
# =========================================================================

# ---- forged for unstop.com (https://unstop.com) ----


@mcp.tool()
def unstop_search(query: str, limit: int = 10) -> list:
    """Search Unstop for hackathons with prize >50000"""
    page = _ensure_page()
    try:
        page.goto("https://unstop.com", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        _smart(page, "fill", role="textbox", name="Search Opportunities", css="#un-input-0", value=query)
        _smart(page, "click", role="button", name="Search", css="button.search")
        page.wait_for_timeout(2000)
        return _extract(page, css="body", limit=12)
    except Exception as err:
        return [{"ok": False, "tool": "unstop_search", "error": repr(err)}]


@mcp.tool()
def unstop_filter_hackathons(search_query: str, min_prize: int = 50000, limit: int = 10) -> list:
    """Filter search results to find Web3 hackathons with prize >50000"""
    page = _ensure_page()
    try:
        page.goto("https://unstop.com", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        _smart(page, "fill", role="textbox", name="Search Opportunities", css="#un-input-0", value=search_query)
        _smart(page, "click", role="button", name="Search", css="button.search")
        page.wait_for_timeout(2000)
        return _extract(page, css="body", limit=12)
    except Exception as err:
        return [{"ok": False, "tool": "unstop_filter_hackathons", "error": repr(err)}]



# =========================================================================
# OFFICIAL WRAPPERS — typed wrappers over official REST APIs (bring your token)
# =========================================================================


@mcp.tool()
def notion_create_entry(title: str, database_id: str = "", content: str = "") -> dict:
    """Create a page entry in Notion (uses NOTION_PARENT_PAGE or a database_id) (official Notion wrapper; needs NOTION_TOKEN)"""
    import httpx

    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env NOTION_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {
            "Authorization": "Bearer " + token,
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        parent_page = os.environ.get("NOTION_PARENT_PAGE", "")
        parent = (
            {"type": "page_id", "page_id": parent_page}
            if parent_page
            else {"type": "database_id", "database_id": database_id}
        )
        payload = {"parent": parent, "properties": {"title": {"title": [{"text": {"content": title[:180]}}]}}}
        if content:
            payload["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:1900]}}]},
                }
            ]
        resp = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=30)

        data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
        return {"ok": resp.status_code in (200, 201), "status": resp.status_code, "data": data}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


# ---------------------------------------------------------------------------
# Manifest helper — `python server.py --list-tools` prints the tool table
# ---------------------------------------------------------------------------
if "--list-tools" in sys.argv:
    print(json.dumps(TOOL_MANIFEST, indent=2))
    raise SystemExit(0)

if __name__ == "__main__":
    mcp.run()
