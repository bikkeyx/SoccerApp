"""Prediction engine for soccer-prediction-app.

Phase 5: Prediction Engine
Produces calibrated, explainable soccer match predictions using statistical
and machine learning models with backtesting and verification.
"""

import sys
import math
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.context import (
    WeatherData, haversine_distance_km, calculate_rest_days,
    VenueEffects, MotivationContext, analyze_context,
    STADIUM_DATABASE
)
from src.events.analytics import EventAnalytics