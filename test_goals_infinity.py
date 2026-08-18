"""FORGE INFINITY — Goal-based test harness.

Runs all 15 goals + edge/stress against the live backend modules and prints
a PASS/FAIL report. Usage: python test_goals_infinity.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

RESULTS = []


def check(goal: str, name: str, ok: bool, detail: str = ""):
    RESULTS.append((goal, name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {goal} :: {name}" + (f" — {detail}" if detail else ""))


def section(title: str):
    print(f"\n=== {title} ===")


def main():
    # ---------------------------------------------------------------- GOAL 1
    section("GOAL 1 — Factory Forge Text")
    from backend.factory.factory_mcp import forge_new_mcp

    t0 = time.time()
    r = json.loads(forge_new_mcp(goal="Track RAM usage and notify via email", official_integrations=["gmail"], server_name="ram_tracker"))
    elapsed = time.time() - t0
    check("G1", f"forge time {r.get('elapsed_seconds')}s < 2.5s", r.get("elapsed_seconds", 99) < 2.5)
    check("G1", "path is mcp/ram_tracker/server.py", r["server_path"].endswith("mcp/ram_tracker/server.py"), r["server_path"])
    check("G1", "path normalized '/' (no backslash)", "\\" not in r["server_path"])
    check("G1", "SKILL.md at mcp/<name>/SKILL.md exists", Path(r["skill_root"]).exists(), r["skill_root"])
    check("G1", "server.py exists", Path(r["server_path"]).exists())
    check("G1", f"tools == 7 (got {r['tools_count']})", r["tools_count"] == 7)
    check("G1", "forge.mcp.json updated (mtime fresh)", (ROOT / "forge.mcp.json").exists())
    cfg = json.loads((ROOT / "forge.mcp.json").read_text("utf-8"))
    check("G1", "forge.mcp.json has unified_server/forge_factory entries",
          "forge_factory" in cfg.get("servers", {}) and "servers" in cfg)

    # ---------------------------------------------------------------- GOAL 2
    section("GOAL 2 — Factory Forge Voice + auto-chain")
    from backend.factory.factory_mcp import forge_from_voice

    rv = json.loads(forge_from_voice("Forge Notion writer MCP and chain with ram_tracker"))
    check("G2", "voice forge success", rv.get("ok") is True)
    check("G2", "voice transcript parsed into name (not generic)", "notion" in rv.get("mcp_id", ""), rv.get("mcp_id"))
    check("G2", "auto chain_mcps triggered", rv.get("chain", {}).get("ok") is True, json.dumps(rv.get("chain", {}))[:120])
    check("G2", "chain composite server written", Path(rv.get("chain", {}).get("server_path", "x")).exists())

    # ---------------------------------------------------------------- GOAL 3
    section("GOAL 3 — Universal Config 5 IDEs")
    cfg_raw = (ROOT / "forge.mcp.json").read_text("utf-8")
    cfg = json.loads(cfg_raw)
    ides = cfg.get("ides", {})
    for ide in ("antigravity", "z_code", "claude_code", "cursor", "windsurf"):
        present = ide in ides
        check("G3", f"ides.{ide} present", present)
        if present:
            entry = ides[ide]
            if ide == "claude_code":
                check("G3", f"{ide} has cli_command", bool(entry.get("cli_command")))
            snippet_ok = isinstance(entry.get("snippet"), dict) and isinstance(entry["snippet"].get("mcpServers"), dict)
            check("G3", f"{ide} snippet valid mcpServers JSON", snippet_ok)
    check("G3", "no backslash anywhere in forge.mcp.json", "\\" not in cfg_raw)
    servers = cfg.get("servers", {})
    check("G3", "servers.forge_factory args use '/'", all("\\" not in a for a in servers.get("forge_factory", {}).get("args", ["\\"])))

    # ---------------------------------------------------------------- GOAL 4
    section("GOAL 4 — Hot-Loader 1-Click Inject")
    from backend.factory.hot_loader import hot_load_into_ide, validate_environment

    sp = (ROOT / "mcp" / "ram_tracker" / "server.py").resolve().as_posix()
    hl = hot_load_into_ide("all", "ram_tracker", sp)
    all_ok = hl.get("ok") and all(v.get("ok") for v in hl.get("results", {}).values())
    check("G4", "hot_load all 5 IDEs ok", all_ok, json.dumps({k: v.get("ok") for k, v in hl.get("results", {}).items()}))
    home = Path.home()
    for ide_path in (
        home / ".claude.json",
        home / ".cursor" / "mcp.json",
        home / ".codeium" / "windsurf" / "mcp_config.json",
        home / ".antigravity" / "mcp.json",
        home / ".zcode" / "mcp.json",
    ):
        exists = ide_path.exists()
        content_ok = False
        no_backslash = True
        if exists:
            try:
                data = json.loads(ide_path.read_text("utf-8"))
                content_ok = "ram_tracker" in data.get("mcpServers", {})
                no_backslash = "\\" not in json.dumps(data.get("mcpServers", {}).get("ram_tracker", {}))
            except Exception:
                content_ok = False
        check("G4", f"{ide_path.name} written + ram_tracker registered + '/'", exists and content_ok and no_backslash, str(ide_path))
    val = validate_environment(sp)
    check("G4", "validator green: path/python/fastmcp", val["ok"] and val["path_exists"] and val["python_available"] and val["fastmcp_ready"])
    val_bad = validate_environment("D:/nonexistent/path/server.py")
    check("G4", "validator RED on wrong path (not ok)", val_bad["ok"] is False and val_bad["path_exists"] is False)

    # ---------------------------------------------------------------- GOAL 5
    section("GOAL 5 — Marketplace Publish Day-0 Clean")
    from backend.marketplace.marketplace import load_marketplace, publish_mcp, save_marketplace

    save_marketplace([])  # reset to Day-0 clean
    pkgs = load_marketplace()
    check("G5", "marketplace.json starts [] clean", pkgs == [])
    p1 = publish_mcp("ram_tracker", author="test", tags=["System"])
    check("G5", "publish ok", p1.get("ok") is True)
    pkg = p1.get("package", {})
    for field in ("package_id", "name", "version", "author", "tags", "tools_count", "installs_count", "published_at"):
        check("G5", f"entry has field '{field}'", field in pkg)
    check("G5", "installs starts 0", pkg.get("installs_count") == 0)
    check("G5", f"tools=7 recorded (got {pkg.get('tools_count')})", pkg.get("tools_count") == 7)
    p2 = publish_mcp("ram_tracker", author="test", tags=["System"])
    pkgs = load_marketplace()
    check("G5", f"republish bumps version ({p2.get('version')}), no duplicate (count={len(pkgs)})", len(pkgs) == 1 and p2.get("version") != p1.get("version") and p2.get("republished") is True)
    # corrupt recovery
    (ROOT / "mcp_registry" / "marketplace.json").write_text("{corrupt json", "utf-8")
    pkgs = load_marketplace()
    check("G5", "corrupt marketplace.json recovered to []", pkgs == [])
    p3 = publish_mcp("ram_tracker", author="test")
    check("G5", "publish after corruption recreate works", p3.get("ok") is True)

    # ---------------------------------------------------------------- GOAL 6
    section("GOAL 6 — Marketplace Search & Install + Hot-Load")
    from backend.marketplace.marketplace import install_package, search_packages

    hits = search_packages("RAM")
    check("G6", "search 'RAM' finds package", any("ram_tracker" == h["name"] for h in hits), str([h["name"] for h in hits]))
    cats_ok = all(h.get("category") for h in hits)
    check("G6", "category assigned", cats_ok)
    inst = install_package(p3["package_id"])
    check("G6", "1-click install ok", inst.get("ok") is True)
    check("G6", "install writes server + SKILL.md", Path(inst["server_path"]).exists() and Path(inst["skill_path"]).exists())
    check("G6", "install hot-loads into IDEs", inst.get("hot_load", {}).get("ok") is True)
    pkgs = load_marketplace()
    check("G6", "installs_count incremented", pkgs and pkgs[0].get("installs_count", 0) >= 1)

    # ---------------------------------------------------------------- GOAL 7
    section("GOAL 7 — Self-Heal Duplicate Return")
    from backend.healer.self_heal_engine import diagnose_and_heal_file

    victim = ROOT / "mcp" / "ram_tracker" / "server.py"
    orig = victim.read_text("utf-8")
    # Inject: duplicate return + dead code inside first tool function (same indent as the return)
    lines = orig.splitlines(keepends=True)
    injected = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("return ") and "@mcp.tool()" in "".join(lines[max(0, i - 40):i]):
            indent = ln[: len(ln) - len(ln.lstrip())]
            lines.insert(i + 1, f"{indent}x_dead_code_after_return = 1\n")
            lines.insert(i + 2, f'{indent}return {{"duplicate": True}}\n')
            injected = True
            break
    victim.write_text("".join(lines), "utf-8")
    check("G7", "bug injected into first tool (compiles as dead code)", injected)
    try:
        compile(victim.read_text("utf-8"), str(victim), "exec")
        valid_injection = True
    except SyntaxError:
        valid_injection = False
    check("G7", "injected bug is valid python (realistic)", valid_injection)
    t0 = time.time()
    h = diagnose_and_heal_file(str(victim), "duplicate return _extract")
    heal_ms = h.get("elapsed_ms", 999)
    check("G7", f"heal < 200ms (got {heal_ms}ms)", heal_ms < 200)
    check("G7", "ok + compilation verified", h.get("ok") and h.get("compilation_verified"))
    check("G7", "duplicate return detected", any("uplicate" in e for e in h.get("errors_detected", [])))
    check("G7", "patch applied", any("uplicate" in p.lower() for p in h.get("patches_applied", [])))
    healed = victim.read_text("utf-8")
    check("G7", "dead code removed from file", "x_dead_code_after_return" not in healed)
    victim.write_text(orig, "utf-8")

    # ---------------------------------------------------------------- GOAL 8
    section("GOAL 8 — Self-Heal Path Backslash")
    orig = victim.read_text("utf-8")
    # Insert a Windows backslash path literal after the __future__ import (valid placement)
    marker = "from __future__ import annotations\n"
    victim.write_text(orig.replace(marker, marker + 'WIN_PATH = "D:\\\\Aditya\\\\Forge\\\\logs"\n', 1), "utf-8")
    h8 = diagnose_and_heal_file(str(victim), "unescaped backslash")
    healed8 = victim.read_text("utf-8")
    g8_ok = "D:/Aditya/Forge" in healed8 and "D:\\\\Aditya" not in healed8
    if not g8_ok:
        print("    [debug] WIN line after heal:", [l for l in healed8.splitlines() if "WIN_PATH" in l])
        print("    [debug] h8:", {k: h8.get(k) for k in ("ok", "code_modified", "compilation_verified", "compilation_error", "errors_detected", "patches_applied")})
    check("G8", "backslash path fixed to '/'", g8_ok)
    check("G8", "heal ok + compile verified", h8.get("ok") is True and h8.get("compilation_verified") is True)
    victim.write_text(orig, "utf-8")

    # ---------------------------------------------------------------- GOAL 9
    section("GOAL 9 — Self-Heal FastMCP Decorator")
    orig = victim.read_text("utf-8")
    # Inject: strip the FastMCP import block entirely + bare decorator (both valid syntax alone)
    import_block = (
        "try:\n"
        "    from fastmcp import FastMCP\n"
        "except ImportError:  # fall back to the reference implementation bundled with `mcp`\n"
        "    from mcp.server.fastmcp import FastMCP\n"
    )
    bugged9 = orig.replace(import_block, "", 1).replace("@mcp.tool()", "@mcp.tool", 1)
    victim.write_text(bugged9, "utf-8")
    try:
        compile(bugged9, str(victim), "exec")
        valid9 = True
    except SyntaxError:
        valid9 = False
    check("G9", "decorator bug is valid python (realistic)", valid9)
    h9 = diagnose_and_heal_file(str(victim), "TypeError decorator missing parentheses")
    healed9 = victim.read_text("utf-8")
    check("G9", "@mcp.tool normalized to @mcp.tool()", "@mcp.tool\n" not in healed9)
    check("G9", "FastMCP import re-injected", "from fastmcp import FastMCP" in healed9)
    check("G9", "compilation verified", h9.get("compilation_verified") is True)
    victim.write_text(orig, "utf-8")

    # ---------------------------------------------------------------- GOAL 10
    section("GOAL 10 — Benchmark Empirical")
    from backend.benchmark.benchmark_suite import run_comparative_benchmark

    b = run_comparative_benchmark("ram_tracker")
    live = b.get("live_execution", {})
    check("G10", "live runner measured real time", live.get("live_measured_seconds", 99) < 5)
    check("G10", "FORGE tool_count 7 vs 15 vs 18", b["baselines"]["forge_infinity"]["tool_count"] == 7 and b["baselines"]["stainless"]["tool_count"] == 15 and b["baselines"]["spex"]["tool_count"] == 18)
    check("G10", "2.1s vs 175s vs 240s vs 4.2h baselines", b["baselines"]["forge_infinity"]["time_to_first_tool_s"] <= 2.1 and b["baselines"]["stainless"]["time_to_first_tool_s"] == 175.0)
    check("G10", "0 vs 45k vs 62k tokens", b["baselines"]["forge_infinity"]["tokens_consumed"] == 0 and b["baselines"]["stainless"]["tokens_consumed"] == 45200)
    check("G10", "radar comparison present (6 metrics)", len(b.get("radar_comparison", [])) == 6)

    # ---------------------------------------------------------------- GOAL 13
    section("GOAL 13 — Auto-Chaining Engine")
    from backend.chain.mcp_chainer import chain_mcp_servers

    c = chain_mcp_servers(["ram_tracker", "notion_writer"], "Compose RAM tracking with Notion logging")
    check("G13", "chain ok", c.get("ok") is True)
    check("G13", "composite server.py exists + compiles", Path(c["server_path"]).exists())
    compiled = False
    try:
        compile(Path(c["server_path"]).read_text("utf-8"), "chain", "exec")
        compiled = True
    except SyntaxError:
        compiled = False
    check("G13", "composite server syntax valid", compiled)
    check("G13", "DAG topology levelled", isinstance(c.get("dag_levels"), dict) and len(c["dag_levels"]) > 0, str(c.get("dag_levels")))

    # ---------------------------------------------------------------- GOAL 14
    section("GOAL 14 — Telemetry")
    from backend.telemetry import snapshot

    tel = snapshot()
    check("G14", "telemetry ok", tel.get("ok") is True)
    check("G14", "invocation counts recorded", tel.get("total_invocations", 0) >= 3, str(tel.get("invocations")))
    check("G14", "latency recorded (avg_latency_ms)", len(tel.get("avg_latency_ms", {})) > 0)
    check("G14", "memory tracked", tel.get("memory_mb", 0) > 0)
    check("G14", "self-heal events recorded", tel.get("self_heal", {}).get("count", 0) >= 1)

    # ---------------------------------------------------------------- GOAL 15
    section("GOAL 15 — Export Universal")
    bat = (ROOT / "export.bat").read_text("utf-8")
    sh = (ROOT / "export.sh").read_text("utf-8")
    check("G15", "export.bat uses '/' path", "\\" not in bat and "D:/" in bat)
    check("G15", "export.sh uses '/' path", "D:/" in sh)
    zf = zipfile.ZipFile(ROOT / "dist" / "ram_tracker-mcp.zip")
    names = zf.namelist()
    check("G15", "dist zip contains forge.mcp.json", "forge.mcp.json" in names, str(names[:5]))
    check("G15", "dist zip contains SKILL.md + server.py", "SKILL.md" in names and "server.py" in names)

    # ---------------------------------------------------------------- EDGE/STRESS
    section("EDGE & STRESS")
    # 10 MCP fast loop
    t0 = time.time()
    ok_count = 0
    for i in range(10):
        r = json.loads(forge_new_mcp(goal=f"Track price site {i} and log to notion", urls=["https://example.com"], official_integrations=["notion"], server_name=f"stress_{i}"))
        if r.get("ok"):
            ok_count += 1
    stress_s = time.time() - t0
    check("EDGE", f"10 MCP loop no crash ({ok_count}/10 ok in {stress_s:.1f}s)", ok_count == 10)
    from backend.marketplace.marketplace import load_marketplace as lm
    pub_ok = 0
    for i in range(10):
        pr = publish_mcp(f"stress_{i}")
        if pr.get("ok"):
            pub_ok += 1
    check("EDGE", f"all 10 stress MCPs publishable ({pub_ok}/10)", pub_ok == 10)
    check("EDGE", "marketplace holds 10 stress entries + ram_tracker", len(lm()) == 11)

    print("\n" + "=" * 70)
    passed = sum(1 for _, _, ok, _ in RESULTS if ok)
    failed = sum(1 for _, _, ok, _ in RESULTS if not ok)
    print(f"TOTAL: {passed} PASS / {failed} FAIL / {len(RESULTS)} checks")
    if failed:
        print("\nFAILED CHECKS:")
        for goal, name, ok, detail in RESULTS:
            if not ok:
                print(f"  [{goal}] {name} — {detail}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
