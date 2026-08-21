---
name: chain_eco_monitor
description: Operate chain_eco_monitor workflow
version: 1.0.0
mcp: chain_eco_monitor
---

# Skill: Operate chain_eco_monitor workflow

## Overview
This skill executes: Operate chain_eco_monitor workflow
Uses MCP Server: chain_eco_monitor with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `chain_eco_monitor` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from chain_eco_monitor) in parallel
   - CALL `notion_create_database_entry` (from chain_eco_monitor) in parallel
3. Return summary

Do not re-discover tools — use chain_eco_monitor tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate chain_eco_monitor workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
