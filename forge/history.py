"""FORGE History Storage & Registry Management.

Manages forge_registry.json (atomic writes) and mcp_registry/history/{id}/ archives.
"""
from __future__ import annotations

import json
import os
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import ROOT, MCP_REGISTRY_DIR, DIST_DIR, ensure_dirs

FORGE_REGISTRY_JSON = ROOT / "forge_registry.json"
HISTORY_DIR = MCP_REGISTRY_DIR / "history"

_history_lock = threading.Lock()


def ensure_history_dirs() -> None:
    ensure_dirs()
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def generate_history_id() -> str:
    """Generate unique history ID with microsecond resolution: forge_YYYYMMDD_HHMMSS_micros."""
    now = datetime.now()
    return f"forge_{now.strftime('%Y%m%d_%H%M%S')}_{now.strftime('%f')}"


def load_forge_registry() -> list[dict[str, Any]]:
    with _history_lock:
        if not FORGE_REGISTRY_JSON.exists():
            return []
        try:
            data = json.loads(FORGE_REGISTRY_JSON.read_text("utf-8"))
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []


def save_forge_registry(entries: list[dict[str, Any]]) -> None:
    """Atomic write to forge_registry.json using temp file replacement."""
    ensure_history_dirs()
    with _history_lock:
        tmp = FORGE_REGISTRY_JSON.with_suffix(f".tmp_{os.getpid()}")
        tmp.write_text(json.dumps(entries, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(FORGE_REGISTRY_JSON)


def record_history_entry(
    goal: str,
    mcp_name: str,
    server_path: str,
    tools: list[Any],
    dag: dict[str, Any] | None,
    skill_content: str,
    zip_path: str,
    server_py: str | None = None,
    history_id: str | None = None,
) -> dict[str, Any]:
    ensure_history_dirs()
    hid = history_id or generate_history_id()
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Extract tool names cleanly
    tool_names: list[str] = []
    for t in tools or []:
        if isinstance(t, str):
            tool_names.append(t)
        elif isinstance(t, dict):
            name = t.get("name") or t.get("tool_name")
            if name:
                tool_names.append(str(name))

    clean_server_path = str(server_path).replace("\\", "/")
    clean_zip_path = str(zip_path).replace("\\", "/")

    # Create history directory mcp_registry/history/{id}/
    target_hist_dir = HISTORY_DIR / hid
    target_hist_dir.mkdir(parents=True, exist_ok=True)

    # Copy / save files into target_hist_dir
    hist_server_file = target_hist_dir / "server.py"
    if server_py:
        hist_server_file.write_text(server_py, "utf-8")
    elif Path(server_path).exists():
        shutil.copy2(server_path, hist_server_file)

    hist_skill_file = target_hist_dir / "SKILL.md"
    hist_skill_file.write_text(skill_content, "utf-8")

    hist_zip_file = target_hist_dir / f"unified-mcp-{hid}.zip"
    if Path(zip_path).exists():
        shutil.copy2(zip_path, hist_zip_file)

    entry: dict[str, Any] = {
        "id": hid,
        "timestamp": now_iso,
        "goal": (goal or "Unified Forge Workflow").strip(),
        "mcp_name": mcp_name,
        "abs_path": clean_server_path,
        "tools": tool_names,
        "dag": dag or {},
        "skill_content": skill_content,
        "zip_path": str(hist_zip_file).replace("\\", "/"),
    }

    entries = load_forge_registry()
    # Deduplicate by id and prepend newest first
    entries = [e for e in entries if e.get("id") != hid]
    entries.insert(0, entry)
    save_forge_registry(entries)
    return entry


def get_all_history() -> list[dict[str, Any]]:
    return load_forge_registry()


def get_history_by_id(hid: str) -> dict[str, Any] | None:
    entries = load_forge_registry()
    for e in entries:
        if e.get("id") == hid:
            return e
    return None


def search_history(query: str) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return load_forge_registry()
    results = []
    for e in load_forge_registry():
        goal = str(e.get("goal", "")).lower()
        tools_str = " ".join(e.get("tools", [])).lower()
        mcp_name = str(e.get("mcp_name", "")).lower()
        eid = str(e.get("id", "")).lower()
        if q in goal or q in tools_str or q in mcp_name or q in eid:
            results.append(e)
    return results
