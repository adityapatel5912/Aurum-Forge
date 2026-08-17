"""Healer — the FORGE self-heal loop.

Two flavours:
  * Healer.attempt(fn)   — retry a callable HEAL_RETRIES times, 200ms apart.
  * Healer.fallback_locator(page, role, name, css) — primary accessible-role
    locator with a CSS fallback (the same pattern embedded in every forged
    server, exposed here for the executor when it drives pages directly).
"""
from __future__ import annotations

import time
from typing import Callable

from backend.config import HEAL_DELAY_MS, HEAL_RETRIES


class Healer:
    def __init__(self, retries: int = HEAL_RETRIES, delay_ms: int = HEAL_DELAY_MS):
        self.retries = retries
        self.delay_ms = delay_ms

    def attempt(self, fn: Callable, *args, **kwargs):
        """Run fn, retrying on exception. Returns the first success or raises the last error."""
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as err:
                last_err = err
                if attempt < self.retries:
                    time.sleep(self.delay_ms / 1000.0)
        assert last_err is not None
        raise last_err

    @staticmethod
    def fallback_locator(page, role=None, name=None, css=None):
        """Locator 1: get_by_role(role, name=name). Locator 2: page.locator(css)."""
        if role:
            try:
                return page.get_by_role(role, name=name) if name else page.get_by_role(role)
            except Exception:
                pass
        return page.locator(css or "body")
