"""FORGE 6-way agent exporter.

Exports MCP Server configuration and command to:
- Claude Code (CLI)
- Cursor (Config)
- Z Code / Zed (Config)
- OpenCode (CLI)
- Antigravity (Config)
- Codex (CLI)
"""
from __future__ import annotations

from typing import Any

VALID_PLATFORMS = ("claude_code", "cursor", "zcode", "opencode", "antigravity", "codex")

PLATFORM_METADATA = {
    "claude_code": {
        "id": "claude_code",
        "name": "Claude Code",
        "is_cli": True,
        "alias": ["claude", "claude_code", "claudecode"],
        "configFile": "claude_desktop_config.json",
        "configPath": "%APPDATA%/Claude/claude_desktop_config.json",
    },
    "cursor": {
        "id": "cursor",
        "name": "Cursor",
        "is_cli": False,
        "alias": ["cursor"],
        "configFile": ".cursor/mcp.json",
        "configPath": ".cursor/mcp.json",
    },
    "zcode": {
        "id": "zcode",
        "name": "Z Code (Zed)",
        "is_cli": False,
        "alias": ["zcode", "zed", "z_code"],
        "configFile": "settings.json",
        "configPath": "~/.config/zed/settings.json (context_servers)",
    },
    "opencode": {
        "id": "opencode",
        "name": "OpenCode",
        "is_cli": True,
        "alias": ["opencode", "open_code"],
        "configFile": "opencode_mcp.json",
        "configPath": "opencode_mcp.json",
    },
    "antigravity": {
        "id": "antigravity",
        "name": "Antigravity",
        "is_cli": False,
        "alias": ["antigravity", "agy"],
        "configFile": "mcp.json",
        "configPath": "~/.config/antigravity/mcp.json",
    },
    "codex": {
        "id": "codex",
        "name": "Codex",
        "is_cli": True,
        "alias": ["codex", "openai_codex"],
        "configFile": "codex_mcp.json",
        "configPath": "codex_mcp.json",
    },
}


def normalize_platform_key(platform: str) -> str:
    p = (platform or "").strip().lower().replace("-", "_").replace(" ", "_")
    for key, meta in PLATFORM_METADATA.items():
        if p == key or p in meta["alias"]:
            return key
    return "claude_code"


def default_env_block() -> dict[str, str]:
    return {
        "NOTION_TOKEN": "<your_notion_token>",
        "NOTION_DATABASE_ID": "<optional_notion_database_id>",
        "GMAIL_USER": "<your_gmail_address>",
        "GMAIL_APP_PASSWORD": "<your_gmail_app_password>",
        "GMAIL_TO": "<where_to_send_alerts>",
        "FORGE_HEADLESS": "0",
    }


def generate_export_for_platform(
    platform: str,
    mcp_name: str,
    server_path: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    key = normalize_platform_key(platform)
    env_vars = env or default_env_block()
    clean_path = str(server_path).replace("\\", "/")

    if key == "claude_code":
        return {
            "platform_id": "claude_code",
            "platform": "Claude Code",
            "is_cli": True,
            "command": f"claude mcp add {mcp_name} -- python {clean_path}",
            "config_file": "claude_desktop_config.json",
            "config_path": "%APPDATA%/Claude/claude_desktop_config.json",
            "config": {
                "mcpServers": {
                    mcp_name: {
                        "command": "python",
                        "args": [clean_path],
                        "env": env_vars,
                    }
                }
            },
            "instructions": f"Run `claude mcp add {mcp_name} -- python {clean_path}` in your terminal.",
        }

    if key == "codex":
        return {
            "platform_id": "codex",
            "platform": "Codex",
            "is_cli": True,
            "command": f"codex mcp add {mcp_name} -- python {clean_path}",
            "config_file": "codex_mcp.json",
            "config_path": "codex_mcp.json",
            "config": {
                "mcpServers": {
                    mcp_name: {
                        "command": "python",
                        "args": [clean_path],
                        "env": env_vars,
                    }
                }
            },
            "instructions": f"Run `codex mcp add {mcp_name} -- python {clean_path}` in your terminal.",
        }

    if key == "opencode":
        return {
            "platform_id": "opencode",
            "platform": "OpenCode",
            "is_cli": True,
            "command": f"opencode mcp add {mcp_name} -- python {clean_path}",
            "config_file": "opencode_mcp.json",
            "config_path": "opencode_mcp.json",
            "config": {
                "mcp": {
                    "servers": {
                        mcp_name: {
                            "type": "stdio",
                            "command": "python",
                            "args": [clean_path],
                            "env": env_vars,
                        }
                    }
                }
            },
            "instructions": f"Run `opencode mcp add {mcp_name} -- python {clean_path}` in your terminal.",
        }

    if key == "cursor":
        return {
            "platform_id": "cursor",
            "platform": "Cursor",
            "is_cli": False,
            "command": None,
            "config_file": ".cursor/mcp.json",
            "config_path": ".cursor/mcp.json",
            "config": {
                "mcpServers": {
                    mcp_name: {
                        "command": "python",
                        "args": [clean_path],
                        "env": env_vars,
                    }
                }
            },
            "instructions": "Copy this JSON config into your project's .cursor/mcp.json and reload Cursor.",
        }

    if key == "zcode":
        return {
            "platform_id": "zcode",
            "platform": "Z Code (Zed)",
            "is_cli": False,
            "command": None,
            "config_file": "settings.json",
            "config_path": "~/.config/zed/settings.json (context_servers)",
            "config": {
                "context_servers": {
                    mcp_name: {
                        "command": {
                            "path": "python",
                            "args": [clean_path],
                            "env": env_vars,
                        }
                    }
                }
            },
            "instructions": "Add this JSON snippet to settings.json under `context_servers` in Zed.",
        }

    # antigravity
    return {
        "platform_id": "antigravity",
        "platform": "Antigravity",
        "is_cli": False,
        "command": None,
        "config_file": "mcp.json",
        "config_path": "~/.config/antigravity/mcp.json",
        "config": {
            "mcpServers": {
                mcp_name: {
                    "command": "python",
                    "args": [clean_path],
                    "env": env_vars,
                }
            }
        },
        "instructions": "Add this configuration into ~/.config/antigravity/mcp.json or Antigravity MCP settings.",
    }


def generate_all_export_configs(
    mcp_name: str,
    server_path: str,
    env: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Generate configs for all 6 supported platforms."""
    return {
        key: generate_export_for_platform(key, mcp_name, server_path, env)
        for key in VALID_PLATFORMS
    }


def generate_export_scripts(mcp_name: str, server_path: str) -> tuple[str, str]:
    """Generate export.bat (Windows) and export.sh (POSIX) scripts."""
    clean_path = str(server_path).replace("\\", "/")

    bat_content = f"""@echo off
REM FORGE 1-Click Multi-Agent MCP Exporter (Windows)
setlocal EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
set "LOCAL_SERVER=%SCRIPT_DIR%server.py"
if exist "!LOCAL_SERVER!" (
    set "RUN_PATH=!LOCAL_SERVER:\\=/!"
) else (
    set "RUN_PATH={clean_path}"
)

echo ========================================================
echo Exporting MCP Server '{mcp_name}' to AI Agents...
echo Server Path: !RUN_PATH!
echo ========================================================

echo [1/3] Adding to Claude Code...
where claude >nul 2>nul
if %errorlevel%==0 (
    claude mcp add {mcp_name} -- python "!RUN_PATH!"
    echo [OK] Claude Code configured.
) else (
    echo [SKIP] Claude Code CLI not installed.
)

echo [2/3] Adding to Codex...
where codex >nul 2>nul
if %errorlevel%==0 (
    codex mcp add {mcp_name} -- python "!RUN_PATH!"
    echo [OK] Codex configured.
) else (
    echo [SKIP] Codex CLI not installed.
)

echo [3/3] Adding to OpenCode...
where opencode >nul 2>nul
if %errorlevel%==0 (
    opencode mcp add {mcp_name} -- python "!RUN_PATH!"
    echo [OK] OpenCode configured.
) else (
    echo [SKIP] OpenCode CLI not installed.
)

echo.
echo For Cursor, Zed, and Antigravity, see export_configs.json for copy-paste configuration.
echo Done!
"""

    sh_content = f"""#!/usr/bin/env bash
# FORGE 1-Click Multi-Agent MCP Exporter (Linux / macOS)
set -e
DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" >/dev/null 2>&1 && pwd)"
if [ -f "$DIR/server.py" ]; then
    RUN_PATH="$DIR/server.py"
else
    RUN_PATH="{clean_path}"
fi

echo "========================================================"
echo "Exporting MCP Server '{mcp_name}' to AI Agents..."
echo "Server Path: $RUN_PATH"
echo "========================================================"

if command -v claude &> /dev/null; then
    echo "[1/3] Adding to Claude Code..."
    claude mcp add {mcp_name} -- python "$RUN_PATH" || true
else
    echo "[SKIP] Claude Code CLI not found."
fi

if command -v codex &> /dev/null; then
    echo "[2/3] Adding to Codex..."
    codex mcp add {mcp_name} -- python "$RUN_PATH" || true
else
    echo "[SKIP] Codex CLI not found."
fi

if command -v opencode &> /dev/null; then
    echo "[3/3] Adding to OpenCode..."
    opencode mcp add {mcp_name} -- python "$RUN_PATH" || true
else
    echo "[SKIP] OpenCode CLI not found."
fi

echo ""
echo "For Cursor, Zed, and Antigravity, see export_configs.json for JSON configuration."
echo "Done!"
"""

    return bat_content, sh_content
