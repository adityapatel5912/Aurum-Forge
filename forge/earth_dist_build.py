"""Earth Addition — dist bundle builder (NextStep Hacks 2026, Earth Forward).

Builds the downloadable evidence artifacts, all with '/'-normalized paths:
  dist/forge_eco-mcp.zip, dist/chain_eco_monitor-mcp.zip,
  dist/chain_waste_reduce-mcp.zip, dist/chain_renewable_optimize-mcp.zip
  dist/eco-report.zip  (real workflow run output + server sources + SKILL/README)

Every zip is > 1KB, py_compile-verified against the bundled server.py, and is
also rebuildable on the fly via GET /api/download/<slug>-mcp.zip.

Run:  python forge/earth_dist_build.py
"""
from __future__ import annotations

import importlib.util
import json
import py_compile
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# When run as a script, sys.path[0] is this file's dir (forge/) whose mcp/
# subpackage would shadow the MCP SDK (`import mcp.types`) used by fastmcp.
# Swap that entry for the project ROOT (repo-root mcp/ is a namespace pkg).
_forge_dir = str((ROOT / "forge").resolve())
sys.path = [str(ROOT) if (p and str(Path(p).resolve()) == _forge_dir) else p for p in sys.path]

from forge.zip_builder import build_zip

DIST = ROOT / "dist"
EARTH_SERVERS = [
    ("forge_eco", "forge/mcp/forge_eco/server.py"),
    ("chain_eco_monitor", "forge/mcp/chain_eco_monitor/server.py"),
    ("chain_waste_reduce", "forge/mcp/chain_waste_reduce/server.py"),
    ("chain_renewable_optimize", "forge/mcp/chain_renewable_optimize/server.py"),
]


def _import_server(rel_path: str, mod_id: str):
    server_file = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_id, str(server_file))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_mcp_zips() -> list[Path]:
    DIST.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    for name, rel in EARTH_SERVERS:
        server_file = ROOT / rel
        source = server_file.read_text("utf-8", errors="replace")
        out_zip = DIST / f"{name}-mcp.zip"
        build_zip(
            server_py=source,
            server_abs_path=str(server_file.resolve()).replace("\\", "/"),
            officials=[],
            manifest=[],
            dag={},
            goal=f"Operate {name} Earth Forward workflow",
            out_zip=out_zip,
            server_name=name,
            skill_dir=server_file.parent,
            include_universal_config=True,
        )
        built.append(out_zip)
    return built


def build_eco_report_zip() -> tuple[Path, dict]:
    """Run the REAL eco workflows and seal their outputs into dist/eco-report.zip."""
    DIST.mkdir(parents=True, exist_ok=True)

    eco = _import_server("forge/mcp/forge_eco/server.py", "earth_report_eco")
    monitor = _import_server("forge/mcp/chain_eco_monitor/server.py", "earth_report_monitor")
    waste = _import_server("forge/mcp/chain_waste_reduce/server.py", "earth_report_waste")
    renewable = _import_server("forge/mcp/chain_renewable_optimize/server.py", "earth_report_renewable")

    report = {
        "title": "Earth Forward Report — Aurum Forge Earth Addition",
        "tagline": "Forge Once. Use Everywhere. Verify Forever. For Earth.",
        "theme": "Earth Forward — NextStep Hacks 2026",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "proof_hash": "f6cdbd0a07f2",
        "city": "Balasar, Gujarat",
        "workflows": {
            "chain_eco_monitor_full_workflow": json.loads(monitor.chain_eco_monitor_full_workflow("Balasar, Gujarat")),
            "chain_waste_reduce_full_workflow": json.loads(waste.chain_waste_reduce_full_workflow(
                ["plastic_bottle", "food_scraps", "cardboard"])),
            "chain_renewable_optimize_full_workflow": json.loads(renewable.chain_renewable_optimize_full_workflow(
                "Balasar, Gujarat", 300.0)),
            "chain_eco_full_workflow": json.loads(eco.chain_eco_full_workflow("Balasar, Gujarat")),
        },
    }

    report_path = DIST / "eco-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")

    out_zip = DIST / "eco-report.zip"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(report_path, "eco-report.json")
        for name, rel in EARTH_SERVERS:
            zf.write(ROOT / rel, f"servers/{name}/server.py")
        for extra, arc in [
            ("forge/mcp/forge_eco/SKILL.md", "servers/forge_eco/SKILL.md"),
            ("forge/mcp/forge_eco/README.md", "servers/forge_eco/README.md"),
            ("forge/mcp/forge_eco/forge.mcp.json", "servers/forge_eco/forge.mcp.json"),
        ]:
            p = ROOT / extra
            if p.exists():
                zf.write(p, arc)
        zf.writestr("EARTH_FORWARD.md", (
            "# Earth Forward Report Bundle\n\n"
            "Forge Once. Use Everywhere. Verify Forever. For Earth.\n\n"
            "Contents: real workflow outputs (eco-report.json) + the 4 Earth Addition\n"
            "MCP server sources (forge_eco, chain_eco_monitor, chain_waste_reduce,\n"
            "chain_renewable_optimize). Proof hash f6cdbd0a07f2. Zero-LLM, 0 tokens.\n"
        ))
    return out_zip, report


def verify_zip(zip_path: Path) -> dict:
    size = zip_path.stat().st_size
    ok_size = size > 1024
    compile_ok = True
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        for n in names:
            if n.endswith(".py"):
                import tempfile

                with tempfile.TemporaryDirectory() as td:
                    extracted = Path(td) / Path(n).name
                    extracted.write_bytes(zf.read(n), )
                    try:
                        py_compile.compile(str(extracted), doraise=True)
                    except Exception:
                        compile_ok = False
    return {"zip": zip_path.name, "bytes": size, "gt_1kb": ok_size, "py_compile": compile_ok, "files": len(names)}


if __name__ == "__main__":
    results = []
    for z in build_mcp_zips():
        results.append(verify_zip(z))
    report_zip, report = build_eco_report_zip()
    results.append(verify_zip(report_zip))

    print("=" * 70)
    print("EARTH ADDITION DIST BUNDLES — REAL BUILD")
    print("=" * 70)
    all_ok = True
    for r in results:
        status = "PASS" if (r["gt_1kb"] and r["py_compile"]) else "FAIL"
        if status == "FAIL":
            all_ok = False
        print(f"  [{status}] {r['zip']}: {r['bytes']} bytes (>1KB: {r['gt_1kb']}) files={r['files']} py_compile={r['py_compile']}")
    wf = report["workflows"]
    for k, v in wf.items():
        print(f"  workflow {k}: {v.get('status')} | notion {str(v.get('notion_url'))[:58]} | slack_posted {v.get('slack_posted')} | {v.get('time_human')}")
    print("=" * 70)
    print("ALL PASS" if all_ok else "SOME FAILED")
    raise SystemExit(0 if all_ok else 1)
