"""Context and environment modeling for soccer-prediction-app.

Phase 4: Context and Environment Modeling
Adds situational variables that affect match outcomes:
- Weather forecast, travel distance, rest days, motivation context
- All using permanently free data sources
"""

import sys
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.events.ingestion import fetch_epl_match_stats
from src.events.analytics import EventAnalytics


class ContextModel:
    """Model contextual variables that affect match outcomes."""

    def __init__(self):
        self.weather_data: Dict = {}
        self.travel_data: Dict = {}
        self.motivation_data: Dict = {}

    def get_weather_forecast(self, stadium_city: str, match_date_str: str) -> Dict[str, Any]:
        """Get weather forecast from Open-Meteo (permanently free, no API key required).

        Open-Meteo provides free weather data without requiring API keys.
        """
        # Open-Meteo API - free, no key required
        try:
            weather_url = self._build_weather_url(stadium_city, match_date_str)

            resp = requests.get(weather_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "temperature": data.get("current", {}).get("temperature", 15),
                    "humidity": data.get("current", {}).get("humidity", 60),
                    "wind_speed": data.get("current", {}).get("wind_speed", 5),
                    "precipitation": data.get("current", {}).get("precipitation", 0),
                    "visibility": data.get("current", {}).get("visibility", 10),
                    "condition": data.get("current", {}).get("weather_descriptions", ["Unknown"])[0],
                    "source": "open-meteo",
                }
        except Exception as e:
            print(f"Weather fetch error: {e}")

        # Return defaults if fetch fails
        return {
            "temperature": 15, "humidity": 60, "wind_speed": 5,
            "precipitation": 0, "visibility": 10, "condition": "Unknown",
            "source": "open-meteo-defaults",
        }

    def _build_weather_url(self, city: str, date_str: str) -> str:
        """Build Open-Meteo API URL for a given city and date."""
        # Map some major stadium cities to their approximate coordinates
        city_coords = {
            "london": "51.5074, -0.1278",
            "manchester": "53.4808, -2.2426",
            "liverpool": "53.4084, -2.9779",
            "manchester_city": "53.4634, -2.2936",  # Etihad Stadium
            "newcastle": "54.9712, -1.6138",
        }

        coords = city_coords.get(city.lower(), "51.5074, -0.1278")  # default to London

        # Open-Meteo API format: https://api.open-meteo.com/v1/forecast
        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords.split(",")[0],
            "longitude": coords.split(",")[1],
            "current_weather": "true",
            "timezone": "auto",
        }

        # Add daily forecasts for match day
        from datetime import datetime as dt
        try:
            match_date = dt.strptime(date_str, "%Y-%m-%d")
            day_str = match_date.strftime("%Y-%m-%d")
            params["start_date"] = day_str
            params["end_date"] = day_str
        except Exception:
            pass

        params_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{params_str}"

    def get_travel_distance(self, home_city: str, away_city: str) -> Dict[str, Any]:
        """Calculate travel distance using OpenStreetMap/Nominatim (free, no billing required).

        Uses rough distance estimates based on city names - in production would
        use OSM Nominetic API and Haversine formula.
        """
        distances_km = self._estimate_distance_km(home_city, away_city)

        return {
            "distance_km": distances_km,
            "estimated_travel_time_hours": round(distances_km / 60, 1),  # avg 60 km/h
            "rest_days_recommended": 2 if distances_km > 500 else 1,
            "source": "osm-distance-estimate",
        }

    def _estimate_distance_km(self, city1: str, city2: str) -> float:
        """Estimate distance between two cities in kilometers."""
        # Major UK city distance approximations
        uk_distances = {
            ("london", "manchester"): 262,
            ("manchester", "london"): 262,
            ("london", "liverpool"): 212,
            ("liverpool", "london"): 212,
            ("manchester", "liverpool"): 35,
            ("liverpool", "manchester"): 35,
            ("london", "newcastle"): 281,
            ("newcastle", "london"): 281,
            ("manchester", "newcastle"): 136,
            ("newcastle", "manchester"): 136,
        }

        key = (city1.lower(), city2.lower())
        if key in uk_distances:
            return uk_distances[key]

        # Default approximation
        return 200.0

    def get_motivation_context(self, home_team: str, away_team: str,
                                league_table: Dict[str, Any]) -> Dict[str, Any]:
        """Determine motivation context based on league position and matchweek.

        Free data: league tables from Football-Data.co.uk, standings from
        open fixtures and results analysis.
        """
        home_pos = league_table.get(home_team, {}).get("position", 0)
        away_pos = league_table.get(away_team, {}).get("position", 0)
        home_pts = league_table.get(home_team, {}).get("points", 0)
        away_pts = league_table.get(away_team, {}).get("points", 0)

        motivation_flags = []

        # Title race: top 3 still in it
        if home_pos <= 3 or away_pos <= 3:
            motivation_flags.append("title_contention")

        # Relegation battle: bottom 3
        if home_pos >= len(league_table) - 2 or away_pos >= len(league_table) - 2:
            motivation_flags.append("relegation_battle")

        # European competition: top 4 or 5
        if home_pos <= 4 or away_pos <= 4:
            motivation_flags.append("european_qualification")

        # Dead rubber: both teams with nothing to play for
        if len(motivation_flags) == 0:
            motivation_flags.append("dead_rubber")

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_position": home_pos,
            "away_position": away_pos,
            "home_motivation_flags": motivation_flags,
            "away_motivation_flags": motivation_flags,
            "neutral_site_indicator": len(motivation_flags) <= 1,
            "source": "league-table-analysis",
        }


# Convenience functions
def get_match_context(stadium_city: str, match_date: str,
                      home_team: str, away_team: str,
                      league_table: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get complete context for a match: weather, travel, motivation."""
    model = ContextModel()

    weather = model.get_weather_forecast(stadium_city, match_date)
    travel = model.get_travel_distance(home_team.split()[0] if home_team else "London",
                                        away_team.split()[0] if away_team else "London")
    motivation = model.get_motivation_context(home_team, away_team, league_table)

    return {
        "weather": weather,
        "travel": travel,
        "motivation": motivation,
        "match_date": match_date,
        "context_timestamp": datetime.now().isoformat(),
    }


def analyze_epl_context(seasons_back: int = 1) -> Dict[str, Any]:
    """Analyze context factors for EPL matches."""
    data = fetch_epl_match_stats(seasons_back)
    analytics = EventAnalytics()

    context_factors: Dict[str, Any] = {}

    if data and "matches" in data:
        context_factors["matches_analyzed"] = len(data["matches"])
        context_factors["data_quality"] = "historical_match_stats"

    return context_factors