"""Notion core — 2 hardcoded REST tools (official Notion API, no browser)."""

NOTION_CORE_SOURCE = '''
@mcp.tool()
def notion_create_database_entry(database_id: str, title: str, content: str = "") -> dict:
    """Create a page entry in a Notion database via the official API (NOTION_TOKEN required)."""
    import os

    import httpx

    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        return {"ok": False, "error": "set NOTION_TOKEN env (Notion integration token)"}
    db = database_id or os.environ.get("NOTION_DATABASE_ID", "")
    if not db:
        return {"ok": False, "error": "pass database_id or set NOTION_DATABASE_ID env"}
    headers = {
        "Authorization": "Bearer " + token,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    payload = {"parent": {"type": "database_id", "database_id": db}}
    result = {"ok": False, "error": "could not create entry"}
    try:
        for title_key in ("title", "Name", "Title"):  # databases name their title prop differently
            payload["properties"] = {title_key: {"title": [{"text": {"content": title[:180]}}]}}
            if content:
                payload["children"] = [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:1900]}}]},
                    }
                ]
            resp = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=30)
            if resp.status_code in (200, 201):
                result = {"ok": True, "status": resp.status_code, "data": resp.json()}
                break
            result = {"ok": False, "status": resp.status_code, "error": resp.text[:300]}
        return result
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def notion_log_price(title: str, price: str = "", discount: str = "") -> dict:
    """Log a price/discount observation as a Notion database entry (uses NOTION_DATABASE_ID)."""
    import os

    db = os.environ.get("NOTION_DATABASE_ID", "")
    content = "price: {0}\\ndiscount: {1}%\\nlogged: via unified-forge".format(price or "n/a", discount or "n/a")
    return notion_create_database_entry(db, title[:180], content)
'''
