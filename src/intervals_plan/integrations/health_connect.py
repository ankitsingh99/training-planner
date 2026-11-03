"""
Health Connect Webhook Integration Engine.
Receives, parses, and synchronizes Samsung Health & Health Connect biometric data
(HRV, RHR, Sleep Stages, SpO2, Blood Pressure, Weight, Exercise Sessions)
and synchronizes it with Intervals.icu and COROS.
"""

from dataclasses import asdict, dataclass, field
import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import urllib.error
import urllib.parse
import urllib.request

from intervals_plan.audit import AuditLogger
from intervals_plan.config import Config
from intervals_plan.integrations.coros_client import CorosClient
from intervals_plan.intervals_client import IntervalsClient

logger = logging.getLogger(__name__)


@dataclass
class HealthConnectSyncResult:
    """Summary of Health Connect data processed and pushed."""

    timestamp: str
    source: str  # 'webhook' or 'lan_pull'
    dates_processed: List[str]
    wellness_records_updated: int
    activities_uploaded: int
    coros_synced: bool
    coros_mode: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HealthConnectParser:
    """Parses raw Health Connect JSON payloads into sports-science data models."""

    SPORT_MAP = {
        # String names
        "RUNNING": "Run",
        "RUN": "Run",
        "BIKING": "Ride",
        "CYCLING": "Ride",
        "ROAD_BIKING": "Ride",
        "MOUNTAIN_BIKING": "Ride",
        "SWIMMING": "Swim",
        "SWIMMING_POOL": "Swim",
        "SWIMMING_OPEN_WATER": "Swim",
        "WALKING": "Walk",
        "HIKING": "Walk",
        "WEIGHTLIFTING": "WeightTraining",
        "CALISTHENICS": "WeightTraining",
        "STRENGTH_TRAINING": "WeightTraining",
        "YOGA": "Yoga",
        "PILATES": "Yoga",
        "ROWING": "Rowing",
        "ELLIPTICAL": "Workout",
        # Android Health Connect / Google Fit numeric activity type codes
        "8": "Ride",  # Biking
        "56": "Run",  # Running
        "70": "Swim",  # Swimming
        "79": "Walk",  # Walking
        "80": "WeightTraining",  # Weightlifting
        "82": "Yoga",  # Yoga
    }

    @staticmethod
    def _extract_date(time_str: Optional[str]) -> Optional[str]:
        """Extract YYYY-MM-DD from ISO-8601 string."""
        if not time_str or len(time_str) < 10:
            return None
        return time_str[:10]

    def parse_wellness(
        self,
        payload: Dict[str, Any],
        include_steps: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate Health Connect data into date-indexed Intervals.icu wellness updates.
        Restricted to body vitals and health statistics (RHR, Sleep Stages, SpO2, Weight, Body Fat, VO2max).
        Steps are excluded by default to avoid contaminating pure watch/training telemetry.
        Returns: { 'YYYY-MM-DD': { 'restingHR': 52, 'hrv': 64.5, 'sleepSecs': 28800, ... } }
        """
        daily: Dict[str, Dict[str, Any]] = {}

        def get_day(dt: str) -> Dict[str, Any]:
            if dt not in daily:
                daily[dt] = {}
            return daily[dt]

        # 1. Resting Heart Rate
        for r in payload.get("resting_heart_rate", []):
            dt = self._extract_date(r.get("time"))
            bpm = r.get("bpm") or r.get("rate")
            if dt and bpm:
                get_day(dt)["restingHR"] = round(float(bpm))

        # 2. Heart Rate (if resting_heart_rate not provided, fallback to min HR observed that day)
        hr_by_date: Dict[str, List[float]] = {}
        for hr in payload.get("heart_rate", []):
            dt = self._extract_date(hr.get("time"))
            val = hr.get("min") or hr.get("bpm")
            if dt and val:
                hr_by_date.setdefault(dt, []).append(float(val))

        for dt, hr_vals in hr_by_date.items():
            day = get_day(dt)
            if "restingHR" not in day and hr_vals:
                day["restingHR"] = round(min(hr_vals))

        # 3. Heart Rate Variability (RMSSD in ms)
        for hrv in payload.get("heart_rate_variability", []):
            dt = self._extract_date(hrv.get("time"))
            val = hrv.get("rmssd_millis") or hrv.get("avg") or hrv.get("rmssd")
            if dt and val:
                get_day(dt)["hrv"] = round(float(val), 1)

        # 4. Sleep & Sleep Stages
        # Health Connect sleep stages: 1=Awake, 4=Light, 5=Deep, 6=REM
        for sl in payload.get("sleep", []):
            dt = self._extract_date(sl.get("session_end_time") or sl.get("start_time"))
            dur = sl.get("duration_seconds")
            if dt and dur:
                day = get_day(dt)
                day["sleepSecs"] = int(dur)
                stages = sl.get("stages", [])
                if stages:
                    deep_sec = sum(
                        s.get("duration_seconds", 0)
                        for s in stages
                        if "DEEP" in str(s.get("stage", "")).upper() or str(s.get("stage", "")).strip() == "5"
                    )
                    rem_sec = sum(
                        s.get("duration_seconds", 0)
                        for s in stages
                        if "REM" in str(s.get("stage", "")).upper() or str(s.get("stage", "")).strip() == "6"
                    )
                    light_sec = sum(
                        s.get("duration_seconds", 0)
                        for s in stages
                        if "LIGHT" in str(s.get("stage", "")).upper() or str(s.get("stage", "")).strip() == "4"
                    )
                    awake_sec = sum(
                        s.get("duration_seconds", 0)
                        for s in stages
                        if "AWAKE" in str(s.get("stage", "")).upper() or str(s.get("stage", "")).strip() == "1"
                    )
                    total_hrs = dur / 3600.0
                    deep_hrs = deep_sec / 3600.0
                    rem_hrs = rem_sec / 3600.0
                    light_hrs = light_sec / 3600.0
                    day["comments"] = f"Samsung Health Sleep: {total_hrs:.1f}h total ({deep_hrs:.1f}h Deep, {rem_hrs:.1f}h REM, {light_hrs:.1f}h Light)"

        # 5. Weight & Body Composition
        for w in payload.get("weight", []):
            dt = self._extract_date(w.get("time"))
            kg = w.get("kilograms") or w.get("weight_kg") or w.get("kg") or w.get("weight")
            if dt and kg:
                get_day(dt)["weight"] = round(float(kg), 2)

        for bf in payload.get("body_fat", []):
            dt = self._extract_date(bf.get("time"))
            pct = bf.get("percentage") or bf.get("body_fat_pct")
            if dt and pct:
                get_day(dt)["bodyFat"] = round(float(pct), 1)

        # 5b. VO2 Max
        for vm in payload.get("vo2_max", []):
            dt = self._extract_date(vm.get("time"))
            vo2 = vm.get("ml_per_kg_per_min") or vm.get("vo2_max") or vm.get("value")
            if dt and vo2:
                get_day(dt)["vo2max"] = round(float(vo2), 1)

        # 6. Blood Pressure
        for bp in payload.get("blood_pressure", []):
            dt = self._extract_date(bp.get("time"))
            sys = bp.get("systolic_mmhg") or bp.get("systolic")
            dia = bp.get("diastolic_mmhg") or bp.get("diastolic")
            if dt and sys and dia:
                day = get_day(dt)
                day["systolic"] = round(float(sys))
                day["diastolic"] = round(float(dia))

        # 7. Blood Oxygen Saturation (SpO2)
        for ox in payload.get("oxygen_saturation", []):
            dt = self._extract_date(ox.get("time"))
            pct = ox.get("percentage") or ox.get("avg")
            if dt and pct:
                get_day(dt)["spO2"] = round(float(pct), 1)

        # 8. Respiratory Rate
        for rr in payload.get("respiratory_rate", []):
            dt = self._extract_date(rr.get("time"))
            rate = rr.get("rate") or rr.get("avg")
            if dt and rate:
                get_day(dt)["respiration"] = round(float(rate), 1)

        # 9. Blood Glucose
        for bg in payload.get("blood_glucose", []):
            dt = self._extract_date(bg.get("time"))
            lvl = bg.get("level_milligrams_per_deciliter") or bg.get("level")
            if dt and lvl:
                get_day(dt)["bloodGlucose"] = round(float(lvl), 1)

        # 10. Hydration
        for hy in payload.get("hydration", []):
            dt = self._extract_date(hy.get("time"))
            liters = hy.get("volume_liters") or (float(hy.get("volume_milliliters", 0)) / 1000.0)
            if dt and liters:
                day = get_day(dt)
                day["hydration"] = round(day.get("hydration", 0.0) + float(liters), 2)

        # 11. Nutrition
        for nu in payload.get("nutrition", []):
            dt = self._extract_date(nu.get("time"))
            kcal = nu.get("calories") or nu.get("energy_kcal")
            if dt and kcal:
                day = get_day(dt)
                day["kcalConsumed"] = round(day.get("kcalConsumed", 0.0) + float(kcal))

        # 12. Steps Daily Sum (Only included if explicitly enabled)
        if include_steps:
            for st in payload.get("steps", []):
                dt = self._extract_date(st.get("start_time") or st.get("time"))
                cnt = st.get("count") or 0
                if dt and cnt:
                    day = get_day(dt)
                    day["steps"] = int(day.get("steps", 0) + int(cnt))

        return daily

    def parse_activities(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse exercise sessions into Intervals.icu activity format.
        Supports both 'exercise_sessions' and 'exercise' keys.
        """
        acts: List[Dict[str, Any]] = []
        raw_exercises = payload.get("exercise_sessions") or payload.get("exercise") or []
        for ex in raw_exercises:
            start = ex.get("start_time")
            if not start:
                continue

            ex_type = str(ex.get("exercise_type") or ex.get("type") or "").strip().upper()
            sport = self.SPORT_MAP.get(ex_type, "Workout")

            title_val = ex.get("title") or ""
            title_lower = title_val.lower()
            if any(w in title_lower for w in ["legs", "strength", "weight", "gym", "chest", "back", "workout"]):
                sport = "WeightTraining"
            elif any(w in title_lower for w in ["swim", "pool"]):
                sport = "Swim"
            elif any(w in title_lower for w in ["run", "jog"]):
                sport = "Run"
            elif any(w in title_lower for w in ["ride", "bike", "cycle"]):
                sport = "Ride"

            dur = int(ex.get("duration_seconds") or 0)
            if dur <= 0 and ex.get("end_time"):
                try:
                    t1 = datetime.datetime.fromisoformat(ex["start_time"].replace("Z", "+00:00"))
                    t2 = datetime.datetime.fromisoformat(ex["end_time"].replace("Z", "+00:00"))
                    dur = int((t2 - t1).total_seconds())
                except Exception:
                    dur = 1800

            dist = float(ex.get("distance_meters") or 0.0)
            cals = float(ex.get("calories_burned") or ex.get("active_calories") or 0.0)
            title = title_val or f"Samsung Health {sport}"

            # Calculate estimated training load if duration is available
            est_load = round((dur / 3600.0) * 50.0, 1) if dur > 0 else 25.0

            act_dict = {
                "start_date_local": start[:19],
                "name": title,
                "type": sport,
                "moving_time": dur,
                "elapsed_time": dur,
                "distance": round(dist, 1),
                "icu_training_load": est_load,
                "description": f"Source: Samsung Health / Health Connect | Calories: {cals:.0f} kcal",
            }
            acts.append(act_dict)

        return acts


class HealthConnectClient:
    """Client for pulling Health Connect data from phone's local HTTP server."""

    @staticmethod
    def fetch_lan(
        phone_ip: str,
        port: int = 8787,
        days: int = 7,
        timeout: int = 20,
        auth_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch health data directly from HC Webhook local HTTP server on LAN."""
        url = f"http://{phone_ip}:{port}/?days={days}"
        headers = {"Accept": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.URLError as exc:
            logger.error("Failed to connect to phone at %s: %s", url, exc)
            raise ConnectionError(f"Could not connect to Health Connect server at {url}: {exc}") from exc


class HealthConnectSyncManager:
    """Coordinates receiving Health Connect data and pushing to Intervals.icu + COROS."""

    STATE_FILE = Path("data/health_connect_sync.json")

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or Config.load()
        self.parser = HealthConnectParser()
        self.audit = AuditLogger(Path(self.cfg.data_dir) / "audit.log")

    def sync_payload(
        self,
        payload: Dict[str, Any],
        source: str = "webhook",
        dry_run: bool = False,
        sync_activities: bool = False,
        include_steps: bool = False,
    ) -> HealthConnectSyncResult:
        """
        Process incoming Health Connect JSON payload and sync to Intervals.icu and COROS.
        By default, only body vitals and health statistics are synced (no activities, no steps).
        """
        daily_wellness = self.parser.parse_wellness(payload, include_steps=include_steps)
        activities = self.parser.parse_activities(payload) if sync_activities else []

        dates_processed = sorted(daily_wellness.keys())
        wellness_count = 0
        acts_count = 0

        intervals_client = None
        if self.cfg.api_key and len(self.cfg.api_key) > 5:
            intervals_client = IntervalsClient(
                api_key=self.cfg.api_key,
                athlete_id=self.cfg.athlete_id,
                base_url=self.cfg.base_url,
            )

        # 1. Update Intervals.icu Wellness (Body Vitals and Health Stats only)
        if intervals_client and not dry_run:
            for dt, w_data in daily_wellness.items():
                try:
                    intervals_client.update_wellness(dt, w_data)
                    wellness_count += 1
                except Exception as exc:
                    logger.warning("Failed updating wellness for %s: %s", dt, exc)
        else:
            wellness_count = len(daily_wellness)

        # 2. Upload Activities (Only if sync_activities is explicitly requested)
        if intervals_client and not dry_run and sync_activities:
            for act in activities:
                try:
                    intervals_client.upload_activity(act)
                    acts_count += 1
                except Exception as exc:
                    logger.warning("Failed uploading activity: %s", exc)
        else:
            acts_count = len(activities)

        # 3. Check COROS Cloud Status
        coros_client = CorosClient.from_config(self.cfg)
        coros_status = coros_client.check_status(intervals_client)

        now_iso = datetime.datetime.now().isoformat()
        result = HealthConnectSyncResult(
            timestamp=now_iso,
            source=source,
            dates_processed=dates_processed,
            wellness_records_updated=wellness_count,
            activities_uploaded=acts_count,
            coros_synced=coros_status.connected,
            coros_mode=coros_status.mode,
            details={
                "dry_run": dry_run,
                "intervals_connected": bool(intervals_client is not None),
                "coros_user_id": coros_status.user_id,
                "coros_upload_workouts": coros_status.upload_workouts,
                "coros_download_wellness": coros_status.download_wellness,
                "coros_direct_ready": coros_status.direct_api_ready,
                "sample_wellness": {k: daily_wellness[k] for k in list(daily_wellness.keys())[:2]},
            },
        )

        # Log audit entry
        self.audit.log(
            action="HEALTH_CONNECT_SYNC",
            target_ids=dates_processed,
            status="dry_run" if dry_run else "success",
            details={
                "source": source,
                "wellness_count": wellness_count,
                "activities_count": acts_count,
                "coros_mode": coros_status.mode,
            },
        )

        # Persist last sync state
        self._save_state(result.to_dict())
        return result

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save latest sync state to data/health_connect_sync.json."""
        try:
            self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.debug("Failed saving Health Connect sync state: %s", exc)

    def load_last_state(self) -> Optional[Dict[str, Any]]:
        """Load last sync state if present."""
        if self.STATE_FILE.exists():
            try:
                return json.loads(self.STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None
