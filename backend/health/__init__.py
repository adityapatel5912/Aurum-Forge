"""Autonomous Health System for FORGE Agent Runtime.

Provides:
- Dual-probe architecture (Process Liveness & Operational Readiness)
- Internal heartbeat & state telemetry (Idle, Active, Stuck, Degraded)
- Independent watchdog & automated recovery (Task Cancellation, Runtime Recycling, Circuit Breaking)
"""
from __future__ import annotations

from backend.health.agent_state import AgentState, StateTelemetryManager, get_telemetry_manager
from backend.health.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerState,
    get_circuit_breaker_registry,
)
from backend.health.probes import check_liveness, check_readiness, get_full_telemetry
from backend.health.watchdog import AgentWatchdog, get_watchdog, start_watchdog, stop_watchdog

__all__ = [
    "AgentState",
    "StateTelemetryManager",
    "get_telemetry_manager",
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerRegistry",
    "get_circuit_breaker_registry",
    "AgentWatchdog",
    "get_watchdog",
    "start_watchdog",
    "stop_watchdog",
    "check_liveness",
    "check_readiness",
    "get_full_telemetry",
]
