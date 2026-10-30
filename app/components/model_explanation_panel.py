"""Model explanation panel component for soccer-prediction-app."""

import streamlit as st
from app.theme import *


def model_explanation_panel(features: dict, explanations: dict = None):
    """Render a terminal-style model explanation panel."""
    st.markdown(
        f"""
        <div style="background: {PANEL_BACKGROUND}; border: 1px solid {BORDER_DIVIDER}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <div style="font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT}; text-transform: uppercase; letter-spacing: 1px;">MODEL EXPLANATION</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if features:
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        for feature, importance in sorted(features.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                    <span style="color: {MUTED_TEXT}; width: 150px;">{feature}</span>
                    <span style="color: {PRIMARY_TEXT};">{importance:.1f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)