import json
import csv
import io

def export_report_json(report: dict) -> str:
    """Exports structured report dictionary to pretty-printed JSON string."""
    # Convert non-serializable elements if any
    clean_report = json.loads(json.dumps(report, default=str))
    return json.dumps(clean_report, indent=2)

def export_report_csv(report: dict) -> str:
    """Exports key metrics, executive summary, and key intelligence from report into CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["OPTIFREIGHT MARITIME INTELLIGENCE REPORT"])
    writer.writerow(["Report Title", report.get("title", "")])
    writer.writerow(["Report Period", report.get("period", "")])
    writer.writerow(["Generated At", report.get("generated_at", "")])
    writer.writerow(["Data Mode", report.get("mode", "")])
    writer.writerow([])
    
    # KPIs
    writer.writerow(["KEY PERFORMANCE INDICATORS"])
    writer.writerow(["Metric", "Value", "Data Status"])
    for k, v in report.get("kpis", {}).items():
        writer.writerow([k.replace("_", " ").upper(), v.get("val", ""), v.get("status", "")])
    writer.writerow([])
    
    # Executive Summary
    writer.writerow(["EXECUTIVE SUMMARY"])
    for section, content in report.get("executive_summary", {}).items():
        writer.writerow([section.replace("_", " ").title(), content])
    writer.writerow([])
    
    # Key Intelligence
    writer.writerow(["KEY INTELLIGENCE DETAILS"])
    for module_name, details in report.get("key_intelligence", {}).items():
        writer.writerow([f"--- {module_name.replace('_', ' ').upper()} ---"])
        for metric, val in details.items():
            if metric != "status":
                writer.writerow([metric.replace("_", " ").title(), val])
        writer.writerow(["Status", details.get("status", "")])
        writer.writerow([])

    # Data Sources
    writer.writerow(["DATA SOURCES TRANSPARENCY"])
    writer.writerow(["Source Name", "Provider", "Status", "Last Updated"])
    for ds in report.get("data_sources", []):
        writer.writerow([ds.get("name"), ds.get("source"), ds.get("status"), ds.get("updated")])
    writer.writerow([])
    
    # Historical Time-Series Data (7, 30, Custom Range)
    writer.writerow(["HISTORICAL TIME-SERIES DATA"])
    chart_data = report.get("chart_data", {})
    dates = chart_data.get("dates", [])
    prices = chart_data.get("historical_prices", [])
    
    writer.writerow(["Date", "Freight Rate ($/MT)"])
    for d, p in zip(dates, prices):
        writer.writerow([d, p])
        
    return output.getvalue()
