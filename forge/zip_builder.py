"""FORGE zip generator — packages the config-once bundle into dist/unified-mcp.zip.

ZIP contents (Root level, NO 6-platform subfolders):
  server.py           — the ONE unified MCP server
  SKILL.md            — ONE performance-optimized workflow skill
  requirements.txt    — fastmcp, playwright, httpx
  export_configs.json — 6-way agent export configurations (Claude, Cursor, Zed, OpenCode, Antigravity, Codex)
  export.bat          — 1-click Windows multi-agent exporter
  export.sh           — 1-click Unix/macOS multi-agent exporter
  README.md           — 5-step CONFIG ONCE instructions
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from backend.config import DIST_DIR, ROOT, SERVER_NAME, UNIFIED_SERVER_DIR, VERSION, ensure_dirs
from forge.exporter import default_env_block, generate_all_export_configs, generate_export_scripts
from forge.skills.single_skill_generator import generate_single_skill

ROOT_FORGE_DIR = ROOT

ZIP_REQUIREMENTS = "fastmcp>=2.3.0\nplaywright>=1.48.0\nhttpx>=0.27.0\n"

README_TEMPLATE = """# FORGE UNIFIED MCP — CONFIG ONCE

One server ({server_name}) operates {n_sites} custom site(s) + {n_officials} official MCP(s).
{tools_line}

## Setup — one time only

1. Unzip this archive anywhere you like.
2. Install dependencies:
   ```
   pip install -r requirements.txt && playwright install chromium
   ```
3. Export to your AI Agent:
   - Run `export.bat` (Windows) or `bash export.sh` (macOS / Linux) to configure Claude Code, Codex, and OpenCode automatically.
   - For Cursor, Zed, and Antigravity: consult `export_configs.json` for ready-to-use JSON blocks.
4. Workflow Skill:
   `SKILL.md` is provided at the root as the single source of truth for your agent.

## Official MCP tokens

{tokens_section}

## Test without any client

```
npx @modelcontextprotocol/inspector python server.py
```
or simply:
```
python server.py --list-tools
```

## Hardcoded core tools (always included, no LLM was used)

{core_tools}

## Forged tools (browser automation, two-locator self-healing)

{forged_tools}

## Official wrappers

{official_tools}

---
Forged by FORGE v{version} — Turn Any Website Into A Reusable MCP Server.
"""


def build_zip(
    server_py: str,
    server_abs_path: str,
    officials: list[dict],
    manifest: list[dict],
    dag: dict[str, Any] | None = None,
    goal: str = "",
    out_zip: Path | None = None,
    server_name: str | None = None,
    skill_dir: Path | None = None,
    include_universal_config: bool = True,
) -> tuple[Path, dict, dict, str, str, dict]:
    """Create dist/<name>.zip with single SKILL.md, export_configs.json, and export scripts.

    When ``server_name``/``skill_dir`` are provided (Factory mode), the single
    root SKILL.md is also written into the per-MCP directory. The universal
    forge.mcp.json is embedded in the archive when present.

    Returns (zip_path, claude_snippet, cursor_snippet, readme, skill_content, export_configs).
    """
    ensure_dirs()
    active_name = server_name or SERVER_NAME
    out_zip = out_zip or (DIST_DIR / "unified-mcp.zip")
    server_clean_path = str(server_abs_path).replace("\\", "/")

    forged = [t for t in manifest if t.get("badge") == "FORGED"]
    official = [t for t in manifest if t.get("badge") == "OFFICIAL"]
    core = [t for t in manifest if t.get("badge") == "CORE"]
    n_sites = len({t.get("source") for t in forged})
    n_officials = len({t.get("source") for t in official})

    env_block: dict[str, str] = {}
    for o in officials:
        if o.get("token_env"):
            env_block[o["token_env"]] = f"<your_{o['token_env'].lower()}>"
    if any(o.get("kind") == "notion" for o in officials):
        env_block.setdefault("NOTION_PARENT_PAGE", "<optional_notion_parent_page_id>")

    env_block.setdefault("NOTION_TOKEN", "<your_notion_token>")
    env_block.setdefault("NOTION_DATABASE_ID", "<optional_notion_database_id>")
    env_block.setdefault("GMAIL_USER", "<your_gmail_address>")
    env_block.setdefault("GMAIL_APP_PASSWORD", "<your_gmail_app_password>")
    env_block.setdefault("GMAIL_TO", "<where_to_send_alerts>")
    env_block.setdefault("FORGE_HEADLESS", "0")

    # 1. Single SKILL.md (written next to the server so each MCP dir is self-contained)
    skill_content = generate_single_skill(goal, manifest, dag, active_name)
    skill_file_dest = (skill_dir or UNIFIED_SERVER_DIR) / "SKILL.md"
    skill_file_dest.parent.mkdir(parents=True, exist_ok=True)
    skill_file_dest.write_text(skill_content, "utf-8")

    # 2. 6-Way Export Configs and Scripts
    export_configs = generate_all_export_configs(active_name, server_clean_path, env_block)
    bat_script, sh_script = generate_export_scripts(active_name, server_clean_path)

    cursor_snippet = export_configs.get("cursor", {}).get("config", {})
    antigravity_snippet = export_configs.get("antigravity", {}).get("config", {})

    tokens_section = (
        "\n".join(
            [
                "- `NOTION_TOKEN` / `NOTION_DATABASE_ID` — Notion core (log_price, create entry)",
                "- `GMAIL_USER` / `GMAIL_APP_PASSWORD` / `GMAIL_TO` — Gmail core (SMTP app password)",
                *(f"- `{o['token_env']}` — for the {o['name']} wrapper you selected" for o in officials if o.get("token_env")),
            ]
        )
        or "- None selected — this server is pure browser automation, no tokens needed."
    )
    readme = README_TEMPLATE.format(
        server_name=active_name,
        n_sites=n_sites,
        n_officials=n_officials,
        tools_line=f"{len(core)} core + {len(forged)} forged + {len(official)} official = {len(manifest)} tools total.",
        abs_path=server_clean_path,
        tokens_section=tokens_section,
        core_tools="\n".join(f"- `{t['name']}` — {t['source']} (hardcoded, always available)" for t in core) or "- none",
        forged_tools="\n".join(f"- `{t['name']}` — {t['source']}" for t in forged) or "- none",
        official_tools="\n".join(f"- `{t['name']}` — {t['source']}" for t in official) or "- none",
        version=VERSION,
    )

    export_json_str = json.dumps(export_configs, indent=2, ensure_ascii=False)

    # Universal config (forge.mcp.json) embedded so any machine can 1-click connect
    universal_config_bytes = b""
    if include_universal_config:
        universal_cfg = ROOT_FORGE_DIR / "forge.mcp.json"
        if universal_cfg.exists():
            universal_config_bytes = universal_cfg.read_bytes()

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # Root level files (single SKILL.md, no subfolders for 6 platforms)
        zf.writestr("server.py", server_py)
        zf.writestr("SKILL.md", skill_content)
        zf.writestr("requirements.txt", ZIP_REQUIREMENTS)
        zf.writestr("export_configs.json", export_json_str)
        zf.writestr("export.bat", bat_script)
        zf.writestr("export.sh", sh_script)
        zf.writestr("README.md", readme)
        if universal_config_bytes:
            zf.writestr("forge.mcp.json", universal_config_bytes)
        # Also include unified-mcp/ folder prefix for archive tools
        zf.writestr("unified-mcp/server.py", server_py)
        zf.writestr("unified-mcp/SKILL.md", skill_content)
        zf.writestr("unified-mcp/requirements.txt", ZIP_REQUIREMENTS)
        zf.writestr("unified-mcp/export_configs.json", export_json_str)
        zf.writestr("unified-mcp/export.bat", bat_script)
        zf.writestr("unified-mcp/export.sh", sh_script)
        zf.writestr("unified-mcp/README.md", readme)
        if universal_config_bytes:
            zf.writestr("unified-mcp/forge.mcp.json", universal_config_bytes)

    return out_zip, antigravity_snippet, cursor_snippet, readme, skill_content, export_configs
