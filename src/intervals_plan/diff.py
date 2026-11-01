"""
Diff engine: compares desired plan events with live Intervals.icu events.
"""

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple
from intervals_plan.api_models import IntervalsEvent


def compute_event_hash(event: IntervalsEvent) -> str:
    """Generate a stable deterministic hash of the event's functional contents."""
    norm = {
        "start_date_local": event.start_date_local,
        "name": event.name,
        "category": event.category,
        "type": event.type,
        "moving_time": event.moving_time,
        "description": event.description,
        "workout_doc": event.workout_doc.to_dict() if event.workout_doc else None,
    }
    raw = json.dumps(norm, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class EventDiff:
    event: IntervalsEvent
    existing_event: Optional[IntervalsEvent] = None
    changes: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    is_conflict: bool = False
    conflict_reason: str = ""


@dataclass
class PlanDiff:
    to_create: List[IntervalsEvent] = field(default_factory=list)
    to_update: List[EventDiff] = field(default_factory=list)
    to_delete: List[IntervalsEvent] = field(default_factory=list)
    unchanged: List[IntervalsEvent] = field(default_factory=list)
    conflicts: List[EventDiff] = field(default_factory=list)

    @property
    def has_mutations(self) -> bool:
        return bool(self.to_create or self.to_update or self.to_delete)

    def summary(self) -> str:
        lines = [
            f"Plan Diff Summary:",
            f"  - To Create:  {len(self.to_create)}",
            f"  - To Update:  {len(self.to_update)}",
            f"  - To Delete:  {len(self.to_delete)}",
            f"  - Unchanged:  {len(self.unchanged)}",
            f"  - Conflicts:  {len(self.conflicts)}",
        ]
        return "\n".join(lines)


def calculate_diff(
    desired_events: List[IntervalsEvent],
    live_events: List[IntervalsEvent],
    manifest: Optional[Dict[str, Any]] = None,
    managed_prefix: str = "",
) -> PlanDiff:
    """Compute difference between desired plan events and live calendar events."""
    manifest_records = (manifest or {}).get("records", {})
    live_by_ext_id = {e.external_id: e for e in live_events if e.external_id}

    diff = PlanDiff()

    for desired in desired_events:
        ext_id = desired.external_id
        if not ext_id:
            diff.to_create.append(desired)
            continue

        if ext_id not in live_by_ext_id:
            diff.to_create.append(desired)
            continue

        live = live_by_ext_id[ext_id]
        desired_hash = compute_event_hash(desired)
        live_hash = compute_event_hash(live)

        if desired_hash == live_hash:
            diff.unchanged.append(desired)
            continue

        # Check for conflict against manifest
        manifest_record = manifest_records.get(ext_id)
        is_conflict = False
        conflict_msg = ""
        if manifest_record and manifest_record.get("last_known_hash"):
            last_hash = manifest_record["last_known_hash"]
            if live_hash != last_hash and live_hash != desired_hash:
                is_conflict = True
                conflict_msg = (
                    f"Event '{live.name}' was modified directly on Intervals.icu since last sync!"
                )

        # Detect specific field changes
        changes: Dict[str, Tuple[Any, Any]] = {}
        if desired.start_date_local != live.start_date_local:
            changes["start_date_local"] = (live.start_date_local, desired.start_date_local)
        if desired.name != live.name:
            changes["name"] = (live.name, desired.name)
        if desired.moving_time != live.moving_time:
            changes["moving_time"] = (live.moving_time, desired.moving_time)
        if desired.description != live.description:
            changes["description"] = (live.description, desired.description)

        event_diff = EventDiff(
            event=desired,
            existing_event=live,
            changes=changes,
            is_conflict=is_conflict,
            conflict_reason=conflict_msg,
        )

        if is_conflict:
            diff.conflicts.append(event_diff)
        else:
            diff.to_update.append(event_diff)

    return diff

