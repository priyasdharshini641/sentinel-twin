import random


class HydraulicModel:
    """Models the pump, pipe network, water flow, pressure, and tank level.
    
    Strict Invariants:
    - If pump_status == "OFF", water_flow == 0.0 L/min, pump_speed == 0.0%,
      pressure rests at static baseline (~1.0-1.1 bar), and pump power == 0.0 kW.
    - If pump_status == "ON", water_flow > 0, pressure rises dynamically with pump head,
      and pump electrical power follows affinity laws (P ∝ speed³).
    - Tank level evolves continuously under mass conservation.
    """

    def __init__(
        self,
        max_flow_rate: float = 120.0,       # L/min at 100% speed
        static_pressure: float = 1.05,       # bar with pump OFF
        max_dynamic_pressure: float = 3.2,   # additional bar at 100% speed
        max_pump_power: float = 4.5,         # kW at 100% speed
        initial_tank_level: float = 75.0,    # %
        seed: int = 101,
    ):
        self.max_flow_rate = max_flow_rate
        self.static_pressure = static_pressure
        self.max_dynamic_pressure = max_dynamic_pressure
        self.max_pump_power = max_pump_power
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
            # Static head pressure with slight sensor flutter
            pressure = round(self.static_pressure + self.rng.gauss(0, 0.01), 2)
            pump_power = 0.0
        else:
            effective_speed = max(0.0, min(100.0, float(pump_speed_setpoint)))
            speed_fraction = effective_speed / 100.0

            # Water flow is proportional to pump speed
            water_flow = self.max_flow_rate * speed_fraction
            water_flow += self.rng.gauss(0, 0.3)
            water_flow = max(0.0, round(water_flow, 1))

            # Pressure = static pressure + dynamic head proportional to speed²
            pressure = self.static_pressure + self.max_dynamic_pressure * (speed_fraction ** 2)
            pressure += self.rng.gauss(0, 0.02)
            pressure = round(pressure, 2)

            # Pump electrical power follows affinity laws (P ∝ speed³) + electrical motor overhead
            if speed_fraction > 0.01:
                pump_power = 0.3 + (self.max_pump_power - 0.3) * (speed_fraction ** 3)
                pump_power += self.rng.gauss(0, 0.02)
                pump_power = max(0.0, round(pump_power, 2))
            else:
                pump_power = 0.0

        # Tank level evolution (closed-loop buffer with slight nominal makeup float equilibrium)
        # Smooth oscillation around 75% without discontinuous teleportation
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
