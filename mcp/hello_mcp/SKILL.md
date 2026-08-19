---
name: hello_mcp
description: Make a useless MCP that does nothing but says hello
version: 1.0.0
mcp: hello_mcp
---

# Skill: Make a useless MCP that does nothing but says hello

## Overview
This skill executes: Make a useless MCP that does nothing but says hello
Uses MCP Server: hello_mcp with 7 tools

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
    "tool": "notion_log_price",
    "source": "Core Notion"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `hello_mcp` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from hello_mcp) in parallel
   - CALL `gmail_notify_and_log` (from hello_mcp) in parallel
3. Return summary

Do not re-discover tools — use hello_mcp tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Make a useless MCP that does nothing but says hello" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
