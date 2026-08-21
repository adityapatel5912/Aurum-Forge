"""Earth Addition acceptance suite — NextStep Hacks 2026 (Earth Forward).

Run:  python test_earth_addition.py [base_url]
      (default http://127.0.0.1:8740 — start the API first with
       `python backend/main.py --serve --port 8740`)

Verifies, with REAL outputs only:
  1. New eco servers exist, py_compile PASS, exact tool rosters
  2. Super-Hub auto-discovered them (total_tools >= 67, zero backslashes, >5KB)
  3. /api/earth/health, /api/earth/chains (8 chains), /api/earth/chains/run,
     /api/earth/stats, /api/earth/vault/scan — all 200 with proof hash
  4. Existing routes still 200 (no breaking change)
  5. dist zips exist, >1KB, bundled server.py py_compiles
  6. No hardcoded drive letters in Earth Addition sources; zero backslashes
     in generated JSONs
"""
from __future__ import annotations

import json
import py_compile
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8740").rstrip("/")

PASS = 0
FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def http(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


EXPECTED_TOOLS = {
    "forge_eco": {"eco_air_quality", "eco_water_quality", "eco_waste_audit", "eco_solar_calc",
                  "eco_wildlife_monitor", "chain_eco_full_workflow"},
    "chain_eco_monitor": {"get_chain_metadata", "tavily_search_eco", "browser_fetch_enrich_eco",
                          "eco_air_quality", "eco_water_quality", "notion_create_page_eco",
                          "slack_post_message_eco", "chain_eco_monitor_full_workflow"},
    "chain_waste_reduce": {"get_chain_metadata", "eco_waste_audit", "sheets_add_row",
                           "notion_create_page", "slack_post_message", "chain_waste_reduce_full_workflow"},
    "chain_renewable_optimize": {"get_chain_metadata", "eco_solar_calc", "sheets_add_row",
                                 "browser_fetch_enrich", "notion_create_page", "slack_post_message",
                                 "chain_renewable_optimize_full_workflow"},
}


def tools_in_file(server_file: Path) -> set[str]:
    import ast

    tree = ast.parse(server_file.read_text("utf-8", errors="replace"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                dname = ""
                if isinstance(dec, ast.Call):
                    dname = getattr(dec.func, "attr", "") or getattr(dec.func, "id", "")
                elif isinstance(dec, (ast.Attribute, ast.Name)):
                    dname = getattr(dec, "attr", "") or getattr(dec, "id", "")
                if dname == "tool":
                    names.add(node.name)
    return names


def main() -> int:
    print("=" * 72)
    print("EARTH ADDITION ACCEPTANCE SUITE — real outputs only")
    print(f"BASE: {BASE}")
    print("=" * 72)

    print("\n[1] Eco servers on disk + py_compile + tool rosters")
    for name, expected in EXPECTED_TOOLS.items():
        server_file = ROOT / "forge" / "mcp" / name / "server.py"
        check(f"{name}/server.py exists", server_file.exists())
        if not server_file.exists():
            continue
        try:
            py_compile.compile(str(server_file), doraise=True)
            check(f"{name} py_compile", True)
        except Exception as e:
            check(f"{name} py_compile", False, str(e)[:80])
        found = tools_in_file(server_file)
        check(f"{name} tool roster ({len(found)})", found == expected,
              f"missing={sorted(expected - found)} extra={sorted(found - expected)}" if found != expected else "")

    print("\n[2] Super-Hub auto-discovery")
    hub_cfg = ROOT / "forge" / "mcp" / "forge_aurum_hub" / "super_hub.mcp.json"
    if hub_cfg.exists():
        cfg = json.loads(hub_cfg.read_text("utf-8"))
        tools = cfg["aurum_auto_update"]["total_tools"]
        servers = cfg["aurum_auto_update"]["total_servers"]
        text = hub_cfg.read_text("utf-8")
        check(f"super_hub.mcp.json >5KB ({hub_cfg.stat().st_size}B)", hub_cfg.stat().st_size > 5120)
        check(f"total_tools >= 67 ({tools})", tools >= 67)
        check(f"earth servers discovered", all(s in cfg["discovered_servers"] for s in EXPECTED_TOOLS),
              f"servers={servers}")
        check("zero backslashes in super_hub.mcp.json", "\\" not in text)
        check("give_once + auto_update + aurum_verified",
              cfg["super_hub_summary"]["give_once"] is True
              and cfg["mcpServers"]["forge-aurum-hub"]["auto_update"] is True
              and cfg["mcpServers"]["forge-aurum-hub"]["aurum_verified"] is True
              and cfg["mcpServers"]["forge-aurum-hub"]["hash"] == "f6cdbd0a07f2")
    else:
        check("super_hub.mcp.json exists", False)

    print("\n[3] /api/earth/* routes")
    code, health = http("GET", "/api/earth/health")
    check(f"GET /api/earth/health -> {code}", code == 200 and health.get("status") == "ok")
    check("earth health payload", health.get("earth_forward") is True
          and health.get("hash") == "f6cdbd0a07f2"
          and health.get("aurum_verified") is True
          and health.get("total_tools", 0) >= 67, f"tools={health.get('total_tools')} uptime={health.get('uptime_s')}")

    code, chains = http("GET", "/api/earth/chains")
    ids = [c.get("id") for c in chains.get("chains", [])]
    check(f"GET /api/earth/chains -> {code} ({len(ids)} chains)", code == 200 and len(ids) == 8)
    check("8 chains = 3 earth + 5 existing",
          {"chain_eco_monitor", "chain_waste_reduce", "chain_renewable_optimize",
           "chain_research", "chain_content", "chain_ops", "chain_dev_workflow",
           "chain_sales_outreach"} == set(ids))
    check("earth chains aurum_verified with 12-char hash",
          all(c.get("aurum_verified") and len(str(c.get("hash", ""))) == 12
              for c in chains.get("earth_chains", [])))

    for chain_key, expect_channel in [("eco_monitor", "#earth-forward"),
                                      ("waste_reduce", "#sustainability"),
                                      ("renewable_optimize", "#sustainability")]:
        code, res = http("POST", "/api/earth/chains/run",
                         {"chain": chain_key, "city": "Balasar, Gujarat", "usage_kwh": 300})
        ok = (code == 200 and res.get("status") == "success"
              and res.get("slack_posted") is True and res.get("notion_url", "").startswith("https://notion.so/")
              and res.get("hash") == "f6cdbd0a07f2" and res.get("tokens_saved", 0) >= 45200)
        check(f"POST /api/earth/chains/run {chain_key} -> {code}", ok,
              f"notion={str(res.get('notion_url'))[:52]} channel={res.get('slack_channel')} time={res.get('time_human')}")

    code, stats = http("GET", "/api/earth/stats")
    check(f"GET /api/earth/stats -> {code}", code == 200 and stats.get("total_reports", 0) >= 3,
          f"reports={stats.get('total_reports')} waste_kg={stats.get('total_waste_kg_reduced')} "
          f"solar_kw={stats.get('total_solar_potential_kw')} tokens={stats.get('total_tokens_saved')}")

    code, vault = http("POST", "/api/earth/vault/scan", {})
    check(f"POST /api/earth/vault/scan -> {code}", code == 200 and vault.get("security_score") == 100
          and vault.get("can_publish") is True, f"score={vault.get('security_score')} badge={vault.get('badge_label')}")

    print("\n[4] Existing routes still 200 (no breaking change)")
    for path in ["/api/health", "/api/health/deep", "/ping", "/api/aurum/chains", "/api/aurum/hub/status"]:
        code, _ = http("GET", path)
        check(f"GET {path} -> {code}", code == 200)

    print("\n[5] dist zips >1KB + bundled py_compile")
    for zname in ["forge_eco-mcp.zip", "chain_eco_monitor-mcp.zip", "chain_waste_reduce-mcp.zip",
                  "chain_renewable_optimize-mcp.zip", "eco-report.zip", "unified-mcp.zip"]:
        zpath = ROOT / "dist" / zname
        if not zpath.exists():
            check(f"dist/{zname} exists", False)
            continue
        size = zpath.stat().st_size
        compile_ok = True
        with zipfile.ZipFile(zpath) as zf:
            for n in zf.namelist():
                if n.endswith(".py"):
                    with tempfile.TemporaryDirectory() as td:
                        p = Path(td) / "s.py"
                        p.write_bytes(zf.read(n))
                        try:
                            py_compile.compile(str(p), doraise=True)
                        except Exception:
                            compile_ok = False
        check(f"dist/{zname} ({size}B)", size > 1024 and compile_ok,
              "" if size > 1024 else "TOO SMALL")

    print("\n[6] Path hygiene (Earth Addition sources)")
    earth_files = list((ROOT / "forge" / "mcp" / "forge_eco").glob("**/*")) + \
        [ROOT / "backend" / "aurum" / "earth.py", ROOT / "forge" / "earth_dist_build.py",
         ROOT / "frontend" / "src" / "components" / "EarthForwardView.tsx",
         ROOT / "frontend" / "src" / "components" / "EarthDependencyGraph.tsx"]
    hits = []
    for f in earth_files:
        if f.is_file() and "__pycache__" not in str(f):
            try:
                if "D:/" in f.read_text("utf-8", errors="replace"):
                    hits.append(str(f.relative_to(ROOT)))
            except Exception:
                pass
    check("grep 'D:/' across Earth Addition sources = 0", not hits, f"hits={hits}")

    print("\n" + "=" * 72)
    print(f"RESULT: {PASS} PASS / {FAIL} FAIL — {'ALL GREEN' if FAIL == 0 else 'FIX REQUIRED'}")
    print("Forge Once. Use Everywhere. Verify Forever. For Earth.")
    print("=" * 72)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
