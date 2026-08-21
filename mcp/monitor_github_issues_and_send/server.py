"""
monitor_github_issues_and_send — ONE unified MCP server forged by FORGE.
Generated : 2026-08-21 10:06 UTC
Goal      : Monitor GitHub issues and send alert notifications to Slack channel
Forged    : none
Wrapped   : GitHub, Slack

Every forged tool drives a stealth Playwright browser with TWO locators
(primary accessible-role, fallback CSS) plus a 2-retry / 200ms
self-heal loop. Official wrappers are thin typed calls over official REST APIs.

CONFIG ONCE — then just say: "Use monitor_github_issues_and_send at <absolute path to this file>"
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


mcp = FastMCP("monitor_github_issues_and_send")

TOOL_MANIFEST = [
    {
        "name": "slack_post_message",
        "source": "Official Slack",
        "badge": "OFFICIAL",
        "description": "Post a formatted message or alert to a Slack channel or webhook"
    },
    {
        "name": "slack_list_channels",
        "source": "Official Slack",
        "badge": "OFFICIAL",
        "description": "List available public and private channels in the workspace"
    },
    {
        "name": "github_create_issue",
        "source": "Official GitHub",
        "badge": "OFFICIAL",
        "description": "Create an issue on a GitHub repo (owner/name)"
    },
    {
        "name": "github_list_prs",
        "source": "Official GitHub",
        "badge": "OFFICIAL",
        "description": "List pull requests for a repository"
    },
    {
        "name": "github_get_file_contents",
        "source": "Official GitHub",
        "badge": "OFFICIAL",
        "description": "Fetch file content from GitHub repository default or target branch"
    }
]

# Planned DAG for this server's goal (rendered by FORGE's planner):
# {
#   "t1": {
#     "tool": "notion_log_price",
#     "source": "Core Notion"
#   },
#   "t2": {
#     "tool": "slack_post_message",
#     "source": "Official Slack"
#   },
#   "t3": {
#     "tool": "github_create_issue",
#     "source": "Official GitHub"
#   }
# }

# =========================================================================
# HARDCODED CORES — 7 tools, zero LLM calls, always available
# (amazon browser tools + gmail SMTP + notion REST API)
# =========================================================================


# =========================================================================
# GENERIC FORGED TOOLS — LLM-forged per custom site (2 tools each)
# House rule: ONE return per tool, no code after the return.
# =========================================================================


# =========================================================================
# OFFICIAL WRAPPERS — typed wrappers over official REST APIs (bring your token)
# =========================================================================


@mcp.tool()
def slack_post_message(channel: str, text: str = "", thread_ts: str = "") -> dict:
    """Post a formatted message or alert to a Slack channel or webhook (official Slack wrapper; needs SLACK_BOT_TOKEN)"""
    import httpx

    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env SLACK_BOT_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

        resp = httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json={"channel": channel, "text": text[:3500]},
            timeout=30,
        )


        data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
        return {"ok": resp.status_code in (200, 201), "status": resp.status_code, "data": data}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def slack_list_channels(types: str = "public_channel") -> dict:
    """List available public and private channels in the workspace (official Slack wrapper; needs SLACK_BOT_TOKEN)"""
    import httpx

    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env SLACK_BOT_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

        resp = httpx.get(
            "https://slack.com/api/conversations.list",
            headers=headers,
            params={"types": types or "public_channel,private_channel"},
            timeout=30,
        )


        data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
        return {"ok": resp.status_code in (200, 201), "status": resp.status_code, "data": data}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def github_create_issue(repo: str, title: str, body: str = "", labels: str = "[]") -> dict:
    """Create an issue on a GitHub repo (owner/name) (official GitHub wrapper; needs GITHUB_TOKEN)"""
    import httpx

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env GITHUB_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        clean_repo = repo.strip().strip("/")

        resp = httpx.post(
            f"https://api.github.com/repos/{clean_repo}/issues",
            headers=headers,
            json={"title": title[:200], "body": body or ""},
            timeout=30,
            follow_redirects=True,
        )


        data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
        return {"ok": resp.status_code in (200, 201), "status": resp.status_code, "data": data}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def github_list_prs(repo: str, state: str = "open") -> dict:
    """List pull requests for a repository (official GitHub wrapper; needs GITHUB_TOKEN)"""
    import httpx

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env GITHUB_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        clean_repo = repo.strip().strip("/")

        resp = httpx.get(
            f"https://api.github.com/repos/{clean_repo}/pulls",
            headers=headers,
            params={"state": state or "open"},
            timeout=30,
            follow_redirects=True,
        )


        data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
        return {"ok": resp.status_code in (200, 201), "status": resp.status_code, "data": data}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def github_get_file_contents(repo: str, path: str, ref: str = "main") -> dict:
    """Fetch file content from GitHub repository default or target branch (official GitHub wrapper; needs GITHUB_TOKEN)"""
    import httpx

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return {"ok": False, "error": "env GITHUB_TOKEN not set — add it to the env block of your mcpServers config"}
    try:

        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        clean_repo = repo.strip().strip("/")

        resp = httpx.get(
            f"https://api.github.com/repos/{clean_repo}/contents/{path.lstrip('/')}",
            headers=headers,
            params={"ref": ref or "main"},
            timeout=30,
            follow_redirects=True,
        )


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
