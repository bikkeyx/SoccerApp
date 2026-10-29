"""Suggestions and value detection for soccer-prediction-app.

Phase 6: Suggestions and Value Detection
Provides value-based betting suggestions converted from model predictions.
"""

from src.suggestions.value import (
    Suggestion,
    calculate_implied_probability,
    calculate_edge,
    detect_value_suggestions,
    format_suggestion,
    evaluate_suggestion_performance,
    _calculate_over_under_probability,
    _calculate_btts_probability,
)

__all__ = [
    "Suggestion",
    "calculate_implied_probability",
    "calculate_edge",
    "detect_value_suggestions",
    "format_suggestion",
    "evaluate_suggestion_performance",
]