"""
SENTINEL TWIN — P2 Red Team Attack Engine Integration Adapter
Connects P4 API orchestrator to the official P2 Attack Engine:
backend.attacks.controller.AttackController
"""

from typing import Dict, Any, List, Optional
from app.models.telemetry import Telemetry, AttackType, AttackLaunchRequest, CustomAttackRequest
from backend.attacks.controller import AttackController
from backend.attacks.pump_flow_attack import (
    SCENARIO_PUMP_OFF_HIGH_FLOW,
    SCENARIO_PUMP_ON_LOW_ENERGY,
)
from backend.attacks.coordinated_attack import (
    SCENARIO_THERMAL,
    SCENARIO_PUMP,
)


class AttackEngineService:
    """Adapter wrapping official P2 AttackController for P4 system pipeline."""

    def __init__(self):
        self.controller: AttackController = AttackController()
        self._attack_type_str: str = "coordinated"
        self._target_sensors: List[str] = ["temperature", "solar_radiation", "cooling_load"]
        self._intensity: float = 0.75
        self._stealth: bool = True
        self._duration_seconds: Optional[int] = None
        self._elapsed_seconds: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.controller.active

    @property
    def active(self) -> bool:
        return self.controller.active

    @property
    def attack_type(self) -> AttackType:
        try:
            return AttackType(self._attack_type_str)
        except Exception:
            return AttackType.COORDINATED

    def launch_attack(self, request: AttackLaunchRequest) -> Dict[str, Any]:
        """Activate an attack scenario using the official P2 AttackController."""
        raw_type = request.attack_type.value if hasattr(request.attack_type, "value") else str(request.attack_type)
        self._attack_type_str = raw_type
        self._target_sensors = list(request.target_sensors)
        self._intensity = request.intensity
        self._stealth = request.stealth
        self._duration_seconds = request.duration_seconds
        self._elapsed_seconds = 0.0

        target = self._target_sensors[0] if self._target_sensors else "temperature"

        config: Dict[str, Any] = {
            "active": True,
            "intensity": request.intensity,
        }

        norm_type = raw_type.lower()
        if norm_type in ["fdi", "false_injection"]:
            config["type"] = "FALSE_INJECTION"
            config["target"] = target
            config["intensity"] = request.intensity
        elif norm_type in ["drift", "gradual_drift"]:
            config["type"] = "GRADUAL_DRIFT"
            config["target"] = target
            config["rate"] = 0.5 * max(0.1, request.intensity)
        elif norm_type in ["coordinated", "coordinated_attack"]:
            config["type"] = "COORDINATED_ATTACK"
            has_pump_sensor = any(s in ["pump_status", "pump_speed", "water_flow", "pressure"] for s in self._target_sensors)
            config["scenario"] = SCENARIO_PUMP if has_pump_sensor else SCENARIO_THERMAL
            config["direction"] = -1.0
            config["intensity"] = request.intensity
        elif norm_type in ["pump", "pump_flow", "pump_flow_attack"]:
            config["type"] = "PUMP_FLOW_ATTACK"
            config["scenario"] = SCENARIO_PUMP_OFF_HIGH_FLOW
            config["intensity"] = request.intensity
        elif norm_type == "freeze":
            config["type"] = "FALSE_INJECTION"
            config["target"] = target
            config["offset"] = 0.0
            config["intensity"] = request.intensity
        else:
            config["type"] = "FALSE_INJECTION"
            config["target"] = target
            config["intensity"] = request.intensity

        self.controller.configure(config)
        self.controller.start()

        return {
            "status": "ATTACK_LAUNCHED",
            "attack_type": self._attack_type_str,
            "target_sensors": self._target_sensors,
            "intensity": self._intensity,
            "stealth": self._stealth,
        }

    def launch_custom_attack(self, request: CustomAttackRequest) -> Dict[str, Any]:
        """Custom stage attack with arbitrary sensor offsets."""
        self._attack_type_str = "coordinated"
        self._target_sensors = list(request.target_sensors.keys())
        self._intensity = 1.0
        self._stealth = getattr(request, "stealth_mode", getattr(request, "stealth", True))


        first_target = self._target_sensors[0] if self._target_sensors else "temperature"
        first_offset = request.target_sensors.get(first_target, -8.0)

        config = {
            "type": "FALSE_INJECTION",
            "active": True,
            "target": first_target,
            "offset": first_offset,
            "intensity": 1.0,
        }
        self.controller.configure(config)
        self.controller.start()

        return {
            "status": "ATTACK_LAUNCHED",
            "attack_type": "custom",
            "target_sensors": self._target_sensors,
            "intensity": 1.0,
            "stealth": self._stealth,
            "hacker_alias": getattr(request, "hacker_alias", "Judge Hacker"),
        }



    def stop_attack(self) -> Dict[str, Any]:
        """Halt any ongoing attack and return system to baseline."""
        was_active = self.controller.active
        self.controller.stop()
        return {
            "status": "ATTACK_STOPPED",
            "message": "Attack terminated. Telemetry restored to ground truth." if was_active else "No active attack was running."
        }

    def reset(self):
        """Reset internal attack engine state."""
        self.controller.reset()
        self.controller.stop()
        self._elapsed_seconds = 0.0

    def apply(self, truth: Telemetry, dt: float = 1.0) -> Telemetry:
        """Apply attack transformation to ground truth using P2 AttackController."""
        if not self.controller.active:
            return truth.copy_with()

        self._elapsed_seconds += dt
        if self._duration_seconds and self._elapsed_seconds >= self._duration_seconds:
            self.stop_attack()
            return truth.copy_with()

        return self.controller.apply(truth)

    def get_attack_state(self) -> Dict[str, Any]:
        """Export serialized attack state for API responses and frontend."""
        return {
            "is_active": self.controller.active,
            "active": self.controller.active,
            "attack_type": self._attack_type_str if self.controller.active else "NONE",
            "type": self._attack_type_str if self.controller.active else "NONE",
            "target_sensors": self._target_sensors if self.controller.active else [],
            "intensity": self._intensity if self.controller.active else 0.0,
            "stealth": self._stealth,
            "controller_metadata": self.controller.get_metadata(),
        }
