"""
Tests for Intelligent Coaching Advisor.
"""

import datetime

from intervals_plan.analytics import (
    ACWRMetric,
    DisciplineSummary,
    IntensityDistribution,
    PhysiologicalReadiness,
    RollingAnalysisReport,
)
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.coaching_advisor import CoachingAdvisor


def _make_dummy_report(
    rhr_elevated=False,
    acwr_status="SWEET_SPOT",
    readiness_state="OPTIMAL_OVERLOAD",
    acwr_ratio=1.05,
):
    acwr = ACWRMetric(
        acute_load_7d=350.0,
        chronic_load_28d=1400.0,
        chronic_weekly_avg=350.0,
        ratio=acwr_ratio,
        status=acwr_status,
        guidance="Optimal load",
    )
    readiness = PhysiologicalReadiness(
        ctl=45.0,
        atl=42.0,
        tsb=3.0,
        resting_hr_baseline=50.0,
        recent_resting_hr=56.0 if rhr_elevated else 50.0,
        rhr_delta=6.0 if rhr_elevated else 0.0,
        rhr_elevated=rhr_elevated,
        readiness_state=readiness_state,
        readiness_score=85 if not rhr_elevated else 45,
        recommendation="Continue training",
        target_next_week_tss=380.0,
        target_next_week_hours=8.0,
    )
    dist = IntensityDistribution(
        low_intensity_pct=80.0,
        moderate_intensity_pct=10.0,
        high_intensity_pct=10.0,
        total_moving_time_hours=8.0,
        is_polarized=True,
        summary="Polarized",
    )
    return RollingAnalysisReport(
        period_start="2026-10-01",
        period_end="2026-10-30",
        total_activities=12,
        total_moving_hours=8.0,
        total_load_tss=350.0,
        disciplines={"Run": DisciplineSummary("Run", 6, 4.0, 180.0, 45.0)},
        acwr=acwr,
        readiness=readiness,
        intensity_distribution=dist,
        raw_wellness_count=30,
    )


def test_coaching_advisor_base_phase():
    prof = AthleteProfileConfig(
        target_event_name="Autumn 10k",
        target_race_date=(datetime.date.today() + datetime.timedelta(days=70)).isoformat(),
        constraints=["achilles_caution"],
    )
    advisor = CoachingAdvisor(prof)
    report = _make_dummy_report()
    advice = advisor.advise(report)

    assert advice.periodization_phase == "base"
    assert "Base Foundation" in advice.headline
    assert any("Constraint Active: Achilles caution" in a for a in advice.alerts)
    lines = advice.to_lines()
    assert any("BASE" in l for l in lines)


def test_coaching_advisor_taper_phase():
    prof = AthleteProfileConfig(
        target_event_name="Marathon",
        target_race_date=(datetime.date.today() + datetime.timedelta(days=10)).isoformat(),
    )
    advisor = CoachingAdvisor(prof)
    report = _make_dummy_report()
    advice = advisor.advise(report)

    assert advice.periodization_phase == "taper"
    assert "Taper & Sharpening" in advice.headline
    assert len(advice.key_recommendations) > 0


def test_coaching_advisor_peak_and_build():
    # Peak
    prof_peak = AthleteProfileConfig(
        target_race_date=(datetime.date.today() + datetime.timedelta(days=21)).isoformat()
    )
    advice_peak = CoachingAdvisor(prof_peak).advise(_make_dummy_report())
    assert advice_peak.periodization_phase == "peak"
    assert "Peak Phase" in advice_peak.headline

    # Build
    prof_build = AthleteProfileConfig(
        target_race_date=(datetime.date.today() + datetime.timedelta(days=40)).isoformat()
    )
    advice_build = CoachingAdvisor(prof_build).advise(_make_dummy_report())
    assert advice_build.periodization_phase == "build"
    assert "Build Phase" in advice_build.headline


def test_coaching_advisor_rhr_elevated_and_danger_acwr():
    prof = AthleteProfileConfig(target_race_date=None)
    report = _make_dummy_report(rhr_elevated=True, acwr_status="DANGER_ZONE", acwr_ratio=1.65)
    advice = CoachingAdvisor(prof).advise(report)

    assert "Recovery" in advice.headline
    assert any("Acute Spike" in a for a in advice.alerts)
    assert any("Elevated Resting HR" in a for a in advice.alerts)


def test_coaching_advisor_under_training():
    prof = AthleteProfileConfig(target_race_date=None)
    report = _make_dummy_report(acwr_status="UNDER_TRAINING", acwr_ratio=0.6)
    advice = CoachingAdvisor(prof).advise(report)
    assert any("Under-Training" in a for a in advice.alerts)
