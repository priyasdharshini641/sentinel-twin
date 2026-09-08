from typing import Any, Dict, Optional, Set, Tuple
from backend.attacks.base_attack import BaseAttack
from backend.models.telemetry import Telemetry

PUMP_RELATED_FIELDS: Set[str] = {
    "pump_status",
    "pump_speed",
    "water_flow",
    "pressure",
    "power_consumption",
}

SENSOR_BOUNDS: Dict[str, Tuple[float, float]] = {
    "water_flow": (0.0, 200.0),          # L/min
    "pressure": (0.0, 10.0),             # bar
    "power_consumption": (0.0, 100.0),   # kW
    "pump_speed": (0.0, 100.0),          # %
}

# Standard scenarios
SCENARIO_PUMP_OFF_HIGH_FLOW = "PUMP_OFF_HIGH_FLOW"
SCENARIO_PUMP_ON_LOW_ENERGY = "PUMP_ON_LOW_ENERGY"
SCENARIO_CUSTOM = "CUSTOM"


class PumpFlowAttack(BaseAttack):
    """Pump / Flow Actuator Attack (P2 Red Team Module).

    Manipulates multiple pump and hydraulic telemetry fields
    (pump_status, pump_speed, water_flow, pressure, power_consumption)
    to create a deceptive actuator state.

    Supported Scenarios:
    1. PUMP_OFF_HIGH_FLOW: Pump is reported/confirmed OFF/speed 0, but water_flow
       and pressure are reported high (phantom flow).
    2. PUMP_ON_LOW_ENERGY: Pump is ON and operating, but reported power_consumption
       is abnormally low (stealth consumption / false efficiency).
    3. CUSTOM: User-configured overrides for pump-related fields.

    Guardrails:
    - Never mutates ground_truth (always returns a new Telemetry object).
    - Preserves all non-pump telemetry fields (temperature, humidity, solar, cooling, tank).
    - Attack metadata is kept internal and never injected into Telemetry.
    - No defensive anomaly checks, causal validation, or physical consistency calculations.
    """

    def __init__(
        self,
        scenario: str = SCENARIO_PUMP_OFF_HIGH_FLOW,
        intensity: float = 1.0,
        target_flow: Optional[float] = None,
        target_pressure: Optional[float] = None,
        target_power: Optional[float] = None,
        target_pump_speed: Optional[float] = None,
        target_pump_status: Optional[str] = None,
        force_actuator_state: bool = False,
        active: bool = True,
        **kwargs: Any,
    ) -> None:
        norm_scenario = scenario.upper().strip()
        alias_map = {
            "GHOST_FLOW": SCENARIO_PUMP_OFF_HIGH_FLOW,
            "PHANTOM_FLOW": SCENARIO_PUMP_OFF_HIGH_FLOW,
            "PUMP_OFF_HIGH_FLOW": SCENARIO_PUMP_OFF_HIGH_FLOW,
            "LOW_ENERGY": SCENARIO_PUMP_ON_LOW_ENERGY,
            "STEALTH_ENERGY": SCENARIO_PUMP_ON_LOW_ENERGY,
            "STEALTH_POWER": SCENARIO_PUMP_ON_LOW_ENERGY,
            "PUMP_ON_LOW_ENERGY": SCENARIO_PUMP_ON_LOW_ENERGY,
            "CUSTOM": SCENARIO_CUSTOM,
        }

        if norm_scenario not in alias_map:
            raise ValueError(
                f"Unknown scenario '{scenario}'. Supported scenarios: "
                f"{sorted(set(alias_map.values()))}"
            )

        resolved_scenario = alias_map[norm_scenario]

        super().__init__(
            name="PUMP_FLOW_ATTACK",
            target_field=list(PUMP_RELATED_FIELDS),
            intensity=intensity,
            active=active,
            scenario=resolved_scenario,
            target_flow=target_flow,
            target_pressure=target_pressure,
            target_power=target_power,
            target_pump_speed=target_pump_speed,
            target_pump_status=target_pump_status,
            force_actuator_state=force_actuator_state,
            **kwargs,
        )

        self.scenario = resolved_scenario
        self.target_flow = target_flow
        self.target_pressure = target_pressure
        self.target_power = target_power
        self.target_pump_speed = target_pump_speed
        self.target_pump_status = target_pump_status
        self.force_actuator_state = force_actuator_state

    def get_metadata(self) -> Dict[str, Any]:
        """Returns internal attack configuration and execution metadata.

        Guaranteed separate from Telemetry objects.
        """
        meta = super().get_metadata()
        meta.update(
            {
                "scenario": self.scenario,
                "target_flow": self.target_flow,
                "target_pressure": self.target_pressure,
                "target_power": self.target_power,
                "target_pump_speed": self.target_pump_speed,
                "target_pump_status": self.target_pump_status,
                "force_actuator_state": self.force_actuator_state,
            }
        )
        return meta

    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        """Applies actuator manipulation without mutating ground_truth."""
        changes: Dict[str, Any] = {}

        if self.scenario == SCENARIO_PUMP_OFF_HIGH_FLOW:
            # Scenario 1: Pump is OFF / idle, but reported flow and pressure are high
            if self.force_actuator_state:
                changes["pump_status"] = "OFF"
                changes["pump_speed"] = 0.0

            # Compute manipulated high flow
            nominal_high_flow = (
                float(self.target_flow)
                if self.target_flow is not None
                else 60.0
            )
            flow = nominal_high_flow * self.intensity
            flow = max(SENSOR_BOUNDS["water_flow"][0], min(SENSOR_BOUNDS["water_flow"][1], flow))
            changes["water_flow"] = round(flow, 4)

            # Compute manipulated high pressure
            nominal_high_pressure = (
                float(self.target_pressure)
                if self.target_pressure is not None
                else 4.2
            )
            pressure = nominal_high_pressure * self.intensity
            pressure = max(
                SENSOR_BOUNDS["pressure"][0], min(SENSOR_BOUNDS["pressure"][1], pressure)
            )
            changes["pressure"] = round(pressure, 4)

        elif self.scenario == SCENARIO_PUMP_ON_LOW_ENERGY:
            # Scenario 2: Pump is ON, but power consumption is reported abnormally low
            if self.force_actuator_state:
                changes["pump_status"] = "ON"

            gt_power = float(ground_truth.power_consumption)
            if self.target_power is not None:
                manipulated_power = gt_power + (float(self.target_power) - gt_power) * self.intensity
            else:
                # Default: reduce power by up to 85% proportional to intensity
                reduction_factor = max(0.05, 1.0 - (0.85 * self.intensity))
                manipulated_power = max(0.5, gt_power * reduction_factor)

            manipulated_power = max(
                SENSOR_BOUNDS["power_consumption"][0],
                min(SENSOR_BOUNDS["power_consumption"][1], manipulated_power),
            )
            changes["power_consumption"] = round(manipulated_power, 4)

        elif self.scenario == SCENARIO_CUSTOM:
            if self.target_pump_status is not None:
                changes["pump_status"] = self.target_pump_status
            if self.target_pump_speed is not None:
                changes["pump_speed"] = round(float(self.target_pump_speed), 4)
            if self.target_flow is not None:
                changes["water_flow"] = round(float(self.target_flow) * self.intensity, 4)
            if self.target_pressure is not None:
                changes["pressure"] = round(float(self.target_pressure) * self.intensity, 4)
            if self.target_power is not None:
                changes["power_consumption"] = round(float(self.target_power), 4)

        return ground_truth.copy_with(**changes)
