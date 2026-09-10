import requests
import streamlit as st
from datetime import datetime
from utils.data_status import DataStatus

# Coordinates for major maritime locations
LOCATIONS = {
    "Singapore": {"lat": 1.2903, "lon": 103.852},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Suez": {"lat": 29.9668, "lon": 32.5498},
    "Rotterdam": {"lat": 51.9225, "lon": 4.4792},
    "South China Sea": {"lat": 12.0, "lon": 114.0},
}

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_weather(location_name: str):
    """Fetches real-time weather data from Open-Meteo."""
    if location_name not in LOCATIONS:
        return {"status": DataStatus.ERROR, "data": None, "updated_at": datetime.utcnow(), "source": "Open-Meteo"}

    coords = LOCATIONS[location_name]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true&hourly=temperature_2m,windspeed_10m,winddirection_10m"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        
        # Format the data
        weather_info = {
            "temperature": current.get("temperature"),
            "wind_speed": current.get("windspeed"),
            "wind_direction": current.get("winddirection"),
            "weather_code": current.get("weathercode"),
        }
        
        # Calculate Risk Score
        risk_score, risk_label = calculate_weather_risk(weather_info["wind_speed"])
        weather_info["risk_label"] = risk_label
        
        return {
            "status": DataStatus.LIVE,
            "data": weather_info,
            "updated_at": datetime.utcnow(),
            "source": "Open-Meteo"
        }
    except Exception as e:
        # Fallback if API fails
        return {
            "status": DataStatus.ERROR,
            "data": None,
            "updated_at": datetime.utcnow(),
            "source": "Open-Meteo"
        }

def calculate_weather_risk(wind_speed_kmh):
    """Calculates a simple transparent OptiFreight Weather Risk Score."""
    if wind_speed_kmh is None:
        return 0, "UNKNOWN"
    
    if wind_speed_kmh < 20:
        return 1, "LOW"
    elif wind_speed_kmh < 40:
        return 2, "MODERATE"
    else:
        return 3, "HIGH"
