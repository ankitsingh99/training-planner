"""
Garmin Connect and Ecosystem Integration Client.
Handles direct Garmin Connect API interactions, Garmin FIT workout generation,
and synchronization with the Intervals.icu native Garmin Health & Training bridge.
"""

from dataclasses import asdict, dataclass, field
import datetime
import json
import logging
from pathlib import Path
import struct
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from intervals_plan.api_models import IntervalsEvent, WorkoutDoc, WorkoutStep
from intervals_plan.config import Config
from intervals_plan.intervals_client import IntervalsClient

logger = logging.getLogger(__name__)


@dataclass
class GarminSyncStatus:
    """Status of Garmin Connect integration across direct API and Intervals cloud sync."""

    connected: bool
    mode: str  # 'DIRECT_CONNECT_API', 'INTERVALS_RELAY', or 'NOT_CONFIGURED'
    user_id: Optional[str] = None
    upload_workouts: bool = False
    download_activities: bool = False
    download_wellness: bool = False
    body_battery_enabled: bool = False
    last_cloud_push: Optional[str] = None
    direct_api_ready: bool = False
    power_target_mode: str = "POWER_LAP"
    hr_range_pct: float = 1.5
    pace_range_pct: float = 2.5
    device_names: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GarminClient:
    """Manages Garmin Connect API, FIT workout compilation, and Intervals.icu Garmin relay."""

    GARMIN_CONNECT_BASE = "https://connectapi.garmin.com"

    CRC_TABLE = [
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]

    SPORT_MAP = {
        "Run": {"id": 1, "key": "running", "fit_sport": 1},
        "Ride": {"id": 2, "key": "cycling", "fit_sport": 2},
        "Swim": {"id": 5, "key": "swimming", "fit_sport": 5},
        "WeightTraining": {"id": 4, "key": "training", "fit_sport": 10},
        "Strength": {"id": 4, "key": "training", "fit_sport": 10},
        "Walk": {"id": 3, "key": "walking", "fit_sport": 11},
        "Other": {"id": 0, "key": "generic", "fit_sport": 0},
    }

    def __init__(
        self,
        access_token: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        user_id: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.access_token = access_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user_id = user_id
        self.base_url = (base_url or self.GARMIN_CONNECT_BASE).rstrip("/")

    @classmethod
    def from_config(cls, cfg: Config) -> "GarminClient":
        """Instantiate GarminClient from environment configuration."""
        token = getattr(cfg, "garmin_access_token", None)
        key = getattr(cfg, "garmin_consumer_key", None)
        sec = getattr(cfg, "garmin_consumer_secret", None)
        uid = getattr(cfg, "garmin_user_id", None)
        return cls(
            access_token=token,
            consumer_key=key,
            consumer_secret=sec,
            user_id=uid,
        )

    def is_direct_api_ready(self) -> bool:
        """Check if direct Garmin Connect API credentials are configured."""
        return bool(self.access_token and len(self.access_token) > 8)

    def check_status(self, intervals_client: Optional[IntervalsClient] = None) -> GarminSyncStatus:
        """
        Evaluate Garmin connectivity across Intervals.icu relay and direct API.
        """
        direct_ready = self.is_direct_api_ready()

        if intervals_client and intervals_client.api_key:
            try:
                ath = intervals_client._request("GET", f"/athlete/{intervals_client.athlete_id}")
                has_health = bool(ath.get("icu_garmin_health"))
                has_training = bool(ath.get("icu_garmin_training"))
                upload_workouts = bool(ath.get("icu_garmin_upload_workouts"))
                download_acts = bool(ath.get("icu_garmin_sync_activities"))
                download_well = bool(ath.get("icu_garmin_download_wellness"))

                if has_health or has_training or upload_workouts or download_acts:
                    return GarminSyncStatus(
                        connected=True,
                        mode="DIRECT_CONNECT_API" if direct_ready else "INTERVALS_GARMIN_RELAY",
                        user_id=str(ath.get("id", intervals_client.athlete_id)),
                        upload_workouts=upload_workouts,
                        download_activities=download_acts,
                        download_wellness=download_well,
                        body_battery_enabled=download_well,
                        last_cloud_push=ath.get("icu_garmin_last_upload"),
                        direct_api_ready=direct_ready,
                        power_target_mode=ath.get("garmin_power_target") or "POWER_LAP",
                        hr_range_pct=float(ath.get("icu_garmin_hr_range") or 1.5),
                        pace_range_pct=float(ath.get("garmin_pace_range") or 2.5),
                        device_names=["Garmin Forerunner", "Garmin Edge / Fenix"],
                    )
            except Exception as exc:
                logger.debug("Failed checking Intervals Garmin status: %s", exc)

        if direct_ready:
            return GarminSyncStatus(
                connected=True,
                mode="DIRECT_CONNECT_API",
                user_id=self.user_id,
                upload_workouts=True,
                download_activities=True,
                download_wellness=True,
                body_battery_enabled=True,
                direct_api_ready=True,
                device_names=["Garmin Connect Device"],
            )

        return GarminSyncStatus(
            connected=False,
            mode="NOT_CONFIGURED",
            direct_api_ready=False,
        )

    def enable_intervals_relay(
        self,
        intervals_client: IntervalsClient,
        upload_workouts: bool = True,
        download_wellness: bool = True,
    ) -> Dict[str, Any]:
        """Enable Garmin auto-push and wellness sync on the athlete's Intervals profile."""
        payload = {
            "icu_garmin_upload_workouts": upload_workouts,
            "icu_garmin_download_wellness": download_wellness,
        }
        try:
            res = intervals_client._request(
                "PUT",
                f"/athlete/{intervals_client.athlete_id}",
                data=json.dumps(payload),
            )
            return {"status": "success", "athlete_id": intervals_client.athlete_id, "updated": payload}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def convert_event_to_garmin_json(self, event: IntervalsEvent) -> Dict[str, Any]:
        """
        Convert an IntervalsEvent into a standard Garmin Connect Workout JSON object.
        """
        sport_info = self.SPORT_MAP.get(event.type, self.SPORT_MAP["Other"])
        workout_name = (event.name or "AdaptPulse Workout")[:30]
        desc = (event.description or "")[:250]

        steps: List[Dict[str, Any]] = []
        step_order = 1

        if event.workout_doc and event.workout_doc.steps:
            for s in event.workout_doc.steps:
                cue_val = getattr(s, "cue", None) or getattr(s, "text", "") or ""
                cue_lower = cue_val.lower()
                step_type_key = "interval"
                step_type_id = 3
                if "warm" in cue_lower:
                    step_type_key = "warmup"
                    step_type_id = 1
                elif "cool" in cue_lower:
                    step_type_key = "cooldown"
                    step_type_id = 2
                elif "rest" in cue_lower or "recov" in cue_lower:
                    step_type_key = "recovery"
                    step_type_id = 4

                dur = getattr(s, "duration", None) or getattr(s, "duration_seconds", None) or 300
                target_type = {"targetTypeId": 1, "targetTypeKey": "no.target"}
                val_one: Optional[float] = None
                val_two: Optional[float] = None

                pwr = getattr(s, "power", None)
                if isinstance(pwr, dict) and pwr.get("start") is not None:
                    target_type = {"targetTypeId": 2, "targetTypeKey": "power.zone"}
                    val_one = float(pwr["start"])
                    val_two = float(pwr.get("end") or pwr["start"])
                elif hasattr(pwr, "start") and pwr.start is not None:
                    target_type = {"targetTypeId": 2, "targetTypeKey": "power.zone"}
                    val_one = float(pwr.start)
                    val_two = float(getattr(pwr, "end", pwr.start) or pwr.start)

                hr_obj = getattr(s, "hr", None)
                if val_one is None:
                    if isinstance(hr_obj, dict) and hr_obj.get("start") is not None:
                        target_type = {"targetTypeId": 4, "targetTypeKey": "heart.rate.zone"}
                        val_one = float(hr_obj["start"])
                        val_two = float(hr_obj.get("end") or hr_obj["start"])
                    elif hasattr(hr_obj, "start") and hr_obj.start is not None:
                        target_type = {"targetTypeId": 4, "targetTypeKey": "heart.rate.zone"}
                        val_one = float(hr_obj.start)
                        val_two = float(getattr(hr_obj, "end", hr_obj.start) or hr_obj.start)

                step_obj = {
                    "type": "WorkoutStep",
                    "stepId": step_order,
                    "stepOrder": step_order,
                    "description": cue_val,
                    "stepType": {"stepTypeId": step_type_id, "stepTypeKey": step_type_key},
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                    "endConditionValue": dur,
                    "targetType": target_type,
                }
                if val_one is not None:
                    step_obj["targetValueOne"] = val_one
                if val_two is not None:
                    step_obj["targetValueTwo"] = val_two

                steps.append(step_obj)
                step_order += 1
        else:
            dur = event.moving_time if event.moving_time else 2700
            steps.append({
                "type": "WorkoutStep",
                "stepId": 1,
                "stepOrder": 1,
                "description": workout_name,
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": dur,
                "targetType": {"targetTypeId": 1, "targetTypeKey": "no.target"},
            })

        total_secs = sum(int(st.get("endConditionValue", 0)) for st in steps)

        return {
            "workoutName": workout_name,
            "description": desc,
            "sportType": {"sportTypeId": sport_info["id"], "sportTypeKey": sport_info["key"]},
            "subSportType": None,
            "estimatedDurationInSecs": total_secs,
            "workoutSegments": [
                {
                    "segmentOrder": 1,
                    "sportType": {"sportTypeId": sport_info["id"], "sportTypeKey": sport_info["key"]},
                    "workoutSteps": steps,
                }
            ],
        }

    def _compute_fit_crc(self, data: bytes) -> int:
        """Compute 16-bit CRC for FIT protocol frames."""
        crc = 0
        for byte in data:
            tmp = self.CRC_TABLE[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ self.CRC_TABLE[byte & 0xF]
            tmp = self.CRC_TABLE[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ self.CRC_TABLE[(byte >> 4) & 0xF]
        return crc & 0xFFFF

    def generate_fit_workout(self, event: IntervalsEvent) -> bytes:
        """
        Compile an IntervalsEvent into a binary Garmin .FIT workout file.
        Fully compatible with Garmin devices (GARMIN/NEWFILES or GARMIN/WORKOUTS).
        """
        sport_info = self.SPORT_MAP.get(event.type, self.SPORT_MAP["Other"])
        fit_sport = sport_info["fit_sport"]
        workout_name = (event.name or "AdaptPulse Workout")[:16].encode("ascii", "ignore")

        # FIT Epoch: Dec 31 1989 00:00:00 UTC
        fit_epoch = datetime.datetime(1989, 12, 31, 0, 0, 0, tzinfo=datetime.timezone.utc)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        fit_timestamp = int((now_utc - fit_epoch).total_seconds())

        records = bytearray()

        # 1. Definition Message 0: File ID (Global Mesg Num 0)
        # Fields: type (uint8=5 for workout), manufacturer (uint16=1 for garmin), time_created (uint32)
        records.append(0x40)  # Definition record, local mesg 0
        records.append(0x00)  # Reserved
        records.append(0x00)  # Architecture: Little Endian
        records.extend(struct.pack("<H", 0))  # Global Mesg Num: File ID (0)
        records.append(3)     # Number of fields
        # Field 1: type (Field Num 0, 1 byte, enum uint8)
        records.extend([0, 1, 0x00])
        # Field 2: manufacturer (Field Num 1, 2 bytes, uint16)
        records.extend([1, 2, 0x84])
        # Field 3: time_created (Field Num 4, 4 bytes, uint32)
        records.extend([4, 4, 0x86])

        # Data Message 0: File ID Data
        records.append(0x00)  # Data record, local mesg 0
        records.append(0x05)  # Workout File Type (5)
        records.extend(struct.pack("<H", 1))           # Manufacturer: Garmin (1)
        records.extend(struct.pack("<I", fit_timestamp)) # Timestamp

        # 2. Definition Message 1: Workout Message (Global Mesg Num 26)
        # Fields: sport (uint8), capabilities (uint32), num_valid_steps (uint16), wkt_name (16 bytes string)
        records.append(0x41)  # Definition record, local mesg 1
        records.append(0x00)
        records.append(0x00)
        records.extend(struct.pack("<H", 26))  # Global Mesg Num: Workout (26)
        records.append(4)     # Number of fields
        # Field 1: sport (Field Num 4, 1 byte, enum)
        records.extend([4, 1, 0x00])
        # Field 2: capabilities (Field Num 5, 4 bytes, uint32z)
        records.extend([5, 4, 0x8c])
        # Field 3: num_valid_steps (Field Num 6, 2 bytes, uint16)
        records.extend([6, 2, 0x84])
        # Field 4: wkt_name (Field Num 8, 16 bytes, string)
        records.extend([8, 16, 0x07])

        # Compute steps count
        steps = (event.workout_doc.steps if event.workout_doc and event.workout_doc.steps else [])
        num_steps = max(1, len(steps))

        # Data Message 1: Workout Data
        padded_name = workout_name.ljust(16, b"\x00")[:16]
        records.append(0x01)  # Data record, local mesg 1
        records.append(fit_sport)
        records.extend(struct.pack("<I", 0x00000020))  # Capabilities (custom workout)
        records.extend(struct.pack("<H", num_steps))
        records.extend(padded_name)

        # 3. Definition Message 2: Workout Step Message (Global Mesg Num 27)
        # Fields: message_index (uint16), duration_type (uint8), duration_value (uint32), target_type (uint8), target_value (uint32)
        records.append(0x42)  # Definition record, local mesg 2
        records.append(0x00)
        records.append(0x00)
        records.extend(struct.pack("<H", 27))  # Global Mesg Num: Workout Step (27)
        records.append(5)     # Number of fields
        # Field 1: message_index (Field Num 254, 2 bytes, uint16)
        records.extend([254, 2, 0x84])
        # Field 2: duration_type (Field Num 1, 1 byte, enum)
        records.extend([1, 1, 0x00])
        # Field 3: duration_value (Field Num 2, 4 bytes, uint32)
        records.extend([2, 4, 0x86])
        # Field 4: target_type (Field Num 3, 1 byte, enum)
        records.extend([3, 1, 0x00])
        # Field 5: target_value (Field Num 4, 4 bytes, uint32)
        records.extend([4, 4, 0x86])

        # Data Messages 2: Workout Steps
        if steps:
            for idx, s in enumerate(steps):
                dur_val = getattr(s, "duration", None) or getattr(s, "duration_seconds", None) or 300
                dur_ms = int(dur_val * 1000)
                # Target: power watts or hr bpm
                target_val = 0
                target_type = 0  # 0: open / no target
                pwr = getattr(s, "power", None)
                if isinstance(pwr, dict) and pwr.get("start") is not None:
                    target_type = 1
                    target_val = int(float(pwr["start"]) + 1000)
                elif hasattr(pwr, "start") and pwr.start is not None:
                    target_type = 1
                    target_val = int(float(pwr.start) + 1000)

                hr_obj = getattr(s, "hr", None)
                if target_type == 0:
                    if isinstance(hr_obj, dict) and hr_obj.get("start") is not None:
                        target_type = 4
                        target_val = int(float(hr_obj["start"]) + 100)
                    elif hasattr(hr_obj, "start") and hr_obj.start is not None:
                        target_type = 4
                        target_val = int(float(hr_obj.start) + 100)

                records.append(0x02)  # Data record, local mesg 2
                records.extend(struct.pack("<H", idx))
                records.append(0)     # duration_type = 0 (time)
                records.extend(struct.pack("<I", dur_ms))
                records.append(target_type)
                records.extend(struct.pack("<I", target_val))
        else:
            default_dur_ms = int((event.moving_time or 2700) * 1000)
            records.append(0x02)
            records.extend(struct.pack("<H", 0))
            records.append(0)
            records.extend(struct.pack("<I", default_dur_ms))
            records.append(0)
            records.extend(struct.pack("<I", 0))

        # 4. Header (14 bytes)
        data_size = len(records)
        header_base = bytearray([
            14,          # Header size
            0x20,        # Protocol version: FIT 2.0
            0x70, 0x08,  # Profile version: 21.60
        ])
        header_base.extend(struct.pack("<I", data_size))
        header_base.extend(b".FIT")
        header_crc = self._compute_fit_crc(header_base)
        header_base.extend(struct.pack("<H", header_crc))

        # 5. File CRC (2 bytes over all records)
        data_crc = self._compute_fit_crc(records)

        return bytes(header_base + records + struct.pack("<H", data_crc))

    def upload_workout_direct(self, workout_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Upload workout to Garmin Connect via direct API if credentials exist."""
        if not self.is_direct_api_ready():
            return {
                "status": "skipped",
                "message": "Direct Garmin Connect API token not configured",
            }

        url = f"{self.base_url}/workout-service/workout"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
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
