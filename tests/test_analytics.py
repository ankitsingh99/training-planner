"""
Tests for Sports Science Analytics Engine (ACWR, PMC, Seiler 80/20, Autonomic Readiness).
"""

import datetime
from intervals_plan.analytics import (
    ACWRMetric,
    DisciplineSummary,
    IntensityDistribution,
    PhysiologicalReadiness,
    RollingAnalysisReport,
    RollingMetricsAnalyzer,
)


def test_compute_acwr_sweet_spot():
    analyzer = RollingMetricsAnalyzer()
    end_date = datetime.date(2026, 11, 2)
    
    daily_loads = []
    curr = end_date - datetime.timedelta(days=27)
    while curr <= end_date:
        daily_loads.append((curr, 50.0))
        curr += datetime.timedelta(days=1)

    metric = analyzer.compute_acwr(daily_loads, end_date)
    assert metric.ratio == 1.00
    assert metric.status == "SWEET_SPOT"


def test_compute_acwr_danger_zone_spike():
    analyzer = RollingMetricsAnalyzer()
    end_date = datetime.date(2026, 11, 2)

    daily_loads = []
    curr = end_date - datetime.timedelta(days=27)
    while curr <= end_date:
        if (end_date - curr).days < 7:
            daily_loads.append((curr, 80.0))
        else:
            daily_loads.append((curr, 10.0))
        curr += datetime.timedelta(days=1)

    metric = analyzer.compute_acwr(daily_loads, end_date)
    assert metric.ratio > 1.5
    assert metric.status == "DANGER_ZONE"


def test_compute_acwr_elevated_load_and_zero_chronic():
    analyzer = RollingMetricsAnalyzer()
    end_date = datetime.date(2026, 11, 2)

    # 1. Zero chronic, acute positive
    daily_loads_zero_chronic = [(end_date, 50.0)]
    # chronic_start is 27 days back, so this only has load on end_date
    # wait, chronic_start <= end_date is true so chronic_total is 50.0
    # To test chronic_weekly_avg == 0 but acute > 0:
    # Actually if chronic_weekly_avg == 0, acute_total must be > 0.
    # In compute_acwr:
    # acute_start = end_date - 6, chronic_start = end_date - 27
    # Any load in acute_start is also in chronic_start. So chronic_total >= acute_total.
    # But if chronic_total is 0, acute is 0.
    # Empty loads:
    metric_empty = analyzer.compute_acwr([], end_date)
    assert metric_empty.ratio == 0.0
    assert metric_empty.status == "UNDER_TRAINING"

    # Elevated load between 1.3 and 1.5
    # Let chronic weekly avg = 100 (chronic_total = 400), acute = 140
    daily_loads_elevated = []
    curr = end_date - datetime.timedelta(days=27)
    while curr <= end_date:
        if (end_date - curr).days < 7:
            daily_loads_elevated.append((curr, 20.0))  # 7 * 20 = 140
        else:
            daily_loads_elevated.append((curr, 260.0 / 21.0)) # ~260 / 21
        curr += datetime.timedelta(days=1)
    metric_elevated = analyzer.compute_acwr(daily_loads_elevated, end_date)
    assert metric_elevated.status == "ELEVATED_LOAD"


def test_analyze_autonomic_readiness_elevated_rhr():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.0, athlete_lthr=182)
    end_date = datetime.date(2026, 11, 2)
    
    wellness = []
    for i in range(25):
        d = (end_date - datetime.timedelta(days=29 - i)).isoformat()
        wellness.append({"id": d, "restingHR": 49 + (i % 3)})
    for i in range(3):
        d = (end_date - datetime.timedelta(days=2 - i)).isoformat()
        wellness.append({"id": d, "restingHR": 65})

    acwr = analyzer.compute_acwr([], end_date)
    readiness = analyzer.analyze_autonomic_readiness(wellness, acwr, ctl=15.0, atl=30.0)

    assert readiness.rhr_elevated is True
    assert readiness.rhr_delta is not None and readiness.rhr_delta >= 4.0
    assert readiness.readiness_state in ["ELEVATED_FATIGUE", "RECOVERY_MANDATORY"]
    assert readiness.target_next_week_hours < 8.0


def test_analyze_autonomic_readiness_states():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.0, athlete_lthr=182)
    end_date = datetime.date(2026, 11, 2)
    wellness = [{"id": f"2026-10-{i:02d}", "restingHR": 50} for i in range(1, 20)]

    # 1. OPTIMAL_OVERLOAD (tsb >= -10, acwr sweet spot, normal rhr)
    daily_loads_sweet = [(end_date - datetime.timedelta(days=i), 50.0) for i in range(28)]
    acwr_sweet = analyzer.compute_acwr(daily_loads_sweet, end_date)
    r1 = analyzer.analyze_autonomic_readiness(wellness, acwr_sweet, ctl=50.0, atl=52.0)
    assert r1.readiness_state == "OPTIMAL_OVERLOAD"

    # 2. PRODUCTIVE_MAINTENANCE (tsb between -30 and -16)
    r2 = analyzer.analyze_autonomic_readiness(wellness, acwr_sweet, ctl=40.0, atl=62.0)
    assert r2.readiness_state == "PRODUCTIVE_MAINTENANCE"

    # 3. ELEVATED_FATIGUE (tsb < -30)
    r3 = analyzer.analyze_autonomic_readiness(wellness, acwr_sweet, ctl=30.0, atl=65.0)
    assert r3.readiness_state == "ELEVATED_FATIGUE"

    # 4. RECOVERY_MANDATORY (elevated RHR + tsb < -25)
    wellness_spiked = [{"id": f"2026-10-{i:02d}", "restingHR": 48} for i in range(1, 20)] + [
        {"id": "2026-10-30", "restingHR": 60},
        {"id": "2026-10-31", "restingHR": 60},
        {"id": "2026-11-01", "restingHR": 60},
    ]
    r4 = analyzer.analyze_autonomic_readiness(wellness_spiked, acwr_sweet, ctl=30.0, atl=65.0)
    assert r4.readiness_state == "RECOVERY_MANDATORY"


def test_analyze_intensity_distribution_with_hr_and_heuristics():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.0, athlete_lthr=180)
    
    # HR based: low (<84% LTHR = 151), mod (151-171), high (>=171)
    acts_hr = [
        {"moving_time": 3600, "average_heartrate": 140}, # low
        {"moving_time": 1800, "average_heartrate": 160}, # mod
        {"moving_time": 600, "average_heartrate": 175},  # high
    ]
    dist_hr = analyzer.analyze_intensity_distribution(acts_hr)
    assert dist_hr.total_moving_time_hours == 1.7
    assert dist_hr.low_intensity_pct > 50.0

    # Heuristic based (missing HR)
    acts_names = [
        {"moving_time": 3600, "name": "Easy Base Recovery Spin"},
        {"moving_time": 1800, "name": "Club Tempo Group Ride"},
        {"moving_time": 1200, "name": "Track 5k Interval Sprint"},
        {"moving_time": 1800, "name": "General Workout"},
    ]
    dist_names = analyzer.analyze_intensity_distribution(acts_names)
    assert dist_names.total_moving_time_hours > 0

    # Empty activities fallback
    dist_empty = analyzer.analyze_intensity_distribution([])
    assert dist_empty.low_intensity_pct == 80.0
    assert dist_empty.is_polarized is True


def test_analyze_disciplines():
    analyzer = RollingMetricsAnalyzer()
    acts = [
        {"type": "VirtualRide", "moving_time": 3600, "icu_training_load": 60, "distance": 30000},
        {"type": "TrailRun", "moving_time": 1800, "icu_training_load": 40, "distance": 5000},
        {"type": "OpenWaterSwim", "moving_time": 1200, "icu_training_load": 25, "distance": 1000},
        {"type": "WeightTraining", "moving_time": 2400, "icu_training_load": 30, "distance": 0},
    ]
    disciplines = analyzer.analyze_disciplines(acts)
    assert "Ride" in disciplines
    assert "Run" in disciplines
    assert "Swim" in disciplines
    assert "Other" in disciplines
    assert disciplines["Ride"].moving_time_hours == 1.0


def test_analyze_30d_end_to_end_and_summary_lines():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.5, athlete_lthr=180)
    end_str = "2026-11-02"
    
    wellness = [
        {"id": f"2026-10-{i:02d}", "restingHR": 50, "ctl": 40.0, "atl": 42.0}
        for i in range(10, 32)
    ]
    activities = [
        {"start_date_local": "2026-10-25T07:00:00", "type": "Run", "moving_time": 3600, "icu_training_load": 55, "average_heartrate": 145},
        {"start_date_local": "2026-10-28T08:00:00", "type": "Ride", "moving_time": 7200, "icu_training_load": 110, "average_heartrate": 140},
        {"start_date_local": "2026-08-01T08:00:00", "type": "Ride", "moving_time": 7200, "icu_training_load": 110}, # outside 30d
    ]

    report = analyzer.analyze_30d(wellness, activities, end_date_str=end_str)
    assert report.total_activities == 3
    assert report.total_moving_hours > 0

    lines = report.summary_lines()
    assert len(lines) > 20
    assert any("PHYSIOLOGICAL & TRAINING LOAD REPORT" in l for l in lines)
    assert any("PERFORMANCE MANAGEMENT CHART" in l for l in lines)
    assert any("ACUTE:CHRONIC WORKLOAD RATIO" in l for l in lines)
