---
name: live_hacker_news_forge
description: Operate live_hacker_news_forge workflow
version: 1.0.0
mcp: live_hacker_news_forge
---

# Skill: Operate live_hacker_news_forge workflow

## Overview
This skill executes: Operate live_hacker_news_forge workflow
Uses MCP Server: live_hacker_news_forge with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `live_hacker_news_forge` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from live_hacker_news_forge) in parallel
   - CALL `notion_create_database_entry` (from live_hacker_news_forge) in parallel
3. Return summary

Do not re-discover tools — use live_hacker_news_forge tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate live_hacker_news_forge workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
