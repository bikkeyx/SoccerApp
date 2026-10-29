"""Squad depth module for soccer-prediction-app.

Phase 2: Player Availability and Rotation Intelligence.
Builds squad-depth scores for each position group and rotation risk assessment.
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.players.availability import PlayerAvailability
from src.lineups.predicted_xi import PredictedXI


class SquadDepth:
    """Calculate squad depth and rotation risk for a team."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.availability = PlayerAvailability(api_key)
        self.squad_data: Dict = {}
        self.fixture_congestion: List[Dict] = []
    
    def load_squad(self, squad_data: Dict[str, Any]) -> None:
        """Load squad data with player information."""
        self.squad_data = squad_data
        # Extract player names and positions
        if "players" in squad_data:
            for p in squad_data["players"]:
                # Ensure basic structure
                if "name" not in p:
                    print(f"Warning: Player missing name: {p}")
    
    def assess_rotation_risk(self, upcoming_matches: int = 3) -> Dict[str, Any]:
        """Assess rotation risk based on fixture congestion and minutes played."""
        if not self.squad_data:
            return {"risk": "N/A", "detail": "No squad data loaded"}
        
        # Count players with high minutes load (270+ mins = fatigue risk = 3+ full games)
        high_minutes_players = []
        moderate_minutes_players = []
        fresh_players = []
        
        for player_name, player_data in self.squad_data.get("players", {}).items():
            recent_minutes = player_data.get("recent_minutes", 0)
            
            if recent_minutes >= 270:
                high_minutes_players.append({
                    "name": player_name,
                    "minutes": recent_minutes,
                    "risk": "high_fatigue",
                })
            elif recent_minutes >= 180:
                moderate_minutes_players.append({
                    "name": player_name,
                    "minutes": recent_minutes,
                    "risk": "moderate_fatigue",
                })
            else:
                fresh_players.append({
                    "name": player_name,
                    "minutes": recent_minutes,
                    "risk": "fresh",
                })
        
        # Calculate rotation risk score
        # Risk increases with: more high-minutes players, more upcoming matches, less squad depth
        high_risk_count = len(high_minutes_players)
        total_squad_count = len(self.squad_data.get("players", {}))
        
        if total_squad_count == 0:
            return {"risk": "N/A", "detail": "No squad data"}
        
        # Rotation risk percentage: proportion of squad at fatigue risk
        fatigue_proportion = high_risk_count / total_squad_count
        
        # Adjust based on upcoming fixtures
        fixture_factor = min(upcoming_matches / 5, 1.0)  # 5+ matches = max factor
        
        overall_risk_score = round(min((fatigue_proportion * 0.6 + fixture_factor * 0.4) * 100, 100), 1)
        
        return {
            "overall_risk_score": overall_risk_score,  # 0-100 scale
            "risk_tier": "High" if overall_risk_score > 60 else "Moderate" if overall_risk_score > 30 else "Low",
            "high_fatigue_players": high_minutes_players[:10],  # Top 10
            "moderate_fatigue_players": moderate_minutes_players[:10],
            "fresh_players_available": len(fresh_players),
            "squad_size": total_squad_count,
            "upcoming_matches": upcoming_matches,
            "calculated_at": datetime.now().isoformat(),
        }
    
    def get_rest_days_analysis(self, player_name: str) -> Dict[str, Any]:
        """Analyze rest days for a specific player."""
        player_data = self.squad_data.get("players", {}).get(player_name, {})
        recent_minutes = player_data.get("recent_minutes", 0)
        
        # Estimate rest days based on minutes
        # Rough calculation: ~60 mins per "half-game" of recovery needed
        if recent_minutes == 0:
            rest_status = "fully_rest"
            rest_days_estimate = "—"
        elif recent_minutes <= 90:
            rest_status = "light_minutes"
            rest_days_estimate = "1-2 days"
        elif recent_minutes <= 180:
            rest_status = "moderate_minutes"
            rest_days_estimate = "2-3 days"
        elif recent_minutes <= 270:
            rest_status = "high_minutes"
            rest_days_estimate = "3-4 days"
        else:
            rest_status = "very_high_minutes"
            rest_days_estimate = "5+ days"
        
        return {
            "player_name": player_name,
            "recent_minutes": recent_minutes,
            "rest_status": rest_status,
            "rest_days_estimate": rest_days_estimate,
            "recommendation": self._get_rest_recommendation(rest_status),
        }
    
    def _get_rest_recommendation(self, rest_status: str) -> str:
        """Get rest recommendation based on status."""
        recs = {
            "fully_rest": "Player can start next match without concern",
            "light_minutes": "Player should be fine for full start",
            "moderate_minutes": "Consider rotating or monitoring closely",
            "high_minutes": "Rotate if possible; monitor fitness",
            "very_high_minutes": "Definitely rotate; high injury risk",
        }
        return recs.get(rest_status, "Monitor")
    
    def save_depth_chart(self, filepath: str) -> Path:
        """Save squad depth analysis to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        analysis = self.assess_rotation_risk()
        analysis["squad_size"] = len(self.squad_data.get("players", {}))
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Saved depth chart to {path}")
        return path
    
    def load_depth_chart(self, filepath: str) -> None:
        """Load depth chart from disk."""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Could restore state here
            print(f"Loaded depth chart from {path}")
        else:
            print(f"Depth chart not found: {path}")


# Convenience functions
def assess_team_rotation_risk(squad_data: Dict[str, Any], 
                               upcoming_matches: int = 3) -> Dict[str, Any]:
    """Quick rotation risk assessment for a team squad."""
    sq = SquadDepth(api_key=None)
    sq.load_squad(squad_data)
    return sq.assess_rotation_risk(upcoming_matches)


def get_player_rest_analysis(squad_data: Dict[str, Any], player_name: str) -> Dict[str, Any]:
    """Get rest/ fatigue analysis for a specific player."""
    sq = SquadDepth(api_key=None)
    sq.load_squad(squad_data)
    return sq.get_rest_days_analysis(player_name)