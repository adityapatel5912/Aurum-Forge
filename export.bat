@echo off
REM FORGE INFINITY 1-Click Multi-IDE Exporter
REM Configures Claude Code, Codex, and OpenCode with normalized '/' paths
echo [FORGE INFINITY] Exporting MCP 'chain_research' to AI IDEs...

REM Claude Code
claude mcp add chain_research -- python "/app/mcp_registry/servers/chain_research/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Claude Code configured successfully.
) else (
    echo   [INFO] claude CLI not found or already configured.
)

REM Codex
codex mcp add chain_research -- python "/app/mcp_registry/servers/chain_research/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Codex configured successfully.
)

REM OpenCode
opencode mcp add chain_research -- python "/app/mcp_registry/servers/chain_research/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] OpenCode configured successfully.
)

echo [FORGE INFINITY] For Antigravity, Z Code, Cursor, and Windsurf, copy snippets from forge.mcp.json!
pause
