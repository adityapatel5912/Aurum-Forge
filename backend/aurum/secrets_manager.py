"""FORGE-AURUM Secrets & Token Vault Manager.

Allows entering API keys/tokens through the UI only.
Secrets are securely stored locally and injected directly into target IDE
configuration files (mcpServers[name].env) so the user never has to give tokens to the agent.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.paths import get_project_root, get_user_home

VAULT_FILE = ROOT / "mcp_registry" / "secrets_vault.json"
ENV_FILE = ROOT / ".env"

OFFICIAL_SECRET_DEFINITIONS = [
    {
        "service": "telegram",
        "name": "Telegram",
        "keys": [
            {
                "key": "TELEGRAM_BOT_TOKEN",
                "label": "Bot Token",
                "placeholder": "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ",
                "description": "Telegram Bot API Token from @BotFather",
                "required": True,
            },
            {
                "key": "TELEGRAM_CHAT_ID",
                "label": "Default Chat ID",
                "placeholder": "-100123456789 or @channel",
                "description": "Target chat, group, or channel ID",
                "required": False,
            },
        ],
    },
    {
        "service": "gmail",
        "name": "Gmail",
        "keys": [
            {
                "key": "GMAIL_USER",
                "label": "Gmail Address",
                "placeholder": "your.email@gmail.com",
                "description": "Your Google/Gmail email address",
                "required": True,
            },
            {
                "key": "GMAIL_APP_PASSWORD",
                "label": "App Password",
                "placeholder": "abcd efgh ijkl mnop",
                "description": "Google 16-character App Password (from Security > 2FA)",
                "required": True,
            },
        ],
    },
    {
        "service": "instagram",
        "name": "Instagram",
        "keys": [
            {
                "key": "INSTAGRAM_ACCESS_TOKEN",
                "label": "Graph API Access Token",
                "placeholder": "EAABwzLIXnjYBO...",
                "description": "Meta Graph API Long-Lived User Access Token",
                "required": True,
            },
            {
                "key": "INSTAGRAM_ACCOUNT_ID",
                "label": "Business Account ID",
                "placeholder": "17841400000000000",
                "description": "Instagram Professional / Creator Account ID",
                "required": False,
            },
        ],
    },
    {
        "service": "youtube",
        "name": "YouTube",
        "keys": [
            {
                "key": "YOUTUBE_API_KEY",
                "label": "Data API v3 Key",
                "placeholder": "AIzaSyD-1234567890abcdef...",
                "description": "Google Cloud YouTube Data API v3 Key",
                "required": True,
            },
        ],
    },
    {
        "service": "github",
        "name": "GitHub",
        "keys": [
            {
                "key": "GITHUB_TOKEN",
                "label": "Personal Access Token",
                "placeholder": "ghp_xxxxxxxxxxxxxxxxxxxx",
                "description": "GitHub PAT with repo / issues scope",
                "required": True,
            },
        ],
    },
    {
        "service": "notion",
        "name": "Notion",
        "keys": [
            {
                "key": "NOTION_TOKEN",
                "label": "Internal Integration Secret",
                "placeholder": "secret_xxxxxxxxxxxxxxxxxxxxxxxx",
                "description": "Notion Internal Integration Token",
                "required": True,
            },
        ],
    },
    {
        "service": "slack",
        "name": "Slack",
        "keys": [
            {
                "key": "SLACK_BOT_TOKEN",
                "label": "Bot User OAuth Token",
                "placeholder": "xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx",
                "description": "Slack Bot User OAuth Token (chat:write scope)",
                "required": True,
            },
        ],
    },
]


def _mask_value(val: str) -> str:
    if not val:
        return ""
    if len(val) <= 6:
        return "••••••"
    return val[:3] + "•" * (len(val) - 6) + val[-3:]


def load_vault_secrets() -> Dict[str, str]:
    """Load secrets from local vault file and environment."""
    secrets: Dict[str, str] = {}
    if VAULT_FILE.exists():
        try:
            secrets.update(json.loads(VAULT_FILE.read_text("utf-8")))
        except Exception:
            pass

    # Also check os.environ for existing tokens
    all_keys = [k["key"] for s in OFFICIAL_SECRET_DEFINITIONS for k in s["keys"]]
    for k in all_keys:
        env_val = os.environ.get(k)
        if env_val and not secrets.get(k):
            secrets[k] = env_val

    return secrets


def save_vault_secrets(new_secrets: Dict[str, str]) -> Dict[str, Any]:
    """Save user-entered secrets to vault file and update os.environ & .env."""
    current = load_vault_secrets()
    for k, v in new_secrets.items():
        if v is not None:
            v_str = str(v).strip()
            # If value contains masking bullets, don't overwrite with masked string
            if "••" not in v_str:
                if v_str:
                    current[k] = v_str
                    os.environ[k] = v_str
                elif k in current:
                    del current[k]
                    os.environ.pop(k, None)

    VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    VAULT_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False), "utf-8")

    # Update .env file if feasible
    _sync_env_file(current)

    return get_secrets_status()


def _sync_env_file(secrets: Dict[str, str]) -> None:
    """Sync secrets to .env file safely."""
    try:
        lines: List[str] = []
        existing_keys = set()
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text("utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k = line.split("=", 1)[0].strip()
                    if k in secrets:
                        lines.append(f"{k}={secrets[k]}")
                        existing_keys.add(k)
                        continue
                lines.append(line)

        for k, v in secrets.items():
            if k not in existing_keys and v:
                lines.append(f"{k}={v}")

        ENV_FILE.write_text("\n".join(lines) + "\n", "utf-8")
    except Exception:
        pass


def get_secrets_status() -> Dict[str, Any]:
    """Return UI-safe schema with masked values and configured statuses."""
    stored = load_vault_secrets()
    services_status = []
    total_keys = 0
    configured_keys = 0

    for svc in OFFICIAL_SECRET_DEFINITIONS:
        svc_keys = []
        svc_configured = True
        for k in svc["keys"]:
            total_keys += 1
            val = stored.get(k["key"], "")
            is_set = bool(val and len(val.strip()) > 0)
            if is_set:
                configured_keys += 1
            elif k.get("required"):
                svc_configured = False

            svc_keys.append({
                "key": k["key"],
                "label": k["label"],
                "placeholder": k["placeholder"],
                "description": k["description"],
                "required": k.get("required", False),
                "is_configured": is_set,
                "masked_value": _mask_value(val) if is_set else "",
            })

        services_status.append({
            "service": svc["service"],
            "name": svc["name"],
            "configured": svc_configured,
            "keys": svc_keys,
        })

    return {
        "ok": True,
        "total_services": len(OFFICIAL_SECRET_DEFINITIONS),
        "total_keys": total_keys,
        "configured_keys": configured_keys,
        "services": services_status,
        "badge": "AURUM ZERO-LEAK VAULT (#C6A96B)",
    }


def get_injection_env_block() -> Dict[str, str]:
    """Get active secrets dictionary for injection into IDE mcpServers config."""
    stored = load_vault_secrets()
    env_block = {
        "FORGE_HEADLESS": os.environ.get("FORGE_HEADLESS", "0"),
    }
    all_keys = [k["key"] for s in OFFICIAL_SECRET_DEFINITIONS for k in s["keys"]]
    for k in all_keys:
        if stored.get(k):
            env_block[k] = stored[k]
        else:
            # Provide clean placeholder
            env_block[k] = f"<your_{k.lower()}>"

    return env_block
