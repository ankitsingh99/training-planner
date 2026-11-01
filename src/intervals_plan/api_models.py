"""
Data models representing Intervals.icu API entities.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import json


@dataclass
class HRTarget:
    start: Optional[float] = None
    end: Optional[float] = None
    value: Optional[float] = None
    units: str = "%lthr"  # %lthr, bpm, etc.

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"units": self.units}
        if self.start is not None:
            d["start"] = self.start
        if self.end is not None:
            d["end"] = self.end
        if self.value is not None:
            d["value"] = self.value
        return d


@dataclass
class WorkoutStep:
    duration: Optional[int] = None
    text: str = ""
    reps: Optional[int] = None
    steps: Optional[List["WorkoutStep"]] = None
    hr: Optional[HRTarget] = None
    power: Optional[Dict[str, Any]] = None
    cadence: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.duration is not None:
            d["duration"] = int(self.duration)
        if self.text:
            d["text"] = self.text
        if self.reps is not None:
            d["reps"] = int(self.reps)
        if self.hr:
            d["hr"] = self.hr.to_dict()
        if self.power:
            d["power"] = self.power
        if self.cadence:
            d["cadence"] = self.cadence
        if self.steps:
            d["steps"] = [s.to_dict() for s in self.steps]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkoutStep":
        hr_obj = None
        if "hr" in data and isinstance(data["hr"], dict):
            hr_obj = HRTarget(
                start=data["hr"].get("start"),
                end=data["hr"].get("end"),
                value=data["hr"].get("value"),
                units=data["hr"].get("units", "%lthr"),
            )
        nested = None
        if "steps" in data and isinstance(data["steps"], list):
            nested = [cls.from_dict(s) for s in data["steps"]]
        
        return cls(
            duration=data.get("duration"),
            text=data.get("text", ""),
            reps=data.get("reps"),
            steps=nested,
            hr=hr_obj,
            power=data.get("power"),
            cadence=data.get("cadence"),
        )


@dataclass
class WorkoutDoc:
    description: str = ""
    steps: List[WorkoutStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkoutDoc":
        steps_list = [WorkoutStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            description=data.get("description", ""),
            steps=steps_list,
        )


@dataclass
class IntervalsEvent:
    start_date_local: str
    category: str = "WORKOUT"  # WORKOUT, NOTE, RACE, TARGET
    type: str = "Run"          # Run, Ride, WeightTraining, Walk
    name: str = ""
    description: str = ""
    moving_time: Optional[int] = None
    external_id: Optional[str] = None
    workout_doc: Optional[WorkoutDoc] = None
    id: Optional[int] = None
    color: Optional[str] = None
    athlete_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "start_date_local": self.start_date_local,
            "category": self.category,
            "type": self.type,
            "name": self.name,
            "description": self.description,
        }
        if self.moving_time is not None:
            d["moving_time"] = int(self.moving_time)
        if self.external_id:
            d["external_id"] = self.external_id
        if self.id is not None:
            d["id"] = self.id
        if self.color:
            d["color"] = self.color
        if self.workout_doc:
            d["workout_doc"] = self.workout_doc.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntervalsEvent":
        wdoc = None
        if "workout_doc" in data and isinstance(data["workout_doc"], dict):
            wdoc = WorkoutDoc.from_dict(data["workout_doc"])
        return cls(
            start_date_local=data.get("start_date_local", ""),
            category=data.get("category", "WORKOUT"),
            type=data.get("type", "Run"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            moving_time=data.get("moving_time"),
            external_id=data.get("external_id"),
            workout_doc=wdoc,
            id=data.get("id"),
            color=data.get("color"),
            athlete_id=data.get("athlete_id"),
        )


@dataclass
class AthleteProfile:
    id: str
    name: str = ""
    email: Optional[str] = None
    timezone: Optional[str] = None
    restingHR: Optional[int] = None
    lthr: Optional[int] = None
    maxHR: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AthleteProfile":
        return cls(
            id=str(data.get("id", "")),
            name=data.get("name") or data.get("username") or "Athlete",
            email=data.get("email"),
            timezone=data.get("timezone"),
            restingHR=data.get("restingHR"),
            lthr=data.get("lthr"),
            maxHR=data.get("maxHR"),
            city=data.get("city"),
            country=data.get("country"),
        )
