"""
COROS Open API and Ecosystem Integration Client.
Handles direct COROS Open API interactions (if credentials are provided)
and integrates with the Intervals.icu native COROS cloud sync bridge.
"""

from dataclasses import dataclass
import json
import logging
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from intervals_plan.config import Config
from intervals_plan.intervals_client import IntervalsClient

logger = logging.getLogger(__name__)


@dataclass
class CorosSyncStatus:
    """Status of COROS integration across direct API, MCP server, and Intervals cloud sync."""

    connected: bool
    mode: str  # 'DIRECT_OPEN_API', 'INTERVALS_RELAY', 'MCP_SERVER', or 'NOT_CONFIGURED'
    user_id: Optional[str] = None
    upload_workouts: bool = False
    download_activities: bool = False
    download_wellness: bool = False
    last_cloud_push: Optional[str] = None
    direct_api_ready: bool = False
    mcp_endpoint: str = "https://mcp.coros.com/mcp"
    mcp_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "mode": self.mode,
            "user_id": self.user_id,
            "upload_workouts": self.upload_workouts,
            "download_activities": self.download_activities,
            "download_wellness": self.download_wellness,
            "last_cloud_push": self.last_cloud_push,
            "direct_api_ready": self.direct_api_ready,
            "mcp_endpoint": self.mcp_endpoint,
            "mcp_enabled": self.mcp_enabled,
        }


class CorosClient:
    """Manages communication with COROS Open API and Intervals.icu COROS bridge."""

    OPEN_API_BASE = "https://open.coros.com/v2"

    def __init__(
        self,
        access_token: Optional[str] = None,
        user_id: Optional[str] = None,
        base_url: Optional[str] = None,
        mcp_endpoint: Optional[str] = None,
    ):
        # Support passing Config object or direct strings
        if isinstance(access_token, Config):
            cfg = access_token
            self.access_token = getattr(cfg, "coros_access_token", None)
            self.user_id = getattr(cfg, "coros_user_id", None)
            self.base_url = (base_url or self.OPEN_API_BASE).rstrip("/")
        else:
            self.access_token = access_token
            self.user_id = user_id
            self.base_url = (base_url or self.OPEN_API_BASE).rstrip("/")
        self.mcp_endpoint = mcp_endpoint or "https://mcp.coros.com/mcp"

    @classmethod
    def from_config(cls, cfg: Config) -> "CorosClient":
        """Instantiate CorosClient from environment config."""
        token = getattr(cfg, "coros_access_token", None)
        uid = getattr(cfg, "coros_user_id", None)
        return cls(access_token=token, user_id=uid)

    def is_direct_api_ready(self) -> bool:
        """Check if direct COROS Open API token is present."""
        return bool(self.access_token and len(self.access_token) > 8)

    def check_status(self, intervals_client: Optional[IntervalsClient] = None) -> CorosSyncStatus:
        """Evaluate overall COROS connectivity including Intervals relay and MCP endpoint."""
        direct_ready = self.is_direct_api_ready()
        mcp_configured = bool(self.mcp_endpoint)
        
        # Check Intervals.icu native COROS cloud status if available
        if intervals_client and intervals_client.api_key:
            try:
                ath = intervals_client._request("GET", f"/athlete/{intervals_client.athlete_id}")
                user_id = ath.get("coros_user_id")
                if user_id:
                    return CorosSyncStatus(
                        connected=True,
                        mode="DIRECT_OPEN_API" if direct_ready else "INTERVALS_RELAY",
                        user_id=user_id,
                        upload_workouts=bool(ath.get("coros_upload_workouts")),
                        download_activities=bool(ath.get("coros_sync_activities")),
                        download_wellness=bool(ath.get("coros_download_wellness")),
                        last_cloud_push=ath.get("coros_last_upload"),
                        direct_api_ready=direct_ready,
                        mcp_endpoint=self.mcp_endpoint,
                        mcp_enabled=mcp_configured,
                    )
            except Exception as exc:
                logger.debug("Failed querying Intervals.icu for COROS status: %s", exc)

        if direct_ready:
            return CorosSyncStatus(
                connected=True,
                mode="DIRECT_OPEN_API",
                user_id=self.user_id,
                upload_workouts=True,
                download_activities=True,
                download_wellness=True,
                direct_api_ready=True,
                mcp_endpoint=self.mcp_endpoint,
                mcp_enabled=mcp_configured,
            )

        return CorosSyncStatus(
            connected=mcp_configured,
            mode="MCP_SERVER" if mcp_configured else "NOT_CONFIGURED",
            direct_api_ready=False,
            mcp_endpoint=self.mcp_endpoint,
            mcp_enabled=mcp_configured,
        )

    def upload_workout_direct(self, workout_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Upload workout to COROS via direct Open API if credentials exist."""
        if not self.is_direct_api_ready():
            return {"status": "skipped", "message": "Direct COROS Open API token not configured"}

        url = f"{self.base_url}/coros/workout/upload"
        headers = {
            "accessToken": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data_bytes = json.dumps(workout_payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body) if res_body else {"status": "success"}
        except urllib.error.HTTPError as err:
            err_msg = err.read().decode("utf-8") if err.fp else str(err)
            return {"status": "error", "code": err.code, "message": err_msg}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
