"""
Declarative SQLAlchemy Models for Unified Training Analyst Data Architecture.
Adheres strictly to PROJECT_SPEC.md Section 5 Unified Data Architecture.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from intervals_plan.database import Base


class UserProfileModel(Base):
    """User profile, personal metrics, training preferences and constraints."""

    __tablename__ = "user_profiles"

    user_id = Column(String(64), primary_key=True)
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    body_fat_pct = Column(Float, nullable=True)
    fat_mass_kg = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    hrv_baseline = Column(Float, nullable=True)
    vo2_max = Column(Float, nullable=True)

    training_preferences = Column(JSON, nullable=False, default=dict)
    goals = Column(JSON, nullable=False, default=dict)
    heart_rate_zones = Column(JSON, nullable=False, default=dict)
    available_equipment = Column(JSON, nullable=False, default=list)
    training_constraints = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "age": self.age,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "body_fat_pct": self.body_fat_pct,
            "fat_mass_kg": self.fat_mass_kg,
            "muscle_mass_kg": self.muscle_mass_kg,
            "resting_heart_rate": self.resting_heart_rate,
            "hrv_baseline": self.hrv_baseline,
            "vo2_max": self.vo2_max,
            "training_preferences": self.training_preferences,
            "goals": self.goals,
            "heart_rate_zones": self.heart_rate_zones,
            "available_equipment": self.available_equipment,
            "training_constraints": self.training_constraints,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ActivityModel(Base):
    """Endurance and general cardio activity entity (COROS, Manual). Provenance retained."""

    __tablename__ = "activities"

    activity_id = Column(String(64), primary_key=True)
    source = Column(String(32), nullable=False, index=True)  # 'COROS', 'MANUAL_IMPORT' (Strava strictly excluded)
    source_activity_id = Column(String(128), nullable=False, index=True)
    activity_type = Column(String(32), nullable=False, index=True)  # 'cycling', 'running', etc.
    start_time = Column(DateTime, nullable=False, index=True)
    duration = Column(Float, nullable=False)  # Duration in seconds
    distance = Column(Float, nullable=True)  # Distance in meters
    elevation = Column(Float, nullable=True)  # Elevation gain in meters
    average_heart_rate = Column(Float, nullable=True)
    maximum_heart_rate = Column(Float, nullable=True)
    average_speed = Column(Float, nullable=True)  # m/s
    average_pace = Column(Float, nullable=True)  # sec/km
    calories = Column(Float, nullable=True)
    training_load = Column(Float, nullable=True)
    cadence_avg = Column(Float, nullable=True)
    cadence_max = Column(Float, nullable=True)
    power_avg = Column(Float, nullable=True)
    hr_zones_seconds = Column(JSON, nullable=True)
    raw_data_reference = Column(Text, nullable=True)
    import_timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("source", "source_activity_id", name="uq_activity_source_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_id": self.activity_id,
            "source": self.source,
            "source_activity_id": self.source_activity_id,
            "activity_type": self.activity_type,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration": self.duration,
            "distance": self.distance,
            "elevation": self.elevation,
            "average_heart_rate": self.average_heart_rate,
            "maximum_heart_rate": self.maximum_heart_rate,
            "average_speed": self.average_speed,
            "average_pace": self.average_pace,
            "calories": self.calories,
            "training_load": self.training_load,
            "cadence_avg": self.cadence_avg,
            "cadence_max": self.cadence_max,
            "power_avg": self.power_avg,
            "hr_zones_seconds": self.hr_zones_seconds,
            "import_timestamp": self.import_timestamp.isoformat() if self.import_timestamp else None,
        }


class StrengthWorkoutModel(Base):
    """Strength training workout entity (Hevy, Manual)."""

    __tablename__ = "strength_workouts"

    workout_id = Column(String(64), primary_key=True)
    source = Column(String(32), nullable=False, index=True)  # 'HEVY', 'HEVY_CSV', etc.
    source_workout_id = Column(String(128), nullable=False, index=True)
    workout_name = Column(String(256), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    duration = Column(Float, nullable=False)  # seconds
    raw_data_reference = Column(Text, nullable=True)
    import_timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    sets = relationship("ExerciseSetModel", back_populates="workout", cascade="all, delete-orphan", order_by="ExerciseSetModel.set_number")

    __table_args__ = (
        UniqueConstraint("source", "source_workout_id", name="uq_strength_source_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workout_id": self.workout_id,
            "source": self.source,
            "source_workout_id": self.source_workout_id,
            "workout_name": self.workout_name,
            "date": self.date.isoformat() if self.date else None,
            "duration": self.duration,
            "import_timestamp": self.import_timestamp.isoformat() if self.import_timestamp else None,
            "sets": [s.to_dict() for s in self.sets] if self.sets else [],
        }


class ExerciseModel(Base):
    """Catalog of normalized exercises with muscle group contributions."""

    __tablename__ = "exercises"

    exercise_id = Column(String(64), primary_key=True)
    original_name = Column(String(256), nullable=False)
    normalized_name = Column(String(256), nullable=False, unique=True, index=True)
    muscle_groups = Column(JSON, nullable=False)  # list of {"muscle": str, "contribution": float}
    movement_pattern = Column(String(64), nullable=True)
    equipment = Column(String(64), nullable=True)
    exercise_category = Column(String(32), nullable=True)  # 'compound', 'isolation'
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    sets = relationship("ExerciseSetModel", back_populates="exercise")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exercise_id": self.exercise_id,
            "original_name": self.original_name,
            "normalized_name": self.normalized_name,
            "muscle_groups": self.muscle_groups,
            "movement_pattern": self.movement_pattern,
            "equipment": self.equipment,
            "exercise_category": self.exercise_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ExerciseSetModel(Base):
    """Individual set performance within a strength workout."""

    __tablename__ = "exercise_sets"

    set_id = Column(String(64), primary_key=True)
    workout_id = Column(String(64), ForeignKey("strength_workouts.workout_id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id = Column(String(64), ForeignKey("exercises.exercise_id", ondelete="CASCADE"), nullable=False, index=True)
    set_number = Column(Integer, nullable=False)
    repetitions = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # kg
    duration = Column(Float, nullable=True)  # seconds
    distance = Column(Float, nullable=True)  # meters
    set_type = Column(String(32), default="normal", nullable=False)  # 'normal', 'warmup', 'drop', 'failure'
    estimated_rir = Column(Float, nullable=True)
    estimated_1rm = Column(Float, nullable=True)  # Epley: weight * (1 + reps/30)

    workout = relationship("StrengthWorkoutModel", back_populates="sets")
    exercise = relationship("ExerciseModel", back_populates="sets")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_id": self.set_id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.normalized_name if self.exercise else None,
            "set_number": self.set_number,
            "repetitions": self.repetitions,
            "weight": self.weight,
            "duration": self.duration,
            "distance": self.distance,
            "set_type": self.set_type,
            "estimated_rir": self.estimated_rir,
            "estimated_1rm": self.estimated_1rm,
        }


class PlannedWorkoutModel(Base):
    """Prescribed upcoming workout (Strength or Endurance)."""

    __tablename__ = "planned_workouts"

    planned_workout_id = Column(String(64), primary_key=True)
    date = Column(String(10), nullable=False, index=True)  # 'YYYY-MM-DD'
    workout_type = Column(String(64), nullable=False, index=True)
    workout_structure = Column(JSON, nullable=False)
    target_intensity = Column(String(64), nullable=True)
    status = Column(String(32), default="planned", nullable=False, index=True)  # 'planned', 'completed', 'missed', 'rescheduled', 'cancelled'
    source = Column(String(32), default="ADAPTPULSE_AI", nullable=False)
    external_id = Column(String(128), nullable=True, index=True)
    completed_workout_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "planned_workout_id": self.planned_workout_id,
            "date": self.date,
            "workout_type": self.workout_type,
            "workout_structure": self.workout_structure,
            "target_intensity": self.target_intensity,
            "status": self.status,
            "source": self.source,
            "external_id": self.external_id,
            "completed_workout_id": self.completed_workout_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FitnessSnapshotModel(Base):
    """Time-series physiological baseline measurements and fitness markers (COROS EvoLab)."""

    __tablename__ = "fitness_snapshots"

    snapshot_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(32), nullable=False, index=True)
    vo2_max = Column(Float, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    hrv = Column(Float, nullable=True)
    threshold_pace = Column(Float, nullable=True)  # sec/km
    threshold_heart_rate = Column(Integer, nullable=True)
    training_load = Column(Float, nullable=True)
    recovery_status = Column(String(64), nullable=True)
    raw_data_reference = Column(Text, nullable=True)
    import_timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("source", "timestamp", name="uq_snapshot_source_ts"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "vo2_max": self.vo2_max,
            "resting_heart_rate": self.resting_heart_rate,
            "hrv": self.hrv,
            "threshold_pace": self.threshold_pace,
            "threshold_heart_rate": self.threshold_heart_rate,
            "training_load": self.training_load,
            "recovery_status": self.recovery_status,
            "import_timestamp": self.import_timestamp.isoformat() if self.import_timestamp else None,
        }


class CoachRecommendationModel(Base):
    """Stored AI training recommendations, evidence, and outcomes."""

    __tablename__ = "coach_recommendations"

    recommendation_id = Column(String(64), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True)
    recommendation_type = Column(String(64), nullable=False)  # 'daily_analysis', 'weekly_review', 'monthly_review', 'adaptive_plan'
    recommendation = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    supporting_metrics = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String(32), default="proposed", nullable=False)  # 'proposed', 'approved', 'rejected', 'applied'
    outcome = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "recommendation_type": self.recommendation_type,
            "recommendation": self.recommendation,
            "rationale": self.rationale,
            "supporting_metrics": self.supporting_metrics,
            "confidence": self.confidence,
            "status": self.status,
            "outcome": self.outcome,
        }


class ImportAuditModel(Base):
    """Audit log of data import operations and reconciliations."""

    __tablename__ = "import_audits"

    audit_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    source = Column(String(32), nullable=False)
    records_discovered = Column(Integer, nullable=False)
    records_inserted = Column(Integer, nullable=False)
    records_updated = Column(Integer, nullable=False)
    duplicates_skipped = Column(Integer, nullable=False)
    records_rejected = Column(Integer, nullable=False)
    errors = Column(JSON, nullable=False, default=list)
    earliest_record_date = Column(String(32), nullable=True)
    latest_record_date = Column(String(32), nullable=True)
    report_summary = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "records_discovered": self.records_discovered,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "duplicates_skipped": self.duplicates_skipped,
            "records_rejected": self.records_rejected,
            "errors": self.errors,
            "earliest_record_date": self.earliest_record_date,
            "latest_record_date": self.latest_record_date,
            "report_summary": self.report_summary,
        }
