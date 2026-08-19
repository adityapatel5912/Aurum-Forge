---
name: notion_forge
description: Build Notion MCP that creates pages and databases with 5 tools
version: 1.0.0
mcp: notion_forge
---

# Skill: Build Notion MCP that creates pages and databases with 5 tools

## Overview
This skill executes: Build Notion MCP that creates pages and databases with 5 tools
Uses MCP Server: notion_forge with 8 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- notion_create_entry

## Workflow DAG
```json
{
  "t1": {
    "tool": "notion_log_price",
    "source": "Core Notion"
  },
  "t2": {
    "tool": "notion_create_entry",
    "source": "Official Notion"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `notion_forge` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from notion_forge) in parallel
   - CALL `gmail_notify_and_log` (from notion_forge) in parallel
3. Return summary

Do not re-discover tools — use notion_forge tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Build Notion MCP that creates pages and databases with 5 tools" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
