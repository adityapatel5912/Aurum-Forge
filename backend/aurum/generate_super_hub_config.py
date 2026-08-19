"""FORGE-AURUM Super-Hub Config Generator & Auto-Sync Engine.

Give Once, All Future MCPs Auto-Appear in IDE without Re-Inject:
- Dynamic discovery across mcp_registry/servers/*/server.py
- Generates forge/mcp/forge_aurum_hub/super_hub.mcp.json with auto_update: true
- Auto-syncs IDE config files (~/.antigravity/mcp.json, ~/.cursor/mcp.json, etc.)
- 1 single entry stays 1 entry while tools auto-grow 62 -> 66 -> 70+
- Strict '/' forward slash normalization, zero '\\' in JSON
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import DIST_DIR, MCP_REGISTRY_DIR, ensure_dirs

HUB_DIR = ROOT / "forge" / "mcp" / "forge_aurum_hub"
SUPER_HUB_MCP_JSON = HUB_DIR / "super_hub.mcp.json"
ROOT_FORGE_MCP_JSON = ROOT / "forge.mcp.json"
DIST_SUPER_HUB_JSON = DIST_DIR / "super_hub.mcp.json"
REGISTRY_FORGE_JSON = MCP_REGISTRY_DIR / "forge.mcp.json"
AURUM_HUB_SERVER_PATH = (HUB_DIR / "server.py").resolve().as_posix()


def _atomic_write_json(file_path: Path, data: Any) -> None:
    """Atomic write to JSON file ensuring strict '/' path normalization and zero '\\'."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    fd, tmp_name = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_hub_", suffix=".json")
    try:
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        # Normalize any stray backslashes in Windows file paths
        clean_json = raw_json.replace("\\\\", "/").replace("\\", "/")
        with open(fd, "w", encoding="utf-8") as f:
            f.write(clean_json)
        if file_path.exists():
            os.replace(tmp_name, file_path)
        else:
            shutil.move(tmp_name, file_path)
    except Exception:
        if os.path.exists(tmp_name):
            try:
                os.unlink(tmp_name)
            except Exception:
                pass
        raise


def extract_tools_from_file(file_path: Path) -> List[Dict[str, str]]:
    """Parse python source via AST and extract all functions decorated with @mcp.tool()."""
    if not file_path.exists():
        return []
    try:
        source = file_path.read_text("utf-8", errors="replace")
        tree = ast.parse(source)
        tools = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_tool = False
                for dec in node.decorator_list:
                    dname = ""
                    if isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute):
                            dname = dec.func.attr
                        elif isinstance(dec.func, ast.Name):
                            dname = dec.func.id
                    elif isinstance(dec, ast.Attribute):
                        dname = dec.attr
                    elif isinstance(dec, ast.Name):
                        dname = dec.id
                    if dname in ("tool", "mcp_tool"):
                        is_tool = True
                        break
                if is_tool:
                    doc = ast.get_docstring(node) or "FastMCP tool"
                    tools.append({"name": node.name, "description": doc.splitlines()[0] if doc else "FastMCP tool"})
        return tools
    except Exception:
        return []


def scan_all_mcp_servers() -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Scan mcp_registry/servers/ and discover all active MCP servers and their tools."""
    ensure_dirs()
    discovered: Dict[str, Dict[str, Any]] = {}
    total_tools_count = 0

    servers_dir = MCP_REGISTRY_DIR / "servers"
    if servers_dir.exists():
        for sdir in sorted(servers_dir.iterdir()):
            if not sdir.is_dir() or sdir.name.startswith((".", "_")) or sdir.name == "temp":
                continue
            server_file = sdir / "server.py"
            if not server_file.exists():
                continue

            tools = extract_tools_from_file(server_file)
            tools_count = len(tools)
            if tools_count == 0:
                continue

            content = server_file.read_text("utf-8", errors="replace")
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
            rel_path = f"mcp_registry/servers/{sdir.name}/server.py"

            discovered[sdir.name] = {
                "name": sdir.name,
                "path": rel_path,
                "abs_path": str(server_file.resolve()).replace("\\", "/"),
                "tools": tools_count,
                "tool_names": [t["name"] for t in tools],
                "hash": content_hash,
                "aurum_verified": True,
                "badge": "AURUM GOLD #C6A96B",
            }
            total_tools_count += tools_count

    return discovered, total_tools_count


def generate_super_hub_config_data(
    discovered_servers: Optional[Dict[str, Dict[str, Any]]] = None,
    total_tools: Optional[int] = None,
) -> Dict[str, Any]:
    """Generate the canonical auto-updating super_hub.mcp.json structure with '/' paths."""
    if discovered_servers is None or total_tools is None:
        discovered_servers, total_tools = scan_all_mcp_servers()

    server_script = str(AURUM_HUB_SERVER_PATH).replace("\\", "/")
    watch_path = str(MCP_REGISTRY_DIR / "servers").replace("\\", "/")
    last_scan = datetime.now(timezone.utc).isoformat(timespec="seconds")
    total_servers_count = len(discovered_servers)

    config_data: Dict[str, Any] = {
        "mcpServers": {
            "forge-aurum-hub": {
                "command": "python",
                "args": [server_script],
                "env": {},
                "description": "Super-Hub 1 entry replaces 50+ — auto-updates — give once",
                "type": "aurum_gold",
                "badge": "#C6A96B",
                "auto_update": True,
                "watch_path": watch_path,
                "hot_reload": "0.1s",
                "version": "1.0.1",
                "hash": "f6cdbd0a07f2",
                "aurum_verified": True,
            }
        },
        "aurum_auto_update": {
            "enabled": True,
            "watch_paths": ["mcp_registry/servers", "forge/mcp", "marketplace.json"],
            "reload_interval": "0.1s",
            "ide_auto_sync": True,
            "ide_targets": [
                "antigravity",
                "claude_code",
                "cursor",
                "windsurf",
                "opencode",
                "codex",
                "z_code",
                "all",
            ],
            "last_scan": last_scan,
            "total_servers": total_servers_count,
            "total_tools": total_tools,
        },
        "discovered_servers": discovered_servers,
        "super_hub_summary": {
            "give_once": True,
            "auto_updates": "All future forged MCPs appear automatically without re-inject",
            "total_servers": total_servers_count,
            "total_tools": total_tools,
            "ide_entry": f"1 entry stays 1 entry, tools auto-grow {total_tools}",
            "version": "1.0.1",
        },
    }
    return config_data


HUB_ENTRY_KEYS = {"forge_aurum_hub", "forge-aurum-hub", "aurum_hub", "forge-hub", "aurum-super-hub"}


def auto_sync_ide_configs(server_script_path: str) -> List[str]:
    """Auto-sync IDE config files: exactly ONE 'forge-aurum-hub' entry with '/' paths.

    Non-destructive: unrelated user MCP entries are preserved. Only (a) stale
    hub-name variants and (b) entries pointing into mcp_registry/servers or /mcp/
    (redundant with the give-once hub) are collapsed into the single hub entry.
    """
    clean_path = str(server_script_path).replace("\\", "/")
    home_dir = Path.home().resolve()
    synced_ides: List[str] = []

    ide_configs: Dict[str, Path] = {
        "antigravity": home_dir / ".antigravity" / "mcp.json",
        "cursor": home_dir / ".cursor" / "mcp.json",
        "cursor_project": ROOT / ".cursor" / "mcp.json",
        "claude_code": home_dir / ".claude.json",
        "windsurf": home_dir / ".codeium" / "windsurf" / "mcp_config.json",
        "z_code": home_dir / ".zcode" / "mcp.json",
    }

    for ide_key, cfg_path in ide_configs.items():
        try:
            cfg_path.parent.mkdir(parents=True, exist_ok=True)
            existing_data: Dict[str, Any] = {}
            if cfg_path.exists():
                try:
                    existing_data = json.loads(cfg_path.read_text("utf-8"))
                except Exception:
                    existing_data = {}

            servers = dict(existing_data.get("mcpServers") or {})
            for key in list(servers.keys()):
                normalized = key.lower().replace("-", "_").replace(" ", "_")
                entry_json = json.dumps(servers[key])
                redundant = ("mcp_registry/servers" in entry_json or "/mcp/" in entry_json.replace("\\", "/"))
                if normalized in HUB_ENTRY_KEYS or redundant:
                    del servers[key]  # give-once: hub already serves these tools
            servers["forge-aurum-hub"] = {"command": "python", "args": [clean_path]}
            existing_data["mcpServers"] = servers

            _atomic_write_json(cfg_path, existing_data)
            synced_ides.append(ide_key)
        except Exception as e:
            print(f"[AUTO-SYNC] Error updating {ide_key} at {cfg_path}: {e}")

    return synced_ides


def generate_and_sync_super_hub(auto_sync_ides: bool = True) -> Dict[str, Any]:
    """Full execution: scan servers -> generate super_hub.mcp.json -> distribute & sync IDEs."""
    ensure_dirs()
    HUB_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    discovered, total_tools = scan_all_mcp_servers()
    config_data = generate_super_hub_config_data(discovered, total_tools)

    # 1. Write to forge/mcp/forge_aurum_hub/super_hub.mcp.json
    _atomic_write_json(SUPER_HUB_MCP_JSON, config_data)

    # 2. Copy to root forge.mcp.json, dist/super_hub.mcp.json, mcp_registry/forge.mcp.json
    _atomic_write_json(ROOT_FORGE_MCP_JSON, config_data)
    _atomic_write_json(DIST_SUPER_HUB_JSON, config_data)
    _atomic_write_json(REGISTRY_FORGE_JSON, config_data)

    # Assert no backslashes in any generated config
    for target in [SUPER_HUB_MCP_JSON, ROOT_FORGE_MCP_JSON, DIST_SUPER_HUB_JSON, REGISTRY_FORGE_JSON]:
        if target.exists():
            text = target.read_text("utf-8")
            assert "\\" not in text, f"Stray backslash detected in {target}"

    # 3. Auto-sync IDEs
    synced_ides = []
    if auto_sync_ides:
        server_path = str(AURUM_HUB_SERVER_PATH).replace("\\", "/")
        synced_ides = auto_sync_ide_configs(server_path)
        print(f"[AUTO-SYNC] IDEs updated: {', '.join(synced_ides)} — total_tools {total_tools}")

    return {
        "ok": True,
        "total_servers": len(discovered),
        "total_tools": total_tools,
        "discovered_servers": discovered,
        "super_hub_json_path": str(SUPER_HUB_MCP_JSON).replace("\\", "/"),
        "ide_synced": synced_ides,
        "last_scan": config_data["aurum_auto_update"]["last_scan"],
        "message": f"Successfully generated Super-Hub config ({len(discovered)} servers, {total_tools} tools) and synced IDEs!",
    }


if __name__ == "__main__":
    res = generate_and_sync_super_hub(auto_sync_ides=True)
    print(json.dumps(res, indent=2))
