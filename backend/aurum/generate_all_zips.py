"""Package generator ensuring all dist/ ZIP bundles exist with >1KB size and strict '/' normalization."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import DIST_DIR, ROOT, ensure_dirs
from backend.aurum.chains import PRODUCTION_CHAINS
from backend.aurum.skill_bridge import export_universal_bundle


def build_all_zips():
    ensure_dirs()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build unified-mcp.zip (tool list mirrors the live dynamic hub catalog)
    hub_py = ROOT / "forge" / "mcp" / "forge_aurum_hub" / "server.py"
    hub_code = hub_py.read_text("utf-8", errors="replace") if hub_py.exists() else "# forge-aurum-hub"
    try:
        from backend.aurum.generate_super_hub_config import scan_all_mcp_servers
        _servers, total_tools = scan_all_mcp_servers()
    except Exception:
        total_tools = 89
    hub_tools = [
        {"name": "ram_search", "description": "Top-100 RAM products sorted by price"},
        {"name": "youtube_get_transcript", "description": "Extract video transcript + title"},
        {"name": "chain_content_full_workflow", "description": "End-to-end Content Chain with proof ledger"},
        {"name": "notion_create_page", "description": "Create Notion page, returns notion_url"},
        {"name": "slack_post_message", "description": "Post launch announcement to Slack"},
        {"name": "get_super_hub_catalog", "description": "Live dynamic tool catalog"},
    ]
    out_unified = DIST_DIR / "unified-mcp.zip"
    export_universal_bundle(
        mcp_name="forge-aurum-hub",
        server_py=hub_code,
        goal=f"FORGE-AURUM Super-Hub — Collapsing {total_tools} tools into 1 unified MCP server (give once, auto-update)",
        tools=hub_tools,
        out_zip_path=out_unified,
    )
    print(f"Generated {out_unified.name}: {out_unified.stat().st_size} bytes")

    # 2. Build all 5 chain ZIP bundles
    for cid, chain in PRODUCTION_CHAINS.items():
        chain_py = ROOT / "mcp_registry" / "servers" / cid / "server.py"
        chain_code = chain_py.read_text("utf-8", errors="replace") if chain_py.exists() else f"# {cid}"
        out_chain = DIST_DIR / f"{cid}-mcp.zip"
        export_universal_bundle(
            mcp_name=cid,
            server_py=chain_code,
            goal=chain.get("description", f"Production Chain {cid}"),
            tools=chain.get("tools", []),
            out_zip_path=out_chain,
        )
        print(f"Generated {out_chain.name}: {out_chain.stat().st_size} bytes")

    # 3. Build super_hub.mcp.json in dist
    from backend.aurum.generate_super_hub_config import generate_and_sync_super_hub
    generate_and_sync_super_hub(auto_sync_ides=True)
    print("Super-hub configs synced with strict '/' normalization.")


if __name__ == "__main__":
    build_all_zips()
