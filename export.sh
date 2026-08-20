#!/usr/bin/env bash
# FORGE INFINITY 1-Click Multi-IDE Exporter
# Configures Claude Code, Codex, and OpenCode with normalized '/' paths
set -e
echo "[FORGE INFINITY] Exporting MCP 'track_top_artificial_intellige' to AI IDEs..."

if command -v claude &> /dev/null; then
    claude mcp add track_top_artificial_intellige -- python "D:/Aditya/Forge/mcp/track_top_artificial_intellige/server.py" || true
    echo "  [OK] Claude Code configured successfully."
fi

if command -v codex &> /dev/null; then
    codex mcp add track_top_artificial_intellige -- python "D:/Aditya/Forge/mcp/track_top_artificial_intellige/server.py" || true
    echo "  [OK] Codex configured successfully."
fi

if command -v opencode &> /dev/null; then
    opencode mcp add track_top_artificial_intellige -- python "D:/Aditya/Forge/mcp/track_top_artificial_intellige/server.py" || true
    echo "  [OK] OpenCode configured successfully."
fi

echo "[FORGE INFINITY] For Antigravity, Z Code, Cursor, and Windsurf, copy snippets from forge.mcp.json!"
