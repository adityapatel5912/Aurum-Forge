---
name: pdf_research_summarizer
description: Extract and summarize research PDFs from arXiv and notify via Gmail
version: 1.0.0
mcp: pdf_research_summarizer
---

# Skill: Extract and summarize research PDFs from arXiv and notify via Gmail

## Overview
This skill executes: Extract and summarize research PDFs from arXiv and notify via Gmail
Uses MCP Server: pdf_research_summarizer with 12 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price
- search_arxiv
- read_page_arxiv
- click_element_arxiv
- fill_field_arxiv
- extract_links_arxiv

## Workflow DAG
```json
{
  "t1": {
    "tool": "search_arxiv",
    "source": "Custom arxiv.org Forged",
    "parallel": true
  },
  "t2": {
    "tool": "gmail_notify_and_log",
    "source": "Core Gmail",
    "deps": [
      "t1"
    ],
    "parallel": true
  },
  "t3": {
    "tool": "notion_log_price",
    "source": "Core Notion",
    "deps": [
      "t1"
    ],
    "parallel": true
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `pdf_research_summarizer` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from pdf_research_summarizer) in parallel
   - CALL `gmail_notify_and_log` (from pdf_research_summarizer) in parallel
3. Return summary

Do not re-discover tools — use pdf_research_summarizer tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Extract and summarize research PDFs from arXiv and notify via Gmail" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
