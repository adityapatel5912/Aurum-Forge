# DEPENDENCIES.md - External GitHub Repos + Setup

FORGE is built ON TOP of these open-source projects. You don't need to fork them, just reference.

## Core External Repos (Clone for reference)

### 1. browser-use - AI Browser Agent Foundation
- **Repo:** https://github.com/browser-use/browser-use
- **Why FORGE uses it:** Scout uses browser-use to explore unknown sites, capture accessibility tree + screenshots + actions. It's more robust than raw Playwright.
- **Install:** `pip install browser-use`
- **Clone:** `git clone https://github.com/browser-use/browser-use.git external/browser-use`

### 2. FastMCP - Fast Pythonic MCP Framework
- **Repo:** https://github.com/jlowin/fastmcp
- **Why:** Our Forge generates FastMCP servers (not low-level MCP SDK). FastMCP is simpler: `@mcp.tool()` decorator.
- **Install:** `pip install fastmcp`
- **Clone:** `git clone https://github.com/jlowin/fastmcp.git external/fastmcp`

### 3. MCP Servers (Official) - Playwright Reference
- **Repo:** https://github.com/modelcontextprotocol/servers/tree/main/src/playwright
- **Why:** Bootstrap `browser-mcp` and reference for how official Playwright MCP handles 3-fallback locators. Your forged MCPs should mimic its structure.
- **NPM:** `npx @modelcontextprotocol/server-playwright`
- **Clone:** `git clone https://github.com/modelcontextprotocol/servers.git external/mcp-servers`

### 4. LangGraph - Orchestration & Supervisor Pattern
- **Repo:** https://github.com/langchain-ai/langgraph
- **Why:** Orchestrator uses StateGraph + Supervisor pattern (planner -> executor -> verifier). LangGraph is industry standard for agentic orchestration.
- **Install:** `pip install langgraph`
- **Clone:** `git clone https://github.com/langchain-ai/langgraph.git external/langgraph`

### 5. Stagehand (Optional, Alternative to browser-use)
- **Repo:** https://github.com/browserbase/stagehand
- **Why:** Provides AI vision + self-healing locators (AI-act, AI-extract). Good fallback if browser-use fails on dynamic sites like One8.
- **Install:** `npm install @browserbasehq/stagehand`
- **Clone:** `git clone https://github.com/browserbase/stagehand.git external/stagehand`

## Clone All At Once

```bash
bash scripts/clone_external.sh
```

Script:
```bash
#!/bin/bash
mkdir -p external
cd external
git clone https://github.com/browser-use/browser-use.git || true
git clone https://github.com/jlowin/fastmcp.git || true
git clone https://github.com/modelcontextprotocol/servers.git || true
git clone https://github.com/langchain-ai/langgraph.git || true
git clone https://github.com/browserbase/stagehand.git || true
cd ..
```

## Playwright Setup (Required)

```bash
playwright install
playwright install-deps  # Linux deps
```

## MCP Inspector (Test Forged MCPs)

Test if your forged MCP works:

```bash
npx @modelcontextprotocol/inspector python mcp_registry/servers/unstop-mcp/server.py
```

Should show tools like `search_hackathons`, `get_details`.

## Claude Desktop Integration (Prove Reusability)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unstop": {
      "command": "python",
      "args": ["/absolute/path/to/FORGE/mcp_registry/servers/unstop-mcp/server.py"]
    },
    "one8": {
      "command": "python",
      "args": ["/absolute/path/to/FORGE/mcp_registry/servers/one8-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop — now you can ask Claude: "Search Unstop for AI hackathons"

## Why These Dependencies?

- **browser-use + Playwright** = Scout can handle dynamic React sites (Unstop, One8 are React)
- **FastMCP** = Generated servers are readable, typed, easy to debug (judges can read code)
- **LangGraph** = Orchestration graph visualization is your WOW factor
- **MCP Inspector** = Prove forged MCP is valid MCP (not just a script)

All are MIT/Apache licensed, hackathon-safe.
