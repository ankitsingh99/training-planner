"""
Unit tests for IntervalsClient with mocked network calls and error sanitization.
"""

import json
from unittest.mock import MagicMock, patch
import urllib.error
import unittest

from intervals_plan.api_models import IntervalsEvent
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
        self.assertNotIn(self.secret_key, error_message)
        self.assertIn("<REDACTED_API_KEY>", error_message)

    @patch("urllib.request.urlopen")
    def test_events_crud_and_bulk(self, mock_urlopen):
        # 1. list_events
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps([
            {"id": 101, "start_date_local": "2026-11-02T07:00:00", "name": "Run", "category": "WORKOUT", "type": "Run"}
        ]).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        events = self.client.list_events("2026-11-01", "2026-11-07")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, 101)

        # 2. get_event
        mock_resp.read.return_value = json.dumps({
            "id": 101, "start_date_local": "2026-11-02T07:00:00", "name": "Run", "category": "WORKOUT", "type": "Run"
        }).encode("utf-8")
        ev = self.client.get_event(101)
        self.assertEqual(ev.name, "Run")

        # 3. update_event
        mock_resp.read.return_value = json.dumps({"id": 102, "start_date_local": "2026-11-03T07:00:00", "name": "Updated"}).encode("utf-8")
        new_ev = IntervalsEvent(start_date_local="2026-11-03T07:00:00", name="Created")
        up_res = self.client.update_event(102, new_ev)
        self.assertEqual(up_res.name, "Updated")

        # 4. delete_event
        mock_resp.read.return_value = b"{}"
        self.client.delete_event(102)

        # 5. bulk_upsert_events
        mock_resp.read.return_value = json.dumps([{"id": 103}, {"id": 104}]).encode("utf-8")
        bulk_res = self.client.bulk_upsert_events([new_ev])
        self.assertEqual(len(bulk_res), 2)

        # 6. get_activities
        mock_resp.read.return_value = json.dumps([{"id": "a1", "type": "Run"}]).encode("utf-8")
        acts = self.client.get_activities("2026-11-01", "2026-11-07")
        self.assertEqual(len(acts), 1)

    @patch("urllib.request.urlopen")
    def test_wellness_and_sport_settings(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"restingHR": 50, "ctl": 45.0}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # 1. get_wellness
        w = self.client.get_wellness("2026-11-02")
        self.assertEqual(w.get("restingHR"), 50)

        # 2. get_wellness_range
        mock_resp.read.return_value = json.dumps([{"id": "2026-11-01", "restingHR": 51}]).encode("utf-8")
        w_range = self.client.get_wellness_range("2026-11-01", "2026-11-02")
        self.assertEqual(len(w_range), 1)

        # 3. get_sport_settings
        mock_resp.read.return_value = json.dumps([{"types": ["Run"], "lthr": 182}]).encode("utf-8")
        sports = self.client.get_sport_settings()
        self.assertEqual(len(sports), 1)

    @patch("urllib.request.urlopen")
    def test_api_errors_and_fallbacks(self, mock_urlopen):
        # 1. Doctor error response
        mock_err = urllib.error.HTTPError(
            url="https://intervals.icu/api/v1/athlete/0",
            code=500,
            msg="Server error",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=b'{"error": "Internal Error"}')),
        )
        mock_urlopen.side_effect = mock_err
        doc_res = self.client.doctor()
        self.assertEqual(doc_res["status"], "ERROR")

        # 2. get_wellness failure returns None
        self.assertIsNone(self.client.get_wellness("2026-11-02"))

        # 3. get_wellness_range failure returns empty list
        self.assertEqual(self.client.get_wellness_range("2026-11-01", "2026-11-02"), [])

        # 4. get_sport_settings failure returns empty list
        self.assertEqual(self.client.get_sport_settings(), [])

        # 5. get_activities failure returns empty list
        self.assertEqual(self.client.get_activities("2026-11-01", "2026-11-02"), [])


if __name__ == "__main__":
    unittest.main()
