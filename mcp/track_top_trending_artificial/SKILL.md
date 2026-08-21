---
name: track_top_trending_artificial
description: Track top trending artificial intelligence breakthroughs and developer discussions from Hacker News and broadcast instan
version: 1.0.0
mcp: track_top_trending_artificial
---

# Skill: Track top trending artificial intelligence breakthroughs and developer discussions from Hacker News and broadcast instant intelligence briefs to Slack.

## Overview
This skill executes: Track top trending artificial intelligence breakthroughs and developer discussions from Hacker News and broadcast instant intelligence briefs to Slack.
Uses MCP Server: track_top_trending_artificial with 10 tools

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
- slack_post_message

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_news_ycombinator",
    "source": "Custom news.ycombinator.com Forged",
    "parallel": true
  },
  "t2": {
    "tool": "notion_log_price",
    "source": "Core Notion",
    "deps": [
      "t1"
    ],
    "parallel": true
  },
  "t3": {
    "tool": "slack_post_message",
    "source": "Official Slack",
    "deps": [
      "t1"
    ],
    "parallel": true
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `track_top_trending_artificial` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from track_top_trending_artificial) in parallel
   - CALL `gmail_notify_and_log` (from track_top_trending_artificial) in parallel
3. Return summary

Do not re-discover tools — use track_top_trending_artificial tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Track top trending artificial intelligence breakthroughs and developer discussions from Hacker News and broadcast instant intelligence briefs to Slack." or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
