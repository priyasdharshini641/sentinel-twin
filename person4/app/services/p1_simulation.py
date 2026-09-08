"""
SENTINEL TWIN — P1 Physical Ground Truth Simulator
Role: P1 Service Interface (Official Integration with person1 package)

Simulates the true physics of a climate-responsive smart facility:
- Ambient temperature & humidity driven by solar diurnal cycle
- Chilled water thermal cooling dynamics (Q = m * Cp * deltaT)
- Hydraulic pumping loop with Bernoulli pressure-flow coupling
- Electrical energy consumption adhering to motor affinity laws
"""

import os
import sys
from datetime import datetime, timezone
from app.models.telemetry import Telemetry

# Ensure repository root is in python path to access person1 package
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    from person1.simulator import PlantSimulator
except ImportError:
    PlantSimulator = None


class SimulationService:
    """
    Connects to the official P1 PlantSimulator engine from person1/.
    Generates high-fidelity physical ground truth across all 11 fields.
    """

    def __init__(self):
        if PlantSimulator is not None:
            self.sim = PlantSimulator(default_pump_status="ON", default_pump_speed=75.0)
        else:
            self.sim = None

    def reset(self):
        """Reset simulation clock and state to nominal baseline."""
        if self.sim:
            self.sim.reset()

    def step(self, dt: float = 1.0) -> Telemetry:
        """
        Advance simulation by dt seconds using the official P1 physics engine
        and return fresh uncorrupted Ground Truth Telemetry.
        """
        if self.sim:
            p1_tel = self.sim.step(dt_seconds=dt)
            if isinstance(p1_tel, Telemetry):
                return p1_tel
            return Telemetry.from_dict(p1_tel.to_dict())

        else:
            # Fallback nominal
            return Telemetry(
                temperature=28.0,
                humidity=55.0,
                solar_radiation=800.0,
                cooling_load=24.0,
                power_consumption=12.0,
                water_flow=90.0,
                tank_level=75.0,
                pump_status="ON",
                pump_speed=75.0,
                pressure=3.0,
                timestamp=datetime.now(timezone.utc)
            )
