"""FORGE INFINITY Live Telemetry Tracker.

Records real invocation counts, latency, memory, and self-heal events across
the Factory OS. Counters persist to logs/telemetry.json (atomic writes) so the
dashboard survives restarts.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import LOGS_DIR

TELEMETRY_JSON = LOGS_DIR / "telemetry.json"
_lock = threading.RLock()  # reentrant: _persist() calls snapshot() while holding the lock
_max_samples = 50

_state: Dict[str, Any] = {
    "invocations": {},          # tool name -> count
    "errors": {},               # tool name -> count
    "latency_ms": {},           # tool name -> [samples]
    "self_heal_events": [],     # [{ts, path, elapsed_ms, patches}]
    "forge_events": [],         # [{ts, mcp_id, elapsed_s, tools}]
    "started_at": None,
}


def _ensure_loaded() -> None:
    if _state["started_at"] is not None:
        return
    _state["started_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        if TELEMETRY_JSON.exists():
            data = json.loads(TELEMETRY_JSON.read_text("utf-8"))
            for key in ("invocations", "errors", "latency_ms"):
                if isinstance(data.get(key), dict):
                    _state[key] = data[key]
            for key in ("self_heal_events", "forge_events"):
                if isinstance(data.get(key), list):
                    _state[key] = data[key][-_max_samples:]
            if data.get("started_at"):
                _state["started_at"] = data["started_at"]
    except Exception:
        pass


def _persist() -> None:
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = TELEMETRY_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(snapshot(), indent=2, ensure_ascii=False), "utf-8")
        os.replace(tmp, TELEMETRY_JSON)
    except Exception:
        pass


def _memory_mb() -> float:
    try:
        import psutil

        return round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 1)
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            k32 = ctypes.WinDLL("kernel32")
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            fn = getattr(k32, "K32GetProcessMemoryInfo", None)
            if fn is None:
                fn = ctypes.WinDLL("psapi").GetProcessMemoryInfo
            fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
            fn.restype = wintypes.BOOL

            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            if fn(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
                return round(pmc.WorkingSetSize / (1024 * 1024), 1)
            return 0.0
        except Exception:
            return 0.0
    try:
        import resource

        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except Exception:
        return 0.0


def record_invocation(tool: str, latency_ms: float, ok: bool = True) -> None:
    """Record one factory tool invocation with latency."""
    with _lock:
        _ensure_loaded()
        _state["invocations"][tool] = _state["invocations"].get(tool, 0) + 1
        if not ok:
            _state["errors"][tool] = _state["errors"].get(tool, 0) + 1
        samples = _state["latency_ms"].setdefault(tool, [])
        samples.append(round(float(latency_ms), 1))
        if len(samples) > _max_samples:
            del samples[:-_max_samples]
        _persist()


def record_self_heal(server_path: str, elapsed_ms: float, patches: int, ok: bool) -> None:
    """Record one self-heal event with its patch count and latency."""
    with _lock:
        _ensure_loaded()
        _state["self_heal_events"].append(
            {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "server_path": str(server_path).replace("\\", "/"),
                "elapsed_ms": round(float(elapsed_ms), 1),
                "patches_applied": int(patches),
                "ok": bool(ok),
            }
        )
        _state["self_heal_events"] = _state["self_heal_events"][-_max_samples:]
        _persist()


def record_forge(mcp_id: str, elapsed_s: float, tools: int, ok: bool) -> None:
    """Record one forge event."""
    with _lock:
        _ensure_loaded()
        _state["forge_events"].append(
            {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "mcp_id": mcp_id,
                "elapsed_s": round(float(elapsed_s), 2),
                "tools": int(tools),
                "ok": bool(ok),
            }
        )
        _state["forge_events"] = _state["forge_events"][-_max_samples:]
        _persist()


def snapshot() -> Dict[str, Any]:
    """Return the live telemetry snapshot for the dashboard."""
    with _lock:
        _ensure_loaded()
        invocations = dict(_state["invocations"])
        errors = dict(_state["errors"])
        latency = {k: list(v) for k, v in _state["latency_ms"].items()}

    avg_latency = {}
    p95_latency = {}
    for tool, samples in latency.items():
        if samples:
            avg_latency[tool] = round(sum(samples) / len(samples), 1)
            ordered = sorted(samples)
            p95_latency[tool] = round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 1)

    heal_events = list(_state["self_heal_events"])
    forge_events = list(_state["forge_events"])

    return {
        "ok": True,
        "started_at": _state["started_at"],
        "now": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "memory_mb": _memory_mb(),
        "total_invocations": sum(invocations.values()),
        "invocations": invocations,
        "errors": errors,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "self_heal": {
            "count": len(heal_events),
            "avg_ms": round(sum(e["elapsed_ms"] for e in heal_events) / len(heal_events), 1) if heal_events else 0,
            "last": heal_events[-1] if heal_events else None,
            "events": heal_events[-10:],
        },
        "forges": {
            "count": len(forge_events),
            "avg_s": round(sum(e["elapsed_s"] for e in forge_events) / len(forge_events), 2) if forge_events else 0,
            "last": forge_events[-1] if forge_events else None,
            "events": forge_events[-10:],
        },
    }
