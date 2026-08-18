---
name: stress_4
description: Track price site 4 and log to notion
version: 1.0.0
mcp: stress_4
---

# Skill: Track price site 4 and log to notion

## Overview
This skill executes: Track price site 4 and log to notion
Uses MCP Server: stress_4 with 13 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- search_example
- read_page_example
- click_element_example
- fill_field_example
- extract_links_example
- notion_create_entry

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_example",
    "source": "Custom example.com Forged",
    "params": {
      "query": "site 4 price"
    },
    "parallel": false
  },
  "t2": {
    "tool": "notion_log_price",
    "source": "Core Notion",
    "parallel": true,
    "deps": [
      "t1"
    ]
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `stress_4` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from stress_4) in parallel
   - CALL `gmail_notify_and_log` (from stress_4) in parallel
3. Return summary

Do not re-discover tools — use stress_4 tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Track price site 4 and log to notion" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
