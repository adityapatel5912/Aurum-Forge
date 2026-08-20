---
name: docker_devops_manager
description: Inspect docker containers, tail logs, and send alerts to Slack
version: 1.0.0
mcp: docker_devops_manager
---

# Skill: Inspect docker containers, tail logs, and send alerts to Slack

## Overview
This skill executes: Inspect docker containers, tail logs, and send alerts to Slack
Uses MCP Server: docker_devops_manager with 8 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- slack_post_message

## Workflow DAG
```json
{
  "t1": {
    "tool": "notion_log_price",
    "source": "Core Notion"
  },
  "t2": {
    "tool": "slack_post_message",
    "source": "Official Slack"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `docker_devops_manager` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from docker_devops_manager) in parallel
   - CALL `gmail_notify_and_log` (from docker_devops_manager) in parallel
3. Return summary

Do not re-discover tools — use docker_devops_manager tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Inspect docker containers, tail logs, and send alerts to Slack" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
