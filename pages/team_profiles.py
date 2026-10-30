"""Team Profiles - Streamlit Dashboard Page 3

Displays team statistics, form guides, and profile information.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Team Profiles",
    page_icon="👥",
    layout="wide",
)

# Custom CSS theme
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
    st.title("👥 Team Profiles")
    st.markdown("### Team Statistics & Form Guide")

    # Sidebar - Team select
    st.sidebar.header("Team Selector")
    team = st.sidebar.selectbox("Select Team", [
        "Arsenal", "Manchester United", "Liverpool", "Manchester City",
        "Chelsea", "Tottenham", "Newcastle", "Brighton"
    ])

    # Main content
    st.markdown(f"### {team} Profile")

    # Get historical data (simulated)
    with st.spinner("Loading team data..."):
        # Would load from historical match database
        pass

    # Team statistics columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Games Played", "38", help="Total league games")
    with col2:
        st.metric("Win Rate", "65.5%", help="Win percentage")
    with col3:
        st.metric("Goals Scored", "82", help="Total goals for")
    with col4:
        st.metric("Goals Conceded", "36", help="Total goals against")

    # Form guide - last 5 matches
    st.markdown("#### Last 5 Matches")
    form_data = pd.DataFrame({
        'Date': ['2024-11-24', '2024-11-10', '2024-11-03', '2024-10-20', '2024-10-05'],
        'Opponent': ['Liverpool', 'Chelsea', 'Tottenham', 'Everton', 'Man City'],
        'Result': ['W', 'D', 'W', 'L', 'W'],
        'GF': [2, 1, 3, 1, 2],
        'GA': [1, 1, 2, 3, 1]
    })

    st.dataframe(form_data, hide_index=True, use_container_width=True)

    # Key players section
    st.markdown("#### Key Players")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Attack**")
        st.markdown("- Saka (12 goals)\n- Son (10 goals)\n- Haaland (18 goals)")
    with col2:
        st.markdown("**Defense**")
        st.markdown("- Saliba (8 clean sheets)\n- Van Dijk (7 clean sheets)\n- Rice (6 interceptions)")

    # Form analysis
    st.markdown("#### Form Analysis")
    st.markdown("""
    **Recent Form:** W-D-W-W-L  
    **Home Form:** W-W-W-W-D (5 games)  
    **Away Form:** W-L-W-W-L (5 games)  
    **Goals Trend:** Scoring 1.8 GF per game (last 5)  
    **Conceding Trend:** Conceding 1.4 GA per game (last 5)
    """)

    # Model explanation
    with st.expander("Model Explanation"):
        st.markdown("""
        **How ratings are calculated:**
        - Elo-based rating system (K-factor: 32)
        - Home advantage: +1.12 multiplier
        - Attack/defense strength: Ratio-based
        - Recent form: Last 5 matches weighted more heavily
        - Context adjustments: Rest days, motivation, venue effects
        """)

    # Status bar
    status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model_version="1.0.0",
        data_freshness="Updated after each match"
    )


if __name__ == "__main__":
    main()