"""
Intervals.icu REST API client with security redaction and error handling.
"""

import base64
import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Union

from intervals_plan.api_models import AthleteProfile, IntervalsEvent
from intervals_plan.security import redact_headers, sanitize_text


class IntervalsAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class IntervalsClient:
    def __init__(
        self,
        api_key: str,
        athlete_id: str = "0",
        base_url: str = "https://intervals.icu/api/v1",
        user_agent: str = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
        timeout: int = 45,
    ):
        self.api_key = api_key
        self.athlete_id = athlete_id or "0"
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        token = base64.b64encode(("API_KEY:" + self.api_key).encode()).decode()
        return {
            "Authorization": "Basic " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if query_params:
            query_str = urllib.parse.urlencode(query_params)
            url += f"?{query_str}"

        body = json.dumps(data).encode("utf-8") if data is not None else None
        headers = self._get_headers()

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw_err = exc.read().decode("utf-8", errors="replace")
            clean_err = sanitize_text(raw_err, self.api_key)
            msg = f"Intervals.icu returned HTTP {exc.code} for {method} {path}: {clean_err}"
            raise IntervalsAPIError(msg, status_code=exc.code, response_text=clean_err) from exc
        except urllib.error.URLError as exc:
            clean_err = sanitize_text(str(exc.reason), self.api_key)
            msg = f"Network connection error to Intervals.icu ({clean_err})"
            raise IntervalsAPIError(msg) from exc
        except Exception as exc:
            clean_err = sanitize_text(str(exc), self.api_key)
            raise IntervalsAPIError(f"Unexpected error calling Intervals.icu: {clean_err}") from exc

    def get_athlete(self) -> AthleteProfile:
        """Fetch current athlete profile."""
        data = self._request("GET", f"/athlete/{self.athlete_id}")
        return AthleteProfile.from_dict(data)

    def doctor(self) -> Dict[str, Any]:
        """Perform non-mutating diagnostics and connectivity verification."""
        try:
            profile = self.get_athlete()
            return {
                "status": "HEALTHY",
                "athlete_id": profile.id,
                "name": profile.name,
                "timezone": profile.timezone or "Not specified",
                "resting_hr": profile.restingHR,
                "lthr": profile.lthr,
            }
        except IntervalsAPIError as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "status_code": e.status_code,
            }

    def list_events(self, start_date: str, end_date: str) -> List[IntervalsEvent]:
        """List calendar events in the given date range (YYYY-MM-DD)."""
        data = self._request(
            "GET",
            f"/athlete/{self.athlete_id}/events",
            query_params={"oldest": start_date, "newest": end_date},
        )
        if not isinstance(data, list):
            return []
        return [IntervalsEvent.from_dict(item) for item in data]

    def get_event(self, event_id: Union[int, str]) -> IntervalsEvent:
        """Fetch a single calendar event by internal ID."""
        data = self._request("GET", f"/athlete/{self.athlete_id}/events/{event_id}")
        return IntervalsEvent.from_dict(data)

    def bulk_upsert_events(self, events: List[IntervalsEvent]) -> List[IntervalsEvent]:
        """Bulk create or update calendar events idempotently using external_id."""
        payload = [e.to_dict() for e in events]
        data = self._request(
            "POST",
            f"/athlete/{self.athlete_id}/events/bulk",
            data=payload,
            query_params={"upsert": "true"},
        )
        if not isinstance(data, list):
            return []
        return [IntervalsEvent.from_dict(item) for item in data]

    def update_event(self, event_id: Union[int, str], event: IntervalsEvent) -> IntervalsEvent:
        """Update a specific calendar event."""
        payload = event.to_dict()
        data = self._request("PUT", f"/athlete/{self.athlete_id}/events/{event_id}", data=payload)
        return IntervalsEvent.from_dict(data)

    def delete_event(self, event_id: Union[int, str]) -> bool:
        """Delete a calendar event by ID."""
        self._request("DELETE", f"/athlete/{self.athlete_id}/events/{event_id}")
        return True

    def get_wellness(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Fetch wellness metrics (resting HR, HRV, sleep, fatigue) for a single date."""
        try:
            return self._request("GET", f"/athlete/{self.athlete_id}/wellness/{date_str}")
        except IntervalsAPIError:
            return None

    def get_wellness_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch wellness metrics across a date range (YYYY-MM-DD)."""
        try:
            res = self._request(
                "GET",
                f"/athlete/{self.athlete_id}/wellness",
                query_params={"oldest": start_date, "newest": end_date},
            )
            return res if isinstance(res, list) else []
        except IntervalsAPIError:
            return []

    def get_sport_settings(self) -> List[Dict[str, Any]]:
        """Fetch athlete sport-specific settings (LTHR, max HR, FTP, pace zones)."""
        try:
            res = self._request("GET", f"/athlete/{self.athlete_id}/sport-settings")
            return res if isinstance(res, list) else []
        except IntervalsAPIError:
            return []

    def get_activities(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch completed activities in the date range."""
        try:
            res = self._request(
                "GET",
                f"/athlete/{self.athlete_id}/activities",
                query_params={"oldest": start_date, "newest": end_date},
            )
            return res if isinstance(res, list) else []
        except IntervalsAPIError:
            return []

    def update_wellness(self, date_str: str, wellness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update or create wellness metrics for a specific date (YYYY-MM-DD)."""
        return self._request("PUT", f"/athlete/{self.athlete_id}/wellness/{date_str}", data=wellness_data)

    def upload_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a completed activity record to Intervals.icu."""
        return self._request("POST", f"/athlete/{self.athlete_id}/activities", data=activity_data)

