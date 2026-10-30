"""Model Performance - Streamlit Dashboard Page 8

Displays model performance metrics, calibration curves, and backtesting results.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Model Performance",
    page_icon="📈",
    layout="wide",
)

# Import theme variables
from app.theme import (
    BACKGROUND_COLOR, PANEL_BACKGROUND, PRIMARY_TEXT, MUTED_TEXT,
    ACCENT_GREEN, SECONDARY_ACCENT, WARNING_AMBER, RISK_RED,
    BORDER_DIVIDER, FONT_FAMILY
)

# Apply custom CSS
st.markdown(f"""
<style>
:root {{
    --bg-primary: {BACKGROUND_COLOR};
    --bg-panel: {PANEL_BACKGROUND};
    --text-primary: {PRIMARY_TEXT};
    --text-muted: {MUTED_TEXT};
    --accent-green: {ACCENT_GREEN};
    --accent-cyan: {SECONDARY_ACCENT};
    --warning-amber: {WARNING_AMBER};
    --risk-red: {RISK_RED};
    --border: {BORDER_DIVIDER};
    --mono-font: {FONT_FAMILY};
}}
html, body, [class*="st"] {{ font-family: var(--mono-font), monospace; }}
.main {{ background-color: var(--bg-primary); color: var(--text-primary); }}
.stMetric {{ background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }}
.stButton > button {{ background-color: var(--accent-green); color: var(--bg-primary); border: none; padding: 0.5rem 1rem; border-radius: 4px; font-weight: 500; transition: all 0.2s; }}
.stButton > button:hover {{ background-color: var(--accent-cyan); color: var(--bg-primary); }}
.stSelectbox > div > div {{ background-color: var(--bg-panel); border: 1px solid var(--border); color: var(--text-primary); }}
.stExpander {{ background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; }}
.warning-box {{ background-color: rgba(251, 191, 36, 0.1); border: 1px solid var(--warning-amber); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }}
.risk-box {{ background-color: rgba(248, 113, 113, 0.1); border: 1px solid var(--risk-red); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }}
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📈 Model Performance")
    st.markdown("### Model Calibration & Backtesting")

    # Sidebar - Model selection
    st.sidebar.header("Model Selector")
    model = st.sidebar.radio("Select Model", ["Poisson", "Poisson + Dixon-Coles", "Elo Ensemble", "ML Gradient Boosting"])

    # Main content
    st.markdown(f"### {model} Performance")

    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Log Loss", "0.645", "-0.012")
    with col2:
        st.metric("Brier Score", "0.218", "+0.003")
    with col3:
        st.metric("Calibration Error", "0.045", "-0.008")
    with col4:
        st.metric("Accuracy", "72.5%", "+1.2%")

    # Probability calibration chart
    st.markdown("#### Probability Calibration")
    st.markdown("*Model probability vs. actual frequency*")

    # Sample calibration data
    cal_data = pd.DataFrame({
        'Bin': ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
        'Model Prob': [5, 15, 25, 35, 45, 55, 65, 75, 85, 95],
        'Actual Rate': [4, 14, 27, 38, 44, 51, 62, 73, 82, 96]
    })
    st.bar_chart(cal_data.set_index('Bin'))

    # Backtesting results
    st.markdown("#### Chronological Backtesting (3 seasons)")
    backtest_data = pd.DataFrame({
        'Season': ['2021-22', '2022-23', '2023-24'],
        'Log Loss': [0.652, 0.641, 0.638],
        'Brier': [0.225, 0.219, 0.215],
        'ROI': [-0.15, -0.08, -0.03]
    })
    st.dataframe(backtest_data, hide_index=True, use_container_width=True)

    # Feature importance
    st.markdown("#### Top Features")
    features = pd.DataFrame({
        'Feature': ['Home Advantage', 'Attack Rating', 'Defense Rating', 'Recent Form', 'Rest Days', 'Travel Distance'],
        'Importance': [25.5, 22.3, 18.7, 15.2, 12.1, 6.2]
    })
    st.bar_chart(features.set_index('Feature'))

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Model retrained monthly",
        model_version="1.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()