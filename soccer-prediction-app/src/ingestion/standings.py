"""Standings ingestion module for soccer-prediction-app.

Uses permanently free data sources for league tables and standings.
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime


class StandingsIngestion:
    """Ingest league standings/tables from free sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.session = requests.Session()
        self.use_free_alt = api_key is None
    
    def get_standings(self, competition_code: str = "PL") -> Optional[Dict[str, Any]]:
        """Get current league table/standings."""
        if self.api_key:
            url = f"{self.base_url}/competitions/{competition_code}/standings"
            headers = {"X-Auth-Token": self.api_key}
            try:
                resp = self.session.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalize_standings(data)
                elif resp.status_code == 401:
                    self.use_free_alt = True
            except Exception as e:
                print(f"Standings API error: {e}")
        
        # Fall back to Football-Data.co.uk CSVs
        return self._fetch_from_csv(competition_code)
    
    def _fetch_from_csv(self, competition_code: str) -> Optional[Dict[str, Any]]:
        """Fetch standings from Football-Data.co.uk CSV."""
        season = self._current_season()
        csv_url = f"https://www.football-data.co.uk/mmz4281/{season}/{competition_code.lower()}.csv"
        
        try:
            resp = self.session.get(csv_url, timeout=30)
            if resp.status_code == 200:
                return self._parse_csv_standings(resp.text, competition_code)
        except Exception as e:
            print(f"CSV standings error: {e}")
        
        return {"standings": [], "source": "football-data.co.uk CSV", "competition": competition_code}
    
    def _current_season(self) -> str:
        """Get current season year string."""
        now = datetime.now()
        if now.month > 7:
            return f"{now.year}-{now.year + 1}"
        return f"{now.year - 1}-{now.year}"
    
    def _parse_csv_standings(self, csv_text: str, competition_code: str) -> Optional[Dict[str, Any]]:
        """Parse Football-Data.co.uk CSV into structured standings."""
        lines = csv_text.strip().split('\n')
        if not lines or len(lines) < 3:
            return {"standings": [], "source": "football-data.co.uk CSV", "competition": competition_code}
        
        # CSV columns vary by season, but typically:
        # Pos, Team, Pld, W, D, L, GF, GA, GD, Pts
        standings = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) < 10:
                continue
            
            try:
                pos = int(values[0])
                team = values[1].strip()
                Pld = int(values[2])
                W = int(values[3])
                D = int(values[4])
                L = int(values[5])
                GF = int(values[6])
                GA = int(values[7])
                GD = int(values[8])
                Pts = int(values[9])
                
                standings.append({
                    "position": pos,
                    "team": team,
                    "played": Pld,
                    "won": W,
                    "drawn": D,
                    "lost": L,
                    "goals_for": GF,
                    "goals_against": GA,
                    "goal_difference": GD,
                    "points": Pts,
                })
            except (ValueError, IndexError):
                continue
        
        return {"standings": standings, "source": "football-data.co.uk CSV", "competition": competition_code}
    
    def save_raw(self, data: Dict[str, Any], league: str) -> Path:
        """Save raw standings data to data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{league}_standings.json"
        filepath = raw_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Saved raw standings to {filepath}")
        return filepath
    
    def load_raw(self, league: str) -> Optional[Dict[str, Any]]:
        """Load raw standings data from data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        filepath = raw_dir / f"{league}_standings.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_top_n(self, standings_data: Dict, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N teams from standings."""
        return standings_data.get("standings", [])[:n]
    
    def get_relegation_zones(self, standings_data: Dict, n: int = 3) -> List[Dict[str, Any]]:
        """Get bottom N teams (relegation zone)."""
        standings = standings_data.get("standings", [])
        return standings[-n:] if len(standings) >= n else standings


# Convenience functions
def fetch_epl_standings(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch current EPL standings."""
    ingestor = StandingsIngestion(api_key)
    data = ingestor.get_standings("PL")
    if data:
        ingestor.save_raw(data, "EPL")
    return data


def fetch_bundesliga_standings(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch current Bundesliga standings."""
    ingestor = StandingsIngestion(api_key)
    data = ingestor.get_standings("BL1")
    if data:
        ingestor.save_raw(data, "BL1")
    return data


def fetch_serie_a_standings(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch current Serie A standings."""
    ingestor = StandingsIngestion(api_key)
    data = ingestor.get_standings("SA")
    if data:
        ingestor.save_raw(data, "SA")
    return data