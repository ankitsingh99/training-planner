"""
Unit tests for TrainingPeaksClient connector with credential redaction and mocked HTTP calls.
"""

import json
from unittest.mock import MagicMock, patch
import urllib.error
import unittest

from intervals_plan.trainingpeaks_client import TrainingPeaksAPIError, TrainingPeaksClient


class TestTrainingPeaksClient(unittest.TestCase):
    def setUp(self):
        self.token = "tp_token_secret_abcdef12345"
        self.client = TrainingPeaksClient(
            access_token=self.token,
            client_id="my_client_id",
            client_secret="my_client_secret",
            athlete_id="998877",
            base_url="https://api.trainingpeaks.com",
        )

    def test_error_redaction_and_string_representation(self):
        secret = "secret_auth_token_999"
        # With status code
        err = TrainingPeaksAPIError(
            message=f"Request failed with token {secret}",
            status_code=401,
            response_body=f"Invalid token: {secret}",
            secret_to_redact=secret,
        )
        self.assertNotIn(secret, str(err))
        self.assertNotIn(secret, err.response_body)
        self.assertIn("<REDACTED_API_KEY>", str(err))
        self.assertIn("<REDACTED_API_KEY>", err.response_body)
        self.assertIn("TrainingPeaks API Error (401):", str(err))

        # Without status code
        err_no_code = TrainingPeaksAPIError(
            message=f"Network error with token {secret}",
            secret_to_redact=secret,
        )
        self.assertNotIn(secret, str(err_no_code))
        self.assertIn("<REDACTED_API_KEY>", str(err_no_code))
        self.assertIn("TrainingPeaks API Error:", str(err_no_code))

    def test_headers_with_and_without_token(self):
        headers = self.client._get_headers()
        self.assertEqual(headers["Authorization"], f"Bearer {self.token}")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["User-Agent"], "AdaptPulse/0.3.0")

        empty_client = TrainingPeaksClient()
        empty_headers = empty_client._get_headers()
        self.assertNotIn("Authorization", empty_headers)

    @patch("urllib.request.urlopen")
    def test_request_get_with_query_params(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "ok"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.client._request("GET", "/v3/test", query_params={"page": "1", "limit": "10"})
        self.assertEqual(res, {"status": "ok"})
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        self.assertIn("/v3/test?page=1&limit=10", req.full_url)
        self.assertEqual(req.get_method(), "GET")

    @patch("urllib.request.urlopen")
    def test_request_post_with_data(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"id": 1001, "title": "Intervals"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        payload = {"title": "Intervals", "duration": 3600}
        res = self.client._request("POST", "/v3/workouts", data=payload)
        self.assertEqual(res["id"], 1001)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(json.loads(req.data.decode("utf-8")), payload)

    @patch("urllib.request.urlopen")
    def test_request_empty_body_returns_dict(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"   "
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = self.client._request("DELETE", "/v3/workouts/1001")
        self.assertEqual(res, {})

    @patch("urllib.request.urlopen")
    def test_request_http_error_redaction(self, mock_urlopen):
        err_body = f"Forbidden: token {self.token} expired".encode("utf-8")
        mock_error = urllib.error.HTTPError(
            url="https://api.trainingpeaks.com/v3/athlete",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=err_body)),
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(TrainingPeaksAPIError) as ctx:
            self.client.get_athlete()

        self.assertNotIn(self.token, str(ctx.exception))
        self.assertNotIn(self.token, ctx.exception.response_body)
        self.assertIn("<REDACTED_API_KEY>", ctx.exception.response_body)
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("urllib.request.urlopen")
    def test_request_http_error_unread_exception(self, mock_urlopen):
        mock_fp = MagicMock()
        mock_fp.read.side_effect = Exception("Read failed")
        mock_error = urllib.error.HTTPError(
            url="https://api.trainingpeaks.com/v3/athlete",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=mock_fp,
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(TrainingPeaksAPIError) as ctx:
            self.client.get_athlete()

        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(ctx.exception.response_body, "")

    @patch("urllib.request.urlopen")
    def test_request_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with self.assertRaises(TrainingPeaksAPIError) as ctx:
            self.client.get_athlete()

        self.assertIn("Network failure", str(ctx.exception))
        self.assertIsNone(ctx.exception.status_code)

    def test_check_connection_unconfigured(self):
        client = TrainingPeaksClient(access_token="")
        status = client.check_connection()
        self.assertEqual(status["status"], "UNCONFIGURED")
        self.assertIn("TRAININGPEAKS_ACCESS_TOKEN is not configured", status["message"])

    @patch.object(TrainingPeaksClient, "get_athlete")
    def test_check_connection_healthy(self, mock_get_athlete):
        mock_get_athlete.return_value = {
            "athleteId": "ath_789",
            "firstName": "Alex",
            "lastName": "Rider",
            "email": "alex@example.com",
        }
        status = self.client.check_connection()
        self.assertEqual(status["status"], "HEALTHY")
        self.assertEqual(status["athlete_id"], "ath_789")
        self.assertEqual(status["first_name"], "Alex")
        self.assertEqual(status["last_name"], "Rider")
        self.assertEqual(status["email"], "alex@example.com")

    @patch.object(TrainingPeaksClient, "get_athlete")
    def test_check_connection_healthy_fallback_id(self, mock_get_athlete):
        mock_get_athlete.return_value = {
            "id": "fallback_id_456",
            "firstName": "Sam",
            "lastName": "Fisher",
            "email": "sam@example.com",
        }
        status = self.client.check_connection()
        self.assertEqual(status["status"], "HEALTHY")
        self.assertEqual(status["athlete_id"], "fallback_id_456")

    @patch.object(TrainingPeaksClient, "get_athlete")
    def test_check_connection_error(self, mock_get_athlete):
        mock_get_athlete.side_effect = TrainingPeaksAPIError("OAuth handshake failed", status_code=401)
        status = self.client.check_connection()
        self.assertEqual(status["status"], "ERROR")
        self.assertIn("OAuth handshake failed", status["error"])

    @patch.object(TrainingPeaksClient, "_request")
    def test_get_athlete_and_zones(self, mock_request):
        mock_request.side_effect = [{"id": "ath_1"}, {"heartRate": []}]

        ath = self.client.get_athlete()
        self.assertEqual(ath, {"id": "ath_1"})
        mock_request.assert_called_with("GET", "/v3/athlete")

        zones = self.client.get_athlete_zones()
        self.assertEqual(zones, {"heartRate": []})
        mock_request.assert_called_with("GET", "/v3/athlete/zones")

    @patch.object(TrainingPeaksClient, "_request")
    def test_get_workouts(self, mock_request):
        mock_request.return_value = [{"workoutId": 1}, {"workoutId": 2}]
        workouts = self.client.get_workouts("2026-11-01", "2026-11-07")
        self.assertEqual(len(workouts), 2)
        mock_request.assert_called_with("GET", "/v3/workouts/2026-11-01/2026-11-07")

        # Fallback when non-list returned
        mock_request.return_value = {"error": "none"}
        workouts_empty = self.client.get_workouts("2026-11-01", "2026-11-07")
        self.assertEqual(workouts_empty, [])

    @patch.object(TrainingPeaksClient, "_request")
    def test_crud_workout_methods(self, mock_request):
        # get_workout
        mock_request.return_value = {"workoutId": 42, "title": "Tempo Run"}
        w = self.client.get_workout(42)
        self.assertEqual(w["workoutId"], 42)
        mock_request.assert_called_with("GET", "/v3/workouts/42")

        # create_workout
        mock_request.return_value = {"workoutId": 43, "title": "New Ride"}
        w_created = self.client.create_workout({"title": "New Ride"})
        self.assertEqual(w_created["workoutId"], 43)
        mock_request.assert_called_with("POST", "/v3/workouts", data={"title": "New Ride"})

        # update_workout
        mock_request.return_value = {"workoutId": 43, "title": "Updated Ride"}
        w_updated = self.client.update_workout(43, {"title": "Updated Ride"})
        self.assertEqual(w_updated["workoutId"], 43)
        mock_request.assert_called_with("PUT", "/v3/workouts/43", data={"title": "Updated Ride"})

        # delete_workout
        mock_request.return_value = {}
        res = self.client.delete_workout(43)
        self.assertTrue(res)
        mock_request.assert_called_with("DELETE", "/v3/workouts/43")


if __name__ == "__main__":
    unittest.main()
