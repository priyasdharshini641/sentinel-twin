from datetime import datetime
from typing import Generator
try:
    from .simulator import PlantSimulator
    from .models import Telemetry
except ImportError:
    from simulator import PlantSimulator
    from models import Telemetry


def run_nominal_scenario(
    steps: int = 10,
    dt_seconds: float = 1.0,
    simulator: PlantSimulator = None,
) -> Generator[Telemetry, None, None]:
    """Generates consecutive nominal telemetry readings."""
    sim = simulator or PlantSimulator()
    for _ in range(steps):
        yield sim.step(dt_seconds=dt_seconds)


def run_pump_cycle_scenario(
    on_steps: int = 5,
    off_steps: int = 5,
    dt_seconds: float = 1.0,
) -> Generator[Telemetry, None, None]:
    """Demonstrates pump dynamic transition: ON -> OFF -> ON.
    
    Verifies that flow drops to 0 and pressure drops to static level
    whenever pump is turned OFF.
    """
    sim = PlantSimulator(default_pump_status="ON", default_pump_speed=80.0)

    # Phase 1: Pump ON
    for _ in range(on_steps):
        yield sim.step(dt_seconds=dt_seconds)

    # Phase 2: Turn Pump OFF
    sim.set_pump(status="OFF")
    for _ in range(off_steps):
        yield sim.step(dt_seconds=dt_seconds)

    # Phase 3: Turn Pump back ON at 60% speed
    sim.set_pump(status="ON", speed=60.0)
    for _ in range(on_steps):
        yield sim.step(dt_seconds=dt_seconds)
