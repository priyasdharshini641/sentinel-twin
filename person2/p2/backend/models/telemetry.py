"""
SENTINEL TWIN — P2 Telemetry Model Re-Export
Re-exports the canonical Telemetry dataclass from backend.models.telemetry
to ensure 100% object identity and schema consistency across the entire codebase.
"""

import sys
import importlib.util
from pathlib import Path

root_file = Path(__file__).resolve().parents[4] / "backend" / "models" / "telemetry.py"


if "backend.models.telemetry" in sys.modules and hasattr(sys.modules["backend.models.telemetry"], "Telemetry"):
    _canonical = sys.modules["backend.models.telemetry"]
elif root_file.exists() and root_file != Path(__file__).resolve():
    spec = importlib.util.spec_from_file_location("backend.models.telemetry", str(root_file))
    _canonical = importlib.util.module_from_spec(spec)
    sys.modules["backend.models.telemetry"] = _canonical
    spec.loader.exec_module(_canonical)
else:
    _canonical = None

if _canonical is not None:
    Telemetry = _canonical.Telemetry
    FROZEN_TELEMETRY_FIELDS = _canonical.FROZEN_TELEMETRY_FIELDS
    VALID_PUMP_STATUS = _canonical.VALID_PUMP_STATUS
else:
    raise ImportError("Failed to locate canonical Telemetry model at backend/models/telemetry.py")

__all__ = ["Telemetry", "FROZEN_TELEMETRY_FIELDS", "VALID_PUMP_STATUS"]
