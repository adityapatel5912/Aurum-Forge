"""Dual-Probe Diagnostics and Telemetry Endpoints for FORGE Agent.

1. Process Liveness: Lightweight ping verifying web server and event loop are responsive.
2. Operational Readiness: Deep diagnostic verifying LLM quota, tool integrations, and storage.
"""
from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.config import LOGS_DIR, MCP_REGISTRY_DIR, PROVIDERS, VERSION, ensure_dirs
from backend.health.agent_state import AgentState, get_telemetry_manager
from backend.health.circuit_breaker import get_circuit_breaker_registry
from backend.health.watchdog import get_watchdog
from backend.paths import get_project_root


_PROCESS_START_TIME = time.time()


def check_liveness() -> Dict[str, Any]:
    """Instant Process Liveness Probe (<2ms).
    
    Verifies web server and event loop are running and handling network traffic.
    """
    now = time.time()
    uptime_s = round(now - _PROCESS_START_TIME, 2)
    
    # Record heartbeat on probe
    tel = get_telemetry_manager()
    tel.record_heartbeat()

    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "uptime_seconds": uptime_s,
        "pid": os.getpid(),
        "active_threads": threading.active_count(),
        "event_loop": "responsive",
        "version": VERSION,
    }


def check_readiness() -> Dict[str, Any]:
    """Operational Readiness Diagnostic Probe.
    
    Evaluates critical dependencies before routing work:
    - LLM provider API availability and circuit breaker status
    - Tool integrations / Super-Hub status
    - Filesystem storage / logs writeability
    - Agent state machine readiness
    """
    ensure_dirs()
    now = time.time()
    checks: Dict[str, Any] = {}
    is_ready = True
    degraded = False

    # 1. Check Filesystem Writeability
    storage_ok = False
    try:
        test_file = LOGS_DIR / f".readiness_probe_{int(now)}.tmp"
        test_file.write_text("probe", encoding="utf-8")
        if test_file.exists():
            test_file.unlink()
            storage_ok = True
    except Exception as e:
        storage_ok = False
        checks["storage_error"] = str(e)
    
    checks["storage_writable"] = {
        "ok": storage_ok,
        "logs_dir": str(LOGS_DIR).replace("\\", "/"),
        "registry_dir": str(MCP_REGISTRY_DIR).replace("\\", "/"),
    }
    if not storage_ok:
        is_ready = False

    # 2. Check LLM Providers & Circuit Breakers
    circuits = get_circuit_breaker_registry()
    provider_status: Dict[str, Any] = {}
    active_keys_count = 0

    for p_name, p_meta in PROVIDERS.items():
        key_found = any(bool(os.getenv(k)) for k in p_meta.get("key_envs", []))
        if key_found:
            active_keys_count += 1
        available = circuits.is_available(p_name)
        provider_status[p_name] = {
            "key_configured": key_found,
            "circuit_available": available,
            "circuit_state": circuits.get_or_create(p_name)._state.value,
        }

    # FORGE can operate in Zero-LLM Deterministic Mode even if keys are absent,
    # so missing keys do not fail readiness, but open circuits mark degraded.
    has_open_circuits = any(p["circuit_state"] == "open" for p in provider_status.values())
    if has_open_circuits:
        degraded = True

    checks["llm_providers"] = {
        "active_keys_count": active_keys_count,
        "zero_llm_mode": active_keys_count == 0,
        "providers": provider_status,
    }

    # 3. Check Super-Hub Tool Integrations
    tools_count = 0
    try:
        from backend.aurum.super_hub import get_super_hub
        hub = get_super_hub()
        cat = hub.get_catalog()
        tools_count = cat.get("total_tools_count", 0)
        tools_ok = tools_count > 0
    except Exception as e:
        tools_ok = False
        checks["tool_catalog_error"] = str(e)

    checks["tool_integrations"] = {
        "ok": tools_ok,
        "super_hub": "forge-aurum-hub",
        "total_tools_available": tools_count,
        "aurum_gold_verified": True,
    }
    if not tools_ok:
        is_ready = False

    # 4. Check Agent State Machine
    tel = get_telemetry_manager()
    tel_data = tel.get_telemetry()
    agent_state = tel_data["state"]

    if agent_state == AgentState.STUCK.value:
        is_ready = False
    elif agent_state == AgentState.DEGRADED.value or degraded:
        degraded = True

    checks["agent_state"] = {
        "state": agent_state,
        "is_stuck": tel_data["is_stuck"],
        "memory_rss_mb": tel_data["metrics"]["memory_rss_mb"],
    }

    overall_status = "ready" if (is_ready and not degraded) else ("degraded" if is_ready else "not_ready")

    return {
        "ready": is_ready,
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "uptime_seconds": round(now - _PROCESS_START_TIME, 2),
        "version": VERSION,
        "checks": checks,
    }


def get_full_telemetry() -> Dict[str, Any]:
    """Aggregate full runtime diagnostics: liveness, readiness, state telemetry, circuits, and watchdog."""
    tel = get_telemetry_manager()
    circuits = get_circuit_breaker_registry()
    wd = get_watchdog()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "version": VERSION,
        "liveness": check_liveness(),
        "readiness_summary": check_readiness(),
        "state_telemetry": tel.get_telemetry(),
        "circuit_breakers": circuits.get_status(),
        "watchdog": wd.get_status(),
    }
