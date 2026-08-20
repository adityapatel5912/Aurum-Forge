---
name: aws_s3_archiver
description: Archive files to S3 bucket and log status to Google Sheets
version: 1.0.0
mcp: aws_s3_archiver
---

# Skill: Archive files to S3 bucket and log status to Google Sheets

## Overview
This skill executes: Archive files to S3 bucket and log status to Google Sheets
Uses MCP Server: aws_s3_archiver with 7 tools

## MCP Tools (from server.py)
- amazon_search_ram
- amazon_check_discount
- amazon_monitor_ram_discount
- gmail_send_email
- gmail_notify_and_log
- notion_create_database_entry
- notion_log_price

## Workflow DAG
```json
{
  "t1": {
    "tool": "notion_log_price",
    "source": "Core Notion"
  }
}
```

## Instructions for Agent (Performance Optimized)
You have MCP Server `aws_s3_archiver` installed. Follow this exact sequence:

1. CALL mcp tool `amazon_search_ram` or respective search tool from DAG T1
2. IF result meets threshold (discount >20%, prize>50000, price<2000):
   - CALL `gmail_send_email` (from aws_s3_archiver) in parallel
   - CALL `gmail_notify_and_log` (from aws_s3_archiver) in parallel
3. Return summary

Do not re-discover tools — use aws_s3_archiver tools directly. This SKILL.md is single source of truth for this workflow.

## When to Invoke
User says: "Archive files to S3 bucket and log status to Google Sheets" or similar to RAM/hackathon/tee tracking

## Expected Output
- Email sent
- Notion logged
- Summary returned
