"""Results ingestion module for soccer-prediction-app.

Uses permanently free data sources for historical match results.
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta


class ResultsIngestion:
    """Ingest historical match results from free sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.session = requests.Session()
        self.use_free_alt = api_key is None
    
    def get_results(self, 
                    competition_code: str = "PL",
                    date_from: Optional[str] = None,
                    date_to: Optional[str] = None,
                    limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get historical results for a competition."""
        if self.api_key:
            url = f"{self.base_url}/matches"
            params = {"competition": competition_code, "limit": limit}
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
                    self.use_free_alt = True
            except Exception as e:
                print(f"API error, falling back to CSV: {e}")
        
        # Fall back to Football-Data.co.uk CSVs which have historical results
        return self._fetch_results_from_csv(competition_code, date_from, date_to, limit)
    
    def _season_to_csv_format(self, season_str: str) -> str:
        """Convert internal season format (e.g. '2024-2025') to CSV format (e.g. '2425').
        
        Football-Data.co.uk uses a 4-digit compressed format where:
        - 2324 = 2023-24 season
        - 2425 = 2024-25 season  
        - 2526 = 2025-26 season
        """
        parts = season_str.split('-')
        if len(parts) >= 2:
            start_year = int(parts[0])
            # Format: last 2 digits of start year + last 2 digits of end year
            return f"{(start_year - 1) % 100:02d}{start_year % 100:02d}"
        return season_str
    
    def _get_season_from_dates(self, date_from: Optional[str], date_to: Optional[str]) -> str:
        """Determine season year from date range.
        
        Returns internal format like '2024-2025' which is then converted
        to CSV format via _season_to_csv_format().
        """
        now = datetime.now()
        
        if date_from and date_to:
            # Use the year from date_from
            fy = datetime.strptime(date_from, "%Y-%m-%d")
            return f"{fy.year - 1}-{fy.year}" if fy.month > 7 else f"{fy.year}-{fy.year + 1}"
        
        # Default to current/recent season
        if now.month > 7:
            return f"{now.year - 1}-{now.year}"
        return f"{now.year}-{now.year + 1}"
    
    def _fetch_results_from_csv(self, 
                                competition_code: str,
                                date_from: Optional[str] = None,
                                date_to: Optional[str] = None,
                                limit: int = 100) -> Optional[Dict[str, Any]]:
        """Fetch results from Football-Data.co.uk CSV files."""
        season_internal = self._get_season_from_dates(date_from, date_to)
        season_csv = self._season_to_csv_format(season_internal)
        csv_url = f"https://www.football-data.co.uk/mmz4281/{season_csv}/{competition_code.lower()}.csv"
        
        try:
            resp = self.session.get(csv_url, timeout=30)
            if resp.status_code == 200:
                return self._parse_csv_results(resp.text, competition_code, limit)
            else:
                print(f"CSV URL returned {resp.status_code}: {csv_url}")
        except Exception as e:
            print(f"CSV results error: {e}")
        
        return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition_code, "note": "fallback"}
    
    def _parse_csv_results(self, csv_text: str, competition_code: str, limit: int) -> Optional[Dict[str, Any]]:
        """Parse Football-Data.co.uk CSV results.
        
        Confirmed column order from data inspection:
        Div, Date, Time, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAG, HTR, HS, AS, HST, AST, HF, AF, HC, AC, HY, AY, HR, AR, B365H, B365D, B365A, BWH, BWD, BWA, BFH, BFD, BFA, PSD, ... etc.
        
        Key columns:
        - Date (index 1)
        - HomeTeam (index 3)  
        - AwayTeam (index 4)
        - FTHG (index 5) - Full Time Home Goals
        - FTAG (index 6) - Full Time Away Goals
        - FTR (index 7) - Full Time Result: H=home win, D=draw, A=away win
        """
        lines = csv_text.strip().split('\n')
        if not lines or len(lines) < 2:
            return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition_code}
        
        # Skip header row, parse data rows
        matches = []
        
        # Column positions (0-indexed from our data inspection):
        # 0=Div, 1=Date, 2=Time, 3=HomeTeam, 4=AwayTeam, 5=FTHG, 6=FTAG, 7=FTR
        DATE_IDX = 1
        HOME_IDX = 3
        AWAY_IDX = 4
        HGOALS_IDX = 5
        AGOALS_IDX = 6
        RESULT_IDX = 7
        
        # Parse up to limit rows (or all available)
        end_idx = min(limit + 1, len(lines))
        for i, line in enumerate(lines[1:end_idx]):
            values = line.split(',')
            if len(values) < RESULT_IDX + 1:
                continue
            
            match_date = values[DATE_IDX]
            home_team = values[HOME_IDX]
            away_team = values[AWAY_IDX]
            home_goals_str = values[HGOALS_IDX]
            away_goals_str = values[AGOALS_IDX]
            result = values[RESULT_IDX]  # H=home win, D=draw, A=away win
            
            # Only include matches with complete data
            if not home_goals_str or not away_goals_str:
                continue
            
            try:
                home_goals = int(home_goals_str)
                away_goals = int(away_goals_str)
            except ValueError:
                continue
            
            match = {
                "date": match_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": result,  # H=home win, D=draw, A=away win
                "competition": competition_code,
            }
            matches.append(match)
        
        return {"matches": matches, "source": "football-data.co.uk CSV", "competition": competition_code}
    
    def save_raw(self, data: Dict[str, Any], league: str, season: str = "historical") -> Path:
        """Save raw results data to data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{league}_{season}_results.json"
        filepath = raw_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Saved raw results to {filepath}")
        return filepath
    
    def load_raw(self, league: str, season: str = "historical") -> Optional[Dict[str, Any]]:
        """Load raw results data from data/raw/."""
        raw_dir = Path("soccer-prediction-app/data/raw")
        filepath = raw_dir / f"{league}_{season}_results.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def standardize_team_names(self, matches_data: List[Dict]) -> Dict[str, str]:
        """Standardize team names across sources."""
        name_map = {}
        for match in matches_data:
            home = match.get("home_team")
            away = match.get("away_team")
            
            if home:
                name_map[home] = home.strip().title()
            if away:
                name_map[away] = away.strip().title()
        
        return name_map
    
    def get_head_to_head(self, 
                        home_team: str, away_team: str,
                        competition_code: str = "PL",
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Get head-to-head record between two teams."""
        data = self.get_results(competition_code, limit=limit * 2)
        if not data:
            return []
        
        h2h = []
        for match in data.get("matches", []):
            if (match.get("home_team") == home_team and match.get("away_team") == away_team) or \
               (match.get("home_team") == away_team and match.get("away_team") == home_team):
                h2h.append(match)
                
                if len(h2h) >= limit:
                    break
        
        return h2h


# Convenience functions
def fetch_epl_results(api_key: Optional[str] = None, 
                      years_back: int = 5) -> Dict[str, Any]:
    """Fetch EPL historical results."""
    ingestor = ResultsIngestion(api_key)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back * 365)).strftime("%Y-%m-%d")
    
    data = ingestor.get_results("PL", start_date, end_date, limit=500)
    if data:
        ingestor.save_raw(data, "EPL", f"{years_back}y")
    return data


def fetch_bundesliga_results(api_key: Optional[str] = None, 
                             years_back: int = 5) -> Dict[str, Any]:
    """Fetch Bundesliga historical results."""
    ingestor = ResultsIngestion(api_key)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back * 365)).strftime("%Y-%m-%d")
    
    data = ingestor.get_results("BL1", start_date, end_date, limit=500)
    if data:
        ingestor.save_raw(data, "BL1", f"{years_back}y")
    return data


def fetch_serie_a_results(api_key: Optional[str] = None, 
                          years_back: int = 5) -> Dict[str, Any]:
    """Fetch Serie A historical results."""
    ingestor = ResultsIngestion(api_key)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back * 365)).strftime("%Y-%m-%d")
    
    data = ingestor.get_results("SA", start_date, end_date, limit=500)
    if data:
        ingestor.save_raw(data, "SA", f"{years_back}y")
    return data