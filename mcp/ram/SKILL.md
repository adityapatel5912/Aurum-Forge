---
name: ram
description: Forge RAM tracker MCP and email alerts
version: 1.0.0
mcp: ram
---

# Skill: Forge RAM tracker MCP and email alerts

## Overview
This skill executes: Forge RAM tracker MCP and email alerts
Uses MCP Server: ram with 12 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- search_amazon
- read_page_amazon
- click_element_amazon
- fill_field_amazon
- extract_links_amazon

## Workflow DAG
```json
{
  "t1": {
    "tool": "amazon_monitor_ram_discount",
    "source": "Core Amazon",
    "parallel": true
  },
  "t2": {
    "tool": "gmail_notify_and_log",
    "source": "Core Gmail",
    "parallel": true,
    "deps": [
      "t1"
    ]
  },
  "t3": {
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
You have MCP Server `ram` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from ram) in parallel
   - CALL `gmail_notify_and_log` (from ram) in parallel
3. Return summary

Do not re-discover tools — use ram tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Forge RAM tracker MCP and email alerts" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
