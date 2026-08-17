---
name: unified-forge
description: Find hackathons and log events
version: 1.0.0
mcp: unified-forge
---

# Skill: Find hackathons and log events

## Overview
This skill executes: Find hackathons and log events
Uses MCP Server: unified-forge with 2 tools

## MCP Tools (from server.py)
- devpost_search_hackathons
- mlh_get_events

## Workflow DAG
```json
{
  "t1": {
    "tool": "devpost_search_hackathons",
    "source": "Custom Devpost Forged"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `unified-forge` installed. Follow this exact sequence:

1. CALL mcp tool `devpost_search_hackathons` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from unified-forge) in parallel
   - CALL `notion_create_database_entry` (from unified-forge) in parallel
3. Return summary

Do not re-discover tools — use unified-forge tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Find hackathons and log events" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
