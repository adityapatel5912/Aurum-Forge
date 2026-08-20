"""Circuit Breaker Pattern for LLM Providers and Tool Integrations.

Prevents the agent from freezing or wasting quota when external APIs encounter
consecutive rate limits (HTTP 429), timeouts, or server outages.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"        # Normal operation: requests pass through
    OPEN = "open"            # Failing/tripped: requests immediately routed to fallback
    HALF_OPEN = "half_open"  # Cooldown expired: probe request allowed to test recovery


class CircuitBreaker:
    """Individual circuit breaker protecting a specific provider or dependency."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_cooldown_seconds: float = 30.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_cooldown_seconds = recovery_cooldown_seconds
        
        self._lock = threading.Lock()
        self._state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self._consecutive_failures: int = 0
        self._total_failures: int = 0
        self._total_successes: int = 0
        self._last_state_change: float = time.time()
        self._last_failure_time: Optional[float] = None
        self._last_error: str = ""

    def can_execute(self) -> bool:
        """Check if request is allowed to pass to this provider."""
        with self._lock:
            now = time.time()
            if self._state == CircuitBreakerState.CLOSED:
                return True
            elif self._state == CircuitBreakerState.OPEN:
                if (now - self._last_state_change) >= self.recovery_cooldown_seconds:
                    self._state = CircuitBreakerState.HALF_OPEN
                    self._last_state_change = now
                    return True
                return False
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Allow probe execution
                return True
            return False

    def record_success(self) -> None:
        """Record successful execution, resetting failure count or closing half-open circuit."""
        with self._lock:
            self._total_successes += 1
            self._consecutive_failures = 0
            if self._state != CircuitBreakerState.CLOSED:
                self._state = CircuitBreakerState.CLOSED
                self._last_state_change = time.time()

    def record_failure(self, status_code: Optional[int] = None, error: Optional[str] = None) -> bool:
        """Record a failure (e.g. HTTP 429 / 5xx / timeout). Returns True if circuit tripped."""
        with self._lock:
            now = time.time()
            self._total_failures += 1
            self._consecutive_failures += 1
            self._last_failure_time = now
            self._last_error = error or f"Error (status_code={status_code})"

            # If in HALF_OPEN, immediate trip back to OPEN
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.OPEN
                self._last_state_change = now
                return True

            # If consecutive failures exceed threshold or status is 429 rate limit
            if self._consecutive_failures >= self.failure_threshold or status_code == 429:
                if self._state != CircuitBreakerState.OPEN:
                    self._state = CircuitBreakerState.OPEN
                    self._last_state_change = now
                    return True
            return False

    def trip(self, reason: str = "Manual trip") -> None:
        """Force the circuit breaker to OPEN state."""
        with self._lock:
            self._state = CircuitBreakerState.OPEN
            self._last_state_change = time.time()
            self._last_error = reason

    def reset(self) -> None:
        """Reset the circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._consecutive_failures = 0
            self._last_state_change = time.time()
            self._last_error = ""

    def to_dict(self) -> Dict[str, Any]:
        """Return diagnostic dictionary of circuit state."""
        with self._lock:
            now = time.time()
            time_in_state = round(now - self._last_state_change, 2)
            cooldown_remaining = max(0.0, round(self.recovery_cooldown_seconds - time_in_state, 2)) if self._state == CircuitBreakerState.OPEN else 0.0
            
            return {
                "name": self.name,
                "state": self._state.value,
                "is_available": self._state in (CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN),
                "consecutive_failures": self._consecutive_failures,
                "total_failures": self._total_failures,
                "total_successes": self._total_successes,
                "time_in_state_seconds": time_in_state,
                "cooldown_remaining_seconds": cooldown_remaining,
                "last_error": self._last_error,
            }


class CircuitBreakerRegistry:
    """Registry holding circuit breakers for all providers and external integrations."""

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

        # Initialize default providers
        for p in ("groq", "nvidia", "gemini", "openrouter", "tools"):
            self.get_or_create(p)

    def get_or_create(self, name: str, threshold: int = 3, cooldown: float = 30.0) -> CircuitBreaker:
        """Retrieve existing or create new circuit breaker."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, failure_threshold=threshold, recovery_cooldown_seconds=cooldown)
            return self._breakers[name]

    def is_available(self, name: str) -> bool:
        """Check if target provider is available for execution."""
        breaker = self.get_or_create(name)
        return breaker.can_execute()

    def record_success(self, name: str) -> None:
        """Record success for provider."""
        breaker = self.get_or_create(name)
        breaker.record_success()

    def record_failure(self, name: str, status_code: Optional[int] = None, error: Optional[str] = None) -> bool:
        """Record failure for provider."""
        breaker = self.get_or_create(name)
        return breaker.record_failure(status_code=status_code, error=error)

    def reset_all(self) -> None:
        """Reset all circuit breakers to CLOSED."""
        with self._lock:
            for b in self._breakers.values():
                b.reset()

    def get_status(self) -> Dict[str, Any]:
        """Return status of all registered circuit breakers."""
        with self._lock:
            return {name: cb.to_dict() for name, cb in self._breakers.items()}


_GLOBAL_REGISTRY: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Singleton getter for circuit breaker registry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = CircuitBreakerRegistry()
    return _GLOBAL_REGISTRY
