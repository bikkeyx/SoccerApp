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
.main { background-color: var(--bg-primary); color: var(--text-primary); }
.stMetric { background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
.stButton > button { background-color: var(--accent-green); color: var(--bg-primary); border: none; padding: 0.5rem 1rem; border-radius: 4px; font-weight: 500; transition: all 0.2s; }
.stButton > button:hover { background-color: var(--accent-cyan); color: var(--bg-primary); }
.stSelectbox > div > div { background-color: var(--bg-panel); border: 1px solid var(--border); color: var(--text-primary); }
.stExpander { background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; }
.warning-box { background-color: rgba(251, 191, 36, 0.1); border: 1px solid var(--warning-amber); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
.risk-box { background-color: rgba(248, 113, 113, 0.1); border: 1px solid var(--risk-red); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


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
        from suggestions import detect_value_suggestions
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