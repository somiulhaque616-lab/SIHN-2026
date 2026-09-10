import requests
import streamlit as st
from datetime import datetime
from utils.data_status import DataStatus

@st.cache_data(ttl=1800) # Cache for 30 minutes
def get_currency_rate(base="USD", target="INR"):
    """Fetches currency exchange rates from Frankfurter API."""
    url = f"https://api.frankfurter.dev/v2/rate/{base}/{target}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        rate = data.get("rate")
        if rate:
            return {
                "status": DataStatus.LIVE,
                "data": {"rate": rate, "base": base, "target": target},
                "updated_at": datetime.utcnow(),
                "source": "Frankfurter (ECB)"
            }
        else:
            raise ValueError("Rate not found")
            
    except Exception as e:
        # Fallback if API fails
        return {
            "status": DataStatus.ERROR,
            "data": None,
            "updated_at": datetime.utcnow(),
            "source": "Frankfurter (ECB)"
        }
