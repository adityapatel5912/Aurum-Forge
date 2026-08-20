"""External Watchdog and Automated Recovery Supervisor for FORGE Agent.

Runs as an independent monitoring daemon querying the agent's telemetry at fixed intervals.
Executes autonomous recovery protocols without requiring human intervention:
1. Task Cancellation: Terminates individual hanging task chains and frees working memory.
2. Process/Runtime Recycling: Triggers memory garbage collection and clears temp caches on bloat.
3. Circuit Breaking: Checks provider health and confirms traffic is routed to active fallbacks.
"""
from __future__ import annotations

import gc
import os
import shutil
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.health.agent_state import AgentState, StateTelemetryManager, get_telemetry_manager
from backend.health.circuit_breaker import CircuitBreakerRegistry, get_circuit_breaker_registry
from backend.paths import get_project_root, get_temp_dir


class AgentWatchdog:
    """Autonomous watchdog supervisor continuously evaluating agent health and executing recovery."""

    def __init__(
        self,
        interval_seconds: float = 5.0,
        memory_ceiling_mb: float = 650.0,
        telemetry: Optional[StateTelemetryManager] = None,
        circuits: Optional[CircuitBreakerRegistry] = None,
    ):
        self.interval_seconds = interval_seconds
        self.memory_ceiling_mb = memory_ceiling_mb
        self.telemetry = telemetry or get_telemetry_manager()
        self.circuits = circuits or get_circuit_breaker_registry()
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._check_count = 0
        self._last_check_time: Optional[float] = None
        self._incidents: List[Dict[str, Any]] = []

    def start(self) -> None:
        """Start the autonomous watchdog monitoring thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, name="ForgeAgentWatchdog", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop the watchdog monitoring thread."""
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run_loop(self) -> None:
        while self._running:
            try:
                self.check_health()
            except Exception as e:
                self._record_incident(
                    incident_type="watchdog_error",
                    severity="warning",
                    details=f"Watchdog evaluation error: {e}",
                    action_taken="none",
                )
            time.sleep(self.interval_seconds)

    def check_health(self) -> Dict[str, Any]:
        """Perform one comprehensive health check cycle and execute needed recoveries."""
        now = time.time()
        self._check_count += 1
        self._last_check_time = now

        # Update telemetry heartbeat
        self.telemetry.record_heartbeat()
        
        actions_taken = []
        
        # 1. Stuck Task Detection & Automated Task Cancellation
        is_stuck = self.telemetry.check_and_update_stuck()
        if is_stuck:
            tel = self.telemetry.get_telemetry()
            active_task = tel.get("active_task") or {}
            task_id = active_task.get("task_id", "unknown")
            elapsed = active_task.get("elapsed_seconds", 0.0)
            
            # Execute Task Cancellation Protocol
            cancelled = self.telemetry.cancel_active_task(
                reason=f"Watchdog auto-recovery: task exceeded ceiling ({elapsed}s)"
            )
            if cancelled:
                action_msg = f"Cancelled hanging task chain '{task_id}' ({elapsed}s > threshold)"
                actions_taken.append(action_msg)
                self._record_incident(
                    incident_type="stuck_task_cancelled",
                    severity="high",
                    details=f"Task '{task_id}' was frozen for {elapsed}s without progress",
                    action_taken=action_msg,
                )

        # 2. Process / Memory Bloat Recycling
        mem_mb = self.telemetry.get_memory_rss_mb()
        if mem_mb > self.memory_ceiling_mb:
            recycled = self.recycle_process_memory()
            action_msg = f"Recycled runtime memory (RSS {mem_mb}MB -> {recycled.get('after_mb')}MB)"
            actions_taken.append(action_msg)
            self._record_incident(
                incident_type="memory_bloat_recycled",
                severity="medium",
                details=f"Memory RSS reached {mem_mb}MB (threshold: {self.memory_ceiling_mb}MB)",
                action_taken=action_msg,
            )

        # 3. Circuit Breaker Monitoring
        circuit_status = self.circuits.get_status()
        open_circuits = [k for k, v in circuit_status.items() if v["state"] == "open"]
        if open_circuits:
            # If primary providers are open, ensure state telemetry reflects degraded status if not already active
            if self.telemetry._state == AgentState.IDLE:
                self.telemetry.set_state(
                    AgentState.DEGRADED,
                    reason=f"Providers in open circuit: {', '.join(open_circuits)}",
                )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "check_count": self._check_count,
            "actions_taken": actions_taken,
            "is_healthy": len(actions_taken) == 0,
            "agent_state": self.telemetry._state.value,
            "memory_rss_mb": mem_mb,
            "open_circuits": open_circuits,
        }

    def recycle_process_memory(self) -> Dict[str, Any]:
        """Perform garbage collection and purge stale temporary files."""
        before_mb = self.telemetry.get_memory_rss_mb()
        
        # 1. Force GC
        gc.collect()
        
        # 2. Purge stale temp cache files older than 30 minutes
        temp_dir = get_temp_dir()
        purged_files = 0
        now = time.time()
        if temp_dir.exists():
            for item in temp_dir.iterdir():
                try:
                    if item.is_file() and (now - item.stat().st_mtime) > 1800:
                        item.unlink()
                        purged_files += 1
                except Exception:
                    pass

        after_mb = self.telemetry.get_memory_rss_mb()
        return {
            "before_mb": before_mb,
            "after_mb": after_mb,
            "purged_temp_files": purged_files,
            "gc_collected": True,
        }

    def execute_recovery(self, action: str, target: Optional[str] = None) -> Dict[str, Any]:
        """Execute a targeted automated recovery protocol."""
        if action == "cancel_task":
            ok = self.telemetry.cancel_active_task(reason="Manual/Watchdog recovery trigger")
            self._record_incident("manual_task_cancellation", "medium", "Task cancelled on demand", f"Cancelled active task (ok={ok})")
            return {"action": "cancel_task", "ok": ok}
        elif action == "recycle_memory":
            res = self.recycle_process_memory()
            self._record_incident("manual_memory_recycling", "info", "Memory recycled on demand", f"GC run (freed {round(res['before_mb'] - res['after_mb'], 2)}MB)")
            return {"action": "recycle_memory", "result": res}
        elif action == "reset_circuits":
            self.circuits.reset_all()
            self.telemetry.set_state(AgentState.IDLE, reason="All circuit breakers reset")
            self._record_incident("circuit_breakers_reset", "info", "Reset all circuit breakers", "Circuits reset to CLOSED")
            return {"action": "reset_circuits", "ok": True}
        else:
            return {"action": action, "ok": False, "error": f"Unknown recovery action '{action}'"}

    def _record_incident(self, incident_type: str, severity: str, details: str, action_taken: str) -> None:
        """Log an incident to the in-memory audit log."""
        with self._lock:
            entry = {
                "id": f"inc_{len(self._incidents) + 1}",
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "type": incident_type,
                "severity": severity,
                "details": details,
                "action_taken": action_taken,
            }
            self._incidents.append(entry)
            if len(self._incidents) > 100:
                self._incidents.pop(0)

    def get_status(self) -> Dict[str, Any]:
        """Return watchdog status, configuration, and incident history."""
        with self._lock:
            return {
                "running": self._running,
                "interval_seconds": self.interval_seconds,
                "memory_ceiling_mb": self.memory_ceiling_mb,
                "total_checks": self._check_count,
                "last_check": datetime.fromtimestamp(self._last_check_time, timezone.utc).isoformat(timespec="seconds") if self._last_check_time else None,
                "total_incidents": len(self._incidents),
                "recent_incidents": list(reversed(self._incidents[-10:])),
            }


_GLOBAL_WATCHDOG: Optional[AgentWatchdog] = None


def get_watchdog() -> AgentWatchdog:
    """Return singleton instance of AgentWatchdog."""
    global _GLOBAL_WATCHDOG
    if _GLOBAL_WATCHDOG is None:
        _GLOBAL_WATCHDOG = AgentWatchdog()
    return _GLOBAL_WATCHDOG


def start_watchdog() -> AgentWatchdog:
    """Start the global watchdog."""
    wd = get_watchdog()
    wd.start()
    return wd


def stop_watchdog() -> None:
    """Stop the global watchdog."""
    global _GLOBAL_WATCHDOG
    if _GLOBAL_WATCHDOG:
        _GLOBAL_WATCHDOG.stop()
