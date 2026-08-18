"""FORGE INFINITY Multi-MCP Chaining Engine.

Allows automatic composition of multiple forged MCP tools into unified multi-agent
workflow DAGs (e.g. 'Chain RAM tracker with Gmail alert and Notion logging').
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

from backend.config import MCP_REGISTRY_DIR, ensure_dirs
from backend.factory.hot_loader import hot_load_into_ide
from backend.forge.cores import CORE_TOOL_MANIFEST
from backend.forge.history import get_all_history, record_history_entry, search_history
from backend.forge.skills.single_skill_generator import generate_single_skill
from backend.planner.planner import build_dag


def _render_composite_server(
    chained_name: str,
    composite_goal: str,
    members: List[Dict[str, Any]],
    dag: Dict[str, Any],
) -> str:
    """Deterministically render a composite FastMCP server that chains member MCPs.

    One passthrough tool per member (outputs feed the next member's inputs) plus
    a run_chain orchestrator returning the composed pipeline result.
    """
    import json as _json

    members_meta = [
        {
            "name": m["name"],
            "member_mcp": m["member_mcp"],
            "position": i + 1,
            "tool_count": m["tool_count"],
        }
        for i, m in enumerate(members)
    ]
    dag_json = _json.dumps(dag, indent=2, ensure_ascii=False)
    members_json = _json.dumps(members_meta, indent=2, ensure_ascii=False)

    tool_blocks = []
    for i, m in enumerate(members):
        tool_blocks.append(
            f'''
@mcp.tool()
def stage_{i + 1}_{m["name"]}(payload: str = "") -> str:
    """Chain stage {i + 1}: route through {m["member_mcp"]}.{m["name"]} and pass its output downstream."""
    upstream = json.loads(payload) if payload.strip().startswith("{{") else {{"payload": payload}}
    return json.dumps(
        {{
            "stage": {i + 1},
            "tool": "{m["name"]}",
            "member_mcp": "{m["member_mcp"]}",
            "input": upstream,
            "output": {{"status": "routed", "next_stage": {i + 2 if i + 1 < len(members) else None}}},
        }},
        indent=2,
        ensure_ascii=False,
    )
'''
        )

    stages_list = ", ".join(f'"stage_{i + 1}_{m["name"]}"' for i, m in enumerate(members))

    source = f'''"""{chained_name} — composite chained MCP workflow forged by FORGE INFINITY.

Composite goal: {composite_goal}

Chained members ({len(members)}):
{chr(10).join(f"  {i + 1}. {m['member_mcp']} -> {m['name']}" for i, m in enumerate(members))}

DAG (levelled topology):
{chr(10).join("  # " + line for line in dag_json.splitlines())}
"""
from __future__ import annotations

import json

from fastmcp import FastMCP

mcp = FastMCP("{chained_name}")

CHAIN_MEMBERS = {members_json}

CHAIN_DAG = {dag_json}


@mcp.tool()
def list_chain_members() -> str:
    """List the member MCPs composed into this chained workflow, in execution order."""
    return json.dumps(CHAIN_MEMBERS, indent=2, ensure_ascii=False)

{''.join(tool_blocks)}


@mcp.tool()
def run_chain(initial_payload: str = "") -> str:
    """Execute the full chain: each stage's output is fed as the next stage's input."""
    results = []
    current = initial_payload
    for stage in [{stages_list}]:
        tool = globals()[stage]
        current = tool(current)
        results.append(json.loads(current))
    return json.dumps(
        {{"ok": True, "stages_executed": len(results), "results": results}},
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run()
'''
    compile(source, f"{chained_name}.py", "exec")  # must compile before writing
    return source


def chain_mcp_servers(
    mcp_names_or_ids: List[str],
    composite_goal: str,
) -> Dict[str, Any]:
    """Combine multiple MCP servers into a single chained workflow pipeline."""
    ensure_dirs()
    goal_clean = (composite_goal or "Chained Multi-MCP Workflow").strip()
    chained_name = f"chain-{int(time.time())}"

    collected_tools: List[Dict[str, Any]] = []
    members: List[Dict[str, Any]] = []
    seen_names = set()

    for name in mcp_names_or_ids:
        name_clean = name.strip()
        history_matches = search_history(name_clean)
        if history_matches:
            entry = history_matches[0]
            entry_tools = entry.get("tools", [])
            for t in entry_tools:
                tname = t if isinstance(t, str) else t.get("name", "")
                if tname and tname not in seen_names:
                    seen_names.add(tname)
                    collected_tools.append(
                        {
                            "name": tname,
                            "source": f"Chained from {entry.get('mcp_name', 'mcp')}",
                            "badge": "FORGED",
                            "description": f"Chained tool {tname}",
                        }
                    )
            members.append(
                {
                    "name": re.sub(r"[^a-z0-9_]+", "_", entry.get("mcp_name", name_clean).lower()).strip("_") or "member",
                    "member_mcp": entry.get("mcp_name", name_clean),
                    "history_id": entry.get("id", ""),
                    "tool_count": len(entry_tools),
                    "tools": entry_tools,
                }
            )

    # Fallback to cores if nothing matched
    if not collected_tools:
        for t in CORE_TOOL_MANIFEST:
            if t["name"] not in seen_names:
                seen_names.add(t["name"])
                collected_tools.append(dict(t))

    dag, _ = build_dag(goal_clean, collected_tools)
    skill_content = generate_single_skill(goal_clean, collected_tools, dag, chained_name)

    # Output chained composite server + skill
    chain_dir = MCP_REGISTRY_DIR / "servers" / chained_name
    chain_dir.mkdir(parents=True, exist_ok=True)
    chain_server_file = chain_dir / "server.py"
    chain_skill_file = chain_dir / "SKILL.md"

    composite_source = _render_composite_server(chained_name, goal_clean, members or [
        {"name": "fallback", "member_mcp": n, "tool_count": 1} for n in mcp_names_or_ids
    ], dag)
    chain_server_file.write_text(composite_source, "utf-8")
    chain_skill_file.write_text(skill_content, "utf-8")
    clean_server_path = str(chain_server_file).replace("\\", "/")

    hist_entry = record_history_entry(
        goal=goal_clean,
        mcp_name=chained_name,
        server_path=clean_server_path,
        tools=collected_tools,
        dag=dag,
        skill_content=skill_content,
        zip_path="",
        server_py=composite_source,
    )

    hot_load_into_ide("all", chained_name, clean_server_path)

    def _level_of(task_id: str, visiting: set | None = None) -> int:
        """Topological level: 0 for roots, else 1 + max(level of deps)."""
        visiting = visiting or set()
        if task_id in visiting:
            return 0
        deps = (dag.get(task_id) or {}).get("deps", [])
        visiting.add(task_id)
        level = 1 + max((_level_of(d, visiting) for d in deps if d in dag), default=-1)
        visiting.discard(task_id)
        return level

    return {
        "ok": True,
        "chained_name": chained_name,
        "composite_goal": goal_clean,
        "tools_count": len(collected_tools),
        "tools": [t["name"] for t in collected_tools],
        "members": members,
        "dag": dag,
        "dag_levels": {tid: _level_of(tid) for tid in dag},
        "skill_content": skill_content,
        "server_path": clean_server_path,
        "history_id": hist_entry["id"],
        "message": f"Successfully chained {len(mcp_names_or_ids)} MCPs into '{chained_name}'!",
    }
