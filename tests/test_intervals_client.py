"""
Unit tests for IntervalsClient with mocked network calls and error sanitization.
"""

import json
from unittest.mock import MagicMock, patch
import urllib.error
import unittest
from intervals_plan.intervals_client import IntervalsAPIError, IntervalsClient


class TestIntervalsClient(unittest.TestCase):
    def setUp(self):
        self.secret_key = "secret_key_12345"
        self.client = IntervalsClient(api_key=self.secret_key, athlete_id="0")

    @patch("urllib.request.urlopen")
    def test_get_athlete_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "id": "i12345",
            "name": "Test Runner",
            "timezone": "Asia/Kolkata",
            "restingHR": 52,
            "lthr": 164,
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        profile = self.client.get_athlete()
        self.assertEqual(profile.id, "i12345")
        self.assertEqual(profile.name, "Test Runner")
        self.assertEqual(profile.timezone, "Asia/Kolkata")
        self.assertEqual(profile.restingHR, 52)
        self.assertEqual(profile.lthr, 164)

    @patch("urllib.request.urlopen")
    def test_doctor_healthy(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "id": "i12345",
            "name": "Test Runner",
            "timezone": "Asia/Kolkata",
            "restingHR": 52,
            "lthr": 164,
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.client.doctor()
        self.assertEqual(res["status"], "HEALTHY")
        self.assertEqual(res["athlete_id"], "i12345")

    @patch("urllib.request.urlopen")
    def test_error_redaction(self, mock_urlopen):
        # Simulate server error containing the secret key
        err_body = f"Forbidden: user with key {self.secret_key} unauthorized".encode("utf-8")
        mock_error = urllib.error.HTTPError(
            url="https://intervals.icu/api/v1/athlete/0",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=err_body)),
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(IntervalsAPIError) as ctx:
            self.client.get_athlete()

        error_message = str(ctx.exception)
        self.assertNotIn(self.secret_key, error_message, "Secret API key was leaked in error message!")
        self.assertIn("<REDACTED_API_KEY>", error_message)


if __name__ == "__main__":
    unittest.main()

