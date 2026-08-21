---
name: monitor_github_issues_and_send_v3
description: Monitor GitHub issues and send alert notifications to Slack channel
version: 1.0.0
mcp: monitor_github_issues_and_send_v3
---

# Skill: Monitor GitHub issues and send alert notifications to Slack channel

## Overview
This skill executes: Monitor GitHub issues and send alert notifications to Slack channel
Uses MCP Server: monitor_github_issues_and_send_v3 with 24 tools

## MCP Tools (from server.py)
- search_news_ycombinator
- read_page_news_ycombinator
- click_element_news_ycombinator
- fill_field_news_ycombinator
- extract_links_news_ycombinator
- search_arxiv
- read_page_arxiv
- click_element_arxiv
- fill_field_arxiv
- extract_links_arxiv
- search_spaceflightnow
- read_page_spaceflightnow
- click_element_spaceflightnow
- fill_field_spaceflightnow
- extract_links_spaceflightnow
- telegram_send_message
- telegram_get_updates
- telegram_send_photo
- telegram_get_chat
- slack_post_message
- slack_list_channels
- github_create_issue
- github_list_prs
- github_get_file_contents

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_news_ycombinator",
    "source": "Custom news.ycombinator.com Forged",
    "parallel": true
  },
  "t2": {
    "tool": "search_arxiv",
    "source": "Custom arxiv.org Forged",
    "parallel": true
  },
  "t3": {
    "tool": "search_spaceflightnow",
    "source": "Custom spaceflightnow.com Forged",
    "parallel": true
  },
  "t4": {
    "tool": "notion_log_price",
    "source": "Core Notion",
    "deps": [
      "t1",
      "t2",
      "t3"
    ],
    "parallel": true
  },
  "t5": {
    "tool": "slack_post_message",
    "source": "Official Slack",
    "deps": [
      "t1",
      "t2",
      "t3"
    ],
    "parallel": true
  },
  "t6": {
    "tool": "github_create_issue",
    "source": "Official GitHub",
    "deps": [
      "t1",
      "t2",
      "t3"
    ],
    "parallel": true
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `monitor_github_issues_and_send_v3` installed. Follow this exact sequence:

1. CALL mcp tool `search_news_ycombinator` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `telegram_send_message` (from monitor_github_issues_and_send_v3) in parallel
   - CALL `notion_create_database_entry` (from monitor_github_issues_and_send_v3) in parallel
3. Return summary

Do not re-discover tools — use monitor_github_issues_and_send_v3 tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Monitor GitHub issues and send alert notifications to Slack channel" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
