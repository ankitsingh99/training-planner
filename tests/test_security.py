"""
Unit tests for security, credential masking, and redaction.
"""

import unittest
from intervals_plan.security import redact_headers, redact_secret, sanitize_text


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


if __name__ == "__main__":
    unittest.main()
