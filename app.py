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

    # Import and run the selected page using app.pages module path
    import importlib

    if page == "Today's Matches":
        mod = importlib.import_module("app.pages.Today_Matches")
        mod.main()
    elif page == "Match Analysis":
        mod = importlib.import_module("app.pages.Match_Analysis")
        mod.main()
    elif page == "Team Profiles":
        mod = importlib.import_module("app.pages.Team_Profiles")
        mod.main()
    elif page == "Predictions":
        mod = importlib.import_module("app.pages.Predictions")
        mod.main()
    elif page == "Suggestions":
        mod = importlib.import_module("app.pages.Suggestions")
        mod.main()


if __name__ == "__main__":
    main()