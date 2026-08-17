# REQUIREMENTS.md - FORGE Dependencies Explained

## Python Dependencies (requirements.txt)

### Core MCP + Browser
- `fastmcp>=0.9.0` - Fast Pythonic MCP server framework (we generate these)
- `mcp>=1.0.0` - Official MCP SDK
- `playwright>=1.48.0` - Headless browser automation (core of Scout)
- `python-dotenv>=1.0.0` - Load .env keys
- `pydantic>=2.8.0` - Typed tool inputs/outputs
- `jinja2>=3.1.0` - Template for generated MCP code

### Agent + Orchestration (LangGraph)
- `langgraph>=0.2.0` - Supervisor pattern, StateGraph for orchestrator
- `langchain>=0.3.0` - Base agent framework
- `langchain-openai>=0.2.0` - OpenRouter + Nvidia use OpenAI-compatible API
- `langchain-google-genai>=2.0.0` - Gemini integration

### Browser Automation
- `browser-use>=0.1.0` - AI browser agent (Scout foundation)
- `beautifulsoup4>=4.12.0` - Fallback HTML parsing
- `stagehand>=0.1.0` (optional) - Browserbase AI vision locators

### Free Tier LLM Providers (Your Keys)
- `groq>=0.11.0` - Groq client (openai/gpt-oss-120b, qwen3.6-27b, llama-3.3-70b)
- `openai>=1.50.0` - Used for OpenRouter + Nvidia (both OpenAI-compatible)
- `google-generativeai>=0.8.0` - Gemini 3.7 Flash, 3.5 Flash Lite

### Memory + Storage
- `chromadb>=0.5.0` - Site knowledge (selectors that worked, flows)
- `sqlalchemy>=2.0.0` - Registry DB abstraction

### Utils
- `httpx>=0.27.0` - Async HTTP
- `rich>=13.0.0` - Pretty logs for orchestrator
- `typer>=0.12.0` - CLI for scout.py, forge.py

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
playwright install-deps
```

## Frontend Dependencies (frontend/package.json)

- `next@14.2.5` - React framework
- `react@^18` + `react-dom@^18` - UI
- `reactflow@^11.10.0` - Live DAG visualization (orchestration graph)
- `@modelcontextprotocol/sdk@^1.0.0` - MCP client in browser
- `tailwindcss@^3.4.1` - Styling

```bash
cd frontend
npm install
npm run dev
```

## Model Requirements (MODEL_ID.md)

You must have in .env:
- OPENROUTER_API_KEY (for gemma-4-31b-it:free)
- NVIDIA_API_KEY (for nemotron-3-ultra, laguna-xs, muse-glimmer)
- GROQ_API_KEY (for gpt-oss-120b, qwen3.6-27b, llama-3.3-70b)
- GEMINI_API_KEY (for gemini-3.7-flash, gemini-3.5-flash-lite)

All models listed in MODEL_ID.md are free-tier compatible.

## System Requirements

- Python 3.10+
- Node 18+
- 8GB RAM (for Playwright + Chroma)
- Docker (optional, for MCP registry)
