import requests
import streamlit as st
from datetime import datetime
from utils.data_status import DataStatus

# Coordinates for major marine locations
MARINE_LOCATIONS = {
    "South China Sea": {"lat": 12.0, "lon": 114.0},
    "Suez Canal Approach": {"lat": 29.9668, "lon": 32.5498},
    "Strait of Malacca": {"lat": 4.0, "lon": 100.0},
    "English Channel": {"lat": 50.0, "lon": -1.0},
}

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_marine_conditions(location_name: str):
    """Fetches real-time marine data from Open-Meteo Marine API."""
    if location_name not in MARINE_LOCATIONS:
        return {"status": DataStatus.ERROR, "data": None, "updated_at": datetime.utcnow(), "source": "Open-Meteo Marine"}

    coords = MARINE_LOCATIONS[location_name]
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={coords['lat']}&longitude={coords['lon']}&current=wave_height,wave_direction,wave_period"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        
        # Format the data
        marine_info = {
            "wave_height": current.get("wave_height"),
            "wave_direction": current.get("wave_direction"),
            "wave_period": current.get("wave_period"),
        }
        
        # Calculate Risk Score based on wave height
        risk_score, risk_label = calculate_marine_risk(marine_info["wave_height"])
        marine_info["risk_label"] = risk_label
        
        return {
            "status": DataStatus.LIVE,
            "data": marine_info,
            "updated_at": datetime.utcnow(),
            "source": "Open-Meteo Marine"
        }
    except Exception as e:
        # Fallback if API fails
        return {
            "status": DataStatus.ERROR,
            "data": None,
            "updated_at": datetime.utcnow(),
            "source": "Open-Meteo Marine"
        }

def calculate_marine_risk(wave_height_m):
    """Calculates a simple marine risk score based on wave height."""
    if wave_height_m is None:
        return 0, "UNKNOWN"
    
    if wave_height_m < 2.0:
        return 1, "LOW"
    elif wave_height_m < 4.0:
        return 2, "MODERATE"
    else:
        return 3, "HIGH"
