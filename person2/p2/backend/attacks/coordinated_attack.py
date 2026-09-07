from typing import Any, Dict, List, Optional, Set, Tuple
from backend.attacks.base_attack import BaseAttack
from backend.models.telemetry import Telemetry

SCENARIO_THERMAL = "THERMAL"
SCENARIO_PUMP = "PUMP"

THERMAL_COORDINATED_FIELDS: Set[str] = {
    "temperature",
    "solar_radiation",
    "cooling_load",
    "power_consumption",
}

PUMP_COORDINATED_FIELDS: Set[str] = {
    "pump_status",
    "pump_speed",
    "water_flow",
    "pressure",
    "power_consumption",
}

SENSOR_BOUNDS: Dict[str, Tuple[float, float]] = {
    "temperature": (-20.0, 70.0),       # °C
    "humidity": (0.0, 100.0),            # %
    "solar_radiation": (0.0, 1500.0),    # W/m²
    "cooling_load": (0.0, 100.0),        # kW
    "power_consumption": (0.0, 100.0),   # kW
    "water_flow": (0.0, 200.0),          # L/min
    "tank_level": (0.0, 100.0),          # %
    "pump_speed": (0.0, 100.0),          # %
    "pressure": (0.0, 10.0),             # bar
}

# Reference delta vectors for coordinated changes when intensity=1.0 and direction=-1.0 (suppression)
THERMAL_REFERENCE_DELTAS: Dict[str, float] = {
    "temperature": 10.0,       # 10.0 °C
    "solar_radiation": 350.0,  # 350.0 W/m²
    "cooling_load": 8.0,       # 8.0 kW
    "power_consumption": 10.0, # 10.0 kW
}

PUMP_REFERENCE_DELTAS: Dict[str, float] = {
    "pump_speed": 40.0,        # 40.0 %
    "water_flow": 25.0,        # 25.0 L/min
    "pressure": 1.5,           # 1.5 bar
    "power_consumption": 8.0,  # 8.0 kW
}


class CoordinatedAttack(BaseAttack):
    """Coordinated Attack (P2 Red Team Module).

    Manipulates multiple coupled telemetry values simultaneously in a coordinated,
    physically consistent direction rather than modifying an isolated sensor.

    Supported Scenarios:
    1. THERMAL: Coordinates temperature, solar_radiation, cooling_load, and power_consumption.
       - Suppression (direction=-1.0): Masks heatwave / cooling demand downwards.
       - Boost (direction=1.0): Spoofs severe heat and high cooling load upwards.
    2. PUMP: Coordinates pump_status, pump_speed, water_flow, pressure, and power_consumption.
       - Suppression (direction=-1.0): Masks active pumping into a throttled or idle state.
       - Boost (direction=1.0): Spoofs active flow/pressure and hydraulic load from idle.

    Guardrails:
    - Never mutates ground_truth (always outputs a new Telemetry object).
    - Preserves all uncoordinated/unrelated telemetry fields.
    - Attack metadata is kept internal and never injected into Telemetry.
    - No defensive anomaly checks, trust scores, or detection simulation.
    """

    def __init__(
        self,
        scenario: str = SCENARIO_THERMAL,
        intensity: float = 1.0,
        direction: float = -1.0,
        target_pump_status: Optional[str] = None,
        clip_bounds: bool = True,
        active: bool = True,
        **kwargs: Any,
    ) -> None:
        norm_scenario = scenario.upper().strip()
        alias_map = {
            "THERMAL": SCENARIO_THERMAL,
            "COOLING": SCENARIO_THERMAL,
            "THERMAL_COORDINATION": SCENARIO_THERMAL,
            "COOLING_SUPPRESSION": SCENARIO_THERMAL,
            "PUMP": SCENARIO_PUMP,
            "HYDRAULIC": SCENARIO_PUMP,
            "PUMP_COORDINATION": SCENARIO_PUMP,
            "PUMP_SUPPRESSION": SCENARIO_PUMP,
        }

        if norm_scenario not in alias_map:
            raise ValueError(
                f"Unknown scenario '{scenario}'. Supported scenarios: "
                f"{sorted(set(alias_map.values()))}"
            )

        resolved_scenario = alias_map[norm_scenario]
        target_fields = list(
            THERMAL_COORDINATED_FIELDS
            if resolved_scenario == SCENARIO_THERMAL
            else PUMP_COORDINATED_FIELDS
        )

        super().__init__(
            name="COORDINATED_ATTACK",
            target_field=target_fields,
            intensity=intensity,
            active=active,
            scenario=resolved_scenario,
            direction=direction,
            target_pump_status=target_pump_status,
            clip_bounds=clip_bounds,
            **kwargs,
        )

        self.scenario = resolved_scenario
        self.direction = direction
        self.target_pump_status = target_pump_status
        self.clip_bounds = clip_bounds
        self.target_fields = target_fields

    def get_metadata(self) -> Dict[str, Any]:
        """Returns internal attack configuration metadata separate from Telemetry."""
        meta = super().get_metadata()
        meta.update(
            {
                "scenario": self.scenario,
                "direction": self.direction,
                "target_pump_status": self.target_pump_status,
                "target_fields": list(self.target_fields),
            }
        )
        return meta

    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        """Applies coordinated multi-sensor manipulation without mutating ground_truth."""
        changes: Dict[str, Any] = {}

        if self.scenario == SCENARIO_THERMAL:
            # Coordinate: temperature, solar_radiation, cooling_load, power_consumption
            for field, ref_delta in THERMAL_REFERENCE_DELTAS.items():
                current_val = float(getattr(ground_truth, field))
                delta = self.direction * ref_delta * self.intensity
                manipulated = current_val + delta

                if self.clip_bounds and field in SENSOR_BOUNDS:
                    min_b, max_b = SENSOR_BOUNDS[field]
                    manipulated = max(min_b, min(max_b, manipulated))

                changes[field] = round(manipulated, 4)

        elif self.scenario == SCENARIO_PUMP:
            # Coordinate continuous hydraulic fields: pump_speed, water_flow, pressure, power_consumption
            for field, ref_delta in PUMP_REFERENCE_DELTAS.items():
                current_val = float(getattr(ground_truth, field))
                delta = self.direction * ref_delta * self.intensity
                manipulated = current_val + delta

                if self.clip_bounds and field in SENSOR_BOUNDS:
                    min_b, max_b = SENSOR_BOUNDS[field]
                    manipulated = max(min_b, min(max_b, manipulated))

                changes[field] = round(manipulated, 4)

            # Coordinate pump_status
            if self.target_pump_status is not None:
                changes["pump_status"] = self.target_pump_status
            else:
                # If suppressing speed to 0, status becomes OFF; if boosting above 0 from OFF, status becomes ON
                new_speed = changes["pump_speed"]
                if new_speed <= 0.0:
                    changes["pump_status"] = "OFF"
                elif ground_truth.pump_status == "OFF" and self.direction > 0:
                    changes["pump_status"] = "ON"
                else:
                    changes["pump_status"] = ground_truth.pump_status

        return ground_truth.copy_with(**changes)
