"""FORGE INFINITY Marketplace Engine — npm for FastMCP servers.

Day-0 Clean Package Registry for publishing, discovering, and 1-click installing
MCP servers into any AI IDE with zero manual configuration.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import DIST_DIR, MCP_REGISTRY_DIR, ensure_dirs
from backend.factory.hot_loader import _atomic_write_json, hot_load_into_ide
from backend.forge.history import get_all_history, get_history_by_id, search_history

MARKETPLACE_JSON = MCP_REGISTRY_DIR / "marketplace.json"
PACKAGES_DIR = MCP_REGISTRY_DIR / "packages"

_marketplace_lock = threading.Lock()

CATEGORIES = [
    "System & Hardware",
    "Browser Automation",
    "Productivity",
    "Data & APIs",
    "DevTools",
]


def ensure_marketplace_dirs() -> None:
    ensure_dirs()
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    with _marketplace_lock:
        if not MARKETPLACE_JSON.exists():
            _atomic_write_json(MARKETPLACE_JSON, [])


def load_marketplace() -> List[Dict[str, Any]]:
    ensure_marketplace_dirs()
    with _marketplace_lock:
        if not MARKETPLACE_JSON.exists():
            return []
        try:
            data = json.loads(MARKETPLACE_JSON.read_text("utf-8"))
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []


def save_marketplace(packages: List[Dict[str, Any]]) -> None:
    ensure_marketplace_dirs()
    with _marketplace_lock:
        _atomic_write_json(MARKETPLACE_JSON, packages)


def infer_category(goal: str, tools: List[str]) -> str:
    text = f"{goal} {' '.join(tools)}".lower()
    if any(k in text for k in ["ram", "cpu", "gpu", "hardware", "disk", "battery", "system"]):
        return "System & Hardware"
    if any(k in text for k in ["notion", "gmail", "email", "calendar", "slack", "todo"]):
        return "Productivity"
    if any(k in text for k in ["api", "db", "sql", "weather", "stock", "crypto", "database"]):
        return "Data & APIs"
    if any(k in text for k in ["code", "git", "debug", "test", "benchmark", "inspector"]):
        return "DevTools"
    return "Browser Automation"


def _bump_version(version: str) -> str:
    """Increment the patch segment of a semver string: 1.0.0 -> 1.0.1."""
    parts = str(version or "1.0.0").split(".")
    while len(parts) < 3:
        parts.append("0")
    try:
        parts[2] = str(int(parts[2]) + 1)
    except ValueError:
        parts[2] = "1"
    return ".".join(parts)


def publish_mcp(
    history_id_or_name: str,
    author: str = "local_dev",
    description: str = "",
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
    version: str = "1.0.0",
) -> Dict[str, Any]:
    """Publish a forged MCP from history or active registry to the Marketplace.

    Re-publishing an existing package name bumps its version instead of duplicating.
    """
    ensure_marketplace_dirs()
    target_id = (history_id_or_name or "").strip()

    # Look up in history: exact id, then exact mcp_name, then fuzzy text match
    entry = get_history_by_id(target_id)
    if not entry:
        all_entries = get_all_history()
        exact = [e for e in all_entries if e.get("mcp_name", "").lower() == target_id.lower()]
        if exact:
            entry = exact[0]
    if not entry:
        matches = search_history(target_id)
        # Prefer entries whose goal/tools do not merely mention the name in a chain composite
        matches = [e for e in matches if not str(e.get("mcp_name", "")).startswith("chain-")] or matches
        if matches:
            entry = matches[0]

    if not entry:
        # Fallback to current unified server
        unified_py = ROOT / "mcp_registry" / "servers" / "unified-mcp" / "server.py"
        unified_skill = ROOT / "mcp_registry" / "servers" / "unified-mcp" / "SKILL.md"
        if not unified_py.exists():
            return {"ok": False, "error": f"No forged MCP found with id/name '{target_id}' to publish"}

        entry = {
            "id": f"pkg_{int(time.time())}",
            "mcp_name": "unified-forge",
            "goal": "Unified Browser and API Automation",
            "abs_path": str(unified_py).replace("\\", "/"),
            "tools": ["search_ram", "gmail_send_email", "notion_log_price"],
            "skill_content": unified_skill.read_text("utf-8") if unified_skill.exists() else "",
            "zip_path": str(DIST_DIR / "unified-mcp.zip").replace("\\", "/"),
        }

    mcp_name = (entry.get("mcp_name") or "unified-forge").strip().lower().replace(" ", "-")

    server_source = ""
    server_path = entry.get("abs_path", "")
    if server_path and Path(server_path).exists():
        server_source = Path(server_path).read_text("utf-8")
    if not server_source and entry.get("skill_content"):
        server_source = entry.get("skill_content", "")

    # Security Vault Gate — Hard block if secrets or unsafe calls are present in source or metadata
    all_content_to_scan = f"{server_source}\n{description}\n{entry.get('goal', '')}\n{entry.get('skill_content', '')}"
    if all_content_to_scan.strip():
        from backend.aurum.security_vault import scan_source_security
        sec_report = scan_source_security(all_content_to_scan, mcp_name)
        if not sec_report.get("can_publish", True) or sec_report.get("security_score", 100) < 90:
            return {
                "ok": False,
                "error": f"Publish blocked: secret or high-severity vulnerability detected in {mcp_name} (Score: {sec_report.get('security_score')}/100)",
                "security_report": sec_report,
            }

    import hashlib
    content_hash = hashlib.sha256(f"{server_source}\n{mcp_name}".encode("utf-8")).hexdigest()[:12]

    tools = entry.get("tools", [])
    cat = category or infer_category(entry.get("goal", ""), tools)
    tag_list = tags or [t.split("_")[0] for t in tools[:4]]
    if cat not in tag_list:
        tag_list.append(cat.lower().replace(" ", "-"))

    packages = load_marketplace()

    # Re-publish: bump version on the existing record instead of duplicating
    existing = next((p for p in packages if p.get("name") == mcp_name), None)
    if existing is not None:
        package_id = existing["package_id"]
        new_version = _bump_version(existing.get("version", version))
        existing.update(
            {
                "version": new_version,
                "author": author or existing.get("author", "local_dev"),
                "description": description or entry.get("goal") or existing.get("description", ""),
                "category": cat,
                "tags": list(set(tag_list)) or existing.get("tags", []),
                "tools_count": len(tools),
                "tools": tools,
                "dag": entry.get("dag", existing.get("dag", {})),
                "skill_content": entry.get("skill_content", existing.get("skill_content", "")),
                "zip_path": entry.get("zip_path", existing.get("zip_path", "")),
                "verified": True,
                "aurum_verified": True,
                "aurum_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "hash": content_hash,
                "aurum_gold_badge": True,
                "badge_color": "#C6A96B",
                "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )
        pkg_dir = PACKAGES_DIR / package_id
        pkg_dir.mkdir(parents=True, exist_ok=True)
        if server_source:
            (pkg_dir / "server.py").write_text(server_source, "utf-8")
            existing["server_path"] = str(pkg_dir / "server.py").replace("\\", "/")
        if entry.get("skill_content"):
            (pkg_dir / "SKILL.md").write_text(entry["skill_content"], "utf-8")
        save_marketplace(packages)
        return {
            "ok": True,
            "package_id": package_id,
            "name": mcp_name,
            "version": new_version,
            "republished": True,
            "message": f"Version bumped to {new_version} for '{mcp_name}' (no duplicate created).",
            "package": existing,
        }

    package_id = f"pkg_{mcp_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Package files storage
    pkg_dir = PACKAGES_DIR / package_id
    pkg_dir.mkdir(parents=True, exist_ok=True)
    if server_source:
        (pkg_dir / "server.py").write_text(server_source, "utf-8")
    if entry.get("skill_content"):
        (pkg_dir / "SKILL.md").write_text(entry.get("skill_content", ""), "utf-8")

    pkg_record: Dict[str, Any] = {
        "package_id": package_id,
        "name": mcp_name,
        "version": version,
        "author": author or "local_dev",
        "description": description or entry.get("goal") or f"FastMCP server for {mcp_name}",
        "category": cat,
        "tags": list(set(tag_list)),
        "tools_count": len(tools),
        "tools": tools,
        "dag": entry.get("dag", {}),
        "server_path": str(pkg_dir / "server.py").replace("\\", "/"),
        "skill_content": entry.get("skill_content", ""),
        "zip_path": entry.get("zip_path", ""),
        "installs_count": 0,
        "verified": True,
        "aurum_verified": True,
        "aurum_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hash": content_hash,
        "aurum_gold_badge": True,
        "badge_color": "#C6A96B",
        "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    packages = [p for p in packages if p.get("package_id") != package_id]
    packages.insert(0, pkg_record)
    save_marketplace(packages)

    return {
        "ok": True,
        "package_id": package_id,
        "name": mcp_name,
        "version": version,
        "message": f"Successfully published '{mcp_name}' to Forge Marketplace!",
        "package": pkg_record,
    }


def search_packages(
    query: str = "",
    category: str = "",
    tag: str = "",
) -> List[Dict[str, Any]]:
    """Search Marketplace packages by text query, category, or tag."""
    packages = load_marketplace()
    q = (query or "").strip().lower()
    cat_filter = (category or "").strip().lower()
    tag_filter = (tag or "").strip().lower()

    results = []
    for p in packages:
        p_name = p.get("name", "").lower()
        p_desc = p.get("description", "").lower()
        p_author = p.get("author", "").lower()
        p_tools = " ".join(p.get("tools", [])).lower()
        p_cat = p.get("category", "").lower()
        p_tags = [t.lower() for t in p.get("tags", [])]

        if q and not (q in p_name or q in p_desc or q in p_author or q in p_tools):
            continue
        if cat_filter and p_cat != cat_filter:
            continue
        if tag_filter and tag_filter not in p_tags:
            continue

        results.append(p)

    return results


def get_package(package_id: str) -> Optional[Dict[str, Any]]:
    for p in load_marketplace():
        if p.get("package_id") == package_id or p.get("name") == package_id:
            return p
    return None


def install_package(package_id: str, target_ide: str = "all") -> Dict[str, Any]:
    """1-Click Install package from Marketplace: writes local server, root SKILL.md, and hot-loads into active IDEs."""
    pkg = get_package(package_id)
    if not pkg:
        return {"ok": False, "error": f"Package '{package_id}' not found in Marketplace"}

    mcp_name = pkg.get("name", "installed-mcp")
    dest_dir = MCP_REGISTRY_DIR / "servers" / mcp_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_server = dest_dir / "server.py"
    dest_skill = dest_dir / "SKILL.md"

    # Copy / write server.py and single root SKILL.md
    src_server = Path(pkg.get("server_path", ""))
    if src_server.exists():
        shutil.copy2(src_server, dest_server)
    elif pkg.get("server_py"):
        dest_server.write_text(pkg["server_py"], "utf-8")

    if pkg.get("skill_content"):
        dest_skill.write_text(pkg["skill_content"], "utf-8")

    clean_path = str(dest_server).replace("\\", "/")

    # Atomically hot-load into all active IDEs
    hot_load_res = hot_load_into_ide(target_ide, mcp_name, clean_path)

    # Increment real install counter
    packages = load_marketplace()
    for p in packages:
        if p.get("package_id") == pkg.get("package_id"):
            p["installs_count"] = p.get("installs_count", 0) + 1
            break
    save_marketplace(packages)

    return {
        "ok": True,
        "package_id": pkg.get("package_id"),
        "name": mcp_name,
        "server_path": clean_path,
        "skill_path": str(dest_skill).replace("\\", "/"),
        "installs_count": pkg.get("installs_count", 0) + 1,
        "hot_load": hot_load_res,
        "say_line": f"Use {mcp_name} at {clean_path}",
        "message": f"Installed '{mcp_name}' and hot-loaded into active IDEs in 1-click!",
    }
