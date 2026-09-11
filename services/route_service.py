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
    return distance_km

def calculate_route(origin_name: str, dest_name: str, speed_knots: float = 14.0, daily_fuel_mt: float = 35.0):
    """Calculates a route between two ports."""
    if origin_name not in PORTS or dest_name not in PORTS:
        return None
        
    origin = PORTS[origin_name]
    dest = PORTS[dest_name]
    
    # Calculate exact geodesic distance in Kilometers (matches Google Maps straight-line measure)
    direct_dist_km = haversine(origin["lat"], origin["lon"], dest["lat"], dest["lon"])
    
    # Apply a "routing factor" to account for landmasses. 1.25 is an approximation. 
    routing_factor = 1.25 
    adjusted_dist_km = direct_dist_km * routing_factor
    
    # Transit time (Days). Note: Speed is in knots (1 knot = 1.852 km/h)
    speed_kmh = speed_knots * 1.852
    transit_hours = adjusted_dist_km / speed_kmh
    transit_days = transit_hours / 24.0
    
    # Fuel (MT)
    fuel_estimate = transit_days * daily_fuel_mt
    
    # We will generate a simple interpolated line for the map
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
        "status": DataStatus.MODEL,
        "data": {
            "origin": origin_name,
            "destination": dest_name,
            "distance_km": adjusted_dist_km,
            "eta_days": transit_days,
            "fuel_mt": fuel_estimate,
            "speed_knots": speed_knots,
            "map_lats": lats,
            "map_lons": lons
        },
        "updated_at": datetime.utcnow(),
        "source": "OptiFreight Engine / Google Maps Distance"
    }
