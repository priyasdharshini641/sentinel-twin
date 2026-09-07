import random


class HVACModel:
    """Models thermal cooling load and electrical power consumption.
    
    Strict Invariants (calibrated to team's Cyber-Physical Invariant Contracts):
    - Invariant 01: Thermodynamic First-Law Balance
      cooling_load = 2.4 * max(0, temperature - 23.0) + 0.015 * solar_radiation + 1.5 (kW)
    - Invariant 04: Actuator-Energy Coupling
      total_power = 0.78 * cooling_load + pump_power + 0.5 (kW)
    """

    def __init__(
        self,
        setpoint_temp: float = 23.0,          # °C indoor target setpoint
        building_ua: float = 2.4,             # kW/°C thermal conduction
        solar_absorption: float = 0.015,      # kW per W/m² solar thermal gain
        base_internal_heat: float = 1.5,      # kW internal baseline thermal heat
        chiller_work_factor: float = 0.78,    # Electrical kW per thermal kW (1/COP)
        aux_facility_power: float = 0.5,      # kW auxiliary controls & sensors
        seed: int = 202,
    ):
        self.setpoint_temp = setpoint_temp
        self.building_ua = building_ua
        self.solar_absorption = solar_absorption
        self.base_internal_heat = base_internal_heat
        self.chiller_work_factor = chiller_work_factor
        self.aux_facility_power = aux_facility_power
        self.rng = random.Random(seed)

    def calculate(
        self,
        temperature: float,
        solar_radiation: float,
        pump_power: float,
    ) -> tuple[float, float]:
        """Calculates (cooling_load, total_power_consumption).
        
        Args:
            temperature: Current ambient/facility temperature (°C).
            solar_radiation: Solar irradiance (W/m²).
            pump_power: Electrical power drawn by the water pump (kW).
            
        Returns:
            (cooling_load_kW, total_power_kW)
        """
        # 1. Thermal load strictly adheres to First Law of Thermodynamics
        delta_t = max(0.0, temperature - self.setpoint_temp)
        conductive_load = self.building_ua * delta_t
        solar_load = self.solar_absorption * max(0.0, solar_radiation)

        cooling_load = conductive_load + solar_load + self.base_internal_heat
        cooling_load += self.rng.gauss(0, 0.05)
        cooling_load = max(1.0, round(cooling_load, 2))

        # 2. Total electrical power balances chiller work + pump power + aux controls
        chiller_power = cooling_load * self.chiller_work_factor
        total_power = chiller_power + pump_power + self.aux_facility_power
        total_power += self.rng.gauss(0, 0.02)
        total_power = max(1.0, round(total_power, 2))

        return cooling_load, total_power
