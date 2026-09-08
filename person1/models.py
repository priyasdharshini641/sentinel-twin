import sys
from pathlib import Path

try:
    from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS, VALID_PUMP_STATUS
except ImportError:
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS, VALID_PUMP_STATUS

__all__ = ["Telemetry", "FROZEN_TELEMETRY_FIELDS", "VALID_PUMP_STATUS"]

