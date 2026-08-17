# FORGE — Self-Forging Browser Workforce

> **Turn Any Website Into A Reusable MCP Server. One Server Operates Everything.**
>
> Tell FORGE *why* you need MCPs, add any custom sites, toggle the official MCPs you
> already use — FORGE generates **ONE unified `server.py`** (plus a config-once ZIP).
> After a one-time config, you just say: **"Use unified-forge at D:\...\server.py"**
> and it works in Claude Desktop / Cursor.

---

## Quick Start

```bash
# 1) install backend deps
pip install -r requirements.txt
python -m playwright install chromium

# 2) keys (already present in .env — see .env.example)
#    GROQ_API_KEY / NVIDIA_API_KEY / GOOGLE_API_KEY / OPENROUTER_API_KEY

# 3) CLI end-to-end test (2 custom sites + 1 official)
python backend/main.py --urls https://news.ycombinator.com,https://example.com --official notion --goal "test"
# -> mcp_registry/servers/unified-mcp/server.py + dist/unified-mcp.zip

# 4) UI
python backend/main.py --serve --port 8740     # API + built UI at http://127.0.0.1:8740
# or dev mode:
cd frontend && npm install && npm run dev      # http://localhost:5173 (proxies /api -> 8740)
```

## The Config-Once Flow

1. Type your goal, add site URLs, toggle officials, hit **FORGE UNIFIED MCP SERVER**
2. Download `dist/unified-mcp.zip` — it contains `unified-mcp/server.py`,
   `requirements.txt`, `README.md`, `claude_config_snippet.json`,
   `cursor_config_snippet.json` (absolute path auto-filled)
3. Unzip → `pip install -r requirements.txt && playwright install chromium`
4. Paste the snippet into `claude_desktop_config.json`
   (Windows `%APPDATA%/Claude/` · macOS `~/Library/Application Support/Claude/`)
5. Restart Claude → **"Use unified-forge at D:\...\server.py"** — done, forever.

## Architecture

```
UI (React/Vite/Tailwind)  ──POST /api/forge──▶  pipeline (backend/pipeline.py)
                                                │
   ┌────────────┬──────────────┬────────────────┼───────────────┬─────────────┐
   ▼            ▼              ▼                ▼               ▼             ▼
 scout       forge          registry        planner         zipper       executor/healer
 headful     1 LLM call     JSON only       gpt-oss-120b    dist/        run DAG,
 stealth     per site       + official      DAG JSON        .zip         2-fallback
 2-locator   -> 5 tools     catalog                                  200ms heal
   │            │
   ▼            ▼
 logs/{site}.json   mcp_registry/servers/unified-mcp/server.py
```

**Scout** (`backend/scout/`) — headful stealth Chromium (`--disable-blink-features=AutomationControlled`,
1920x1080, real UA, 2s settle, scroll + 1s delay) captures TWO locators per element:
primary `get_by_role("button", name="Search")`, fallback CSS `button.search` → `logs/{site}.json`.

**Forge** (`backend/forge/`) — official-API domains (Gmail, Notion) are auto-detected
(`utils/detect_official.py`) and never browser-forged; Amazon is covered by
**hardcoded cores** (`cores/`: 3 amazon browser tools + 2 gmail SMTP + 2 notion REST,
injected in <2s with zero LLM calls). Every *other* custom site gets ONE codegen call
(`nvidia/poolside/laguna-xs-2.1`, chain-fallback, 30s cap) returning 2 tools as a
**validated JSON step-list** (never raw Python); Jinja2 (`templates/unified_server.py.j2`)
merges CORES + forged tools + official wrappers into ONE server with the two-locator
`_smart()` self-heal pattern and a single-return-per-tool rule. Scout and forge run in
parallel across sites.

**Planner** (`backend/planner/`) — `groq/openai/gpt-oss-120b` emits
`{"t1": {"tool": "search_siteA", "parallel": true}, "t3": {"tool": "notion_create_entry", "deps": ["t1","t2"]}}`.

**Models** (chain Groq → Nvidia → Gemini → OpenRouter, cached in `logs/llm_cache.json`):
planner `groq/openai/gpt-oss-120b` → `nvidia/nemotron-3-ultra-550b-a55b` ·
codegen `nvidia/poolside/laguna-xs-2.1` · executor `groq/llama-3.1-8b-instant` ·
vision `gemini/gemini-3.7-flash` (backup). Full list: `MODEL-ID.md`.

If every provider is down, deterministic local forging still produces a working server.

## Repo Structure

```
backend/
  config.py  llm.py  pipeline.py  main.py        # CLI + FastAPI (jobs, download, officials)
  scout/     stealth.py explorer.py              # two-locator capture (browser or virtual fallback)
  forge/     generator.py zipper.py templates/  # codegen + Jinja + dist zip
  registry/  registry.py official_mcps.json     # JSON registry + official catalog
  planner/   planner.py                         # DAG JSON
  executor/  executor.py                        # pure-Python DAG runner
  healer/    healer.py                          # 2-retry / 200ms self-heal
frontend/                                        # React + Vite + Tailwind UI
  src/components/ GoalInput CustomSitesList OfficialMCPs UnifiedOutput DAGView ConfigSnippet …
mcp_registry/servers/unified-mcp/server.py       # GENERATED unified server
logs/                                            # scout logs, llm cache/diagnostics, executions
dist/unified-mcp.zip                             # GENERATED config-once bundle
```

## Testing Checklist

```bash
# CLI: generate dist/unified-mcp.zip
python backend/main.py --urls https://news.ycombinator.com,https://example.com --official notion --goal "test"

# List tools without a client
python mcp_registry/servers/unified-mcp/server.py --list-tools

# MCP Inspector (real stdio handshake)
npx @modelcontextprotocol/inspector python mcp_registry/servers/unified-mcp/server.py

# Programmatic MCP client check
python -c "import asyncio; from fastmcp import Client;
async def m():
    async with Client('mcp_registry/servers/unified-mcp/server.py') as c:
        print([t.name for t in await c.list_tools()])
asyncio.run(m())"

# Run the planned DAG against the forged server
python backend/main.py --urls https://example.com --official notion --goal "demo" --execute
```

UI test: open http://localhost:5173 (or :8740), add 2 custom URLs + 1 official,
click FORGE → progress (Scout… Forge… Merge… Plan… Create server.py… Package zip)
→ Tools / DAG / server.py / Config tabs → **Download ZIP**.

Theme: light `#FFFBF0` · navy `#0A1931` · golden `#C6A96B`.

---
Built for Proof of Possible (20–22 Aug 2026). We don't just **use** MCPs — we **generate** them.
