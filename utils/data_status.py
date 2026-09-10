from enum import Enum
from datetime import datetime

class DataStatus(Enum):
    LIVE = ("LIVE", "🟢")
    DELAYED = ("DELAYED", "🟡")
    MODEL = ("MODEL", "🔵")
    DEMO = ("DEMO", "⚪")
    ERROR = ("ERROR", "🔴")

def get_status_badge_html(status: DataStatus, updated_at: datetime = None, source: str = None) -> str:
    """Returns HTML for a data status badge with optional timestamp and source."""
    label, icon = status.value
    
    html = f"""<div style="display: flex; flex-direction: column; gap: 4px; font-size: 0.7rem; color: #94a3b8;">
<div style="display: flex; align-items: center; gap: 4px; font-weight: 700; color: #fff;">
<span style="font-size: 0.8rem;">{icon}</span> {label}
</div>"""
    
    if updated_at:
        # Assuming updated_at is UTC, we can format it nicely
        time_str = updated_at.strftime("%H:%M UTC")
        html += f"<div>Updated {time_str}</div>"
        
    if source:
        html += f"<div>Source: {source}</div>"
        
    html += "</div>"
    return html

def get_simple_badge_html(status: DataStatus) -> str:
    """Returns just the simple inline badge (e.g. for small cards)."""
    label, icon = status.value
    return f"""<span style="display: inline-flex; align-items: center; gap: 4px; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1);">
<span>{icon}</span> {label}
</span>"""
