---
name: hacker_news_monitor
description: Operate hacker_news_monitor workflow
version: 1.0.0
mcp: hacker_news_monitor
---

# Skill: Operate hacker_news_monitor workflow

## Overview
This skill executes: Operate hacker_news_monitor workflow
Uses MCP Server: hacker_news_monitor with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `hacker_news_monitor` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from hacker_news_monitor) in parallel
   - CALL `notion_create_database_entry` (from hacker_news_monitor) in parallel
3. Return summary

Do not re-discover tools — use hacker_news_monitor tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate hacker_news_monitor workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
