"""DAG planner — one LLM call (planner chain), validated, heuristic fallback."""
from __future__ import annotations

from typing import Optional

from backend.llm import LLMChain, extract_json

_SYSTEM = (
    "You are FORGE's planner. You compose typed MCP tools into a dependency "
    "DAG that achieves the user's goal. Reply with ONLY a JSON object — no "
    "markdown fences, no prose."
)


def _planner_user(goal: str, manifest: list[dict]) -> str:
    lines = [
        f'- {t["name"]}  [{t["badge"]}, source: {t["source"]}]  {t.get("description", "")[:90]}'
        for t in manifest
    ]
    return f"""GOAL: {goal}

AVAILABLE TOOLS:
{chr(10).join(lines)}

Return a JSON object mapping task ids to tasks, e.g.
{{"t1": {{"tool": "<tool name>", "source": "<its source>", "parallel": true}},
  "t2": {{"tool": "<tool name>", "source": "<its source>", "parallel": true}},
  "t3": {{"tool": "<tool name>", "source": "<its source>", "deps": ["t1", "t2"]}}}}

RULES:
- Use ONLY tool names from AVAILABLE TOOLS (exact strings).
- At most 6 tasks. Independent site searches/browsing run in parallel (parallel=true, no deps).
- Official logging/recording tools depend on the data-gathering tasks that feed them (deps lists those ids).
- If the goal mentions email/mail/notify AND log/notion: ALWAYS create exactly 3 tasks —
  t1 = the data-gathering core tool (e.g. amazon_monitor_ram_discount, parallel=false),
  t2 = gmail_notify_and_log with deps ["t1"],
  t3 = notion_log_price with deps ["t1"] —
  t2 and t3 both get "parallel": true (they run side by side after t1).
- A task with deps may still be parallel=true if it can run beside its siblings.
- "params" optional: {{"tool": "...", "params": {{"query": "example"}}}}"""


# core domains enter the DAG only when the goal actually mentions them
_CORE_GOAL_HINTS = {"Core Amazon": ("amazon", "ram")}
_LOG_TOOLS = {"notion_log_price", "notion_create_entry", "sheets_append_row", "github_create_issue", "slack_post_message"}


def _heuristic_dag(manifest: list[dict], goal: str = "") -> dict:
    """No-LLM plan. Core RAM workflow first, then: parallel custom searches -> notify/log."""
    names = {t["name"]: t for t in manifest}
    g = (goal or "").lower()

    # RAM + mail + Notion goal -> t1 monitor, then t2 gmail ∥ t3 notion (both depend on t1)
    core3 = {"amazon_monitor_ram_discount", "gmail_notify_and_log", "notion_log_price"}
    if (
        core3 <= names.keys()
        and any(k in g for k in ("ram", "amazon"))
        and any(k in g for k in ("mail", "email", "notify"))
        and any(k in g for k in ("log", "notion"))
    ):
        return {
            "t1": {"tool": "amazon_monitor_ram_discount", "source": names["amazon_monitor_ram_discount"]["source"]},
            "t2": {"tool": "gmail_notify_and_log", "source": names["gmail_notify_and_log"]["source"], "deps": ["t1"], "parallel": True},
            "t3": {"tool": "notion_log_price", "source": names["notion_log_price"]["source"], "deps": ["t1"], "parallel": True},
        }

    dag: dict = {}
    level1: list[str] = []
    seen_sources: set[str] = set()
    for t in manifest:
        if t["badge"] not in ("FORGED", "CORE") or t["source"] in seen_sources:
            continue
        if t["badge"] == "CORE":
            hints = _CORE_GOAL_HINTS.get(t["source"], ())
            if not hints or not any(h in g for h in hints):
                continue  # core domain not mentioned in this goal
        if not t["name"].startswith(("search_", "monitor_", "read_")) and level1:
            continue
        seen_sources.add(t["source"])
        tid = f"t{len(dag) + 1}"
        dag[tid] = {"tool": t["name"], "source": t["source"], "parallel": True}
        level1.append(tid)

    wants_mail = any(k in g for k in ("mail", "email", "notify"))
    for t in manifest:
        is_notify = t["name"] == "gmail_notify_and_log" and wants_mail
        is_log = t["name"] in _LOG_TOOLS
        if not (is_notify or is_log):
            continue
        tid = f"t{len(dag) + 1}"
        task = {"tool": t["name"], "source": t["source"]}
        if level1:
            task["deps"] = list(level1)
            task["parallel"] = True
        dag[tid] = task
    return dag


def _normalize(raw, manifest: list[dict]) -> Optional[dict]:
    valid = {t["name"]: t for t in manifest}
    if isinstance(raw, dict) and isinstance(raw.get("tasks"), list):
        raw = {f"t{i + 1}": t for i, t in enumerate(raw["tasks"]) if isinstance(t, dict)}
    if not isinstance(raw, dict) or not raw:
        return None

    # accept both {"t1": {...}} and {"t1": {"id": "t1", ...}}
    dag: dict = {}
    order: list[str] = []
    for i, (tid, task) in enumerate(raw.items()):
        if not isinstance(task, dict) or task.get("tool") not in valid:
            continue
        tid = str(task.get("id") or tid or f"t{i + 1}")
        deps = [d for d in (task.get("deps") or []) if str(d) in dag][:4]
        entry = {"tool": task["tool"], "source": valid[task["tool"]]["source"]}
        if task.get("params") and isinstance(task["params"], dict):
            entry["params"] = dict(list(task["params"].items())[:6])
        # no deps -> parallel by default; with deps -> parallel only if the model/heuristic says so
        entry["parallel"] = bool(task.get("parallel", not deps))
        if deps:
            entry["deps"] = deps
        dag[tid] = entry
        order.append(tid)
        if len(dag) >= 6:
            break
    # ensure at least one executable task exists
    if not dag:
        return None
    return dag


def build_dag(goal: str, manifest: list[dict], llm: Optional[LLMChain] = None) -> tuple[dict, dict]:
    """Returns (dag, llm_meta). Never raises; falls back to the heuristic plan."""
    if not manifest:
        return {}, {"provider": None, "model": None, "cached": False, "tried": []}
    if llm is None:
        llm = LLMChain("planner")

    text, meta = llm.chat(_SYSTEM, _planner_user(goal, manifest), temperature=0.1, max_tokens=1200)
    dag = _normalize(extract_json(text or ""), manifest)
    if dag:
        return dag, meta
    return _heuristic_dag(manifest, goal), meta
