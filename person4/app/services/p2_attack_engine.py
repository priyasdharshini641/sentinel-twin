"""
SENTINEL TWIN — P2 Red Team Attack Engine
Role: P2 Service Interface (Included for complete standalone P4 integration)

Takes ground truth Telemetry and applies cyber-physical spoofing attacks:
1. False Data Injection (FDI): Step-function abrupt offset.
2. Gradual Drift: Linear stealth ramp that sneaks under traditional statistical thresholds.
3. Coordinated Attack: Simultaneously spoofs multiple correlated sensors to look individually plausible.
4. Freeze Attack: Freezes sensor at stale value despite ongoing physical fluctuations.
"""

import copy
import random
from typing import Dict, Any, List
from app.models.telemetry import Telemetry, AttackType, AttackLaunchRequest


class AttackEngineService:
    """
    Manages active red-team attack state and transforms Ground Truth into Reported Telemetry.
    """

    def __init__(self):
        self.is_active: bool = False
        self.attack_type: AttackType = AttackType.COORDINATED
        self.target_sensors: List[str] = ["temperature", "solar_radiation", "cooling_load"]
        self.intensity: float = 0.75
        self.stealth: bool = True
        self.elapsed_seconds: float = 0.0
        self.duration_seconds: float = 0.0

        # Stateful attack accumulators
        self.drift_offset: float = 0.0
        self.frozen_values: Dict[str, Any] = {}

    def launch_attack(self, request: AttackLaunchRequest) -> Dict[str, Any]:
        """Activate an attack scenario with configured parameters."""
        self.is_active = True
        self.attack_type = request.attack_type
        self.target_sensors = request.target_sensors
        self.intensity = request.intensity
        self.stealth = request.stealth
        self.elapsed_seconds = 0.0
        self.duration_seconds = request.duration_seconds or 0.0
        self.drift_offset = 0.0
        self.frozen_values = {}

        return {
            "status": "ATTACK_LAUNCHED",
            "attack_type": self.attack_type.value,
            "target_sensors": self.target_sensors,
            "intensity": self.intensity,
            "stealth": self.stealth
        }

    def stop_attack(self) -> Dict[str, Any]:
        """Halt any ongoing attack and return system to baseline."""
        was_active = self.is_active
        self.is_active = False
        self.drift_offset = 0.0
        self.frozen_values.clear()

        return {
            "status": "ATTACK_STOPPED",
            "message": "Attack terminated. Telemetry restored to ground truth." if was_active else "No active attack was running."
        }

    def reset(self):
        """Reset internal attack engine state."""
        self.stop_attack()

    def apply(self, truth: Telemetry, dt: float = 1.0) -> Telemetry:
        """
        Produce reported telemetry by perturbing ground truth if attack is active.
        """
        if not self.is_active:
            # Clean passthrough
            return copy.deepcopy(truth)

        self.elapsed_seconds += dt

        # Check auto-expiration if duration was configured
        if self.duration_seconds > 0 and self.elapsed_seconds >= self.duration_seconds:
            self.stop_attack()
            return copy.deepcopy(truth)

        # Clone ground truth so we never mutate the pristine original
        rep = copy.deepcopy(truth)

        # ---------------------------------------------------------------------
        # 1. FALSE DATA INJECTION (FDI): Step-function abrupt bias
        # ---------------------------------------------------------------------
        if self.attack_type == AttackType.FDI:
            offset_mag = 8.0 * self.intensity
            if "temperature" in self.target_sensors:
                # Spoof ambient temperature artificially cold (e.g. -8°C offset)
                rep.temperature = round(truth.temperature - offset_mag, 2)
            if "solar_radiation" in self.target_sensors:
                rep.solar_radiation = round(max(0.0, truth.solar_radiation - 350.0 * self.intensity), 1)
            if "cooling_load" in self.target_sensors:
                rep.cooling_load = round(max(0.5, truth.cooling_load - 12.0 * self.intensity), 2)
            if "water_flow" in self.target_sensors:
                rep.water_flow = round(truth.water_flow + 60.0 * self.intensity, 1)
            if "tank_level" in self.target_sensors:
                rep.tank_level = round(min(100.0, truth.tank_level + 25.0 * self.intensity), 1)

        # ---------------------------------------------------------------------
        # 2. GRADUAL DRIFT: Smooth linear ramp that avoids sudden jump alarms
        # ---------------------------------------------------------------------
        elif self.attack_type == AttackType.DRIFT:
            drift_rate = 0.15 * self.intensity * dt  # Ramp rate per second
            self.drift_offset += drift_rate

            if "temperature" in self.target_sensors:
                rep.temperature = round(truth.temperature - self.drift_offset, 2)
            if "cooling_load" in self.target_sensors:
                rep.cooling_load = round(max(0.5, truth.cooling_load - self.drift_offset * 1.8), 2)
            if "power_consumption" in self.target_sensors:
                rep.power_consumption = round(max(0.5, truth.power_consumption - self.drift_offset * 1.2), 2)

        # ---------------------------------------------------------------------
        # 3. COORDINATED ATTACK: Multi-sensor falsification with masked plausibility
        # ---------------------------------------------------------------------
        elif self.attack_type == AttackType.COORDINATED:
            # Attacker fakes a sudden cool weather front to trick automated HVAC
            # into cutting power while actual building overheats!
            temp_cut = 7.5 * self.intensity
            solar_cut = 320.0 * self.intensity
            load_cut = 10.5 * self.intensity

            rep.temperature = round(truth.temperature - temp_cut, 2)
            rep.solar_radiation = round(max(0.0, truth.solar_radiation - solar_cut), 1)
            rep.cooling_load = round(max(1.0, truth.cooling_load - load_cut), 2)
            # Notice: The attacker cleverly drops temp, solar, and load together,
            # so each individual sensor appears internally reasonable within 0-50°C!
            # BUT: Pump speed and physical water flow remain coupled to the real thermal load,
            # triggering Invariant 01 and Invariant 04!

        # ---------------------------------------------------------------------
        # 4. FREEZE ATTACK: Hold sensor at stale snapshot
        # ---------------------------------------------------------------------
        elif self.attack_type == AttackType.FREEZE:
            for sensor in self.target_sensors:
                if sensor not in self.frozen_values:
                    self.frozen_values[sensor] = getattr(truth, sensor)
                setattr(rep, sensor, self.frozen_values[sensor])

        # ---------------------------------------------------------------------
        # 5. NOISE ATTACK: High variance random walk
        # ---------------------------------------------------------------------
        elif self.attack_type == AttackType.NOISE:
            for sensor in self.target_sensors:
                current_val = getattr(truth, sensor)
                if isinstance(current_val, (int, float)):
                    noise = (random.random() - 0.5) * 10.0 * self.intensity
                    setattr(rep, sensor, round(current_val + noise, 2))

        # Always maintain valid timestamp
        rep.timestamp = truth.timestamp
        return rep

    def get_attack_state(self) -> Dict[str, Any]:
        """Return read-only attack state for API responses."""
        return {
            "is_active": self.is_active,
            "attack_type": self.attack_type.value if self.is_active else None,
            "target_sensors": self.target_sensors if self.is_active else [],
            "intensity": self.intensity if self.is_active else 0.0,
            "stealth": self.stealth if self.is_active else False,
            "elapsed_seconds": round(self.elapsed_seconds, 1) if self.is_active else 0.0
        }
