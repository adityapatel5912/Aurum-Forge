"""FORGE INFINITY Factory MCP Server — Standalone Entrypoint.

Plug directly into any IDE:
- Antigravity: Add to ~/.antigravity/mcp.json
- Z Code (Zed): Add to ~/.zcode/mcp.json
- Claude Code: claude mcp add forge-factory -- python <this_file>
- Cursor: Add to .cursor/mcp.json
- Windsurf: Add to ~/.codeium/windsurf/mcp_config.json
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.factory.factory_mcp import mcp

if __name__ == "__main__":
    if "--list-tools" in sys.argv:
        import asyncio
        import json

        names = [t.name for t in asyncio.run(mcp.list_tools())]
        print(json.dumps(names, indent=2))
        raise SystemExit(0)
    mcp.run()
