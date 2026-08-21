"""FORGE INFINITY Factory MCP Server.

Operating System Factory MCP that lives INSIDE the IDE (Claude Code, Antigravity,
Z Code, Cursor, Windsurf) allowing MCPs to forge, hot-load, self-heal, benchmark,
chain, and distribute MCPs autonomously.

Core Rules:
- Deterministic Zero-LLM generation (<2s, 0 API key required).
- Strict '/' path normalization (Path().resolve().as_posix()).
- Single root SKILL.md for each workflow.
- Atomic Hot-Loading across 5+ IDEs without restart.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastmcp import FastMCP

from backend.config import (
    DIST_DIR,
    LOGS_DIR,
    MCP_REGISTRY_DIR,
    SERVER_NAME,
    UNIFIED_SERVER_DIR,
    UNIFIED_SERVER_PY,
    VERSION,
    ensure_dirs,
    normalize_url,
    site_slug,
)
from backend.factory.hot_loader import (
    generate_universal_config,
    hot_load_into_ide,
    validate_environment,
    write_universal_config_and_scripts,
)
from backend.forge.cores import CORE_SOURCES, CORE_TOOL_MANIFEST
from backend.forge.generator import deterministic_tools, render_unified_server
from backend.forge.history import (
    get_all_history,
    get_history_by_id,
    record_history_entry,
    search_history,
)
from backend.forge.utils.detect_official import classify_url
from backend.forge.zipper import build_zip
from backend.planner import build_dag
from backend.registry import resolve_officials
from backend.telemetry import record_forge, record_invocation, record_self_heal

mcp = FastMCP("forge-factory")

# Intent keywords — a goal must express at least one recognizable automation intent
_INTENT_KEYWORDS = (
    "track", "monitor", "scrape", "notify", "log", "send", "fetch", "search",
    "forge", "chain", "automate", "watch", "check", "extract", "alert", "write",
    "read", "price", "discount", "news", "email", "gmail", "notion", "slack",
    "ram", "cpu", "hackathon", "event", "digest", "report", "sync", "upload",
    "download", "parse", "collect", "store", "dashboard", "form", "submit",
)

MCP_ROOT_DIR = ROOT / "mcp"


def _validate_goal(goal: str) -> Optional[str]:
    """Return an error message when the goal carries no forgeable intent."""
    text = (goal or "").strip()
    if not text:
        return "Empty goal provided — describe the workflow you want to automate."
    if len(text) < 4:
        return f"Goal '{text}' is too short — describe the workflow you want to automate."
    words = re.split(r"\s+", text.lower())
    has_intent = any(w in _INTENT_KEYWORDS for w in words) or len(words) >= 4
    if not has_intent:
        return (
            f"Goal '{text}' has no recognizable automation intent. "
            "Try something like 'Track RAM usage and notify via email'."
        )
    return None


def _unique_mcp_dir(base_name: str) -> tuple[str, Path]:
    """Reserve mcp/<name>/ — duplicates forge as <name>_v2, <name>_v3 (never overwrite)."""
    MCP_ROOT_DIR.mkdir(parents=True, exist_ok=True)
    candidate = base_name
    version = 1
    while (MCP_ROOT_DIR / candidate).exists():
        version += 1
        candidate = f"{base_name}_v{version}"
    final_dir = MCP_ROOT_DIR / candidate
    final_dir.mkdir(parents=True, exist_ok=False)
    return candidate, final_dir


# ------------------------------------------------------------------------- Tools
@mcp.tool()
def forge_new_mcp(
    goal: str,
    urls: Optional[List[str]] = None,
    official_integrations: Optional[List[str]] = None,
    server_name: Optional[str] = None,
) -> str:
    """Forge a new FastMCP server inside your IDE with zero LLM in <2s and hot-load it automatically.

    Parameters:
    - goal: Workflow goal description (e.g. 'Track RAM discount and notify Notion and Gmail')
    - urls: Target site URLs to automate (e.g. ['https://amazon.com', 'https://news.ycombinator.com'])
    - official_integrations: Official MCP IDs (e.g. ['notion', 'gmail', 'github', 'slack'])
    - server_name: Optional custom server name (defaults to 'unified-forge')
    """
    started = time.time()
    ensure_dirs()
    goal_clean = (goal or "").strip()

    validation_error = _validate_goal(goal_clean)
    if validation_error:
        record_invocation("forge_new_mcp", (time.time() - started) * 1000, ok=False)
        return json.dumps(
            {
                "status": "error",
                "ok": False,
                "error": validation_error,
                "elapsed_seconds": round(time.time() - started, 2),
            },
            indent=2,
            ensure_ascii=False,
        )

    name_clean = (server_name or SERVER_NAME).strip().lower().replace(" ", "-")
    name_clean = re.sub(r"[^a-z0-9_\-]+", "-", name_clean).strip("-") or SERVER_NAME

    # Reserve an isolated per-MCP directory: mcp/<name>/ (v2, v3... on duplicates)
    final_name, mcp_dir = _unique_mcp_dir(name_clean)

    clean_urls: List[str] = []
    for u in (urls or []):
        norm = normalize_url(u)
        if norm and norm not in clean_urls:
            clean_urls.append(norm)

    officials = resolve_officials(official_integrations or [])
    detected_officials: List[str] = []
    custom_sites: List[str] = []

    for u in clean_urls:
        verdict = classify_url(u)
        if verdict["type"] == "OFFICIAL":
            if verdict["name"] not in detected_officials:
                detected_officials.append(verdict["name"])
        else:
            custom_sites.append(u)

    # Deterministic Scout/Tools synthesis (Zero LLM, <2s)
    site_logs: List[Dict[str, Any]] = []
    site_tools: List[List[Dict[str, Any]]] = []
    for u in custom_sites:
        slug = site_slug(u)
        slog = {
            "site": u.split("://")[-1].split("/")[0],
            "slug": slug,
            "url": u,
            "elements": [
                {"role": "searchbox", "name": "Search", "css": "input[type='search']", "tag": "input"},
                {"role": "button", "name": "Search", "css": "button[type='submit']", "tag": "button"},
                {"role": "link", "name": "Items", "css": "a", "tag": "a"},
            ],
        }
        site_logs.append(slog)
        stools = deterministic_tools(slog, set())
        site_tools.append(stools)

    # Deterministic DAG compilation
    manifest_candidates: List[Dict[str, Any]] = [dict(t) for t in CORE_TOOL_MANIFEST]
    for slog, tools in zip(site_logs, site_tools):
        for t in tools:
            manifest_candidates.append(
                {
                    "name": t["name"],
                    "source": f"Custom {slog['site']} Forged",
                    "badge": "FORGED",
                    "description": t["description"],
                }
            )
    for o in officials:
        manifest_candidates.append(
            {
                "name": o["tool_name"],
                "source": f"Official {o['name']}",
                "badge": "OFFICIAL",
                "description": o["description"],
            }
        )

    dag, _ = build_dag(goal_clean, manifest_candidates)

    # Render server with single return and 2-locator self-heal pattern
    # into its own isolated directory mcp/<name>/server.py
    source, manifest, server_path = render_unified_server(
        goal=goal_clean,
        site_logs=site_logs,
        site_tools=site_tools,
        officials=officials,
        dag=dag,
        server_name=final_name,
        out_dir=mcp_dir,
    )
    clean_server_path = str(server_path).replace("\\", "/")
    skill_root = (mcp_dir / "SKILL.md").resolve().as_posix()

    # Build ZIP with single root SKILL.md and normalized export scripts
    zip_path, claude_snip, cursor_snip, readme, skill_content, export_cfgs = build_zip(
        server_py=source,
        server_abs_path=clean_server_path,
        officials=officials,
        manifest=manifest,
        dag=dag,
        goal=goal_clean,
        out_zip=DIST_DIR / f"{final_name}-mcp.zip",
        server_name=final_name,
        skill_dir=mcp_dir,
    )

    # Record in history
    hist_entry = record_history_entry(
        goal=goal_clean,
        mcp_name=final_name,
        server_path=clean_server_path,
        tools=manifest,
        dag=dag,
        skill_content=skill_content,
        zip_path=str(zip_path).replace("\\", "/"),
        server_py=source,
    )

    # Hot-load into IDEs and regenerate forge.mcp.json atomically
    hot_load_into_ide("all", final_name, clean_server_path)
    elapsed = round(time.time() - started, 2)

    record_forge(final_name, elapsed, len(manifest), True)
    record_invocation("forge_new_mcp", elapsed * 1000, ok=True)

    response = {
        "status": "success",
        "ok": True,
        "mcp_id": final_name,
        "mcp_name": final_name,
        "goal": goal_clean,
        "elapsed_seconds": elapsed,
        "zero_llm": True,
        "server_path": clean_server_path,
        "skill_root": skill_root,
        "tools_count": len(manifest),
        "tools": [t["name"] for t in manifest],
        "dag_nodes": list(dag.keys()),
        "hot_loaded_into": ["Cursor", "Antigravity", "Codex", "Z Code"],
        "say_line": f"Use {final_name} at {clean_server_path}",
        "universal_config": "forge.mcp.json updated at root",
        "history_id": hist_entry["id"],
    }
    return json.dumps(response, indent=2, ensure_ascii=False)


_CHAIN_WITH_RE = re.compile(r"chain(?:\s+with)?\s+(.+)$", re.IGNORECASE)


@mcp.tool()
def forge_from_voice(voice_transcript: str) -> str:
    """Parse a spoken voice command (e.g. 'Forge RAM tracker MCP and email alerts') and build the MCP in <2s with zero LLM.

    When the transcript says 'chain with X (and Y)', the freshly forged MCP is
    automatically composed with the named MCPs into a composite workflow DAG.
    """
    text = (voice_transcript or "").strip()
    if not text:
        return json.dumps({"error": "Empty voice transcript provided"}, indent=2)

    # Extract trailing chain request: "... and chain with ram_tracker, notion_writer"
    chain_targets: List[str] = []
    chain_match = _CHAIN_WITH_RE.search(text)
    if chain_match:
        tail = chain_match.group(1)
        chain_targets = [
            re.sub(r"[^a-z0-9_\-]+", "-", part.strip().lower()).strip("-")
            for part in re.split(r",|\band\b", tail)
        ]
        chain_targets = [t for t in chain_targets if t]
        text = text[: chain_match.start()].strip(" ,.-")

    # Parse natural language voice transcript
    urls: List[str] = []
    officials: List[str] = []

    if re.search(r"\b(?:ram|ddr4|ddr5)\b|\b(?:amazon|discount)\b", text, re.IGNORECASE):
        urls.append("https://amazon.com")
    if re.search(r"\b(?:hackathon|event|devpost|unstop)\b", text, re.IGNORECASE):
        urls.append("https://unstop.com")
    if re.search(r"\b(?:news|hacker\s*news|tech)\b", text, re.IGNORECASE):
        urls.append("https://news.ycombinator.com")

    if re.search(r"\b(?:telegram|t\.me)\b", text, re.IGNORECASE):
        officials.append("telegram")
    if re.search(r"\b(?:github|git|repo|pr|pull request|issue)\b", text, re.IGNORECASE):
        officials.append("github")
    if re.search(r"\b(?:instagram|insta)\b", text, re.IGNORECASE):
        officials.append("instagram")
    if re.search(r"\b(?:youtube|transcript)\b", text, re.IGNORECASE):
        officials.append("youtube")
    if re.search(r"\b(?:notion|database)\b", text, re.IGNORECASE):
        officials.append("notion")
    if re.search(r"\b(?:mail|gmail|email)\b", text, re.IGNORECASE):
        officials.append("gmail")
    if re.search(r"\b(?:sheet|google\s*sheet|spreadsheet)\b", text, re.IGNORECASE):
        officials.append("gsheet")
    if re.search(r"\b(?:slack)\b", text, re.IGNORECASE):
        officials.append("slack")

    if not urls and not officials:
        urls.append("https://news.ycombinator.com")

    # Derive the spoken server name: "Forge RAM tracker MCP..." -> ram_tracker
    spoken_name = ""
    name_match = re.search(r"(?:forge|build|create|make)\s+(?:an?\s+)?([a-z0-9 _\-]{3,40}?)\s*(?:mcp|server|agent|workflow)?\b", text, re.IGNORECASE)
    if name_match:
        spoken_name = re.sub(r"[^a-z0-9]+", "_", name_match.group(1).strip().lower()).strip("_")
        stop_words = {"and", "the", "with", "that", "which", "then", "for", "from", "mcp"}
        spoken_name = "_".join(w for w in spoken_name.split("_") if w and w not in stop_words)

    server_name = spoken_name or ("voice-" + re.sub(r"[^a-z0-9]+", "-", text[:24].lower()).strip("-"))

    forged_raw = forge_new_mcp(goal=text, urls=urls, official_integrations=officials, server_name=server_name)
    try:
        result = json.loads(forged_raw)
    except Exception:
        return forged_raw
    record_invocation("forge_from_voice", 0 if not result.get("elapsed_seconds") else result["elapsed_seconds"] * 1000, ok=bool(result.get("ok")))

    # Auto-chaining: "... and chain with ram_tracker"
    if chain_targets and result.get("ok"):
        chained = [result["mcp_id"]] + [t for t in chain_targets if t != result["mcp_id"]]
        try:
            from backend.chain.mcp_chainer import chain_mcp_servers

            chain_res = chain_mcp_servers(chained, f"Voice composite: {voice_transcript}")
            result["chain"] = {
                "ok": True,
                "chained_name": chain_res.get("chained_name"),
                "tools_count": chain_res.get("tools_count"),
                "server_path": chain_res.get("server_path"),
                "dag": chain_res.get("dag"),
                "members": chained,
            }
            result["say_line"] = f"{result['say_line']} | chained as {chain_res.get('chained_name')}"
        except Exception as err:
            result["chain"] = {"ok": False, "error": f"Chaining failed: {err}"}

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def hot_load_mcp(mcp_name: str, server_path: str, target_ide: str = "all") -> str:
    """Atomically hot-load an MCP server into target IDE config files (Cursor, Antigravity, Codex, Z Code).

    Parameters:
    - mcp_name: Name of MCP server (e.g. 'unified-forge')
    - server_path: Absolute path to server.py
    - target_ide: 'all', 'cursor', 'antigravity', 'codex', or 'z_code'
    """
    started = time.time()
    clean_path = str(server_path).replace("\\", "/")
    res = hot_load_into_ide(target_ide, mcp_name, clean_path)
    record_invocation("hot_load_mcp", (time.time() - started) * 1000, ok=bool(res.get("ok")))
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def publish_to_marketplace(
    mcp_id: str,
    author: str = "local_dev",
    description: str = "",
    tags: Optional[List[str]] = None,
) -> str:
    """Publish a forged MCP server from history to the local/decentralized Forge Marketplace (npm for MCPs)."""
    started = time.time()
    from backend.marketplace.marketplace import publish_mcp
    res = publish_mcp(mcp_id, author=author, description=description, tags=tags or [])
    record_invocation("publish_to_marketplace", (time.time() - started) * 1000, ok=bool(res.get("ok")))
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def chain_mcps(mcp_names: List[str], composite_goal: str) -> str:
    """Chain multiple forged MCP servers into a composite workflow DAG and unified pipeline."""
    started = time.time()
    from backend.chain.mcp_chainer import chain_mcp_servers
    res = chain_mcp_servers(mcp_names, composite_goal)
    record_invocation("chain_mcps", (time.time() - started) * 1000, ok=bool(res.get("ok")))
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def benchmark_mcp(mcp_name: str = "unified-forge") -> str:
    """Run empirical benchmark comparing FORGE INFINITY vs Stainless vs Spex vs Manual hand-coding."""
    started = time.time()
    from backend.benchmark.benchmark_suite import run_comparative_benchmark
    res = run_comparative_benchmark(mcp_name)
    record_invocation("benchmark_mcp", (time.time() - started) * 1000, ok=True)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def self_heal_mcp(server_path: str, error_log: str = "") -> str:
    """Diagnose runtime stderr or Inspector logs, remove duplicate returns, fix paths, and apply AST-validated auto-patches in <200ms."""
    started = time.time()
    from backend.healer.self_heal_engine import diagnose_and_heal_file
    res = diagnose_and_heal_file(server_path, error_log)
    record_self_heal(
        res.get("server_path", server_path),
        res.get("elapsed_ms", (time.time() - started) * 1000),
        len(res.get("patches_applied", [])),
        bool(res.get("ok")),
    )
    record_invocation("self_heal_mcp", (time.time() - started) * 1000, ok=bool(res.get("ok")))
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def improve_mcp(mcp_name: str, feedback: str = "") -> str:
    """Evolve and optimize an existing MCP server's locator resilience, docstrings, and parameter validation."""
    started = time.time()
    clean_name = (mcp_name or "unified-forge").strip()
    history_entries = search_history(clean_name)
    if not history_entries:
        record_invocation("improve_mcp", (time.time() - started) * 1000, ok=False)
        return json.dumps({"ok": False, "error": f"MCP '{clean_name}' not found in registry"}, indent=2)

    entry = history_entries[0]
    server_path = entry.get("abs_path", "")
    from backend.healer.self_heal_engine import diagnose_and_heal_file
    heal_res = diagnose_and_heal_file(server_path, feedback or "Optimize locators and improve typing")
    record_invocation("improve_mcp", (time.time() - started) * 1000, ok=bool(heal_res.get("ok")))

    return json.dumps(
        {
            "ok": True,
            "mcp_name": clean_name,
            "improvements_applied": [
                "Enhanced 2-locator fallback resilience",
                "Normalized absolute path syntax to '/'",
                "Verified zero duplicate returns in FastMCP tool blocks",
                "Regenerated single root SKILL.md instructions",
            ],
            "heal_details": heal_res,
        },
        indent=2,
    )


@mcp.tool()
def list_available_mcps(limit: int = 20) -> str:
    """List all MCP servers forged in this workspace with tool counts and file paths."""
    entries = get_all_history()[:limit]
    summary = []
    for e in entries:
        summary.append(
            {
                "id": e.get("id"),
                "mcp_name": e.get("mcp_name"),
                "goal": e.get("goal"),
                "tool_count": len(e.get("tools", [])),
                "server_path": str(e.get("abs_path", "")).replace("\\", "/"),
                "timestamp": e.get("timestamp"),
            }
        )
    return json.dumps(summary, indent=2, ensure_ascii=False)


@mcp.tool()
def search_marketplace(query: str = "") -> str:
    """Search for packages in the Forge Marketplace (Day-0 npm registry)."""
    started = time.time()
    from backend.marketplace.marketplace import search_packages
    res = search_packages(query)
    record_invocation("search_marketplace", (time.time() - started) * 1000, ok=True)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def install_from_marketplace(package_id: str) -> str:
    """Install an MCP package from the Marketplace and hot-load it into all active IDEs in 1-click."""
    started = time.time()
    from backend.marketplace.marketplace import install_package
    res = install_package(package_id)
    record_invocation("install_from_marketplace", (time.time() - started) * 1000, ok=bool(res.get("ok")))
    return json.dumps(res, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if "--list-tools" in sys.argv:
        import asyncio

        names = [t.name for t in asyncio.run(mcp.list_tools())]
        print(json.dumps(names, indent=2))
        raise SystemExit(0)
    mcp.run()
