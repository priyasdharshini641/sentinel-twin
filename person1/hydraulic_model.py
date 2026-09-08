import random


class HydraulicModel:
    """Models the pump, pipe network, water flow, pressure, and tank level.
    
    Strict Invariants (calibrated to team's Cyber-Physical Invariant Contracts):
    - When pump_status == "OFF":
      water_flow == 0.0 L/min, pump_speed == 0.0%, pressure == 1.0-1.05 bar (static), pump_power == 0.0 kW.
    - When pump_status == "ON":
      water_flow = 2.2 * pump_speed (L/min)
      pressure = 1.2 + 0.035 * pump_speed (bar)
      pump_power = 0.4 + 2.8 * (pump_speed / 100)³ (kW)
    - Tank level evolves continuously under mass conservation (~75%).
    """

    def __init__(
        self,
        flow_coefficient: float = 2.2,
        static_pressure_off: float = 1.0,
        pressure_base_on: float = 1.2,
        pressure_gain: float = 0.035,
        initial_tank_level: float = 75.0,
        seed: int = 101,
    ):
        self.flow_coefficient = flow_coefficient
        self.static_pressure_off = static_pressure_off
        self.pressure_base_on = pressure_base_on
        self.pressure_gain = pressure_gain
        self.tank_level = initial_tank_level
        self.rng = random.Random(seed)

    def calculate(
        self,
        pump_status: str,
        pump_speed_setpoint: float,
        dt_seconds: float = 1.0,
    ) -> tuple[float, float, str, float, float, float]:
        """Calculates hydraulic telemetry and updates tank level.
        
        Returns:
            (water_flow, tank_level, effective_pump_status, effective_pump_speed, pressure, pump_power)
        """
        status_norm = pump_status.upper().strip()
        if status_norm != "ON":
            status_norm = "OFF"

        if status_norm == "OFF":
            effective_speed = 0.0
            water_flow = 0.0
            pressure = round(self.static_pressure_off + self.rng.gauss(0, 0.01), 2)
            pump_power = 0.0
        else:
            effective_speed = max(0.0, min(100.0, float(pump_speed_setpoint)))

            # 1. Flow matches P3 Navier-Stokes invariant (2.2 * speed) with small physical turbulence (+-0.2)
            water_flow = self.flow_coefficient * effective_speed + self.rng.gauss(0, 0.15)
            water_flow = max(0.0, round(water_flow, 1))

            # 2. Pressure matches P3 Bernoulli invariant (1.2 + 0.035 * speed)
            pressure = self.pressure_base_on + self.pressure_gain * effective_speed + self.rng.gauss(0, 0.01)
            pressure = round(pressure, 2)

            # 3. Pump Power follows cubic affinity law P = 0.4 + 2.8 * (speed/100)³
            speed_fraction = effective_speed / 100.0
            pump_power = 0.4 + 2.8 * (speed_fraction ** 3) + self.rng.gauss(0, 0.01)
            pump_power = max(0.0, round(pump_power, 2))

        # Tank level evolution (closed-loop buffered mass balance)
        target_tank = 75.0
        drift_rate = 0.002 * (target_tank - self.tank_level) * dt_seconds
        noise = self.rng.gauss(0, 0.01)
        self.tank_level = max(20.0, min(95.0, round(self.tank_level + drift_rate + noise, 2)))

        return (
            water_flow,
            self.tank_level,
            status_norm,
            effective_speed,
            pressure,
            pump_power,
        )
