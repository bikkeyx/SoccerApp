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
        - Poisson-based attack/defense strength (goals per game vs league average)
        - Dixon-Coles low-score correction applied
        - Home advantage: +0.25 xG for home side
        - Context adjustments: Rest days, motivation, venue effects
        """)

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Updated after each match",
        model_version="2.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()
else:
    main()
