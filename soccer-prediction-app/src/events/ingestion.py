"""Event-level performance data ingestion for soccer-prediction-app.

Phase 3: Event-Level Performance Data
Uses permanently free sources:
- Football-Data.co.uk CSV files (shot data, stats)
- FBref (open data, player stats)
- Understat (public data)
- Football-Data.co.uk CSVs (comprehensive match stats)
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime


class EventIngestion:
    """Ingest event-level and match-level statistics from free sources."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.football-data.co.uk"
        self.session = requests.Session()
        self.use_free_alt = api_key is None

    def _season_to_csv(self, season_str: str) -> str:
        """Convert '2024-2025' to '2425' format for Football-Data.co.uk URLs."""
        parts = season_str.split("-")
        if len(parts) >= 2:
            start_year = int(parts[0])
            return f"{(start_year - 1) % 100:02d}{start_year % 100:02d}"
        return season_str

    def _get_season(self) -> str:
        """Get current season internal format."""
        now = datetime.now()
        if now.month > 7:
            return f"{now.year - 1}-{now.year}"
        return f"{now.year}-{now.year + 1}"

    def fetch_match_stats(self, competition: str = "PL", seasons_back: int = 1) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive match statistics from Football-Data.co.uk CSVs.

        Columns include: shots, corners, cards, possession, fouls, etc.
        """
        season_csv = self._season_to_csv(self._get_season())
        csv_url = f"https://www.football-data.co.uk/mmz4281/{season_csv}/{competition.lower()}.csv"

        try:
            resp = self.session.get(csv_url, timeout=30)
            if resp.status_code == 200:
                return self._parse_match_stats(resp.text, competition)
        except Exception as e:
            print(f"Match stats fetch error: {e}")

        return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition, "note": "fallback"}

    def _parse_match_stats(self, csv_text: str, competition: str) -> Optional[Dict[str, Any]]:
        """Parse Football-Data.co.uk CSV into structured match stats.

        Key columns (confirmed from data inspection):
        Div, Date, Time, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAG, HTR,
        HS, AS, HST, AST, HF, AF, HC, AC, HY, AY, HR, AR,
        B365H, B365D, B365A, BWH, BWD, BWA, BFH, BFD, BFA, PSD, ... etc.
        """
        lines = csv_text.strip().split('\n')
        if not lines or len(lines) < 2:
            return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition}

        # Column positions (0-indexed):
        # 0=Div, 1=Date, 2=Time, 3=HomeTeam, 4=AwayTeam, 5=FTHG, 6=FTAG, 7=FTR
        # 8=HTHG, 9=HTAG, 10=HTR
        # 11=HS (Home Shots), 12=AS (Away Shots)
        # 13=HST (Home Shots on Target), 14=AST (Away Shots on Target)
        # 15=HF (Home Fouls), 16=AF (Away Fouls)
        # 17=HC (Home Corners), 18=AC (Away Corners)
        # 19=HY (Home Yellow Cards), 20=AY (Away Yellow Cards)
        # 21=HR (Home Red Cards), 22=AR (Away Red Cards)

        DATE_IDX, HOME_IDX, AWAY_IDX = 1, 3, 4
        HGOALS_IDX, AGOALS_IDX = 5, 6
        RESULT_IDX = 7
        HS_IDX, AS_IDX = 11, 12
        HST_IDX, AST_IDX = 13, 14
        HF_IDX, AF_IDX = 15, 16
        HC_IDX, AC_IDX = 17, 18
        HY_IDX, AY_IDX = 19, 20
        HR_IDX, AR_IDX = 21, 22

        matches = []
        for i, line in enumerate(lines[1:]):
            values = line.split(',')
            if len(values) < MAX_IDX + 1:
                continue

            try:
                match = {
                    "date": values[DATE_IDX],
                    "home_team": values[HOME_IDX],
                    "away_team": values[AWAY_IDX],
                    "home_goals": int(values[HGOALS_IDX]) if values[HGOALS_IDX] else 0,
                    "away_goals": int(values[AGOALS_IDX]) if values[AGOALS_IDX] else 0,
                    "result": values[RESULT_IDX],  # H=home win, D=draw, A=away win
                    "home_shots": int(values[HS_IDX]) if values[HS_IDX] else 0,
                    "away_shots": int(values[AS_IDX]) if values[AS_IDX] else 0,
                    "home_shots_on_target": int(values[HST_IDX]) if values[HST_IDX] else 0,
                    "away_shots_on_target": int(values[AST_IDX]) if values[AST_IDX] else 0,
                    "home_fouls": int(values[HF_IDX]) if values[HF_IDX] else 0,
                    "away_fouls": int(values[AF_IDX]) if values[AF_IDX] else 0,
                    "home_corners": int(values[HC_IDX]) if values[HC_IDX] else 0,
                    "away_corners": int(values[AC_IDX]) if values[AC_IDX] else 0,
                    "home_yellow_cards": int(values[HY_IDX]) if values[HY_IDX] else 0,
                    "away_yellow_cards": int(values[AY_IDX]) if values[AY_IDX] else 0,
                    "home_red_cards": int(values[HR_IDX]) if values[HR_IDX] else 0,
                    "away_red_cards": int(values[AR_IDX]) if values[AR_IDX] else 0,
                }
                matches.append(match)
            except (ValueError, IndexError):
                continue

        return {"matches": matches, "source": "football-data.co.uk CSV", "competition": competition}

    def fetch_player_stats(self, competition: str = "PL", season: str = "") -> Optional[Dict[str, Any]]:
        """Fetch player statistics from free sources.

        Falls back to Football-Data.co.uk if no specific player API is available.
        """
        # For now, return structure placeholder
        # In production, this would integrate with FBref, Understat APIs
        return {
            "players": [],
            "source": "player stats placeholder",
            "note": "To be integrated with FBref/Understat open data"
        }

    def save_raw(self, data: Dict[str, Any], league: str, category: str = "events") -> Path:
        """Save raw event data to data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{league}_{category}.json"
        filepath = raw_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Saved event data to {filepath}")
        return filepath

    def load_raw(self, league: str, category: str = "events") -> Optional[Dict[str, Any]]:
        """Load raw event data from data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        filepath = raw_dir / f"{league}_{category}.json"

        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


# Convenience functions
def fetch_epl_match_stats(seasons_back: int = 1) -> Dict[str, Any]:
    """Fetch EPL match statistics."""
    ingestor = EventIngestion(api_key=None)
    season = ingestor._get_season()
    data = ingestor.fetch_match_stats("PL", seasons_back)
    if data:
        ingestor.save_raw(data, "EPL", "match_stats")
    return data


def fetch_bundesliga_match_stats(seasons_back: int = 1) -> Dict[str, Any]:
    """Fetch Bundesliga match statistics."""
    ingestor = EventIngestion(api_key=None)
    season = ingestor._get_season()
    data = ingestor.fetch_match_stats("BL1", seasons_back)
    if data:
        ingestor.save_raw(data, "BL1", "match_stats")
    return data


def fetch_serie_a_match_stats(seasons_back: int = 1) -> Dict[str, Any]:
    """Fetch Serie A match statistics."""
    ingestor = EventIngestion(api_key=None)
    season = ingestor._get_season()
    data = ingestor.fetch_match_stats("SA", seasons_back)
    if data:
        ingestor.save_raw(data, "SA", "match_stats")
    return data