---
name: chain_sales_outreach
description: Automated B2B growth engine: scrapes high-intent leads from targeted directories, tracks prospect pipeline in Google She
version: 1.0.0
mcp_server: chain_sales_outreach
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

# Universal Skill: Automated B2B growth engine: scrapes high-intent leads from targeted directories, tracks prospect pipeline in Google Sheets, dispatches personalized cold emails via Gmail, and writes lead cards to Notion CRM. Rewrites 4 hours of sales labor.

## 1. Overview & Golden Badge
- **MCP Server Name**: `chain_sales_outreach`
- **Server Path**: `mcp/chain_sales_outreach/server.py`
- **Aurum Verification**: Gold Verified `#C6A96B` (Self-Heal Active, Deterministic <2.1s, 0 Token Cost)
- **Target Goal**: Automated B2B growth engine: scrapes high-intent leads from targeted directories, tracks prospect pipeline in Google Sheets, dispatches personalized cold emails via Gmail, and writes lead cards to Notion CRM. Rewrites 4 hours of sales labor.

## 2. FastMCP Tool Manifest
- `browser_extract_leads` [AURUM GOLD]: Extracts verified prospect emails and company details
- `sheets_record_prospect` [AURUM GOLD]: Appends prospect row into Google Sheets CRM pipeline
- `gmail_send_personalized_outreach` [AURUM GOLD]: Sends personalized outreach with dynamic variables
- `notion_create_crm_entry` [AURUM GOLD]: Creates linked account page in Notion CRM database
- `run_sales_outreach_chain` [AURUM GOLD]: Executes full Sales Outreach Chain pipeline end-to-end

## 3. Levelled Workflow DAG
```json
{
  "T1_browser_leads": {
    "tool": "browser_extract_leads",
    "source": "Browser MCP",
    "category": "trigger",
    "color": "#3B82F6",
    "deps": [],
    "params": {
      "target_industry": "Developer Tools",
      "limit": 25
    }
  },
  "T2_sheets_prospect": {
    "tool": "sheets_record_prospect",
    "source": "Sheets MCP",
    "category": "process",
    "color": "#10B981",
    "deps": [
      "T1_browser_leads"
    ],
    "params": {
      "spreadsheet_id": "auto",
      "range": "Leads!A1"
    }
  },
  "T3_gmail_outreach": {
    "tool": "gmail_send_personalized_outreach",
    "source": "Gmail MCP",
    "category": "output",
    "color": "#8B5CF6",
    "deps": [
      "T2_sheets_prospect"
    ],
    "params": {
      "subject": "Empowering your team with autonomous MCPs"
    }
  },
  "T4_notion_crm": {
    "tool": "notion_create_crm_entry",
    "source": "Notion MCP",
    "category": "output",
    "color": "#C6A96B",
    "gold_pulse": true,
    "deps": [
      "T3_gmail_outreach"
    ],
    "params": {
      "title": "Company Lead Record",
      "status": "Contacted"
    }
  }
}
```

## 4. Execution Protocol for AI Agents
When the user requests **"Automated B2B growth engine: scrapes high-intent leads from targeted directories, tracks prospect pipeline in Google Sheets, dispatches personalized cold emails via Gmail, and writes lead cards to Notion CRM. Rewrites 4 hours of sales labor."** or asks to execute this workflow:
1. **Direct Invocation**: Use the tools exposed by `chain_sales_outreach` directly. Do not guess parameters or synthesize ad-hoc browser scripts.
2. **Topological Order**: Follow the DAG stages. Feed output payloads from Trigger -> Process -> Output nodes.
3. **Resilience**: If a locator encounters a dynamic DOM change, the built-in 2-locator fallback self-heals in `<200ms`.

## 5. Universal IDE Configuration
Connect this skill to your favorite IDE with 1-click via `forge.mcp.json`:
- **Antigravity**: Add `chain_sales_outreach` to `~/.antigravity/mcp.json`
- **Z Code**: Add `chain_sales_outreach` to `settings.json` under `mcpServers`
- **Claude Code**: Run `claude mcp add chain_sales_outreach -- python "mcp/chain_sales_outreach/server.py"`
- **Cursor / Windsurf**: Add to `.cursor/mcp.json` or `.codeium/windsurf/mcp_config.json`
