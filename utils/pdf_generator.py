import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def build_pdf_report(report: dict) -> bytes:
    """
    Generates a professional B2B Maritime Intelligence PDF document using ReportLab.
    Returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    NAVY_DARK = colors.HexColor("#071426")
    NAVY_CARD = colors.HexColor("#0A1B35")
    CYAN_ACCENT = colors.HexColor("#0088cc") # Printable blue/cyan
    CYAN_TEXT = colors.HexColor("#005588")
    TEXT_DARK = colors.HexColor("#1e293b")
    TEXT_MUTED = colors.HexColor("#64748b")
    BG_LIGHT = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=NAVY_DARK,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=CYAN_ACCENT,
        textTransform='uppercase',
        spaceAfter=12
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=NAVY_DARK,
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bold_label_style = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=NAVY_DARK
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # Format the Period string to include explicit custom range dates if available
    period_str = report.get("period", "")
    c_range = report.get("custom_range")
    if period_str == "Custom Range" and c_range and len(c_range) == 2:
        period_str = f"Custom Range ({c_range[0]} to {c_range[1]})"

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>OPTIFREIGHT</b>", title_style),
            Paragraph(f"<b>REPORT ID:</b> {report.get('id', 'REP-001')}<br/><b>STATUS:</b> {report.get('mode', 'LIVE')}", ParagraphStyle('RightHead', parent=body_style, alignment=2, fontSize=8.5, leading=11))
        ],
        [
            Paragraph("PREDICTIVE MARITIME INTELLIGENCE BRIEF", subtitle_style),
            Paragraph(f"<b>GENERATED:</b> {report.get('generated_date_display', '')}", ParagraphStyle('RightDate', parent=body_style, alignment=2, fontSize=8.5, leading=11))
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=CYAN_ACCENT, spaceBefore=2, spaceAfter=12))

    # 2. Report Overview Box
    meta_data = [
        [
            Paragraph("<b>Report Type:</b>", bold_label_style),
            Paragraph(report.get("title", ""), body_style),
            Paragraph("<b>Evaluation Period:</b>", bold_label_style),
            Paragraph(period_str, body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[80, 190, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Key Indicators (KPI Grid Table)
    story.append(Paragraph("KEY PERFORMANCE INDICATORS", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
    
    kpis = report.get("kpis", {})
    kpi_rows = [
        [
            Paragraph("<b>Metric</b>", bold_label_style),
            Paragraph("<b>Value</b>", bold_label_style),
            Paragraph("<b>Data Status</b>", bold_label_style)
        ]
    ]
    for key, item in kpis.items():
        label = key.replace("_", " ").title()
        val = item.get("val", "N/A")
        status = item.get("status", "LIVE")
        kpi_rows.append([
            Paragraph(label, body_style),
            Paragraph(f"<b>{val}</b>", body_style),
            Paragraph(f"{status}", body_style)
        ])
    
    kpi_table = Table(kpi_rows, colWidths=[200, 180, 160])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('LINEBELOW', (0,0), (-1,0), 1, NAVY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 4. Executive Summary
    story.append(Paragraph("AI EXECUTIVE SUMMARY", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
    
    exec_sum = report.get("executive_summary", {})
    exec_items = [
        ("Market Outlook", exec_sum.get("market_outlook", "")),
        ("Freight Forecast", exec_sum.get("freight_forecast", "")),
        ("Operational Risk", exec_sum.get("operational_risk", "")),
        ("Chartering Recommendation", exec_sum.get("chartering_recommendation", "")),
        ("Potential Opportunity", exec_sum.get("potential_opportunity", ""))
    ]
    
    exec_rows = []
    for title, text in exec_items:
        exec_rows.append([
            Paragraph(f"<b>{title}:</b>", bold_label_style),
            Paragraph(text, body_style)
        ])
    
    exec_table = Table(exec_rows, colWidths=[150, 390])
    exec_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 14))

    # 5. Key Intelligence Breakdown
    story.append(Paragraph("KEY MARITIME INTELLIGENCE", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
    
    key_intel = report.get("key_intelligence", {})
    intel_rows = [
        [
            Paragraph("<b>Domain</b>", bold_label_style),
            Paragraph("<b>Key Findings & Metrics</b>", bold_label_style),
            Paragraph("<b>Source Status</b>", bold_label_style)
        ]
    ]
    
    # Freight
    f_data = key_intel.get("freight_market", {})
    intel_rows.append([
        Paragraph("<b>Freight Market</b>", body_style),
        Paragraph(f"Current: {f_data.get('current_rate')} | Trend: {f_data.get('trend')} | 30d Forecast: {f_data.get('forecast_30d')}", body_style),
        Paragraph(f"{f_data.get('status', 'MODEL')}", body_style)
    ])
    
    # Route
    r_data = key_intel.get("route_intelligence", {})
    intel_rows.append([
        Paragraph("<b>Route Intelligence</b>", body_style),
        Paragraph(f"Route: {r_data.get('recommended_route')}<br/>Distance: {r_data.get('distance_nm')} | Transit: {r_data.get('transit_time')} | Risk: {r_data.get('route_risk')}", body_style),
        Paragraph(f"{r_data.get('status', 'MODEL')}", body_style)
    ])

    # Weather
    w_data = key_intel.get("weather", {})
    intel_rows.append([
        Paragraph("<b>Weather & Marine</b>", body_style),
        Paragraph(f"Singapore Risk: {w_data.get('weather_risk')} ({w_data.get('singapore_temp')}, {w_data.get('singapore_wind')})<br/>Marine State: {w_data.get('marine_conditions')}", body_style),
        Paragraph(f"{w_data.get('status', 'LIVE')}", body_style)
    ])

    # Fuel
    fuel_data = key_intel.get("fuel", {})
    intel_rows.append([
        Paragraph("<b>Bunker Fuel</b>", body_style),
        Paragraph(f"VLSFO Price: {fuel_data.get('vlsfo_price')} (Trend: {fuel_data.get('trend')})", body_style),
        Paragraph(f"{fuel_data.get('status', 'DEMO')}", body_style)
    ])

    # Chartering
    c_data = key_intel.get("chartering", {})
    intel_rows.append([
        Paragraph("<b>AI Chartering</b>", body_style),
        Paragraph(f"Action: <b>{c_data.get('action')}</b> (Confidence: {c_data.get('confidence')})<br/>Expected Savings: {c_data.get('savings')}<br/><i>{c_data.get('reason')}</i>", body_style),
        Paragraph(f"{c_data.get('status', 'MODEL')}", body_style)
    ])

    intel_table = Table(intel_rows, colWidths=[120, 310, 110])
    intel_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(intel_table)
    story.append(Spacer(1, 14))

    # 6. Data Sources Transparency Table
    story.append(Paragraph("DATA SOURCES & TRANSPARENCY", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
    
    ds_rows = [
        [
            Paragraph("<b>Data Feed / Module</b>", bold_label_style),
            Paragraph("<b>Provider / Mechanism</b>", bold_label_style),
            Paragraph("<b>Status</b>", bold_label_style),
            Paragraph("<b>Last Updated</b>", bold_label_style)
        ]
    ]
    for ds in report.get("data_sources", []):
        ds_rows.append([
            Paragraph(ds.get("name", ""), body_style),
            Paragraph(ds.get("source", ""), body_style),
            Paragraph(f"<b>{ds.get('status', '')}</b>", body_style),
            Paragraph(ds.get("updated", ""), body_style)
        ])
    
    ds_table = Table(ds_rows, colWidths=[150, 190, 90, 110])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(ds_table)
    story.append(Spacer(1, 20))
    
    # 7. Historical Time-Series Data (Appended Table for custom ranges / 7d / 30d)
    chart_data = report.get("chart_data", {})
    ts_dates = chart_data.get("dates", [])
    ts_prices = chart_data.get("historical_prices", [])
    
    if ts_dates and ts_prices:
        story.append(Paragraph("HISTORICAL DATA LOG", section_header_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
        
        ts_rows = [
            [
                Paragraph("<b>Date</b>", bold_label_style),
                Paragraph("<b>Freight Rate ($/MT)</b>", bold_label_style)
            ]
        ]
        
        # Limit rows if it's too huge, but they want the data
        for d, p in zip(ts_dates, ts_prices):
            ts_rows.append([
                Paragraph(d, body_style),
                Paragraph(f"${p:,.2f}", body_style)
            ])
            
        ts_table = Table(ts_rows, colWidths=[270, 270])
        ts_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(ts_table)
        story.append(Spacer(1, 20))

    # Footer Notice
    footer_text = (
        "OptiFreight Predictive Maritime Intelligence Platform | Smart India Hackathon (SIH 2026)<br/>"
        "Confidential Intelligence Brief — Generated for Executive Decision Support."
    )
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=body_style, alignment=1, textColor=TEXT_MUTED, fontSize=7.5, leading=10)))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
