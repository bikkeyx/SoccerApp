"""Context and environment modeling for soccer-prediction-app.

Phase 4: Context and Environment Modeling
Adds situational variables that affect match outcomes: weather, travel, rest,
venue conditions, and motivation context.
"""

import sys
import math
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

EARTH_RADIUS_KM = 6371.0


class WeatherData:
    """Weather information for a stadium location and kickoff time."""

    def __init__(self, temperature: float, humidity: float,
                 wind_speed: float, precipitation: float,
                 visibility: float, conditions: str):
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.precipitation = precipitation
        self.visibility = visibility
        self.conditions = conditions  # e.g., 'clear', 'rain', 'cloudy'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "precipitation": self.precipitation,
            "visibility": self.visibility,
            "conditions": self.conditions,
        }

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "WeatherData":
        """Create WeatherData from Open-Meteo API response."""
        return WeatherData(
            temperature=float(data.get("temperature", 15.0)),
            humidity=float(data.get("humidity", 60.0)),
            wind_speed=float(data.get("wind_speed", 5.0)),
            precipitation=float(data.get("precipitation", 0.0)),
            visibility=float(data.get("visibility", 10000.0)),
            conditions=data.get("weather_conditions", "clear"),
        )


def get_weather(stadium_lat: float, stadium_lon: float,
                kickoff_hour: int) -> WeatherData:
    """Fetch weather forecast from Open-Meteo for stadium location.

    Open-Meteo is free, no API key required.
    """
    import requests

    # Get forecast for kickoff time - use the stadium coordinates
    url = "https://api.open-meteo.com/v1/forecast"

    # Calculate the date for the kickoff match
    now = datetime.now()
    days_ahead = max(0, (kickoff_hour - now.hour + 24 * (0 if kickoff_hour >= now.hour else 1)) // 24)
    forecast_date = now.strftime("%Y-%m-%d")

    params = {
        "latitude": stadium_lat,
        "longitude": stadium_lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,visibility,",
        "weathercode": "true",
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()

            # Find the closest hour to kickoff
            times = data.get("hourly", {}).get("time", [])
            temps = data.get("hourly", {}).get("temperature_2m", [])
            humidity = data.get("hourly", {}).get("relative_humidity_2m", [])
            winds = data.get("hourly", {}).get("wind_speed_10m", [])
            precips = data.get("hourly", {}).get("precipitation", [])
            visibilities = data.get("hourly", {}).get("visibility", [])
            weathercodes = data.get("hourly", {}).get("weathercode", [])

            # Map weathercode to conditions
            weather_code_map = {
                0: "clear", 1: "partly_cloudy", 2: "cloudy",
                3: "overcast", 45: "fog", 48: "depositing_fog",
                51: "light_drizzle", 53: "moderate_drizzle", 55: "dense_drizzle",
                61: "light_rain", 63: "moderate_rain", 65: "heavy_rain",
                71: "light_snow", 73: "moderate_snow", 75: "heavy_snow",
                80: "light_rain_showers", 81: "moderate_rain_showers",
                82: "violent_rain_showers",
            }

            # Find closest to kickoff (hour 15 typical for matches)
            kickoff_idx = 0
            if times:
                for i, t in enumerate(times):
                    if "15:00" in t or "17:00" in t or "19:00" in t:
                        kickoff_idx = i
                        break

            idx = min(kickoff_idx, len(times) - 1) if times else 0

            # Get weather conditions
            weather_code = weathercodes[idx] if idx < len(weathercodes) else 0
            conditions = weather_code_map.get(weather_code, "clear")

            return WeatherData(
                temperature=temps[idx] if idx < len(temps) else 15.0,
                humidity=humidity[idx] if idx < len(humidity) else 60.0,
                wind_speed=winds[idx] if idx < len(winds) else 5.0,
                precipitation=precips[idx] if idx < len(precips) else 0.0,
                visibility=visibilities[idx] if idx < len(visibilities) else 10000.0,
                conditions=conditions,
            )
    except Exception as e:
        print(f"Weather API error: {e}")

    # Return default weather if API fails
    return WeatherData(temperature=15.0, humidity=60.0,
                       wind_speed=5.0, precipitation=0.0,
                       visibility=10000.0, conditions="clear")


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in kilometers."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * c


def calculate_travel_distance(home_stadium: Dict[str, Any],
                              away_stadium: Dict[str, Any]) -> float:
    """Calculate travel distance between two stadiums."""
    return haversine_distance_km(
        home_stadium["latitude"], home_stadium["longitude"],
        away_stadium["latitude"], away_stadium["longitude"]
    )


def calculate_rest_days(last_match_date: Optional[str],
                        next_match_date: Optional[str]) -> Optional[int]:
    """Calculate rest days between two matches."""
    if not last_match_date or not next_match_date:
        return None

    from datetime import datetime
    try:
        last = datetime.strptime(last_match_date, "%Y-%m-%d")
        next_ = datetime.strptime(next_match_date, "%Y-%m-%d")
        delta = (next_ - last).days
        return max(delta, 0)
    except ValueError:
        return None


class VenueEffects:
    """Calculate venue-related effects on match outcomes."""

    def __init__(self):
        self.venue_data: Dict[str, Dict[str, Any]] = {}

    def add_stadium(self, stadium_name: str, latitude: float,
                    longitude: float, surface: str = "grass",
                    altitude: float = 0.0,
                    pitch_length: float = 105.0, pitch_width: float = 68.0) -> None:
        """Add stadium metadata for venue effect calculations."""
        self.venue_data[stadium_name] = {
            "latitude": latitude,
            "longitude": longitude,
            "surface": surface,
            "altitude": altitude,
            "pitch_length": pitch_length,
            "pitch_width": pitch_width,
        }

    def get_venue_effects(self, stadium_name: str) -> Dict[str, Any]:
        """Get venue effects for a specific stadium."""
        if stadium_name not in self.venue_data:
            return {
                "home_advantage": 0.1,  # Default 10% home advantage
                "surface": "grass",
                "altitude": 0.0,
                "note": "Using default values - stadium not in database"
            }

        v = self.venue_data[stadium_name]
        # Higher altitude can favor home team due to conditioning
        altitude_factor = v["altitude"] / 500.0 * 0.02  # 2% per 500m, max ~10%
        altitude_factor = min(altitude_factor, 0.1)

        # Surface type effects
        surface_factor = 0.05 if v["surface"] == "grass" else -0.02  # Grass slightly favors traditional style

        return {
            "home_advantage": round(0.1 + altitude_factor + surface_factor, 3),
            "surface": v["surface"],
            "altitude": v["altitude"],
            "pitch_dimensions": {"length": v["pitch_length"], "width": v["pitch_width"]},
        }

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


class MotivationContext:
    """Determine motivation/context factors for teams in a match."""

    # Competition importance weights (higher = more motivated)
    COMPETITION_WEIGHTS = {
        "champions_league": 1.3,
        "europa_league": 1.2,
        "conference_league": 1.1,
        "national_cup_final": 1.5,
        "national_cup_semi": 1.3,
        "national_cup_quarter": 1.2,
        "relegation": 1.4,
        "title_race": 1.5,
        "european_qualification": 1.2,
        "dead_rubber": 0.8,  # Low motivation
        "mid_table": 1.0,
    }

    def assess_motivation(self, team_data: Dict[str, Any],
                          competition: str) -> float:
        """Assess motivation factor for a team based on competition and position."""
        weight = self.COMPETITION_WEIGHTS.get(competition, 1.0)

        # Adjust based on team position/standing
        position = team_data.get("position", "mid_table")

        if competition in ["title_race", "relegation"]:
            # Teams at extremes have higher motivation
            if position in ["1", "2", "3", "4", "15", "16", "17", "18", "19", "20"]:
                weight *= 1.2

        # European competition motivation
        if competition in ["champions_league", "europa_league"]:
            if position in ["1", "2", "3", "4"]:
                weight *= 1.1  # Top teams extra motivated for UCL

        # Cup finals have highest motivation
        if "final" in competition.lower() or "final" in competition:
            weight = 1.5

        return weight


def analyze_context(epl_matches_data: List[Dict[str, Any]],
                  stadium_db: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Full context analysis for EPL matches."""
    from src.players.availability import calculate_rest_days

    analytics = EventAnalytics()
    venue_effects = VenueEffects()

    # Load stadium data
    for name, info in stadium_db.items():
        venue_effects.add_stadium(
            name, info.get("latitude", 0), info.get("longitude", 0),
            info.get("surface", "grass"), info.get("altitude", 0)
        )

    # Calculate venue splits
    venue_splits = analytics.calculate_home_away_splits(epl_matches_data)

    # Calculate referee profiles
    referee_profile = analytics.calculate_referee_profile(epl_matches_data)

    return {
        "venue_splits": venue_splits,
        "referee_profile": referee_profile,
        "stadium_database": dict(stadium_db),
    }


# Example stadium database (lat/lon for Premier League stadiums)
STADIUM_DATABASE: Dict[str, Dict[str, Any]] = {
    "Old Trafford": {"latitude": 53.4631, "longitude": -2.2910, "surface": "grass", "altitude": 50},
    "Etihad Stadium": {"latitude": 53.4608, "longitude": -0.0262, "surface": "grass", "altitude": 32},
    "Anfield": {"latitude": 51.5062, "longitude": -2.0425, "surface": "grass", "altitude": 25},
    "Stamford Bridge": {"latitude": 51.4808, "longitude": -0.1909, "surface": "grass", "altitude": 3},
    "Emirates Stadium": {"latitude": 51.5562, "longitude": -0.1160, "surface": "grass", "altitude": 15},
    "St. James' Park": {"latitude": 54.9711, "longitude": -1.6138, "surface": "grass", "altitude": 60},
    "Selhurst Park": {"latitude": 51.3781, "longitude": -0.0821, "surface": "grass", "altitude": 30},
    "London Stadium": {"latitude": 51.5375, "longitude": 0.0173, "surface": "grass", "altitude": 24},
    "Villa Park": {"latitude": 52.4814, "longitude": -1.9139, "surface": "grass", "altitude": 85},
    "Molineux": {"latitude": 52.2618, "longitude": -2.2056, "surface": "grass", "altitude": 48},
}