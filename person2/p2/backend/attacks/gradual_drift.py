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

# Physical sanity bounds (min, max)
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

# Default drift rate per reading when intensity=1.0
DEFAULT_DRIFT_RATES: Dict[str, float] = {
    "temperature": 0.75,       # °C per step
    "humidity": 1.5,           # % per step
    "solar_radiation": 15.0,   # W/m² per step
    "cooling_load": 0.5,       # kW per step
    "power_consumption": 0.5,  # kW per step
    "water_flow": 1.5,         # L/min per step
    "tank_level": 1.0,         # % per step
    "pump_speed": 2.0,         # % per step
    "pressure": 0.1,           # bar per step
}


class GradualDrift(BaseAttack):
    """Gradual Drift Attack (P2 Red Team Module).

    Gradually manipulates a single target sensor telemetry value across
    successive readings by accumulating a drift bias per apply() call.

    Guardrails:
    - Never mutates ground_truth (always returns a new Telemetry object).
    - Preserves untargeted fields exactly.
    - Attack state (accumulated drift, step count) is maintained internally
      and never injected into Telemetry.
    - reset() restores internal state to pristine baseline.
    - No defense/detection, anomaly flags, or risk scores.
    """

    def __init__(
        self,
        target: Optional[str] = None,
        target_field: Optional[str] = None,
        drift_rate: Optional[float] = None,
        intensity: float = 1.0,
        direction: float = -1.0,
        final_value: Optional[float] = None,
        max_drift: Optional[float] = None,
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
                f"Target sensor '{resolved_target}' is not supported by GradualDrift. "
                f"Supported sensors: {sorted(SUPPORTED_SENSORS)}"
            )

        super().__init__(
            name="GRADUAL_DRIFT",
            target_field=resolved_target,
            intensity=intensity,
            active=active,
            drift_rate=drift_rate,
            direction=direction,
            final_value=final_value,
            max_drift=max_drift,
            clip_bounds=clip_bounds,
            **kwargs,
        )
        self.target = resolved_target
        self.drift_rate = drift_rate
        self.direction = direction
        self.final_value = final_value
        self.max_drift = max_drift
        self.clip_bounds = clip_bounds

        # Internal state tracking successive readings
        self.steps: int = 0
        self.accumulated_drift: float = 0.0

    def reset(self) -> None:
        """Restores internal attack state to initial baseline."""
        self.steps = 0
        self.accumulated_drift = 0.0

    def get_metadata(self) -> Dict[str, Any]:
        """Returns internal attack configuration and execution state.

        Guaranteed separate from Telemetry objects.
        """
        base_meta = super().get_metadata()
        base_meta.update(
            {
                "steps": self.steps,
                "accumulated_drift": round(self.accumulated_drift, 4),
                "drift_rate": self.drift_rate,
                "direction": self.direction,
                "final_value": self.final_value,
                "max_drift": self.max_drift,
            }
        )
        return base_meta

    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        """Applies gradual drift over successive readings without mutating ground_truth."""
        gt_val = float(getattr(ground_truth, self.target))

        # Determine effective step drift
        base_rate = (
            float(self.drift_rate)
            if self.drift_rate is not None
            else DEFAULT_DRIFT_RATES[self.target]
        )
        step_increment = self.direction * base_rate * self.intensity

        # Advance internal state
        self.steps += 1
        self.accumulated_drift += step_increment

        # Cap total drift if max_drift is specified
        if self.max_drift is not None:
            max_d = abs(float(self.max_drift))
            if self.direction < 0:
                self.accumulated_drift = max(-max_d, self.accumulated_drift)
            else:
                self.accumulated_drift = min(max_d, self.accumulated_drift)

        manipulated = gt_val + self.accumulated_drift

        # Cap at final_value if specified
        if self.final_value is not None:
            if self.direction < 0:
                manipulated = max(float(self.final_value), manipulated)
            else:
                manipulated = min(float(self.final_value), manipulated)

        # Enforce physical sanity bounds
        if self.clip_bounds and self.target in SENSOR_BOUNDS:
            min_b, max_b = SENSOR_BOUNDS[self.target]
            manipulated = max(min_b, min(max_b, manipulated))

        manipulated = round(manipulated, 4)

        return ground_truth.copy_with(**{self.target: manipulated})
