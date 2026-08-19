---
name: ram_tracker_v3
description: Track top 100 RAM products from Amazon, Newegg, BestBuy, Microcenter, B&H sorted by price
version: 1.0.0
mcp: ram_tracker_v3
---

# Skill: Track top 100 RAM products from Amazon, Newegg, BestBuy, Microcenter, B&H sorted by price

## Overview
This skill executes: Track top 100 RAM products from Amazon, Newegg, BestBuy, Microcenter, B&H sorted by price
Uses MCP Server: ram_tracker_v3 with 7 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price

## Workflow DAG
```json
{
  "t1": {
    "tool": "amazon_search_ram",
    "source": "Core Amazon",
    "parallel": true
  },
  "t2": {
    "tool": "notion_log_price",
    "source": "Core Notion",
    "deps": [
      "t1"
    ],
    "parallel": true
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `ram_tracker_v3` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from ram_tracker_v3) in parallel
   - CALL `gmail_notify_and_log` (from ram_tracker_v3) in parallel
3. Return summary

Do not re-discover tools — use ram_tracker_v3 tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Track top 100 RAM products from Amazon, Newegg, BestBuy, Microcenter, B&H sorted by price" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
