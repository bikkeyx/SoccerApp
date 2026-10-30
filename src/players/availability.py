"""Player availability module for soccer-prediction-app.

Phase 2: Player Availability and Rotation Intelligence.
Estimates player availability, likely starters, squad depth, and performance impact of absences.

Uses permanently free sources:
- football-data.org free tier (lineups sometimes included)
- API-Football free tier (limited lineup data)
- Transfermarkt (free squad data)
- FBref (player minutes, stats)
- Premier Injuries (free injury data)
- Club websites (free lineup announcements)
- National federation sites (free)
- Wikipedia (supplemental historical)
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import json
from datetime import datetime


class PlayerAvailability:
    """Track player availability, injuries, suspensions, and lineup probability."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4"
        self.session = requests.Session()
        self.use_free_alt = api_key is None
        
        # In-memory data stores
        self.injuries: Dict = {}
        self.suspensions: Dict = {}
        self.lineups: Dict = {}
        self.player_minutes: Dict = {}  # player -> recent minutes played
    
    def update_injuries(self, league: str = "EPL") -> Dict[str, Any]:
        """Update injury data for a league from free sources."""
        # Try football-data.org (lineups sometimes include injury status)
        if self.api_key:
            return self._fetch_from_football_data(league)
        
        # Fall back to free alternative sources
        return self._fetch_from_free_sources(league)
    
    def _fetch_from_football_data(self, league: str) -> Dict[str, Any]:
        """Fetch injury/lineup data from football-data.org."""
        # football-data.org free tier may include some lineup info
        # This is a placeholder - actual implementation depends on API capabilities
        return {"injuries": [], "source": "football-data.org", "note": "lineup data may be partial"}
    
    def _fetch_from_free_sources(self, league: str) -> Dict[str, Any]:
        """Fetch from free alternative injury/suspension sources."""
        # Free sources for injury data:
        # - Premier Injuries (premierinjuries.com) - free
        # - PhysioRoom (physioroom.com) - free
        # - Club websites - free
        # - National federation sites - free
        # - Wikipedia - supplemental historical
        
        # Placeholder data structure
        return {
            "injuries": [],
            "suspensions": [], 
            "source": "free alternative sources",
            "note": "To be populated from Premier Injuries, PhysioRoom, club websites"
        }
    
    def update_suspensions(self, league: str = "EPL") -> Dict[str, Any]:
        """Update suspension data for a league."""
        # yellow card accumulation leads to suspensions
        # Free sources: football-data.org, national federation cards data
        
        if self.api_key:
            return self._fetch_suspensions_from_data(league)
        
        return self._fetch_suspensions_free(league)
    
    def _fetch_suspensions_from_data(self, league: str) -> Dict[str, Any]:
        """Fetch suspensions from football-data.org API data."""
        return {"suspensions": [], "source": "football-data.org", "note": "suspension data limited in free tier"}
    
    def _fetch_suspensions_free(self, league: str) -> Dict[str, Any]:
        """Fetch suspensions from free sources."""
        # Accumulation of yellow cards: typically 5 yellows = 1 match ban
        # Sources: match reports, federation records, free CSS data
        return {
            "suspensions": [],
            "source": "free card accumulation tracking",
            "note": "Yellow card data from FBref, transfermarkt (free tier)"
        }
    
    def record_injury(self, 
                      player_name: str, 
                      team: str, 
                      injury_type: str,
                      date_received: str,
                      expected_return: str,
                      severity: str = "medium",
                      competition_matches: int = 0) -> Dict[str, Any]:
        """Record a new injury entry."""
        injury_entry = {
            "player_name": player_name,
            "team": team,
            "injury_type": injury_type,
            "date_received": date_received,
            "expected_return": expected_return,
            "severity": severity,  # minor, medium, major, long-term
            "competition_misses": competition_matches,
            "date_created": datetime.now().isoformat(),
            "recurrence_risk": self._calculate_recurrence_risk(severity),
            "minutes_restriction": self._calculate_minutes_restriction(severity),
        }
        
        if league not in self.injuries:
            self.injuries[league] = []
        self.injuries[league].append(injury_entry)
        
        return injury_entry
    
    def record_suspension(self, 
                          player_name: str, 
                          team: str, 
                          reason: str,
                          date_start: str,
                          date_end: str,
                          competition_matches: int = 0) -> Dict[str, Any]:
        """Record a new suspension entry."""
        suspension_entry = {
            "player_name": player_name,
            "team": team,
            "reason": reason,  # yellow card accumulation, red card, etc.
            "date_start": date_start,
            "date_end": date_end,
            "competition_misses": competition_matches,
            "date_created": datetime.now().isoformat(),
        }
        
        if league not in self.suspensions:
            self.suspensions[league] = []
        self.suspensions[league].append(suspension_entry)
        
        return suspension_entry
    
    def predict_start_probability(self, 
                                  player_name: str, 
                                  team: str, 
                                  position: str,
                                  competition: str) -> Dict[str, Any]:
        """Predict probability of player starting the next match."""
        
        # Model factors (from plan.md):
        # - Recent starts
        # - Minutes played
        # - Position and tactical role
        # - Injury/suspension status
        # - Rotation history
        # - Fixture congestion
        
        # Get current availability status
        injury_status = self._check_injury_status(player_name, team)
        suspension_status = self._check_suspension_status(player_name, team)
        
        # Base probability based on position and typical usage
        base_probability = self._position_base_probability(position)
        
        # Adjust for injuries
        injury_penalty = 0.0
        if injury_status.get("is_injured"):
            injury_penalty = self._injury_penalty(injury_status)
        
        # Adjust for suspensions
        suspension_penalty = 0.0
        if suspension_status.get("is_suspended"):
            suspension_penalty = 1.0  # Automatic suspension = 0% start probability
        
        # Adjust for minutes load (fatigue)
        minutes_adjustment = self._minutes_adjustment(player_name)
        
        # Calculate final probability
        final_prob = max(0.0, min(1.0, base_probability - injury_penalty - suspension_penalty + minutes_adjustment))
        
        return {
            "player_name": player_name,
            "position": position,
            "team": team,
            "competition": competition,
            "start_probability": round(final_prob * 100, 1),
            "injury_status": injury_status,
            "suspension_status": suspension_status,
            "minutes_played_recent": self._get_recent_minutes(player_name),
            "factors": {
                "base_probability": round(base_probability * 100, 1),
                "injury_penalty": round(injury_penalty * 100, 1),
                "suspension_penalty": round(suspension_penalty * 100, 1),
                "fatigue_adjustment": round(minutes_adjustment * 100, 1),
            }
        }
    
    def _position_base_probability(self, position: str) -> float:
        """Base start probability by position."""
        position_probs = {
            "GK": 0.95,      # Goalkeepers almost always start
            "CB": 0.80,      # Center backs typically 80%
            "WB": 0.75,      # Wing backs typically 75%
            "DM": 0.70,      # Defensive mids typically 70%
            "CM": 0.75,      # Central mids typically 75%
            "AM": 0.65,      # Attacking mids typically 65%
            "RW": 0.70,      # Right wingers typically 70%
            "LW": 0.70,      # Left wingers typically 70%
            "ST": 0.80,      # Strikers typically 80%
        }
        return position_probs.get(position, 0.50)  # Default 50% unknown positions
    
    def _check_injury_status(self, player_name: str, team: str) -> Dict[str, Any]:
        """Check if player is currently injured."""
        # Search through recorded injuries
        for league, injuries in self.injuries.items():
            for inj in injuries:
                if inj.get("player_name") == player_name and inj.get("team") == team:
                    # Check if injury period includes today
                    date_received = inj.get("date_received")
                    expected_return = inj.get("expected_return")
                    
                    if date_received and expected_return:
                        try:
                            today = datetime.now().strftime("%Y-%m-%d")
                            # Parse dates and check if today is within injury period
                            from datetime import datetime as dt
                            rec_date = dt.strptime(date_received, "%Y-%m-%d") if isinstance(date_received, str) else date_received
                            ret_date = dt.strptime(expected_return, "%Y-%m-%d") if isinstance(expected_return, str) else expected_return
                            today_date = dt.strptime(today, "%Y-%m-%d")
                            
                            is_injured = rec_date <= today_date <= ret_date
                            
                            return {
                                "is_injured": is_injured,
                                "injury_type": inj.get("injury_type"),
                                "severity": inj.get("severity"),
                                "expected_return": expected_return,
                                "days_since_injury": (today_date - rec_date).days if is_injured else 0,
                                "days_until_return": (ret_date - today_date).days if is_injured else 0,
                            }
                        except:
                            pass
                    
                    # If no dates, assume injured if severity is medium+
                    severity = inj.get("severity", "low")
                    return {
                        "is_injured": severity in ["medium", "major", "long-term"],
                        "injury_type": inj.get("injury_type"),
                        "severity": severity,
                    }
        
        return {"is_injured": False}
    
    def _check_suspension_status(self, player_name: str, team: str) -> Dict[str, Any]:
        """Check if player is currently suspended."""
        for league, suspensions in self.suspensions.items():
            for susp in suspensions:
                if susp.get("player_name") == player_name and susp.get("team") == team:
                    date_start = susp.get("date_start")
                    date_end = susp.get("date_end")
                    
                    if date_start and date_end:
                        from datetime import datetime as dt
                        try:
                            today = dt.now().strftime("%Y-%m-%d")
                            start_date = dt.strptime(date_start, "%Y-%m-%d")
                            end_date = dt.strptime(date_end, "%Y-%m-%d")
                            today_date = dt.now()
                            
                            is_suspended = start_date <= today_date <= end_date
                            
                            return {
                                "is_suspended": is_suspended,
                                "reason": susp.get("reason"),
                                "days_missing": self._calculate_missing_days(start_date, end_date),
                            }
                        except:
                            pass
                    
                    # If no dates, assume suspended
                    return {"is_suspended": True, "reason": susp.get("reason")}
        
        return {"is_suspended": False}
    
    def _calculate_recurrence_risk(self, severity: str) -> str:
        """Calculate injury recurrence risk."""
        risk_map = {
            "minor": "low",
            "medium": "moderate", 
            "major": "high",
            "long-term": "very high",
        }
        return risk_map.get(severity, "unknown")
    
    def _calculate_minutes_restriction(self, severity: str) -> int:
        """Calculate minutes restriction based on severity."""
        restriction_map = {
            "minor": 0,       # Full fitness
            "medium": 60,     # Partial fitness, 60 min cap
            "major": 45,      # Limited minutes, 45 min cap
            "long-term": 0,   # TBD - being rebuilt
        }
        return restriction_map.get(severity, 0)
    
    def _minutes_adjustment(self, player_name: str) -> float:
        """Adjust start probability based on recent minutes load."""
        # Get recent minutes for player
        recent_minutes = self.player_minutes.get(player_name, 0)
        
        # If player has played full 90+ minutes in multiple recent games, fatigue penalty
        if recent_minutes > 270:  # >3 games of 90 mins
            return -0.15  # 15% penalty
        elif recent_minutes > 180:  # ~2 games of 90 mins
            return -0.10  # 10% penalty
        elif recent_minutes > 90:   # 1 game of 90 mins
            return -0.05  # 5% penalty
        return 0.0
    
    def _get_recent_minutes(self, player_name: str) -> int:
        """Get recent minutes played by player."""
        return self.player_minutes.get(player_name, 0)
    
    def _calculate_missing_days(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate days missed due to suspension."""
        return (end_date - start_date).days
    
    def save_state(self, filepath: str) -> Path:
        """Save availability state to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "injuries": self.injuries,
            "suspensions": self.suspensions,
            "player_minutes": self.player_minutes,
            "saved_at": datetime.now().isoformat(),
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)
        
        print(f"Saved availability state to {path}")
        return path
    
    def load_state(self, filepath: str) -> None:
        """Load availability state from disk."""
        path = Path(filepath)
        
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.injuries = state.get("injuries", {})
            self.suspensions = state.get("suspensions", {})
            self.player_minutes = state.get("player_minutes", {})
            
            print(f"Loaded availability state from {path}")
        else:
            print(f"State file not found: {path}")


# Convenience functions
def update_league_availability(league: str = "EPL", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Update availability data for entire league."""
    availability = PlayerAvailability(api_key)
    injuries = availability.update_injuries(league)
    suspensions = availability.update_suspensions(league)
    
    return {
        "league": league,
        "injuries": injuries,
        "suspensions": suspensions,
        "updated_at": datetime.now().isoformat(),
    }


def predict_starting_xi(team: str, position: str, competition: str, 
                        api_key: Optional[str] = None) -> Dict[str, Any]:
    """Predict whether a player will start the next match."""
    availability = PlayerAvailability(api_key)
    prediction = availability.predict_start_probability(
        player_name="",  # Will be filled in UI
        team=team,
        position=position,
        competition=competition,
    )
    return prediction