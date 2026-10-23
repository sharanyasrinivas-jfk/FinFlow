"""Synthetic FinFlow onboarding data.

Every number here is an ASSUMPTION chosen to mirror the FinFlow onboarding lab
page. Nothing is measured from real applicants.

Run:  python -m src.data_generator            (writes data/onboarding_applications.csv)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STAGES = [
    "Visited",
    "Started sign-up",
    "Created account",
    "Submitted documents",
    "Passed verification",
    "Completed profile",
    "Funded account",
]
# Column holding "hours since the previous stage" for each stage after Visited.
HOURS_COLS = [
    "hours_to_started",
    "hours_to_account",
    "hours_to_docs",
    "hours_to_verified",
    "hours_to_profile",
    "hours_to_funded",
]

# Stage-to-stage pass rates (6 transitions), per cohort.
PASS_RATES = {
    "baseline": [0.62, 0.80, 0.70, 0.78, 0.84, 0.72],
    "pilot": [0.66, 0.86, 0.82, 0.88, 0.90, 0.78],
}
# Median hours spent on each transition.
MEDIAN_HOURS = {
    "baseline": [0.1, 0.3, 18, 26, 40, 62],
    "pilot": [0.1, 0.2, 5, 9, 14, 30],
}
DEVICE_SHARE = {"mobile": 0.62, "web": 0.38}
# Device effect on the account -> documents step (transition index 2).
# Mobile applicants struggle more with photo capture; the pilot narrows the gap.
DEVICE_DOC_MULT = {
    "baseline": {"mobile": 0.88, "web": 1.10},
    "pilot": {"mobile": 0.95, "web": 1.04},
}
# First-submission rejections per 1,000 submitted documents, by reason.
REJECTION_PER_1000 = {
    "baseline": {
        "Blurry or unreadable photo": 105,
        "Name differs from profile": 75,
        "Expired ID": 61,
        "Address proof too old": 51,
        "Glare or cropped edges": 31,
        "Other": 17,
    },
    "pilot": {
        "Blurry or unreadable photo": 31,
        "Name differs from profile": 38,
        "Expired ID": 24,
        "Address proof too old": 22,
        "Glare or cropped edges": 13,
        "Other": 12,
    },
}
# Status-related support contacts per applicant (applicant = created an account).
SUPPORT_CONTACT_RATE = {"baseline": 0.086, "pilot": 0.041}
LAUNCH_WEEK = 7  # pilot cohort traffic is weeks 7-12, baseline weeks 1-6
N_PER_COHORT = 10_000
SEED = 42


def _device_multipliers(cohort: str) -> dict[str, float]:
    """Normalise device multipliers so the traffic-weighted mean is exactly 1.
    This keeps the overall transition rate equal to PASS_RATES."""
    raw = DEVICE_DOC_MULT[cohort]
    k = 1.0 / sum(DEVICE_SHARE[d] * raw[d] for d in raw)
    return {d: raw[d] * k for d in raw}


def generate_cohort(cohort: str, n: int, rng: np.random.Generator) -> pd.DataFrame:
    devices = rng.choice(list(DEVICE_SHARE), size=n, p=list(DEVICE_SHARE.values()))
    weeks = rng.integers(1, LAUNCH_WEEK, n) if cohort == "baseline" else rng.integers(LAUNCH_WEEK, 13, n)
    mults = _device_multipliers(cohort)

    furthest = np.zeros(n, dtype=int)
    alive = np.ones(n, dtype=bool)
    hours = {c: np.full(n, np.nan) for c in HOURS_COLS}

    for t, col in enumerate(HOURS_COLS):
        p = np.full(n, PASS_RATES[cohort][t])
        if t == 2:
            p = np.clip(p * np.array([mults[d] for d in devices]), 0, 0.99)
        passed = alive & (rng.random(n) < p)
        # lognormal durations; median = MEDIAN_HOURS, sigma 0.8
        hours[col][passed] = rng.lognormal(np.log(MEDIAN_HOURS[cohort][t]), 0.8, passed.sum())
        furthest[passed] += 1
        alive = passed

    reasons = list(REJECTION_PER_1000[cohort])
    probs = np.array([REJECTION_PER_1000[cohort][r] for r in reasons]) / 1000
    labels = np.array(reasons + ["None"], dtype=object)
    probs = np.append(probs, 1 - probs.sum())
    submitted = furthest >= 3
    reason = np.full(n, "None", dtype=object)
    reason[submitted] = rng.choice(labels, size=int(submitted.sum()), p=probs)
    rejected = submitted & (reason != "None")

    applicant = furthest >= 2
    support = applicant & (rng.random(n) < SUPPORT_CONTACT_RATE[cohort])

    return pd.DataFrame(
        {
            "cohort": cohort,
            "device": devices,
            "week": weeks,
            "furthest_stage": furthest,
            **hours,
            "first_submission_rejected": rejected,
            "rejection_reason": np.where(rejected, reason, ""),
            "support_contact": support,
        }
    )


def generate(n_per_cohort: int = N_PER_COHORT, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.concat(
        [generate_cohort(c, n_per_cohort, rng) for c in ("baseline", "pilot")],
        ignore_index=True,
    )
    df.insert(0, "applicant_id", [f"A{i:05d}" for i in range(1, len(df) + 1)])
    return df.round({c: 2 for c in HOURS_COLS})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/onboarding_applications.csv")
    ap.add_argument("--n", type=int, default=N_PER_COHORT, help="visitors per cohort")
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = generate(a.n, a.seed)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}  (SYNTHETIC DATA)")


if __name__ == "__main__":
    main()
