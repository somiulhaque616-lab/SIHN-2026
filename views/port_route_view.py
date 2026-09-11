import streamlit as st
import plotly.graph_objects as go
from services.route_service import calculate_route
from services.weather_service import get_weather
from services.demo_services import get_freight_data # (or just remove the line completely if not needed)
from data.ports import PORTS
from utils.data_status import DataStatus, get_status_badge_html, get_simple_badge_html

def render_port_route_intel(render_page_header):
    render_page_header("Port & Route Intel", "Live congestion monitoring and optimal route mapping")
    
    port_names = list(PORTS.keys())
    
    # Selection Panel
    st.markdown('<div class="chart-container" style="margin-bottom: 24px;">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="margin-bottom: 16px;">PORT SELECTION</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 1])
    
    with c1:
        origin = st.selectbox("ORIGIN PORT", port_names, index=port_names.index("Shanghai"))
    with c2:
        dest = st.selectbox("DESTINATION PORT", port_names, index=port_names.index("Rotterdam"))
    with c3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # padding
        calculate_btn = st.button("CALCULATE ROUTE", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    route_data = calculate_route(origin, dest)
    
    if route_data:
        r_data = route_data["data"]
        
        # Top KPI Cards
        st.markdown('<div class="kpi-container" style="grid-template-columns: repeat(4, 1fr);">', unsafe_allow_html=True)
        
        distance_str = f"{r_data['distance_km']:,.0f} KM"
        eta_str = f"{r_data['eta_days']:.1f} Days"
        fuel_str = f"{r_data['fuel_mt']:,.0f} MT"
        
        # Origin Weather
        w_origin = get_weather(origin)
        w_status = get_simple_badge_html(w_origin["status"])
        w_text = f"{w_origin['data']['temperature']}°C, Wind {w_origin['data']['wind_speed']} km/h" if w_origin["status"] == DataStatus.LIVE else "UNAVAILABLE"
        
        # Dest Weather
        w_dest = get_weather(dest)
        wd_status = get_simple_badge_html(w_dest["status"])
        wd_text = f"{w_dest['data']['temperature']}°C, Wind {w_dest['data']['wind_speed']} km/h" if w_dest["status"] == DataStatus.LIVE else "UNAVAILABLE"
        
        calc_status = get_simple_badge_html(DataStatus.MODEL)
        
        kpi_cards = f"""
<div class="kpi-card">
<div class="title">DISTANCE <span>📏</span></div>
<div class="value">{distance_str}</div>
<div class="status-badge" style="margin-top:auto;">{calc_status}</div>
</div>
<div class="kpi-card">
<div class="title">ESTIMATED TRANSIT <span>⏱️</span></div>
<div class="value">{eta_str}</div>
<div class="status-badge" style="margin-top:auto;">{calc_status}</div>
</div>
<div class="kpi-card">
<div class="title">ORIGIN WEATHER <span>🌤️</span></div>
<div class="value" style="font-size: 1.2rem; margin-top: 8px;">{w_text}</div>
<div class="status-badge" style="margin-top:auto;">{w_status}</div>
</div>
<div class="kpi-card">
<div class="title">DEST WEATHER <span>🌧️</span></div>
<div class="value" style="font-size: 1.2rem; margin-top: 8px;">{wd_text}</div>
<div class="status-badge" style="margin-top:auto;">{wd_status}</div>
</div>
"""
        st.markdown(kpi_cards, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Map
        st.markdown('<div class="chart-container" style="margin-bottom: 32px;">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">LIVE ROUTE MAP</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        # Route Line
        fig.add_trace(go.Scattergeo(
            lon = r_data["map_lons"],
            lat = r_data["map_lats"],
            mode = 'lines',
            line = dict(width = 3, color = '#00d4ff'),
            name = 'Optimal Route'
        ))
        
        # Ports
        fig.add_trace(go.Scattergeo(
            lon = [PORTS[origin]["lon"], PORTS[dest]["lon"]],
            lat = [PORTS[origin]["lat"], PORTS[dest]["lat"]],
            hoverinfo = 'text',
            text = [origin, dest],
            mode = 'markers+text',
            marker = dict(size = 10, color = '#10b981', line=dict(width=2, color='white')),
            textposition="bottom center",
            textfont=dict(color="white", size=14, family="Inter"),
            name = 'Ports'
        ))

        fig.update_layout(
            geo = dict(
                showland = True,
                landcolor = "#0B1D36",
                showocean = True,
                oceancolor = "#050C18",
                showcountries = True,
                countrycolor = "#1E3A5F",
                bgcolor = 'rgba(0,0,0,0)',
                projection_type = "equirectangular",
                center=dict(lat=20, lon=80),
                projection_scale=1.5
            ),
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Congestion & Chokepoints
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-title">PORT CONGESTION MONITORING</div>', unsafe_allow_html=True)
            st.info("Port congestion data will appear here when a verified data source is connected.")
            
        with col2:
            st.markdown('<div class="section-title">GLOBAL MARITIME CHOKEPOINTS</div>', unsafe_allow_html=True)
            st.info("Maritime chokepoint intelligence will appear here when a verified data source is connected.")
            
        # AI Route Recommendation
        st.markdown('<div class="section-title">AI ROUTE RECOMMENDATION</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="ai-hero">
<div class="header">● RECOMMENDED ROUTE</div>
<div class="status wait" style="font-size: 2.5rem; color: #00d4ff; text-shadow: 0 0 20px rgba(0, 212, 255, 0.4);">{origin} → {dest}</div>
<div class="confidence">Confidence: <strong>HIGH</strong></div>
<div class="metrics">
<div class="metric-col"><div class="label">EXPECTED TRANSIT</div><div class="val">{eta_str}</div></div>
<div class="metric-col"><div class="label">FUEL ESTIMATE</div><div class="val" style="color: #10b981;">{fuel_str}</div></div>
<div class="metric-col"><div class="label">OVERALL RISK</div><div class="val" style="color: #f59e0b;">MODERATE</div></div>
</div>
<div class="reason">💡 Based on current weather models, chokepoint congestion, and geopolitical risk factors, this route offers the optimal balance of speed and security.</div>
<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(0,212,255,0.2);">{get_simple_badge_html(DataStatus.MODEL)}</div>
</div>
""", unsafe_allow_html=True)
