"""League Standings - Streamlit Dashboard Page 7

Displays league tables and standings.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="League Standings",
    page_icon="📊",
    layout="wide",
)

# Import theme variables
from app.theme import (
    BACKGROUND_COLOR, PANEL_BACKGROUND, PRIMARY_TEXT, MUTED_TEXT,
    ACCENT_GREEN, SECONDARY_ACCENT, WARNING_AMBER, RISK_RED,
    BORDER_DIVIDER, FONT_FAMILY
)

# Apply custom CSS
st.markdown(f"""
<style>
:root {{
    --bg-primary: {BACKGROUND_COLOR};
    --bg-panel: {PANEL_BACKGROUND};
    --text-primary: {PRIMARY_TEXT};
    --text-muted: {MUTED_TEXT};
    --accent-green: {ACCENT_GREEN};
    --accent-cyan: {SECONDARY_ACCENT};
    --warning-amber: {WARNING_AMBER};
    --risk-red: {RISK_RED};
    --border: {BORDER_DIVIDER};
    --mono-font: {FONT_FAMILY};
}}
html, body, [class*="st"] {{ font-family: var(--mono-font), monospace; }}
.main {{ background-color: var(--bg-primary); color: var(--text-primary); }}
.stMetric {{ background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }}
.stButton > button {{ background-color: var(--accent-green); color: var(--bg-primary); border: none; padding: 0.5rem 1rem; border-radius: 4px; font-weight: 500; transition: all 0.2s; }}
.stButton > button:hover {{ background-color: var(--accent-cyan); color: var(--bg-primary); }}
.stSelectbox > div > div {{ background-color: var(--bg-panel); border: 1px solid var(--border); color: var(--text-primary); }}
.stExpander {{ background-color: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; }}
.warning-box {{ background-color: rgba(251, 191, 36, 0.1); border: 1px solid var(--warning-amber); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }}
.risk-box {{ background-color: rgba(248, 113, 113, 0.1); border: 1px solid var(--risk-red); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }}
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📊 League Standings")
    st.markdown("### Premier League Table")

    # Sidebar - League select
    st.sidebar.header("League Selector")
    league = st.sidebar.selectbox("League", ["EPL", "Bundesliga", "Serie A", "Ligue 1", "Bundesliga"])

    # Main content
    st.markdown(f"### {league} Table")

    # Sample standings data
    standings_data = pd.DataFrame({
        'Pos': [1, 2, 3, 4, 5, 6, 7, 8],
        'Team': ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Aston Villa', 'Newcastle', 'Spurs', 'Man Utd'],
        'P': [38, 38, 38, 38, 38, 38, 38, 38],
        'W': [28, 25, 24, 22, 20, 18, 17, 15],
        'D': [8, 10, 10, 12, 10, 12, 12, 13],
        'L': [2, 3, 4, 4, 8, 8, 9, 10],
        'GD': [+65, +58, +52, +41, +30, +28, +22, +15],
        'Pts': [92, 85, 82, 78, 70, 66, 63, 58]
    })

    # Format dataframe display
    st.dataframe(
        standings_data,
        column_config={
            "Pos": st.column_config.NumberColumn("Pos", width="small"),
            "Team": st.column_config.TextColumn("Team", width="medium"),
            "P": st.column_config.NumberColumn("P", width="small"),
            "W": st.column_config.NumberColumn("W", width="small"),
            "D": st.column_config.NumberColumn("D", width="small"),
            "L": st.column_config.NumberColumn("L", width="small"),
            "GD": st.column_config.NumberColumn("GD", width="small"),
            "Pts": st.column_config.NumberColumn("Pts", width="medium")
        },
        hide_index=True,
        use_container_width=True
    )

    # Additional info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Games Played", "38")
    with col2:
        st.metric("Top Scorer", "S. Kane", "24 goals")
    with col3:
        st.metric("Goal Difference", "+65")

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Updated after each matchday",
        model_version="1.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()