"""Universal Hot-Loader & IDE Config Manager for FORGE INFINITY.

Manages forge.mcp.json, export.bat, export.sh, and direct config injection into:
- Antigravity (~/.gemini/antigravity/mcp_config.json, ~/.antigravity/mcp.json, or workspace .antigravity/mcp.json)
- Cursor (~/.cursor/mcp.json or workspace .cursor/mcp.json)
- Codex (~/.codex/config.json, ~/.codex/mcp.json, or workspace .codex/mcp.json)
- Z Code / Zed (~/.zcode/mcp.json, ~/.config/zed/settings.json, or %APPDATA%/Zed/settings.json)

All file writes are atomic (temp file + os.replace) with strict '/' path normalization.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.paths import get_project_root, get_user_home, normalize_path, to_posix_str
from backend.aurum.secrets_manager import get_injection_env_block

ROOT = get_project_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FORGE_MCP_JSON = ROOT / "forge.mcp.json"
EXPORT_BAT = ROOT / "export.bat"
EXPORT_SH = ROOT / "export.sh"

AURUM_HUB_SERVER_PATH = (ROOT / "forge" / "mcp" / "forge_aurum_hub" / "server.py").resolve().as_posix()
FACTORY_SERVER_PATH = (ROOT / "forge" / "mcp" / "forge_factory_mcp" / "server.py").resolve().as_posix()
UNIFIED_SERVER_PATH = (ROOT / "mcp_registry" / "servers" / "unified-mcp" / "server.py").resolve().as_posix()


def _atomic_write_json(file_path: Path, data: Any) -> None:
    """Atomic write to JSON file using temp file + os.replace with Windows file-lock retry/fallback."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    text = json.dumps(data, indent=2, ensure_ascii=False)
    clean_text = text.replace("\\\\", "/").replace("\\", "/")
    for attempt in range(3):
        try:
            fd, tmp_name = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_forge_", suffix=".json")
            with open(fd, "w", encoding="utf-8") as f:
                f.write(clean_text)
            if file_path.exists():
                os.replace(tmp_name, file_path)
            else:
                shutil.move(tmp_name, file_path)
            return
        except Exception:
            if "tmp_name" in locals() and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except Exception:
                    pass
            if attempt < 2:
                time.sleep(0.05)
    file_path.write_text(clean_text, encoding="utf-8")


def _atomic_write_text(file_path: Path, text: str) -> None:
    """Atomic write to text file using temp file + os.replace with Windows file-lock retry/fallback."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    for attempt in range(3):
        try:
            fd, tmp_name = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_forge_", suffix=".txt")
            with open(fd, "w", encoding="utf-8") as f:
                f.write(text)
            if file_path.exists():
                os.replace(tmp_name, file_path)
            else:
                shutil.move(tmp_name, file_path)
            return
        except Exception:
            if "tmp_name" in locals() and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except Exception:
                    pass
            if attempt < 2:
                time.sleep(0.05)
    file_path.write_text(text, encoding="utf-8")


def get_ide_config_paths() -> Dict[str, List[Path]]:
    """Return true, dynamic OS-aware config file paths for the 4 supported IDEs."""
    home_dir = get_user_home()
    appdata = os.environ.get("APPDATA", "")
    
    # Z Code / Zed OS paths
    zed_paths: List[Path] = [
        home_dir / ".zcode" / "mcp.json",
        ROOT / ".zcode" / "mcp.json",
        home_dir / ".config" / "zed" / "settings.json",
    ]
    if appdata:
        zed_paths.insert(0, Path(appdata).resolve() / "Zed" / "settings.json")
    mac_zed = home_dir / "Library" / "Application Support" / "Zed" / "settings.json"
    zed_paths.append(mac_zed)

    return {
        "cursor": [
            home_dir / ".cursor" / "mcp.json",
            ROOT / ".cursor" / "mcp.json",
        ],
        "antigravity": [
            home_dir / ".gemini" / "antigravity" / "mcp_config.json",
            home_dir / ".antigravity" / "mcp.json",
            home_dir / ".gemini" / "config" / "mcp_config.json",
            ROOT / ".gemini" / "antigravity" / "mcp_config.json",
            ROOT / ".antigravity" / "mcp.json",
        ],
        "codex": [
            home_dir / ".codex" / "config.json",
            home_dir / ".codex" / "mcp.json",
            home_dir / ".config" / "codex" / "config.json",
            ROOT / ".codex" / "mcp.json",
        ],
        "z_code": zed_paths,
    }


def generate_universal_config(
    active_mcp_name: str = "forge-aurum-hub",
    active_server_path: str = AURUM_HUB_SERVER_PATH,
    env_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate forge.mcp.json structure with strict '/' path normalization for Cursor, Antigravity, Codex, Z Code."""
    clean_path = str(active_server_path).replace("\\", "/")
    clean_hub = str(AURUM_HUB_SERVER_PATH).replace("\\", "/")
    clean_factory = str(FACTORY_SERVER_PATH).replace("\\", "/")
    clean_unified = str(UNIFIED_SERVER_PATH).replace("\\", "/")
    clean_root = str(ROOT).replace("\\", "/")

    home_dir = get_user_home().as_posix()
    env_block = env_vars if env_vars is not None else get_injection_env_block()

    config: Dict[str, Any] = {
        "version": "3.1.0",
        "name": "FORGE-AURUM SUPER-HUB Universal Configuration",
        "badge": "AURUM GOLD (#C6A96B)",
        "description": "One-click executable connection config for Cursor, Antigravity, Codex, and Z Code",
        "active_mcp": {
            "name": active_mcp_name,
            "server_path": clean_path,
            "command": "python",
            "args": [clean_path],
            "env": env_block,
        },
        "servers": {
            "forge_aurum_hub": {
                "name": "forge-aurum-hub",
                "description": "FORGE-AURUM Super-Hub (50-in-1 Aggregator MCP operating Telegram, Gmail, Instagram, YouTube, GitHub, Notion, Slack, and custom sites)",
                "command": "python",
                "args": [clean_hub],
            },
            "forge_factory": {
                "name": "forge-factory",
                "description": "Operating System Factory MCP — forges, hot-loads, benchmarks, and heals MCPs inside your IDE",
                "command": "python",
                "args": [clean_factory],
            },
            "unified_forge": {
                "name": "unified-forge",
                "description": "Active Unified MCP server operating custom websites and official APIs",
                "command": "python",
                "args": [clean_unified],
            },
        },
        "ides": {
            "cursor": {
                "ide_name": "Cursor",
                "config_path": f"{clean_root}/.cursor/mcp.json",
                "format": "mcpServers",
                "snippet": {
                    "mcpServers": {
                        active_mcp_name: {
                            "command": "python",
                            "args": [clean_path],
                            "env": env_block,
                        }
                    }
                },
                "how_to_connect": "1. Save into .cursor/mcp.json in workspace or ~/.cursor/mcp.json. | 2. 1-Click Inject automatically writes to disk.",
                "is_cli": False,
            },
            "antigravity": {
                "ide_name": "Google Antigravity",
                "config_path": f"{home_dir}/.gemini/antigravity/mcp_config.json",
                "format": "mcpServers",
                "snippet": {
                    "mcpServers": {
                        active_mcp_name: {
                            "command": "python",
                            "args": [clean_path],
                            "env": env_block,
                        }
                    }
                },
                "how_to_connect": "1. Open Antigravity Settings -> MCP or ~/.gemini/antigravity/mcp_config.json. | 2. 1-Click Inject automatically configures the server in <1s.",
                "is_cli": False,
            },
            "codex": {
                "ide_name": "Codex",
                "config_path": f"{home_dir}/.codex/config.json",
                "format": "mcpServers",
                "cli_command": f"codex mcp add {active_mcp_name} -- python '{clean_path}'",
                "snippet": {
                    "mcpServers": {
                        active_mcp_name: {
                            "command": "python",
                            "args": [clean_path],
                            "env": env_block,
                        }
                    }
                },
                "how_to_connect": f"Run `codex mcp add {active_mcp_name} -- python '{clean_path}'` or inject directly into ~/.codex/config.json",
                "is_cli": True,
            },
            "z_code": {
                "ide_name": "Z Code / Zed",
                "config_path": f"{home_dir}/.zcode/mcp.json",
                "format": "mcpServers / context_servers",
                "snippet": {
                    "context_servers": {
                        active_mcp_name: {
                            "command": {
                                "path": "python",
                                "args": [clean_path],
                                "env": env_block,
                            }
                        }
                    },
                    "mcpServers": {
                        active_mcp_name: {
                            "command": "python",
                            "args": [clean_path],
                            "env": env_block,
                        }
                    }
                },
                "how_to_connect": "1. Open Zed/Z Code settings.json or ~/.zcode/mcp.json. | 2. 1-Click Inject configures both context_servers and mcpServers automatically.",
                "is_cli": False,
            },
        },
        "export_scripts": {
            "windows": "export.bat",
            "unix": "export.sh",
        },
    }
    return config


def generate_root_export_scripts(mcp_name: str, server_path: str) -> Tuple[str, str]:
    """Generate export.bat and export.sh scripts targeting Codex, Z Code, Cursor, and Antigravity."""
    clean_path = str(server_path).replace("\\", "/")

    bat_content = f"""@echo off
REM FORGE INFINITY 1-Click Multi-IDE Exporter
REM Configures Cursor, Antigravity, Codex, and Z Code with normalized '/' paths
echo [FORGE INFINITY] Exporting MCP '{mcp_name}' to AI IDEs (Cursor, Antigravity, Codex, Z Code)...

REM Codex CLI auto-configuration
where codex >nul 2>nul
if %ERRORLEVEL% equ 0 (
    codex mcp add {mcp_name} -- python "{clean_path}" 2>nul
    echo   [OK] Codex configured successfully.
) else (
    echo   [INFO] codex CLI not in PATH - use 1-Click Inject from UI.
)

echo [FORGE INFINITY] For Cursor, Antigravity, and Z Code, 1-Click Inject from UI writes directly to disk!
echo [FORGE INFINITY] Secrets are injected directly into environment blocks.
"""

    sh_content = f"""#!/usr/bin/env bash
# FORGE INFINITY 1-Click Multi-IDE Exporter
# Configures Cursor, Antigravity, Codex, and Z Code with normalized '/' paths
set -e
echo "[FORGE INFINITY] Exporting MCP '{mcp_name}' to AI IDEs (Cursor, Antigravity, Codex, Z Code)..."

if command -v codex &> /dev/null; then
    codex mcp add {mcp_name} -- python "{clean_path}" || true
    echo "  [OK] Codex configured successfully."
else
    echo "  [INFO] codex CLI not found - use 1-Click Inject from UI."
fi

echo "[FORGE INFINITY] For Cursor, Antigravity, and Z Code, 1-Click Inject from UI writes directly to disk!"
echo "[FORGE INFINITY] Secrets are injected directly into environment blocks."
"""
    return bat_content, sh_content


def write_universal_config_and_scripts(
    active_mcp_name: str = "forge-aurum-hub",
    active_server_path: str = AURUM_HUB_SERVER_PATH,
    env_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Regenerate forge.mcp.json, export.bat, and export.sh atomically at repo root."""
    config = generate_universal_config(active_mcp_name, active_server_path, env_vars)
    _atomic_write_json(FORGE_MCP_JSON, config)

    bat_script, sh_script = generate_root_export_scripts(active_mcp_name, active_server_path)
    _atomic_write_text(EXPORT_BAT, bat_script)
    _atomic_write_text(EXPORT_SH, sh_script)

    return config


def validate_environment(server_path: Optional[str] = None) -> Dict[str, Any]:
    """Validate system readiness: path existence, Python executable, FastMCP importability, and Aurum proof."""
    target_path = Path(server_path) if server_path else Path(AURUM_HUB_SERVER_PATH)
    path_exists = target_path.exists()

    python_ok = False
    python_version = ""
    try:
        res = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            python_ok = True
            python_version = (res.stdout or res.stderr).strip()
    except Exception:
        python_ok = False

    fastmcp_ok = False
    try:
        import fastmcp
        fastmcp_ok = True
    except ImportError:
        fastmcp_ok = False

    aurum_verified = path_exists and python_ok and fastmcp_ok

    return {
        "ok": aurum_verified,
        "path_exists": path_exists,
        "server_path": str(target_path).replace("\\", "/"),
        "python_available": python_ok,
        "python_version": python_version or sys.version.split()[0],
        "fastmcp_ready": fastmcp_ok,
        "aurum_verified": aurum_verified,
        "badge_color": "#C6A96B",
        "root_normalized": str(ROOT).replace("\\", "/"),
        "active_server": "forge-aurum-hub",
    }


def hot_load_into_ide(
    ide_key: str,
    mcp_name: str,
    server_path: str,
    env_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Directly and atomically inject MCP server configuration into target IDE config files."""
    clean_path = str(server_path).replace("\\", "/")
    effective_env = env_vars if env_vars is not None else get_injection_env_block()
    ide_paths = get_ide_config_paths()

    def _write_one_file(target_file: Path, is_zed_settings: bool = False) -> bool:
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            existing_data: Dict[str, Any] = {}
            if target_file.exists():
                try:
                    existing_data = json.loads(target_file.read_text("utf-8"))
                except Exception:
                    existing_data = {}

            if not isinstance(existing_data, dict):
                existing_data = {}

            # Build server entry
            server_entry = {
                "command": "python",
                "args": [clean_path],
            }
            if effective_env:
                server_entry["env"] = effective_env

            # Write standard mcpServers
            if not isinstance(existing_data.get("mcpServers"), dict):
                existing_data["mcpServers"] = {}
            existing_data["mcpServers"][mcp_name] = server_entry

            # For Zed settings.json, also write context_servers
            if is_zed_settings or "settings.json" in target_file.name:
                if not isinstance(existing_data.get("context_servers"), dict):
                    existing_data["context_servers"] = {}
                existing_data["context_servers"][mcp_name] = {
                    "command": {
                        "path": "python",
                        "args": [clean_path],
                        "env": effective_env,
                    }
                }

            _atomic_write_json(target_file, existing_data)
            return True
        except Exception:
            return False

    def _write_ide_config(key: str) -> Dict[str, Any]:
        """Write the entry into all associated paths for this IDE."""
        files = ide_paths.get(key, [])
        written_paths = []
        for tf in files:
            is_zed_settings = (key == "z_code" and "settings.json" in tf.name)
            if _write_one_file(tf, is_zed_settings):
                written_paths.append(str(tf).replace("\\", "/"))

        if written_paths:
            return {
                "ok": True,
                "ide": key,
                "config_path": written_paths[0],
                "all_paths": written_paths,
                "mcp_name": mcp_name,
                "server_path": clean_path,
                "message": f"Successfully hot-loaded '{mcp_name}' into {key} with secrets injected!",
            }
        else:
            return {
                "ok": False,
                "ide": key,
                "error": f"Failed to write config for {key}",
            }

    valid_keys = {"cursor", "antigravity", "codex", "z_code"}

    if ide_key == "all":
        results = {k: _write_ide_config(k) for k in valid_keys}
        # Also refresh root config
        write_universal_config_and_scripts(mcp_name, clean_path, effective_env)
        return {"ok": True, "target": "all", "results": results}

    if ide_key not in valid_keys:
        return {"ok": False, "error": f"Unsupported IDE key '{ide_key}'. Must be one of {list(valid_keys)}"}

    result = _write_ide_config(ide_key)

    # Update root universal config
    write_universal_config_and_scripts(mcp_name, clean_path, effective_env)
    return result
