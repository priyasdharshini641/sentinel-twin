"""
SENTINEL TWIN — P1 Physical Ground Truth Simulator
Role: P1 Service Interface (Included for complete standalone P4 integration)

Simulates the true physics of a climate-responsive smart facility:
- Ambient temperature & humidity driven by solar diurnal cycle
- Chilled water thermal cooling dynamics (Q = m * Cp * deltaT)
- Hydraulic pumping loop with Bernoulli pressure-flow coupling
- Electrical energy consumption adhering to motor affinity laws
"""

import math
from datetime import datetime, timezone
from app.models.telemetry import Telemetry


class SimulationService:
    """
    Simulates high-fidelity physical ground truth across 10 physical variables + timestamp.
    Guarantees that all physical invariants hold true in the uncorrupted state.
    """

    def __init__(self):
        self.time_seconds: float = 0.0
        # Physical plant parameters
        self.base_temp: float = 32.0          # °C midday baseline
        self.setpoint_temp: float = 23.0      # °C target indoor comfort
        self.building_ua: float = 2.4         # Thermal transfer coefficient (kW/°C)
        self.solar_absorption: float = 0.015  # Solar thermal absorption fraction
        self.tank_capacity: float = 5000.0    # Liters
        self.current_tank_liters: float = 3800.0

    def reset(self):
        """Reset simulation clock and state to nominal baseline."""
        self.time_seconds = 0.0
        self.current_tank_liters = 3800.0

    def step(self, dt: float = 1.0) -> Telemetry:
        """
        Advance simulation by dt seconds and return fresh uncorrupted Ground Truth Telemetry.
        """
        self.time_seconds += dt
        t = self.time_seconds

        # 1. Solar Radiation (Diurnal bell curve + mild natural noise)
        # Periodic cycle over a virtual day or demo cycle (period = 180s for lively demo dynamics)
        cycle_phase = (t % 180.0) / 180.0 * 2.0 * math.pi
        solar_base = max(0.0, math.sin(cycle_phase))
        solar_radiation = round(solar_base * 900.0 + 15.0 * math.sin(t * 0.3), 1)

        # 2. Ambient Temperature (Lags solar irradiance slightly)
        thermal_lag_phase = cycle_phase - 0.2
        temperature = round(
            self.base_temp + 6.0 * math.sin(thermal_lag_phase) + 0.3 * math.sin(t * 0.5),
            2
        )

        # 3. Ambient Humidity (Inverse psychrometric correlation with temperature)
        # High heat = lower relative humidity
        humidity = round(
            max(20.0, min(95.0, 75.0 - (temperature - 26.0) * 2.8 + 1.2 * math.cos(t * 0.2))),
            1
        )

        # 4. Cooling Load (Thermodynamic demand from ambient delta-T + solar load)
        delta_t = max(0.0, temperature - self.setpoint_temp)
        cooling_load = round(
            self.building_ua * delta_t + self.solar_absorption * solar_radiation + 1.5,
            2
        )

        # 5. Pump Dynamics (Actuator responds dynamically to cooling demand)
        # Pump speed modulates between 40% and 95% based on cooling load
        pump_status = "ON"
        pump_speed = round(min(100.0, max(35.0, 30.0 + cooling_load * 3.2)), 1)

        # 6. Water Flow (Centrifugal pump flow proportional to speed)
        # Nominal flow: 80 - 220 L/min
        water_flow = round(2.2 * pump_speed + 0.8 * math.sin(t * 0.7), 1)

        # 7. Hydraulic Loop Pressure (Bernoulli: pressure rises with pump speed)
        pressure = round(1.2 + 0.035 * pump_speed + 0.05 * math.sin(t * 0.4), 2)

        # 8. Reserve Tank Level (Hydraulic mass conservation)
        inflow = 120.0 + 10.0 * math.sin(t * 0.1)  # Municipal makeup feed
        outflow = water_flow
        net_flow = (inflow - outflow) * (dt / 60.0)  # L/s to L
        self.current_tank_liters = max(1000.0, min(self.tank_capacity, self.current_tank_liters + net_flow))
        tank_level = round((self.current_tank_liters / self.tank_capacity) * 100.0, 1)

        # 9. Power Consumption (Motor Affinity Laws: P ~ P_idle + chiller_work + pump_speed^3)
        chiller_power = cooling_load * 0.78
        pump_power = 0.4 + 2.8 * math.pow(pump_speed / 100.0, 3)
        aux_power = 0.5
        power_consumption = round(chiller_power + pump_power + aux_power, 2)

        # 10. ISO-8601 Timestamp
        timestamp = datetime.now(timezone.utc)

        return Telemetry(
            temperature=temperature,
            humidity=humidity,
            solar_radiation=solar_radiation,
            cooling_load=cooling_load,
            power_consumption=power_consumption,
            water_flow=water_flow,
            tank_level=tank_level,
            pump_status=pump_status,
            pump_speed=pump_speed,
            pressure=pressure,
            timestamp=timestamp
        )
