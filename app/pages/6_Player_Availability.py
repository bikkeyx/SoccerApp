"""Player Availability - Streamlit Dashboard Page 6

Displays player availability, likely starters, squad depth, and injury impact.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Player Availability",
    page_icon="👥",
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
    st.title("👥 Player Availability")
    st.markdown("### Squad Depth & Injury Tracker")

    # Sidebar - Team select
    st.sidebar.header("Team Selector")
    team = st.sidebar.selectbox("Select Team", [
        "Arsenal", "Manchester United", "Liverpool", "Manchester City",
        "Chelsea", "Tottenham", "Newcastle", "Brighton"
    ])

    # Main content
    st.markdown(f"### {team} Squad")

    # Availability status
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Fit Players", "22", help="Available for selection")
    with col2:
        st.metric("Injured", "4", help="Current injuries")
    with col3:
        st.metric("Suspended", "1", help="Suspended matches")

    # Injury list
    st.markdown("#### Injury List")
    injury_data = pd.DataFrame({
        'Player': ['Player A', 'Player B', 'Player C', 'Player D'],
        'Injury': ['Hamstring', 'Ankle', 'Knee', 'Groin'],
        'Expected Return': ['2024-12-15', '2024-12-01', '2024-12-20', '2024-12-10'],
        'Status': [' doubtful', 'questionable', 'out', 'doubtful']
    })
    st.dataframe(injury_data, hide_index=True, use_container_width=True)

    # Suspension list
    st.markdown("#### Suspension List")
    suspension_data = pd.DataFrame({
        'Player': ['Player E'],
        'Reason': ['Yellow card accumulation'],
        'Missing Matches': ['3']
    })
    st.dataframe(suspension_data, hide_index=True, use_container_width=True)

    # Squad depth
    st.markdown("#### Squad Depth by Position")
    depth_data = pd.DataFrame({
        'Position': ['GK', 'RB', 'CB', 'CB', 'LB', 'RM', 'CM', 'CM', 'LM', 'RW', 'ST', 'LW'],
        'First Choice': ['Raya', 'White', 'Saliba', 'Gabriel', 'Tierney', 'Saka', 'Xhaka', 'Odegaard', 'Salah', 'Saka', 'Haaland', 'Martinelli'],
        'Backup': ['Steffen', 'Pavlovic', "Gabriel's backup", "CB cover", "Tierney backup", "Neto", "Rice", "Partey", "Gilbert", "Nunez", "Lewis", "Gordon"]
    })
    st.dataframe(depth_data, hide_index=True, use_container_width=True)

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Updated after each match",
        model_version="1.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()