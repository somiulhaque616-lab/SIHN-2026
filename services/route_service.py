import math
import streamlit as st
from datetime import datetime
from data.ports import PORTS
from utils.data_status import DataStatus

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance between two points on the Earth surface."""
    R = 6371.0 # Radius of Earth in kilometers
    
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance_km = R * c
    distance_nm = distance_km * 0.539957 # Convert to nautical miles
    return distance_nm

def calculate_route(origin_name: str, dest_name: str, speed_knots: float = 14.0, daily_fuel_mt: float = 35.0):
    """Calculates a route between two ports."""
    if origin_name not in PORTS or dest_name not in PORTS:
        return None
        
    origin = PORTS[origin_name]
    dest = PORTS[dest_name]
    
    # Calculate direct geodesic distance (In reality, ships avoid land, but we use an approximation factor for demo purposes)
    direct_dist_nm = haversine(origin["lat"], origin["lon"], dest["lat"], dest["lon"])
    
    # Apply a "routing factor" to account for landmasses. 1.2 is a naive approximation. 
    # For a real application we would use a maritime routing engine API.
    routing_factor = 1.25 
    adjusted_dist_nm = direct_dist_nm * routing_factor
    
    # Transit time (Days)
    transit_hours = adjusted_dist_nm / speed_knots
    transit_days = transit_hours / 24.0
    
    # Fuel (MT)
    fuel_estimate = transit_days * daily_fuel_mt
    
    # We will generate a simple interpolated line for the map, bowing it slightly
    lats = [origin["lat"]]
    lons = [origin["lon"]]
    
    num_points = 5
    for i in range(1, num_points):
        frac = i / num_points
        lats.append(origin["lat"] + (dest["lat"] - origin["lat"]) * frac)
        lons.append(origin["lon"] + (dest["lon"] - origin["lon"]) * frac)
        
    lats.append(dest["lat"])
    lons.append(dest["lon"])
    
    return {
        "status": DataStatus.MODEL, # Distance calculation is a model approximation here
        "data": {
            "origin": origin_name,
            "destination": dest_name,
            "distance_nm": adjusted_dist_nm,
            "eta_days": transit_days,
            "fuel_mt": fuel_estimate,
            "speed_knots": speed_knots,
            "map_lats": lats,
            "map_lons": lons
        },
        "updated_at": datetime.utcnow(),
        "source": "OptiFreight Routing Engine"
    }
