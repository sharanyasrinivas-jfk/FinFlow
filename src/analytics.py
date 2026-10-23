"""Funnel analytics on the onboarding dataset (synthetic or real, same schema)."""
from __future__ import annotations

import math
from statistics import NormalDist

import pandas as pd

from .data_generator import HOURS_COLS, STAGES


def load(path: str = "data/onboarding_applications.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def filter_data(df: pd.DataFrame, device: str = "all") -> pd.DataFrame:
    return df if device == "all" else df[df["device"] == device]


def funnel(df: pd.DataFrame, cohort: str) -> pd.DataFrame:
    """One row per stage: users, step conversion, cumulative conversion, step loss."""
    d = df[df["cohort"] == cohort]
    users = [int((d["furthest_stage"] >= i).sum()) for i in range(len(STAGES))]
    out = pd.DataFrame({"stage": STAGES, "users": users})
    out["step_conversion"] = (out["users"] / out["users"].shift(1)).fillna(1.0)
    out["cumulative_conversion"] = out["users"] / out["users"].iloc[0]
    out["step_loss"] = 1 - out["step_conversion"]
    return out


def median_hours(df: pd.DataFrame, cohort: str) -> pd.Series:
    """Median hours spent on the step that ends at each stage."""
    s = df[df["cohort"] == cohort][HOURS_COLS].median()
    s.index = STAGES[1:]
    return s


def rejection_reasons(df: pd.DataFrame, cohort: str) -> pd.DataFrame:
    """First-submission rejections per 1,000 submitted documents, by reason."""
    d = df[(df["cohort"] == cohort) & (df["furthest_stage"] >= 3)]
    r = d.loc[d["first_submission_rejected"], "rejection_reason"].value_counts()
    out = (r / len(d) * 1000).rename("per_1000_submissions").reset_index()
    out.columns = ["reason", "per_1000_submissions"]
    return out


def rejection_rate(df: pd.DataFrame, cohort: str) -> float:
    d = df[(df["cohort"] == cohort) & (df["furthest_stage"] >= 3)]
    return float(d["first_submission_rejected"].mean())


def support_per_1000(df: pd.DataFrame, cohort: str) -> float:
    d = df[(df["cohort"] == cohort) & (df["furthest_stage"] >= 2)]
    return float(d["support_contact"].mean() * 1000)


def weekly_conversion(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("week")
    out = g.agg(visitors=("applicant_id", "size"),
                funded=("furthest_stage", lambda s: int((s == 6).sum())))
    out["visit_to_funded"] = out["funded"] / out["visitors"]
    return out.reset_index()


def biggest_loss_after_signup(df: pd.DataFrame, cohort: str) -> dict:
    """Largest step loss among transitions that start at 'Created account' or later."""
    f = funnel(df, cohort)
    after = f.iloc[3:]  # steps ending at Submitted documents or later
    i = after["step_loss"].idxmax()
    return {"from": f.loc[i - 1, "stage"], "to": f.loc[i, "stage"], "loss": float(f.loc[i, "step_loss"])}


def kpis(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in ("baseline", "pilot"):
        f = funnel(df, c)
        h = median_hours(df, c)
        rows.append({
            "cohort": c,
            "visit_to_funded": f["cumulative_conversion"].iloc[-1],
            "application_completion": f["step_conversion"].iloc[3],
            "document_rejection_rate": rejection_rate(df, c),
            "median_verification_hours": h["Passed verification"],
            "median_first_submit_hours": h["Submitted documents"],
            "support_per_1000": support_per_1000(df, c),
        })
    return pd.DataFrame(rows).set_index("cohort")


# ---------- statistics for the A/B plan ----------
def two_proportion_ztest(x1: int, n1: int, x2: int, n2: int) -> dict:
    """Two-sided pooled z-test for p2 - p1, with unpooled 95% CI."""
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se0 if se0 else 0.0
    p = 2 * (1 - NormalDist().cdf(abs(z)))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p2 - p1
    return {"diff": d, "ci_low": d - 1.96 * se, "ci_high": d + 1.96 * se, "z": z, "p_value": p}


def sample_size_per_arm(p_base: float, mde_abs: float, alpha: float = 0.05,
                        power: float = 0.80) -> int:
    """Visitors needed per arm to detect an absolute lift of mde_abs (two-sided)."""
    nd = NormalDist()
    za, zb = nd.inv_cdf(1 - alpha / 2), nd.inv_cdf(power)
    p2 = p_base + mde_abs
    var = p_base * (1 - p_base) + p2 * (1 - p2)
    return math.ceil((za + zb) ** 2 * var / mde_abs ** 2)
