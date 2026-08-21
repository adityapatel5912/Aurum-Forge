---
name: chain_waste_reduce
description: Operate chain_waste_reduce workflow
version: 1.0.0
mcp: chain_waste_reduce
---

# Skill: Operate chain_waste_reduce workflow

## Overview
This skill executes: Operate chain_waste_reduce workflow
Uses MCP Server: chain_waste_reduce with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `chain_waste_reduce` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from chain_waste_reduce) in parallel
   - CALL `notion_create_database_entry` (from chain_waste_reduce) in parallel
3. Return summary

Do not re-discover tools — use chain_waste_reduce tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate chain_waste_reduce workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
