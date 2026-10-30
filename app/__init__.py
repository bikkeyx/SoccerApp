"""Soccer Prediction App - Streamlit Multi-Page Application."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Freebuff Soccer Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom theme CSS
st.markdown("""
<style>
:root {
    --bg-primary: #0B0F14;
    --bg-panel: #151B22;
    --text-primary: #D7E3EE;
    --text-muted: #7C8B99;
    --accent-green: #4ADE80;
    --accent-cyan: #38BDF8;
    --warning-amber: #FBBF24;
    --risk-red: #F87171;
    --border: #22303B;
    --mono-font: 'JetBrains Mono', 'Fira Code', monospace;
}
html, body, [class*="st"] { font-family: var(--mono-font), monospace; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    st.sidebar.title("📋 Navigation")
    st.sidebar.markdown("---")

    # Page selection
    page = st.sidebar.radio(
        "Go to",
        [
            "Today's Matches",
            "Match Analysis",
            "Team Profiles",
            "Predictions",
            "Suggestions",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Model: 1.0.0 | Data: {datetime.now().strftime('%Y-%m-%d')}")

    # Route to the selected page
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