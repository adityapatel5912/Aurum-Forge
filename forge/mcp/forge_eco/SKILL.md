---
name: forge_eco
description: Operate forge_eco workflow
version: 1.0.0
mcp: forge_eco
---

# Skill: Operate forge_eco workflow

## Overview
This skill executes: Operate forge_eco workflow
Uses MCP Server: forge_eco with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `forge_eco` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from forge_eco) in parallel
   - CALL `notion_create_database_entry` (from forge_eco) in parallel
3. Return summary

Do not re-discover tools — use forge_eco tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate forge_eco workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
