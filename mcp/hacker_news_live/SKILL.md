---
name: hacker_news_live
description: Monitor top Hacker News stories and notify via Mail.
version: 1.0.0
mcp: hacker_news_live
---

# Skill: Monitor top Hacker News stories and notify via Mail.

## Overview
This skill executes: Monitor top Hacker News stories and notify via Mail.
Uses MCP Server: hacker_news_live with 12 tools

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
    "parallel": true
  },
  "t2": {
    "tool": "gmail_notify_and_log",
    "source": "Core Gmail",
    "deps": [
      "t1"
    ],
    "parallel": true
  },
  "t3": {
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
You have MCP Server `hacker_news_live` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from hacker_news_live) in parallel
   - CALL `gmail_notify_and_log` (from hacker_news_live) in parallel
3. Return summary

Do not re-discover tools — use hacker_news_live tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Monitor top Hacker News stories and notify via Mail." or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
