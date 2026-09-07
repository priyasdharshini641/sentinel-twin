"""
SENTINEL TWIN — Sustainability Blast Radius Engine
Role: Sustainability Impact Tracking (P4 Service Integration)

Calculates the real-time physical, environmental, and financial damage caused
when cyber-physical attacks manipulate automated infrastructure controllers:
- Energy Wasted (kWh)
- Water Wasted (Liters)
- Carbon Emissions (kg CO2e avoided / incurred @ 0.82 kg CO2 / kWh)
- Financial Loss in INR (₹9.50/kWh commercial tariff) and USD ($0.11/kWh)
"""

from typing import Dict, Any
from app.models.telemetry import Telemetry, DefenseResult, SustainabilityImpact


class SustainabilityService:
    """
    Accumulates sustainability damage metrics during an attack.
    """

    def __init__(self):
        self.water_wasted_liters: float = 0.0
        self.energy_wasted_kwh: float = 0.0
        self.carbon_kg_per_kwh: float = 0.82    # Standard grid carbon intensity
        self.electricity_rate_inr: float = 9.50  # ₹ / kWh
        self.electricity_rate_usd: float = 0.114 # $ / kWh
        self.water_rate_inr: float = 0.08        # ₹ / Liter
        self.water_rate_usd: float = 0.001       # $ / Liter

    def reset(self):
        """Reset accumulated sustainability losses."""
        self.water_wasted_liters = 0.0
        self.energy_wasted_kwh = 0.0

    def update(
        self,
        ground_truth: Telemetry,
        reported: Telemetry,
        defense: DefenseResult,
        dt: float = 1.0
    ) -> SustainabilityImpact:
        """
        Integrate damage caused by discrepancy between ground truth and automated reaction.
        """
        # If an attack is active and compromised sensors are detected:
        if defense.threat_level.value in ["ELEVATED", "CRITICAL"]:
            # False load signals cause chillers to fight incorrect thermal setpoints
            load_error = abs(ground_truth.cooling_load - reported.cooling_load)
            # Wasted power delta ~ 0.85 * load_error
            excess_power_kw = load_error * 0.85
            self.energy_wasted_kwh += excess_power_kw * (dt / 3600.0)

            # False flow/pressure signals cause unnecessary pump venting or overflow
            flow_error = abs(ground_truth.water_flow - reported.water_flow)
            self.water_wasted_liters += (flow_error * 0.3) * (dt / 60.0)

        carbon_emissions_kg = self.energy_wasted_kwh * self.carbon_kg_per_kwh

        financial_loss_inr = (
            self.energy_wasted_kwh * self.electricity_rate_inr +
            self.water_wasted_liters * self.water_rate_inr
        )
        financial_loss_usd = (
            self.energy_wasted_kwh * self.electricity_rate_usd +
            self.water_wasted_liters * self.water_rate_usd
        )

        return SustainabilityImpact(
            water_wasted_liters=round(self.water_wasted_liters, 2),
            energy_wasted_kwh=round(self.energy_wasted_kwh, 3),
            carbon_emissions_kg=round(carbon_emissions_kg, 3),
            financial_loss_inr=round(financial_loss_inr, 2),
            financial_loss_usd=round(financial_loss_usd, 2)
        )
