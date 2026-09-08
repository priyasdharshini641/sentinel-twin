# SENTINEL TWIN — P1 Physical Simulation (Ground Truth)

This module produces the ground-truth physical sensor state of the climate-responsive water and HVAC infrastructure.

## Telemetry Schema (Frozen 11 Fields)

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Telemetry:
    temperature: float          # °C
    humidity: float             # %
    solar_radiation: float      # W/m²
    cooling_load: float         # kW
    power_consumption: float    # kW
    water_flow: float           # L/min
    tank_level: float           # %
    pump_status: str            # ON / OFF
    pump_speed: float           # % (0.0 to 100.0)
    pressure: float             # bar
    timestamp: datetime         # ISO-8601
```

## Physical Invariants Enforced

1. **Hydraulic Coupling**:
   - `pump_status == "OFF"`: `water_flow == 0.0`, `pump_speed == 0.0`, `pressure` at static baseline (~1.05 bar).
   - `pump_status == "ON"`: `water_flow` scales with `pump_speed`, `pressure` rises dynamically with flow friction (2.5 - 4.2 bar).
2. **Thermal & Energy Conservation**:
   - `cooling_load` dynamically responds to ambient temperature and solar irradiance.
   - `power_consumption` strictly accounts for: $\text{base facility power} + \text{chiller electrical power} + \text{pump electrical power}$.
3. **Diurnal Cycles**:
   - Solar irradiance rises and sets smoothly along daylight hours (0 at night, up to ~950 W/m² at solar noon).
   - Ambient temperature lags solar peak by ~2 hours.
   - Humidity inversely correlates with temperature.

## Usage in Code

```python
from simulation import PlantSimulator

# 1. Initialize
sim = PlantSimulator()

# 2. Advance 1 step (1 second dt)
telemetry = sim.step(dt_seconds=1.0)
print(telemetry.to_formatted_row())

# 3. Control actuators
sim.set_pump(status="OFF")
sim.set_pump(status="ON", speed=85.0)

# 4. Serialize
data_dict = telemetry.to_dict()
```

## Running Demo & Tests

```powershell
# Run the live simulation demo:
python demo.py

# Run unit tests:
python -m unittest test_simulation.py
```
