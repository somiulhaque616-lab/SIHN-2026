import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from utils.data_status import DataStatus

@st.cache_data
def get_freight_data():
    """Returns simulated/demo BDI data with AI Forecast."""
    dates = pd.date_range(start="2026-01-01", periods=100)
    historical_prices = np.linspace(1500, 2000, 100) + np.random.normal(0, 50, 100)
    future_dates = pd.date_range(start=dates[-1] + timedelta(days=1), periods=30)
    forecast_prices = np.linspace(historical_prices[-1], 1700, 30) + np.random.normal(0, 40, 30)
    
    current_rate = historical_prices[-1]
    projected_low = min(forecast_prices)
    projected_high = max(forecast_prices)
    pct_change = ((current_rate - historical_prices[-2]) / historical_prices[-2]) * 100
    low_pct = ((projected_low - current_rate) / current_rate) * 100
    high_pct = ((projected_high - current_rate) / current_rate) * 100

    if projected_low < current_rate:
        recommendation = "WAIT"
        rec_class = "wait"
        confidence = "HIGH"
        movement = f"-{abs(low_pct):.1f}%"
        reason = "Freight rates are projected to drop by ~12% over the next 14 days due to easing port congestion in Singapore. Delay chartering to capture lower rates."
    else:
        recommendation = "CHARTER NOW"
        rec_class = "charter"
        confidence = "HIGH"
        movement = f"+{abs(low_pct):.1f}%"
        reason = "Geopolitical risk metrics indicate imminent rate hikes. Lock in contracts immediately to avoid increased costs."
        
    data = {
        "dates": dates,
        "historical_prices": historical_prices,
        "future_dates": future_dates,
        "forecast_prices": forecast_prices,
        "current_rate": current_rate,
        "projected_low": projected_low,
        "projected_high": projected_high,
        "pct_change": pct_change,
        "low_pct": low_pct,
        "high_pct": high_pct,
        "recommendation": recommendation,
        "rec_class": rec_class,
        "confidence": confidence,
        "movement": movement,
        "reason": reason
    }
    
    # We return the primary status as MODEL/DEMO
    return {
        "status": DataStatus.MODEL,
        "data": data,
        "updated_at": datetime.utcnow(),
        "source": "AI Model (Simulated Data)"
    }

def get_fuel_price():
    """Returns DEMO data for VLSFO fuel price."""
    return {
        "status": DataStatus.DEMO,
        "data": {"price": 610, "unit": "USD/mt", "change": -0.8},
        "updated_at": datetime.utcnow(),
        "source": "Simulated Data"
    }

def get_vessel_intelligence():
    """Returns DEMO data for AIS Vessel tracking."""
    return {
        "status": DataStatus.DEMO,
        "data": {"active_vessels": 412, "critical_alerts": 3},
        "updated_at": datetime.utcnow(),
        "source": "Simulated AIS Data"
    }

