@echo off
REM FORGE INFINITY 1-Click Multi-IDE Exporter
REM Configures Cursor, Antigravity, Codex, and Z Code with normalized '/' paths
echo [FORGE INFINITY] Exporting MCP 'monitor_github_issues_and_send_v3' to AI IDEs (Cursor, Antigravity, Codex, Z Code)...

REM Codex CLI auto-configuration
where codex >nul 2>nul
if %ERRORLEVEL% equ 0 (
    codex mcp add monitor_github_issues_and_send_v3 -- python "D:/Aditya/Forge/mcp/monitor_github_issues_and_send_v3/server.py" 2>nul
    echo   [OK] Codex configured successfully.
) else (
    echo   [INFO] codex CLI not in PATH - use 1-Click Inject from UI.
)

echo [FORGE INFINITY] For Cursor, Antigravity, and Z Code, 1-Click Inject from UI writes directly to disk!
echo [FORGE INFINITY] Secrets are injected directly into environment blocks.
