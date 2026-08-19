@echo off
REM FORGE INFINITY 1-Click Multi-IDE Exporter
REM Configures Claude Code, Codex, and OpenCode with normalized '/' paths
echo [FORGE INFINITY] Exporting MCP 'forge-aurum-hub' to AI IDEs...

REM Claude Code
claude mcp add forge-aurum-hub -- python "D:/Aditya/Forge/forge/mcp/forge_aurum_hub/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Claude Code configured successfully.
) else (
    echo   [INFO] claude CLI not found or already configured.
)

REM Codex
codex mcp add forge-aurum-hub -- python "D:/Aditya/Forge/forge/mcp/forge_aurum_hub/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] Codex configured successfully.
)

REM OpenCode
opencode mcp add forge-aurum-hub -- python "D:/Aditya/Forge/forge/mcp/forge_aurum_hub/server.py" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   [OK] OpenCode configured successfully.
)

echo [FORGE INFINITY] For Antigravity, Z Code, Cursor, and Windsurf, copy snippets from forge.mcp.json!
pause
