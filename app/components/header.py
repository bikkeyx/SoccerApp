"""Header/status bar component for soccer-prediction-app."""

import streamlit as st
from app.theme import *

def header_status_bar(data_freshness: str, model_version: str = "v1.0", last_update: str = "Just now"):
    """Render terminal-style header/status bar."""
    st.markdown(
        f"""
        <div style="background: {PANEL_BACKGROUND}; border-bottom: 1px solid {BORDER_DIVIDER}; padding: 0.5rem 1rem; margin-bottom: 1rem;>
            <span style="font-family: {FONT_FAMILY}; font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT};">
                ⚽ {data_freshness}  |  Model: {model_version}  |  Last update: {last_update}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
