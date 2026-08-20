---
name: test-bridge
description: Universal Skill Bridge Test
version: 1.0.0
mcp_server: test-bridge
aurum_badge: "AURUM GOLD (#C6A96B)"
compatible_ides:
  - Antigravity
  - Z Code
  - Claude Code
  - Cursor
  - Windsurf
  - OpenCode
  - Codex
---

# Universal Skill: Universal Skill Bridge Test

## 1. Overview & Golden Badge
- **MCP Server Name**: `test-bridge`
- **Server Path**: `mcp/test-bridge/server.py`
- **Aurum Verification**: Gold Verified `#C6A96B` (Self-Heal Active, Deterministic <2.1s, 0 Token Cost)
- **Target Goal**: Universal Skill Bridge Test

## 2. FastMCP Tool Manifest
- `test_tool` [AURUM GOLD]: Test tool

## 3. Levelled Workflow DAG
```json
{}
```

## 4. Execution Protocol for AI Agents
When the user requests **"Universal Skill Bridge Test"** or asks to execute this workflow:
1. **Direct Invocation**: Use the tools exposed by `test-bridge` directly. Do not guess parameters or synthesize ad-hoc browser scripts.
2. **Topological Order**: Follow the DAG stages. Feed output payloads from Trigger -> Process -> Output nodes.
3. **Resilience**: If a locator encounters a dynamic DOM change, the built-in 2-locator fallback self-heals in `<200ms`.

## 5. Universal IDE Configuration
Connect this skill to your favorite IDE with 1-click via `forge.mcp.json`:
- **Antigravity**: Add `test-bridge` to `~/.antigravity/mcp.json`
- **Z Code**: Add `test-bridge` to `settings.json` under `mcpServers`
- **Claude Code**: Run `claude mcp add test-bridge -- python "mcp/test-bridge/server.py"`
- **Cursor / Windsurf**: Add to `.cursor/mcp.json` or `.codeium/windsurf/mcp_config.json`
