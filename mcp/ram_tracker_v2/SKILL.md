---
name: ram_tracker_v2
description: Track RAM usage and notify via email
version: 1.0.0
mcp: ram_tracker_v2
---

# Skill: Track RAM usage and notify via email

## Overview
This skill executes: Track RAM usage and notify via email
Uses MCP Server: ram_tracker_v2 with 7 tools

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
    "tool": "amazon_monitor_ram_discount",
    "source": "Core Amazon",
    "parallel": false
  },
  "t2": {
    "tool": "gmail_notify_and_log",
    "source": "Core Gmail",
    "parallel": true,
    "deps": [
      "t1"
    ]
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `ram_tracker_v2` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from ram_tracker_v2) in parallel
   - CALL `gmail_notify_and_log` (from ram_tracker_v2) in parallel
3. Return summary

Do not re-discover tools — use ram_tracker_v2 tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Track RAM usage and notify via email" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
