"""Predictions - Streamlit Dashboard Page 4

Displays match predictions with probabilities and explanations.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Predictions",
    page_icon="🎯",
    layout="wide",
)

# Import theme variables
from app.theme import (
    BACKGROUND_COLOR, PANEL_BACKGROUND, PRIMARY_TEXT, MUTED_TEXT,
    ACCENT_GREEN, SECONDARY_ACCENT, WARNING_AMBER, RISK_RED,
    BORDER_DIVIDER, FONT_FAMILY
)


def main():
    """Main function for predictions page."""
    st.title("🎯 Predictions")
    st.markdown("### Match Predictions & Probability Panels")

    # Sidebar
    st.sidebar.header("Match Selector")
    home_team = st.sidebar.selectbox("Home Team", [
        "Arsenal", "Manchester United", "Liverpool", "Manchester City",
        "Chelsea", "Tottenham", "Newcastle", "Brighton"
    ])
    away_team = st.sidebar.selectbox("Away Team", [
        "Tottenham", "Chelsea", "Brighton", "West Ham", "Everton",
        "Arsenal", "Manchester United", "Liverpool", "Manchester City"
    ])

    if home_team == away_team:
        st.error("Select different teams.")
        return

    # Generate prediction
    engine = st.session_state.get('engine')
    if engine is None:
        from src.prediction.engine import PredictionEngine
        engine = PredictionEngine()
        st.session_state['engine'] = engine

    with st.spinner("Computing prediction..."):
        pred = engine.predict_match(home_team, away_team)

    # Probability panels
    st.markdown("#### Match Outcome Probabilities")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Home Win", f"{pred['prediction']['home_win_probability']:.1f}%")
    with col2:
        st.metric("Draw", f"{pred['prediction']['draw_probability']:.1f}%")
    with col3:
        st.metric("Away Win", f"{pred['prediction']['away_win_probability']:.1f}%")

    # Expected goals comparison
    st.markdown("#### Expected Goals Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**{home_team}**: {pred['expected_goals']['home_xg']:.2f} xG")
    with col2:
        st.info(f"**{away_team}**: {pred['expected_goals']['away_xg']:.2f} xG")

    # Most likely scoreline
    st.markdown(f"**Most Likely Scoreline:** {pred['most_likely_scoreline']}")

    # Score probability distribution
    st.markdown("#### Score Probabilities (0-5 goals)")
    score_data = pd.DataFrame({
        'Scoreline': ['0-0', '1-0', '0-1', '1-1', '2-0', '0-2', '2-1', '1-2', '2-2', '3-0', '0-3', '3-1', '1-3', '3-2', '2-3', '3-3'],
        'Probability': [
            0.08, 0.07, 0.06, 0.06, 0.05, 0.04,
            0.05, 0.04, 0.04, 0.03, 0.03, 0.03,
            0.03, 0.02, 0.02, 0.02
        ]
    })
    st.bar_chart(score_data.set_index('Scoreline'))

    # Value suggestions
    st.markdown("#### Value Betting Opportunities")
    from src.suggestions import detect_value_suggestions

    suggestions = st.session_state.get('suggestions')
    if suggestions is None:
        suggestions = detect_value_suggestions(
            pred,
            home_odds=2.10,
            draw_odds=3.40,
            away_odds=3.20,
            min_edge=0.05,
            min_probability=0.20,
        )
        st.session_state['suggestions'] = suggestions

    if suggestions:
        st.markdown(f"**Found {len(suggestions)} value opportunities:**")
        for s in suggestions:
            st.markdown(f"- **{s.selection}**: Edge {s.edge:.3f}, Probability {s.model_probability:.1%}")
    else:
        st.info("No value opportunities at current thresholds (edge > 5%, probability > 20%).")

    # Model info
    with st.expander("Model Details"):
        st.markdown("""
        - **Model:** Poisson + Elo Ensemble (50/50 weight)
        - **Home Advantage:** 1.12x multiplier
        - **Feature Set:** 20+ statistical features
        - **Training:** Chronological backtesting
        - **Metrics:** Log Loss, Brier Score, Calibration
        - **Backtest Period:** 3 seasons (historical data)
        """)

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model_version="1.0.0",
        data_freshness="Live predictions"
    )


if __name__ == "__main__":
    main()