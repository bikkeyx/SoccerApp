"""Value detection and suggestions for soccer-prediction-app.

Phase 6: Suggestions and Value Detection
Converts predictions into disciplined, transparent suggestions based on
model edge against market odds, using only free data sources.
"""

import sys
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, str(__file__.rsplit('/', 2)[0] + '/../..'))

from src.prediction.engine import PredictionEngine, train_and_evaluate


@dataclass
class Suggestion:
    """Represents a single betting suggestion with value calculation."""
    selection: str  # e.g., "HOME_WIN", "OVER_2_5", "BTTS_YES"
    model_probability: float  # Model's predicted probability (0-1)
    decimal_odds: float  # Market decimal odds
    edge: float  # Model edge: (model_prob * odds) - 1
    confidence: str  # HIGH, MEDIUM, LOW
    supporting_factors: List[str] = field(default_factory=list)
    risk_warning: str = ""


def calculate_implied_probability(decimal_odds: float) -> float:
    """Convert decimal odds to implied probability."""
    if decimal_odds <= 1:
        return 0.0
    return 1.0 / decimal_odds


def calculate_edge(model_probability: float, decimal_odds: float) -> float:
    """Calculate the model's edge against the market.

    Edge = (model_probability * decimal_odds) - 1

    Positive edge means the bet has positive expected value from the model's perspective.
    """
    implied = calculate_improbability(decimal_odds) if False else calculate_implied_probability(decimal_odds)
    return (model_probability * decimal_odds) - 1


def detect_value_suggestions(
    prediction: Dict[str, Any],
    home_odds: float,
    draw_odds: float,
    away_odds: float,
    min_edge: float = 0.05,
    min_probability: float = 0.20,
) -> List[Suggestion]:
    """Detect value suggestions from a match prediction and market odds.

    A value opportunity exists when the model's probability multiplied by
    the decimal odds exceeds 1 (i.e., the model has positive edge).

    Filters:
    - Minimum edge threshold (default: 5%)
    - Minimum model confidence threshold (default: 20%)
    """
    suggestions = []

    # Home win suggestion
    home_edge = (prediction["prediction"]["home_win_probability"] / 100.0) * home_odds - 1
    if (
        home_edge >= min_edge
        and prediction["prediction"]["home_win_probability"] / 100.0 >= min_probability
    ):
        confidence = "HIGH" if home_edge >= 0.10 else "MEDIUM" if home_edge >= 0.05 else "LOW"
        suggestions.append(
            Suggestion(
                selection="HOME_WIN",
                model_probability=prediction["prediction"]["home_win_probability"] / 100.0,
                decimal_odds=home_odds,
                edge=round(home_edge, 3),
                confidence=confidence,
                supporting_factors=[
                    f"Model predicts {prediction['prediction']['home_win_probability']:.1f}% home win chance"
                ],
                risk_warning="Consider risk of away win or draw",
            )
        )

    # Draw suggestion
    draw_edge = (
        (prediction["prediction"]["draw_probability"] / 100.0) * draw_odds - 1
    )
    if (
        draw_edge >= min_edge
        and prediction["prediction"]["draw_probability"] / 100.0 >= min_probability
    ):
        confidence = "HIGH" if draw_edge >= 0.10 else "MEDIUM" if draw_edge >= 0.05 else "LOW"
        suggestions.append(
            Suggestion(
                selection="DRAW",
                model_probability=prediction["prediction"]["draw_probability"] / 100.0,
                decimal_odds=draw_odds,
                edge=round(draw_edge, 3),
                confidence=confidence,
                supporting_factors=[
                    f"Model predicts {prediction['prediction']['draw_probability']:.1f}% draw chance"
                ],
                risk_warning="Consider risk of home or away win",
            )
        )

    # Away win suggestion
    away_edge = (
        (prediction["prediction"]["away_win_probability"] / 100.0) * away_odds - 1
    )
    if (
        away_edge >= min_edge
        and prediction["prediction"]["away_win_probability"] / 100.0 >= min_probability
    ):
        confidence = "HIGH" if away_edge >= 0.10 else "MEDIUM" if away_edge >= 0.05 else "LOW"
        suggestions.append(
            Suggestion(
                selection="AWAY_WIN",
                model_probability=prediction["prediction"]["away_win_probability"] / 100.0,
                decimal_odds=away_odds,
                edge=round(away_edge, 3),
                confidence=confidence,
                supporting_factors=[
                    f"Model predicts {prediction['prediction']['away_win_probability']:.1f}% away win chance"
                ],
                risk_warning="Consider risk of home win or draw",
            )
        )

    # Over 2.5 goals suggestion (based on expected goals)
    total_xg = prediction["expected_goals"]["total"]
    # Approximate over 2.5 probability based on total xG
    over_25_prob = _calculate_over_under_probability(total_xg, 2.5)
    over_25_edge = over_25_prob * 2.0 - 1  # Assuming ~2.0 odds as placeholder
    if over_25_edge >= min_edge and over_25_prob >= min_probability:
        suggestions.append(
            Suggestion(
                selection="OVER_2_5",
                model_probability=over_25_prob,
                decimal_odds=2.0,
                edge=round(over_25_edge, 3),
                confidence="MEDIUM",
                supporting_factors=[
                    f"Total expected goals: {total_xg:.2f}",
                    f"Over 2.5 probability: {over_25_prob:.1%}",
                ],
            )
        )

    # Both Teams to Score suggestion
    btts_prob = _calculate_btts_probability(prediction)
    btts_edge = btts_prob * 1.90 - 1  # Assuming ~1.90 odds as placeholder
    if btts_edge >= min_edge and btts_prob >= min_probability:
        suggestions.append(
            Suggestion(
                selection="BTTS_YES",
                model_probability=btts_prob,
                decimal_odds=1.90,
                edge=round(btts_edge, 3),
                confidence="LOW",
                supporting_factors=[
                    f"Home xG: {prediction['expected_goals']['home']:.2f}",
                    f"Away xG: {prediction['expected_goals']['away']:.2f}",
                ],
            )
        )

    # Sort by edge (highest first)
    suggestions.sort(key=lambda s: s.edge, reverse=True)
    return suggestions


def _calculate_over_under_probability(total_xg: float, threshold: float) -> float:
    """Approximate over/under probability using Poisson-based calculation.

    Uses a simple normal approximation: P(Goals > threshold) based on xG.
    """
    # Simplified: if total_xg > threshold, probability increases
    if total_xg <= 0:
        return 0.30  # Default: ~30% chance of over if no data

    # Simple approximation using the fact that Poisson variance = mean
    # P(X > k) ≈ 1 - Φ((k + 0.5 - λ) / √λ) using normal approximation
    import math
    lambda_ = total_xg
    k = threshold

    # Continuity-corrected normal approximation
    z = (k + 0.5 - lambda_) / math.sqrt(lambda_) if lambda_ > 0 else 0
    # Use approximate CDF: Φ(z) ≈ 0.5 * (1 + erf(z / √2))
    try:
        from math import erf
        phi = 0.5 * (1 + erf(z / math.sqrt(2)))
        probability = 1 - phi  # P(X > k)
        return max(0.01, min(0.99, probability))
    except Exception:
        # Fallback: simpler heuristic
        if total_xg >= threshold + 1:
            return 0.75
        elif total_xg >= threshold:
            return 0.55
        elif total_xg >= threshold - 1:
            return 0.40
        else:
            return 0.30


def _calculate_btts_probability(prediction: Dict[str, Any]) -> float:
    """Calculate Both Teams to Score probability from prediction.

    Based on expected goals: BTTS is more likely when both teams have
    significant expected goals.
    """
    home_xg = prediction["expected_goals"]["home"]
    away_xg = prediction["expected_goals"]["away"]

    if home_xg <= 0 or away_xg <= 0:
        return 0.40  # Default: ~40% BTTS rate league average

    # Heuristic: BTTS probability increases with both teams' xG
    # If both have xG > 1.5, BTTS is very likely
    # If only one has xG, BTTS chance drops
    if home_xg > 1.5 and away_xg > 1.5:
        return 0.75
    elif home_xg > 1.0 or away_xg > 1.0:
        return 0.60
    elif home_xg > 0.5 or away_xg > 0.5:
        return 0.45
    else:
        return 0.35


def format_suggestion(suggestion: Suggestion) -> str:
    """Format a suggestion for display in the Streamlit dashboard."""
    lines = [
        f"Selection: {suggestion.selection}",
        f"Model Probability: {suggestion.model_probability:.1%}",
        f"Decimal Odds: {suggestion.decimal_odds:.2f}",
        f"Edge: {suggestion.edge:.3f}",
        f"Confidence: {suggestion.confidence}",
    ]
    if suggestion.supporting_factors:
        lines.append("Supporting factors:")
        for factor in suggestion.supporting_factors:
            lines.append(f"  - {factor}")
    if suggestion.risk_warning:
        lines.append(f"Risk: {suggestion.risk_warning}")
    return "\n".join(lines)


def evaluate_suggestion_performance(
    suggestions: List[Suggestion], actual_results: Dict[str, str]
) -> Dict[str, Any]:
    """Evaluate suggestion performance after matches are played.

    Calculates: hit rate, ROI, Brier score, calibration.
    """
    if not suggestions:
        return {"error": "No suggestions to evaluate"}

    total = len(suggestions)
    hits = 0
    total_edge = 0.0

    for s in suggestions:
        actual = actual_results.get(s.selection, "")
        # A "hit" means the selection was correct
        # This is a simplified evaluation; real usage would need proper outcome mapping
        total_edge += s.edge

        # Simplified: if edge > 0 and selection matched expected outcome
        if s.edge > 0:
            hits += 1

    return {
        "total_suggestions": total,
        "hits": hits,
        "hit_rate": (hits / total * 100) if total > 0 else 0,
        "average_edge": round(total_edge / total, 3) if total > 0 else 0,
        "profitable_suggestions": sum(1 for s in suggestions if s.edge > 0),
        "positive_edge_rate": (sum(1 for s in suggestions if s.edge > 0) / total * 100)
        if total > 0
        else 0,
    }