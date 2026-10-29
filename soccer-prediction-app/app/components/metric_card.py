"""Metric card component for soccer-prediction-app."""

import streamlit as st
from app.theme import *


def metric_card(label: str, value: str, delta: str = None):
    """Render a terminal-style metric card."""
    st.markdown(
        f"""
        <div style="background: {PANEL_BACKGROUND}; border: 1px solid {BORDER_DIVIDER}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; color: {PRIMARY_TEXT};">
            <div style="font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT};">{label}</div>
            <div style="font-size: {FONT_SIZE_LARGE}; font-weight: bold;">{value}</div>
            {f"<div style='color: {ACCENT_GREEN}; font-size: {FONT_SIZE_SMALL};'>{delta}</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )