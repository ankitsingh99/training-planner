"""
Multi-Platform Workout & Training Plan Exporters.
Exports scheduled workouts to:
- Zwift Workout Format (.zwo XML)
- iCalendar (.ics) for Google Calendar, Apple Calendar, and Outlook
- JSON summary for third-party platforms
"""

import datetime
import html
import json
import pathlib
from typing import Any, Dict, List, Optional
import uuid

from intervals_plan.api_models import IntervalsEvent, WorkoutDoc, WorkoutStep


class PlanExporter:
    """Exports planned workouts to various industry-standard formats."""

    @staticmethod
    def event_to_zwo(event: IntervalsEvent) -> Optional[str]:
        """
        Convert a cycling IntervalsEvent to Zwift .zwo XML.
        Returns XML string, or None if the event is not a bike workout.
        """
        if event.type != "Ride":
            return None

        doc = event.workout_doc
        name_esc = html.escape(event.name or "Workout")
        desc_esc = html.escape(event.description or "")

        lines = [
            '<workout_file>',
            '  <author>AdaptPulse</author>',
            f'  <name>{name_esc}</name>',
            f'  <description>{desc_esc}</description>',
            '  <sportType>bike</sportType>',
            '  <tags>',
            '    <tag name="Intervals"/>',
            '    <tag name="AdaptPulse"/>',
            '  </tags>',
            '  <workout>',
        ]

        if doc and doc.steps:
            for step in doc.steps:
                dur = step.duration or 300
                power_dict = step.power or {}
                # Default power target in fractional FTP (e.g. 0.70)
                p_start = power_dict.get("start", 65.0)
                p_end = power_dict.get("end", p_start)
                units = power_dict.get("units", "%")

                # Normalize to 0.0 - 1.5 range (fraction of FTP)
                val_start = (p_start / 100.0) if units == "%" else min(1.5, max(0.4, p_start / 250.0))
                val_end = (p_end / 100.0) if units == "%" else min(1.5, max(0.4, p_end / 250.0))

                stype = (step.text or "step").lower()
                cue_esc = html.escape(step.text or "")

                if "warm" in stype:
                    lines.append(
                        f'    <Warmup Duration="{dur}" PowerLow="{val_start:.2f}" PowerHigh="{val_end:.2f}">'
                        f'<textevent timeoffset="0" message="{cue_esc}"/></Warmup>'
                    )
                elif "cool" in stype:
                    lines.append(
                        f'    <Cooldown Duration="{dur}" PowerLow="{val_start:.2f}" PowerHigh="{val_end:.2f}">'
                        f'<textevent timeoffset="0" message="{cue_esc}"/></Cooldown>'
                    )
                elif "interval" in stype or "work" in stype:
                    lines.append(
                        f'    <SteadyState Duration="{dur}" Power="{val_start:.2f}" PowerLow="{val_start:.2f}" PowerHigh="{val_end:.2f}">'
                        f'<textevent timeoffset="0" message="{cue_esc}"/></SteadyState>'
                    )
                elif "recovery" in stype or "rest" in stype:
                    lines.append(
                        f'    <SteadyState Duration="{dur}" Power="{min(val_start, 0.55):.2f}">'
                        f'<textevent timeoffset="0" message="{cue_esc}"/></SteadyState>'
                    )
                else:
                    lines.append(
                        f'    <SteadyState Duration="{dur}" Power="{val_start:.2f}">'
                        f'<textevent timeoffset="0" message="{cue_esc}"/></SteadyState>'
                    )
        else:
            # Fallback duration
            lines.append('    <SteadyState Duration="2400" Power="0.65"/>')

        lines.append('  </workout>')
        lines.append('</workout_file>')
        return "\n".join(lines)

    @staticmethod
    def events_to_ics(events: List[IntervalsEvent], cal_name: str = "AdaptPulse Training Plan") -> str:
        """
        Convert a list of IntervalsEvent objects to standard iCalendar (.ics) format (RFC 5545).
        Compatible with Google Calendar, Apple Calendar, and Microsoft Outlook.
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//AdaptPulse//Endurance Training Planner//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:{cal_name}",
        ]

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        for event in events:
            dt_raw = event.start_date_local
            if not dt_raw:
                continue

            try:
                # Parse ISO date local
                clean_dt = dt_raw.replace("-", "").replace(":", "")
                if "T" in clean_dt:
                    dt_start_str = clean_dt[:15]
                else:
                    dt_start_str = clean_dt[:8] + "T070000"

                # Calculate duration or default to 1 hour
                dur_secs = 3600
                if event.workout_doc and event.workout_doc.steps:
                    dur_secs = sum(s.duration or 0 for s in event.workout_doc.steps) or 3600

                # End time
                start_obj = datetime.datetime.fromisoformat(dt_raw)
                end_obj = start_obj + datetime.timedelta(seconds=dur_secs)
                dt_end_str = end_obj.strftime("%Y%m%dT%H%M%S")

            except Exception:
                continue

            uid = event.external_id or str(uuid.uuid4())
            summary = event.name or "Workout"
            description = (event.description or "").replace("\n", "\\n")
            cat = event.type or "Training"

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}@adaptpulse.local",
                f"DTSTAMP:{now_str}",
                f"DTSTART:{dt_start_str}",
                f"DTEND:{dt_end_str}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                f"CATEGORIES:{cat}",
                "STATUS:CONFIRMED",
                "END:VEVENT",
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    @staticmethod
    def events_to_json(events: List[IntervalsEvent]) -> str:
        """Export events list as structured JSON."""
        data = [e.to_dict() for e in events]
        return json.dumps(data, indent=2)

    @staticmethod
    def event_to_garmin_fit(event: IntervalsEvent) -> bytes:
        """
        Compile an IntervalsEvent into a Garmin binary .fit workout file.
        Compatible with Garmin Edge, Forerunner, and Fenix via GARMIN/NEWFILES.
        """
        from intervals_plan.integrations.garmin_client import GarminClient
        client = GarminClient()
        return client.generate_fit_workout(event)

    @staticmethod
    def event_to_garmin_json(event: IntervalsEvent) -> Dict[str, Any]:
        """Convert an IntervalsEvent into a Garmin Connect Workout JSON object."""
        from intervals_plan.integrations.garmin_client import GarminClient
        client = GarminClient()
        return client.convert_event_to_garmin_json(event)

    @classmethod
    def export_all(
        cls,
        events: List[IntervalsEvent],
        output_dir: pathlib.Path,
        base_name: str = "training_plan",
    ) -> Dict[str, str]:
        """
        Export all formats to the given directory.
        Returns mapping of format to file path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}

        # 1. Export iCalendar
        ics_path = output_dir / f"{base_name}.ics"
        ics_content = cls.events_to_ics(events)
        ics_path.write_text(ics_content, encoding="utf-8")
        results["ics"] = str(ics_path)

        # 2. Export JSON
        json_path = output_dir / f"{base_name}.json"
        json_content = cls.events_to_json(events)
        json_path.write_text(json_content, encoding="utf-8")
        results["json"] = str(json_path)

        # 3. Export Zwift ZWO for bike workouts
        zwo_dir = output_dir / "zwift_workouts"
        zwo_count = 0
        for i, event in enumerate(events):
            zwo_xml = cls.event_to_zwo(event)
            if zwo_xml:
                zwo_dir.mkdir(parents=True, exist_ok=True)
                clean_title = "".join(c if c.isalnum() or c in "._- " else "_" for c in (event.name or f"ride_{i}"))
                fpath = zwo_dir / f"{clean_title.strip().replace(' ', '_')}.zwo"
                fpath.write_text(zwo_xml, encoding="utf-8")
                zwo_count += 1
        results["zwo_count"] = str(zwo_count)
        results["zwo_dir"] = str(zwo_dir) if zwo_count > 0 else ""

        # 4. Export Garmin .fit workouts for all structured activities
        garmin_dir = output_dir / "garmin_workouts"
        garmin_count = 0
        for i, event in enumerate(events):
            fit_bytes = cls.event_to_garmin_fit(event)
            if fit_bytes:
                garmin_dir.mkdir(parents=True, exist_ok=True)
                clean_title = "".join(c if c.isalnum() or c in "._- " else "_" for c in (event.name or f"workout_{i}"))
                fpath = garmin_dir / f"{clean_title.strip().replace(' ', '_')}.fit"
                fpath.write_bytes(fit_bytes)
                garmin_count += 1
        results["garmin_count"] = str(garmin_count)
        results["garmin_dir"] = str(garmin_dir) if garmin_count > 0 else ""

        return results
