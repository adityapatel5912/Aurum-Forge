"""FORGE entrypoint — CLI + REST API for the UI.

CLI (one-shot forge):
  python backend/main.py --urls https://news.ycombinator.com,https://example.com --official notion --goal "test"

API (serves the React UI):
  python backend/main.py --serve --port 8740
"""
from __future__ import annotations

import argparse
import sys
import threading
import traceback
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import SERVER_NAME, VERSION, ensure_dirs  # noqa: E402

from pydantic import BaseModel, Field  # noqa: E402


class ForgeRequest(BaseModel):
    """Module-level so FastAPI can resolve it under `from __future__ import annotations`."""

    goal: str = ""
    urls: list[str] = Field(default_factory=list)
    officials: list[str] = Field(default_factory=list)
    headful: "bool | None" = None
    skip_scout: bool = False


# ---------------------------------------------------------------------- CLI
def run_cli(args: argparse.Namespace) -> int:
    from backend.pipeline import ForgePipeline

    pipe = ForgePipeline()
    printed: set[str] = set()

    def cb(steps: list[dict]) -> None:
        for s in steps:
            tag = f"{s['key']}:{s['state']}"
            if tag in printed:
                continue
            printed.add(tag)
            icon = {"active": ">>", "done": "OK", "error": "!!"}.get(s["state"], "..")
            print(f"  [{icon}] {s['label']}")

    pipe.on_progress(cb)
    urls = [u for u in (args.urls or "").split(",") if u.strip()]
    officials = [o for o in (args.official or "").split(",") if o.strip()]

    print(f"FORGE v{VERSION} — forging {len(urls)} site(s) + {len(officials)} official(s)")
    print(f"Goal: {args.goal or '(none)'}\n")
    result = pipe.run(args.goal or "", urls, officials, headful=(False if args.headless else None), skip_scout=args.skip_scout)

    print()
    stats = result["stats"]
    print(f"Unified MCP Ready — 1 server operates {stats['custom']} custom + {stats['official']} official ({stats['tools_total']} tools, {stats['elapsed_s']}s)")
    print(f"  server.py : {result['server_path']}")
    print(f"  zip       : {result['zip_path']}")
    print(f"  say line  : {result['say_line']}")

    if args.execute and result["dag"]:
        from backend.executor import execute_dag

        print("\nExecuting planned DAG against the forged server...")
        report = execute_dag(result["dag"], result["server_path"])
        print(f"  DAG ok={report['ok']} log={report['log_path']}")
    return 0


# ---------------------------------------------------------------------- API
def create_app():
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse

    from backend.pipeline import ForgePipeline
    from backend.registry import Registry, load_official_catalog

    app = FastAPI(title="FORGE", version=VERSION, description="Self-Forging Browser Workforce")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    jobs: dict[str, dict] = {}
    jobs_lock = threading.Lock()

    def snapshot(job_id: str) -> dict:
        with jobs_lock:
            job = jobs.get(job_id)
            if not job:
                raise HTTPException(404, "job not found")
            snap = {k: v for k, v in job.items() if k != "thread"}
            snap["download_url"] = f"/api/jobs/{job_id}/download"
            return snap

    @app.get("/api/health")
    def health():
        return {"ok": True, "name": "FORGE", "version": VERSION, "server": SERVER_NAME}

    @app.get("/api/officials")
    def officials_catalog():
        return load_official_catalog()

    @app.get("/api/registry")
    def registry_list():
        return Registry().list_servers()

    @app.post("/api/forge")
    def forge(req: ForgeRequest):
        job_id = uuid.uuid4().hex[:12]
        with jobs_lock:
            jobs[job_id] = {
                "id": job_id,
                "status": "running",
                "steps": [],
                "result": None,
                "error": None,
            }

        def cb(steps: list[dict]) -> None:
            with jobs_lock:
                jobs[job_id]["steps"] = steps

        def worker() -> None:
            try:
                pipe = ForgePipeline()
                pipe.on_progress(cb)
                result = pipe.run(
                    req.goal, req.urls, req.officials, headful=req.headful, skip_scout=req.skip_scout
                )
                with jobs_lock:
                    jobs[job_id]["result"] = result
                    jobs[job_id]["status"] = "done"
            except Exception as err:
                traceback.print_exc()
                with jobs_lock:
                    jobs[job_id]["status"] = "error"
                    jobs[job_id]["error"] = f"{type(err).__name__}: {err}"

        threading.Thread(target=worker, daemon=True).start()
        return {"job_id": job_id, "poll": f"/api/jobs/{job_id}"}

    @app.get("/api/jobs/{job_id}")
    def job_state(job_id: str):
        return snapshot(job_id)

    @app.get("/api/jobs/{job_id}/download")
    def job_download(job_id: str):
        snap = snapshot(job_id)
        if snap["status"] != "done" or not snap.get("result"):
            raise HTTPException(409, "job not finished")
        return FileResponse(
            snap["result"]["zip_path"],
            media_type="application/zip",
            filename="unified-mcp.zip",
        )

    # ----------------------------------------------------------- History APIs
    from forge.history import get_all_history, get_history_by_id, search_history
    from forge.exporter import generate_all_export_configs, generate_export_for_platform

    @app.get("/api/history")
    def list_history(q: str = ""):
        if q:
            return search_history(q)
        return get_all_history()

    @app.get("/api/history/{entry_id}")
    def get_history_item(entry_id: str):
        item = get_history_by_id(entry_id)
        if not item:
            raise HTTPException(404, f"History entry '{entry_id}' not found")
        return item

    @app.get("/api/history/{entry_id}/download")
    def download_history_zip(entry_id: str):
        item = get_history_by_id(entry_id)
        if not item:
            raise HTTPException(404, f"History entry '{entry_id}' not found")
        zip_file = Path(item.get("zip_path", ""))
        if not zip_file.exists():
            # Try history dir
            zip_file = ROOT / "mcp_registry" / "history" / entry_id / f"unified-mcp-{entry_id}.zip"
        if not zip_file.exists():
            # Fallback to dist/unified-mcp.zip
            zip_file = ROOT / "dist" / "unified-mcp.zip"
        if not zip_file.exists():
            raise HTTPException(404, "Zip file for this history entry not found on disk")
        return FileResponse(
            str(zip_file),
            media_type="application/zip",
            filename=f"unified-mcp-{entry_id}.zip",
        )

    @app.get("/api/history/{entry_id}/skill")
    def get_history_skill_text(entry_id: str):
        item = get_history_by_id(entry_id)
        if not item:
            raise HTTPException(404, f"History entry '{entry_id}' not found")
        return {"id": entry_id, "skill": item.get("skill_content", "")}

    @app.get("/api/history/{entry_id}/export/{platform}")
    @app.post("/api/history/{entry_id}/export/{platform}")
    def export_history_platform(entry_id: str, platform: str):
        item = get_history_by_id(entry_id)
        if not item:
            raise HTTPException(404, f"History entry '{entry_id}' not found")
        from forge.exporter import VALID_PLATFORMS, normalize_platform_key
        norm = normalize_platform_key(platform)
        if norm not in VALID_PLATFORMS:
            raise HTTPException(400, f"Invalid platform '{platform}'. Must be one of {list(VALID_PLATFORMS)}")
        mcp_name = item.get("mcp_name") or SERVER_NAME
        server_path = item.get("abs_path") or str(ROOT / "mcp_registry" / "servers" / "unified-mcp" / "server.py")
        return generate_export_for_platform(norm, mcp_name, server_path)

    # ------------------------------------------------ Forge Registry Meta MCP
    @app.get("/api/forge-registry-mcp/config")
    def forge_registry_mcp_config():
        meta_mcp_path = (ROOT / "forge" / "mcp" / "forge_registry_mcp" / "server.py").resolve()
        clean_path = str(meta_mcp_path).replace("\\", "/")
        configs = generate_all_export_configs("forge-registry", clean_path)
        return {
            "name": "forge-registry",
            "server_path": clean_path,
            "description": "Meta MCP server exposing all forged MCPs and SKILL.md files to any AI Agent",
            "tools": [
                {"name": "list_forged_mcps", "description": "List all MCP servers generated in Forge"},
                {"name": "get_mcp_details", "description": "Get details of a specific forged MCP by id"},
                {"name": "get_skill", "description": "Get the single SKILL.md for that workflow"},
                {"name": "search_mcps", "description": "Search forged MCPs by goal text or tool name"},
                {"name": "export_mcp_to_platform", "description": "Export MCP Server to 6 platforms"},
            ],
            "platforms": configs,
            "install_command": f"claude mcp add forge-registry -- python {clean_path}",
        }

    # serve the built frontend when present (single-command production mode)
    frontend_dist = ROOT / "frontend" / "dist"
    if frontend_dist.exists():
        from fastapi.staticfiles import StaticFiles

        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app


app = create_app()


# ---------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description="FORGE — Self-Forging Browser Workforce")
    parser.add_argument("--urls", default="", help="comma-separated custom site URLs to forge")
    parser.add_argument("--official", default="", help="comma-separated official MCP ids (notion,gsheet,github,slack)")
    parser.add_argument("--goal", default="", help="why do you need MCPs? plain English workflow goal")
    parser.add_argument("--serve", action="store_true", help="start the REST API for the UI")
    parser.add_argument("--port", type=int, default=8740)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--headless", action="store_true", help="scout with a headless browser")
    parser.add_argument("--skip-scout", action="store_true", help="reuse existing logs/*.json instead of scouting")
    parser.add_argument("--execute", action="store_true", help="run the planned DAG after forging")
    args = parser.parse_args()

    ensure_dirs()

    if args.serve or (not args.urls and not args.official):
        import uvicorn

        print(f"FORGE API -> http://{args.host}:{args.port}  (UI dev server proxies /api here)")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0

    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
