"""Free-tier LLM chain: Groq -> Nvidia -> Gemini -> OpenRouter, cached on disk.

Every provider speaks the OpenAI /chat/completions dialect, so a single
httpx POST covers the whole chain. Responses are cached in
logs/llm_cache.json keyed by (role + prompts) so re-forges are instant and
free-tier friendly.

If every provider fails (no keys / offline / 429s), chat() returns
(None, meta) and callers fall back to deterministic local generation —
the FORGE pipeline never dies waiting on an LLM.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from typing import Any, Optional

import httpx

from backend.config import (
    LLM_CACHE_JSON,
    LLM_DIAG_JSONL,
    MODELS,
    PROVIDERS,
    ROLE_TIMEOUT_S,
    ensure_dirs,
)
from backend.health.agent_state import get_telemetry_manager
from backend.health.circuit_breaker import get_circuit_breaker_registry

REQUEST_TIMEOUT = httpx.Timeout(90.0, connect=15.0)

_CACHE_LOCK = threading.Lock()


def _load_cache() -> dict:
    try:
        return json.loads(LLM_CACHE_JSON.read_text("utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    try:
        ensure_dirs()
        tmp = LLM_CACHE_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(cache, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(LLM_CACHE_JSON)
    except Exception:
        pass


def _diag(entry: dict) -> None:
    try:
        ensure_dirs()
        with LLM_DIAG_JSONL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def extract_json(text: str) -> Optional[Any]:
    """Pull the first JSON value out of an LLM answer (handles ``` fences and prose)."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned[:4].lower() == "json":
            cleaned = cleaned[4:]
    dec = json.JSONDecoder()
    for i, ch in enumerate(cleaned):
        if ch in "[{":
            try:
                obj, _ = dec.raw_decode(cleaned, i)
                return obj
            except ValueError:
                continue
    return None


class LLMChain:
    """Ordered provider fallback for one role (planner / codegen / executor / vision)."""

    def __init__(self, role: str):
        self.role = role
        self.chain = MODELS.get(role, MODELS["planner"])
        self.timeout_s = ROLE_TIMEOUT_S.get(role, 45.0)

    def chat(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        use_cache: bool = True,
    ) -> tuple[Optional[str], dict]:
        ensure_dirs()
        tried: list[dict] = []
        cache_key = hashlib.sha256(
            (self.role + "|" + system + "|" + user).encode("utf-8")
        ).hexdigest()
        request_timeout = httpx.Timeout(self.timeout_s, connect=10.0)

        if use_cache:
            with _CACHE_LOCK:
                cached = _load_cache().get(cache_key)
            if cached:
                return cached["response"], {
                    "role": self.role,
                    "provider": "cache",
                    "model": "cache",
                    "cached": True,
                    "tried": [],
                }

        circuits = get_circuit_breaker_registry()
        telemetry = get_telemetry_manager()

        for full_id in self.chain:
            provider, model = full_id.split("/", 1)
            prov = PROVIDERS.get(provider)
            if not prov:
                continue

            # Circuit Breaker Check: bypass immediately if provider is in OPEN circuit
            if not circuits.is_available(provider):
                tried.append({"model": full_id, "ok": False, "error": "circuit breaker OPEN (fallback active)"})
                telemetry.record_fallback(f"Circuit OPEN for {provider}")
                continue

            key = next(
                (os.getenv(e) for e in prov["key_envs"] if os.getenv(e)), None
            )
            if not key:
                tried.append({"model": full_id, "ok": False, "error": "no api key"})
                continue

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            if provider == "openrouter":
                headers["HTTP-Referer"] = "https://forge.local"
                headers["X-Title"] = "FORGE"

            started = time.time()
            try:
                resp = httpx.post(
                    prov["base_url"].rstrip("/") + "/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=request_timeout,
                )
                if resp.status_code != 200:
                    circuits.record_failure(provider, status_code=resp.status_code, error=resp.text[:180])
                    telemetry.record_fallback(f"Provider {provider} returned HTTP {resp.status_code}")
                    tried.append(
                        {
                            "model": full_id,
                            "ok": False,
                            "status": resp.status_code,
                            "error": resp.text[:180],
                        }
                    )
                    _diag({"ts": started, **tried[-1]})
                    continue

                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                if not text or not text.strip():
                    tried.append({"model": full_id, "ok": False, "error": "empty completion"})
                    _diag({"ts": started, **tried[-1]})
                    continue

                # Request succeeded -> close half-open circuit / reset failure count
                circuits.record_success(provider)

                meta = {
                    "role": self.role,
                    "provider": provider,
                    "model": full_id,
                    "cached": False,
                    "tried": tried,
                    "ms": int((time.time() - started) * 1000),
                }
                _diag({"ts": started, **{k: v for k, v in meta.items() if k != "tried"}})
                with _CACHE_LOCK:
                    cache = _load_cache()
                    cache[cache_key] = {
                        "response": text,
                        "meta": {k: v for k, v in meta.items() if k != "tried"},
                        "ts": started,
                    }
                    _save_cache(cache)
                return text, meta
            except Exception as err:  # network / timeout failure -> trip circuit & record fallback
                circuits.record_failure(provider, error=repr(err)[:180])
                telemetry.record_fallback(f"Provider {provider} exception: {repr(err)[:60]}")
                tried.append({"model": full_id, "ok": False, "error": repr(err)[:180]})
                _diag({"ts": started, **tried[-1]})
                continue

        telemetry.record_fallback("All LLM providers exhausted; falling back to deterministic mode")
        return None, {"role": self.role, "provider": None, "model": None, "cached": False, "tried": tried}
