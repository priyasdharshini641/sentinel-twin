from collections import deque
from datetime import datetime, timedelta
from typing import Optional, List

try:
    from .models import Telemetry
    from .environment import EnvironmentModel
    from .hydraulic_model import HydraulicModel
    from .hvac_model import HVACModel
except ImportError:
    from models import Telemetry
    from environment import EnvironmentModel
    from hydraulic_model import HydraulicModel
    from hvac_model import HVACModel


class PlantSimulator:
    """Core P1 Physical Simulator for SENTINEL TWIN.
    
    Generates realistic, physically-correlated ground-truth sensor telemetry
    adhering strictly to the team's frozen 11-field Telemetry schema.
    
    This simulator models coupled environmental, hydraulic, and HVAC thermodynamics.
    It produces ground_truth that remains uncorrupted and represents true physical reality.
    """

    def __init__(
        self,
        start_time: Optional[datetime] = None,
        default_pump_status: str = "ON",
        default_pump_speed: float = 75.0,
        history_len: int = 120,
        seed: int = 42,
    ):
        self.default_start_time = start_time or datetime(2026, 9, 7, 10, 0, 0)
        self.default_pump_status = default_pump_status
        self.default_pump_speed = default_pump_speed
        self.history_len = history_len
        self.seed = seed

        self.history: deque[Telemetry] = deque(maxlen=history_len)
        self._init_simulation()

    def _init_simulation(self):
        """Initializes or resets all physical subsystem models."""
        self.sim_time = self.default_start_time
        self.pump_status = self.default_pump_status
        self.pump_speed = self.default_pump_speed

        self.env = EnvironmentModel(seed=self.seed)
        self.hydraulic = HydraulicModel(seed=self.seed + 1)
        self.hvac = HVACModel(seed=self.seed + 2)

        # Generate the initial baseline reading
        self.current_telemetry = self._compute_telemetry(dt_seconds=0.0)
        self.history.clear()
        self.history.append(self.current_telemetry)

    def _compute_telemetry(self, dt_seconds: float) -> Telemetry:
        """Internal physics step computing all coupled subsystem telemetry."""
        # 1. Environmental physics (solar, ambient temp, humidity)
        temp, hum, solar = self.env.calculate(self.sim_time)

        # 2. Hydraulic physics (pump, flow, pressure, tank level, pump power)
        flow, tank, eff_status, eff_speed, pres, pump_power = self.hydraulic.calculate(
            pump_status=self.pump_status,
            pump_speed_setpoint=self.pump_speed,
            dt_seconds=dt_seconds,
        )

        # 3. HVAC thermal physics (cooling load and total facility power)
        cool_load, total_power = self.hvac.calculate(
            temperature=temp,
            solar_radiation=solar,
            pump_power=pump_power,
        )

        return Telemetry(
            temperature=temp,
            humidity=hum,
            solar_radiation=solar,
            cooling_load=cool_load,
            power_consumption=total_power,
            water_flow=flow,
            tank_level=tank,
            pump_status=eff_status,
            pump_speed=eff_speed,
            pressure=pres,
            timestamp=self.sim_time,
        )

    def step(self, dt_seconds: float = 1.0) -> Telemetry:
        """Advances the simulation clock by dt_seconds and returns the next ground-truth Telemetry."""
        self.sim_time += timedelta(seconds=dt_seconds)
        self.current_telemetry = self._compute_telemetry(dt_seconds=dt_seconds)
        self.history.append(self.current_telemetry)
        return self.current_telemetry

    def set_pump(self, status: Optional[str] = None, speed: Optional[float] = None) -> None:
        """Actuator control interface: adjust pump status and operating speed."""
        if status is not None:
            norm = status.upper().strip()
            self.pump_status = "ON" if norm == "ON" else "OFF"
        if speed is not None:
            self.pump_speed = max(0.0, min(100.0, float(speed)))

    def reset(
        self,
        start_time: Optional[datetime] = None,
        seed: Optional[int] = None,
    ) -> Telemetry:
        """Resets the simulator back to its starting state."""
        if start_time is not None:
            self.default_start_time = start_time
        if seed is not None:
            self.seed = seed
        self._init_simulation()
        return self.current_telemetry

    def get_telemetry(self) -> Telemetry:
        """Returns the most recent ground-truth telemetry reading."""
        return self.current_telemetry

    def get_history(self) -> List[Telemetry]:
        """Returns the rolling history buffer of recent ground-truth readings."""
        return list(self.history)
