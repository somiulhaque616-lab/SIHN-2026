import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def init_simulator_state(all_data):
    """Initialize default simulation inputs from active data."""
    freight_rate = all_data.get("freight", {}).get("data", {}).get("current_rate", 32.50)
    fuel_price = all_data.get("fuel", {}).get("data", {}).get("price", 610.00)
    
    defaults = {
        "roi_vol": 50000,
        "roi_dist": 8000,
        "roi_voyages": 1,
        "roi_charter_type": "Spot Charter",
        
        "roi_base_freight": float(freight_rate),
        "roi_scen_freight": float(freight_rate),
        
        "roi_base_fuel": float(fuel_price),
        "roi_scen_fuel": float(fuel_price),
        "roi_fuel_cons": 28.5, # MT/day
        "roi_voy_duration": 14.0, # days
        
        "roi_base_port": 45000.0,
        "roi_scen_port": 45000.0,
        "roi_base_delay": 0.0,
        "roi_scen_delay": 0.0,
        "roi_delay_cost": 1500.0, # $/hr
        
        "roi_base_procurement": 12000.0,
        "roi_scen_procurement": 12000.0,
        
        "roi_base_revenue_mt": 40.0,
        "roi_scen_revenue_mt": 40.0,
        
        "roi_market_risk": 5.0,
        "roi_fuel_risk": 5.0,
        "roi_delay_prob": 20.0,
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def apply_preset(preset_name):
    """Apply predefined scenario adjustments."""
    base_freight = st.session_state.roi_base_freight
    base_fuel = st.session_state.roi_base_fuel
    base_rev = st.session_state.roi_base_revenue_mt
    
    st.session_state.roi_scen_revenue_mt = base_rev # Default to keeping revenue stable
    
    if preset_name == "MARKET DROP":
        st.session_state.roi_scen_freight = base_freight * 0.90
        st.session_state.roi_scen_fuel = base_fuel
        st.session_state.roi_scen_delay = st.session_state.roi_base_delay
        st.session_state.roi_scen_revenue_mt = base_rev * 0.85
    elif preset_name == "MARKET SURGE":
        st.session_state.roi_scen_freight = base_freight * 1.15
        st.session_state.roi_scen_fuel = base_fuel
        st.session_state.roi_scen_delay = st.session_state.roi_base_delay
        st.session_state.roi_scen_revenue_mt = base_rev * 1.25
    elif preset_name == "FUEL SHOCK":
        st.session_state.roi_scen_freight = base_freight
        st.session_state.roi_scen_fuel = base_fuel * 1.20
        st.session_state.roi_scen_delay = st.session_state.roi_base_delay
    elif preset_name == "PORT CONGESTION":
        st.session_state.roi_scen_freight = base_freight
        st.session_state.roi_scen_fuel = base_fuel
        st.session_state.roi_scen_delay = st.session_state.roi_base_delay + 48.0
    elif preset_name == "OPTIMISTIC":
        st.session_state.roi_scen_freight = base_freight * 0.90
        st.session_state.roi_scen_fuel = base_fuel * 0.95
        st.session_state.roi_scen_delay = max(0, st.session_state.roi_base_delay - 12.0)
    elif preset_name == "STRESS TEST":
        st.session_state.roi_scen_freight = base_freight * 1.20
        st.session_state.roi_scen_fuel = base_fuel * 1.20
        st.session_state.roi_scen_delay = st.session_state.roi_base_delay + 72.0
        st.session_state.roi_scen_revenue_mt = base_rev * 0.90


def calculate_costs():
    """Calculate all financial metrics based on session state."""
    vol = st.session_state.roi_vol
    voyages = st.session_state.roi_voyages
    total_vol = vol * voyages
    
    # Baseline
    base_freight_cost = st.session_state.roi_base_freight * total_vol
    base_fuel_cost = st.session_state.roi_base_fuel * st.session_state.roi_fuel_cons * st.session_state.roi_voy_duration * voyages
    base_port_cost = st.session_state.roi_base_port * voyages
    base_delay_cost = st.session_state.roi_base_delay * st.session_state.roi_delay_cost * voyages
    base_procurement_cost = st.session_state.roi_base_procurement * voyages
    
    total_base = base_freight_cost + base_fuel_cost + base_port_cost + base_delay_cost + base_procurement_cost
    base_revenue = st.session_state.roi_base_revenue_mt * total_vol
    base_profit = base_revenue - total_base
    
    # Scenario
    scen_freight_cost = st.session_state.roi_scen_freight * total_vol
    scen_fuel_cost = st.session_state.roi_scen_fuel * st.session_state.roi_fuel_cons * st.session_state.roi_voy_duration * voyages
    scen_port_cost = st.session_state.roi_scen_port * voyages
    scen_delay_cost = st.session_state.roi_scen_delay * st.session_state.roi_delay_cost * voyages
    scen_procurement_cost = st.session_state.roi_scen_procurement * voyages
    
    total_scen = scen_freight_cost + scen_fuel_cost + scen_port_cost + scen_delay_cost + scen_procurement_cost
    scen_revenue = st.session_state.roi_scen_revenue_mt * total_vol
    scen_profit = scen_revenue - total_scen
    
    profit_impact = scen_profit - base_profit
    impact_pct = (profit_impact / abs(base_profit) * 100) if base_profit != 0 else 0
    
    # Operational ROI (Comparing profit impact to a fixed enterprise optimization tool cost proxy)
    optimization_cost = 50000.0 
    operational_roi = (profit_impact / optimization_cost * 100) if optimization_cost > 0 else 0
    
    # Risk-Adjusted P&L Impact
    risk_factor = 1.0 - (st.session_state.roi_market_risk / 100.0) - (st.session_state.roi_fuel_risk / 100.0) - (st.session_state.roi_delay_prob / 100.0 * 0.5)
    risk_adj_impact = profit_impact * risk_factor
    
    return {
        "base_breakdown": [base_freight_cost, base_fuel_cost, base_port_cost, base_delay_cost, base_procurement_cost],
        "scen_breakdown": [scen_freight_cost, scen_fuel_cost, scen_port_cost, scen_delay_cost, scen_procurement_cost],
        "base_profit": base_profit,
        "scen_profit": scen_profit,
        "profit_impact": profit_impact,
        "impact_pct": impact_pct,
        "roi": operational_roi,
        "risk_adj_impact": risk_adj_impact
    }


def inject_roi_css():
    st.markdown("""
    <style>
    .roi-kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
    .roi-kpi-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s; animation: fadeInUp 0.4s ease backwards; position: relative; overflow: hidden; }
    .roi-kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: var(--primary); opacity: 0.8; }
    .roi-kpi-card:hover { border-color: var(--card-hover-border); transform: translateY(-2px); }
    .roi-kpi-card .title { font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
    .roi-kpi-card .value { font-size: 2.2rem; font-weight: 800; color: #FFF; line-height: 1.1; }
    .roi-kpi-card .value.positive { color: var(--positive); text-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
    .roi-kpi-card .value.negative { color: var(--critical); text-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }
    .roi-kpi-card .sub { font-size: 0.85rem; color: #FFF; margin-top: 8px; opacity: 0.8; }
    
    .preset-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 32px; }
    
    /* Heatmap Table */
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; font-family: 'Inter', sans-serif; box-shadow: 0 0 20px rgba(0,0,0,0.15); border-radius: 8px; overflow: hidden; }
    .styled-table thead tr { background-color: rgba(0, 212, 255, 0.15); color: #FFF; text-align: center; }
    .styled-table th, .styled-table td { padding: 12px 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }
    .styled-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
    .styled-table tbody tr:nth-of-type(even) { background-color: rgba(255,255,255,0.02); }
    
    .matrix-val { font-weight: 700; }
    .matrix-pos { color: #10b981; }
    .matrix-neg { color: #ef4444; }
    
    .section-header { font-size: 1.1rem; font-weight: 700; color: #00d4ff; border-bottom: 1px solid rgba(0,212,255,0.2); padding-bottom: 8px; margin-bottom: 16px; margin-top: 24px; }
    </style>
    """, unsafe_allow_html=True)


@st.fragment
def render_roi_simulator_view(render_page_header_func, all_data):
    """Render the Enterprise ROI & What-If Scenario Simulator."""
    init_simulator_state(all_data)
    inject_roi_css()
    
    render_page_header_func("Enterprise ROI & What-If Scenario Simulator", "Simulate chartering, freight, fuel and route scenarios to estimate financial impact.")
    
    # ---------------------------------------------------------
    # SCENARIO PRESETS
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">⚡ SCENARIO PRESETS</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    presets = [
        ("MARKET DROP", "⬇️ Freight -10%"),
        ("MARKET SURGE", "⬆️ Freight +15%"),
        ("FUEL SHOCK", "⛽ Fuel +20%"),
        ("PORT CONGESTION", "⚓ Delay +48h"),
        ("OPTIMISTIC", "🌟 Best Case"),
        ("STRESS TEST", "⚠️ Worst Case")
    ]
    
    for i, (p_name, p_label) in enumerate(presets):
        with cols[i]:
            if st.button(p_label, key=f"preset_{i}", use_container_width=True):
                apply_preset(p_name)
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # INPUTS PANEL
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">🎛️ SCENARIO PARAMETERS</div>', unsafe_allow_html=True)
    
    with st.expander("Expand to Adjust Variables", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown('<div class="section-header">A. VOYAGE / REVENUE</div>', unsafe_allow_html=True)
            st.session_state.roi_vol = st.number_input("Cargo Volume (MT)", min_value=1000, value=st.session_state.roi_vol, step=1000)
            st.session_state.roi_base_revenue_mt = st.number_input("Base Revenue ($/MT)", min_value=0.0, value=st.session_state.roi_base_revenue_mt, step=1.0)
            st.session_state.roi_scen_revenue_mt = st.number_input("Scenario Revenue ($/MT)", min_value=0.0, value=st.session_state.roi_scen_revenue_mt, step=1.0)
            st.selectbox("Charter Type", ["Spot Charter", "Time Charter", "Contract"], key="roi_charter_type")
            
        with c2:
            st.markdown('<div class="section-header">B. FREIGHT ASSUMPTIONS</div>', unsafe_allow_html=True)
            st.session_state.roi_base_freight = st.number_input("Baseline Freight Rate ($/MT)", min_value=0.0, value=st.session_state.roi_base_freight, step=1.0)
            st.session_state.roi_scen_freight = st.number_input("Scenario Freight Rate ($/MT)", min_value=0.0, value=st.session_state.roi_scen_freight, step=1.0)
            f_diff = st.session_state.roi_scen_freight - st.session_state.roi_base_freight
            f_pct = (f_diff / st.session_state.roi_base_freight * 100) if st.session_state.roi_base_freight > 0 else 0
            st.caption(f"Difference: ${f_diff:+.2f} ({f_pct:+.1f}%)")
            
        with c3:
            st.markdown('<div class="section-header">C. FUEL ASSUMPTIONS</div>', unsafe_allow_html=True)
            st.session_state.roi_base_fuel = st.number_input("Baseline VLSFO Price ($/MT)", min_value=0.0, value=st.session_state.roi_base_fuel, step=10.0)
            st.session_state.roi_scen_fuel = st.number_input("Scenario VLSFO Price ($/MT)", min_value=0.0, value=st.session_state.roi_scen_fuel, step=10.0)
            st.session_state.roi_fuel_cons = st.number_input("Fuel Consumption (MT/day)", min_value=0.0, value=st.session_state.roi_fuel_cons, step=1.0)
            st.session_state.roi_voy_duration = st.number_input("Voyage Duration (days)", min_value=0.0, value=st.session_state.roi_voy_duration, step=1.0)
            
        with c4:
            st.markdown('<div class="section-header">D. PORT & DELAY</div>', unsafe_allow_html=True)
            st.session_state.roi_base_port = st.number_input("Baseline Port Cost ($)", min_value=0.0, value=st.session_state.roi_base_port, step=1000.0)
            st.session_state.roi_scen_port = st.number_input("Scenario Port Cost ($)", min_value=0.0, value=st.session_state.roi_scen_port, step=1000.0)
            st.session_state.roi_base_delay = st.number_input("Baseline Delay (hours)", min_value=0.0, value=st.session_state.roi_base_delay, step=12.0)
            st.session_state.roi_scen_delay = st.number_input("Scenario Delay (hours)", min_value=0.0, value=st.session_state.roi_scen_delay, step=12.0)
            st.session_state.roi_delay_cost = st.number_input("Cost per Delay Hour ($)", min_value=0.0, value=st.session_state.roi_delay_cost, step=100.0)


    # Calculate metrics
    res = calculate_costs()
    
    # ---------------------------------------------------------
    # KPI DASHBOARD (PROFIT & LOSS)
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">📈 FINANCIAL IMPACT (PROFIT & LOSS)</div>', unsafe_allow_html=True)
    
    impact_class = "positive" if res["profit_impact"] >= 0 else "negative"
    impact_sign = "+" if res["profit_impact"] >= 0 else ""
    
    base_class = "positive" if res["base_profit"] >= 0 else "negative"
    base_sign = "+" if res["base_profit"] >= 0 else ""
    
    scen_class = "positive" if res["scen_profit"] >= 0 else "negative"
    scen_sign = "+" if res["scen_profit"] >= 0 else ""
    
    st.markdown('<div class="roi-kpi-grid">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="roi-kpi-card" style="animation-delay: 0s;">
        <div class="title">BASELINE P&L</div>
        <div class="value {base_class}">{base_sign}${res['base_profit']:,.0f}</div>
        <div class="sub">Current Reference Profit</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="roi-kpi-card" style="animation-delay: 0.1s;">
        <div class="title">SCENARIO P&L</div>
        <div class="value {scen_class}">{scen_sign}${res['scen_profit']:,.0f}</div>
        <div class="sub">Simulated Profit Outcome</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="roi-kpi-card" style="animation-delay: 0.2s;">
        <div class="title">NET P&L IMPACT</div>
        <div class="value {impact_class}">{impact_sign}${res['profit_impact']:,.0f}</div>
        <div class="sub">{impact_sign}{res['impact_pct']:.2f}% Impact vs Baseline</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="roi-kpi-card" style="animation-delay: 0.3s;">
        <div class="title">OPERATIONAL ROI</div>
        <div class="value {impact_class}">{impact_sign}{res['roi']:,.0f}%</div>
        <div class="sub">Relative to $50k optimization cost</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="roi-kpi-card" style="animation-delay: 0.4s;">
        <div class="title">RISK-ADJUSTED P&L IMPACT</div>
        <div class="value {impact_class}">{impact_sign}${res['risk_adj_impact']:,.0f}</div>
        <div class="sub">Factoring market/fuel/delay probabilities</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CHARTS
    # ---------------------------------------------------------
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.markdown('<div class="chart-container"><div class="chart-title">Cost Breakdown Comparison</div>', unsafe_allow_html=True)
        categories = ['Freight', 'Fuel', 'Port', 'Delay', 'Procurement']
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(name='Baseline', x=categories, y=res["base_breakdown"], marker_color='#3b82f6'))
        fig1.add_trace(go.Bar(name='Scenario', x=categories, y=res["scen_breakdown"], marker_color='#14b8a6'))
        fig1.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFF'),
            margin=dict(l=0, r=0, t=30, b=0), height=350,
            xaxis=dict(showgrid=False, linecolor='rgba(0,212,255,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,212,255,0.1)', linecolor='rgba(0,212,255,0.2)'),
            legend=dict(orientation='h', y=1.1)
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_chart2:
        st.markdown('<div class="chart-container"><div class="chart-title">P&L Sensitivity Analysis (Freight Rate Cost)</div>', unsafe_allow_html=True)
        # Generate points for line chart (showing Profit instead of Cost)
        f_rates = np.linspace(st.session_state.roi_base_freight * 0.7, st.session_state.roi_base_freight * 1.3, 20)
        
        vols = st.session_state.roi_vol * st.session_state.roi_voyages
        fixed_costs = res["scen_breakdown"][1] + res["scen_breakdown"][2] + res["scen_breakdown"][3] + res["scen_breakdown"][4]
        scen_revenue = st.session_state.roi_scen_revenue_mt * vols
        
        # Profit = Revenue - (Freight + Fixed Costs)
        profits = [scen_revenue - (f * vols + fixed_costs) for f in f_rates]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=f_rates, y=profits, mode='lines', name='P&L Curve', line=dict(color='#00d4ff', width=3)))
        # Mark baseline and scenario
        fig2.add_trace(go.Scatter(x=[st.session_state.roi_base_freight], y=[res['base_profit']], mode='markers', name='Baseline', marker=dict(color='#f59e0b', size=12, symbol='star')))
        fig2.add_trace(go.Scatter(x=[st.session_state.roi_scen_freight], y=[res['scen_profit']], mode='markers', name='Scenario', marker=dict(color='#10b981', size=12, symbol='star')))
        
        # Add zero-profit baseline
        fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFF'),
            margin=dict(l=0, r=0, t=30, b=0), height=350,
            xaxis=dict(title='Freight Rate ($/MT)', showgrid=True, gridcolor='rgba(0,212,255,0.1)'),
            yaxis=dict(title='Total Voyage Profit ($)', showgrid=True, gridcolor='rgba(0,212,255,0.1)'),
            legend=dict(orientation='h', y=1.1)
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SENSITIVITY MATRIX
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">🧮 ENTERPRISE SENSITIVITY MATRIX</div>', unsafe_allow_html=True)
    st.caption("MODELLED SCENARIO: Financial impact of concurrent Freight and Fuel price shocks (Net P&L Impact $)")
    
    freight_pcts = [-20, -10, 0, 10, 20]
    fuel_pcts = [-10, 0, 10, 20]
    
    # Generate HTML Table
    table_html = '<table class="styled-table"><thead><tr><th>Fuel ∆ \\ Freight ∆</th>'
    for fp in freight_pcts:
        table_html += f'<th>{fp:+}%</th>'
    table_html += '</tr></thead><tbody>'
    
    for fup in fuel_pcts:
        table_html += f'<tr><td><strong>Fuel {fup:+}%</strong></td>'
        for fp in freight_pcts:
            # Calc
            sim_freight = st.session_state.roi_base_freight * (1 + fp/100)
            sim_fuel = st.session_state.roi_base_fuel * (1 + fup/100)
            
            sim_f_cost = sim_freight * st.session_state.roi_vol * st.session_state.roi_voyages
            sim_fu_cost = sim_fuel * st.session_state.roi_fuel_cons * st.session_state.roi_voy_duration * st.session_state.roi_voyages
            sim_fixed = res["base_breakdown"][2] + res["base_breakdown"][3] + res["base_breakdown"][4]
            sim_total = sim_f_cost + sim_fu_cost + sim_fixed
            
            sim_revenue = st.session_state.roi_scen_revenue_mt * st.session_state.roi_vol * st.session_state.roi_voyages
            sim_profit = sim_revenue - sim_total
            
            sim_impact = sim_profit - res['base_profit']
            
            css_class = "matrix-pos" if sim_impact >= 0 else "matrix-neg"
            sign = "+" if sim_impact >= 0 else ""
            table_html += f'<td class="matrix-val {css_class}">{sign}${sim_impact:,.0f}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # RISK ADJUSTMENT
    # ---------------------------------------------------------
    st.markdown('<div class="section-title">🛡️ RISK-ADJUSTED IMPACT</div>', unsafe_allow_html=True)
    with st.expander("Configure Risk Probabilities", expanded=False):
        cr1, cr2, cr3 = st.columns(3)
        with cr1:
            st.session_state.roi_market_risk = st.slider("Market Volatility Risk (%)", 0.0, 50.0, st.session_state.roi_market_risk, 1.0)
        with cr2:
            st.session_state.roi_fuel_risk = st.slider("Fuel Price Shock Risk (%)", 0.0, 50.0, st.session_state.roi_fuel_risk, 1.0)
        with cr3:
            st.session_state.roi_delay_prob = st.slider("Severe Delay Probability (%)", 0.0, 100.0, st.session_state.roi_delay_prob, 5.0)

