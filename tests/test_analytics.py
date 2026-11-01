"""
Tests for Sports Science Analytics Engine (ACWR, PMC, Seiler 80/20, Autonomic Readiness).
"""

import datetime
from intervals_plan.analytics import RollingMetricsAnalyzer


def test_compute_acwr_sweet_spot():
    analyzer = RollingMetricsAnalyzer()
    end_date = datetime.date(2026, 11, 2)
    
    # 28 days of daily 50 TSS load
    daily_loads = []
    curr = end_date - datetime.timedelta(days=27)
    while curr <= end_date:
        daily_loads.append((curr, 50.0))
        curr += datetime.timedelta(days=1)

    # Acute (7 days): 7 * 50 = 350 TSS
    # Chronic (28 days): 28 * 50 = 1400 TSS, weekly avg = 350 TSS
    # ACWR = 350 / 350 = 1.00 -> SWEET_SPOT
    metric = analyzer.compute_acwr(daily_loads, end_date)
    assert metric.ratio == 1.00
    assert metric.status == "SWEET_SPOT"


def test_compute_acwr_danger_zone_spike():
    analyzer = RollingMetricsAnalyzer()
    end_date = datetime.date(2026, 11, 2)

    # Low chronic load for days 0-21, then acute spike in days 22-28
    daily_loads = []
    curr = end_date - datetime.timedelta(days=27)
    while curr <= end_date:
        # Acute period is last 7 days
        if (end_date - curr).days < 7:
            daily_loads.append((curr, 80.0))  # 7 * 80 = 560
        else:
            daily_loads.append((curr, 10.0))  # 21 * 10 = 210
        curr += datetime.timedelta(days=1)

    # Chronic = 560 + 210 = 770. Weekly avg = 192.5
    # ACWR = 560 / 192.5 = 2.91 -> DANGER_ZONE
    metric = analyzer.compute_acwr(daily_loads, end_date)
    assert metric.ratio > 1.5
    assert metric.status == "DANGER_ZONE"


def test_analyze_autonomic_readiness_elevated_rhr():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.0, athlete_lthr=182)
    end_date = datetime.date(2026, 11, 2)
    
    # Fake wellness records with normal baseline (50 bpm) and recent spike (65 bpm)
    wellness = []
    for i in range(25):
        d = (end_date - datetime.timedelta(days=29 - i)).isoformat()
        wellness.append({"id": d, "restingHR": 49 + (i % 3)})
    # Recent 3 days spike
    for i in range(3):
        d = (end_date - datetime.timedelta(days=2 - i)).isoformat()
        wellness.append({"id": d, "restingHR": 65})

    acwr = analyzer.compute_acwr([], end_date)
    readiness = analyzer.analyze_autonomic_readiness(wellness, acwr, ctl=15.0, atl=30.0)

    assert readiness.rhr_elevated is True
    assert readiness.rhr_delta is not None and readiness.rhr_delta >= 4.0
    assert readiness.readiness_state in ["ELEVATED_FATIGUE", "RECOVERY_MANDATORY"]
    assert readiness.target_next_week_hours < 8.0  # Safely throttled


def test_analyze_autonomic_readiness_optimal_overload():
    analyzer = RollingMetricsAnalyzer(target_hours_profile=8.0, athlete_lthr=182)
    end_date = datetime.date(2026, 11, 2)

    # 30 days of stable 50 bpm resting HR
    wellness = []
    for i in range(30):
        d = (end_date - datetime.timedelta(days=29 - i)).isoformat()
        wellness.append({"id": d, "restingHR": 50})

    # ACWR in sweet spot
    daily_loads = [(end_date - datetime.timedelta(days=i), 40.0) for i in range(28)]
    acwr = analyzer.compute_acwr(daily_loads, end_date)
    readiness = analyzer.analyze_autonomic_readiness(wellness, acwr, ctl=40.0, atl=38.0)

    assert readiness.rhr_elevated is False
    assert readiness.readiness_state == "OPTIMAL_OVERLOAD"
    assert readiness.readiness_score >= 80


def test_intensity_distribution_seiler_polarization():
    analyzer = RollingMetricsAnalyzer(athlete_lthr=182)
    activities = [
        # 4 hours easy (avg HR 135 < 151, ~74% LTHR)
        {"moving_time": 14400, "average_heartrate": 135, "name": "Zone 2 Ride"},
        # 1 hour intervals (avg HR 175 > 172, ~96% LTHR)
        {"moving_time": 3600, "average_heartrate": 175, "name": "5K Intervals"},
    ]
    dist = analyzer.analyze_intensity_distribution(activities)
    assert dist.low_intensity_pct == 80.0
    assert dist.high_intensity_pct == 20.0
    assert dist.is_polarized is True

