"""Custom Forge Registry MCP — Meta MCP that exposes all forged MCPs and skills.

Allows any AI Agent (Claude Code, Cursor, Zed, OpenCode, Antigravity, Codex)
to query, inspect, and export MCP servers and performance-optimized SKILL.md files.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastmcp import FastMCP
from forge.history import (
    get_all_history,
    get_history_by_id,
    load_forge_registry,
    search_history as search_history_entries,
)
from forge.exporter import generate_all_export_configs, generate_export_for_platform, normalize_platform_key

mcp = FastMCP("forge-registry")

# Ensure export_configs.json exists for this registry MCP itself
REGISTRY_SERVER_PATH = str(Path(__file__).resolve()).replace("\\", "/")
REGISTRY_EXPORT_CONFIGS = generate_all_export_configs("forge-registry", REGISTRY_SERVER_PATH)
try:
    (Path(__file__).parent / "export_configs.json").write_text(
        json.dumps(REGISTRY_EXPORT_CONFIGS, indent=2), "utf-8"
    )
except Exception:
    pass


@mcp.tool()
def list_forged_mcps(limit: int = 10) -> str:
    """List all MCP servers generated in Forge — history like chat history."""
    entries = get_all_history()
    limit = max(1, min(limit, 50))
    sliced = entries[:limit]
    if not sliced:
        return "No history yet. Forge a workflow in Forge UI or CLI first."

    summary = []
    for item in sliced:
        tools_list = item.get("tools", [])
        clean_path = str(item.get("abs_path", "")).replace("\\", "/")
        summary.append(
            {
                "id": item.get("id"),
                "timestamp": item.get("timestamp"),
                "goal": item.get("goal"),
                "mcp_name": item.get("mcp_name", "unified-forge"),
                "tool_count": len(tools_list),
                "tools": tools_list,
                "abs_path": clean_path,
            }
        )
    return json.dumps(summary, indent=2, ensure_ascii=False)


@mcp.tool()
def get_mcp_details(id: str) -> str:
    """Get details of a specific forged MCP by id."""
    entry = get_history_by_id(id.strip())
    if not entry:
        return f"Error: No forged MCP found with id '{id}'"
    clean_entry = dict(entry)
    if clean_entry.get("abs_path"):
        clean_entry["abs_path"] = str(clean_entry["abs_path"]).replace("\\", "/")
    if clean_entry.get("zip_path"):
        clean_entry["zip_path"] = str(clean_entry["zip_path"]).replace("\\", "/")
    return json.dumps(clean_entry, indent=2, ensure_ascii=False)


@mcp.tool()
def get_skill(id: str) -> str:
    """Get the single SKILL.md for that workflow — for agent performance."""
    entry = get_history_by_id(id.strip())
    if not entry:
        return f"Error: No forged MCP found with id '{id}'"
    skill = entry.get("skill_content")
    if not skill:
        return f"No SKILL.md stored for MCP '{id}'"
    return skill


@mcp.tool()
def search_mcps(query: str) -> str:
    """Search forged MCPs by goal text or tool name — e.g., 'RAM' or 'hackathon'."""
    results = search_history_entries(query)
    if not results:
        return f"No forged MCPs found matching query: '{query}'"
    summary = [
        {
            "id": r.get("id"),
            "timestamp": r.get("timestamp"),
            "goal": r.get("goal"),
            "tools": r.get("tools", []),
            "abs_path": str(r.get("abs_path", "")).replace("\\", "/"),
        }
        for r in results
    ]
    return json.dumps(summary, indent=2, ensure_ascii=False)


@mcp.tool()
def export_mcp_to_platform(id: str, platform: str) -> str:
    """Export MCP Server to Claude Code, Cursor, ZCode, OpenCode, Antigravity, Codex.
    
    platform: claude_code, cursor, zcode, opencode, antigravity, codex
    Returns command and json config.
    """
    entry = get_history_by_id(id.strip())
    if not entry:
        return f"Error: No forged MCP found with id '{id}'"

    server_path = str(entry.get("abs_path") or "").replace("\\", "/")
    mcp_name = entry.get("mcp_name") or "unified-forge"
    export_data = generate_export_for_platform(platform, mcp_name, server_path)
    return json.dumps(export_data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if "--list-tools" in sys.argv:
        import asyncio

        names = [t.name for t in asyncio.run(mcp.list_tools())]
        print(json.dumps(names, indent=2))
        raise SystemExit(0)
    mcp.run()
