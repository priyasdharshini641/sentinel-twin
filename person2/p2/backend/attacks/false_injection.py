from typing import Any, Dict, Optional, Set, Tuple
from backend.attacks.base_attack import BaseAttack
from backend.models.telemetry import Telemetry

SUPPORTED_SENSORS: Set[str] = {
    "temperature",
    "humidity",
    "solar_radiation",
    "cooling_load",
    "power_consumption",
    "water_flow",
    "tank_level",
    "pump_speed",
    "pressure",
}

# Physical sanity bounds (min, max) for continuous climate/cooling sensors
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

# Default reference step sizes per sensor for nominal intensity scaling
DEFAULT_SENSOR_SCALES: Dict[str, float] = {
    "temperature": 10.0,       # 10.0 °C per 1.0 intensity
    "humidity": 20.0,          # 20.0 % per 1.0 intensity
    "solar_radiation": 200.0,  # 200.0 W/m² per 1.0 intensity
    "cooling_load": 10.0,      # 10.0 kW per 1.0 intensity
    "power_consumption": 10.0, # 10.0 kW per 1.0 intensity
    "water_flow": 20.0,        # 20.0 L/min per 1.0 intensity
    "tank_level": 20.0,        # 20.0 % per 1.0 intensity
    "pump_speed": 25.0,        # 25.0 % per 1.0 intensity
    "pressure": 1.5,           # 1.5 bar per 1.0 intensity
}


class FalseInjection(BaseAttack):
    """False Data Injection Attack (P2 Red Team Module).

    Manipulates a single target sensor telemetry value while leaving
    all other telemetry fields completely unchanged.

    Guardrails:
    - Never mutates ground_truth (always outputs a new Telemetry object).
    - Preserves untargeted fields exactly.
    - Attack configuration is kept internal and never injected into Telemetry.
    - No defensive anomaly checks, detection simulation, or risk scoring.
    """

    def __init__(
        self,
        target: Optional[str] = None,
        target_field: Optional[str] = None,
        intensity: float = 1.0,
        value: Optional[float] = None,
        offset: Optional[float] = None,
        direction: float = -1.0,
        clip_bounds: bool = True,
        active: bool = True,
        **kwargs: Any,
    ) -> None:
        resolved_target = target or target_field
        if not resolved_target:
            raise ValueError(
                "A target sensor must be specified (e.g. target='temperature')."
            )

        if resolved_target not in SUPPORTED_SENSORS:
            raise ValueError(
                f"Target sensor '{resolved_target}' is not supported by FalseInjection. "
                f"Supported sensors: {sorted(SUPPORTED_SENSORS)}"
            )

        super().__init__(
            name="FALSE_INJECTION",
            target_field=resolved_target,
            intensity=intensity,
            active=active,
            value=value,
            offset=offset,
            direction=direction,
            clip_bounds=clip_bounds,
            **kwargs,
        )
        self.target = resolved_target
        self.value = value
        self.offset = offset
        self.direction = direction
        self.clip_bounds = clip_bounds

    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        """Applies single-sensor false data injection without modifying ground_truth."""
        gt_val = float(getattr(ground_truth, self.target))

        if self.value is not None:
            # Shift towards target value proportional to intensity
            target_val = float(self.value)
            manipulated = gt_val + (target_val - gt_val) * self.intensity
        elif self.offset is not None:
            # Shift by explicit offset scaled by intensity
            manipulated = gt_val + (float(self.offset) * self.intensity)
        else:
            # Default shift using sensor reference scale and direction
            scale = DEFAULT_SENSOR_SCALES[self.target]
            manipulated = gt_val + (self.direction * self.intensity * scale)

        # Enforce physical sanity bounds where configured
        if self.clip_bounds and self.target in SENSOR_BOUNDS:
            min_bound, max_bound = SENSOR_BOUNDS[self.target]
            manipulated = max(min_bound, min(max_bound, manipulated))

        manipulated = round(manipulated, 4)

        # Return a fresh Telemetry instance with only the target sensor altered
        return ground_truth.copy_with(**{self.target: manipulated})
