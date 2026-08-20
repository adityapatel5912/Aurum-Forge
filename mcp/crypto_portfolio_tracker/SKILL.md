---
name: crypto_portfolio_tracker
description: Operate crypto_portfolio_tracker workflow
version: 1.0.0
mcp: crypto_portfolio_tracker
---

# Skill: Operate crypto_portfolio_tracker workflow

## Overview
This skill executes: Operate crypto_portfolio_tracker workflow
Uses MCP Server: crypto_portfolio_tracker with 2 tools

## MCP Tools (from server.py)
- search_site
- extract_data

## Workflow DAG
```json
{}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `crypto_portfolio_tracker` installed. Follow this exact sequence:

1. CALL mcp tool `search_site` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from crypto_portfolio_tracker) in parallel
   - CALL `notion_create_database_entry` (from crypto_portfolio_tracker) in parallel
3. Return summary

Do not re-discover tools — use crypto_portfolio_tracker tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Operate crypto_portfolio_tracker workflow" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
