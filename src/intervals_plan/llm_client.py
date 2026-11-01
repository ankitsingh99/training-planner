"""Token-Optimized OpenRouter LLM Client for AdaptPulse.

Implements token-lean architecture:
1. Strict Zero-Cost Enforcement: Uses ':free' models exclusively.
2. Local Persistent SQLite Response Cache: 0-token instant reuse of identical queries.
3. Input Text Trimming: Strips HTML and collapses redundant whitespace.
4. Prompt Caching Optimization: Structures system message at index 0.
5. Strict Output Token Bounds: Default max_tokens cap to prevent verbose completions.
6. Token Accounting Ledger: Tracks prompt, completion, total tokens, and cache hits.
7. Zero Emojis: Clean, sports-science oriented logging.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_FREE_MODEL = "openrouter/free"

FALLBACK_FREE_MODELS = [
    "openrouter/free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "minimax/minimax-m3.1-flash:free",
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]

_DEFAULT_CACHE_DIR = Path("data/cache")
_CACHE_DB_PATH = _DEFAULT_CACHE_DIR / "llm_cache.sqlite"
_MODELS_CACHE_FILE = _DEFAULT_CACHE_DIR / "openrouter_free_models.json"
_CACHE_TTL_SECONDS = 3600

_IN_MEMORY_MODELS_CACHE: Dict[str, Any] = {"timestamp": 0.0, "models": []}

_SESSION_USAGE: Dict[str, Any] = {
    "requests": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "cache_hits": 0,
    "calls": [],
}


def get_session_token_usage() -> Dict[str, Any]:
    """Return a snapshot of token usage metrics for the active session."""
    return {
        "requests": _SESSION_USAGE["requests"],
        "prompt_tokens": _SESSION_USAGE["prompt_tokens"],
        "completion_tokens": _SESSION_USAGE["completion_tokens"],
        "total_tokens": _SESSION_USAGE["total_tokens"],
        "cache_hits": _SESSION_USAGE["cache_hits"],
        "calls": list(_SESSION_USAGE["calls"]),
    }


def reset_session_token_usage() -> None:
    """Reset the session token usage counters."""
    global _SESSION_USAGE
    _SESSION_USAGE = {
        "requests": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cache_hits": 0,
        "calls": [],
    }


def print_token_benchmark() -> None:
    """Print an executive summary of token consumption and local cache savings."""
    u = get_session_token_usage()
    print("\n" + "=" * 64)
    print("  ADAPTPULSE - OPENROUTER TOKEN BENCHMARK SUMMARY")
    print("=" * 64)
    print(f"  Total API Requests:       {u['requests']}")
    print(f"  Local Cache Hits (0 tok): {u['cache_hits']}")
    print(f"  Prompt Tokens:            {u['prompt_tokens']}")
    print(f"  Completion Tokens:        {u['completion_tokens']}")
    print(f"  Total Tokens Consumed:    {u['total_tokens']}")
    print("  Zero-Cost Compliance:     Strictly Free Tier (:free)")
    print("=" * 64 + "\n")


def is_free_model(model_name: str) -> bool:
    """Check whether a model qualifies under the zero-cost free tier policy."""
    if not model_name:
        return False
    return (
        model_name.endswith(":free")
        or model_name in ("openrouter/free", "auto", "any")
    )


def trim_text_content(text: str, max_chars: int = 4000) -> str:
    """Compress input text by stripping HTML, collapsing whitespace, and bounding length."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) > max_chars:
        clean = clean[:max_chars] + "... [truncated for token conservation]"
    return clean


class OpenRouterClient:
    """Token-lean, zero-cost OpenRouter API client with local SQLite caching."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = OPENROUTER_BASE_URL,
        default_model: str = DEFAULT_FREE_MODEL,
        cache_db_path: Optional[Path] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.cache_db_path = cache_db_path or _CACHE_DB_PATH
        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize the local SQLite cache database."""
        try:
            self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS response_cache (
                        cache_key TEXT PRIMARY KEY,
                        model TEXT,
                        response TEXT,
                        prompt_tokens INTEGER,
                        completion_tokens INTEGER,
                        created_at REAL
                    )
                """)
        except Exception:
            pass

    def get_cached_response(self, cache_key: str) -> Optional[Tuple[str, int, int]]:
        """Retrieve cached response if available (returns response, prompt_tokens, completion_tokens)."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT response, prompt_tokens, completion_tokens FROM response_cache WHERE cache_key = ?",
                    (cache_key,),
                )
                row = cursor.fetchone()
                if row:
                    return str(row[0]), int(row[1] or 0), int(row[2] or 0)
        except Exception:
            pass
        return None

    def save_cached_response(
        self, cache_key: str, model: str, response: str, p_tok: int = 0, c_tok: int = 0
    ) -> None:
        """Persist LLM response to local SQLite cache for 0-token subsequent reads."""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO response_cache 
                    (cache_key, model, response, prompt_tokens, completion_tokens, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (cache_key, model, response, p_tok, c_tok, time.time()),
                )
        except Exception:
            pass

    def fetch_free_models(self, force_refresh: bool = False, timeout: int = 5) -> List[str]:
        """Dynamically discover available zero-cost (:free) models from OpenRouter."""
        now = time.time()
        if (
            not force_refresh
            and _IN_MEMORY_MODELS_CACHE.get("models")
            and (now - _IN_MEMORY_MODELS_CACHE.get("timestamp", 0) < _CACHE_TTL_SECONDS)
        ):
            return list(_IN_MEMORY_MODELS_CACHE["models"])

        if not force_refresh and _MODELS_CACHE_FILE.exists():
            try:
                cached = json.loads(_MODELS_CACHE_FILE.read_text(encoding="utf-8"))
                if now - cached.get("timestamp", 0) < _CACHE_TTL_SECONDS:
                    models = cached.get("models", [])
                    if models:
                        _IN_MEMORY_MODELS_CACHE["models"] = models
                        _IN_MEMORY_MODELS_CACHE["timestamp"] = cached["timestamp"]
                        return list(models)
            except Exception:
                pass

        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={
                    "User-Agent": "AdaptPulse-Coach (Zero-Cost Free Model Discovery)",
                    "Accept": "application/json",
                },
            )
            if self.api_key:
                req.add_header("Authorization", f"Bearer {self.api_key}")

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_models = data.get("data", [])

            discovered: List[str] = []
            for m in raw_models:
                m_id = m.get("id", "")
                if not (m_id.endswith(":free") or m_id == "openrouter/free"):
                    continue
                pricing = m.get("pricing", {})
                p_cost = str(pricing.get("prompt", "0"))
                c_cost = str(pricing.get("completion", "0"))
                if p_cost not in ("0", "0.0") or c_cost not in ("0", "0.0"):
                    continue
                discovered.append(m_id)

            if discovered:
                _IN_MEMORY_MODELS_CACHE["models"] = discovered
                _IN_MEMORY_MODELS_CACHE["timestamp"] = now
                try:
                    _MODELS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    _MODELS_CACHE_FILE.write_text(
                        json.dumps({"timestamp": now, "models": discovered}, indent=2),
                        encoding="utf-8",
                    )
                except Exception:
                    pass
                return list(discovered)
        except Exception:
            pass

        return list(FALLBACK_FREE_MODELS)

    def generate(
        self,
        prompt: str,
        *,
        system: str = "You are a concise endurance sports science coaching assistant.",
        model: Optional[str] = None,
        max_tokens: int = 400,
        temperature: float = 0.5,
        json_mode: bool = False,
        trim_input: bool = True,
        timeout: int = 45,
    ) -> str:
        """Send a token-optimized completion request with local caching and zero-cost fallback."""
        target_model = model or self.default_model
        if not is_free_model(target_model):
            raise ValueError(f"Strict Zero-Cost Violation: Model '{target_model}' is not a free-tier model (:free).")

        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured in .env or environment.")

        clean_prompt = trim_text_content(prompt, max_chars=3500) if trim_input else prompt
        clean_system = trim_text_content(system, max_chars=1000) if trim_input else system

        # Check local persistent cache (0 tokens consumed on hit)
        cache_key = hashlib.sha256(
            f"{clean_system}::{clean_prompt}::{target_model}::{json_mode}".encode("utf-8")
        ).hexdigest()
        cached = self.get_cached_response(cache_key)
        if cached is not None:
            res_text, _, _ = cached
            _SESSION_USAGE["cache_hits"] += 1
            _SESSION_USAGE["calls"].append({
                "model": f"{target_model} (local_cache_hit)",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            })
            return res_text

        messages = [
            {"role": "system", "content": clean_system},
            {"role": "user", "content": clean_prompt},
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/ankitsingh99/training-planner",
            "X-Title": "AdaptPulse-Endurance-Coach",
            "X-OpenRouter-Cache": "true",
        }

        # Candidate model fallback list
        available = self.fetch_free_models()
        if target_model in ("auto", "any", "openrouter/free"):
            candidate_models = list(available)
        else:
            candidate_models = [target_model] + [m for m in available if m != target_model]

        last_error = None

        for current_model in candidate_models:
            if not is_free_model(current_model):
                continue

            payload: Dict[str, Any] = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    usage = data.get("usage", {})
                    p_tok = usage.get("prompt_tokens", 0)
                    c_tok = usage.get("completion_tokens", 0)
                    tot_tok = usage.get("total_tokens", p_tok + c_tok)

                    _SESSION_USAGE["requests"] += 1
                    _SESSION_USAGE["prompt_tokens"] += p_tok
                    _SESSION_USAGE["completion_tokens"] += c_tok
                    _SESSION_USAGE["total_tokens"] += tot_tok
                    _SESSION_USAGE["calls"].append({
                        "model": current_model,
                        "prompt_tokens": p_tok,
                        "completion_tokens": c_tok,
                        "total_tokens": tot_tok,
                    })

                    choice = data.get("choices", [{}])[0].get("message", {})
                    content = (choice.get("content") or "").strip()
                    if not content and choice.get("reasoning"):
                        content = choice.get("reasoning").strip()

                    # Strip any reasoning or think tags
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

                    if content:
                        self.save_cached_response(cache_key, current_model, content, p_tok, c_tok)
                        return content
            except urllib.error.HTTPError as exc:
                last_error = RuntimeError(f"OpenRouter API HTTP {exc.code} for '{current_model}'")
            except Exception as exc:
                last_error = RuntimeError(f"OpenRouter request failed for '{current_model}': {exc}")

        if last_error:
            raise last_error
        raise RuntimeError("No available free models succeeded.")
