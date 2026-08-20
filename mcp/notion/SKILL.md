---
name: notion
description: Forge Notion writer MCP and
version: 1.0.0
mcp: notion
---

# Skill: Forge Notion writer MCP and

## Overview
This skill executes: Forge Notion writer MCP and
Uses MCP Server: notion with 8 tools

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
    "tool": "notion_create_entry",
    "source": "Official Notion",
    "parallel": true
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `notion` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from notion) in parallel
   - CALL `gmail_notify_and_log` (from notion) in parallel
3. Return summary

Do not re-discover tools — use notion tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Forge Notion writer MCP and" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
