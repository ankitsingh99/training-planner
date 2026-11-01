"""
TrainingPeaks API Client & Connector:
Provides integration with TrainingPeaks Partner API (v3) for syncing
planned workouts, reading athlete zones, and inspecting workout history.
Strictly redacts all authorization tokens from logs and error messages.
"""

import json
from typing import Any, Dict, List, Optional, Union
import urllib.error
import urllib.parse
import urllib.request

from intervals_plan.security import redact_headers, sanitize_text


class TrainingPeaksAPIError(Exception):
    """Custom exception for TrainingPeaks API failures with credential redaction."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        secret_to_redact: Optional[str] = None,
    ):
        clean_msg = sanitize_text(message, secret_to_redact)
        clean_body = sanitize_text(response_body or "", secret_to_redact)
        super().__init__(clean_msg)
        self.status_code = status_code
        self.response_body = clean_body

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"TrainingPeaks API Error ({self.status_code}): {base}"
        return f"TrainingPeaks API Error: {base}"


class TrainingPeaksClient:
    """Connector for the TrainingPeaks Public / Partner API."""

    def __init__(
        self,
        access_token: str = "",
        client_id: str = "",
        client_secret: str = "",
        athlete_id: str = "",
        base_url: str = "https://api.trainingpeaks.com",
    ):
        self.access_token = access_token.strip()
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.athlete_id = athlete_id.strip()
        self.base_url = base_url.rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AdaptPulse/0.3.0",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        if query_params:
            url += f"?{urllib.parse.urlencode(query_params)}"

        payload = None
        if data is not None:
            payload = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(
            url=url,
            data=payload,
            headers=self._get_headers(),
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                if not body.strip():
                    return {}
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            try:
                err_body = exc.read().decode("utf-8")
            except Exception:
                err_body = ""
            msg = f"HTTP {exc.code} for {method} {url}: {exc.reason}"
            raise TrainingPeaksAPIError(
                message=msg,
                status_code=exc.code,
                response_body=err_body,
                secret_to_redact=self.access_token,
            ) from exc
        except urllib.error.URLError as exc:
            msg = f"Network failure for {method} {url}: {exc.reason}"
            raise TrainingPeaksAPIError(
                message=msg,
                secret_to_redact=self.access_token,
            ) from exc

    def check_connection(self) -> Dict[str, Any]:
        """Test API connectivity and credentials."""
        if not self.access_token:
            return {
                "status": "UNCONFIGURED",
                "message": "TRAININGPEAKS_ACCESS_TOKEN is not configured in .env",
            }
        try:
            athlete = self.get_athlete()
            return {
                "status": "HEALTHY",
                "athlete_id": athlete.get("athleteId") or athlete.get("id"),
                "first_name": athlete.get("firstName", ""),
                "last_name": athlete.get("lastName", ""),
                "email": athlete.get("email", ""),
            }
        except TrainingPeaksAPIError as exc:
            return {
                "status": "ERROR",
                "error": str(exc),
            }

    def get_athlete(self) -> Dict[str, Any]:
        """Fetch the authenticated athlete profile."""
        return self._request("GET", "/v3/athlete")

    def get_athlete_zones(self) -> Dict[str, Any]:
        """Fetch athlete heart rate, power, and pace training zones."""
        return self._request("GET", "/v3/athlete/zones")

    def get_workouts(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch workouts across a date range (YYYY-MM-DD)."""
        res = self._request("GET", f"/v3/workouts/{start_date}/{end_date}")
        if isinstance(res, list):
            return res
        return []

    def get_workout(self, workout_id: Union[int, str]) -> Dict[str, Any]:
        """Fetch a specific workout by ID."""
        return self._request("GET", f"/v3/workouts/{workout_id}")

    def create_workout(self, workout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a planned workout in TrainingPeaks calendar."""
        return self._request("POST", "/v3/workouts", data=workout_data)

    def update_workout(self, workout_id: Union[int, str], workout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workout in TrainingPeaks."""
        return self._request("PUT", f"/v3/workouts/{workout_id}", data=workout_data)

    def delete_workout(self, workout_id: Union[int, str]) -> bool:
        """Delete a workout by ID."""
        self._request("DELETE", f"/v3/workouts/{workout_id}")
        return True
