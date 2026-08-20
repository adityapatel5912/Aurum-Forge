"""Internal Heartbeat & State Telemetry Machine for FORGE Agent.

Maintains fine-grained agent lifecycle states:
- IDLE: Ready and waiting for inputs without consuming compute.
- ACTIVE: Executing a defined step within expected time thresholds.
- STUCK: Running a single tool call, reasoning loop, or API request past a hard execution ceiling.
- DEGRADED: The core loop works, but secondary tools or rate limits are currently blocked.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class AgentState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    STUCK = "stuck"
    DEGRADED = "degraded"


class StateTelemetryManager:
    """Thread-safe manager for Agent state, heartbeat, active execution, and runtime telemetry."""

    def __init__(self, stuck_ceiling_seconds: float = 180.0):
        self._lock = threading.Lock()
        self._state: AgentState = AgentState.IDLE
        self._stuck_ceiling_seconds: float = stuck_ceiling_seconds
        self._start_time: float = time.time()
        self._last_heartbeat: float = time.time()
        self._heartbeat_count: int = 0
        
        # Active task context
        self._active_task_id: Optional[str] = None
        self._active_step_name: str = ""
        self._active_task_started_at: Optional[float] = None
        self._active_cancel_fn: Optional[Callable[[], Any]] = None
        
        # Metrics
        self._total_requests: int = 0
        self._total_errors: int = 0
        self._total_fallbacks: int = 0
        self._latencies: List[float] = []
        
        # State transition history (last 50)
        self._history: List[Dict[str, Any]] = [
            {
                "from_state": None,
                "to_state": AgentState.IDLE.value,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": "Agent initialized",
            }
        ]

    def record_heartbeat(self) -> Dict[str, Any]:
        """Record an internal heartbeat ping."""
        with self._lock:
            self._last_heartbeat = time.time()
            self._heartbeat_count += 1
            return {
                "heartbeat_count": self._heartbeat_count,
                "last_heartbeat": datetime.fromtimestamp(self._last_heartbeat, timezone.utc).isoformat(timespec="seconds"),
                "state": self._state.value,
                "uptime_s": round(time.time() - self._start_time, 2),
            }

    def set_state(self, new_state: AgentState, reason: str = "") -> None:
        """Explicitly transition agent state with audit history."""
        with self._lock:
            if self._state == new_state and not reason:
                return
            old_state = self._state
            self._state = new_state
            self._history.append({
                "from_state": old_state.value,
                "to_state": new_state.value,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": reason or f"State transitioned to {new_state.value}",
            })
            if len(self._history) > 50:
                self._history.pop(0)

    def start_task(
        self,
        task_id: str,
        step_name: str = "execution_step",
        timeout_ceiling_s: Optional[float] = None,
        cancel_fn: Optional[Callable[[], Any]] = None,
    ) -> None:
        """Mark agent as ACTIVE executing a specific task chain."""
        with self._lock:
            self._total_requests += 1
            self._active_task_id = task_id
            self._active_step_name = step_name
            self._active_task_started_at = time.time()
            self._active_cancel_fn = cancel_fn
            if timeout_ceiling_s:
                self._stuck_ceiling_seconds = timeout_ceiling_s
            
            old_state = self._state
            self._state = AgentState.ACTIVE
            self._history.append({
                "from_state": old_state.value,
                "to_state": AgentState.ACTIVE.value,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": f"Started task '{task_id}' ({step_name})",
                "task_id": task_id,
            })
            if len(self._history) > 50:
                self._history.pop(0)

    def finish_task(self, task_id: str, success: bool = True, latency_ms: Optional[float] = None, error: Optional[str] = None) -> None:
        """Mark active task completed and return to IDLE (or DEGRADED if partial errors)."""
        with self._lock:
            if self._active_task_id == task_id:
                if latency_ms is not None:
                    self._latencies.append(latency_ms)
                    if len(self._latencies) > 100:
                        self._latencies.pop(0)
                elif self._active_task_started_at:
                    elapsed = (time.time() - self._active_task_started_at) * 1000
                    self._latencies.append(elapsed)
                    if len(self._latencies) > 100:
                        self._latencies.pop(0)

                if not success:
                    self._total_errors += 1

                self._active_task_id = None
                self._active_step_name = ""
                self._active_task_started_at = None
                self._active_cancel_fn = None

                new_state = AgentState.IDLE if success else AgentState.DEGRADED
                old_state = self._state
                self._state = new_state
                self._history.append({
                    "from_state": old_state.value,
                    "to_state": new_state.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "reason": f"Finished task '{task_id}' (success={success})" + (f": {error}" if error else ""),
                    "task_id": task_id,
                })
                if len(self._history) > 50:
                    self._history.pop(0)

    def record_fallback(self, reason: str = "") -> None:
        """Record an automated model/tool fallback invocation."""
        with self._lock:
            self._total_fallbacks += 1

    def cancel_active_task(self, reason: str = "Automated watchdog task cancellation") -> bool:
        """Cancel the currently active task safely without bringing down the runtime."""
        cancel_fn = None
        task_id = None
        with self._lock:
            if not self._active_task_id:
                return False
            task_id = self._active_task_id
            cancel_fn = self._active_cancel_fn
            self._active_task_id = None
            self._active_step_name = ""
            self._active_task_started_at = None
            self._active_cancel_fn = None
            self._total_errors += 1
            
            old_state = self._state
            self._state = AgentState.DEGRADED
            self._history.append({
                "from_state": old_state.value,
                "to_state": AgentState.DEGRADED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": f"Cancelled task '{task_id}': {reason}",
                "task_id": task_id,
            })
            if len(self._history) > 50:
                self._history.pop(0)

        # Invoke callback outside of lock to prevent deadlocks
        if cancel_fn:
            try:
                cancel_fn()
            except Exception:
                pass
        return True

    def check_and_update_stuck(self) -> bool:
        """Evaluate if current active task exceeds execution ceiling. Returns True if stuck."""
        with self._lock:
            if self._state == AgentState.ACTIVE and self._active_task_started_at:
                elapsed = time.time() - self._active_task_started_at
                if elapsed > self._stuck_ceiling_seconds:
                    if self._state != AgentState.STUCK:
                        old_state = self._state
                        self._state = AgentState.STUCK
                        self._history.append({
                            "from_state": old_state.value,
                            "to_state": AgentState.STUCK.value,
                            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "reason": f"Task '{self._active_task_id}' exceeded execution ceiling ({round(elapsed, 1)}s > {self._stuck_ceiling_seconds}s)",
                            "task_id": self._active_task_id,
                        })
                        if len(self._history) > 50:
                            self._history.pop(0)
                    return True
            elif self._state == AgentState.STUCK and not self._active_task_id:
                # If no active task remains, recover from stuck to idle
                self._state = AgentState.IDLE
            return self._state == AgentState.STUCK

    def get_memory_rss_mb(self) -> float:
        """Get current process memory RSS in Megabytes."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / (1024 * 1024), 2)
        except Exception:
            # Fallback estimation without psutil
            return 0.0

    def get_telemetry(self) -> Dict[str, Any]:
        """Return comprehensive telemetry of agent state machine and metrics."""
        self.check_and_update_stuck()
        with self._lock:
            now = time.time()
            uptime_s = round(now - self._start_time, 2)
            active_elapsed_s = round(now - self._active_task_started_at, 2) if self._active_task_started_at else None
            avg_latency_ms = round(sum(self._latencies) / len(self._latencies), 2) if self._latencies else 0.0
            
            return {
                "state": self._state.value,
                "is_alive": True,
                "is_ready": self._state in (AgentState.IDLE, AgentState.ACTIVE, AgentState.DEGRADED),
                "is_stuck": self._state == AgentState.STUCK,
                "uptime_seconds": uptime_s,
                "last_heartbeat": datetime.fromtimestamp(self._last_heartbeat, timezone.utc).isoformat(timespec="seconds"),
                "heartbeat_age_seconds": round(now - self._last_heartbeat, 2),
                "total_heartbeats": self._heartbeat_count,
                "active_task": {
                    "task_id": self._active_task_id,
                    "step_name": self._active_step_name,
                    "elapsed_seconds": active_elapsed_s,
                    "ceiling_seconds": self._stuck_ceiling_seconds,
                } if self._active_task_id else None,
                "metrics": {
                    "total_requests": self._total_requests,
                    "total_errors": self._total_errors,
                    "total_fallbacks": self._total_fallbacks,
                    "error_rate_pct": round((self._total_errors / self._total_requests * 100), 2) if self._total_requests else 0.0,
                    "avg_latency_ms": avg_latency_ms,
                    "memory_rss_mb": self.get_memory_rss_mb(),
                },
                "history": list(reversed(self._history[-10:])),
            }


_GLOBAL_TELEMETRY_MANAGER: Optional[StateTelemetryManager] = None


def get_telemetry_manager() -> StateTelemetryManager:
    """Return the singleton instance of StateTelemetryManager."""
    global _GLOBAL_TELEMETRY_MANAGER
    if _GLOBAL_TELEMETRY_MANAGER is None:
        _GLOBAL_TELEMETRY_MANAGER = StateTelemetryManager()
    return _GLOBAL_TELEMETRY_MANAGER
