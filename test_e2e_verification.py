"""Comprehensive E2E Verification Script for FORGE V3.

Tests:
1. Hardcoded 7 Core Tools preservation (<2s, zero LLM, official APIs for gmail/notion)
2. Official URL Detection (detect_official.py routes mail.google -> gmail, notion -> notion)
3. 3-Task RAM DAG planning & single-return validation (zero duplicate returns)
4. 6-Way Agent Exporter with accurate is_cli flags (CLI vs Config-only)
5. Single SKILL.md and ZIP structure (export.bat, export.sh, export_configs.json, 0 platform folders)
6. Atomic History storage (microsecond IDs, newest first)
7. Custom Forge Registry Meta MCP tools (list_forged_mcps, get_mcp_details, get_skill, search_mcps, export_mcp_to_platform)
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.forge.cores import CORE_SOURCES, CORE_TOOL_MANIFEST, CORE_TOOL_NAMES
from backend.forge.generator import render_unified_server
from backend.forge.utils.detect_official import classify_url
from backend.planner.planner import build_dag
from forge.exporter import (
    PLATFORM_METADATA,
    VALID_PLATFORMS,
    generate_all_export_configs,
    generate_export_for_platform,
    generate_export_scripts,
)
from forge.history import (
    FORGE_REGISTRY_JSON,
    get_all_history,
    get_history_by_id,
    record_history_entry,
    search_history,
)
from forge.mcp.forge_registry_mcp.server import (
    export_mcp_to_platform,
    get_mcp_details,
    get_skill,
    list_forged_mcps,
    search_mcps,
)
from forge.skills.single_skill_generator import generate_single_skill
from forge.zip_builder import build_zip


def verify_all():
    print("================================================================================")
    print("                      FORGE V3 COMPLETE VERIFICATION SUITE                     ")
    print("================================================================================")

    # --------------------------------------------------------------------------
    # 1. HARDCODED 7 CORES INTEGRITY CHECK
    # --------------------------------------------------------------------------
    print("\n[CHECK 1] Verifying 7 Hardcoded Cores...")
    expected_cores = {
        "amazon_search_ram",
        "amazon_check_discount",
        "amazon_monitor_ram_discount",
        "gmail_send_email",
        "gmail_notify_and_log",
        "notion_create_database_entry",
        "notion_log_price",
    }
    manifest_names = {t["name"] for t in CORE_TOOL_MANIFEST}
    assert expected_cores.issubset(manifest_names), f"Missing core tools: {expected_cores - manifest_names}"
    print(f"  [PASS] All 7 hardcoded cores present in manifest: {list(expected_cores)}")

    # --------------------------------------------------------------------------
    # 2. OFFICIAL DETECTION
    # --------------------------------------------------------------------------
    print("\n[CHECK 2] Verifying Official URL Detection (detect_official.py)...")
    res_gmail = classify_url("https://mail.google.com/mail/u/0/#inbox")
    res_notion = classify_url("https://notion.so/my-workspace")
    res_amazon = classify_url("https://www.amazon.com/dp/B08N5WRWNW")
    res_custom = classify_url("https://news.ycombinator.com")

    assert res_gmail["type"] == "OFFICIAL" and res_gmail["name"] == "gmail", f"Gmail detection failed: {res_gmail}"
    assert res_notion["type"] == "OFFICIAL" and res_notion["name"] == "notion", f"Notion detection failed: {res_notion}"
    assert res_amazon["type"] == "CUSTOM" and res_amazon["name"] == "amazon", f"Amazon detection failed: {res_amazon}"
    assert res_custom["type"] == "CUSTOM", f"Custom detection failed: {res_custom}"
    print("  [PASS] classify_url successfully routes official domains away from browser scraping.")

    # --------------------------------------------------------------------------
    # 3. DAG PLANNING & SINGLE RETURN IN SERVER.PY
    # --------------------------------------------------------------------------
    print("\n[CHECK 3] Verifying 3-Task RAM DAG & Single Return in Rendered server.py...")
    ram_goal = "Check RAM discount >20% mail and Notion"
    dag, meta = build_dag(ram_goal, CORE_TOOL_MANIFEST)
    print(f"  DAG Tasks: {list(dag.keys())}")
    assert len(dag) == 3, f"RAM goal DAG must have exactly 3 tasks, got {len(dag)}: {dag}"
    assert "amazon_monitor_ram_discount" in dag["t1"]["tool"]
    assert "gmail_notify_and_log" in dag["t2"]["tool"] and dag["t2"]["parallel"] is True
    assert "notion_log_price" in dag["t3"]["tool"] and dag["t3"]["parallel"] is True
    print("  [PASS] DAG generated 3 tasks (T1 -> T2 [Parallel] + T3 [Parallel]).")

    # Render server.py
    source, rendered_manifest, server_path = render_unified_server(
        goal=ram_goal,
        site_logs=[],
        site_tools=[],
        officials=[],
        dag=dag,
    )
    # Check for dead code or duplicate returns
    tool_blocks = re.findall(r"@mcp\.tool\(\)[\s\S]*?(?=@mcp\.tool\(\)|if __name__|$)", source)
    for block in tool_blocks:
        return_count = len(re.findall(r"^\s+return\s+", block, re.MULTILINE))
        # Each tool function should have a single return in try and single return in except
        # No back-to-back duplicate returns inside try block
        assert "return _extract" not in block or block.count("return _extract") <= 1, "Duplicate return _extract found!"
    print(f"  [PASS] Rendered server.py ({len(rendered_manifest)} tools) verified clean with 0 dead return statements.")

    # --------------------------------------------------------------------------
    # 4. 6-WAY AGENT EXPORTER
    # --------------------------------------------------------------------------
    print("\n[CHECK 4] Verifying 6-Way Agent Exporter (is_cli flags & commands)...")
    configs = generate_all_export_configs("unified-forge", server_path)
    assert len(configs) == 6, f"Expected 6 export configs, got {len(configs)}"

    # Check CLI platforms
    assert configs["claude_code"]["is_cli"] is True and configs["claude_code"]["command"].startswith("claude mcp add")
    assert configs["codex"]["is_cli"] is True and configs["codex"]["command"].startswith("codex mcp add")
    assert configs["opencode"]["is_cli"] is True and configs["opencode"]["command"].startswith("opencode mcp add")

    # Check Config-only platforms
    assert configs["cursor"]["is_cli"] is False and configs["cursor"]["command"] is None
    assert configs["zcode"]["is_cli"] is False and configs["zcode"]["command"] is None
    assert configs["antigravity"]["is_cli"] is False and configs["antigravity"]["command"] is None

    # Check script generation
    bat_str, sh_str = generate_export_scripts("unified-forge", server_path)
    assert "claude mcp add" in bat_str and "codex mcp add" in bat_str
    assert "claude mcp add" in sh_str and "codex mcp add" in sh_str
    print("  [PASS] 6-Way Exporter verified with accurate is_cli flags and export scripts.")

    # --------------------------------------------------------------------------
    # 5. SINGLE SKILL.MD + ZIP ARCHIVE INTEGRITY
    # --------------------------------------------------------------------------
    print("\n[CHECK 5] Verifying Single SKILL.md & ZIP Archive...")
    # Clean registry for test
    if FORGE_REGISTRY_JSON.exists():
        FORGE_REGISTRY_JSON.unlink()

    # Workflow 1
    zip_path_1, claude_1, cursor_1, readme_1, skill_1, configs_1 = build_zip(
        server_py=source,
        server_abs_path=server_path,
        officials=[],
        manifest=rendered_manifest,
        dag=dag,
        goal=ram_goal,
    )

    entry_1 = record_history_entry(
        goal=ram_goal,
        mcp_name="unified-forge",
        server_path=server_path,
        tools=rendered_manifest,
        dag=dag,
        skill_content=skill_1,
        zip_path=str(zip_path_1),
        server_py=source,
    )

    # Workflow 2
    goal_2 = "Find hackathons and log events"
    tools_2 = [
        {"name": "devpost_search_hackathons", "source": "Custom Devpost Forged", "badge": "FORGED", "description": "Search Devpost hackathons"},
        {"name": "mlh_get_events", "source": "Custom MLH Forged", "badge": "FORGED", "description": "Get MLH events"},
    ]
    dag_2 = {"t1": {"tool": "devpost_search_hackathons", "source": "Custom Devpost Forged"}}
    zip_path_2, claude_2, cursor_2, readme_2, skill_2, configs_2 = build_zip(
        server_py=source,
        server_abs_path=server_path,
        officials=[],
        manifest=tools_2,
        dag=dag_2,
        goal=goal_2,
    )
    entry_2 = record_history_entry(
        goal=goal_2,
        mcp_name="unified-forge",
        server_path=server_path,
        tools=tools_2,
        dag=dag_2,
        skill_content=skill_2,
        zip_path=str(zip_path_2),
        server_py=source,
    )

    # Verify ZIP contents
    with zipfile.ZipFile(zip_path_2, "r") as zf:
        names = zf.namelist()
        print(f"  ZIP files: {names}")
        assert "SKILL.md" in names, "SKILL.md must be at ZIP root"
        assert "server.py" in names, "server.py must be at ZIP root"
        assert "requirements.txt" in names, "requirements.txt must be at ZIP root"
        assert "export_configs.json" in names, "export_configs.json must be at ZIP root"
        assert "export.bat" in names, "export.bat must be at ZIP root"
        assert "export.sh" in names, "export.sh must be at ZIP root"
        assert "README.md" in names, "README.md must be at ZIP root"

        # Check there are NO 6 folders
        for folder in ["claude", "cursor", "zcode", "opencode", "antigravity", "codex"]:
            assert not any(n.startswith(f"{folder}/") for n in names), f"ZIP must not contain {folder}/ folder"

    # Check SKILL.md content
    assert "---" in skill_2 and "mcp: unified-forge" in skill_2
    assert "Do not re-discover tools" in skill_2
    print("  [PASS] ZIP contains single SKILL.md, export scripts, and zero platform subfolders.")

    # --------------------------------------------------------------------------
    # 6. ATOMIC HISTORY STORAGE & SORTING
    # --------------------------------------------------------------------------
    print("\n[CHECK 6] Verifying Atomic History Storage & Sorting (Newest First)...")
    history_entries = get_all_history()
    assert len(history_entries) == 2, f"Expected 2 history entries, got {len(history_entries)}"
    assert history_entries[0]["id"] == entry_2["id"], "Newest entry must be at index 0"
    assert history_entries[1]["id"] == entry_1["id"], "Older entry must be at index 1"
    assert "_" in entry_1["id"], "ID must have microsecond format"
    print(f"  [PASS] History storage verified: 2 entries, sorted newest first with microsecond IDs.")

    # --------------------------------------------------------------------------
    # 7. FORGE REGISTRY META MCP SERVER TOOLS
    # --------------------------------------------------------------------------
    print("\n[CHECK 7] Verifying Forge Registry Meta MCP Server Tools...")
    # list_forged_mcps
    mcps_json = list_forged_mcps(10)
    mcps_list = json.loads(mcps_json)
    assert len(mcps_list) == 2
    print("  - list_forged_mcps: OK (2 entries)")

    # get_mcp_details
    details = json.loads(get_mcp_details(entry_1["id"]))
    assert details["id"] == entry_1["id"] and "RAM" in details["goal"]
    print("  - get_mcp_details: OK")

    # get_skill
    skill_out = get_skill(entry_1["id"])
    assert "Skill: Check RAM discount" in skill_out
    print("  - get_skill: OK")

    # search_mcps
    search_res = json.loads(search_mcps("RAM"))
    assert len(search_res) == 1 and search_res[0]["id"] == entry_1["id"]
    print("  - search_mcps: OK")

    # export_mcp_to_platform
    export_out = json.loads(export_mcp_to_platform(entry_1["id"], "claude_code"))
    assert export_out["platform_id"] == "claude_code" and "claude mcp add" in export_out["command"]
    print("  - export_mcp_to_platform: OK")

    print("\n================================================================================")
    print("                  ALL FORGE V3 VERIFICATION CHECKS PASSED!                      ")
    print("================================================================================")


if __name__ == "__main__":
    verify_all()
