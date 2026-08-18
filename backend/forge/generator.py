"""FORGE generator — Scout logs -> typed FastMCP tools -> ONE unified server.py.

Per custom site: ONE LLM call (nvidia/poolside/laguna-xs-2.1 via the chain)
returns 5 tools as a JSON *step list* (never raw Python — we validate and
render ourselves). Jinja2 merges forged tools + official wrappers into
unified_server.py.j2 with the two-locator self-heal pattern.

If the LLM chain is unavailable, a deterministic local forger produces 5
generic-but-real tools from the Scout capture, so FORGE always completes.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader

from backend.config import (
    HEAL_DELAY_MS,
    HEAL_RETRIES,
    LOCATOR_TIMEOUT_MS,
    SERVER_NAME,
    TEMPLATES_DIR,
    UNIFIED_SERVER_PY,
    UNIFIED_SERVER_DIR,
    VERSION,
    ensure_dirs,
    ident,
)
from backend.forge.cores import CORE_SOURCES, CORE_TOOL_MANIFEST

# --------------------------------------------------------------------- util
def _py_lit(value: Any) -> str:
    """JSON literal == valid Python literal for str/int/float/bool/None."""
    return json.dumps(value, ensure_ascii=False)


_TYPE_MAP = {
    "str": "str", "string": "str", "text": "str",
    "int": "int", "integer": "int", "number": "int",
    "float": "float", "double": "float",
    "bool": "bool", "boolean": "bool",
}

_ALLOWED_ACTIONS = {"goto", "wait", "fill", "click", "press", "select", "extract"}

_IDENT_RE = re.compile(r"^[A-Za-z_]\w*$")

_ROLE_CSS = {
    "searchbox": "input[type='search']",
    "textbox": "input[type='text']",
    "button": "button",
    "link": "a",
    "combobox": "select",
    "form": "form",
}


def _clamp(value, lo, hi, default):
    try:
        return max(lo, min(hi, int(value)))
    except Exception:
        return default


def _sanitize_description(text: str, fallback: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = text.replace("\\", "").replace('"""', "'").replace('"', "'")
    return (text[:220] or fallback)


def _signature(params: list[dict]) -> str:
    parts = []
    for p in params:
        seg = f"{p['name']}: {_TYPE_MAP.get(str(p.get('type', 'str')).lower(), 'str')}"
        if p.get("default") is not None:
            seg += f" = {_py_lit(p['default'])}"
        parts.append(seg)
    return ", ".join(parts)


def _step_kwargs(step: dict, param_names: set[str], need_value: bool) -> str:
    """Build kwargs for _smart(...): role/name literals, *_param runtime refs, css always."""
    kwargs = []
    if step.get("role"):
        kwargs.append(f"role={_py_lit(str(step['role']))}")
    if step.get("name_param") and str(step["name_param"]) in param_names:
        kwargs.append(f"name={step['name_param']}")
    elif step.get("name"):
        kwargs.append(f"name={_py_lit(str(step['name']))}")
    css = step.get("css") or _ROLE_CSS.get(str(step.get("role", "")).lower(), "body")
    kwargs.append(f"css={_py_lit(str(css))}")
    if need_value:
        if step.get("value_param") and str(step["value_param"]) in param_names:
            kwargs.append(f"value={step['value_param']}")
        elif step.get("value") is not None:
            kwargs.append(f"value={_py_lit(str(step['value']))}")
    return ", ".join(kwargs)


def _render_lines(steps: list[dict], site_url: str, param_names: set[str]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        action = str(step.get("action", "")).lower()
        if action == "goto":
            url = step.get("url") or site_url
            if not str(url).startswith(("http://", "https://")):
                url = site_url
            lines.append(f"page.goto({_py_lit(str(url))}, wait_until=\"domcontentloaded\", timeout=30000)")
        elif action == "wait":
            lines.append(f"page.wait_for_timeout({_clamp(step.get('ms', 1500), 100, 15000, 1500)})")
        elif action in ("fill", "click", "press", "select"):
            lines.append(f"_smart(page, {_py_lit(action)}, {_step_kwargs(step, param_names, need_value=action in ('fill', 'press', 'select'))})")
        elif action == "extract":
            css = step.get("css") or "body"
            role = f", role={_py_lit(str(step['role']))}" if step.get("role") else ""
            name = f", name={_py_lit(str(step['name']))}" if step.get("name") else ""
            lines.append(f"return _extract(page, css={_py_lit(str(css))}{role}{name}, limit={_clamp(step.get('limit', 12), 1, 30, 12)})")
    return lines or [f"page.goto({_py_lit(site_url)}, wait_until=\"domcontentloaded\", timeout=30000)"]


def _single_return(lines: list[str], site_url: str) -> list[str]:
    """House rule: ONE return per tool, no code after the return."""
    for i, line in enumerate(lines):
        if line.lstrip().startswith("return"):
            return lines[: i + 1]
    return lines + ['return _extract(page, css="body", limit=12)']


def _finalize_tool(raw: dict, site_url: str, slug: str, used: set[str]) -> Optional[dict]:
    """Validate + sanitize one LLM-proposed tool into our render schema."""
    if not isinstance(raw, dict):
        return None
    name = ident(str(raw.get("name") or ""), "")
    if not name or not _IDENT_RE.match(name):
        return None
    base = name
    i = 2
    while name in used:
        name = f"{base}_{i}"
        i += 1

    params: list[dict] = []
    param_names: set[str] = set()
    for p in raw.get("params") or []:
        if not isinstance(p, dict):
            continue
        pname = ident(str(p.get("name") or ""), "")
        if not pname or pname in param_names or not _IDENT_RE.match(pname):
            continue
        if pname in ("page", "self", "mcp"):
            continue
        entry = {"name": pname, "type": _TYPE_MAP.get(str(p.get("type", "str")).lower(), "str")}
        if p.get("default") is not None:
            entry["default"] = p["default"]
        params.append(entry)
        param_names.add(pname)

    steps: list[dict] = []
    for s in raw.get("steps") or []:
        if not isinstance(s, dict):
            continue
        action = str(s.get("action", "")).lower()
        if action not in _ALLOWED_ACTIONS:
            continue
        if action in ("fill", "click", "press", "select") and not (s.get("role") or s.get("css")):
            continue
        if action == "goto" and s.get("url") and not str(s["url"]).startswith(("http://", "https://")):
            continue
        clean = {k: v for k, v in s.items() if v not in (None, "", [])}
        steps.append(clean)
    if not steps:
        return None
    # every tool starts at the site
    if not steps or steps[0].get("action") != "goto":
        steps.insert(0, {"action": "goto", "url": site_url})

    used.add(name)
    return {
        "name": name,
        "description": _sanitize_description(raw.get("description"), f"Forged tool for {slug}"),
        "params": params,
        "signature": _signature(params),
        "lines": _single_return(_render_lines(steps, site_url, param_names), site_url),
    }


# ------------------------------------------------------- deterministic forge
def _pick(elements: list[dict], roles: tuple[str, ...], name_regex: str = "") -> Optional[dict]:
    rx = re.compile(name_regex, re.IGNORECASE) if name_regex else None
    for el in elements:
        if el.get("role") in roles and (not rx or rx.search(str(el.get("name", "")) or el.get("text", ""))):
            return el
    for el in elements:
        if el.get("role") in roles:
            return el
    return None


def deterministic_tools(site_log: dict, used: set[str]) -> list[dict]:
    """5 generic-but-real tools built straight from Scout's two-locator capture."""
    slug = site_log["slug"]
    url = site_log["url"]
    elements = site_log.get("elements") or []

    search_input = _pick(elements, ("searchbox",), r"search|query|^q$") or _pick(elements, ("textbox",), r"search|query|^q$")
    search_button = _pick(elements, ("button",), r"search|go|submit|find")
    any_button = _pick(elements, ("button",))
    any_input = search_input or _pick(elements, ("textbox",))

    inp = {
        "role": (search_input or {}).get("role", "searchbox"),
        "name": (search_input or {}).get("name") or "Search",
        "css": (search_input or {}).get("css") or "input[type='search']",
    }
    btn = {
        "role": "button",
        "name": (search_button or any_button or {}).get("name") or "Search",
        "css": (search_button or any_button or {}).get("css") or "button[type='submit']",
    }

    def mk(name_hint: str) -> str:
        name = ident(f"{name_hint}_{slug}")
        base, i = name, 2
        while name in used:
            name = f"{base}_{i}"
            i += 1
        used.add(name)
        return name

    specs = [
        {
            "name": mk("search"),
            "description": f"Open {site_log['site']}, type a query into the search box and return the results page text.",
            "params": [{"name": "query", "type": "str"}, {"name": "limit", "type": "int", "default": 10}],
            "steps": [
                {"action": "goto", "url": url},
                {"action": "wait", "ms": 1500},
                {"action": "fill", **inp, "value_param": "query"},
                {"action": "click", **btn},
                {"action": "wait", "ms": 2000},
                {"action": "extract", "css": "body", "limit": 12},
            ],
        },
        {
            "name": mk("read_page"),
            "description": f"Open {site_log['site']} and return the main readable page content.",
            "params": [{"name": "limit", "type": "int", "default": 8}],
            "steps": [
                {"action": "goto", "url": url},
                {"action": "wait", "ms": 2000},
                {"action": "extract", "css": "body", "limit": 12},
            ],
        },
        {
            "name": mk("click_element"),
            "description": f"Open {site_log['site']} and click the button whose visible text matches element_text (role locator first, CSS fallback).",
            "params": [{"name": "element_text", "type": "str"}],
            "steps": [
                {"action": "goto", "url": url},
                {"action": "wait", "ms": 1500},
                {"action": "click", "role": "button", "name_param": "element_text", "css": btn["css"]},
                {"action": "wait", "ms": 1200},
                {"action": "extract", "css": "body", "limit": 8},
            ],
        },
        {
            "name": mk("fill_field"),
            "description": f"Open {site_log['site']} and type a value into its main input field, then press Enter.",
            "params": [{"name": "value", "type": "str"}],
            "steps": [
                {"action": "goto", "url": url},
                {"action": "wait", "ms": 1500},
                {"action": "fill", "role": inp["role"], "name": inp["name"], "css": inp["css"], "value_param": "value"},
                {"action": "press", "role": inp["role"], "name": inp["name"], "css": inp["css"], "value": "Enter"},
                {"action": "wait", "ms": 1800},
                {"action": "extract", "css": "body", "limit": 10},
            ],
        },
        {
            "name": mk("extract_links"),
            "description": f"Open {site_log['site']} and return the visible links on the page.",
            "params": [{"name": "limit", "type": "int", "default": 15}],
            "steps": [
                {"action": "goto", "url": url},
                {"action": "wait", "ms": 1500},
                {"action": "extract", "role": "link", "css": "a", "limit": 15},
            ],
        },
    ]
    out = []
    for spec in specs:
        param_names = {p["name"] for p in spec["params"]}
        out.append(
            {
                "name": spec["name"],
                "description": spec["description"],
                "params": spec["params"],
                "signature": _signature(spec["params"]),
                "lines": _single_return(_render_lines(spec["steps"], url, param_names), url),
            }
        )
    return out


# --------------------------------------------------------------- LLM forge
_CODEGEN_SYSTEM = (
    "You are FORGE's codegen module. You design FastMCP browser tools as JSON "
    "step-lists (a compiler renders them into Python — never emit Python code). "
    "Reply with ONLY valid JSON. No markdown fences, no prose."
)


def _codegen_user(site_log: dict, goal: str) -> str:
    elements = [
        {k: el.get(k) for k in ("role", "name", "css", "tag", "type")}
        for el in (site_log.get("elements") or [])[:25]
    ]
    return f"""GOAL: {goal}

SITE: {site_log['site']} ({site_log['url']})
TOOL NAME PREFIX: {site_log['slug']}_ (every tool name must start with it)

SCOUT CAPTURE (two locators per element: role+name primary, css fallback):
{json.dumps(elements, ensure_ascii=False, indent=1)}

Generate EXACTLY 2 typed FastMCP tools as a JSON array. Each tool:
{{
  "name": "search_{site_log['slug']}",
  "description": "one line",
  "params": [{{"name": "query", "type": "str"}}, {{"name": "limit", "type": "int", "default": 10}}],
  "steps": [ ... ]
}}

Allowed steps (use 4-7 per tool):
  {{"action": "goto", "url": "{site_log['url']}"}}
  {{"action": "wait", "ms": 1500}}
  {{"action": "fill", "role": "searchbox", "name": "Search", "css": "input[type='search']", "value_param": "query"}}
  {{"action": "click", "role": "button", "name": "Search", "css": "button.search"}}
  {{"action": "press", "role": "searchbox", "name": "Search", "css": "input[type='search']", "value": "Enter"}}
  {{"action": "select", "role": "combobox", "name": "Filter", "css": "select", "value_param": "option"}}
  {{"action": "extract", "css": "body", "limit": 12}}

RULES:
- Tool 1 MUST be the site search flow (fill the search input, click the search button, extract results).
- Tool 2 MUST be one more useful flow for the GOAL (read/extract, submit, filter...).
- Every locator step MUST have BOTH the role+name primary locator AND a css fallback locator (use the SCOUT CAPTURE).
- Every tool must end with exactly one extract step (single return).
- value_param / name_param must reference names of that tool's params.
- types allowed: str, int, float, bool."""


def forge_site(site_log: dict, goal: str, llm=None) -> tuple[list[dict], dict]:
    """One LLM call per site -> 2 typed tools (validated), deterministic fallback."""
    used: set[str] = set()
    tools: list[dict] = []
    meta: dict = {"role": "codegen", "provider": None, "model": None, "cached": False, "tried": []}

    if llm is not None:
        text, meta = llm.chat(
            _CODEGEN_SYSTEM, _codegen_user(site_log, goal), temperature=0.2, max_tokens=2500
        )
        from backend.llm import extract_json

        raw = extract_json(text or "")
        if isinstance(raw, dict) and isinstance(raw.get("tools"), list):
            raw = raw["tools"]
        if isinstance(raw, list):
            for item in raw[:2]:
                tool = _finalize_tool(item, site_log["url"], site_log["slug"], used)
                if tool:
                    tools.append(tool)

    for extra in deterministic_tools(site_log, used):
        if len(tools) >= 2:
            break
        tools.append(extra)
    return tools[:2], meta


# ------------------------------------------------------------------ render
def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        autoescape=False,
    )


def _site_context(site_log: dict, tools: list[dict]) -> dict:
    return {
        "slug": site_log["slug"],
        "label": site_log["site"],
        "url": site_log["url"],
        "tools": tools,
    }


def render_unified_server(
    goal: str,
    site_logs: list[dict],
    site_tools: list[list[dict]],
    officials: list[dict],
    dag: Optional[dict] = None,
    server_name: Optional[str] = None,
    out_dir: Optional[Any] = None,
) -> tuple[str, list[dict], str]:
    """Render a unified FastMCP server.py.

    By default writes to mcp_registry/servers/unified-mcp/server.py. When
    ``server_name``/``out_dir`` are provided (Factory mode), writes to the
    per-MCP directory so every forge gets its own isolated server + SKILL.md.

    officials: flattened entries from registry.resolve_officials(), each with
    tool_name/description/params/name/kind/token_env.
    Returns (source, manifest, written_path). Falls back to deterministic-only
    tools if the LLM-flavored render does not compile.
    """
    ensure_dirs()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    active_name = server_name or SERVER_NAME
    target_dir = Path(out_dir) if out_dir else UNIFIED_SERVER_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "server.py"

    def build(llm_tools_allowed: bool) -> str:
        custom_sites = []
        for site_log, tools in zip(site_logs, site_tools):
            if not llm_tools_allowed:
                tools = deterministic_tools(site_log, set())[:2]
            custom_sites.append(_site_context(site_log, tools))

        manifest: list[dict] = [dict(entry) for entry in CORE_TOOL_MANIFEST]
        for site in custom_sites:
            for t in site["tools"]:
                manifest.append(
                    {
                        "name": t["name"],
                        "source": f"Custom {site['label']} Forged",
                        "badge": "FORGED",
                        "description": t["description"],
                    }
                )
        for o in officials:
            manifest.append(
                {
                    "name": o["tool_name"],
                    "source": f"Official {o['name']}",
                    "badge": "OFFICIAL",
                    "description": o["description"],
                }
            )

        dag_lines = json.dumps(dag or {}, indent=2, ensure_ascii=False).splitlines()
        dag_comment = "\n".join("# " + ln for ln in dag_lines) or "# (no dag)"

        off_entries = [
            {
                **o,
                "signature": _signature(o.get("params") or []),
            }
            for o in officials
        ]

        context = {
            "server_name": active_name,
            "generated_at": generated_at,
            "goal": goal or "(no goal given)",
            "site_labels": ", ".join(s["label"] for s in custom_sites) or "none",
            "official_labels": ", ".join(sorted({o["name"] for o in off_entries})) or "none",
            "cores": [{"source": src} for src in CORE_SOURCES],
            "custom_sites": custom_sites,
            "officials": off_entries,
            "tool_manifest": json.dumps(manifest, indent=4, ensure_ascii=False),
            "dag_comment": dag_comment,
            "heal_retries": HEAL_RETRIES,
            "heal_delay_ms": HEAL_DELAY_MS,
            "locator_timeout_ms": LOCATOR_TIMEOUT_MS,
            "version": VERSION,
        }
        return _jinja_env().get_template("unified_server.py.j2").render(**context), manifest

    source, manifest = build(llm_tools_allowed=True)
    try:
        compile(source, str(target_path), "exec")
    except SyntaxError:
        source, manifest = build(llm_tools_allowed=False)
        compile(source, str(target_path), "exec")  # must compile — deterministic is trusted

    target_path.write_text(source, "utf-8")
    return source, manifest, str(target_path)


def render_single_site_server(goal: str, site_log: dict, tools: list[dict]) -> tuple[str, str]:
    """Single-site variant (server.py.j2) -> mcp_registry/servers/{slug}-mcp/server.py."""
    out_dir = UNIFIED_SERVER_DIR.parent / f"{site_log['slug']}-mcp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "server.py"
    context = {
        "server_name": f"{site_log['slug']}-mcp",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "goal": goal or "(no goal given)",
        "site_labels": site_log["site"],
        "custom_sites": [_site_context(site_log, tools)],
        "heal_retries": HEAL_RETRIES,
        "heal_delay_ms": HEAL_DELAY_MS,
        "locator_timeout_ms": LOCATOR_TIMEOUT_MS,
        "all_tool_names": json.dumps([t["name"] for t in tools]),
    }
    source = _jinja_env().get_template("server.py.j2").render(**context)
    compile(source, str(out_path), "exec")
    out_path.write_text(source, "utf-8")
    return source, str(out_path)
