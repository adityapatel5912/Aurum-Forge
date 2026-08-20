---
name: track_live_spacex_launch_sched
description: Track live SpaceX launch schedule and notify engineering team via Slack
version: 1.0.0
mcp: track_live_spacex_launch_sched
---

# Skill: Track live SpaceX launch schedule and notify engineering team via Slack

## Overview
This skill executes: Track live SpaceX launch schedule and notify engineering team via Slack
Uses MCP Server: track_live_spacex_launch_sched with 10 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- search_spaceflightnow
- read_page_spaceflightnow
- slack_post_message

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_spaceflightnow",
    "source": "Custom spaceflightnow.com Forged",
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
  },
  "t4": {
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
You have MCP Server `track_live_spacex_launch_sched` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from track_live_spacex_launch_sched) in parallel
   - CALL `gmail_notify_and_log` (from track_live_spacex_launch_sched) in parallel
3. Return summary

Do not re-discover tools — use track_live_spacex_launch_sched tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Track live SpaceX launch schedule and notify engineering team via Slack" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
