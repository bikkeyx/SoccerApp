"""Main Streamlit entry point for soccer-prediction-app."""

import streamlit as st
from app.theme import BACKGROUND_COLOR, PANEL_BACKGROUND, PRIMARY_TEXT, MUTED_TEXT, ACCENT_GREEN, SECONDARY_ACCENT, WARNING_AMBER, RISK_RED, BORDER_DIVIDER, FONT_FAMILY

# Apply theme
st.set_page_config(
    page_title="Soccer Prediction App",
    page_icon="⚽",
    layout="wide",
)

# Terminal-style custom CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {PRIMARY_TEXT};
    }}
    .metric-card {{
        background: {PANEL_BACKGROUND};
        border: 1px solid {BORDER_DIVIDER};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    .stButton > button {{
        background: {ACCENT_GREEN};
        color: {PANEL_BACKGROUND};
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚽ Soccer Prediction App")
st.markdown("#### Terminal Hacker Style - Phase 0: Project Setup")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Fixtures", "Standings", "Predictions"])

if page == "Home":
    st.header("Welcome")
    st.markdown("Phase 0: Project Setup and Foundations")
    st.markdown("- Project structure created")
    st.markdown("- Terminal theme applied")
    st.markdown("- Dependencies installed")
elif page == "Fixtures":
    st.header("Fixtures")
    st.markdown("Phase 1: Coming soon - fixture ingestion")
elif page == "Standings":
    st.header("Standings")
    st.markdown("Phase 1: Coming soon - league standings")
elif page == "Predictions":
    st.header("Predictions")
    st.markdown("Phase 5: Coming soon - prediction engine")
