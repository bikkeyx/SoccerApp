"""Match Analysis - Streamlit Dashboard Page 2

Analyzes a specific match with detailed statistics and predictions.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Match Analysis",
    page_icon="📊",
    layout="wide",
)

# Custom CSS (same theme as Today_Matches)
<style>
/* Import theme from style.css -- do not redefine variables here */
</style>



def main():
    st.title("📊 Match Analysis")
    st.markdown("### Detailed Match Analysis & Prediction")

    # Sidebar - Select match
    st.sidebar.header("Match Selector")
    home_team = st.sidebar.selectbox("Home Team", ["Arsenal", "Manchester United", "Liverpool", "Manchester City", "Chelsea", "Tottenham", "Newcastle", "Brighton", "West Ham", "Everton"])
    away_team = st.sidebar.selectbox("Away Team", ["Tottenham", "Chelsea", "Brighton", "West Ham", "Everton", "Arsenal", "Manchester United", "Liverpool", "Manchester City"])

    if home_team == away_team:
        st.error("Please select different teams for home and away.")
        return

    # Main content
    st.markdown(f"### {home_team} vs {away_team}")

    # prediction engine
    engine = st.session_state.get('engine')
    if engine is None:
        engine = PredictionEngine()
        st.session_state['engine'] = engine

    # Train on historical data (simulated)
    with st.spinner("Loading model..."):
        # Would train on real historical data
        pass

    # Prediction
    pred = engine.predict_match(home_team, away_team)

    # Prediction probabilities
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Home Win", f"{pred['prediction']['home_win_probability']:.1f}%",
                  help=f"Model predicted probability")
    with col2:
        st.metric("Draw", f"{pred['prediction"]["draw_probability']:.1f}%",
                 help=f"Model predicted probability")
    with col3:
        st.metric("Away Win", f"{pred['prediction']['away_win_probability']:.1f}%",
                 help=f"Model predicted probability")

    # Expected goals
    st.markdown("#### Expected Goals")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"{home_team} xG", f"{pred['expected_goals']['home']:.2f}")
    with col2:
        st.metric(f"{away_team} xG", f"{pred['expected_goals']['away']:.2f}")

    # Most likely scoreline
    st.markdown(f"**Most Likely Scoreline:** {pred['most_likely_scoreline']}")

    # Value suggestions
    st.markdown("#### Value Betting Opportunities")
    suggestions = st.session_state.get('suggestions')
    if suggestions is None:
        from src.suggestions import detect_value_suggestions
        suggestions = detect_value_suggestions(
            pred,
            home_odds=2.10,  # Would come from real odds data
            draw_odds=3.40,
            away_odds=3.20,
            min_edge=0.05,
            min_probability=0.20,
        )
        st.session_state['suggestions'] = suggestions

    if suggestions:
        for s in suggestions[:3]:
            st.markdown(
                f'<div class="warning-box"><strong>{s.selection}</strong> | Edge: {s.edge:.2f} | Confidence: {s.confidence}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No value opportunities detected at current thresholds.")


if __name__ == "__main__":
    main()