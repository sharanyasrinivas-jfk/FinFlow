"""Feature prioritisation (RICE-style) and data-driven stage pointers."""
from __future__ import annotations

import pandas as pd

# name, reach %, impact (1-3), confidence %, effort (person-weeks), rationale
# All inputs are PRODUCT JUDGEMENT / HYPOTHESES, not validated estimates.
FEATURES = [
    ("Live photo-quality check on capture", 85, 3, 80, 5, "Blurry, glare and cropped photos are ~40% of rejections"),
    ("Guided checklist with examples", 90, 2, 90, 3, "Sets expectations before the camera opens"),
    ("Real-time status tracker with SMS updates", 100, 2, 80, 6, "Removes 'where is my application?' contacts"),
    ("Fix errors in place, no restart", 34, 3, 80, 4, "Rejected applicants keep their saved documents"),
    ("Progressive profile (defer optional fields)", 100, 1, 80, 3, "Shortens the form before first funding"),
    ("Save and resume across devices", 45, 2, 70, 6, "Desktop-to-phone handoff via QR code"),
    ("Name-mismatch auto-reconcile", 22, 2, 60, 8, "Fuzzy match on initials and order"),
    ("Government e-KYC fetch", 70, 3, 50, 12, "Largest upside, longest lead time, partner risk"),
    ("Stuck-user support escalation", 20, 1, 60, 5, "Offer chat after two failed attempts"),
]


def score_features(features=FEATURES, do_now: int = 3) -> pd.DataFrame:
    """score = reach% x impact x confidence% / effort. Top `do_now` are 'Do now'."""
    df = pd.DataFrame(features, columns=["feature", "reach_pct", "impact", "confidence_pct",
                                         "effort_weeks", "rationale"])
    df["score"] = df.reach_pct * df.impact * df.confidence_pct / 100 / df.effort_weeks
    df = df.sort_values("score", ascending=False, kind="stable").reset_index(drop=True)  # ties keep list order
    df["rank"] = df.index + 1
    df["decision"] = ["Do now" if r <= do_now else "Next" if r <= 6 else "Later" for r in df["rank"]]
    return df


def stage_recommendations(funnel_df: pd.DataFrame, top_n: int = 2) -> list[str]:
    """Plain-language pointers to the biggest step losses after sign-up."""
    after = funnel_df.iloc[3:].sort_values("step_loss", ascending=False).head(top_n)
    notes = []
    for i, r in after.iterrows():
        prev = funnel_df.loc[i - 1]
        notes.append(f"{prev['stage']} -> {r['stage']}: {r['step_loss']:.0%} lost "
                     f"({int(prev['users'] - r['users']):,} applicants). "
                     "Hypothesis: investigate causes before building.")
    return notes
