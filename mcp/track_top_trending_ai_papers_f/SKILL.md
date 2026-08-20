---
name: track_top_trending_ai_papers_f
description: Operate track_top_trending_ai_papers_f workflow
version: 1.0.0
mcp: track_top_trending_ai_papers_f
---

# Skill: Operate track_top_trending_ai_papers_f workflow

## Overview
This skill executes: Operate track_top_trending_ai_papers_f workflow
Uses MCP Server: track_top_trending_ai_papers_f with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `track_top_trending_ai_papers_f` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from track_top_trending_ai_papers_f) in parallel
   - CALL `notion_create_database_entry` (from track_top_trending_ai_papers_f) in parallel
3. Return summary

Do not re-discover tools — use track_top_trending_ai_papers_f tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate track_top_trending_ai_papers_f workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
