"""Predictions - Streamlit Dashboard Page 4"""
import streamlit as st
import pandas as pd
import sys
from datetime import datetime

st.set_page_config(
    page_title="Predictions",
    page_icon="🎯",
    layout="wide",
)

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
.stSelectbox > div > div { background-color: var(--bg-panel); border: 1px solid var(--border); color: var(--text-primary); }
.stExpander { background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; }
.warning-box { background-color: rgba(251, 191, 36, 0.1); border: 1px solid var(--warning-amber); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
.risk-box { background-color: rgba(248, 113, 113, 0.1); border: 1px solid var(--risk-red); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("🎯 Predictions")
    st.markdown("### Match Predictions & Probability Panels")

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

    engine = st.session_state.get('engine')
    if engine is None:
        from prediction.engine import PredictionEngine
        engine = PredictionEngine()
        st.session_state['engine'] = engine

    with st.spinner("Computing prediction..."):
        pred = engine.predict_match(home_team, away_team)

    st.markdown("#### Match Outcome Probabilities")

    col1, col2, col3 = st.columns(3)
    with col1:
        figure = st.progress(float(pred['prediction']['home_win_probability']) / 100)
        st.metric("Home Win", f"{pred['prediction']['home_win_probability']:.1f}%")
    with col2:
        figure = st.progress(float(pred['prediction']['draw_probability']) / 100)
        st.metric("Draw", f"{pred['prediction']['draw_probability']:.1f}%")
    with col3:
        figure = st.progress(float(pred['prediction']['away_win_probability']) / 100)
        st.metric("Away Win", f"{pred['prediction']['away_win_probability']:.1f}%")

    st.markdown("#### Expected Goals Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**{home_team}**: {pred['expected_goals']['home']:.2f} xG")
    with col2:
        st.info(f"**{away_team}**: {pred['expected_goals']['away']:.2f} xG")

    st.markdown(f"**Most Likely Scoreline:** {pred['most_likely_scoreline']}")

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

    from suggestions import detect_value_suggestions, format_suggestion
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
            st.markdown(format_suggestion(s), unsafe_allow_html=True)
    else:
        st.info("No value opportunities at current thresholds (edge > 5%, probability > 20%).")

    with st.expander("Model Details"):
        st.markdown("""
        - **Model:** Poisson + Elo Ensemble (50/50 weight)
        - **Home Advantage:** 1.12x multiplier
        - **Feature Set:** 20+ statistical features
        - **Training:** Chronological backtesting
        - **Metrics:** Log Loss, Brier Score, Calibration
        - **Backtest Period:** 3 seasons (historical data)
        """)

    status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model_version="1.0.0",
        data_freshness="Live predictions"
    )


if __name__ == "__main__":
    main()