"""Event-level performance analytics for soccer-prediction-app.

Phase 3: Event-Level Performance Data
Calculates xG, team styles, matchup features from event data.
Uses permanently free data sources.
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.events.ingestion import fetch_epl_match_stats


class EventAnalytics:
    """Calculate event-level performance metrics from match statistics."""

    def __init__(self):
        self.league_gf_avg: float = 0.0
        self.league_ga_avg: float = 0.0
        self.team_stats: Dict[str, Dict] = {}

    def load_match_data(self, matches_data: List[Dict[str, Any]]) -> None:
        """Load match statistics and calculate team metrics."""
        self.team_stats = defaultdict(lambda: {
            "games": 0, "shg": 0, "sag": 0,  # goals for/against at home/away
            "sf": 0, "sa": 0, "sft": 0, "sat": 0,  # shots for/against, on target
            "cf": 0, "ca": 0,  # corners for/against
            "fy": 0, "fa": 0,  # fouls for/against
            "hc": 0, "ac": 0,  # home corners, away corners
            "hy": 0, "ay": 0,  # home yellows, away yellows
        })

        for m in matches_data:
            home = m["home_team"]
            away = m["away_team"]

            # Update team stats
            self.team_stats[home]["games"] += 1
            self.team_stats[away]["games"] += 1

            # Goals
            self.team_stats[home]["shg"] += m["home_goals"]
            self.team_stats[away]["sag"] += m["away_goals"]
            self.team_stats[away]["shg"] += m["away_goals"]
            self.team_stats[home]["sag"] += m["home_goals"]

            # Shots
            self.team_stats[home]["sf"] += m["home_shots"]
            self.team_stats[away]["sa"] += m["away_shots"]
            self.team_stats[home]["sft"] += m["home_shots_on_target"]
            self.team_stats[away]["sat"] += m["away_shots_on_target"]

            # Corners
            self.team_stats[home]["hc"] += m["home_corners"]
            self.team_stats[away]["ac"] += m["away_corners"]

            # Fouls
            self.team_stats[home]["fy"] += m["home_fouls"]
            self.team_stats[away]["fa"] += m["away_fouls"]

            # Yellow cards
            self.team_stats[home]["hy"] += m["home_yellow_cards"]
            self.team_stats[away]["ay"] += m["away_yellow_cards"]

    def calculate_xg_metrics(self, matches_data: List[Dict[str, Any]],
                            rolling_window: int = 5) -> Dict[str, Any]:
        """Calculate expected goals (xG) metrics from match data.

        Uses actual goals as a proxy when shot-level xG data is not available.
        Framework supports proper xG calculation when shot data becomes available.
        Includes rolling metrics for form tracking.
        """
        team_attack: Dict[str, float] = defaultdict(float)
        team_defense: Dict[str, float] = defaultdict(float)
        team_shots: Dict[str, int] = defaultdict(int)
        team_sot: Dict[str, int] = defaultdict(int)  # shots on target
        team_shots_rolling: Dict[str, List[int]] = defaultdict(list)
        team_goals_rolling: Dict[str, List[int]] = defaultdict(list)

        for m in matches_data:
            home = m["home_team"]
            away = m["away_team"]
            hg = m["home_goals"]
            ag = m["away_goals"]
            hs = m["home_shots"]
            as_ = m["away_shots"]
            hst = m["home_shots_on_target"]
            ast = m["away_shots_on_target"]

            # Update shots and on-target
            team_shots[home] += hs
            team_shots[away] += as_
            team_sot[home] += hst
            team_sot[away] += ast

            # Update attack/defense based on actual goals (proxy for xG)
            team_attack[home] += hg
            team_attack[away] += ag
            team_defense[home] += ag
            team_defense[away] += hg

            # Rolling calculations
            team_shots_rolling[home].append(hs)
            team_shots_rolling[away].append(as_)
            team_goals_rolling[home].append(hg)
            team_goals_rolling[away].append(ag)

        # Calculate rates per game
        metrics: Dict[str, Any] = {}
        for team in set(list(team_attack.keys()) + list(team_defense.keys())):
            games = self.team_stats[team]["games"] if team in self.team_stats else 1
            rolling_games = min(rolling_window, len(team_shots_rolling[team]))
            rolling_goals = sum(team_goals_rolling[team][-rolling_games:]) if team_goals_rolling[team] else 0
            rolling_shots = sum(team_shots_rolling[team][-rolling_games:]) if team_shots_rolling[team] else 0
            rolling_sot = sum(team_shots_rolling[team][-rolling_games:]) if team_shots_rolling[team] else 0

            metrics[team] = {
                "games": games,
                "goals_per_game": team_attack[team] / games if games > 0 else 0,
                "goals_against_per_game": team_defense[team] / games if games > 0 else 0,
                "shots_per_game": team_shots[team] / games if games > 0 else 0,
                "shots_on_target_per_game": team_sot[team] / games if games > 0 else 0,
                "shot_accuracy": (team_sot[team] / team_shots[team] * 100
                                  if team_shots[team] > 0 else 0),
                "rolling_goals_per_game": rolling_goals / rolling_games if rolling_games > 0 else 0,
                "rolling_shots_per_game": rolling_shots / rolling_games if rolling_games > 0 else 0,
                "rolling_shot_accuracy": (rolling_sot / rolling_shots * 100
                                          if rolling_shots > 0 else 0),
            }

        return metrics

    def calculate_team_style(self, matches_data: List[Dict[str, Any]]
                            ) -> Dict[str, Dict[str, Any]]:
        """Determine team playing styles based on match statistics.

        Styles: high_press, low_block, direct, possession_based, counterattacking
        """
        style_metrics: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"shots_per_game": 0, "shots_on_target_pct": 0,
                     "corner_ratio": 0, "foul_rate": 0, "avg_goals": 0})

        for m in matches_data:
            home = m["home_team"]
            away = m["away_team"]
            hs = m["home_shots"]
            as_ = m["away_shots"]
            hst = m["home_shots_on_target"]
            ac = m["away_corners"]

            if home in style_metrics:
                style_metrics[home]["shots_per_game"] += hs
                style_metrics[home]["corner_ratio"] += ac / (hs + 1) if hs > 0 else 0
                style_metrics[home]["avg_goals"] += m["home_goals"]

        # Normalize by games
        for team in style_metrics:
            games = self.team_stats[team]["games"] if team in self.team_stats else 1
            if games > 0:
                for key in style_metrics[team]:
                    style_metrics[team][key] /= games

        # Also process away team stats
        for m in matches_data:
            away = m["away_team"]
            hs = m["home_shots"]
            as_ = m["away_shots"]
            hst = m["home_shots_on_target"]
            ac = m["away_corners"]

            if away in style_metrics:
                style_metrics[away]["shots_per_game"] += as_
                style_metrics[away]["corner_ratio"] += hs / (as_ + 1) if as_ > 0 else 0
                style_metrics[away]["avg_goals"] += m["away_goals"]

        # Normalize away games
        for team in style_metrics:
            games = self.team_stats[team]["games"] if team in self.team_stats else 1
            if games > 0:
                for key in style_metrics[team]:
                    style_metrics[team][key] /= games

        # Classify styles
        classified: Dict[str, str] = {}
        for team, metrics in style_metrics.items():
            shot_pct = metrics["shots_on_target_pct"] / (metrics["shots_per_game"] + 1) * 100 if metrics["shots_per_game"] > 0 else 0
            corner_ratio = metrics["corner_ratio"]

            # Simple classification heuristic
            if shot_pct > 0.35 and corner_ratio > 5:
                classified[team] = "high_press"
            elif shot_pct < 0.25 and corner_ratio < 4:
                classified[team] = "low_block"
            elif corner_ratio > 6:
                classified[team] = "direct"
            else:
                classified[team] = "possession_based"

        return classified

    def calculate_referee_profile(self, matches_data: List[Dict[str, Any]]
                                   ) -> Dict[str, Dict[str, Any]]:
        """Calculate referee disciplinary profiles from match data.

        Tracks cards per match, average fouls, and patterns.
        """
        referee_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "matches": 0, "total_yellows": 0, "total_reds": 0,
            "home_yellows": 0, "away_yellows": 0,
            "home_reds": 0, "away_reds": 0,
            "avg_total_cards": 0.0,
        })

        for m in matches_data:
            referee = m.get("referee", "Unknown")
            if referee == "Unknown" or not referee:
                continue

            referee_stats[referee]["matches"] += 1
            referee_stats[referee]["total_yellows"] += m.get("home_yellow_cards", 0) + m.get("away_yellow_cards", 0)
            referee_stats[referee]["total_reds"] += m.get("home_red_cards", 0) + m.get("away_red_cards", 0)
            referee_stats[referee]["home_yellows"] += m.get("home_yellow_cards", 0)
            referee_stats[referee]["away_yellows"] += m.get("away_yellow_cards", 0)
            referee_stats[referee]["home_reds"] += m.get("home_red_cards", 0)
            referee_stats[referee]["away_reds"] += m.get("away_red_cards", 0)

        # Calculate averages
        for ref, stats in referee_stats.items():
            matches = max(stats["matches"], 1)
            stats["avg_total_cards"] = (stats["total_yellows"] + stats["total_reds"]) / matches
            # Yellow card rate per match
            stats["yellow_rate"] = stats["total_yellows"] / matches
            # Red card rate per match
            stats["red_rate"] = stats["total_reds"] / matches

        return dict(referee_stats)

    def calculate_matchup_features(self, home_team: str, away_team: str,
                                    matches_data: List[Dict[str, Any]]
                                    ) -> Dict[str, Any]:
        """Calculate matchup features for a specific home vs away team pairing."""
        home_matches = [m for m in matches_data if m["home_team"] == home_team]
        away_matches = [m for m in matches_data if m["away_team"] == away_team]

        home_avg_shots = sum(m["home_shots"] for m in home_matches) / max(len(home_matches), 1)
        away_avg_shots = sum(m["away_shots"] for m in away_matches) / max(len(away_matches), 1)

        home_sot_pct = sum(m["home_shots_on_target"] for m in home_matches) / max(sum(m["home_shots"] for m in home_matches), 1) * 100
        away_sot_pct = sum(m["away_shots_on_target"] for m in away_matches) / max(sum(m["away_shots"] for m in away_matches), 1) * 100

        # Calculate home/away strength from all team matches
        all_home_matches = [m for m in matches_data if m["home_team"] == home_team]
        all_away_matches = [m for m in matches_data if m["away_team"] == away_team]

        home_goals_scored = sum(m["home_goals"] for m in all_home_matches)
        away_goals_scored = sum(m["away_goals"] for m in all_away_matches)
        home_games = max(len(all_home_matches), 1)
        away_games = max(len(all_away_matches), 1)

        # Expected goals from shots model
        # League average shot conversion: ~1 goal per 16-17 shots = 0.06
        league_conv_rate = 0.06

        # Expected goals from shots model
        home_xg = home_avg_shots * league_conv_rate + (away_avg_shots / 2) * league_conv_rate * 0.5
        away_xg = away_avg_shots * league_conv_rate + (home_avg_shots / 2) * league_conv_rate * 0.5

        # Adjust for form (last 5 games)
        home_form_factor = 1.0
        away_form_factor = 1.0

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_avg_shots_per_game": round(home_avg_shots, 2),
            "away_avg_shots_per_game": round(away_avg_shots, 2),
            "home_shots_on_target_pct": round(home_sot_pct, 1),
            "away_shots_on_target_pct": round(away_sot_pct, 1),
            "home_goals_scored_avg": round(home_goals_scored / home_games, 2) if home_games > 0 else 0,
            "away_goals_scored_avg": round(away_goals_scored / away_games, 2) if away_games > 0 else 0,
            "home_style": "high_press",  # Would be calculated via calculate_team_style
            "away_style": "low_block",   # Would be calculated via calculate_team_style
            "predicted_open_play_goals": round(
                (home_avg_shots / 15 + away_avg_shots / 15), 2),
            "expected_home_xg": round(home_xg, 2),
            "expected_away_xg": round(away_xg, 2),
            "goal_difference": round(home_xg - away_xg, 2),
            "predicted_result": "H" if home_xg > away_xg else "A" if away_xg > home_xg else "D",
        }

    def calculate_venue_effects(self, matches_data: List[Dict[str, Any]]
                               ) -> Dict[str, Dict[str, Any]]:
        """Calculate home/away venue effects from historical data."""
        venue_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "home_matches": 0, "home_goals_for": 0, "home_goals_against": 0,
            "away_matches": 0, "away_goals_for": 0, "away_goals_against": 0,
            "home_points": 0, "away_points": 0,
            "home_win_pct": 0, "draw_pct": 0, "away_win_pct": 0,
        })

        for m in matches_data:
            home = m["home_team"]
            away = m["away_team"]
            hg = m["home_goals"]
            ag = m["away_goals"]

            # Home team stats
            venue_stats[home]["home_matches"] += 1
            venue_stats[home]["home_goals_for"] += hg
            venue_stats[home]["home_goals_against"] += ag
            if m["result"] == "H":
                venue_stats[home]["home_points"] += 3
            elif m["result"] == "D":
                venue_stats[home]["home_points"] += 1

            # Away team stats
            venue_stats[away]["away_matches"] += 1
            venue_stats[away]["away_goals_for"] += ag
            venue_stats[away]["away_goals_against"] += hg
            if m["result"] == "A":
                venue_stats[away]["away_points"] += 3
            elif m["result"] == "D":
                venue_stats[away]["away_points"] += 1

        # Calculate percentages
        for team, stats in venue_stats.items():
            home_games = max(stats["home_matches"], 1)
            away_games = max(stats["away_matches"], 1)

            # Home wins/points calculation
            h_wins = sum(1 for m in matches_data if m["home_team"] == team and m["result"] == "H")
            h_draws = sum(1 for m in matches_data if m["home_team"] == team and m["result"] == "D")
            h_losses = sum(1 for m in matches_data if m["home_team"] == team and m["result"] == "A")

            a_wins = sum(1 for m in matches_data if m["away_team"] == team and m["result"] == "A")
            a_draws = sum(1 for m in matches_data if m["away_team"] == team and m["result"] == "D")
            a_losses = sum(1 for m in matches_data if m["away_team"] == team and m["result"] == "H")

            stats["home_win_pct"] = (h_wins / home_games * 100) if home_games > 0 else 0
            stats["home_draw_pct"] = (h_draws / home_games * 100) if home_games > 0 else 0
            stats["home_loss_pct"] = (h_losses / home_games * 100) if home_games > 0 else 0
            stats["away_win_pct"] = (a_wins / away_games * 100) if away_games > 0 else 0
            stats["away_draw_pct"] = (a_draws / away_games * 100) if away_games > 0 else 0
            stats["away_loss_pct"] = (a_losses / away_games * 100) if away_games > 0 else 0

        return dict(venue_stats)

    def calculate_home_away_splits(self, matches_data: List[Dict[str, Any]]
                                    ) -> Dict[str, Dict[str, Any]]:
        """Calculate home and away performance splits for all teams."""
        home_performance: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"games": 0, "wins": 0, "draws": 0, "losses": 0,
                     "goals_for": 0, "goals_against": 0, "points": 0})
        away_performance: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"games": 0, "wins": 0, "draws": 0, "losses": 0,
                     "goals_for": 0, "goals_against": 0, "points": 0})

        for m in matches_data:
            home = m["home_team"]
            away = m["away_team"]
            hg = m["home_goals"]
            ag = m["away_goals"]
            result = m.get("result", "D")

            # Home team performance at home
            home_performance[home]["games"] += 1
            home_performance[home]["goals_for"] += hg
            home_performance[home]["goals_against"] += ag

            if result == "H":
                home_performance[home]["wins"] += 1
                home_performance[home]["points"] += 3
            elif result == "D":
                home_performance[home]["draws"] += 1
                home_performance[home]["points"] += 1
            else:
                home_performance[home]["losses"] += 1

            # Away team performance away
            away_performance[away]["games"] += 1
            away_performance[away]["goals_for"] += ag
            away_performance[away]["goals_against"] += hg

            if result == "A":
                away_performance[away]["wins"] += 1
                away_performance[away]["points"] += 3
            elif result == "D":
                away_performance[away]["draws"] += 1
                away_performance[away]["points"] += 1
            else:
                away_performance[away]["losses"] += 1

        # Calculate percentages and averages
        results = {}
        for team in set(list(home_performance.keys()) + list(away_performance.keys())):
            hp = home_performance[team]
            ap = away_performance[team]

            home_win_pct = (hp["wins"] / hp["games"] * 100) if hp["games"] > 0 else 50.0
            home_draw_pct = (hp["draws"] / hp["games"] * 100) if hp["games"] > 0 else 25.0
            home_loss_pct = (hp["losses"] / hp["games"] * 100) if hp["games"] > 0 else 25.0
            home_gf_avg = hp["goals_for"] / hp["games"] if hp["games"] > 0 else 1.5
            home_ga_avg = hp["goals_against"] / hp["games"] if hp["games"] > 0 else 1.5

            away_win_pct = (ap["wins"] / ap["games"] * 100) if ap["games"] > 0 else 33.3
            away_draw_pct = (ap["draws"] / ap["games"] * 100) if ap["games"] > 0 else 25.0
            away_loss_pct = (ap["losses"] / ap["games"] * 100) if ap["games"] > 0 else 41.7
            away_gf_avg = ap["goals_for"] / ap["games"] if ap["games"] > 0 else 1.2
            away_ga_avg = ap["goals_against"] / ap["games"] if ap["games"] > 0 else 1.8

            results[team] = {
                "home": {
                    "win_pct": round(home_win_pct, 1),
                    "draw_pct": round(home_draw_pct, 1),
                    "loss_pct": round(home_loss_pct, 1),
                    "goals_per_game": round(home_gf_avg, 2),
                    "goals_against_avg": round(home_ga_avg, 2),
                    "points_per_game": round(hp["points"] / hp["games"], 2) if hp["games"] > 0 else 1.5,
                },
                "away": {
                    "win_pct": round(away_win_pct, 1),
                    "draw_pct": round(away_draw_pct, 1),
                    "loss_pct": round(away_loss_pct, 1),
                    "goals_per_game": round(away_gf_avg, 2),
                    "goals_against_avg": round(away_ga_avg, 2),
                    "points_per_game": round(ap["points"] / ap["games"], 2) if ap["games"] > 0 else 1.2,
                },
            }

        return results


# Convenience function
def analyze_epl_style(seasons_back: int = 1) -> Dict[str, Any]:
    """Analyze EPL team styles from historical match data."""
    data = fetch_epl_match_stats(seasons_back)
    analytics = EventAnalytics()

    if data and "matches" in data:
        analytics.load_match_data(data["matches"])
        xg_metrics = analytics.calculate_xg_metrics(data["matches"])
        team_styles = analytics.calculate_team_style(data["matches"])
        referee_profile = analytics.calculate_referee_profile(data["matches"])
        venue_effects = analytics.calculate_venue_effects(data["matches"])
        home_away_splits = analytics.calculate_home_away_splits(data["matches"])

        # Get a few sample matchups
        matchup = analytics.calculate_matchup_features(
            "Manchester City", "Liverpool", data["matches"])

        return {
            "xg_metrics": xg_metrics,
            "team_styles": team_styles,
            "referee_profile": referee_profile,
            "venue_effects": venue_effects,
            "home_away_splits": home_away_splits,
            "sample_matchup": matchup,
            "matches_analyzed": len(data["matches"]) if data else 0,
        }

    return {"xg_metrics": {}, "team_styles": {}, "referee_profile": {},
            "venue_effects": {}, "home_away_splits": {}, "sample_matchup": {},
            "matches_analyzed": 0}