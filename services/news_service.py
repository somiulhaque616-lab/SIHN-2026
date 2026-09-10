from datetime import datetime
from utils.data_status import DataStatus

def get_geopolitical_risk():
    """Returns AI-derived geopolitical risk assessment based on DEMO events."""
    return {
        "status": DataStatus.DEMO,
        "data": {
            "level": "MODERATE",
            "reason": "Simulated events indicate rising tensions in the Red Sea and potential delays in Suez transits.",
            "label": "OptiFreight AI-derived risk assessment"
        },
        "updated_at": datetime.utcnow(),
        "source": "Demo Intelligence"
    }
