import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from services.report_service import generate_intelligence_report
from utils.pdf_generator import build_pdf_report
from utils.export_utils import export_report_csv, export_report_json
from utils.data_status import DataStatus, get_status_badge_html, get_simple_badge_html

@st.fragment
def render_reports_view(render_page_header):
    render_page_header("Reports", "Generate and export intelligence briefs")
    
    # Initialize session state for report history & current report
    if "report_history" not in st.session_state:
        st.session_state.report_history = []
        
    if "current_report" not in st.session_state:
        # Pre-generate an initial default report on first load so user immediately sees a report
        initial_rep = generate_intelligence_report("Weekly Freight Intelligence", "Last 7 Days", live_mode=st.session_state.live_mode)
        st.session_state.current_report = initial_rep
        st.session_state.report_history.append(initial_rep)

    # ============================================================
    # 1. CREATE INTELLIGENCE REPORT CARD
    # ============================================================
    st.markdown('<div class="chart-container" style="margin-bottom: 28px;">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="margin-bottom: 16px;">⚙️ CREATE INTELLIGENCE REPORT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    report_types = [
        "Daily Market Brief",
        "Weekly Freight Intelligence",
        "Monthly Maritime Outlook",
        "Route Risk Report",
        "Chartering Recommendation Report",
        "Procurement Intelligence Report"
    ]
    
    period_options = [
        "Today",
        "Last 7 Days",
        "Last 30 Days",
        "Custom Range"
    ]
    
    with col1:
        selected_type = st.selectbox(
            "SELECT REPORT TYPE",
            options=report_types,
            index=1,
            key="rep_type_select"
        )
        
    with col2:
        selected_period = st.radio(
            "REPORT PERIOD",
            options=period_options,
            index=1,
            horizontal=True,
            key="rep_period_radio"
        )
        
    custom_dates = None
    if selected_period == "Custom Range":
        c_start, c_end = st.columns(2)
        with c_start:
            start_d = st.date_input("Start Date", value=date.today() - timedelta(days=14))
        with c_end:
            end_d = st.date_input("End Date", value=date.today())
        custom_dates = (start_d, end_d)
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    gen_btn = st.button("🚀 GENERATE INTELLIGENCE REPORT", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle Generation
    if gen_btn:
        with st.spinner("Aggregating maritime data streams & synthesizing AI report..."):
            new_report = generate_intelligence_report(
                report_type=selected_type,
                period=selected_period,
                custom_range=custom_dates,
                live_mode=st.session_state.live_mode
            )
            st.session_state.current_report = new_report
            # Append to history (keep max 15)
            st.session_state.report_history.insert(0, new_report)
            st.session_state.report_history = st.session_state.report_history[:15]
            st.success(f"Generated {new_report['title']} successfully!")

    curr_report = st.session_state.current_report

    # ============================================================
    # 2. REPORT PREVIEW HEADER & ACTIONS
    # ============================================================
    st.markdown('<div class="section-title">📄 REPORT PREVIEW</div>', unsafe_allow_html=True)
    
    # Action buttons container
    pdf_bytes = build_pdf_report(curr_report)
    csv_str = export_report_csv(curr_report)
    json_str = export_report_json(curr_report)
    
    top_meta_col1, top_meta_col2 = st.columns([2, 3])
    with top_meta_col1:
        mode_badge = f'<span class="badge positive">LIVE DATA REPORT</span>' if not curr_report["is_demo"] else f'<span class="badge negative">DEMO REPORT</span>'
        
        # Format custom range if it exists
        period_str = curr_report['period']
        c_range = curr_report.get('custom_range')
        if period_str == "Custom Range" and c_range and len(c_range) == 2:
            period_str = f"Custom Range ({c_range[0]} to {c_range[1]})"
            
        st.markdown(f"""
<div style="margin-bottom: 12px;">
<div style="font-size: 1.3rem; font-weight: 800; color: #FFF;">{curr_report['title']}</div>
<div style="font-size: 0.8rem; color: #94a3b8;">Period: <strong>{period_str}</strong> &nbsp;|&nbsp; Generated: <strong>{curr_report['generated_date_display']}</strong> &nbsp; {mode_badge}</div>
</div>
""", unsafe_allow_html=True)

    with top_meta_col2:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                label="📥 DOWNLOAD PDF",
                data=pdf_bytes,
                file_name=f"OptiFreight_{curr_report['id']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d2:
            st.download_button(
                label="📊 EXPORT CSV",
                data=csv_str,
                file_name=f"OptiFreight_{curr_report['id']}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d3:
            st.download_button(
                label="📄 EXPORT JSON",
                data=json_str,
                file_name=f"OptiFreight_{curr_report['id']}.json",
                mime="application/json",
                use_container_width=True
            )

    # ============================================================
    # 3. KPI CARDS
    # ============================================================
    kpis = curr_report["kpis"]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    kpi_items = [
        ("CURRENT FREIGHT RATE", kpis["current_freight_rate"], "📈"),
        ("30-DAY FORECAST", kpis["forecast_30d"], "📉"),
        ("MARKET TREND", kpis["market_trend"], "📊"),
        ("ROUTE RISK", kpis["route_risk"], "⚠️"),
        ("PORT CONGESTION", kpis["port_congestion"], "⚓"),
        ("ESTIMATED SAVINGS", kpis["estimated_savings"], "💰"),
    ]
    
    cols = [c1, c2, c3, c4, c5, c6]
    for idx, (label, item, icon) in enumerate(kpi_items):
        st_badge = get_simple_badge_html(item["status"])
        with cols[idx]:
            st.markdown(f"""
<div class="kpi-card" style="padding: 14px; min-height: 120px;">
<div class="title" style="font-size: 0.62rem;">{label} {icon}</div>
<div class="value" style="font-size: 1.15rem; margin-bottom: 6px;">{item['val']}</div>
<div class="status-badge" style="margin-top: 4px; padding-top: 4px;">{st_badge}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # 4. AI EXECUTIVE SUMMARY
    # ============================================================
    exec_sum = curr_report["executive_summary"]
    st.markdown(f"""
<div class="ai-hero" style="margin-bottom: 24px; padding: 24px;">
<div class="header">● AI EXECUTIVE SUMMARY — {curr_report['title'].upper()}</div>
<div style="display: grid; gap: 14px;">
<div><strong style="color: #00d4ff;">Market Outlook:</strong> <span style="color: #e2e8f0;">{exec_sum['market_outlook']}</span></div>
<div><strong style="color: #00d4ff;">Freight Forecast:</strong> <span style="color: #e2e8f0;">{exec_sum['freight_forecast']}</span></div>
<div><strong style="color: #00d4ff;">Operational Risk:</strong> <span style="color: #e2e8f0;">{exec_sum['operational_risk']}</span></div>
<div><strong style="color: #00d4ff;">Chartering Recommendation:</strong> <span style="color: #e2e8f0;">{exec_sum['chartering_recommendation']}</span></div>
<div><strong style="color: #10b981;">Potential Opportunity:</strong> <span style="color: #e2e8f0;">{exec_sum['potential_opportunity']}</span></div>
</div>
</div>
""", unsafe_allow_html=True)

    # ============================================================
    # 5. KEY INTELLIGENCE GRID
    # ============================================================
    st.markdown('<div class="section-title">💡 KEY INTELLIGENCE</div>', unsafe_allow_html=True)
    
    key_intel = curr_report["key_intelligence"]
    
    col_a, col_b, col_c = st.columns(3)
    
    # Column A: Freight Market & Chartering
    with col_a:
        f_data = key_intel["freight_market"]
        f_st = get_simple_badge_html(f_data["status"])
        st.markdown(f"""
<div class="risk-card" style="margin-bottom: 16px;">
<div class="title"><div>📈 FREIGHT MARKET</div></div>
<div class="value">{f_data['current_rate']}</div>
<div class="sub">Trend: <strong>{f_data['trend']}</strong><br/>30-Day Target: <strong>{f_data['forecast_30d']}</strong></div>
<div class="status-badge">{f_st}</div>
</div>
""", unsafe_allow_html=True)

        c_data = key_intel["chartering"]
        c_st = get_simple_badge_html(c_data["status"])
        st.markdown(f"""
<div class="risk-card">
<div class="title"><div>⚓ AI CHARTERING</div></div>
<div class="value" style="color: #10b981;">{c_data['action']}</div>
<div class="sub">Confidence: <strong>{c_data['confidence']}</strong> | Est. Savings: <strong>{c_data['savings']}</strong><br/><i>{c_data['reason']}</i></div>
<div class="status-badge">{c_st}</div>
</div>
""", unsafe_allow_html=True)

    # Column B: Route & Port Intelligence
    with col_b:
        r_data = key_intel["route_intelligence"]
        r_st = get_simple_badge_html(r_data["status"])
        st.markdown(f"""
<div class="risk-card" style="margin-bottom: 16px;">
<div class="title"><div>🗺️ ROUTE INTELLIGENCE</div></div>
<div class="value" style="font-size: 1.2rem;">{r_data['recommended_route']}</div>
<div class="sub">Distance: <strong>{r_data['distance_nm']}</strong> | Transit: <strong>{r_data['transit_time']}</strong><br/>Route Risk: <span style="color: #f59e0b; font-weight: bold;">{r_data['route_risk']}</span></div>
<div class="status-badge">{r_st}</div>
</div>
""", unsafe_allow_html=True)

        p_data = key_intel["port_intelligence"]
        p_st = get_simple_badge_html(p_data["status"])
        st.markdown(f"""
<div class="risk-card">
<div class="title"><div>🏭 PORT INTELLIGENCE</div></div>
<div class="value">{p_data['congestion_level']}</div>
<div class="sub">Avg Wait: <strong>{p_data['wait_time']}</strong> | Trend: <strong>{p_data['trend']}</strong></div>
<div class="status-badge">{p_st}</div>
</div>
""", unsafe_allow_html=True)

    # Column C: Weather & Bunker Fuel
    with col_c:
        w_data = key_intel["weather"]
        w_st = get_simple_badge_html(w_data["status"])
        st.markdown(f"""
<div class="risk-card" style="margin-bottom: 16px;">
<div class="title"><div>🌤️ WEATHER & MARINE</div></div>
<div class="value">{w_data['weather_risk']}</div>
<div class="sub">Singapore: <strong>{w_data['singapore_temp']}</strong>, <strong>{w_data['singapore_wind']}</strong><br/>Marine State: <strong>{w_data['marine_conditions']}</strong></div>
<div class="status-badge">{w_st}</div>
</div>
""", unsafe_allow_html=True)

        fuel_data = key_intel["fuel"]
        fuel_st = get_simple_badge_html(fuel_data["status"])
        st.markdown(f"""
<div class="risk-card">
<div class="title"><div>⛽ BUNKER FUEL</div></div>
<div class="value">{fuel_data['vlsfo_price']}</div>
<div class="sub">Price Trend: <strong>{fuel_data['trend']}</strong></div>
<div class="status-badge">{fuel_st}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # 6. CHARTS SECTION
    # ============================================================
    st.markdown('<div class="section-title">📊 REPORT ANALYTICS & CHARTS</div>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    chart_data = curr_report["chart_data"]
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-header"><div><div class="chart-title">Freight Rate Trend & AI Prediction</div><div class="chart-sub">Historical BDI vs 30-Day Forecast</div></div></div>', unsafe_allow_html=True)
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=chart_data["dates"], y=chart_data["historical_prices"], mode='lines', name='Historical', line=dict(color='#00d4ff', width=2)))
        fig1.add_trace(go.Scatter(x=chart_data["future_dates"], y=chart_data["forecast_prices"], mode='lines', name='AI Forecast', line=dict(color='#f59e0b', width=2.5, dash='dash')))
        
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,212,255,0.1)', tickfont=dict(color='#94a3b8')),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,212,255,0.1)', tickfont=dict(color='#94a3b8')),
            legend=dict(orientation='h', y=1.1, font=dict(color='#FFF')),
            height=300,
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-header"><div><div class="chart-title">Maritime Operational Risk Breakdown</div><div class="chart-sub">Multi-Factor Risk Index</div></div></div>', unsafe_allow_html=True)
        
        categories = ['Weather', 'Marine Waves', 'Geopolitical', 'Port Congestion', 'Fuel Volatility']
        risk_scores = [35, 45, 60, 40, 25] if not curr_report["is_demo"] else [30, 40, 55, 50, 30]
        
        fig2 = go.Figure(data=go.Scatterpolar(
            r=risk_scores,
            theta=categories,
            fill='toself',
            fillcolor='rgba(0, 212, 255, 0.2)',
            line=dict(color='#00d4ff', width=2)
        ))
        
        fig2.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor='rgba(0,212,255,0.15)'),
                angularaxis=dict(tickfont=dict(color='#FFF', size=11), gridcolor='rgba(0,212,255,0.15)'),
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # 7. DATA SOURCES TRANSPARENCY
    # ============================================================
    st.markdown('<div class="section-title">🔍 DATA SOURCES & TRANSPARENCY</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container" style="padding: 16px;">', unsafe_allow_html=True)
    
    ds_cols = st.columns([2, 3, 2, 2])
    with ds_cols[0]: st.markdown("<strong style='color:#00d4ff;'>Module / Field</strong>", unsafe_allow_html=True)
    with ds_cols[1]: st.markdown("<strong style='color:#00d4ff;'>Provider / Service</strong>", unsafe_allow_html=True)
    with ds_cols[2]: st.markdown("<strong style='color:#00d4ff;'>Data Status</strong>", unsafe_allow_html=True)
    with ds_cols[3]: st.markdown("<strong style='color:#00d4ff;'>Last Updated</strong>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(0,212,255,0.15); margin: 8px 0;'>", unsafe_allow_html=True)
    
    for ds in curr_report["data_sources"]:
        c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
        with c1: st.markdown(f"<span style='color:#FFF;'>{ds['name']}</span>", unsafe_allow_html=True)
        with c2: st.markdown(f"<span style='color:#94a3b8;'>{ds['source']}</span>", unsafe_allow_html=True)
        with c3: st.markdown(get_simple_badge_html(ds['status']), unsafe_allow_html=True)
        with c4: st.markdown(f"<span style='color:#94a3b8;'>{ds['updated']}</span>", unsafe_allow_html=True)
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # 8. REPORT HISTORY TABLE
    # ============================================================
    st.markdown('<div class="section-title">📜 REPORT HISTORY</div>', unsafe_allow_html=True)
    
    if not st.session_state.report_history:
        st.info("No report history available for this session.")
    else:
        st.markdown('<div class="chart-container" style="padding: 16px;">', unsafe_allow_html=True)
        
        h_cols = st.columns([3, 2, 2, 2, 3])
        with h_cols[0]: st.markdown("<strong style='color:#00d4ff;'>Report Name</strong>", unsafe_allow_html=True)
        with h_cols[1]: st.markdown("<strong style='color:#00d4ff;'>Period</strong>", unsafe_allow_html=True)
        with h_cols[2]: st.markdown("<strong style='color:#00d4ff;'>Generated</strong>", unsafe_allow_html=True)
        with h_cols[3]: st.markdown("<strong style='color:#00d4ff;'>Status</strong>", unsafe_allow_html=True)
        with h_cols[4]: st.markdown("<strong style='color:#00d4ff;'>Actions</strong>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: rgba(0,212,255,0.15); margin: 8px 0;'>", unsafe_allow_html=True)
        
        for idx, rep in enumerate(st.session_state.report_history):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 3])
            with c1: st.markdown(f"<strong style='color:#FFF;'>{rep['title']}</strong>", unsafe_allow_html=True)
            with c2: st.markdown(f"<span style='color:#94a3b8;'>{rep['period']}</span>", unsafe_allow_html=True)
            with c3: st.markdown(f"<span style='color:#94a3b8;'>{rep['generated_date_display']}</span>", unsafe_allow_html=True)
            with c4: st.markdown(f"<span class='badge positive'>READY</span>", unsafe_allow_html=True)
            with c5:
                v_col, d_col = st.columns(2)
                with v_col:
                    if st.button("👁️ VIEW", key=f"hist_view_{idx}_{rep['id']}", use_container_width=True):
                        st.session_state.current_report = rep
                        st.rerun()
                with d_col:
                    h_pdf = build_pdf_report(rep)
                    st.download_button(
                        label="📥 PDF",
                        data=h_pdf,
                        file_name=f"OptiFreight_{rep['id']}.pdf",
                        mime="application/pdf",
                        key=f"hist_dl_{idx}_{rep['id']}",
                        use_container_width=True
                    )
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
