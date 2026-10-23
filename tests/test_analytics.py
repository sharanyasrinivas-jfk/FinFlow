import pandas as pd
import pytest

from src import analytics as an
from src.data_generator import PASS_RATES, STAGES, generate
from src.recommendations import score_features


@pytest.fixture(scope="module")
def df():
    return generate(10_000, seed=42)


def test_reproducible():
    pd.testing.assert_frame_equal(generate(500, seed=1), generate(500, seed=1))


def test_cohort_sizes(df):
    assert df.groupby("cohort").size().to_dict() == {"baseline": 10_000, "pilot": 10_000}


@pytest.mark.parametrize("cohort", ["baseline", "pilot"])
def test_funnel_monotonic_and_matches_inputs(df, cohort):
    f = an.funnel(df, cohort)
    assert len(f) == len(STAGES)
    assert f["users"].is_monotonic_decreasing
    assert f["users"].iloc[0] == 10_000
    assert f["step_conversion"].iloc[1:].tolist() == pytest.approx(PASS_RATES[cohort], abs=0.03)


def test_pilot_beats_baseline(df):
    k = an.kpis(df)
    assert k.loc["pilot", "visit_to_funded"] > k.loc["baseline", "visit_to_funded"]
    assert k.loc["pilot", "document_rejection_rate"] < k.loc["baseline", "document_rejection_rate"]
    assert k.loc["baseline", "document_rejection_rate"] == pytest.approx(0.34, abs=0.02)


def test_device_filter(df):
    assert set(an.filter_data(df, "mobile")["device"]) == {"mobile"}
    assert len(an.filter_data(df, "all")) == len(df)


def test_biggest_baseline_loss_is_documents(df):
    assert an.biggest_loss_after_signup(df, "baseline")["to"] == "Submitted documents"


def test_weeks_split_by_cohort(df):
    assert df[df.cohort == "baseline"].week.max() == 6
    assert df[df.cohort == "pilot"].week.min() == 7


def test_ztest_detects_known_difference():
    r = an.two_proportion_ztest(1640, 10_000, 2880, 10_000)
    assert r["p_value"] < 1e-6 and r["ci_low"] > 0.10
    assert an.two_proportion_ztest(500, 5000, 500, 5000)["p_value"] == pytest.approx(1.0)


def test_sample_size_known_value():
    assert an.sample_size_per_arm(0.164, 0.02) == pytest.approx(5637, abs=5)
    assert an.sample_size_per_arm(0.164, 0.04) < an.sample_size_per_arm(0.164, 0.02)


def test_prioritization_top3():
    s = score_features()
    assert s.loc[s.decision == "Do now", "feature"].tolist() == [
        "Guided checklist with examples",
        "Live photo-quality check on capture",
        "Real-time status tracker with SMS updates",
    ]
    assert s.score.is_monotonic_decreasing
