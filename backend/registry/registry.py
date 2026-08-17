"""JSON registry for forged servers + the official MCP catalog.

MVP storage is a JSON file (mcp_registry/registry.json) per spec — no Postgres.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from backend.config import OFFICIAL_CATALOG_JSON, REGISTRY_JSON, ensure_dirs


class Registry:
    """Tiny JSON registry: register / list / get forged unified servers."""

    def __init__(self, path=None):
        self.path = path or REGISTRY_JSON

    def _load(self) -> dict:
        try:
            return json.loads(self.path.read_text("utf-8"))
        except Exception:
            return {"servers": []}

    def _save(self, data: dict) -> None:
        ensure_dirs()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(self.path)

    def register(self, entry: dict) -> dict:
        data = self._load()
        entry = {"created": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry}
        data["servers"] = [s for s in data["servers"] if s.get("name") != entry.get("name")]
        data["servers"].insert(0, entry)
        data["servers"] = data["servers"][:50]
        self._save(data)
        return entry

    def list_servers(self) -> list[dict]:
        return self._load()["servers"]

    def get(self, name: str) -> Optional[dict]:
        for s in self._load()["servers"]:
            if s.get("name") == name:
                return s
        return None


def load_official_catalog() -> list[dict]:
    try:
        data = json.loads(OFFICIAL_CATALOG_JSON.read_text("utf-8"))
        return data.get("officials", [])
    except Exception as err:
        raise RuntimeError(f"official catalog unreadable at {OFFICIAL_CATALOG_JSON}: {err}") from err


def resolve_officials(ids: list[str]) -> list[dict]:
    """Flatten selected catalog entries into wrapper descriptors (one per tool)."""
    catalog = {o["id"]: o for o in load_official_catalog()}
    flat: list[dict] = []
    for oid in ids or []:
        entry = catalog.get((oid or "").strip().lower())
        if not entry:
            continue
        for tool in entry.get("tools", []):
            flat.append(
                {
                    "id": entry["id"],
                    "name": entry["name"],
                    "kind": entry["kind"],
                    "token_env": entry["token_env"],
                    "tool_name": tool["tool_name"],
                    "description": tool["description"],
                    "params": tool.get("params", []),
                }
            )
    return flat
