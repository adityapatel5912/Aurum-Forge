"""FORGE backend configuration: paths, model chains, provider endpoints, tuning knobs.

Single source of truth for where things live and which free-tier models to use.
Keys are read from ROOT/.env (Groq / Nvidia / Gemini / OpenRouter free tiers).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlsplit

# ------------------------------------------------------------------ paths --
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
LOGS_DIR = ROOT / "logs"
DIST_DIR = ROOT / "dist"
MCP_REGISTRY_DIR = ROOT / "mcp_registry"
SERVERS_DIR = MCP_REGISTRY_DIR / "servers"
UNIFIED_SERVER_DIR = SERVERS_DIR / "unified-mcp"
UNIFIED_SERVER_PY = UNIFIED_SERVER_DIR / "server.py"
REGISTRY_JSON = MCP_REGISTRY_DIR / "registry.json"
OFFICIAL_CATALOG_JSON = Path(__file__).resolve().parent / "registry" / "official_mcps.json"
TEMPLATES_DIR = Path(__file__).resolve().parent / "forge" / "templates"
LLM_CACHE_JSON = LOGS_DIR / "llm_cache.json"
LLM_DIAG_JSONL = LOGS_DIR / "llm_diagnostics.jsonl"

VERSION = "1.0.0"
SERVER_NAME = "unified-forge"


def ensure_dirs() -> None:
    for p in (LOGS_DIR, DIST_DIR, MCP_REGISTRY_DIR, UNIFIED_SERVER_DIR):
        p.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------- env ---
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:  # pragma: no cover - dotenv is optional
    pass


# ---------------------------------------------------------------- models ---
# provider/model-id chains. Order matters: first provider with a usable key wins.
# Chain per spec: Groq -> Nvidia -> Gemini -> OpenRouter, cached in logs/llm_cache.json
MODELS: dict[str, list[str]] = {
    "planner": [
        "groq/openai/gpt-oss-120b",
        "nvidia/nemotron-3-ultra-550b-a55b",
        "gemini/gemini-3.7-flash",
        "openrouter/google/gemma-4-31b-it:free",
    ],
    "codegen": [
        "nvidia/poolside/laguna-xs-2.1",
        "gemini/gemini-3.7-flash",
        "openrouter/google/gemma-4-31b-it:free",
        "groq/openai/gpt-oss-120b",
    ],
    "executor": [
        "groq/llama-3.1-8b-instant",
        "gemini/gemini-3.5-flash-lite",
        "openrouter/google/gemma-4-31b-it:free",
    ],
    "vision": [
        "gemini/gemini-3.7-flash",
        "nvidia/meta/muse-glimmer-30b",
    ],
}

PROVIDERS: dict[str, dict] = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_envs": ["GROQ_API_KEY"],
    },
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "key_envs": ["NVIDIA_API_KEY"],
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_envs": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_envs": ["OPENROUTER_API_KEY"],
    },
}


# ------------------------------------------------------------------ scout --
SCOUT_HEADFUL_DEFAULT = os.getenv("FORGE_HEADFUL", "1") == "1"
SCOUT_INITIAL_WAIT_MS = 2000        # settle wait after goto
SCOUT_SCROLL_STEPS = 4             # human-ish scrolls
SCOUT_SCROLL_DELAY_MS = 1000       # 1s between scrolls
SCOUT_MAX_ELEMENTS = 60

# ------------------------------------------------------------------ heal ---
HEAL_RETRIES = 2                    # healer retries
HEAL_DELAY_MS = 200                 # 200ms between fallback attempts
LOCATOR_TIMEOUT_MS = 4000

# ------------------------------------------------------------ llm budgets --
# per-role wall-clock budget; a slow provider falls through to the next one
ROLE_TIMEOUT_S = {
    "planner": 30.0,
    "codegen": 30.0,
    "executor": 20.0,
    "vision": 30.0,
}

# --------------------------------------------------------------- helpers ---
_TLD_DROP = {"com", "org", "net", "io", "ai", "co", "in", "dev", "app", "xyz", "me", "gg", "edu", "gov"}


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return url
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", url):
        url = "https://" + url
    return url.rstrip("/")


def site_slug(url: str) -> str:
    """https://example.com -> example | https://news.ycombinator.com -> news_ycombinator"""
    host = urlsplit(normalize_url(url)).netloc.split(":")[0].lower()
    host = host[4:] if host.startswith("www.") else host
    parts = [p for p in host.split(".") if p]
    if len(parts) > 1 and parts[-1] in _TLD_DROP:
        parts = parts[:-1]
    slug = "_".join(re.sub(r"[^a-z0-9]", "", p) for p in parts).strip("_")
    if not slug or not slug[0].isalpha():
        slug = "site_" + (slug or "x")
    return slug


def site_label(url: str) -> str:
    host = urlsplit(normalize_url(url)).netloc.split(":")[0].lower()
    return host[4:] if host.startswith("www.") else host


def ident(name: str, fallback: str = "tool") -> str:
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", (name or "").strip()).strip("_").lower()
    if not s:
        return fallback
    if s[0].isdigit():
        s = "t_" + s
    return s
