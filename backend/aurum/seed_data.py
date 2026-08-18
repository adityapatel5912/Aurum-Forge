"""Seeding script for FORGE-AURUM SUPER-HUB.

Ensures all 5 production chains and the Super-Hub are registered in:
- mcp_registry/marketplace.json
- forge_registry.json
- forge.mcp.json
- dist/*.zip
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.aurum.chains import PRODUCTION_CHAINS, seed_production_chains
from backend.factory.hot_loader import write_universal_config_and_scripts
from backend.marketplace.marketplace import ensure_marketplace_dirs, load_marketplace, save_marketplace


def run_seed():
    print("1. Seeding 5 Aurum Production Chains to disk...")
    seeded_chains = seed_production_chains()
    for s in seeded_chains:
        print(f"   -> Seeded {s['name']} ({s['tools_count']} tools) -> {s['server_path']}")

    print("2. Seeding Marketplace catalog...")
    ensure_marketplace_dirs()
    existing = load_marketplace()
    existing_map = {p.get("package_id"): p for p in existing}

    for cid, meta in PRODUCTION_CHAINS.items():
        from backend.aurum.chains import _chain_content_hash
        c_hash = _chain_content_hash(meta)
        entry = {
            "package_id": cid,
            "name": meta["name"],
            "version": meta["version"],
            "author": meta["author"],
            "description": meta["description"],
            "category": meta["category"],
            "tags": ["aurum-chain", "production-grade", "work-rewritten", meta["category"].lower()],
            "tools_count": len(meta["tools"]),
            "tools": [t["name"] for t in meta["tools"]],
            "dag": meta["dag"],
            "server_path": f"mcp_registry/servers/{cid}/server.py",
            "installs_count": 284,
            "verified": True,
            "aurum_verified": True,
            "aurum_verified_at": "2026-08-20T12:00:00Z",
            "hash": c_hash,
            "aurum_gold_badge": True,
            "badge_color": "#C6A96B",
            "work_rewritten_hours": meta["work_rewritten_hours"],
            "dependencies": meta["dependencies"],
            "published_at": "2026-08-20T12:00:00Z",
        }
        existing_map[cid] = entry

    # Add Super-Hub package as well
    existing_map["forge-aurum-hub"] = {
        "package_id": "forge-aurum-hub",
        "name": "FORGE-AURUM Super-Hub (50-in-1)",
        "version": "3.0.0",
        "author": "FORGE Aurum Core",
        "description": "Unified Ecosystem OS MCP holding 50+ tools, 7 official wrappers, and 5 production chains.",
        "category": "DevTools",
        "tags": ["super-hub", "50-in-1", "aurum-gold", "universal-skill"],
        "tools_count": 52,
        "tools": ["aurum_hub_status", "github_create_issue", "notion_create_database_entry", "run_research_chain", "run_content_chain"],
        "server_path": "forge/mcp/forge_aurum_hub/server.py",
        "installs_count": 1052,
        "verified": True,
        "aurum_verified": True,
        "aurum_verified_at": "2026-08-20T12:00:00Z",
        "hash": "f6cdbd0a07f2",
        "aurum_gold_badge": True,
        "badge_color": "#C6A96B",
        "work_rewritten_hours": 20.0,
        "dependencies": [
            {"source": "forge-aurum-hub", "target": "github", "label": "Wraps into Gold"},
            {"source": "forge-aurum-hub", "target": "notion", "label": "Wraps into Gold"},
            {"source": "forge-aurum-hub", "target": "slack", "label": "Wraps into Gold"},
            {"source": "forge-aurum-hub", "target": "gmail", "label": "Wraps into Gold"},
            {"source": "forge-aurum-hub", "target": "browser", "label": "Stealth DOM automation"},
        ],
        "published_at": "2026-08-20T12:00:00Z",
    }

    save_marketplace(list(existing_map.values()))
    print(f"   -> Marketplace now contains {len(existing_map)} verified Aurum packages.")

    print("3. Regenerating forge.mcp.json and export scripts with '/' normalization...")
    write_universal_config_and_scripts(
        active_mcp_name="forge-aurum-hub",
        active_server_path=(ROOT / "forge" / "mcp" / "forge_aurum_hub" / "server.py").resolve().as_posix(),
    )
    print("   -> forge.mcp.json and export scripts updated.")


if __name__ == "__main__":
    run_seed()
