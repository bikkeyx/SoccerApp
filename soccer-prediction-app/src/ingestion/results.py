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
    
    def _fetch_results_from_csv(self, 
                                competition_code: str,
                                date_from: Optional[str] = None,
                                date_to: Optional[str] = None,
                                limit: int = 100) -> Optional[Dict[str, Any]]:
        """Fetch results from Football-Data.co.uk CSV files."""
        season = self._get_season_from_dates(date_from, date_to)
        csv_url = f"https://www.football-data.co.uk/mmz4281/{season}/{competition_code.lower()}.csv"
        
        try:
            resp = self.session.get(csv_url, timeout=30)
            if resp.status_code == 200:
                return self._parse_csv_results(resp.text, competition_code, limit)
        except Exception as e:
            print(f"CSV results error: {e}")
        
        return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition_code, "note": "fallback"}
    
    def _get_season_from_dates(self, date_from: Optional[str], date_to: Optional[str]) -> str:
        """Determine season year from date range."""
        from datetime import datetime
        now = datetime.now()
        
        if date_from and date_to:
            # Use the year from date_from
            fy = datetime.strptime(date_from, "%Y-%m-%d")
            return f"{fy.year - 1}-{fy.year}" if fy.month > 7 else f"{fy.year}-{fy.year + 1}"
        
        # Default to current/recent season
        if now.month > 7:
            return f"{now.year - 1}-{now.year}"
        return f"{now.year}-{now.year + 1}"
    
    def _parse_csv_results(self, csv_text: str, competition_code: str, limit: int) -> Optional[Dict[str, Any]]:
        """Parse Football-Data.co.uk CSV results."""
        lines = csv_text.strip().split('\n')
        if not lines or len(lines) < 2:
            return {"matches": [], "source": "football-data.co.uk CSV", "competition": competition_code}
        
        headers = lines[0].split(',')
        matches = []
        
        # Column indices for Football-Data.co.uk CSV
        # Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAT, HTR, ... etc.
        for line in lines[1:limit]:
            values = line.split(',')
            if len(values) < 6:
                continue
            
            match_date = values[0]
            home_team = values[1]
            away_team = values[2]
            home_goals = values[3]
            away_goals = values[4]
            result = values[5]  # FTR
            
            # Only include matches with complete data
            if not home_goals or not away_goals:
                continue
            
            match = {
                "date": match_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": int(home_goals),
                "away_goals": int(away_goals),
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
    
    from datetime import datetime
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
    
    from datetime import datetime
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
    
    from datetime import datetime
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years_back * 365)).strftime("%Y-%m-%d")
    
    data = ingestor.get_results("SA", start_date, end_date, limit=500)
    if data:
        ingestor.save_raw(data, "SA", f"{years_back}y")
    return data