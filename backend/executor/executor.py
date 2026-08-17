"""Executor — pure-Python DAG loop over the generated unified server.

Loads mcp_registry/servers/unified-mcp/server.py as a module and calls the
tool functions directly (no stdio round-trip), honouring deps and running
parallel:true tasks concurrently in a thread pool. Every call is wrapped in
the Healer (2 retries, 200ms apart).
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from backend.config import LOGS_DIR, ensure_dirs
from backend.healer import Healer


def load_server_module(server_path: str):
    spec = importlib.util.spec_from_file_location("unified_server", server_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import server from {server_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["unified_server"] = mod
    spec.loader.exec_module(mod)
    return mod


def _tool_fn(mod, name: str):
    fn = getattr(mod, name, None)
    if fn is None:
        raise AttributeError(f"tool not found on server module: {name}")
    if not callable(fn):  # fastmcp FunctionTool wrapper
        inner = getattr(fn, "fn", None)
        if callable(inner):
            return inner
    return fn


def _levels(dag: dict) -> list[list[str]]:
    """Kahn topological levels; tasks without deps form level 0."""
    remaining = {tid: set(t.get("deps", [])) for tid, t in dag.items()}
    levels: list[list[str]] = []
    done: set[str] = set()
    while remaining:
        ready = sorted(tid for tid, deps in remaining.items() if deps <= done)
        if not ready:  # cycle guard — run whatever is left in one batch
            ready = sorted(remaining)
        levels.append(ready)
        done.update(ready)
        for tid in ready:
            remaining.pop(tid, None)
    return levels


def _json_safe(value, cap: int = 4000) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)
    return text[:cap]


def execute_dag(dag: dict, server_path: str, healer: Healer | None = None) -> dict:
    """Run the DAG; writes logs/execution_<ts>.json and returns the report."""
    healer = healer or Healer()
    mod = load_server_module(server_path)
    results: dict[str, dict] = {}
    report = {
        "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "server": str(server_path),
        "dag": dag,
        "results": results,
    }

    def run_task(tid: str) -> None:
        task = dag[tid]
        started = time.time()
        try:
            fn = _tool_fn(mod, task["tool"])
            accepted = set(inspect.signature(fn).parameters)
            params = {k: v for k, v in (task.get("params") or {}).items() if k in accepted}
            value = healer.attempt(fn, **params)
            results[tid] = {
                "ok": True,
                "tool": task["tool"],
                "ms": int((time.time() - started) * 1000),
                "result": _json_safe(value),
            }
        except Exception as err:
            results[tid] = {
                "ok": False,
                "tool": task.get("tool"),
                "ms": int((time.time() - started) * 1000),
                "error": repr(err)[:500],
            }

    for level in _levels(dag):
        parallel = [tid for tid in level if dag[tid].get("parallel") and len(level) > 1]
        serial = [tid for tid in level if tid not in parallel]
        if len(parallel) > 1:
            with ThreadPoolExecutor(max_workers=min(4, len(parallel))) as pool:
                list(pool.map(run_task, parallel))
        else:
            serial = level  # run the whole level serially
        for tid in serial:
            run_task(tid)

    report["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report["ok"] = all(r.get("ok") for r in results.values()) if results else False
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(LOGS_DIR) / f"execution_{stamp}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    report["log_path"] = str(out)
    return report
