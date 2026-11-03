"""Tests for OpenRouter token-lean LLM client, caching, zero-cost enforcement, and text trimming."""
import io
import json
import sqlite3
import urllib.error
from pathlib import Path
import pytest

from intervals_plan.llm_client import (
    DEFAULT_FREE_MODEL,
    FALLBACK_FREE_MODELS,
    OpenRouterClient,
    _IN_MEMORY_MODELS_CACHE,
    get_session_token_usage,
    is_free_model,
    print_token_benchmark,
    reset_session_token_usage,
    trim_text_content,
)


def test_is_free_model_validation():
    """Verify strict zero-cost model filtering."""
    assert is_free_model("openrouter/free") is True
    assert is_free_model("google/gemma-4-31b-it:free") is True
    assert is_free_model("auto") is True
    assert is_free_model("any") is True
    assert is_free_model("openai/gpt-4o") is False
    assert is_free_model("anthropic/claude-3.5-sonnet") is False
    assert is_free_model("") is False


def test_trim_text_content():
    """Verify input text compression and HTML tag stripping."""
    raw = "<div>Hello   <b>World</b>\n\n\nThis   is a    test.</div>"
    trimmed = trim_text_content(raw, max_chars=100)
    assert trimmed == "Hello World This is a test."

    long_text = "word " * 1000
    capped = trim_text_content(long_text, max_chars=50)
    assert len(capped) < 120
    assert "[truncated for token conservation]" in capped

    assert trim_text_content("") == ""


def test_sqlite_cache_initialization_and_hits(tmp_path: Path):
    """Verify response persistence in local SQLite cache."""
    db_path = tmp_path / "cache" / "test_llm.sqlite"
    client = OpenRouterClient(api_key="test_key", cache_db_path=db_path)

    # Cache should be empty initially
    assert client.get_cached_response("nonexistent_hash") is None

    # Save a response
    client.save_cached_response("hash_123", "google/gemma-4-31b-it:free", "Keep pushing threshold intervals.", 45, 12)
    cached = client.get_cached_response("hash_123")
    assert cached is not None
    assert cached[0] == "Keep pushing threshold intervals."
    assert cached[1] == 45
    assert cached[2] == 12


def test_generate_requires_api_key(tmp_path: Path, monkeypatch):
    """Verify error raised when API key is missing."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = OpenRouterClient(api_key="", cache_db_path=tmp_path / "cache.sqlite")
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is not configured"):
        client.generate("Give coaching advice")


def test_generate_rejects_paid_model(tmp_path: Path):
    """Verify error raised when a paid model is requested."""
    client = OpenRouterClient(api_key="test_key", cache_db_path=tmp_path / "cache.sqlite")
    with pytest.raises(ValueError, match="Strict Zero-Cost Violation"):
        client.generate("Test prompt", model="openai/gpt-4o")


def test_generate_network_call_and_cache_hit(tmp_path: Path, monkeypatch):
    """Verify full generate lifecycle: 1st call makes mock request, 2nd call hits cache with 0 tokens."""
    reset_session_token_usage()
    db_path = tmp_path / "cache" / "test_lifecycle.sqlite"
    client = OpenRouterClient(api_key="fake_test_key", cache_db_path=db_path)

    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Maintain 80% aerobic base; schedule 2x weekly mobility sets."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 52,
            "completion_tokens": 18,
            "total_tokens": 70
        }
    }

    class MockHTTPResponse:
        def __init__(self, data):
            self.data = json.dumps(data).encode("utf-8")
        def read(self):
            return self.data
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    request_count = 0

    def mock_urlopen(req, timeout=45):
        nonlocal request_count
        if "/models" in req.full_url:
            return MockHTTPResponse({"data": [{"id": "google/gemma-4-31b-it:free", "pricing": {"prompt": "0", "completion": "0"}}]})
        request_count += 1
        return MockHTTPResponse(mock_response)

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    # 1st Call: Network request
    ans1 = client.generate("Plan microcycle for athlete", model="google/gemma-4-31b-it:free")
    assert "Maintain 80% aerobic base" in ans1
    assert request_count == 1

    usage1 = get_session_token_usage()
    assert usage1["requests"] == 1
    assert usage1["prompt_tokens"] == 52
    assert usage1["completion_tokens"] == 18
    assert usage1["total_tokens"] == 70
    assert usage1["cache_hits"] == 0

    # 2nd Call: Should hit local SQLite cache and consume 0 new tokens
    ans2 = client.generate("Plan microcycle for athlete", model="google/gemma-4-31b-it:free")
    assert ans2 == ans1
    assert request_count == 1  # No new network request

    usage2 = get_session_token_usage()
    assert usage2["requests"] == 1
    assert usage2["total_tokens"] == 70  # Tokens did not increase
    assert usage2["cache_hits"] == 1


def test_generate_model_fallback_on_error(tmp_path: Path, monkeypatch):
    """Verify client attempts next free model in pool if primary returns HTTP error."""
    _IN_MEMORY_MODELS_CACHE.clear()
    reset_session_token_usage()
    db_path = tmp_path / "cache" / "test_fallback.sqlite"
    client = OpenRouterClient(api_key="fake_key", cache_db_path=db_path)

    call_models = []

    def mock_urlopen(req, timeout=45):
        if "/models" in req.full_url:
            return io.BytesIO(json.dumps({
                "data": [
                    {"id": "google/gemma-4-31b-it:free", "pricing": {"prompt": "0", "completion": "0"}},
                    {"id": "meta-llama/llama-3.3-70b-instruct:free", "pricing": {"prompt": "0", "completion": "0"}},
                ]
            }).encode("utf-8"))
        body = json.loads(req.data.decode("utf-8"))
        model = body.get("model")
        call_models.append(model)
        if len(call_models) == 1:
            # First model fails with 503 Service Unavailable
            fp = io.BytesIO(b'{"error": "rate limit"}')
            raise urllib.error.HTTPError(req.full_url, 503, "Service Unavailable", {}, fp)
        # Second model succeeds
        res_data = {
            "choices": [{"message": {"content": "Recovery advice succeeded."}}],
            "usage": {"prompt_tokens": 30, "completion_tokens": 10, "total_tokens": 40}
        }
        return io.BytesIO(json.dumps(res_data).encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    ans = client.generate("Need recovery advice", model="google/gemma-4-31b-it:free")
    assert ans == "Recovery advice succeeded."
    assert len(call_models) >= 2


def test_fetch_free_models_caching(tmp_path: Path, monkeypatch):
    """Verify free model discovery from OpenRouter API and local caching."""
    client = OpenRouterClient(api_key="fake_key", cache_db_path=tmp_path / "cache.sqlite")

    mock_models_payload = {
        "data": [
            {
                "id": "google/gemma-4-31b-it:free",
                "pricing": {"prompt": "0", "completion": "0"}
            },
            {
                "id": "openai/gpt-4o",
                "pricing": {"prompt": "0.005", "completion": "0.015"}
            },
            {
                "id": "openrouter/free",
                "pricing": {"prompt": "0", "completion": "0"}
            }
        ]
    }

    def mock_urlopen(req, timeout=5):
        return io.BytesIO(json.dumps(mock_models_payload).encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    models = client.fetch_free_models(force_refresh=True)
    assert "google/gemma-4-31b-it:free" in models
    assert "openrouter/free" in models
    assert "openai/gpt-4o" not in models


def test_token_benchmark_reporting(capsys):
    """Verify token benchmark printing function."""
    reset_session_token_usage()
    print_token_benchmark()
    out = capsys.readouterr().out
    assert "OPENROUTER TOKEN BENCHMARK SUMMARY" in out
    assert "Total API Requests:" in out
    assert "Zero-Cost Compliance:" in out
