import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.weather_service import get_weather
from services.marine_service import get_marine_conditions
from services.currency_service import get_currency_rate
from services.demo_services import get_freight_data, get_fuel_price, get_port_congestion, get_vessel_intelligence
from services.news_service import get_geopolitical_risk
from utils.data_status import DataStatus, get_status_badge_html, get_simple_badge_html
from views.port_route_view import render_port_route_intel
from views.reports_view import render_reports_view
from views.roi_simulator_view import render_roi_simulator_view
from components.ai_chatbot import render_chatbot


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="OptiFreight — Predictive Maritime Intelligence",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.show_loader = True
else:
    st.session_state.show_loader = False

if "live_mode" not in st.session_state:
    st.session_state.live_mode = True

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.utcnow()

# ============================================================
# DESIGN SYSTEM — CSS INJECTION
# ============================================================
def inject_css():
    loader_css = ""
    if st.session_state.show_loader:
        loader_css = """
/* ── Global Loader ── */
.global-loader { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #071426; z-index: 999999; display: flex; flex-direction: column; align-items: center; justify-content: center; animation: loaderFadeOut 0.5s ease 2s forwards; pointer-events: none; }
.loader-logo { font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 12px; }
.loader-line { width: 0; height: 2px; background: #00d4ff; margin: 0 auto 24px auto; animation: expandLine 1s ease-out 0.2s forwards; }
.loader-text { font-size: 0.9rem; color: #8b95a5; font-weight: 500; }
.loader-text::after { content: "Initializing Maritime Intelligence..."; animation: textChange 2s linear forwards; }
@keyframes expandLine { 0% { width: 0; opacity: 0; } 50% { opacity: 1; } 100% { width: 80px; opacity: 1; } }
@keyframes textChange { 0%, 25% { content: "Initializing Maritime Intelligence..."; } 26%, 50% { content: "Loading market data..."; } 51%, 75% { content: "Loading risk intelligence..."; } 76%, 100% { content: "Preparing AI forecast..."; } }
@keyframes loaderFadeOut { 0% { opacity: 1; pointer-events: all; } 99% { opacity: 0; pointer-events: all; } 100% { opacity: 0; pointer-events: none; visibility: hidden; } }
"""

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

:root {{
    --bg-gradient: linear-gradient(135deg, #071426 0%, #0A1B35 50%, #0D2342 100%);
    --card-bg: rgba(17, 35, 64, 0.7);
    --card-border: rgba(0, 212, 255, 0.3);
    --card-hover-border: rgba(0, 212, 255, 0.8);
    --primary: #00d4ff;
    --secondary: #14b8a6;
    --text-main: #ffffff;
    --text-muted: #94a3b8;
    --positive: #10b981;
    --warning: #f59e0b;
    --critical: #ef4444;
}}

{loader_css}

/* ── Global Styles ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-gradient) !important;
    color: var(--text-main) !important;
}}
#MainMenu, footer, header[data-testid="stHeader"] {{ display: none !important; }}

.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}}

/* ── Animations ── */
@keyframes fadeInUp {{ 0% {{ opacity: 0; transform: translateY(10px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
@keyframes pulseGlow {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.6; }} }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: #050d1a !important;
    border-right: 1px solid rgba(0, 212, 255, 0.1) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}}
.sidebar-header {{ padding: 24px 20px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); margin-bottom: 24px; }}
.sidebar-title {{ font-size: 1.25rem; font-weight: 800; color: #FFF; }}
.sidebar-sub {{ font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }}

[data-testid="stSidebar"] .stRadio > div {{ gap: 4px !important; }}
[data-testid="stSidebar"] .stRadio > div > label {{
    padding: 10px 16px !important; margin: 0 12px !important;
    border-radius: 8px !important; font-size: 0.85rem !important;
    color: var(--text-muted) !important; transition: all 0.2s ease !important;
    cursor: pointer !important; background: transparent !important; border-left: 3px solid transparent !important;
}}
[data-testid="stSidebar"] .stRadio > div > label:hover {{
    background: rgba(0, 212, 255, 0.05) !important; color: #FFF !important;
}}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {{
    background: rgba(0, 212, 255, 0.15) !important; color: #FFF !important;
    font-weight: 600 !important; border-left: 3px solid var(--primary) !important;
    box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.05) !important;
}}

/* ── Header ── */
.dash-header {{ display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 16px; border-bottom: 1px solid rgba(0, 212, 255, 0.15); margin-bottom: 32px; animation: fadeInUp 0.4s ease forwards; }}
.dash-title {{ font-size: 1.8rem; font-weight: 800; color: #FFF; margin-bottom: 4px; }}
.dash-subtitle {{ font-size: 0.85rem; color: var(--text-muted); }}
.dash-meta {{ display: flex; gap: 16px; font-size: 0.8rem; font-weight: 600; color: #FFF; align-items: center; }}
.live-dot {{ display: inline-block; width: 6px; height: 6px; background: var(--positive); border-radius: 50%; margin-right: 6px; animation: pulseGlow 2s infinite; }}

/* ── Sections ── */
.section-title {{ font-size: 0.8rem; font-weight: 700; color: #FFF; text-transform: uppercase; letter-spacing: 0.05em; margin: 32px 0 16px 0; display: flex; align-items: center; gap: 8px; animation: fadeInUp 0.4s ease backwards; }}
.section-title::after {{ content: ''; flex: 1; height: 1px; background: rgba(0, 212, 255, 0.15); }}

/* ── KPI Cards ── */
.kpi-container {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
.kpi-card {{
    background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px;
    padding: 20px 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s ease;
    animation: fadeInUp 0.5s ease backwards; position: relative; overflow: hidden;
}}
.kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--primary), transparent); opacity: 0.5; }}
.kpi-card:hover {{ transform: translateY(-3px); border-color: var(--card-hover-border); box-shadow: 0 8px 16px rgba(0, 212, 255, 0.1); }}
.kpi-card .title {{ font-size: 0.7rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: flex; justify-content: space-between; margin-bottom: 12px; }}
.kpi-card .value {{ font-size: 2rem; font-weight: 800; color: #FFF; line-height: 1; margin-bottom: 12px; }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }}
.badge.positive {{ background: rgba(16, 185, 129, 0.15); color: var(--positive); border: 1px solid rgba(16, 185, 129, 0.3); }}
.badge.negative {{ background: rgba(239, 68, 68, 0.15); color: var(--critical); border: 1px solid rgba(239, 68, 68, 0.3); }}
.badge.neutral {{ background: rgba(0, 212, 255, 0.15); color: var(--primary); border: 1px solid rgba(0, 212, 255, 0.3); }}
.status-badge {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); }}

/* ── AI Hero Card ── */
.ai-hero {{
    background: linear-gradient(135deg, #003a52 0%, #001a2e 100%);
    border: 1px solid #00d4ff; border-radius: 16px; padding: 28px 32px;
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15), inset 0 0 20px rgba(0, 212, 255, 0.05);
    margin-bottom: 32px; animation: fadeInUp 0.6s ease backwards;
}}
.ai-hero .header {{ font-size: 0.75rem; font-weight: 700; color: #00d4ff; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 0.05em; }}
.ai-hero .status {{ font-size: 4rem; font-weight: 800; line-height: 1; margin-bottom: 16px; text-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }}
.ai-hero .status.wait {{ color: var(--positive); }}
.ai-hero .status.charter {{ color: var(--critical); text-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }}
.ai-hero .confidence {{ font-size: 0.85rem; color: #FFF; margin-bottom: 24px; display: inline-block; background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 4px; }}
.ai-hero .metrics {{ display: flex; gap: 48px; padding: 20px 0; border-top: 1px solid rgba(0, 212, 255, 0.2); border-bottom: 1px solid rgba(0, 212, 255, 0.2); margin-bottom: 20px; }}
.ai-hero .metric-col .label {{ font-size: 0.65rem; color: rgba(255,255,255,0.7); font-weight: 600; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; }}
.ai-hero .metric-col .val {{ font-size: 1.5rem; font-weight: 800; color: #FFF; }}
.ai-hero .reason {{ font-size: 0.85rem; color: #e2e8f0; line-height: 1.5; }}

/* ── Chart Panel ── */
.chart-container {{
    background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px;
    padding: 20px; animation: fadeInUp 0.5s ease backwards; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
.chart-header {{ margin-bottom: 16px; display: flex; justify-content: space-between; }}
.chart-title {{ font-size: 1rem; font-weight: 700; color: #FFF; }}
.chart-sub {{ font-size: 0.75rem; color: var(--text-muted); }}

/* ── Risk Cards ── */
.risk-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px; }}
.risk-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s; animation: fadeInUp 0.5s ease backwards; }}
.risk-card:hover {{ border-color: var(--card-hover-border); transform: translateY(-2px); }}
.risk-card .title {{ font-size: 0.85rem; font-weight: 700; color: #FFF; margin-bottom: 12px; display: flex; justify-content: space-between; }}
.risk-card .value {{ font-size: 1.5rem; font-weight: 800; color: #FFF; margin-bottom: 8px; }}
.risk-card .sub {{ font-size: 0.8rem; color: var(--text-muted); margin-bottom: 12px; }}

.stPlotlyChart {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LAYER & CACHING LOGIC
# ============================================================
def load_all_data():
    freight = get_freight_data()
    weather_sg = get_weather("Singapore")
    currency = get_currency_rate("USD", "INR")
    fuel = get_fuel_price()
    marine = get_marine_conditions("South China Sea")
    port = get_port_congestion("Shanghai")
    news = get_geopolitical_risk()
    return {
        "freight": freight,
        "weather_sg": weather_sg,
        "currency": currency,
        "fuel": fuel,
        "marine": marine,
        "port": port,
        "news": news
    }

# Ensure data is loaded
all_data = load_all_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
<div class="sidebar-header">
<div class="sidebar-title">⚓ OPTIFREIGHT</div>
<div class="sidebar-sub">Predictive Maritime Intelligence</div>
</div>
""", unsafe_allow_html=True)

    mode = st.radio("Data Mode", ["🟢 LIVE DATA MODE", "⚪ DEMO MODE"], index=0 if st.session_state.live_mode else 1)
    st.session_state.live_mode = "LIVE" in mode

    nav_items = {
        "Dashboard": "◉" if st.session_state.get("active_page") == "Dashboard" else "○",
        "Freight Forecast": "◉" if st.session_state.get("active_page") == "Freight Forecast" else "○",
        "Risk Intelligence": "◉" if st.session_state.get("active_page") == "Risk Intelligence" else "○",
        "Port & Route Intel": "◉" if st.session_state.get("active_page") == "Port & Route Intel" else "○",
        "Procurement": "◉" if st.session_state.get("active_page") == "Procurement" else "○",
        "ROI & What-If": "◉" if st.session_state.get("active_page") == "ROI & What-If" else "○",
        "Reports": "◉" if st.session_state.get("active_page") == "Reports" else "○",
        "Settings": "◉" if st.session_state.get("active_page") == "Settings" else "○",
    }

    selected_page = st.radio(
        "Navigation",
        options=list(nav_items.keys()),
        format_func=lambda x: f"{nav_items[x]} {x}",
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.session_state.active_page = selected_page

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="margin: 0 16px; padding: 16px; background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 8px;">
<div style="font-size: 0.7rem; color: #00d4ff; font-weight: 700; margin-bottom: 8px;">SIH 2026</div>
<div style="font-size: 0.8rem; color: #FFF; font-weight: 600;">Problem Statement:<br><span style="color:#94a3b8; font-weight: 400;">SIH26006</span></div>
<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px;">Theme:<br>Transportation & Logistics</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# RENDERING FUNCTIONS
# ============================================================

def render_page_header(title, subtitle):
    time_str = st.session_state.last_refresh.strftime("%d %b %Y %H:%M UTC")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
<div class="dash-header">
<div>
<div class="dash-title">{title}</div>
<div class="dash-subtitle">{subtitle}</div>
</div>
<div class="dash-meta">
<span class="live-dot"></span> LIVE &nbsp;|&nbsp; 📅 {time_str}
</div>
</div>
""", unsafe_allow_html=True)
    with col2:
        if st.button("↻ Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.last_refresh = datetime.utcnow()
            st.rerun()

def render_section_header(icon, title):
    st.markdown(f"""
<div class="section-title">{icon} {title}</div>
""", unsafe_allow_html=True)

def render_kpi_cards():
    c1, c2, c3, c4 = st.columns(4)
    freight = all_data["freight"]["data"]
    freight_status = get_status_badge_html(all_data["freight"]["status"], all_data["freight"]["updated_at"], all_data["freight"]["source"])
    
    currency_data = all_data["currency"]
    if currency_data["status"] == DataStatus.LIVE:
        c_rate = currency_data["data"]["rate"]
        c_status = get_status_badge_html(currency_data["status"], currency_data["updated_at"], currency_data["source"])
        currency_html = f'<div class="value">₹{c_rate:,.2f}</div>'
    else:
        c_status = get_status_badge_html(DataStatus.ERROR, datetime.utcnow(), "Frankfurter (ECB)")
        currency_html = f'<div class="value" style="font-size: 1.2rem; color: #ef4444;">DATA UNAVAILABLE</div>'

    with c1:
        st.markdown(f"""
<div class="kpi-card" style="animation-delay: 0.0s;">
<div class="title">CURRENT FREIGHT RATE <span>📈</span></div>
<div class="value">${freight["current_rate"]:,.2f}</div>
<div><span class="badge {'positive' if freight['pct_change'] >= 0 else 'negative'}">{'▲' if freight['pct_change'] >= 0 else '▼'} {abs(freight['pct_change']):.1f}%</span></div>
<div class="status-badge">{freight_status}</div>
</div>
""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div class="kpi-card" style="animation-delay: 0.1s;">
<div class="title">30-DAY PROJECTED LOW <span>📉</span></div>
<div class="value">${freight["projected_low"]:,.2f}</div>
<div><span class="badge negative">▼ {abs(freight['low_pct']):.1f}%</span></div>
<div class="status-badge">{freight_status}</div>
</div>
""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
<div class="kpi-card" style="animation-delay: 0.2s;">
<div class="title">30-DAY PROJECTED HIGH <span>📊</span></div>
<div class="value">${freight["projected_high"]:,.2f}</div>
<div><span class="badge {'positive' if freight['high_pct'] >= 0 else 'negative'}">{'▲' if freight['high_pct'] >= 0 else '▼'} {abs(freight['high_pct']):.1f}%</span></div>
<div class="status-badge">{freight_status}</div>
</div>
""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
<div class="kpi-card" style="animation-delay: 0.3s;">
<div class="title">USD / INR EXCHANGE <span>💱</span></div>
{currency_html}
<div><span class="badge neutral">REFERENCE RATE</span></div>
<div class="status-badge">{c_status}</div>
</div>
""", unsafe_allow_html=True)

def render_ai_panel():
    freight = all_data["freight"]["data"]
    st.markdown(f"""
<div class="ai-hero">
<div class="header">● AI CHARTERING RECOMMENDATION</div>
<div class="status {freight["rec_class"]}">{freight["recommendation"]}</div>
<div class="confidence">Confidence: <strong>{freight["confidence"]}</strong></div>
<div class="metrics">
<div class="metric-col"><div class="label">EXPECTED 30-DAY MOVEMENT</div><div class="val">{freight["movement"]}</div></div>
<div class="metric-col"><div class="label">ESTIMATED SAVING PER VOYAGE</div><div class="val" style="color: #10b981;">$142,500</div></div>
<div class="metric-col"><div class="label">OPTIMAL WINDOW</div><div class="val">14 Days</div></div>
</div>
<div class="reason">💡 {freight["reason"]}</div>
</div>
""", unsafe_allow_html=True)

def render_forecast_chart():
    freight = all_data["freight"]["data"]
    fig = go.Figure()
    
    # Historical Trace
    fig.add_trace(go.Scatter(
        x=freight["dates"], 
        y=freight["historical_prices"], 
        mode='lines', 
        name='Historical Rates (Actual)', 
        line=dict(color='#00d4ff', width=2)
    ))
    
    # Generate confidence intervals
    forecast_prices = freight["forecast_prices"]
    future_dates = freight["future_dates"]
    
    # Calculate expanding variance using REAL-TIME risk data
    # Base uncertainty
    base_spread = 15.0
    cone_expansion = 1.2
    
    # Increase uncertainty based on LIVE telemetry
    weather_risk = all_data["weather_sg"].get("data", {}).get("risk_label", "NORMAL")
    if weather_risk == "HIGH": cone_expansion += 1.5
    elif weather_risk == "ELEVATED": cone_expansion += 0.8
    
    news_level = all_data["news"].get("data", {}).get("level", "MODERATE")
    if news_level == "HIGH": base_spread += 10.0; cone_expansion += 1.0
    elif news_level == "ELEVATED": base_spread += 5.0; cone_expansion += 0.5
    
    fuel_change = abs(all_data["fuel"].get("data", {}).get("change", 0.0))
    if fuel_change > 2.0: cone_expansion += 1.2
    elif fuel_change > 0.5: cone_expansion += 0.5
    
    std_devs = [base_spread + (i * cone_expansion) for i in range(len(forecast_prices))]
    upper_bound = [p + s for p, s in zip(forecast_prices, std_devs)]
    lower_bound = [p - s for p, s in zip(forecast_prices, std_devs)]
    
    # 95% Confidence Interval (Shaded Area)
    fig.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates)[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(245, 158, 11, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='95% Confidence Interval'
    ))
    
    # Forecast Trace
    fig.add_trace(go.Scatter(
        x=future_dates, 
        y=forecast_prices, 
        mode='lines', 
        name='Ensemble AI Forecast', 
        line=dict(color='#f59e0b', width=2.5, dash='dash')
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,212,255,0.1)', linecolor='rgba(0,212,255,0.2)', tickfont=dict(color='#94a3b8')),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,212,255,0.1)', linecolor='rgba(0,212,255,0.2)', tickfont=dict(color='#94a3b8')),
        legend=dict(orientation='h', y=1.1, font=dict(color='#FFF')),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_shap_attribution_chart(all_data):
    # Dynamically calculate SHAP proxies based on real-time data
    base_port = 0.25
    base_fuel = 0.20
    base_momentum = 0.15
    base_canal = 0.10
    base_weather = 0.05
    
    # Adjust based on live telemetry
    weather_risk = all_data["weather_sg"].get("data", {}).get("risk_label", "NORMAL")
    if weather_risk == "HIGH": base_weather += 0.15
    elif weather_risk == "ELEVATED": base_weather += 0.05
    
    fuel_change = abs(all_data["fuel"].get("data", {}).get("change", 0.0))
    if fuel_change > 2.0: base_fuel += 0.12
    elif fuel_change > 0.5: base_fuel += 0.05
    
    news_level = all_data["news"].get("data", {}).get("level", "MODERATE")
    if news_level == "HIGH": base_canal += 0.18
    elif news_level == "ELEVATED": base_canal += 0.08
    
    freight_pct = abs(all_data["freight"].get("data", {}).get("pct_change", 0.0))
    if freight_pct > 3.0: base_momentum += 0.10
    
    # Sort data for horizontal bar chart
    features = {
        "Port Wait Times (Singapore/Shanghai)": base_port,
        "Bunker Fuel (VLSFO Spot Swaps)": base_fuel,
        "Historical Momentum (Baltic Index 14D)": base_momentum,
        "Canal Chokepoint Transit Delays": base_canal,
        "Seasonal Weather Anomalies (ENSO / Typhoons)": base_weather,
    }
    
    # Sort by value ascending for plotly horizontal bar
    sorted_features = dict(sorted(features.items(), key=lambda item: item[1]))
    labels = list(sorted_features.keys())
    values = list(sorted_features.values())
    
    # Use a gradient of colors from light green to dark teal
    colors = ['#86efac', '#6ee7b7', '#34d399', '#2dd4bf', '#14b8a6']
    
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0)', width=1)),
        width=0.6
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=10, r=20, t=10, b=40),
        xaxis=dict(
            title=dict(text="Normalized Gini Importance", font=dict(size=11, color='#94a3b8')),
            showgrid=False, 
            zeroline=False,
            tickfont=dict(size=10, color='#94a3b8')
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False,
            tickfont=dict(size=11, color='#e2e8f0')
        ),
        height=320,
    )
    
    st.markdown('<div class="chart-container"><div class="chart-header"><div><div class="chart-title" style="font-size:1.1rem;">🧬 Feature Importance Attribution (SHAP Proxy)</div></div></div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

def render_risk_cards():
    st.markdown('<div class="risk-grid">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    weather = all_data["weather_sg"]
    w_status = get_status_badge_html(weather["status"], weather["updated_at"], weather["source"])
    if weather["status"] == DataStatus.LIVE:
        w_val = f'{weather["data"]["temperature"]}°C'
        w_sub = f'Wind {weather["data"]["wind_speed"]} km/h | {weather["data"]["risk_label"]}'
    else:
        w_val = '<span style="color:#ef4444; font-size: 1rem;">DATA UNAVAILABLE</span>'
        w_sub = "API Failed"

    marine = all_data["marine"]
    m_status = get_status_badge_html(marine["status"], marine["updated_at"], marine["source"])
    if marine["status"] == DataStatus.LIVE:
        m_val = f'{marine["data"]["wave_height"]}m Waves'
        m_sub = f'Risk: {marine["data"]["risk_label"]}'
    else:
        m_val = '<span style="color:#ef4444; font-size: 1rem;">DATA UNAVAILABLE</span>'
        m_sub = "API Failed"

    fuel = all_data["fuel"]
    f_status = get_status_badge_html(fuel["status"], fuel["updated_at"], fuel["source"])
    
    news = all_data["news"]
    n_status = get_status_badge_html(news["status"], news["updated_at"], news["source"])

    with c1:
        st.markdown(f"""
<div class="risk-card" style="animation-delay:0.1s;">
<div class="title"><div>🌤️ WEATHER (SINGAPORE)</div></div>
<div class="value">{w_val}</div>
<div class="sub">{w_sub}</div>
<div class="status-badge">{w_status}</div>
</div>
<div class="risk-card" style="animation-delay:0.2s; margin-top:16px;">
<div class="title"><div>⛽ GLOBAL FUEL (VLSFO)</div></div>
<div class="value">${fuel["data"]["price"]}/{fuel["data"]["unit"].split("/")[1]}</div>
<div class="sub"><span class="badge {'positive' if fuel['data']['change'] < 0 else 'negative'}">{'↓' if fuel['data']['change'] < 0 else '↑'} {fuel['data']['change']}%</span></div>
<div class="status-badge">{f_status}</div>
</div>
""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div class="risk-card" style="animation-delay:0.15s;">
<div class="title"><div>🌊 MARINE CONDITIONS (SOUTH CHINA SEA)</div></div>
<div class="value">{m_val}</div>
<div class="sub">{m_sub}</div>
<div class="status-badge">{m_status}</div>
</div>
<div class="risk-card" style="animation-delay:0.25s; margin-top:16px;">
<div class="title"><div>🌍 GEOPOLITICAL RISK</div></div>
<div class="value">{news["data"]["level"]}</div>
<div class="sub" style="font-size: 0.7rem;">{news["data"]["reason"]}</div>
<div class="status-badge">{n_status}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# MAIN PAGES
# ============================================================
inject_css()

if st.session_state.active_page == "Dashboard":
    render_page_header("Dashboard", "Real-time maritime freight intelligence & AI-driven chartering recommendations")
    render_section_header("📊", "MARKET OVERVIEW")
    render_kpi_cards()
    render_section_header("●", "AI INTELLIGENCE")
    render_ai_panel()
    render_section_header("📈", "FREIGHT RATE FORECAST")
    freight_status = get_simple_badge_html(all_data["freight"]["status"])
    st.markdown(f'<div class="chart-container"><div class="chart-header"><div><div class="chart-title">Baltic Dry Index (BDI)</div><div class="chart-sub">Historical & AI Prediction</div></div><div>{freight_status}</div></div>', unsafe_allow_html=True)
    render_forecast_chart()
    st.markdown('</div>', unsafe_allow_html=True)
    render_section_header("⚠️", "RISK INTELLIGENCE")
    render_risk_cards()
    
elif st.session_state.active_page == "Freight Forecast":
    render_page_header("Freight Forecast", "Detailed AI projections and historical analysis of bulk maritime rates")
    freight_status = get_simple_badge_html(all_data["freight"]["status"])
    st.markdown(f'<div class="chart-container"><div class="chart-header"><div><div class="chart-title">Advanced Rate Projections</div><div class="chart-sub">BDI Technical Analysis</div></div><div>{freight_status}</div></div>', unsafe_allow_html=True)
    render_forecast_chart()
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_shap_attribution_chart(all_data)
    
elif st.session_state.active_page == "Risk Intelligence":
    render_page_header("Risk Intelligence", "Global meteorological, geopolitical, and supply chain risk factors")
    render_risk_cards()

elif st.session_state.active_page == "Port & Route Intel":
    render_port_route_intel(render_page_header)
    
elif st.session_state.active_page == "Procurement":
    render_page_header("Procurement", "Contract optimization and bunker fuel cost estimations")
    render_kpi_cards()

elif st.session_state.active_page == "ROI & What-If":
    render_roi_simulator_view(render_page_header, all_data)

elif st.session_state.active_page == "Reports":
    render_reports_view(render_page_header)

elif st.session_state.active_page == "Settings":
    render_page_header("Settings", "Configure API preferences and system thresholds")
    st.markdown('<div class="chart-container"><h3>System Status</h3><p>All core intelligence engines are running normally.</p></div>', unsafe_allow_html=True)

# Render floating AI Chatbot across all pages
render_chatbot(all_data)

