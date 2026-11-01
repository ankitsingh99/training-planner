"""
Unit tests for security, credential masking, and redaction.
"""

import os
from unittest.mock import patch
import unittest
from intervals_plan.security import get_secure_key, redact_headers, redact_secret, sanitize_text


class TestSecurity(unittest.TestCase):
    def test_redact_secret(self):
        self.assertEqual(redact_secret(""), "<empty>")
        self.assertEqual(redact_secret(None), "<empty>")
        self.assertEqual(redact_secret("short"), "***")
        self.assertEqual(redact_secret("my_super_secret_api_key_12345"), "my_s...2345")

    def test_redact_headers(self):
        headers = {
            "Authorization": "Basic YXBpa2V5MTIzNA==",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Key": "secret123",
        }
        sanitized = redact_headers(headers)
        self.assertEqual(sanitized["Authorization"], "<REDACTED>")
        self.assertEqual(sanitized["Api-Key"], "<REDACTED>")
        self.assertEqual(sanitized["Content-Type"], "application/json")

    def test_sanitize_text(self):
        self.assertEqual(sanitize_text(""), "")
        secret = "7djsj145o8tx45y8cvjte0cpi"
        err = f"Failed to authenticate with key {secret} at endpoint https://intervals.icu"
        sanitized = sanitize_text(err, secret)
        self.assertNotIn(secret, sanitized)
        self.assertIn("<REDACTED_API_KEY>", sanitized)

    def test_sanitize_auth_tokens_in_logs(self):
        raw = "Sent header Authorization: Basic QVBJX0tFWTpteWtleQ=="
        sanitized = sanitize_text(raw)
        self.assertNotIn("QVBJX0tFWTpteWtleQ==", sanitized)
        self.assertIn("Basic <REDACTED_TOKEN>", sanitized)

        bearer_raw = "Authorization: Bearer my_jwt_token_123.abc"
        bearer_sanitized = sanitize_text(bearer_raw)
        self.assertIn("Bearer <REDACTED_TOKEN>", bearer_sanitized)

    def test_get_secure_key_from_env(self):
        with patch.dict(os.environ, {"INTERVALS_API_KEY": "env_test_key_123"}):
            self.assertEqual(get_secure_key(), "env_test_key_123")

    @patch("getpass.getpass", return_value="prompted_key_456")
    def test_get_secure_key_from_prompt(self, mock_getpass):
        with patch.dict(os.environ, {}, clear=True):
            key = get_secure_key()
            self.assertEqual(key, "prompted_key_456")

    @patch("getpass.getpass", side_effect=EOFError)
    def test_get_secure_key_prompt_interrupted(self, mock_getpass):
        with patch.dict(os.environ, {}, clear=True):
            key = get_secure_key()
            self.assertEqual(key, "")


if __name__ == "__main__":
    unittest.main()
