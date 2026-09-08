"""
SENTINEL TWIN — Canonical Telemetry Data Contract
Unified cross-team data model shared by P1 (Simulation), P2 (Attack), P3 (Defense), and P4 (API).
"""

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Dict, Set, Union

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
    """Canonical Frozen Telemetry Data Contract.

    Units:
    - temperature: deg C (Ambient / building temperature)
    - humidity: % (Relative humidity)
    - solar_radiation: W/m2 (External solar irradiance)
    - cooling_load: kW (Thermal cooling demand)
    - power_consumption: kW (Total electrical power)
    - water_flow: L/min (Hydraulic flow rate)
    - tank_level: % (Storage reservoir level)
    - pump_status: 'ON' / 'OFF'
    - pump_speed: % (0.0 to 100.0)
    - pressure: bar (System hydraulic pressure)
    - timestamp: ISO-8601 string or datetime instance

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
    timestamp: Union[str, datetime]

    def __post_init__(self) -> None:
        if self.pump_status not in VALID_PUMP_STATUS:
            raise ValueError(
                f"Invalid pump_status '{self.pump_status}'. Must be one of {sorted(VALID_PUMP_STATUS)}."
            )

        if isinstance(self.timestamp, str):
            try:
                datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid timestamp '{self.timestamp}'. Must be a valid ISO-8601 string."
                ) from exc
        elif isinstance(self.timestamp, datetime):
            pass
        else:
            raise ValueError(
                f"Invalid timestamp '{self.timestamp}'. Must be a valid ISO-8601 string or datetime instance."
            )

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
        ts = self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
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
            "timestamp": ts,
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
            timestamp=data["timestamp"],
        )

    def to_formatted_row(self) -> str:
        """Format as a clean one-line console status."""
        if isinstance(self.timestamp, datetime):
            ts = self.timestamp.strftime("%H:%M:%S")
        else:
            try:
                dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
                ts = dt.strftime("%H:%M:%S")
            except Exception:
                ts = str(self.timestamp)
        return (
            f"[{ts}] Temp: {self.temperature:5.1f}C | Hum: {self.humidity:4.1f}% | "
            f"Solar: {self.solar_radiation:5.1f}W/m2 | CoolLoad: {self.cooling_load:4.1f}kW | "
            f"Power: {self.power_consumption:4.1f}kW | Flow: {self.water_flow:5.1f}L/m | "
            f"Tank: {self.tank_level:4.1f}% | Pump: {self.pump_status:3s} ({self.pump_speed:4.1f}%) | "
            f"Pres: {self.pressure:4.2f}bar"
        )
