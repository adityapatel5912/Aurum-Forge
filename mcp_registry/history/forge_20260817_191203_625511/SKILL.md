---
name: unified-forge
description: Find Web3 hackathons on Unstop with prize >50000, mail me and log to Notion
version: 1.0.0
mcp: unified-forge
---

# Skill: Find Web3 hackathons on Unstop with prize >50000, mail me and log to Notion

## Overview
This skill executes: Find Web3 hackathons on Unstop with prize >50000, mail me and log to Notion
Uses MCP Server: unified-forge with 10 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- unstop_search
- unstop_filter_hackathons
- notion_create_entry

## Workflow DAG
```json
{
  "t1": {
    "tool": "unstop_filter_hackathons",
    "source": "Custom unstop.com Forged",
    "params": {
      "query": "Web3",
      "prize_min": 50000
    },
    "parallel": false
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
You have MCP Server `unified-forge` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from unified-forge) in parallel
   - CALL `gmail_notify_and_log` (from unified-forge) in parallel
3. Return summary

Do not re-discover tools — use unified-forge tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Find Web3 hackathons on Unstop with prize >50000, mail me and log to Notion" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
