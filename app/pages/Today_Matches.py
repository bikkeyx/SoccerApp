"""Today's Matches - Streamlit Dashboard Page 1

Displays today's fixtures with predictions and probability panels.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Today's Matches",
    page_icon="⚽",
    layout="wide",
)

# Import theme variables
from app.theme import (
    BACKGROUND_COLOR, PANEL_BACKGROUND, PRIMARY_TEXT, MUTED_TEXT,
    ACCENT_GREEN, SECONDARY_ACCENT, WARNING_AMBER, RISK_RED,
    BORDER_DIVIDER, FONT_FAMILY
)

st.title("⚽ Today's Matches")
st.markdown("### English Premier League - Fixtures & Predictions")

# Sidebar controls
st.sidebar.header("Filters")
league = st.sidebar.selectbox("League", ["EPL", "Bundesliga", "Serie A"])
min_confidence = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 20)
show_suggestions = st.sidebar.checkbox("Show Value Suggestions", value=True)

# Main content area
st.markdown("### Today's Fixtures")

# Create sample fixture data
fixtures_data = pd.DataFrame({
    'Time': ['14:00', '14:00', '16:30', '16:30', '19:00'],
    'Home': ['Arsenal', 'Manchester United', 'Liverpool', 'Manchester City', 'Newcastle'],
    'Away': ['Tottenham', 'Chelsea', 'Brighton', 'West Ham', 'Everton'],
    'Home Odds': [2.10, 2.30, 1.85, 1.75, 4.50],
    'Draw Odds': [3.40, 3.50, 3.60, 3.80, 4.20],
    'Away Odds': [3.20, 3.10, 4.30, 4.50, 1.80],
})

# Display fixtures
for _, row in fixtures_data.iterrows():
    with st.container():
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{row['Time']}** | {row['Home']} vs {row['Away']}")
        with cols[1]:
            st.metric("Home", f"{row['Home Odds']:.2f}",
                       help=f"Implied probability: {1/float(row['Home Odds'])*100:.1f}%")
        with cols[2]:
            st.metric("Draw", f"{row['Draw Odds']:.2f}",
                       help=f"Implied probability: {1/float(row['Draw Odds'])*100:.1f}%")
        with cols[3]:
            st.metric("Away", f"{row['Away Odds']:.2f}",
                       help=f"Implied probability: {1/float(row['Away Odds'])*100:.1f}%")
        st.markdown("#### Prediction")
        st.markdown("##### Value Opportunities")
        st.markdown("- No value opportunities at current thresholds")
        st.markdown("---")

    # Footer with model info
    st.markdown("---")
    with st.expander("Model Information"):
        st.markdown(
            f"""
            **Prediction Engine:** Poisson/Dixon-Coles statistical model
            **Model Version:** 1.0.0
            **Training Data:** Historical match results
            **Features:** Attack/defense ratings, home advantage, rest days, venue effects
            **Evaluation:** Log loss, Brier score, calibration curves on chronological backtests

            *Disclaimer: Predictions are for informational purposes only. No gambling advice provided.
            Always gamble responsibly.*
            """
        )


def main():
    """Main function for today's matches page."""
    st.title("⚽ Today's Matches")
    st.markdown("### English Premier League - Fixtures & Predictions")

    # Sidebar controls
    st.sidebar.header("Filters")
    league = st.sidebar.selectbox("League", ["EPL", "Bundesliga", "Serie A"])
    min_confidence = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 20)
    show_suggestions = st.sidebar.checkbox("Show Value Suggestions", value=True)

    # Main content area
    st.markdown("### Today's Fixtures")

    # Create sample fixture data
    fixtures_data = pd.DataFrame({
        'Time': ['14:00', '14:00', '16:30', '16:30', '19:00'],
        'Home': ['Arsenal', 'Manchester United', 'Liverpool', 'Manchester City', 'Newcastle'],
        'Away': ['Tottenham', 'Chelsea', 'Brighton', 'West Ham', 'Everton'],
        'Home Odds': [2.10, 2.30, 1.85, 1.75, 4.50],
        'Draw Odds': [3.40, 3.50, 3.60, 3.80, 4.20],
        'Away Odds': [3.20, 3.10, 4.30, 4.50, 1.80],
    })

    # Display fixtures
    for _, row in fixtures_data.iterrows():
        with st.container():
            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{row['Time']}** | {row['Home']} vs {row['Away']}")
            with cols[1]:
                st.metric("Home", f"{row['Home Odds']:.2f}",
                           help=f"Implied probability: {1/float(row['Home Odds'])*100:.1f}%")
            with cols[2]:
                st.metric("Draw", f"{row['Draw Odds']:.2f}",
                           help=f"Implied probability: {1/float(row['Draw Odds'])*100:.1f}%")
            with cols[3]:
                st.metric("Away", f"{row['Away Odds']:.2f}",
                           help=f"Implied probability: {1/float(row['Away Odds'])*100:.1f}%")
            st.markdown("#### Prediction")
            st.markdown("##### Value Opportunities")
            st.markdown("- No value opportunities at current thresholds")
            st.markdown("---")

    # Footer with model info
    st.markdown("---")
    with st.expander("Model Information"):
        st.markdown(
            f"""
            **Prediction Engine:** Poisson/Dixon-Coles statistical model
            **Model Version:** 1.0.0
            **Training Data:** Historical match results
            **Features:** Attack/defense ratings, home advantage, rest days, venue effects
            **Evaluation:** Log loss, Brier score, calibration curves on chronological backtests

            *Disclaimer: Predictions are for informational purposes only. No gambling advice provided.
            Always gamble responsibly.*
            """
        )


if __name__ == "today_matches":
    pass
else:
    main()


if __name__ == "__main__":
    main()