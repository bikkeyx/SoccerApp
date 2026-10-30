"""Today's Matches - Streamlit Dashboard Page 1"""
import streamlit as st
import pandas as pd
import sys
from datetime import datetime

from prediction.engine import PredictionEngine
from suggestions import detect_value_suggestions


st.title("⚽ Today's Matches")
st.markdown("### English Premier League - Fixtures & Predictions")

status_bar(last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
           model_version="1.0.0",
           data_freshness="Live fixtures")

st.sidebar.header("Filters")
league = st.sidebar.selectbox("League", ["EPL", "Bundesliga", "Serie A"])
min_confidence = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 20)
show_suggestions = st.sidebar.checkbox("Show Value Suggestions", value=True)

st.markdown("### Today's Fixtures")

fixtures_data = pd.DataFrame({
    'Time': ['14:00', '14:00', '16:30', '16:30', '19:00'],
    'Home': ['Arsenal', 'Manchester United', 'Liverpool', 'Manchester City', 'Newcastle'],
    'Away': ['Tottenham', 'Chelsea', 'Brighton', 'West Ham', 'Everton'],
    'Home Odds': [2.10, 2.30, 1.85, 1.75, 4.50],
    'Draw Odds': [3.40, 3.50, 3.60, 3.80, 4.20],
    'Away Odds': [3.20, 3.10, 4.30, 4.50, 1.80],
})

for _, row in fixtures_data.iterrows():
    with st.container():
        cols = st.columns([2, 1, 1, 1])

        with cols[0]:
            st.markdown(f"**{row['Time']}** | {row['Home']} vs {row['Away']}")

        with cols[1]:
            primary_metric("Home", f"{row['Home Odds']:.2f}",
                          help=f"Implied probability: {1/float(row['Home Odds'])*100:.1f}%")

        with cols[2]:
            primary_metric("Draw", f"{row['Draw Odds']:.2f}",
                          help=f"Implied probability: {1/float(row['Draw Odds'])*100:.1f}%")

        with cols[3]:
            primary_metric("Away", f"{row['Away Odds']:.2f}",
                          help=f"Implied probability: {1/float(row['Away Odds'])*100:.1f}%")

        st.markdown("#### Prediction")

        if show_suggestions:
            suggestions = detect_value_suggestions(
                {"prediction": {
                    "home_win_probability": 45.0,
                    "draw_probability": 25.0,
                    "away_win_probability": 30.0,
                }},
                home_odds=float(row['Home Odds']),
                draw_odds=float(row['Draw Odds']),
                away_odds=float(row['Away Odds']),
                min_edge=0.05,
                min_probability=0.20,
            )

            if suggestions:
                st.markdown("##### Value Opportunities")
                for s in suggestions[:2]:
                    st.markdown(
                        f"""
                        <div class="warning-box">
                            <strong>{s.selection}</strong> | 
                            Edge: {s.edge:.2f} | 
                            Confidence: {s.confidence}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("---")

status_bar(last_update=datetime.now().strftime("%Y-%m-%d %H:%M"))


if __name__ == "pages.1_Today_Matches":
    pass
else:
    status_bar(datetime.now().strftime("%Y-%m-%d %H:%M"))


if __name__ == "__main__":
    main()