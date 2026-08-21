---
name: research_v6
description: Forge Research
version: 1.0.0
mcp: research_v6
---

# Skill: Forge Research

## Overview
This skill executes: Forge Research
Uses MCP Server: research_v6 with 12 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- search_news_ycombinator
- read_page_news_ycombinator
- click_element_news_ycombinator
- fill_field_news_ycombinator
- extract_links_news_ycombinator

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_news_ycombinator",
    "source": "Custom news.ycombinator.com Forged",
    "params": {
      "query": "Forge"
    },
    "parallel": false
  },
  "t2": {
    "tool": "extract_links_news_ycombinator",
    "source": "Custom news.ycombinator.com Forged",
    "parallel": false,
    "deps": [
      "t1"
    ]
  },
  "t3": {
    "tool": "notion_create_database_entry",
    "source": "Core Notion",
    "parallel": true,
    "deps": [
      "t2"
    ]
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `research_v6` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from research_v6) in parallel
   - CALL `gmail_notify_and_log` (from research_v6) in parallel
3. Return summary

Do not re-discover tools — use research_v6 tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Forge Research" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
