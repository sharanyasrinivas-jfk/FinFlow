"""Matplotlib figures shared by the Streamlit app and the screenshot script."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import analytics as an
from .data_generator import LAUNCH_WEEK

BASE_C, PILOT_C = "#9aa3b2", "#0f766e"
NOTE = "SIMULATED DATA - illustrative only"


def funnel_chart(df, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    fb, fp = an.funnel(df, "baseline"), an.funnel(df, "pilot")
    y = range(len(fb))
    ax.barh([i + 0.2 for i in y], fb["cumulative_conversion"] * 100, 0.4, label="Baseline", color=BASE_C)
    ax.barh([i - 0.2 for i in y], fp["cumulative_conversion"] * 100, 0.4, label="Redesign pilot", color=PILOT_C)
    ax.set_yticks(list(y)); ax.set_yticklabels(fb["stage"]); ax.invert_yaxis()
    ax.set_xlabel("% of visitors reaching stage"); ax.set_title("Funnel: cumulative conversion")
    ax.legend(frameon=False, loc="lower right")
    return ax


def step_chart(df, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    fb, fp = an.funnel(df, "baseline").iloc[1:], an.funnel(df, "pilot").iloc[1:]
    x = range(len(fb))
    ax.bar([i - 0.2 for i in x], fb["step_conversion"] * 100, 0.4, label="Baseline", color=BASE_C)
    ax.bar([i + 0.2 for i in x], fp["step_conversion"] * 100, 0.4, label="Redesign pilot", color=PILOT_C)
    ax.set_xticks(list(x)); ax.set_xticklabels([s.replace(" ", "\n", 1) for s in fb["stage"]], fontsize=7)
    ax.set_ylim(0, 112); ax.set_ylabel("% passing from previous stage")
    ax.set_title("Step conversion"); ax.legend(frameon=False, loc="upper right", ncol=2, fontsize=8)
    return ax


def rejection_chart(df, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    b = an.rejection_reasons(df, "baseline").set_index("reason")["per_1000_submissions"]
    p = an.rejection_reasons(df, "pilot").set_index("reason")["per_1000_submissions"].reindex(b.index).fillna(0)
    y = range(len(b))
    ax.barh([i + 0.2 for i in y], b.values, 0.4, color=BASE_C, label="Baseline")
    ax.barh([i - 0.2 for i in y], p.values, 0.4, color=PILOT_C, label="Redesign pilot")
    ax.set_yticks(list(y)); ax.set_yticklabels(b.index, fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("Rejections per 1,000 submissions"); ax.set_title("Why documents are rejected")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    return ax


def trend_chart(df, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    w = an.weekly_conversion(df)
    ax.plot(w["week"], w["visit_to_funded"] * 100, marker="o", color=PILOT_C)
    ax.axvline(LAUNCH_WEEK - 0.5, ls="--", color="#b45309")
    ax.text(LAUNCH_WEEK - 0.4, ax.get_ylim()[0] + 0.5, "pilot launch", color="#b45309", fontsize=8)
    ax.set_xlabel("Week"); ax.set_ylabel("Visit to funded (%)"); ax.set_title("Weekly conversion")
    ax.set_xticks(range(1, 13))
    return ax


def dashboard_png(df, path: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    funnel_chart(df, axes[0, 0]); step_chart(df, axes[0, 1])
    rejection_chart(df, axes[1, 0]); trend_chart(df, axes[1, 1])
    k = an.kpis(df)
    fig.suptitle(
        f"FinFlow onboarding dashboard   |   visit-to-funded {k.loc['baseline','visit_to_funded']:.1%} -> "
        f"{k.loc['pilot','visit_to_funded']:.1%}   |   doc rejection {k.loc['baseline','document_rejection_rate']:.0%} -> "
        f"{k.loc['pilot','document_rejection_rate']:.0%}", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.005, NOTE + " (10,000 visitors per cohort). Not validated results.",
             ha="center", fontsize=9, color="#b91c1c")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(path, dpi=110)
    plt.close(fig)
