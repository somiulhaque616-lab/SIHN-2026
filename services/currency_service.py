import requests
import streamlit as st
from datetime import datetime
from utils.data_status import DataStatus

@st.cache_data(ttl=1800) # Cache for 30 minutes
def get_currency_rate(base="USD", target="INR"):
    """Fetches real-time mid-market currency exchange rates from Wise.com."""
    url = f"https://wise.com/rates/history+live?source={base}&target={target}&length=1&resolution=hourly&unit=day"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            rate = data[-1].get("value")
            return {
                "status": DataStatus.LIVE,
                "data": {"rate": rate, "base": base, "target": target},
                "updated_at": datetime.utcnow(),
                "source": "Wise (Mid-Market)"
            }
        else:
            raise ValueError("Rate data array is empty")
            
    except Exception as e:
        # Fallback if API fails
        return {
            "status": DataStatus.ERROR,
            "data": None,
            "updated_at": datetime.utcnow(),
            "source": "Wise (Mid-Market)"
        }
