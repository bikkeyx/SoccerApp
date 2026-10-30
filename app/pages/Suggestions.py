"""Suggestions - Streamlit Dashboard Page 5

Displays value betting suggestions with edge and confidence.
Follows terminal/hacker theme from plan.md.
"""

import streamlit as st
import pandas as pd
import sys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Suggestions",
    page_icon="💡",
    layout="wide",
)

# Custom CSS theme
<style>
/* Import theme from style.css -- do not redefine variables here */
</style>



def main():
    st.title("💡 Suggestions")
    st.markdown("### Value Betting Suggestions")

    # Sidebar controls
    st.sidebar.header("Filters")
    min_edge = st.sidebar.slider("Minimum Edge (%)", 0, 20, 5) / 100
    min_probability = st.sidebar.slider("Minimum Probability (%)", 0, 100, 20) / 100
    show_confidence = st.sidebar.checkbox("Show Confidence Labels", value=True)

    # Generate sample prediction (would use real engine in production)
    engine = st.session_state.get('engine')
    if engine is None:
        from src.prediction.engine import PredictionEngine
        engine = PredictionEngine()
        st.session_state['engine'] = engine

    pred = engine.predict_match("Arsenal", "Liverpool")

    # Get suggestions
    from src.suggestions import detect_value_suggestions, format_suggestion

    suggestions = st.session_state.get('suggestions_list')
    if suggestions is None:
        suggestions = detect_value_suggestions(
            pred,
            min_edge=min_edge,
            min_probability=min_probability,
        )
        st.session_state['suggestions_list'] = suggestions

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Suggestions", len(suggestions) if suggestions else 0)
    with col2:
        positive_edges = sum(1 for s in suggestions if s.edge > 0) if suggestions else 0
        st.metric("Positive Edge", f"{positive_edges}/{len(suggestions) if suggestions else 0}")
    with col3:
        avg_edge = sum(s.edge for s in suggestions) / len(suggestions) if suggestions else 0
        st.metric("Average Edge", f"{avg_edge:.3f}")

    # Suggestions list
    if suggestions:
        st.markdown("#### Recommended Selections")
        for i, s in enumerate(suggestions, 1):
            # Determine risk level
            if s.edge >= 0.10:
                risk = "HIGH"
                risk_class = "risk-box"
            elif s.edge >= 0.05:
                risk = "MEDIUM"
                risk_class = "warning-box"
            else:
                risk = "LOW"
                risk_class = "warning-box"

            # Display
            with st.container():
                st.markdown(
                    f"""{i}. **{s.selection}**
                       <div class="{risk_class}">
                           Edge: {s.edge:.3f} | 
                           Probability: {s.model_probability:.1%} | 
                           Confidence: {s.confidence}
                       </div>""",
                    unsafe_allow_html=True,
                )
                if show_confidence:
                    st.caption(f"Supporting factors: {', '.join(s.supporting_factors) if s.supporting_factors else 'N/A'}")

        # Performance tracking note
        st.markdown("---")
        st.markdown("""
        <div class="warning-box">
            <strong>Performance Tracking:</strong> 
            Suggestions are evaluated after matches are played. 
            Hit rate and ROI are tracked over time.
        </div>""",
                    unsafe_allow_html=True)
    else:
        st.info(f"No suggestions found with edge > {min_edge:.1%} and probability > {min_probability:.1%}.")
        st.markdown("""
        <div class="info-box">
            Adjust the sliders above to lower the thresholds and 
            find more value opportunities.
        </div>""", unsafe_allow_html=True)

    # Model information
    with st.expander("Model Information"):
        st.markdown("""
        **Suggestion Logic:**
        - Edge = (Model Probability × Decimal Odds) - 1
        - Positive edge > 0 means positive expected value
        - Minimum edge filter: 5% (0.05)
        - Minimum probability filter: 20% (0.20)
        - Confidence: HIGH (>10% edge), MEDIUM (5-10% edge), LOW (<5% edge)
        
        **Model:** Poisson/Dixon-Coles ensemble with Elo ratings
        **Data:** Historical match results, team form, context variables
        **Evaluation:** Backtested on unseen chronological data
        """)

    # Status bar
    status_bar(
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model_version="1.0.0",
        data_freshness="Live suggestions"
    )


if __name__ == "__main__":
    main()