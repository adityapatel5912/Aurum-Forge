---
name: monitor_github_issues_and_send
description: Monitor GitHub issues and send alert notifications to Slack channel
version: 1.0.0
mcp: monitor_github_issues_and_send
---

# Skill: Monitor GitHub issues and send alert notifications to Slack channel

## Overview
This skill executes: Monitor GitHub issues and send alert notifications to Slack channel
Uses MCP Server: monitor_github_issues_and_send with 5 tools

## MCP Tools (from server.py)
- slack_post_message
- slack_list_channels
- github_create_issue
- github_list_prs
- github_get_file_contents

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
  },
  "t3": {
    "tool": "github_create_issue",
    "source": "Official GitHub"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `monitor_github_issues_and_send` installed. Follow this exact sequence:

1. CALL mcp tool `slack_post_message` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from monitor_github_issues_and_send) in parallel
   - CALL `notion_create_database_entry` (from monitor_github_issues_and_send) in parallel
3. Return summary

Do not re-discover tools — use monitor_github_issues_and_send tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Monitor GitHub issues and send alert notifications to Slack channel" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
