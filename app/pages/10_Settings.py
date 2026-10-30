"""Settings - Streamlit Dashboard Page 10

App settings, preferences, and configuration.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
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
</style>
""", unsafe_allow_html=True)


def main():
    st.title("⚙️ Settings")
    st.markdown("### App Preferences & Configuration")

    # Sidebar
    st.sidebar.header("Settings Categories")
    category = st.sidebar.radio("Category", [
        "General", "Predictions", "Suggestions", "Data", "Appearance"
    ])

    # Main content based on selection
    if category == "General":
        st.markdown("### General Settings")
        st.checkbox("Show status bar at bottom", value=True)
        st.checkbox("Use monospace font", value=True)
        st.selectbox("Font size", ["Small", "Medium", "Large"], index=1)
        st.slider("Default confidence threshold", 0.0, 0.2, 0.05, 0.01)

    elif category == "Predictions":
        st.markdown("### Prediction Settings")
        st.slider("Minimum edge %", 0, 20, 5)
        st.slider("Minimum probability %", 0, 100, 20)
        st.checkbox("Include context adjustments", value=True)
        st.selectbox("Model version", ["2.0.0", "1.0.0"], index=0)

    elif category == "Suggestions":
        st.markdown("### Suggestion Filters")
        st.slider("Minimum edge for suggestions %", 0, 20, 5)
        st.slider("Minimum probability for suggestions %", 0, 100, 20)
        st.selectbox("Confidence display", ["Always", "High only", "Never"], index=0)
        st.checkbox("Track hypothetical outcomes", value=False)

    elif category == "Data":
        st.markdown("### Data Settings")
        st.selectbox("Data source", ["football-data.org", "FBref", "Understat"])
        st.slider("Cache TTL (hours)", 1, 48, 24)
        st.checkbox("Auto-refresh data", value=True)
        st.selectbox("Refresh schedule", ["Daily", "Every 12h", "Every 24h"], index=0)

    elif category == "Appearance":
        st.markdown("### Appearance Settings")
        st.selectbox("Theme", ["Terminal Hacker (default)", "Light", "Dark"], index=0)
        st.color_picker("Accent color", "#4ADE80")
        st.checkbox("Show borders around panels", value=True)
        st.selectbox("Monospace font", ["JetBrains Mono", "Fira Code", "Consolas"], index=0)

    # Save button
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save Settings", type="primary"):
            st.success("Settings saved!")
    with col2:
        if st.button("Reset to Default"):
            st.info("Settings reset to default")

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Settings stored locally",
        model_version="2.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()
else:
    main()
