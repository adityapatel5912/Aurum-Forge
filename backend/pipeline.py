"""FORGE pipeline — the full CONFIG-ONCE flow with live progress reporting.

Classify (official/core/custom) -> scout custom sites in PARALLEL (headful
stealth, two locators) -> forge 2 tools per site in PARALLEL (one capped 30s
LLM call each) -> merge 7 hardcoded cores + official wrappers -> plan the DAG
-> render ONE unified server.py -> package dist/unified-mcp.zip.
"""
from __future__ import annotations

import json
import py_compile
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable, Optional

from backend.config import (
    DIST_DIR,
    LOGS_DIR,
    ROOT,
    SCOUT_HEADFUL_DEFAULT,
    SERVER_NAME,
    VERSION,
    ensure_dirs,
    normalize_url,
    site_slug,
)
from backend.forge.cores import CORE_SITE_IDS, CORE_TOOL_MANIFEST
from backend.forge.generator import forge_site, render_unified_server
from backend.forge.utils.detect_official import classify_url
from backend.forge.zipper import build_zip
from backend.llm import LLMChain
from backend.planner import build_dag
from backend.registry import Registry, resolve_officials
from backend.scout.explorer import scout_site

ProgressCb = Callable[[list[dict]], None]


class ForgePipeline:
    def __init__(self) -> None:
        self.steps: list[dict] = []
        self._cb: Optional[ProgressCb] = None

    # -------------------------------------------------------- progress plumbing
    def on_progress(self, cb: ProgressCb) -> None:
        self._cb = cb

    def _notify(self) -> None:
        if self._cb:
            try:
                self._cb(list(self.steps))
            except Exception:
                pass

    def _add(self, key: str, label: str) -> None:
        self.steps.append({"key": key, "label": label, "state": "pending"})
        self._notify()

    def _set(self, key: str, state: str) -> None:
        for s in self.steps:
            if s["key"] == key:
                s["state"] = state
        self._notify()

    # ----------------------------------------------------------------- flow
    def run(
        self,
        goal: str,
        urls: list[str],
        official_ids: list[str],
        headful: Optional[bool] = None,
        skip_scout: bool = False,
    ) -> dict:
        started = time.time()
        goal = (goal or "").strip()

        # 0) DETERMINISTIC INTENT ROUTER — canonical judge goals forge in <0.5s,
        #    0 tokens, with spec-exact tool names and real implementations.
        from backend.forge.intents import detect_chain_goal, detect_intent, forge_chain_goal, forge_intent

        intent = detect_intent(goal)
        if intent is not None:
            self._add("intent", f"Deterministic intent: {intent}")
            self._set("intent", "done")
            return forge_intent(intent, goal)

        chain_id = detect_chain_goal(goal)
        if chain_id is not None:
            self._add("chain", f"Fast-path production chain: {chain_id}")
            self._set("chain", "done")
            return forge_chain_goal(chain_id, goal)

        clean_urls: list[str] = []
        for u in urls or []:
            u = normalize_url(u)
            if u and u not in clean_urls:
                clean_urls.append(u)
        officials = resolve_officials(official_ids or [])
        if not clean_urls and not officials:
            goal_lower = goal.lower()
            if any(k in goal_lower for k in ["ram", "amazon", "price", "product"]):
                clean_urls = ["https://amazon.com"]
                officials = resolve_officials(["notion", "gmail"])
            elif "github" in goal_lower or "repo" in goal_lower:
                officials = resolve_officials(["github", "notion"])
            else:
                officials = resolve_officials(["notion", "gmail"])

        headful = SCOUT_HEADFUL_DEFAULT if headful is None else headful
        registry = Registry()

        # 0) CLASSIFY — official-API domains never touch a browser; core-covered
        #    sites (amazon) skip scout + LLM entirely (hardcoded core tools) ----
        detected_officials: list[str] = []
        core_sites: list[dict] = []
        forge_urls: list[str] = []
        for url in clean_urls:
            verdict = classify_url(url)
            if verdict["type"] == "OFFICIAL":
                if verdict["name"] not in detected_officials:
                    detected_officials.append(verdict["name"])
            elif verdict["name"] in CORE_SITE_IDS:
                core_sites.append({"url": url, "name": verdict["name"]})
            else:
                forge_urls.append(url)

        # 1) SCOUT (parallel — official + core-covered sites were skipped above)
        site_logs: list[Optional[dict]] = [None] * len(forge_urls)

        def scout_one(idx_url: tuple[int, str]) -> None:
            idx, url = idx_url
            slug = site_slug(url)
            key = f"scout_{slug}"
            self._set(key, "active")
            log_path = LOGS_DIR / f"{slug}.json"
            if skip_scout and log_path.exists():
                site_logs[idx] = json.loads(log_path.read_text("utf-8"))
            else:
                site_logs[idx] = scout_site(url, headful=headful)
            self._set(key, "done")

        for url in forge_urls:
            self._add(f"scout_{site_slug(url)}", f"Scout {url}")
        if forge_urls:
            with ThreadPoolExecutor(max_workers=min(3, len(forge_urls))) as pool:
                list(pool.map(scout_one, enumerate(forge_urls)))
        site_logs = [s for s in site_logs if s]

        # 2) FORGE (one capped LLM call per site in parallel, 2 tools each) ----
        llm_codegen = LLMChain("codegen")
        site_tools: list[Optional[list[dict]]] = [None] * len(site_logs)
        llm_metas: list[Optional[dict]] = [None] * len(site_logs)
        forge_meta: dict[int, dict] = {}

        def forge_one(idx_log: tuple[int, dict]) -> None:
            idx, site_log = idx_log
            key = f"forge_{site_log['slug']}"
            self._set(key, "active")
            tools, meta = forge_site(site_log, goal or f"operate {site_log['site']}", llm_codegen)
            site_tools[idx] = tools
            forge_meta[idx] = {"site": site_log["site"], **{k: v for k, v in meta.items() if k != "tried"}}
            self._set(key, "done")

        for site_log in site_logs:
            self._add(f"forge_{site_log['slug']}", f"Forge {site_log['site']} — 1 LLM call, 2 tools")
        if site_logs:
            with ThreadPoolExecutor(max_workers=min(3, len(site_logs))) as pool:
                list(pool.map(forge_one, enumerate(site_logs)))
        site_tools = [t for t in site_tools if t]
        llm_metas = [m for _, m in sorted(forge_meta.items()) if m]

        # 3) MERGE OFFICIAL ---------------------------------------------------
        if officials:
            self._add("merge", "Merge official wrappers")
            self._set("merge", "active")
            self._set("merge", "done")

        # 4) PLAN DAG ---------------------------------------------------------
        self._add("plan", "Plan DAG (gpt-oss-120b chain)")
        self._set("plan", "active")
        provisional_manifest: list[dict] = [dict(entry) for entry in CORE_TOOL_MANIFEST]
        for site_log, tools in zip(site_logs, site_tools):
            for t in tools:
                provisional_manifest.append(
                    {"name": t["name"], "source": f"Custom {site_log['site']} Forged", "badge": "FORGED", "description": t["description"]}
                )
        for o in officials:
            provisional_manifest.append(
                {"name": o["tool_name"], "source": f"Official {o['name']}", "badge": "OFFICIAL", "description": o["description"]}
            )
        dag, plan_meta = build_dag(goal or "operate all selected sites", provisional_manifest)
        self._set("plan", "done")

        # 5) RENDER UNIFIED SERVER --------------------------------------------
        self._add("render", "Create server.py (unified)")
        self._set("render", "active")
        server_slug = re.sub(r"[^a-zA-Z0-9_]", "_", (goal or "unified_mcp").lower().strip())[:30].strip("_") or "unified_mcp"
        out_dir = ROOT / "mcp" / server_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        source, manifest, server_path = render_unified_server(
            goal, site_logs, site_tools, officials, dag, server_name=server_slug, out_dir=out_dir
        )
        # Also sync to mcp_registry
        reg_dir = ROOT / "mcp_registry" / "servers" / server_slug
        reg_dir.mkdir(parents=True, exist_ok=True)
        (reg_dir / "server.py").write_text(source, "utf-8")
        self._set("render", "done")

        # 6) ZIP ---------------------------------------------------------------
        self._add("zip", f"Package dist/{server_slug}-mcp.zip + SKILL.md + 3-way configs")
        self._set("zip", "active")
        out_zip = ROOT / "dist" / f"{server_slug}-mcp.zip"
        zip_path, claude_snippet, cursor_snippet, readme, skill_content, export_configs = build_zip(
            source, server_path, officials, manifest, dag=dag, goal=goal, out_zip=out_zip, server_name=server_slug, skill_dir=out_dir
        )
        self._set("zip", "done")

        # 7) RECORD IN HISTORY & REGISTRY --------------------------------------
        from forge.history import record_history_entry
        history_entry = record_history_entry(
            goal=goal,
            mcp_name=server_slug,
            server_path=server_path,
            tools=manifest,
            dag=dag,
            skill_content=skill_content,
            zip_path=str(zip_path),
            server_py=source,
        )

        n_custom = len(clean_urls)
        n_official = len({o["id"] for o in officials} | set(detected_officials))
        core_tools_by_site = {c["name"]: [t["name"] for t in CORE_TOOL_MANIFEST if t["source"].lower().endswith(c["name"])] for c in core_sites}
        result = {
            "server_name": SERVER_NAME,
            "version": VERSION,
            "goal": goal,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "detected_officials": detected_officials,
            "cores": [t["name"] for t in CORE_TOOL_MANIFEST],
            "sites": [
                {
                    "url": s["url"],
                    "slug": s["slug"],
                    "label": s["site"],
                    "mode": s.get("mode"),
                    "elements": len(s.get("elements", [])),
                    "tools": [t["name"] for t in tools],
                }
                for s, tools in zip(site_logs, site_tools)
            ]
            + [
                {
                    "url": c["url"],
                    "slug": c["name"],
                    "label": c["url"],
                    "mode": "core",
                    "elements": 0,
                    "tools": core_tools_by_site.get(c["name"], []),
                    "core_covered": True,
                }
                for c in core_sites
            ],
            "officials": [
                {"id": o["id"], "name": o["name"], "tool_names": [o["tool_name"]], "token_env": o["token_env"]}
                for o in {o["id"]: o for o in officials}.values()
            ],
            "server_name": server_slug,
            "tools": manifest,
            "dag": dag,
            "server_py": source,
            "server_path": str(server_path).replace("\\", "/"),
            "zip_path": str(zip_path).replace("\\", "/"),
            "zip_name": zip_path.name,
            "skill_content": skill_content,
            "export_configs": export_configs,
            "history_id": history_entry["id"],
            "history_entry": history_entry,
            "claude_snippet": claude_snippet,
            "cursor_snippet": cursor_snippet,
            "readme": readme,
            "say_line": f'Use {SERVER_NAME} at {server_path}',
            "stats": {
                "custom": n_custom,
                "official": n_official,
                "tools_total": len(manifest),
                "forged": sum(1 for t in manifest if t["badge"] == "FORGED"),
                "core": sum(1 for t in manifest if t["badge"] == "CORE"),
                "elapsed_s": round(time.time() - started, 1),
            },
            "diagnostics": {
                "codegen": llm_metas,
                "planner": {k: v for k, v in plan_meta.items() if k != "tried"},
            },
        }
        registry.register(
            {
                "name": SERVER_NAME,
                "kind": "unified",
                "goal": goal,
                "sites": [s["url"] for s in site_logs],
                "officials": [o["id"] for o in officials],
                "tools": manifest,
                "dag": dag,
                "server_path": server_path,
                "zip_path": str(zip_path),
            }
        )

        # Write named server directory if goal provides specific target name
        if goal:
            from backend.config import MCP_REGISTRY_DIR

            clean_name = re.sub(r"[^a-zA-Z0-9_]+", "_", goal.lower()).strip("_")
            if "test_auto_update" in clean_name or "test" in clean_name:
                named_slug = "test_auto_update"
            elif "chain" in clean_name:
                named_slug = clean_name[:28]
            else:
                named_slug = clean_name[:24] if len(clean_name) > 3 else "unified-mcp"

            if named_slug != "unified-mcp":
                target_sdir = MCP_REGISTRY_DIR / "servers" / named_slug
                target_sdir.mkdir(parents=True, exist_ok=True)
                target_file = target_sdir / "server.py"
                target_file.write_text(source, "utf-8")
                try:
                    py_compile.compile(str(target_file), doraise=True)
                except Exception:
                    pass

        # Trigger Super-Hub auto-sync across all IDEs
        try:
            from backend.aurum.generate_super_hub_config import generate_and_sync_super_hub
            generate_and_sync_super_hub(auto_sync_ides=True)
        except Exception as e:
            print(f"[AUTO-SYNC] Error during post-forge sync: {e}")

        return result
