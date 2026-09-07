from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Dict, Set

VALID_PUMP_STATUS: Set[str] = {"ON", "OFF"}

FROZEN_TELEMETRY_FIELDS: Set[str] = {
    "temperature",
    "humidity",
    "solar_radiation",
    "cooling_load",
    "power_consumption",
    "water_flow",
    "tank_level",
    "pump_status",
    "pump_speed",
    "pressure",
    "timestamp",
}


@dataclass(frozen=True)
class Telemetry:
    """Frozen Telemetry Data Contract.

    Units:
    - temperature: °C
    - humidity: %
    - solar_radiation: W/m²
    - cooling_load: kW
    - power_consumption: kW
    - water_flow: L/min
    - tank_level: %
    - pump_status: ON/OFF
    - pump_speed: %
    - pressure: bar
    - timestamp: ISO-8601

    Guardrails:
    - Immutable (frozen=True): Prevents in-place tampering of ground truth.
    - Closed schema: Disallows arbitrary attributes or injected attack metadata.
    """

    temperature: float
    humidity: float
    solar_radiation: float
    cooling_load: float
    power_consumption: float
    water_flow: float
    tank_level: float
    pump_status: str
    pump_speed: float
    pressure: float
    timestamp: str

    def __post_init__(self) -> None:
        if self.pump_status not in VALID_PUMP_STATUS:
            raise ValueError(
                f"Invalid pump_status '{self.pump_status}'. Must be one of {sorted(VALID_PUMP_STATUS)}."
            )
        try:
            datetime.fromisoformat(self.timestamp)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid timestamp '{self.timestamp}'. Must be a valid ISO-8601 string."
            ) from exc

    def copy_with(self, **changes: Any) -> "Telemetry":
        """Returns a new Telemetry instance with specified field updates.

        Strictly guarantees the original instance remains unchanged.
        """
        invalid_keys = set(changes.keys()) - FROZEN_TELEMETRY_FIELDS
        if invalid_keys:
            raise ValueError(
                f"Cannot update non-telemetry fields: {invalid_keys}. "
                "Attack metadata must remain separate."
            )
        return replace(self, **changes)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes telemetry into a dictionary with exact contract fields."""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "solar_radiation": self.solar_radiation,
            "cooling_load": self.cooling_load,
            "power_consumption": self.power_consumption,
            "water_flow": self.water_flow,
            "tank_level": self.tank_level,
            "pump_status": self.pump_status,
            "pump_speed": self.pump_speed,
            "pressure": self.pressure,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Telemetry":
        """Instantiates Telemetry from dictionary.

        Rejects incomplete records or extraneous keys (e.g. leaked metadata).
        """
        keys = set(data.keys())
        if keys != FROZEN_TELEMETRY_FIELDS:
            extra = keys - FROZEN_TELEMETRY_FIELDS
            missing = FROZEN_TELEMETRY_FIELDS - keys
            errors = []
            if extra:
                errors.append(f"disallowed extra fields: {sorted(extra)}")
            if missing:
                errors.append(f"missing required fields: {sorted(missing)}")
            raise ValueError(f"Telemetry contract violation: {'; '.join(errors)}")

        return cls(
            temperature=float(data["temperature"]),
            humidity=float(data["humidity"]),
            solar_radiation=float(data["solar_radiation"]),
            cooling_load=float(data["cooling_load"]),
            power_consumption=float(data["power_consumption"]),
            water_flow=float(data["water_flow"]),
            tank_level=float(data["tank_level"]),
            pump_status=str(data["pump_status"]),
            pump_speed=float(data["pump_speed"]),
            pressure=float(data["pressure"]),
            timestamp=str(data["timestamp"]),
        )
