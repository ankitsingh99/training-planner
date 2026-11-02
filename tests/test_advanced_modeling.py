"""Unit tests for advanced sports science modeling (Skiba W'bal, DFA a1, and DataQualityAuditor)."""

from intervals_plan.advanced_modeling import (
    DataQualityAuditor,
    compute_wbal,
    dfa_alpha1,
    flag_artifacts,
    parse_rr_stream,
    summarize_wbal,
)


def test_wbal_depletion_and_recovery():
    # CP = 250 W, W' = 20,000 J
    # 10s at 350 W (+100 W above CP -> 1,000 J depleted)
    # 20s at 150 W (recovery)
    power = [350.0] * 10 + [150.0] * 20
    w_prime = 20000.0
    cp = 250.0

    wbal_series = compute_wbal(power, w_prime=w_prime, cp=cp)
    assert len(wbal_series) == 30
    assert wbal_series[9] == 19000.0  # 20,000 - 10*100
    assert wbal_series[29] > wbal_series[9]  # Reconstituted

    summary = summarize_wbal(wbal_series, w_prime=w_prime)
    assert summary["w_prime_j"] == 20000.0
    assert summary["wbal_min_j"] == 19000.0
    assert summary["wbal_max_depletion_j"] == 1000.0
    assert summary["wbal_usage_pct"] == 5.0


def test_wbal_deep_depletion_events():
    # Deplete below 40% (8,000 J), then recover above 50%
    w_prime = 20000.0
    cp = 200.0
    power = [500.0] * 45 + [100.0] * 300  # 45s at 500W (+300W * 45 = 13,500 J dropped, reaching 6,500 J)
    wbal = compute_wbal(power, w_prime, cp)
    summary = summarize_wbal(wbal, w_prime)

    assert summary["wbal_min_j"] < 8000.0
    assert summary["wbal_depletion_events"] >= 1
    assert summary["wbal_recovery_ratio"] is not None


def test_dfa_alpha1_short_series_returns_none():
    short_rr = [800.0] * 10
    assert dfa_alpha1(short_rr) is None


def test_dfa_alpha1_synthetic_fractal_series():
    # Generate 100 beats with gentle drift
    rr = [800.0 + (i % 20) * 5.0 for i in range(120)]
    alpha = dfa_alpha1(rr)
    assert alpha is not None
    assert 0.0 < alpha < 2.0


def test_parse_rr_stream_and_flag_artifacts():
    hrv_stream = [[800.0], [805.0], None, [810.0, 1600.0]]  # 1600ms is an artifact jump
    beats = parse_rr_stream(hrv_stream)
    assert len(beats) == 4
    assert beats[0] == (0.0, 800.0)

    rr_vals = [b[1] for b in beats]
    mask = flag_artifacts(rr_vals)
    assert mask[0] is True
    assert mask[1] is True
    assert mask[2] is True
    assert mask[3] is False  # 1600ms deviates >20% from 810ms


def test_data_quality_auditor_all_ok():
    report = DataQualityAuditor.audit(
        ftp=250.0,
        rolling_ftp=252.0,
        eftp=248.0,
        w_prime=20000.0,
        rolling_w_prime=19800.0,
        resting_hr=52.0,
        sleep_secs=27000.0,
        recent_activities=[
            {"rpe": 6, "carbs_ingested_g": 60},
            {"rpe": 5, "carbs_ingested_g": 30},
            {"rpe": 7, "carbs_ingested_g": 80},
        ],
    )
    assert report.overall == "Good"
    assert report.non_ok_count == 0
    assert len(report.checks) >= 5


def test_data_quality_auditor_warnings_and_missing():
    report = DataQualityAuditor.audit(
        ftp=250.0,
        rolling_ftp=320.0,  # >20% difference -> Missing
        recent_activities=[],  # 0 activities -> Missing
    )
    assert report.overall in ("Partial", "Limited")
    assert report.non_ok_count >= 2
