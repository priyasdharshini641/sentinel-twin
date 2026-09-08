from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class Telemetry:
    """Frozen 11-field Telemetry schema for SENTINEL TWIN.
    
    Represents the ground-truth physical sensor state of the
    climate-responsive water and HVAC infrastructure.
    """
    temperature: float          # °C (Ambient / building temperature)
    humidity: float             # % (Relative humidity)
    solar_radiation: float      # W/m² (External solar irradiance)
    cooling_load: float         # kW (Thermal cooling demand)
    power_consumption: float    # kW (Total electrical power: HVAC + Pump + Base)
    water_flow: float           # L/min (Hydraulic flow rate)
    tank_level: float           # % (Storage reservoir level)
    pump_status: str            # ON / OFF
    pump_speed: float           # % (0.0 to 100.0)
    pressure: float             # bar (System hydraulic pressure)
    timestamp: datetime         # ISO-8601 (Simulated/UTC timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry to a serializable dictionary with ISO formatted timestamp."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Telemetry":
        """Reconstruct Telemetry from a dictionary."""
        d = dict(data)
        if isinstance(d["timestamp"], str):
            d["timestamp"] = datetime.fromisoformat(d["timestamp"])
        return cls(**d)

    def to_formatted_row(self) -> str:
        """Format as a clean one-line console status."""
        ts = self.timestamp.strftime("%H:%M:%S")
        return (
            f"[{ts}] Temp: {self.temperature:5.1f}C | Hum: {self.humidity:4.1f}% | "
            f"Solar: {self.solar_radiation:5.1f}W/m2 | CoolLoad: {self.cooling_load:4.1f}kW | "
            f"Power: {self.power_consumption:4.1f}kW | Flow: {self.water_flow:5.1f}L/m | "
            f"Tank: {self.tank_level:4.1f}% | Pump: {self.pump_status:3s} ({self.pump_speed:4.1f}%) | "
            f"Pres: {self.pressure:4.2f}bar"
        )
