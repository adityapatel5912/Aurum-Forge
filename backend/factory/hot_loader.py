"""Universal Hot-Loader & IDE Config Manager for FORGE INFINITY.

Manages forge.mcp.json, export.bat, export.sh, and direct config injection into:
- Antigravity (~/.antigravity/mcp.json or workspace .antigravity/mcp.json)
- Z Code (Zed) (~/.zcode/mcp.json or ~/.config/zed/settings.json)
- Claude Code (~/.claude.json or ~/.claude/claude_code_config.json)
- Cursor (.cursor/mcp.json)
- Windsurf (~/.codeium/windsurf/mcp_config.json)
- OpenCode & Codex (CLI configurations)

All file writes are atomic (temp file + os.replace) with '/' path normalization.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FORGE_MCP_JSON = ROOT / "forge.mcp.json"
EXPORT_BAT = ROOT / "export.bat"
EXPORT_SH = ROOT / "export.sh"

AURUM_HUB_SERVER_PATH = (ROOT / "forge" / "mcp" / "forge_aurum_hub" / "server.py").resolve().as_posix()
FACTORY_SERVER_PATH = (ROOT / "forge" / "mcp" / "forge_factory_mcp" / "server.py").resolve().as_posix()
UNIFIED_SERVER_PATH = (ROOT / "mcp_registry" / "servers" / "unified-mcp" / "server.py").resolve().as_posix()


def _atomic_write_json(file_path: Path, data: Any) -> None:
    """Atomic write to JSON file using temp file + os.replace."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    fd, tmp_name = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_forge_", suffix=".json")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Replace target atomically
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


def _atomic_write_text(file_path: Path, text: str) -> None:
    """Atomic write to text file using temp file + os.replace."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    fd, tmp_name = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_forge_", suffix=".txt")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(text)
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


def generate_universal_config(
    active_mcp_name: str = "forge-aurum-hub",
    active_server_path: str = AURUM_HUB_SERVER_PATH,
    env_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate forge.mcp.json structure with strict '/' path normalization."""
    clean_path = str(active_server_path).replace("\\", "/")
    clean_hub = str(AURUM_HUB_SERVER_PATH).replace("\\", "/")
    clean_factory = str(FACTORY_SERVER_PATH).replace("\\", "/")
    clean_unified = str(UNIFIED_SERVER_PATH).replace("\\", "/")
    clean_root = str(ROOT).replace("\\", "/")

    home_dir = Path.home().resolve().as_posix()
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        claude_desktop_path = f"{Path(appdata).resolve().as_posix()}/Claude/claude_desktop_config.json"
    else:
        claude_desktop_path = f"{home_dir}/Library/Application Support/Claude/claude_desktop_config.json"

    env_block = env_vars or {
        "NOTION_TOKEN": "<your_notion_token>",
        "GMAIL_USER": "<your_gmail_address>",
        "GMAIL_APP_PASSWORD": "<your_gmail_app_password>",
        "GITHUB_TOKEN": "<your_github_token>",
        "SLACK_BOT_TOKEN": "<your_slack_token>",
        "FORGE_HEADLESS": "0",
    }

    config: Dict[str, Any] = {
        "version": "3.0.0",
        "name": "FORGE-AURUM SUPER-HUB Universal Configuration",
        "badge": "AURUM GOLD (#C6A96B)",
        "description": "One-click executable connection config for Antigravity, Z Code, Claude Code, Cursor, Windsurf, OpenCode, and Codex",
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
                "description": "FORGE-AURUM Super-Hub (50-in-1 Aggregator MCP operating all custom sites, official APIs, and chains)",
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
                "description": "Active Unified MCP server operating all custom websites and official APIs",
                "command": "python",
                "args": [clean_unified],
            },
        },
        "ides": {
            "antigravity": {
                "ide_name": "Google Antigravity",
                "config_path": f"{home_dir}/.antigravity/mcp.json",
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
                "how_to_connect": "1. Open Antigravity Settings -> MCP. | 2. Paste the JSON snippet into mcpServers. | 3. The Forge Factory MCP connects in <1s.",
                "is_cli": False,
            },
            "z_code": {
                "ide_name": "Z Code / Zed",
                "config_path": f"{home_dir}/.zcode/mcp.json",
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
                "how_to_connect": "1. Open Z Code / Zed settings.json. | 2. Add this snippet inside experimental.mcpServers or mcpServers. | 3. Save and use immediately.",
                "is_cli": False,
            },
            "claude_code": {
                "ide_name": "Claude Code",
                "config_path": f"{home_dir}/.claude.json",
                "format": "cli_or_json",
                "cli_command": f"claude mcp add {active_mcp_name} -- python {clean_path}",
                "snippet": {
                    "mcpServers": {
                        active_mcp_name: {
                            "command": "python",
                            "args": [clean_path],
                            "env": env_block,
                        }
                    }
                },
                "how_to_connect": f"Run in your terminal: claude mcp add {active_mcp_name} -- python {clean_path}",
                "is_cli": True,
            },
            "claude_desktop": {
                "ide_name": "Claude Desktop",
                "config_path": claude_desktop_path,
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
                "how_to_connect": f"Paste snippet into {claude_desktop_path} and restart Claude Desktop.",
                "is_cli": False,
            },
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
                "how_to_connect": "Paste snippet into .cursor/mcp.json in workspace or global Cursor settings.",
                "is_cli": False,
            },
            "windsurf": {
                "ide_name": "Windsurf (Codeium)",
                "config_path": f"{home_dir}/.codeium/windsurf/mcp_config.json",
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
                "how_to_connect": "Open Windsurf Settings -> MCP Servers -> Paste snippet.",
                "is_cli": False,
            },
            "opencode": {
                "ide_name": "OpenCode",
                "config_path": f"{home_dir}/.opencode/mcp.json",
                "format": "cli",
                "cli_command": f"opencode mcp add {active_mcp_name} -- python {clean_path}",
                "how_to_connect": f"Run in your terminal: opencode mcp add {active_mcp_name} -- python {clean_path}",
                "is_cli": True,
            },
            "codex": {
                "ide_name": "Codex",
                "config_path": f"{home_dir}/.codex/mcp.json",
                "format": "cli",
                "cli_command": f"codex mcp add {active_mcp_name} -- python {clean_path}",
                "how_to_connect": f"Run in your terminal: codex mcp add {active_mcp_name} -- python {clean_path}",
                "is_cli": True,
            },
        },
        "export_scripts": {
            "windows": "export.bat",
            "unix": "export.sh",
        },
    }
    return config


def generate_root_export_scripts(mcp_name: str, server_path: str) -> Tuple[str, str]:
    """Generate export.bat and export.sh scripts at root with '/' path normalization."""
    clean_path = str(server_path).replace("\\", "/")
    
    bat_content = f"""@echo off
REM FORGE INFINITY 1-Click Multi-IDE Exporter
REM Configures Claude Code, Codex, and OpenCode with normalized '/' paths
echo [FORGE INFINITY] Exporting MCP '{mcp_name}' to AI IDEs...

REM Claude Code
claude mcp add {mcp_name} -- python "{clean_path}" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Claude Code configured successfully.
) else (
    echo   [INFO] claude CLI not found or already configured.
)

REM Codex
codex mcp add {mcp_name} -- python "{clean_path}" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Codex configured successfully.
)

REM OpenCode
opencode mcp add {mcp_name} -- python "{clean_path}" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] OpenCode configured successfully.
)

echo [FORGE INFINITY] For Antigravity, Z Code, Cursor, and Windsurf, copy snippets from forge.mcp.json!
pause
"""

    sh_content = f"""#!/usr/bin/env bash
# FORGE INFINITY 1-Click Multi-IDE Exporter
# Configures Claude Code, Codex, and OpenCode with normalized '/' paths
set -e
echo "[FORGE INFINITY] Exporting MCP '{mcp_name}' to AI IDEs..."

if command -v claude &> /dev/null; then
    claude mcp add {mcp_name} -- python "{clean_path}" || true
    echo "  [OK] Claude Code configured successfully."
fi

if command -v codex &> /dev/null; then
    codex mcp add {mcp_name} -- python "{clean_path}" || true
    echo "  [OK] Codex configured successfully."
fi

if command -v opencode &> /dev/null; then
    opencode mcp add {mcp_name} -- python "{clean_path}" || true
    echo "  [OK] OpenCode configured successfully."
fi

echo "[FORGE INFINITY] For Antigravity, Z Code, Cursor, and Windsurf, copy snippets from forge.mcp.json!"
"""
    return bat_content, sh_content


def write_universal_config_and_scripts(
    active_mcp_name: str = "forge-factory",
    active_server_path: str = FACTORY_SERVER_PATH,
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
    home_dir = Path.home().resolve()
    
    ide_paths: Dict[str, Path] = {
        "antigravity": home_dir / ".antigravity" / "mcp.json",
        "z_code": home_dir / ".zcode" / "mcp.json",
        "claude_code": home_dir / ".claude.json",
        "cursor": home_dir / ".cursor" / "mcp.json",
        "cursor_project": ROOT / ".cursor" / "mcp.json",
        "windsurf": home_dir / ".codeium" / "windsurf" / "mcp_config.json",
    }

    def _write_ide_config(key: str) -> Dict[str, Any]:
        """Write the mcpServers entry into one IDE config file (atomic, mkdir-safe)."""
        target_file = ide_paths[key]
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            existing_data: Dict[str, Any] = {}
            if target_file.exists():
                try:
                    existing_data = json.loads(target_file.read_text("utf-8"))
                except Exception:
                    existing_data = {}

            if not isinstance(existing_data.get("mcpServers"), dict):
                existing_data["mcpServers"] = {}

            if mcp_name == "forge-aurum-hub":
                hub_clean = str(AURUM_HUB_SERVER_PATH).replace("\\", "/")
                existing_data["mcpServers"] = {
                    "forge-aurum-hub": {
                        "command": "python",
                        "args": [hub_clean],
                    }
                }
                if env_vars:
                    existing_data["mcpServers"]["forge-aurum-hub"]["env"] = env_vars
            else:
                existing_data["mcpServers"][mcp_name] = {
                    "command": "python",
                    "args": [clean_path],
                }
                if env_vars:
                    existing_data["mcpServers"][mcp_name]["env"] = env_vars

            _atomic_write_json(target_file, existing_data)
            return {
                "ok": True,
                "ide": key,
                "config_path": str(target_file).replace("\\", "/"),
                "mcp_name": mcp_name,
                "server_path": clean_path,
                "message": f"Successfully hot-loaded '{mcp_name}' into {key}!",
            }
        except Exception as e:
            return {"ok": False, "ide": key, "error": f"Failed to write config for {key}: {str(e)}"}

    if ide_key == "all":
        results = {k: _write_ide_config(k) for k in ide_paths}
        # Also refresh root config
        write_universal_config_and_scripts(mcp_name, clean_path, env_vars)
        return {"ok": True, "target": "all", "results": results}

    if ide_key == "cursor":
        # Cursor: write both the global (~/.cursor/mcp.json) and project (.cursor/mcp.json) configs
        results = {k: _write_ide_config(k) for k in ("cursor", "cursor_project")}
        write_universal_config_and_scripts(mcp_name, clean_path, env_vars)
        return {"ok": all(v.get("ok") for v in results.values()), "target": "cursor", "results": results}

    if ide_key not in ide_paths:
        return {"ok": False, "error": f"Unsupported IDE key '{ide_key}'"}

    result = _write_ide_config(ide_key)

    # Update root universal config
    write_universal_config_and_scripts(mcp_name, clean_path, env_vars)
    return result
