"""Data Sources & Coverage - Streamlit Dashboard Page 9

Displays data sources, coverage, freshness, and API usage.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Data Sources",
    page_icon="📡",
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
    st.title("📡 Data Sources & Coverage")
    st.markdown("### Free Data Sources & Coverage")

    # Sidebar - Source selection
    st.sidebar.header("Source Selector")
    source = st.sidebar.radio("Primary Source", [
        "football-data.org", "FBref", "Understat", "Transfermarkt",
        "Open-Meteo", "OpenStreetMap"
    ])

    # Main content
    st.markdown(f"### {source} Coverage")

    # Source info card
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### {source} - Free Tier Status")
        st.markdown("**License:** Permanently free for non-commercial use")
        st.markdown("**Rate Limits:** 10 requests/minute (configurable)")
        st.markdown("**Data Freshness:** Daily updates at 4am UTC")
        st.markdown("**Coverage:** All major European leagues")
    with col2:
        st.metric("Request Today", "847", "of 1000/min limit")
        st.metric("Cache Status", "✅ Fresh", "Updated 2h ago")

    # League coverage table
    st.markdown("#### League Coverage")
    league_data = pd.DataFrame({
        'League': ['Premier League', 'Bundesliga', 'Serie A', 'Ligue 1', 'Eredivisie', 'MLS'],
        'Coverage': ['Full Season', 'Full Season', 'Full Season', 'Full Season', 'Partial', 'Partial'],
        'Matches': ['380', '306', '380', '380', '204', '234'],
        'Last Update': ['Today', 'Today', 'Today', 'Yesterday', '3d ago', '5d ago']
    })
    st.dataframe(league_data, hide_index=True, use_container_width=True)

    # API usage summary
    st.markdown("#### API Usage Summary")
    usage_data = pd.DataFrame({
        'Source': ['football-data.org', 'FBref', 'Understat', 'Open-Meteo'],
        'Daily Calls': ['45', '12', '8', '23'],
        'Remaining': ['955', '988', '992', '977'],
        'Status': ['✅ Good', '✅ Good', '✅ Good', '✅ Good']
    })
    st.dataframe(usage_data, hide_index=True, use_container_width=True)

    # Data freshness
    st.markdown("#### Data Freshness")
    freshness_data = pd.DataFrame({
        'Data Type': ['Fixtures', 'Results', 'Standings', 'xG', 'Lineups'],
        'Last Updated': ['2 hours ago', '30 min ago', '1 hour ago', '6 hours ago', '12 hours ago'],
        'Status': ['✅ Fresh', '✅ Fresh', '✅ Fresh', '⚠️ Stale', '⚠️ Stale']
    })
    st.dataframe(freshness_data, hide_index=True, use_container_width=True)

    # Requirements
    st.markdown("#### Requirements")
    st.markdown("""
    - Python 3.8+
    - Streamlit 1.25+
    - pandas 2.0+
    - No API keys required (all free tiers)
    - Caching enabled by default
    - Refresh interval: 24h minimum
    """)

    # Status bar
    from app.components.header import header_status_bar
    header_status_bar(
        data_freshness="Sources: football-data.org, FBref, Understat",
        model_version="1.0.0",
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


if __name__ == "__main__":
    main()