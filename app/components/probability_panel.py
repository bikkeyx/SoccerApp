"""Probability panel component for soccer-prediction-app."""

import streamlit as st
from app.theme import *


def probability_panel(home_prob: float, draw_prob: float, away_prob: float,
                     home_odds: float = None, draw_odds: float = None, away_odds: float = None):
    """Render a terminal-style probability panel with home/draw/away odds."""
    st.markdown(
        f"""
        <div style="background: {PANEL_BACKGROUND}; border: 1px solid {BORDER_DIVIDER}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <div style="font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT}; text-transform: uppercase; letter-spacing: 1px;">MATCH RESULT PROBABILITIES</div>
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span style="color: {ACCENT_GREEN};">HOME WIN</span>
                <span style="color: {PRIMARY_TEXT};">{home_prob:.1f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span style="color: {SECONDARY_ACCENT};">DRAW</span>
                <span style="color: {PRIMARY_TEXT};">{draw_prob:.1f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                <span style="color: {RISK_RED};">AWAY WIN</span>
                <span style="color: {PRIMARY_TEXT};">{away_prob:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Odds sidebar if provided
    if any([home_odds, draw_odds, away_odds]):
        odd_items = []
        if home_odds:
            odd_items.append(f"Home: {home_odds:.2f}")
        if draw_odds:
            odd_items.append(f"Draw: {draw_odds:.2f}")
        if away_odds:
            odd_items.append(f"Away: {away_odds:.2f}")

        odds_text = " | ".join(odd_items)

        st.markdown(
            f"""
            <div style="background: {PANEL_BACKGROUND}; border: 1px solid {BORDER_DIVIDER}; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <div style="font-size: {FONT_SIZE_SMALL}; color: {MUTED_TEXT}; text-transform: uppercase; letter-spacing: 1px;">MARKET ODDS</div>
                <div style="margin-top: 0.5rem;">{odds_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )