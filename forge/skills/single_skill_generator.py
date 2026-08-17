"""FORGE Single SKILL.md Generator.

Generates a single, high-performance SKILL.md for the entire workflow.
Optimized for agent execution so the agent directly references the MCP server
and executes the planned DAG without re-discovering tools.
"""
from __future__ import annotations

import json
from typing import Any


def generate_single_skill(
    goal: str,
    tools: list[Any],
    dag: dict[str, Any] | None = None,
    mcp_name: str = "unified-forge",
) -> str:
    """Single skill for whole workflow — optimized for agent performance."""
    goal_clean = (goal or "Automate browser and official workflow").strip()
    dag_dict = dag or {}

    # Extract tool names cleanly whether list of strings or list of tool dicts
    tool_names: list[str] = []
    for t in tools or []:
        if isinstance(t, str):
            tool_names.append(t)
        elif isinstance(t, dict):
            name = t.get("name") or t.get("tool_name")
            if name:
                tool_names.append(str(name))

    if not tool_names:
        tool_names = ["search_site", "extract_data"]

    tools_bullets = "\n".join([f"- {t}" for t in tool_names])
    dag_json = json.dumps(dag_dict, indent=2, ensure_ascii=False)

    # Dynamic instructions based on available tools
    search_tool = next((t for t in tool_names if "search" in t or "monitor" in t), tool_names[0])
    gmail_tool = next((t for t in tool_names if "gmail" in t or "email" in t or "send" in t), "gmail_send_email")
    notion_tool = next((t for t in tool_names if "notion" in t or "db" in t or "log" in t), "notion_create_database_entry")

    content = f"""---
name: {mcp_name}
description: {goal_clean[:120]}
version: 1.0.0
mcp: {mcp_name}
---

# Skill: {goal_clean}

## Overview
This skill executes: {goal_clean}
Uses MCP Server: {mcp_name} with {len(tool_names)} tools

## MCP Tools (from server.py)
{tools_bullets}

## Workflow DAG
```json
{dag_json}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `{mcp_name}` installed. Follow this exact sequence:

1. CALL mcp tool `{search_tool}` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `{gmail_tool}` (from {mcp_name}) in parallel
   - CALL `{notion_tool}` (from {mcp_name}) in parallel
3. Return summary

Do not re-discover tools — use {mcp_name} tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "{goal_clean}" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
"""
    return content
