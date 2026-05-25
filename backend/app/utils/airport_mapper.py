import math
from typing import Tuple, Optional
from app.core.constants import AIRPORT_COORDINATES

def get_airport_coordinates(code: str) -> Optional[Tuple[float, float]]:
    """Get latitude and longitude of airport from database."""
    if not code:
        return None
    code_clean = code.strip().upper()
    return AIRPORT_COORDINATES.get(code_clean)

def calculate_distance(origin: str, destination: str) -> Optional[float]:
    """
    Calculates distance (in km) between two airport codes using Haversine formula.
    Returns None if any airport is invalid.
    """
    coord1 = get_airport_coordinates(origin)
    coord2 = get_airport_coordinates(destination)
    
    if not coord1 or not coord2:
        return None
        
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Haversine formula
    R = 6371.0  # Earth's radius in km
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
         
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c
