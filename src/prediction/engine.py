"""Prediction engine for soccer-prediction-app.

Phase 5: Prediction Engine
Produces calibrated, explainable soccer match predictions using a real
Poisson + Dixon-Coles statistical model with fuzzy team-name matching,
context adjustments (rest, travel, weather, motivation), and full
scoreline / over-under / BTTS probabilities.
"""

import sys
import math
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.context import (
    WeatherData, haversine_distance_km, calculate_rest_days,
    VenueEffects, MotivationContext, analyze_context,
    STADIUM_DATABASE,
)
from src.events.analytics import EventAnalytics


class PredictionEngine:
    """Prediction engine using Poisson + Dixon-Coles model.

    Training computes per-team attack / defense strength relative to the
    league average.  predict_match uses the full Poisson distribution
    (goals 0-6) with the Dixon-Coles low-score correction to produce
    calibrated home/draw/away, scoreline, over-under, and BTTS
    probabilities.  Context adjustments (rest, travel, weather,
    motivation) are applied when supplied.
    """

    def __init__(self, trained: bool = False):
        self.trained = trained
        # goals scored / conceded per game per team
        self.attack_ratings: Dict[str, float] = {}
        self.defense_ratings: Dict[str, float] = {}
        self.home_advantage_goals: float = 0.25   # extra xG for home side
        self.model_version = "2.0.0"
        self._league_avg: float = 1.35            # fallback league average

    # ------------------------------------------------------------------ #
    #  Training                                                            #
    # ------------------------------------------------------------------ #
    def train(self, match_results: List[Dict[str, Any]]) -> None:
        """Train on historical match results.

        Args:
            match_results: list of dicts with keys:
                home_team, away_team, home_goals, away_goals, date
        """
        if not match_results:
            return

        goals_scored: Dict[str, float] = defaultdict(float)
        goals_conceded: Dict[str, float] = defaultdict(float)
        games: Dict[str, int] = defaultdict(int)

        total_goals = 0
        for m in match_results:
            ht = m["home_team"]
            at = m["away_team"]
            hg = int(m["home_goals"])
            ag = int(m["away_goals"])
            goals_scored[ht] += hg
            goals_scored[at] += ag
            goals_conceded[ht] += ag
            goals_conceded[at] += hg
            games[ht] += 1
            games[at] += 1
            total_goals += hg + ag

        all_teams = set(goals_scored.keys())
        n_games = len(match_results)
        self._league_avg = total_goals / (2 * n_games) if n_games else 1.35

        self.attack_ratings = {
            t: goals_scored[t] / games[t] for t in all_teams if games[t] > 0
        }
        self.defense_ratings = {
            t: goals_conceded[t] / games[t] for t in all_teams if games[t] > 0
        }
        self.trained = True

    # ------------------------------------------------------------------ #
    #  Fuzzy team-name matching                                            #
    # ------------------------------------------------------------------ #
    def _resolve(self, name: str) -> Optional[str]:
        """Return the closest known team name, or None if not found."""
        nl = name.lower().strip()
        # 1. exact
        for k in self.attack_ratings:
            if k.lower() == nl:
                return k
        # 2. substring either way
        for k in self.attack_ratings:
            kl = k.lower()
            if nl in kl or kl in nl:
                return k
        # 3. word-overlap (ignore noise words)
        stop = {"fc", "cf", "sc", "ac", "the", "united", "city", "hotspur"}
        nw = set(nl.split()) - stop
        best, best_n = None, 0
        for k in self.attack_ratings:
            kw = set(k.lower().split()) - stop
            n = len(nw & kw)
            if n > best_n:
                best_n, best = n, k
        return best if best_n >= 1 else None

    # ------------------------------------------------------------------ #
    #  Poisson helpers                                                     #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _poisson(lam: float, k: int) -> float:
        """P(X = k) for Poisson(lam)."""
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return math.exp(-lam) * (lam ** k) / math.factorial(k)

    @staticmethod
    def _dc_tau(h: int, a: int, mu: float, nu: float, rho: float = -0.13) -> float:
        """Dixon-Coles correction for low-scoring cells."""
        if h == 0 and a == 0:
            return 1 - mu * nu * rho
        if h == 0 and a == 1:
            return 1 + mu * rho
        if h == 1 and a == 0:
            return 1 + nu * rho
        if h == 1 and a == 1:
            return 1 - rho
        return 1.0

    # ------------------------------------------------------------------ #
    #  Prediction                                                          #
    # ------------------------------------------------------------------ #
    def predict_match(
        self,
        home_team: str,
        away_team: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Predict a match using Poisson + Dixon-Coles.

        Args:
            home_team: Home team name (fuzzy-matched to training data).
            away_team: Away team name.
            context: Optional dict with any of:
                rest_days_home (int), rest_days_away (int),
                travel_km_away (float), weather_penalty (float 0-1),
                motivation_home (float), motivation_away (float).

        Returns:
            Dict with prediction, expected_goals, scorelines,
            most_likely_scoreline, over_under, btts, goal_difference,
            model_version, explanation.
        """
        avg = self._league_avg

        # Resolve to trained names (may be None if unknown team)
        hk = self._resolve(home_team)
        ak = self._resolve(away_team)

        h_atk = self.attack_ratings.get(hk, avg) if hk else avg
        h_def = self.defense_ratings.get(hk, avg) if hk else avg
        a_atk = self.attack_ratings.get(ak, avg) if ak else avg
        a_def = self.defense_ratings.get(ak, avg) if ak else avg

        # Strength ratios relative to league average
        h_atk_str = h_atk / avg if avg > 0 else 1.0
        h_def_str = h_def / avg if avg > 0 else 1.0   # higher = leakier defense
        a_atk_str = a_atk / avg if avg > 0 else 1.0
        a_def_str = a_def / avg if avg > 0 else 1.0

        # Standard Dixon-Coles expected goals
        home_xg = avg * h_atk_str * a_def_str + self.home_advantage_goals
        away_xg = avg * a_atk_str * h_def_str

        home_xg = max(0.3, min(5.0, home_xg))
        away_xg = max(0.3, min(5.0, away_xg))

        # ── Context adjustments ──────────────────────────────────────────
        context_notes: List[str] = []
        ctx = context or {}

        home_rest = ctx.get("rest_days_home")
        away_rest = ctx.get("rest_days_away")
        if home_rest is not None and home_rest < 4:
            pen = 0.04 * (4 - home_rest)
            home_xg *= (1 - pen)
            context_notes.append(f"Home fatigue ({home_rest}d rest): -{pen:.0%} xG")
        if away_rest is not None and away_rest < 4:
            pen = 0.04 * (4 - away_rest)
            away_xg *= (1 - pen)
            context_notes.append(f"Away fatigue ({away_rest}d rest): -{pen:.0%} xG")

        travel = ctx.get("travel_km_away", 0) or 0
        if travel > 400:
            tpen = min(0.06, (travel - 400) / 15000)
            away_xg *= (1 - tpen)
            context_notes.append(f"Away travel ({travel:.0f} km): -{tpen:.0%} xG")

        weather_pen = ctx.get("weather_penalty", 0.0) or 0.0
        if weather_pen > 0:
            home_xg *= (1 - weather_pen * 0.5)
            away_xg *= (1 - weather_pen * 0.5)
            context_notes.append(f"Weather: -{weather_pen:.0%} both teams")

        home_xg *= ctx.get("motivation_home", 1.0)
        away_xg *= ctx.get("motivation_away", 1.0)

        home_xg = max(0.3, min(5.0, home_xg))
        away_xg = max(0.3, min(5.0, away_xg))

        # ── Poisson score matrix (0-6 goals each) ───────────────────────
        MAX_G = 7
        home_win_p = draw_p = away_win_p = 0.0
        score_matrix: Dict[str, float] = {}

        for h in range(MAX_G):
            for a in range(MAX_G):
                p = (self._poisson(home_xg, h)
                     * self._poisson(away_xg, a)
                     * self._dc_tau(h, a, home_xg, away_xg))
                score_matrix[f"{h}-{a}"] = round(p, 5)
                if h > a:
                    home_win_p += p
                elif h == a:
                    draw_p += p
                else:
                    away_win_p += p

        total = home_win_p + draw_p + away_win_p
        if total > 0:
            home_win_p /= total
            draw_p /= total
            away_win_p /= total

        most_likely = max(score_matrix, key=lambda k: score_matrix[k])

        over_25_p = sum(
            score_matrix[k] for k in score_matrix
            if sum(int(x) for x in k.split("-")) > 2
        )
        btts_p = sum(
            score_matrix[k] for k in score_matrix
            if int(k.split("-")[0]) > 0 and int(k.split("-")[1]) > 0
        )

        return {
            "prediction": {
                "home_win_probability": round(home_win_p * 100, 1),
                "draw_probability": round(draw_p * 100, 1),
                "away_win_probability": round(away_win_p * 100, 1),
            },
            "expected_goals": {
                "home_xg": round(home_xg, 2),
                "away_xg": round(away_xg, 2),
                "total_xg": round(home_xg + away_xg, 2),
            },
            "scorelines": score_matrix,
            "most_likely_scoreline": most_likely,
            "over_under": {
                "over_2_5": round(over_25_p * 100, 1),
                "under_2_5": round((1 - over_25_p) * 100, 1),
            },
            "btts": round(btts_p * 100, 1),
            "goal_difference": round(home_xg - away_xg, 2),
            "model_version": self.model_version,
            "explanation": {
                "home_team_found": hk is not None,
                "away_team_found": ak is not None,
                "home_attack_strength": round(h_atk_str, 2),
                "away_attack_strength": round(a_atk_str, 2),
                "home_defense_strength": round(h_def_str, 2),
                "away_defense_strength": round(a_def_str, 2),
                "context_notes": context_notes,
                "data_quality": (
                    "high" if (hk and ak) else
                    "medium" if (hk or ak) else "low"
                ),
            },
        }

    def predict_tournament(
        self, teams: List[str], matches: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Predict tournament outcomes."""
        results = []
        for match in matches:
            pred = self.predict_match(match["home_team"], match["away_team"])
            results.append({
                "home": match["home_team"],
                "away": match["away_team"],
                "prediction": pred["prediction"],
                "expected_goals": pred["expected_goals"],
            })
        return {"tournament": True, "teams": teams, "matches": results}
