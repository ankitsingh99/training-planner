"""
Security and credential protection utilities for Intervals.icu.
"""

import getpass
import os
import re
from typing import Any, Dict, Optional


def redact_secret(val: Optional[str], visible_chars: int = 4) -> str:
    """Return a masked representation of a secret string."""
    if not val:
        return "<empty>"
    if len(val) <= visible_chars * 2:
        return "***"
    return f"{val[:visible_chars]}...{val[-visible_chars:]}"


def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of headers with sensitive authorization tokens redacted."""
    sanitized = {}
    for k, v in headers.items():
        if k.lower() in ("authorization", "api-key", "token", "password"):
            sanitized[k] = "<REDACTED>"
        else:
            sanitized[k] = v
    return sanitized


def sanitize_text(text: str, secret: Optional[str] = None) -> str:
    """Redact known secret patterns and any provided secret from text."""
    if not text:
        return ""
    if secret and len(secret) > 4:
        text = text.replace(secret, "<REDACTED_API_KEY>")
    # Redact basic auth header patterns
    text = re.sub(r"Basic\s+[A-Za-z0-9+/=]+", "Basic <REDACTED_TOKEN>", text)
    # Redact generic bearer tokens
    text = re.sub(r"Bearer\s+[A-Za-z0-9._~+/-]+", "Bearer <REDACTED_TOKEN>", text)
    return text


def get_secure_key(env_var: str = "INTERVALS_API_KEY") -> str:
    """Retrieve the API key from environment, or prompt interactively via getpass."""
    key = os.environ.get(env_var, "").strip().strip("'\"")
    if key:
        return key
    
    print("\n[Security] INTERVALS_API_KEY is not set in environment or .env.")
    print("Please enter your Intervals.icu API key (input will not echo):")
    try:
        entered = getpass.getpass("API Key: ").strip().strip("'\"")
        if entered:
            os.environ[env_var] = entered
            return entered
    except (EOFError, KeyboardInterrupt):
        pass
    
    return ""

