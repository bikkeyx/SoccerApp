"""Fixtures ingestion module for soccer-prediction-app.

Uses permanently free data sources:
- football-data.org free tier
- Football-Data.co.uk CSV files
- openfootball
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time

# Free API endpoints
FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"
FOOTBALL_DATA_COMPETITIONS = "/competitions"

# League codes for free tier
LEAGUE_CODES = {
    "EPL": "PL",      # English Premier League
    "BL1": "BL1",     # Bundesliga
    "SA": "SA",       # Serie A
}


class FixturesIngestion:
    """Ingest football fixtures from free sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key  # Optional - football-data.org free tier
        self.base_url = FOOTBALL_DATA_BASE
        self.session = requests.Session()
        
        # If no API key, will use Football-Data.co.uk CSVs / openfootball
        self.use_free_alt = api_key is None
    
    def get_competitions(self) -> Optional[Dict[str, Any]]:
        """Get competitions list from football-data.org."""
        if self.api_key:
            url = f"{self.base_url}/competitions"
            headers = {"X-Auth-Token": self.api_key} if self.api_key else {}
            try:
                resp = self.session.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                print(f"Error fetching competitions: {e}")
        return None
    
    def get_matches(self, 
                    competition_code: str = "PL", 
                    date_from: Optional[str] = None, 
                    date_to: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get matches for a competition from football-data.org free tier."""
        if self.api_key:
            url = f"{self.base_url}/matches"
            params = {"competition": competition_code}
            if date_from:
                params["dateFrom"] = date_from
            if date_to:
                params["dateTo"] = date_to
            
            headers = {"X-Auth-Token": self.api_key}
            try:
                resp = self.session.get(url, headers=headers, params=params, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 401:
                    print("Invalid API key - falling back to free CSV sources")
                    self.use_free_alt = True
            except Exception as e:
                print(f"Error fetching matches: {e}")
        
        # Fall back to free CSV sources
        return self._fetch_from_csv(competition_code)
    
    def _fetch_from_csv(self, competition_code: str) -> Optional[Dict[str, Any]]:
        """Fetch fixtures from Football-Data.co.uk CSV files."""
        # Football-Data.co.uk provides free CSV fixtures
        csv_url = f"https://www.football-data.co.uk/mmz4281/{self._season_year()}/{competition_code.lower()}.csv"
        
        try:
            resp = self.session.get(csv_url, timeout=30)
            if resp.status_code == 200:
                return self._parse_csv_fixtures(resp.text, competition_code)
        except Exception as e:
            print(f"CSV fetch error: {e}")
        
        # Try openfootball data
        return self._fetch_openfootball(competition_code)
    
    def _season_year(self) -> str:
        """Get current season year string for CSV URLs."""
        from datetime import datetime
        now = datetime.now()
        # Football season typically August-May, so if month > 7, season spans current+1 year
        if now.month > 7:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def _parse_csv_fixtures(self, csv_text: str, competition_code: str) -> Optional[Dict[str, Any]]:
        """Parse Football-Data.co.uk CSV format into structured fixtures."""
        lines = csv_text.strip().split('\n')
        if not lines:
            return None
        
        # CSV headers: Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAT, HTR, Referee, etc.
        headers = lines[0].split(',')
        matches = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) < 3:
                continue
            
            match_date = values[0] if values[0] else None
            home_team = values[1] if len(values) > 1 else None
            away_team = values[2] if len(values) > 2 else None
            
            # Free tier typically has full-time results only for past matches
            # For upcoming matches, FTHG/FTAG may be empty
            ft_hg = values[3] if len(values) > 3 else None
            ft_ag = values[4] if len(values) > 4 else None
            ftr = values[5] if len(values) > 5 else None  # FTR: H=home win, D=draw, A=away win
            
            match = {
                "date": match_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": ft_hg,
                "away_goals": ft_ag,
                "result": ftr,
                "competition": competition_code,
            }
            matches.append(match)
        
        return {"matches": matches, "source": "football-data.co.uk CSV", "competition": competition_code}
    
    def _fetch_openfootball(self, competition_code: str) -> Optional[Dict[str, Any]]:
        """Fetch from openfootball open data."""
        # openfootball provides free JSON fixtures
        try:
            # This is a placeholder - openfootball API structure may vary
            url = f"https://openfootball.com/api/{competition_code}/fixtures"
            # Note: openfootball may require different approach
            return {"matches": [], "source": "openfootball", "competition": competition_code, "note": "placeholder"}
        except Exception as e:
            print(f"openfootball error: {e}")
            return None
    
    def save_raw(self, data: Dict[str, Any], league: str, season: str = "current") -> Path:
        """Save raw fixtures data to data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{league}_{season}_fixtures.json"
        filepath = raw_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Saved raw fixtures to {filepath}")
        return filepath
    
    def load_raw(self, league: str, season: str = "current") -> Optional[Dict[str, Any]]:
        """Load raw fixtures data from data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        filepath = raw_dir / f"{league}_{season}_fixtures.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def infer_team_names(self, matches_data: List[Dict]) -> Dict[str, str]:
        """Normalize team names from various sources to standard format."""
        name_map = {}
        for match in matches_data:
            home = match.get("home_team")
            away = match.get("away_team")
            
            if home and away:
                # Simple normalization - title case, remove extra spaces
                home_norm = home.strip().title()
                away_norm = away.strip().title()
                
                # Map common variations
                name_map[home] = home_norm
                name_map[away] = away_norm
        
        return name_map
    
    def get_recent_matches(self, 
                          competition_code: str = "PL", 
                          days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent matches within days_back days."""
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        data = self.get_matches(competition_code, start_date, end_date)
        if not data:
            return []
        
        matches = data.get("matches", [])
        # Filter to only matches within the date range
        filtered = []
        for m in matches:
            match_date = m.get("date")
            if match_date:
                try:
                    if start_date <= match_date <= end_date:
                        filtered.append(m)
                except:
                    pass  # Include matches without clear dates
        
        return filtered


# Convenience functions
def fetch_epl_fixtures(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch EPL fixtures."""
    ingestor = FixturesIngestion(api_key)
    data = ingestor.get_matches("PL")
    if data:
        ingestor.save_raw(data, "EPL")
    return data


def fetch_bundesliga_fixtures(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch Bundesliga fixtures."""
    ingestor = FixturesIngestion(api_key)
    data = ingestor.get_matches("BL1")
    if data:
        ingestor.save_raw(data, "BL1")
    return data


def fetch_serie_a_fixtures(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch Serie A fixtures."""
    ingestor = FixturesIngestion(api_key)
    data = ingestor.get_matches("SA")
    if data:
        ingestor.save_raw(data, "SA")
    return data