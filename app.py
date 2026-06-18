"""
app.py

Streamlit UI for AI Timing Closure Assistant.

- Upload .rpt timing report
- TAB 1: Timing Analysis (histogram + counts)
- TAB 2: Ranked Violations (worst-first, recommended fixes)
- TAB 3: AI Prediction (logic depth & fanout -> predicted slack + risk)

Run:
  streamlit run app.py
"""
import streamlit as st
import matplotlib.pyplot as plt

from parser import parse_timing_report
from analyzer import analyze_paths
from recommender import recommend_fix
from ml_model import predict_slack

st.set_page_config(page_title="AI Timing Closure Assistant", layout="wide")

st.title("AI Timing Closure Assistant")
st.markdown("Upload STA timing reports and analyze violations using engineering rules + ML predictions.")
st.markdown("---")

uploaded = st.file_uploader("Upload timing report (.rpt or .txt)", type=["rpt", "txt"])

paths = []
if uploaded is not None:
    try:
        content = uploaded.getvalue()
        paths = parse_timing_report(content)
        st.success(f"Parsed {len(paths)} path(s)")
    except Exception as e:
        st.error(f"Failed to parse file: {e}")
        paths = []

# Tabs
tab1, tab2, tab3 = st.tabs(["Timing Analysis", "Ranked Violations", "AI Prediction"])

with tab1:
    st.header("Timing Analysis")
    if not paths:
        st.info("No timing data loaded. Upload a .rpt file to begin.")
    else:
        slacks = [p["slack"] for p in paths if p.get("slack") is not None]
        if not slacks:
            st.warning("No slack values found in the parsed report.")
        else:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(slacks, bins=40, color='tab:blue', edgecolor='black', alpha=0.7)
            ax.axvline(0.0, color='green', linestyle='--', label='Zero slack (target)')
            ax.axvline(-0.5, color='red', linestyle='--', label='Critical (-0.5)')
            ax.set_xlabel("Slack")
            ax.set_ylabel("Number of paths")
            ax.set_title("Slack distribution")
            ax.legend()
            st.pyplot(fig)

        violations, ok_paths = analyze_paths(paths)
        cols = st.columns(3)
        cols[0].metric("Total paths", len(paths))
        cols[1].metric("Violations (slack < 0)", len(violations))
        cols[2].metric("OK paths (slack >= 0)", len(ok_paths))

with tab2:
    st.header("Ranked Violations (Worst First)")
    violations, ok_paths = analyze_paths(paths)
    if not violations:
        st.success("No timing violations detected.")
    else:
        n_show = st.slider("Number of top violations to show", min_value=1, max_value=min(200, len(violations)), value=min(20, len(violations)))
        st.write(f"Showing top {n_show} worst violations (most negative slack first):")
        for i, v in enumerate(violations[:n_show]):
            s = v.get('slack')
            s_text = f"{s:.3f}" if isinstance(s, (float, int)) else str(s)
            st.subheader(f"Rank {i+1} — Slack: {s_text}")
            st.write(f"Arrival: {v.get('arrival')}")
            st.write(f"Required: {v.get('required')}")
            fixes = recommend_fix(v)
            st.write("Suggested fixes:")
            for f in fixes:
                st.write("-", f)
            st.markdown("---")

with tab3:
    st.header("AI Prediction")
    st.write("Predict slack from design parameters (logic depth, fanout).")

    depth = st.slider("Logic Depth", min_value=1, max_value=300, value=20)
    fanout = st.slider("Fanout", min_value=1, max_value=200, value=10)

    if st.button("Predict Slack"):
        pred = predict_slack(depth, fanout)
        st.write("Predicted slack:", f"{pred:.4f}")
        if pred < 0:
            st.error("Risk level: HIGH (timing violation expected)")
        elif pred < 0.2:
            st.warning("Risk level: MEDIUM")
        else:
            st.success("Risk level: LOW (safe design)")

st.markdown("---")
st.caption("AI Timing Closure Assistant — simple EDA helper for STA reports.")
