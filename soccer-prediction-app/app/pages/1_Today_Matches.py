"""Today's Matches - Streamlit Dashboard Page

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
    initial_sidebar_state="expanded",
)

# Custom CSS for terminal/hacker theme
st.markdown("""
<style>
/* Root theme variables */
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

/* Apply monospace font */
html, body, [class*="st"] {
    font-family: var(--mono-font), monospace;
}

/* Main background */
.main {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* Panels */
.divider, .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Metric cards */
.stMetric {
    background-color: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* Buttons */
.stButton > button {
    background-color: var(--accent-green);
    color: var(--bg-primary);
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: 500;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: var(--accent-cyan);
    color: var(--bg-primary);
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: var(--bg-panel);
    border: 1px solid var(--border);
    color: var(--text-primary);
}

/* Expander */
.stExpander {
    background-color: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 8px;
}

/* Warning/alert boxes */
.warning-box {
    background-color: rgba(251, 191, 36, 0.1);
    border: 1px solid var(--warning-amber);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}
.risk-box {
    background-color: rgba(248, 113, 113, 0.1);
    border: 1px solid var(--risk-red);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

/* Dataframe */
.dataframe tbody tr {
    background-color: var(--bg-panel);
}
.dataframe th, .dataframe td {
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)


def status_bar(last_update, model_version, data_freshness):
    """Display status bar at bottom of page."""
    st.markdown(
        f"""
        <div class="status-bar">
            <span>📅 Last update: {last_update}</span>
            <span>🤖 Model: {model_version}</span>
            <span>📊 Data: {data_freshness}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def primary_metric(label, value, help_text=None):
    """Display a primary metric card."""
    st.metric(label=label, value=value, help=help_text)


def risk_warning(text):
    """Display a risk warning box."""
    st.markdown(
        f'<div class="risk-box"><strong>⚠️</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def main():
    """Main function for today's matches page."""
    # Status bar
    status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model_version="1.0.0",
        data_freshness="Live fixtures"
    )

    # Page header
    st.title("⚽ Today's Matches")
    st.markdown("### English Premier League - Fixtures & Predictions")

    # Sidebar controls
    st.sidebar.header("Filters")
    league = st.sidebar.selectbox("League", ["EPL", "Bundesliga", "Serie A"])
    min_confidence = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 20)
    show_suggestions = st.sidebar.checkbox("Show Value Suggestions", value=True)

    # Main content area
    st.markdown("### Today's Fixtures")

    # Create sample fixture data (would be loaded from ingestion in production)
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
                primary_metric("Home", f"{row['Home Odds']:.2f}",
                              help=f"Implied probability: {1 / float(row['Home Odds']) * 100:.1f}%")

            with cols[2]):
                primary_metric("Draw", f"{row['Draw Odds']:.2f}",
                              help=f"Implied probability: {1 / float(row['Draw Odds']) * 100:.1f}%")

            with cols[3]):
                primary_metric("Away", f"{row['Away Odds']:.2f}",
                              help=f"Implied probability: {1 / float(row['Away Odds']) * 100:.1f}%")

            # Prediction section
            st.markdown("#### Prediction")

            # Value detection
            if show_suggestions:
                from src.suggestions import detect_value_suggestions

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
                    for s in suggestions[:2]:  # Show top 2
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

    # Footer with model info
    st.markdown("---")
    with st.expander("Model Information"):
        st.markdown(
            """
            **Prediction Engine:** Poisson/Dixon-Coles statistical model  
            **Model Version:** 1.0.0  
            **Training Data:** Historical match results  
            **Features:** Attack/defense ratings, home advantage, rest days, venue effects  
            **Evaluation:** Log loss, Brier score, calibration curves on chronological backtests  
            
            *Disclaimer: Predictions are for informational purposes only. No gambling advice provided. 
            Always gamble responsibly.*"""
        )


    # Run status bar
    status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


if __name__ == "__main__":
    main()