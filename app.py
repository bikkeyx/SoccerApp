"""Soccer Prediction App - Streamlit Multi-Page Application.

Main entry point for the Streamlit multi-page application.
All modules are importable from the project root directory.
"""

import streamlit as st
import sys
import os

# Add project root to path for imports (ensure modules are findable)
# This is needed when running via: streamlit run app.py from project root
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

st.set_page_config(
    page_title="Freebuff Soccer Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom terminal hacker CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.sidebar.title("📋 Navigation")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Go to",
        ["Today's Matches", "Match Analysis", "Team Profiles", "Predictions", "Suggestions"],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Model: 1.0.0 | Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}")
    if page == "Today's Matches":
        from pages.Today_Matches import main as today_matches
        today_matches()
    elif page == "Match Analysis":
        from pages.Match_Analysis import main as match_analysis
        match_analysis()
    elif page == "Team Profiles":
        from pages.Team_Profiles import main as team_profiles
        team_profiles()
    elif page == "Predictions":
        from pages.Predictions import main as predictions
        predictions()
    elif page == "Suggestions":
        from pages.Suggestions import main as suggestions
        suggestions()


if __name__ == "__main__":
    main()