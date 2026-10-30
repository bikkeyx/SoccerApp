"""Data quality indicator component for soccer-prediction-app."""

import streamlit as st
from app.theme import *


def data_quality_indicator(quality_score: float, data_points: int, total_expected: int = 100, 
                          label: str = "Data Quality"):
    """Render a terminal-style data quality indicator."""
    percentage = (data_points / total_expected) * 100 if total_expected > 0 else 0
    color = ACCENT_GREEN if quality_score > 80 else (WARNING_AMBER if quality_score > 50 else RISK_RED)
    
    st.markdown(
        f"""
        <div style="background: {PANEL_BACKGROUND}; border: 1px solid {BORDER_DIVIDER}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <div style="font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT}; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span>{data_points}/{total_expected} records</span>
                <span style="color: {color}; font-weight: bold;">{quality_score:.0f}% quality</span>
            </div>
            <div style="width: 100%; background: {BORDER_DIVIDER}; height: 8px; border-radius: 4px; margin-top: 0.5rem; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background: {color}; border-radius: 4px; transition: width 0.3s;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )