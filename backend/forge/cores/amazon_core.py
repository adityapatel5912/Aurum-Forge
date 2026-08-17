"""Amazon core — 3 hardcoded browser tools (search / discount check / RAM monitor).

Rendered into the CORES section of the generated server; uses its stealth
browser helpers (_ensure_page / _extract). One return per tool.
"""

AMAZON_CORE_SOURCE = '''
import re as _re
import urllib.parse as _urllib_parse


def _parse_amazon_discounts(rows, discount_gt):
    """Extract price (₹) and percent-off from Amazon result rows; keep matches only."""
    matches = []
    for row in rows:
        text = row.get("text", "") if isinstance(row, dict) else str(row)
        price_m = _re.search(r"₹\\s?([\\d,]+(?:\\.\\d+)?)", text)
        if not price_m:
            continue
        discount_m = _re.search(r"(\\d{1,2})\\s?%\\s?(?:off|OFF)", text)
        try:
            price = float(price_m.group(1).replace(",", ""))
        except ValueError:
            continue
        discount = float(discount_m.group(1)) if discount_m else 0.0
        if discount >= float(discount_gt):
            matches.append({"price": price, "discount": discount, "match": True, "text": text[:240]})
    return matches


@mcp.tool()
def amazon_search_ram(query: str, limit: int = 10) -> list:
    """Search Amazon for a query (e.g. '8GB RAM') and return result rows."""
    page = _ensure_page()
    try:
        page.goto(
            "https://www.amazon.in/s?k=" + _urllib_parse.quote(query),
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2500)
        rows = _extract(page, css="div[data-component-type='s-search-result']", limit=limit)
        return [{"text": (r.get("text", "") or "")[:300]} for r in rows]
    except Exception as err:
        return [{"ok": False, "tool": "amazon_search_ram", "error": repr(err)}]


@mcp.tool()
def amazon_check_discount(query: str, discount_gt: float = 20.0, limit: int = 24) -> list:
    """Search Amazon and return only results whose discount is >= discount_gt percent."""
    page = _ensure_page()
    try:
        page.goto(
            "https://www.amazon.in/s?k=" + _urllib_parse.quote(query),
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2500)
        rows = _extract(page, css="div[data-component-type='s-search-result']", limit=limit)
        matches = _parse_amazon_discounts(rows, discount_gt)
        return matches if matches else [{"match": False, "discount_gt": discount_gt, "note": "no deals above threshold right now"}]
    except Exception as err:
        return [{"ok": False, "tool": "amazon_check_discount", "error": repr(err)}]


@mcp.tool()
def amazon_monitor_ram_discount(discount_gt: float = 20.0) -> list:
    """Monitor 8GB RAM prices on Amazon and return deals with discount >= threshold (feeds gmail/notion tasks)."""
    return amazon_check_discount("8GB RAM", discount_gt, limit=24)
'''
