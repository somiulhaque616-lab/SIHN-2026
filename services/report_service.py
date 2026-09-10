import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_status import DataStatus
from services.demo_services import get_freight_data, get_fuel_price, get_vessel_intelligence
from services.weather_service import get_weather
from services.marine_service import get_marine_conditions
from services.currency_service import get_currency_rate
from services.news_service import get_geopolitical_risk
from services.route_service import calculate_route

def generate_intelligence_report(report_type: str, period: str, custom_range: tuple = None, live_mode: bool = True):
    """
    Collects live & model data from OptiFreight services and generates a structured report payload.
    """
    timestamp = datetime.utcnow()
    
    # 1. Fetch raw data from services
    freight_raw = get_freight_data()
    weather_sg_raw = get_weather("Singapore")
    weather_rot_raw = get_weather("Rotterdam")
    marine_raw = get_marine_conditions("South China Sea")
    currency_raw = get_currency_rate("USD", "INR")
    fuel_raw = get_fuel_price()
    news_raw = get_geopolitical_risk()
    vessel_raw = get_vessel_intelligence()
    route_raw = calculate_route("Shanghai", "Rotterdam")
    
    # Extract data status labels
    freight_data = freight_raw.get("data", {})
    freight_status = freight_raw.get("status", DataStatus.MODEL)
    
    weather_sg = weather_sg_raw.get("data", {})
    weather_sg_status = weather_sg_raw.get("status", DataStatus.ERROR)
    
    marine = marine_raw.get("data", {})
    marine_status = marine_raw.get("status", DataStatus.ERROR)
    
    currency = currency_raw.get("data", {})
    currency_status = currency_raw.get("status", DataStatus.ERROR)
    
    fuel = fuel_raw.get("data", {})
    fuel_status = fuel_raw.get("status", DataStatus.DEMO)
    
    news = news_raw.get("data", {})
    news_status = news_raw.get("status", DataStatus.DEMO)

    # 2. Compute KPIs
    current_rate = freight_data.get("current_rate", 1850.0)
    forecast_30d = freight_data.get("projected_low", 1680.0)
    trend_pct = freight_data.get("pct_change", -2.4)
    charter_rec = freight_data.get("recommendation", "WAIT")
    charter_conf = freight_data.get("confidence", "HIGH")
    charter_reason = freight_data.get("reason", "Rates projected to soften over next 14 days.")
    
    # Route KPIs
    route_dist = route_raw["data"]["distance_nm"] if route_raw else 10500
    route_eta = route_raw["data"]["eta_days"] if route_raw else 31.2
    
    # Port & Route Risk calculation
    marine_risk = marine.get("risk_label", "MODERATE") if marine_status == DataStatus.LIVE else "UNKNOWN"
    geo_risk = news.get("level", "ELEVATED")
    
    # Overall risk level determination
    if geo_risk == "HIGH" or marine_risk == "HIGH":
        overall_risk = "HIGH RISK"
        risk_color = "#ef4444"
    elif geo_risk == "MODERATE" or marine_risk == "MODERATE":
        overall_risk = "MODERATE RISK"
        risk_color = "#f59e0b"
    else:
        overall_risk = "LOW RISK"
        risk_color = "#10b981"

    # Port congestion status
    port_congestion = "MODERATE (36h avg wait)"
    port_status = DataStatus.DEMO

    # Estimated savings per voyage
    estimated_savings = "$142,500" if charter_rec == "WAIT" else "$95,000"

    # 3. Build Dynamic Executive Summary
    exec_summary = build_executive_summary(
        report_type=report_type,
        period=period,
        current_rate=current_rate,
        forecast_30d=forecast_30d,
        trend_pct=trend_pct,
        charter_rec=charter_rec,
        charter_reason=charter_reason,
        overall_risk=overall_risk,
        weather_risk=weather_sg.get("risk_label", "NORMAL") if weather_sg_status == DataStatus.LIVE else "UNAVAILABLE",
        geo_risk=geo_risk,
        estimated_savings=estimated_savings,
        live_mode=live_mode
    )

    # 4. Construct complete report dictionary
    report = {
        "id": f"REP-{int(timestamp.timestamp())}",
        "title": report_type,
        "period": period,
        "custom_range": [str(d) for d in custom_range] if custom_range else None,
        "generated_at": timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "generated_date_display": timestamp.strftime("%d %b %Y %H:%M UTC"),
        "mode": "LIVE DATA MODE" if live_mode else "DEMO MODE",
        "mode_badge": "LIVE" if live_mode else "DEMO",
        "is_demo": not live_mode,
        
        "kpis": {
            "current_freight_rate": {"val": f"${current_rate:,.2f}", "status": freight_status},
            "forecast_30d": {"val": f"${forecast_30d:,.2f}", "status": freight_status},
            "market_trend": {"val": f"{'▲' if trend_pct >= 0 else '▼'} {abs(trend_pct):.1f}%", "status": freight_status, "positive": trend_pct >= 0},
            "route_risk": {"val": overall_risk, "status": DataStatus.MODEL if live_mode else DataStatus.DEMO},
            "port_congestion": {"val": port_congestion, "status": port_status},
            "estimated_savings": {"val": estimated_savings, "status": DataStatus.MODEL}
        },

        "executive_summary": exec_summary,

        "key_intelligence": {
            "freight_market": {
                "current_rate": f"${current_rate:,.2f}",
                "trend": f"{'Increasing' if trend_pct >= 0 else 'Decreasing'} ({trend_pct:+.1f}%)",
                "forecast_30d": f"${forecast_30d:,.2f}",
                "status": freight_status
            },
            "route_intelligence": {
                "recommended_route": "Shanghai → Rotterdam (via Suez)",
                "distance_nm": f"{route_dist:,.0f} NM",
                "transit_time": f"{route_eta:.1f} Days",
                "route_risk": overall_risk,
                "status": DataStatus.MODEL
            },
            "port_intelligence": {
                "congestion_level": "MODERATE",
                "wait_time": "36 Hours Avg",
                "trend": "Improving",
                "status": DataStatus.DEMO
            },
            "weather": {
                "weather_risk": weather_sg.get("risk_label", "NORMAL") if weather_sg_status == DataStatus.LIVE else "DATA UNAVAILABLE",
                "singapore_temp": f"{weather_sg.get('temperature', 'N/A')}°C" if weather_sg_status == DataStatus.LIVE else "DATA UNAVAILABLE",
                "singapore_wind": f"{weather_sg.get('wind_speed', 'N/A')} km/h" if weather_sg_status == DataStatus.LIVE else "DATA UNAVAILABLE",
                "marine_conditions": f"{marine.get('wave_height', 'N/A')}m Waves" if marine_status == DataStatus.LIVE else "DATA UNAVAILABLE",
                "status": weather_sg_status
            },
            "fuel": {
                "vlsfo_price": f"${fuel.get('price', 610)}/{fuel.get('unit', 'USD/mt').split('/')[-1]}",
                "trend": f"{'▼' if fuel.get('change', -0.8) < 0 else '▲'} {abs(fuel.get('change', -0.8))}%",
                "status": fuel_status
            },
            "chartering": {
                "action": charter_rec,
                "confidence": charter_conf,
                "savings": estimated_savings,
                "reason": charter_reason,
                "status": freight_status
            }
        },

        "data_sources": [
            {"name": "Freight Rate Engine", "source": "OptiFreight AI BDI Model", "status": freight_status, "updated": "Just now"},
            {"name": "Meteorological Data", "source": "Open-Meteo API", "status": weather_sg_status, "updated": weather_sg_raw.get("updated_at", timestamp).strftime("%H:%M UTC") if weather_sg_status == DataStatus.LIVE else "Failed"},
            {"name": "Marine & Wave Conditions", "source": "Open-Meteo Marine API", "status": marine_status, "updated": marine_raw.get("updated_at", timestamp).strftime("%H:%M UTC") if marine_status == DataStatus.LIVE else "Failed"},
            {"name": "Currency Exchange", "source": "Frankfurter (ECB API)", "status": currency_status, "updated": currency_raw.get("updated_at", timestamp).strftime("%H:%M UTC") if currency_status == DataStatus.LIVE else "Failed"},
            {"name": "Bunker Fuel Prices", "source": "Global VLSFO Benchmark", "status": fuel_status, "updated": "Daily Reference"},
            {"name": "Geopolitical News Intel", "source": "Maritime Risk Feed", "status": news_status, "updated": "Hourly Scan"},
            {"name": "Port Congestion Index", "source": "AIS Port Tracking", "status": port_status, "updated": "Model Estimate"}
        ],

        "chart_data": {
            "dates": [d.strftime("%Y-%m-%d") for d in freight_data.get("dates", [])],
            "historical_prices": [round(float(x), 2) for x in freight_data.get("historical_prices", [])],
            "future_dates": [d.strftime("%Y-%m-%d") for d in freight_data.get("future_dates", [])],
            "forecast_prices": [round(float(x), 2) for x in freight_data.get("forecast_prices", [])]
        }
    }
    
    return report

def build_executive_summary(report_type, period, current_rate, forecast_30d, trend_pct, charter_rec, charter_reason, overall_risk, weather_risk, geo_risk, estimated_savings, live_mode):
    mode_str = "Live Market Telemetry" if live_mode else "Demo Simulation Models"
    
    summary = {
        "market_outlook": (
            f"During the target evaluation window ({period}), bulk freight markets exhibit "
            f"{'downward pressure' if trend_pct < 0 else 'upward momentum'} with current Baltic Dry Index proxy rates at "
            f"${current_rate:,.2f} ({trend_pct:+.1f}% change). Data synthesized via {mode_str}."
        ),
        "freight_forecast": (
            f"OptiFreight predictive models project 30-day rate movement reaching a benchmark low of ${forecast_30d:,.2f}. "
            f"Model indicators reflect stabilized fleet supply across major Asian shipping corridors."
        ),
        "operational_risk": (
            f"Overall maritime operational risk is assessed as {overall_risk}. "
            f"Meteorological conditions report {weather_risk} risk levels at key transshipment hubs (Singapore/South China Sea), "
            f"while geopolitical risk metrics sit at {geo_risk}."
        ),
        "chartering_recommendation": (
            f"Primary Action: {charter_rec}. {charter_reason}"
        ),
        "potential_opportunity": (
            f"Capitalizing on optimal chartering timing is estimated to yield {estimated_savings} per voyage contract "
            f"under current fuel benchmark assumptions."
        )
    }
    return summary
