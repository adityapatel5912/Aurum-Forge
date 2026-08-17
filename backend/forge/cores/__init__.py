"""HARDCODED CORES — 7 tools injected into every unified server in <2s, zero LLM calls.

- amazon_core : 3 browser tools (search / check discount / monitor RAM discount)
- gmail_core  : 2 SMTP tools (send email / notify-and-log)
- notion_core : 2 REST tools (create database entry / log price)

Each core module exposes a SOURCE string (complete, authored Python — one return
per tool, no dead code) that the Jinja template embeds in the CORES section of
the generated server.py.
"""
from backend.forge.cores.amazon_core import AMAZON_CORE_SOURCE
from backend.forge.cores.gmail_core import GMAIL_CORE_SOURCE
from backend.forge.cores.notion_core import NOTION_CORE_SOURCE

CORE_SOURCES = [AMAZON_CORE_SOURCE, GMAIL_CORE_SOURCE, NOTION_CORE_SOURCE]

CORE_TOOL_MANIFEST = [
    {"name": "amazon_search_ram", "source": "Core Amazon", "badge": "CORE", "description": "Search Amazon for a query and return result rows"},
    {"name": "amazon_check_discount", "source": "Core Amazon", "badge": "CORE", "description": "Find results whose discount is above a threshold"},
    {"name": "amazon_monitor_ram_discount", "source": "Core Amazon", "badge": "CORE", "description": "Monitor 8GB RAM prices and return deals above the discount threshold"},
    {"name": "gmail_send_email", "source": "Core Gmail", "badge": "CORE", "description": "Send an email via Gmail SMTP (official path, no browser login)"},
    {"name": "gmail_notify_and_log", "source": "Core Gmail", "badge": "CORE", "description": "Send a discount alert email with price details"},
    {"name": "notion_create_database_entry", "source": "Core Notion", "badge": "CORE", "description": "Create an entry in a Notion database via the official API"},
    {"name": "notion_log_price", "source": "Core Notion", "badge": "CORE", "description": "Log a price/discount observation as a Notion entry"},
]

CORE_TOOL_NAMES = {t["name"] for t in CORE_TOOL_MANIFEST}

# Sites fully covered by a core module — no scouting / no LLM forging needed.
CORE_SITE_IDS = {"amazon"}

__all__ = [
    "CORE_SOURCES",
    "CORE_TOOL_MANIFEST",
    "CORE_TOOL_NAMES",
    "CORE_SITE_IDS",
]
