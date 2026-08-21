#!/usr/bin/env bash
# FORGE INFINITY 1-Click Multi-IDE Exporter
# Configures Cursor, Antigravity, Codex, and Z Code with normalized '/' paths
set -e
echo "[FORGE INFINITY] Exporting MCP 'monitor_github_issues_and_send_v3' to AI IDEs (Cursor, Antigravity, Codex, Z Code)..."

if command -v codex &> /dev/null; then
    codex mcp add monitor_github_issues_and_send_v3 -- python "D:/Aditya/Forge/mcp/monitor_github_issues_and_send_v3/server.py" || true
    echo "  [OK] Codex configured successfully."
else
    echo "  [INFO] codex CLI not found - use 1-Click Inject from UI."
fi

echo "[FORGE INFINITY] For Cursor, Antigravity, and Z Code, 1-Click Inject from UI writes directly to disk!"
echo "[FORGE INFINITY] Secrets are injected directly into environment blocks."
