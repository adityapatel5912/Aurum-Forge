"""
live_hacker_news_forge — FastMCP Server created with FORGE.
"""
from fastmcp import FastMCP
import urllib.request
import json

mcp = FastMCP("live_hacker_news_forge")

@mcp.tool()
def get_top_hn_story() -> str:
    """Fetches the #1 top story on Hacker News via Firebase API."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Forge-MCP/1.0"})
    with urllib.request.urlopen(req, timeout=8) as res:
        story_ids = json.loads(res.read().decode())
    
    top_id = story_ids[0]
    item_url = f"https://hacker-news.firebaseio.com/v0/item/{top_id}.json"
    item_req = urllib.request.Request(item_url, headers={"User-Agent": "Forge-MCP/1.0"})
    with urllib.request.urlopen(item_req, timeout=8) as item_res:
        item = json.loads(item_res.read().decode())
    
    title = item.get("title", "No title")
    url = item.get("url", f"https://news.ycombinator.com/item?id={top_id}")
    score = item.get("score", 0)
    by = item.get("by", "unknown")
    return f"🔥 #1 HN Story: '{title}' by {by} ({score} points) - {url}"

@mcp.tool()
def calculate_growth(initial_val: float, final_val: float) -> str:
    """Calculates percentage growth between two metrics."""
    if initial_val == 0:
        return "Initial value cannot be zero."
    growth = ((final_val - initial_val) / initial_val) * 100
    return f"Growth: {growth:+.2f}% (from {initial_val} to {final_val})"

if __name__ == "__main__":
    mcp.run()
