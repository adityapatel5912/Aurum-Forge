---
name: monitor_open_prs_on_github_rep
description: Operate monitor_open_prs_on_github_rep workflow
version: 1.0.0
mcp: monitor_open_prs_on_github_rep
---

# Skill: Operate monitor_open_prs_on_github_rep workflow

## Overview
This skill executes: Operate monitor_open_prs_on_github_rep workflow
Uses MCP Server: monitor_open_prs_on_github_rep with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `monitor_open_prs_on_github_rep` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from monitor_open_prs_on_github_rep) in parallel
   - CALL `notion_create_database_entry` (from monitor_open_prs_on_github_rep) in parallel
3. Return summary

Do not re-discover tools — use monitor_open_prs_on_github_rep tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate monitor_open_prs_on_github_rep workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
