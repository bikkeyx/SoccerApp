"""Predicted XI module for soccer-prediction-app.

Phase 2: Player Availability and Rotation Intelligence.
Builds a starter-probability model using recent starts, minutes played,
position and tactical role, injury/suspension status, rotation history,
and fixture congestion.
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.players.availability import PlayerAvailability, predict_starting_xi, update_league_availability


class PredictedXI:
    """Generate predicted starting lineups based on availability and form."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.availability = PlayerAvailability(api_key)
        self.form_data: Dict = {}  # Player form tracking
        self.tactical_role: Dict = {}  # Player tactical role
        
        # Standard soccer formation positions
        self.formation = "4-2-3-1"  # Default formation
        self.positions = {
            "GK": ["GK"],  # Goalkeeper
            "DEF": ["CB", "WB"],  # Defenders
            "MID": ["DM", "CM", "AM", "RW", "LW"],  # Midfielders
            "FWD": ["ST"],  # Forward
        }
    
    def set_formation(self, formation: str) -> None:
        """Set the tactical formation."""
        self.formation = formation
        # Validate formation has required positions
        valid_formations = ["4-2-3-1", "4-3-3", "4-4-2", "3-5-2", "3-4-3"]
        if formation not in valid_formations:
            print(f"Formation '{formation}' not in standard set. Using {valid_formations[0]}")
            self.formation = valid_formations[0]
    
    def set_team_squad(self, squad_data: Dict[str, Any]) -> None:
        """Set the team's squad with player information."""
        # Expected squad data structure:
        # {
        #   "players": [
        #     {
        #       "name": "Player Name",
        #       "position": "CB",
        #       "captain": False,
        #       "current_form": 0.8,  # 0-1 scale
        #       "recent_minutes": 270,  # minutes over last 5 games
        #       "injury_status": False,
        #       "suspension_status": False,
        #     },
        #     ...
        #   ]
        # }
        if "players" in squad_data:
            self.form_data = {p["name"]: p for p in squad_data["players"]}
            print(f"Loaded squad with {len(squad_data['players'])} players")
        else:
            print("Squad data missing 'players' key")
    
    def generate_predicted_xi(self, competition: str = "EPL") -> Dict[str, Any]:
        """Generate the predicted starting XI for a team."""
        # First update availability if we have team data
        if self.form_data:
            # Record availability for all squad players
            for player_name, player_data in self.form_data.items():
                self.availability.record_injury(
                    player_name=player_name,
                    team="",  # Will be set from data
                    injury_type="",  # Will be set from data
                    date_received="",  # Will be set from data
                    expected_return="",  # Will be set from data
                    severity="low",  # Default
                    competition_matches=0,
                )
                self.availability.record_suspension(
                    player_name=player_name,
                    team="",
                    reason="",
                    date_start="",
                    date_end="",
                    competition_matches=0,
                )
        
        # Generate start probabilities for all players
        starters = []
        substitutes = []
        
        for player_name, player_data in self.form_data.items():
            position = player_data.get("position", "ST")
            
            prediction = self.availability.predict_start_probability(
                player_name=player_name,
                team=player_data.get("team", ""),
                position=position,
                competition=competition,
            )
            
            player_entry = {
                "name": player_name,
                "position": position,
                "start_probability": prediction["start_probability"],
                "injury_status": prediction["injury_status"],
                "suspension_status": prediction["suspension_status"],
                "recent_minutes": prediction["minutes_played_recent"],
                "form": player_data.get("current_form", 0.5),
            }
            
            if prediction["start_probability"] >= 70.0:
                starters.append(player_entry)
            else:
                substitutes.append(player_entry)
        
        # Sort by start probability (descending)
        starters.sort(key=lambda x: x["start_probability"], reverse=True)
        substitutes.sort(key=lambda x: x["start_probability"], reverse=True)
        
        # Limit to formation-based counts
        xi = self._assemble_xi(starters, substitutes)
        
        return {
            "formation": self.formation,
            "starting_xi": xi["starting_xi"],
            "substitutes": xi["substitutes"],
            "generated_at": datetime.now().isoformat(),
        }
    
    def _assemble_xi(self, starters: List[Dict], substitutes: List[Dict]) -> Dict[str, Any]:
        """Assemble starting XI and substitutes by position."""
        # Position groups for 4-2-3-1 formation
        position_groups = {
            "GK": [],      # 1 goalkeeper
            "DEF": [],     # 4 defenders (2 CB + 2 WB)
            "MID": [],     # 3 midfielders (1 DM + 2 CM/AM)
            "FWD": [],     # 1 striker
        }
        
        # Assign starters to position groups
        for player in starters:
            pos = player["position"]
            if pos == "GK":
                position_groups["GK"].append(player)
            elif pos in ["CB", "WB"]:
                position_groups["DEF"].append(player)
            elif pos in ["DM", "CM"]:
                position_groups["MID"].append(player)
            elif pos in ["AM", "RW", "LW"]:
                position_groups["MID"].append(player)  # AM/RW/LW count as midfield in 4-2-3-1
            elif pos == "ST":
                position_groups["FWD"].append(player)
        
        # Fill remaining spots from substitutes if needed
        # (this handles cases where we don't have enough starters for full formation)
        result_xi = []
        
        # Goalkeeper - must have 1
        if position_groups["GK"]:
            result_xi.append(position_groups["GK"][0])  # Take the highest prob GK
        
        # Defenders - need 4 total (2 CB + 2 WB approx)
        defenders = position_groups["DEF"]
        result_xi.extend(defenders[:4])  # Take up to 4
        
        # Midfielders - need 3 total (1 DM + 2 others)
        mids = position_groups.get("MID", [])
        result_xi.extend(mids[:3])
        
        # Forward - need 1
        forwards = position_groups.get("FWD", [])
        result_xi.extend(forwards[:1])
        
        # If we don't have enough players for full XI, fill from remaining subs
        current_count = len(result_xi)
        needed = 11 - current_count
        
        all_remaining = substitutes + [p for p in starters if p not in result_xi]
        all_remaining.sort(key=lambda x: x["start_probability"], reverse=True)
        
        for i in range(min(needed, len(all_remaining))):
            result_xi.append(all_remaining[i])
        
        # Final sort by position, then by probability
        position_order = {"GK": 0, "CB": 1, "WB": 2, "DM": 3, "CM": 4, "AM": 5, "RW": 6, "LW": 7, "ST": 8}
        result_xi.sort(key=lambda x: (position_order.get(x.get("position", "ST"), 9), -x["start_probability"]))
        
        # Split back into starters and subs for return
        starting_xi = result_xi[:11]
        remaining_subs = result_xi[11:]
        
        return {
            "starting_xi": starting_xi,
            "substitutes": remaining_subs,
        }
    
    def generate_squad_depth_score(self) -> Dict[str, Any]:
        """Calculate squad depth score for each position group."""
        if not self.form_data:
            return {"score": "N/A", "detail": "No squad data loaded"}
        
        position_groups = {
            "GK": [], "CB": [], "WB": [], "DM": [], "CM": [], 
            "AM": [], "RW": [], "LW": [], "ST": []
        }
        
        for player_name, player_data in self.form_data.items():
            position = player_data.get("position", "ST")
            if position in position_groups:
                # Calculate effective strength considering form and availability
                form = player_data.get("current_form", 0.5)
                injury = player_data.get("injury_status", False)
                suspension = player_data.get("suspension_status", False)
                minutes = player_data.get("recent_minutes", 0)
                
                # Availability factor: fully available players get higher score
                avail_factor = 1.0 if not (injury or suspension) else 0.5
                
                # Minutes factor: players with game time are more reliable
                mins_factor = min(minutes / 450, 1.0)  # 450 mins = ~5 full games
                
                effective_strength = form * avail_factor * mins_factor
                
                position_groups[position].append({
                    "name": player_name,
                    "effective_strength": round(effective_strength, 3),
                    "form": round(form, 3),
                    "available": not (injury or suspension),
                    "minutes": minutes,
                })
        
        # Calculate depth score per position (average effective strength)
        scores = {}
        for pos, players in position_groups.items():
            if players:
                avg_strength = sum(p["effective_strength"] for p in players) / len(players)
                scores[pos] = {
                    "average_strength": round(avg_strength, 3),
                    "player_count": len(players),
                    "depth_tier": "Deep" if avg_strength > 0.7 else "Adequate" if avg_strength > 0.4 else "Thin",
                }
            else:
                scores[pos] = {
                    "average_strength": 0.0,
                    "player_count": 0,
                    "depth_tier": "No data",
                }
        
        # Overall squad depth score
        all_players = [p for g in position_groups.values() for p in g]
        if all_players:
            overall = sum(p["effective_strength"] for p in all_players) / len(all_players)
        else:
            overall = 0.0
        
        return {
            "overall_score": round(overall, 3),
            "overall_tier": "Strong" if overall > 0.7 else "Moderate" if overall > 0.4 else "Weak",
            "position_scores": scores,
            "calculated_at": datetime.now().isoformat(),
        }


# Convenience function
def predict_xi(team_squad: Dict[str, Any], formation: str = "4-2-3-1", 
               competition: str = "EPL", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Predict starting XI for a team with given squad."""
    xi_gen = PredictedXI(api_key)
    xi_gen.set_formation(formation)
    xi_gen.set_team_squad(team_squad)
    return xi_gen.generate_predicted_xi(competition)


def assess_squad_depth(team_squad: Dict[str, Any], competition: str = "EPL") -> Dict[str, Any]:
    """Assess squad depth for a team."""
    xi_gen = PredictedXI(api_key=None)
    xi_gen.set_team_squad(team_squad)
    return xi_gen.generate_squad_depth_score()