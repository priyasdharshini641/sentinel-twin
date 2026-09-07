import random


class HVACModel:
    """Models thermal cooling load and electrical power consumption.
    
    Invariants:
    - Cooling load increases when ambient temperature rises above setpoint (21°C).
    - Solar radiation directly contributes to building thermal gain.
    - HVAC power consumption is bound to cooling load by Chiller COP (Coefficient of Performance).
    - Total power equals: base_power + hvac_power + pump_power.
    """

    def __init__(
        self,
        indoor_setpoint: float = 21.0,       # °C
        base_building_load: float = 4.0,     # kW internal baseline thermal heat
        solar_gain_factor: float = 0.015,    # kW per W/m² solar irradiance
        thermal_transmission: float = 1.2,   # kW per °C temperature delta
        chiller_cop: float = 3.6,            # Coefficient of Performance
        facility_base_power: float = 2.5,    # kW baseline electrical draw
        seed: int = 202,
    ):
        self.indoor_setpoint = indoor_setpoint
        self.base_building_load = base_building_load
        self.solar_gain_factor = solar_gain_factor
        self.thermal_transmission = thermal_transmission
        self.chiller_cop = chiller_cop
        self.facility_base_power = facility_base_power
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
        # Thermal load from ambient temperature gradient
        temp_delta = max(0.0, temperature - self.indoor_setpoint)
        conductive_load = temp_delta * self.thermal_transmission

        # Thermal load from solar radiation
        solar_load = max(0.0, solar_radiation * self.solar_gain_factor)

        # Total cooling load (kW) required to maintain temperature
        cooling_load = self.base_building_load + conductive_load + solar_load
        cooling_load += self.rng.gauss(0, 0.1)
        cooling_load = max(1.0, round(cooling_load, 1))

        # Electrical power consumed by HVAC chiller compressor
        hvac_power = cooling_load / self.chiller_cop

        # Total facility electrical power = base facility + HVAC chiller + water pump
        total_power = self.facility_base_power + hvac_power + pump_power
        total_power += self.rng.gauss(0, 0.05)
        total_power = max(1.0, round(total_power, 2))

        return cooling_load, total_power
