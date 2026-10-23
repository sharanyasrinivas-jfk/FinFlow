"""FinFlow onboarding lab - Streamlit dashboard.  Run: streamlit run app.py"""
from pathlib import Path

import pandas as pd
import streamlit as st

from src import analytics as an
from src import charts, recommendations as rec
from src.data_generator import generate

DATA = Path("data/onboarding_applications.csv")

st.set_page_config(page_title="FinFlow onboarding lab", layout="wide")
st.title("FinFlow onboarding lab")
st.error("All figures come from a SIMULATED dataset (10,000 visitors per cohort). "
         "They are hypotheses to test, not validated findings.")


@st.cache_data
def get_data(path: str) -> pd.DataFrame:
    return an.load(path) if Path(path).exists() else generate()


uploaded = st.sidebar.file_uploader("Use your own CSV (same schema)", type="csv")
df = pd.read_csv(uploaded) if uploaded else get_data(str(DATA))
device = st.sidebar.radio("Device", ["all", "mobile", "web"])
d = an.filter_data(df, device)

tab1, tab2, tab3 = st.tabs(["Funnel dashboard", "Prioritization", "A/B test planner"])

with tab1:
    k = an.kpis(d)
    b, p = k.loc["baseline"], k.loc["pilot"]
    c = st.columns(4)
    c[0].metric("Visit to funded", f"{p.visit_to_funded:.1%}", f"{(p.visit_to_funded-b.visit_to_funded)*100:+.1f} pp")
    c[1].metric("Application completion", f"{p.application_completion:.0%}", f"{(p.application_completion-b.application_completion)*100:+.0f} pp")
    c[2].metric("Document rejection", f"{p.document_rejection_rate:.0%}", f"{(p.document_rejection_rate-b.document_rejection_rate)*100:+.0f} pp", delta_color="inverse")
    c[3].metric("Median verification (h)", f"{p.median_verification_hours:.0f}", f"{p.median_verification_hours-b.median_verification_hours:+.0f} h", delta_color="inverse")
    loss = an.biggest_loss_after_signup(d, "baseline")
    st.info(f"Biggest baseline loss after account creation: **{loss['from']} -> {loss['to']}** ({loss['loss']:.0%} lost).")
    left, right = st.columns(2)
    left.pyplot(charts.funnel_chart(d).figure); right.pyplot(charts.step_chart(d).figure)
    left.pyplot(charts.rejection_chart(d).figure); right.pyplot(charts.trend_chart(d).figure)
    st.subheader("Median hours per step")
    st.dataframe(pd.DataFrame({"baseline": an.median_hours(d, "baseline"),
                               "pilot": an.median_hours(d, "pilot")}).round(1))
    st.caption("Weeks 1-6 are the baseline cohort and weeks 7-12 the pilot cohort, so the trend is a "
               "before/after comparison, not a randomised test.")

with tab2:
    st.write("Score = reach % x impact (1-3) x confidence % / effort (person-weeks). "
             "Inputs are judgement calls (hypotheses).")
    st.dataframe(rec.score_features()[["rank", "feature", "reach_pct", "impact", "confidence_pct",
                                       "effort_weeks", "score", "decision", "rationale"]]
                 .round({"score": 1}), hide_index=True)

with tab3:
    st.write("Visitors needed per arm for a randomised test on visit-to-funded conversion.")
    base = st.number_input("Baseline conversion", 0.01, 0.99, 0.164, 0.001, format="%.3f")
    mde = st.slider("Minimum detectable lift (absolute, pp)", 0.5, 8.0, 2.0, 0.5) / 100
    power = st.select_slider("Power", [0.8, 0.85, 0.9], 0.8)
    n = an.sample_size_per_arm(base, mde, power=power)
    st.metric("Visitors per arm", f"{n:,}")
    st.caption(f"{2*n:,} total. Alpha 0.05, two-sided. At ~1,650 visitors/week in total, "
               f"that is about {2*n/1650:.1f} weeks of traffic.")
