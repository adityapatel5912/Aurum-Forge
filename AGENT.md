# AGENT.md - FORGE Implementation Guide for AI Coding Agent
### Read this + MODEL_ID.md + .env before coding

## Goal
Build FORGE: System that takes URL + natural language goal, auto-generates custom MCP server for that site, and orchestrates multi-site workflows.

## Your Free Models (from MODEL_ID.md)
- planner: groq/openai/gpt-oss-120b (120B reasoner) - Use for DAG generation
- vision: gemini/gemini-3.7-flash - Use for screenshot understanding + self-heal
- codegen: nvidia/poolside/laguna-xs-2.1 - Use for generating FastMCP code
- executor: groq/llama-3.3-70b-versatile - Use for fast tool calls

Provider Init:
- gemini: genai.configure(api_key=GEMINI_API_KEY); model=GenerativeModel("gemini-3.7-flash")
- groq: Groq(api_key=GROQ_API_KEY); model id after groq/ prefix e.g. "openai/gpt-oss-120b"
- nvidia: OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
- openrouter: OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

## Architecture Details

### 1. Scout (mcp_factory/scout.py)
Input: URL
Process:
- Launch Playwright
- Use browser-use to explore: click all interactive elements, capture accessibility tree, screenshots, network logs, DOM snapshots
- Save log: {url, actions: [{type: click, selector, role, text, screenshot}], dom_snapshots: [], a11y_tree: []}
Output: logs/{site}.json

Reference external: browser-use repo examples

### 2. Forge (mcp_factory/forge.py)
Input: logs/{site}.json
Process:
- LLM codegen (codegen model) reads scout log + uses Jinja template in templates/mcp_server.py.j2
- Generates FastMCP Python server with typed tools
- Each tool must have 3-fallback locators:
  1. get_by_role (most stable)
  2. CSS selector
  3. AI Vision fallback (calls vision model to re-locate)
- Pydantic input/output models
- Self-contained Playwright code
Output: mcp_registry/servers/{site}-mcp/server.py

Template structure:
```python
from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright
mcp = FastMCP("unstop-mcp")

@mcp.tool()
def search_hackathons(query: str) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://unstop.com")
        # Locator 1: page.get_by_role("searchbox")
        # Locator 2: page.locator("input[type=search]")
        # Locator 3: vision fallback
        return [...]
```

### 3. Registry (mcp_registry/registry.py)
- SQLite DB: servers(name, url, tools_json, version, last_tested)
- File storage: servers/{name}/server.py
- Methods: register(), list(), get(), test()

### 4. Planner (orchestrator/planner.py)
Input: Natural language goal
Process:
- Call planner model (groq/openai/gpt-oss-120b) with prompt: "Break goal into DAG of MCP tool calls"
- Output JSON:
```json
{
  "goal": "Find hackathons and order tees",
  "tasks": [
    {"id": "t1", "tool": "unstop-mcp.search_hackathons", "params": {"tech": "AI"}, "deps": [], "parallel": true},
    {"id": "t2", "tool": "one8-mcp.search_products", "params": {"query": "tee"}, "deps": [], "parallel": true},
    {"id": "t3", "tool": "notion-mcp.log", "deps": ["t1","t2"], "parallel": false}
  ]
}
```

### 5. Supervisor (orchestrator/supervisor.py)
LangGraph StateGraph:
Nodes: planner_node, executor_node, verifier_node, human_gate_node, heal_node
Edges:
- planner -> executor
- executor -> verifier (if success) / heal (if fail) / human_gate (if captcha/payment)
- verifier -> END or planner (if re-plan needed)
- heal -> executor (retry with new locator)
- human_gate -> executor (after human solves)

State: {goal, dag, current_task, logs, screenshots, retries}

### 6. Executor (executor/runner.py, heal.py)
runner.py:
- Takes task, calls MCP tool via stdio
- Streams logs to UI
- Captures screenshot after each action
- On failure, calls heal.py

heal.py:
- Input: failure_screenshot, dom_snapshot, original_locator, task description
- Calls vision model (gemini-3.7-flash): "Where is the [button] now? Return new selector"
- Returns new locator, patches server.py file, retries

### 7. Frontend (frontend/app/page.tsx)
- Chat input for goal
- ReactFlow for live DAG visualization
- Log panel with screenshots
- Human-in-loop modal for captcha

## MVP Prioritization (72h)

Day 1 (20 Aug): Get ONE site forging E2E (Unstop). Scout + Forge + Registry + test in Inspector.
Day 2 (21 Aug): Build Planner + Supervisor + Frontend chat + Executor for cross-site (Unstop + One8).
Day 3 (22 Aug): Add heal.py, polish UI, record demo video, write README.

## What Judges Look For

1. Forged MCP used instantly in Claude Desktop / Cursor (prove reusability)
2. Live orchestration graph (ReactFlow / LangGraph Studio)
3. Failure + self-heal demo (WOW moment)
4. Mention: "We GENERATE MCPs"

## Files to Create First

1. mcp_factory/scout.py - integrate browser-use
2. mcp_factory/templates/mcp_server.py.j2 - Jinja template
3. mcp_factory/forge.py - codegen with MODEL_ID.md codegen model
4. mcp_registry/registry.py - simple file registry
5. orchestrator/planner.py - DAG generation with planner model
6. executor/runner.py - call MCP tools

## Testing

- Test forged MCP: npx @modelcontextprotocol/inspector python mcp_registry/servers/unstop-mcp/server.py
- Test in Claude Desktop: add to claude_desktop_config.json
- Test planner: python orchestrator/planner.py

## Deliverables

- [ ] GitHub repo clean structure
- [ ] Live demo URL (Vercel frontend + Railway backend)
- [ ] 2 min video
- [ ] Architecture diagram in README
- [ ] 3 forged MCPs in registry
- [ ] .env.example + MODEL_ID.md.example (don't commit real keys)
