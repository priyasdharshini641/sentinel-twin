"""
SENTINEL TWIN — Climate-Aware Agricultural Decision Engine
Role: Agricultural Cyber-Physical Decision Layer

Implements:
1. 7-Activity Farming Suitability Matrix (Sowing, Irrigation, Fertilizer, Pesticide, Weeding, Harvesting, Drying)
2. 3-Tier Anomaly Scoring:
   - Tier 1: Environmental / Climate Suitability (Favourable / Warning / Severe)
   - Tier 2: Statistical Telemetry Anomaly (Normal / Outlier)
   - Tier 3: Causal Reality Verification (Consistent / Suspicious / Violated)
3. Automated Irrigation Controller with Cyber-Physical Interlock
"""

from enum import Enum
from typing import Dict, Any, List
from datetime import datetime


class Suitability(str, Enum):
    FAVORABLE = "FAVORABLE"      # 🟢 Safe for operation
    CAUTION = "CAUTION"          # 🟡 Suboptimal / Warning
    UNFAVORABLE = "UNFAVORABLE"  # 🔴 Risk of crop/chemical damage


class FarmingActivity(str, Enum):
    SOWING = "Sowing"
    IRRIGATION = "Irrigation"
    FERTILIZER = "Fertilizer Application"
    PESTICIDE = "Pesticide Spraying"
    WEEDING = "Weeding"
    HARVESTING = "Harvesting"
    DRYING = "Drying"


class AgriculturalDecisionEngine:
    """
    Evaluates agricultural operations against multi-variable climate telemetry
    and coordinates with Sentinel Twin's Causal Reality Engine.
    """

    def __init__(self):
        # Default nominal field parameters
        self.crop_stage = "Vegetative Growth"
        self.target_soil_moisture = 55.0  # % optimal field capacity

    def evaluate_farming_matrix(self, telemetry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluates current climate & field telemetry against the 7 core farming activities.
        Matches the team's canonical Farming Activity Matrix.
        """
        temp = float(telemetry.get("temperature", 25.0))
        hum = float(telemetry.get("humidity", 50.0))
        solar = float(telemetry.get("solar_radiation", 500.0))
        flow = float(telemetry.get("water_flow", 0.0))
        pump_on = str(telemetry.get("pump_status", "OFF")).upper() == "ON"
        
        # Inferred / virtual field soil moisture from pump delivery and ambient heat
        soil_moisture = float(telemetry.get("soil_moisture", 52.0))

        # Synthetic micro-climate indicators
        rain = 0.0 if solar > 200.0 else (5.2 if hum > 85.0 else 0.0)
        wind = round(3.5 + 1.5 * (solar / 1000.0), 1)

        matrix = []

        # 1. SOWING
        sow_status = Suitability.FAVORABLE
        sow_reason = "Temperature and soil moisture within optimal germination window."
        if temp > 35.0 or temp < 15.0:
            sow_status = Suitability.CAUTION
            sow_reason = "Thermal stress may inhibit seed germination."
        if rain > 10.0:
            sow_status = Suitability.UNFAVORABLE
            sow_reason = "Heavy rain causes seed washout and waterlogging."
        matrix.append({
            "activity": FarmingActivity.SOWING.value,
            "status": sow_status.value,
            "reason": sow_reason,
            "factors": {"temp": "🟢", "humidity": "🟢", "rain": "🟢" if rain == 0 else "🔴", "soil": "🟢"}
        })

        # 2. IRRIGATION
        irr_status = Suitability.FAVORABLE
        irr_reason = "Irrigation active; water flow meeting evapotranspiration demand."
        if rain > 2.0:
            irr_status = Suitability.UNFAVORABLE
            irr_reason = "Natural precipitation active. Irrigation should be cut off to conserve water."
        elif soil_moisture > 75.0:
            irr_status = Suitability.UNFAVORABLE
            irr_reason = "Soil saturated (>75%). Over-watering risks root hypoxia."
        elif soil_moisture < 35.0:
            irr_status = Suitability.CAUTION
            irr_reason = "Soil moisture critically low (<35%). High irrigation demand."
        matrix.append({
            "activity": FarmingActivity.IRRIGATION.value,
            "status": irr_status.value,
            "reason": irr_reason,
            "factors": {"temp": "🟡" if temp > 32 else "🟢", "solar": "🟡" if solar > 800 else "🟢", "rain": "🟢" if rain == 0 else "🔴", "soil": "🟡" if soil_moisture < 40 else "🟢"}
        })

        # 3. FERTILIZER APPLICATION
        fert_status = Suitability.FAVORABLE
        fert_reason = "Optimal soil moisture and calm winds for nutrient uptake."
        if rain > 1.0:
            fert_status = Suitability.UNFAVORABLE
            fert_reason = "Rainfall risks nutrient runoff and fertilizer wastage."
        elif wind > 15.0:
            fert_status = Suitability.CAUTION
            fert_reason = "High winds may disrupt uniform granular distribution."
        matrix.append({
            "activity": FarmingActivity.FERTILIZER.value,
            "status": fert_status.value,
            "reason": fert_reason,
            "factors": {"temp": "🟢", "humidity": "🟢", "rain": "🔴" if rain > 1 else "🟢", "wind": "🟢"}
        })

        # 4. PESTICIDE SPRAYING
        pest_status = Suitability.FAVORABLE
        pest_reason = "Low wind drift risk and dry canopy suitable for foliar spraying."
        if rain > 0.0:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = "Precipitation will wash chemical sprays off foliage."
        elif wind > 12.0:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = "Excessive wind creates dangerous spray drift into non-target zones."
        elif temp > 32.0:
            pest_status = Suitability.CAUTION
            pest_reason = "High temperature increases chemical volatilization."
        matrix.append({
            "activity": FarmingActivity.PESTICIDE.value,
            "status": pest_status.value,
            "reason": pest_reason,
            "factors": {"temp": "🟢" if temp <= 32 else "🟡", "rain": "🔴" if rain > 0 else "🟢", "wind": "🔴" if wind > 12 else "🟢"}
        })

        # 5. WEEDING
        weed_status = Suitability.FAVORABLE
        weed_reason = "Soil friability optimal for root extraction."
        if rain > 2.0 or soil_moisture > 70.0:
            weed_status = Suitability.UNFAVORABLE
            weed_reason = "Waterlogged soil creates heavy mud and complicates mechanical weeding."
        matrix.append({
            "activity": FarmingActivity.WEEDING.value,
            "status": weed_status.value,
            "reason": weed_reason,
            "factors": {"soil": "🟢" if soil_moisture <= 70 else "🔴", "rain": "🟢" if rain == 0 else "🔴"}
        })

        # 6. HARVESTING
        harv_status = Suitability.FAVORABLE
        harv_reason = "Dry canopy and firm field conditions suitable for equipment."
        if rain > 0.0:
            harv_status = Suitability.UNFAVORABLE
            harv_reason = "Moisture damages ripe crops and causes soil compaction."
        elif hum > 80.0:
            harv_status = Suitability.CAUTION
            harv_reason = "High humidity increases post-harvest fungal infection risk."
        matrix.append({
            "activity": FarmingActivity.HARVESTING.value,
            "status": harv_status.value,
            "reason": harv_reason,
            "factors": {"humidity": "🟡" if hum > 80 else "🟢", "rain": "🔴" if rain > 0 else "🟢"}
        })

        # 7. DRYING
        dry_status = Suitability.FAVORABLE
        dry_reason = "High solar irradiance and low humidity enable rapid grain drying."
        if rain > 0.0 or hum > 75.0:
            dry_status = Suitability.UNFAVORABLE
            dry_reason = "Atmospheric moisture prevents crop moisture reduction."
        elif solar < 300.0:
            dry_status = Suitability.CAUTION
            dry_reason = "Low solar irradiance prolongs required drying duration."
        matrix.append({
            "activity": FarmingActivity.DRYING.value,
            "status": dry_status.value,
            "reason": dry_reason,
            "factors": {"solar": "🟢" if solar >= 300 else "🟡", "humidity": "🔴" if hum > 75 else "🟢", "rain": "🔴" if rain > 0 else "🟢"}
        })

        return matrix

    def compute_3tier_decision(
        self,
        telemetry: Dict[str, Any],
        is_statistical_outlier: bool,
        is_causal_violation: bool,
        violated_invariants: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesizes the 3-Tier Anomaly Scoring Model:
        1. Climate Analysis: Favourable / Warning / Severe
        2. Statistical Telemetry Anomaly: Normal / Outlier
        3. Causal Reality Engine: Consistent / Suspicious / Violated
        """
        temp = float(telemetry.get("temperature", 25.0))
        solar = float(telemetry.get("solar_radiation", 500.0))

        # Tier 1: Climate Severity
        if temp > 38.0 or solar > 950.0:
            climate_tier = "SEVERE"
            climate_label = "Severe Heatwave / High Solar Irradiance"
        elif temp > 33.0 or solar > 800.0:
            climate_tier = "WARNING"
            climate_label = "Elevated Evaporative Stress"
        else:
            climate_tier = "FAVOURABLE"
            climate_label = "Nominal Agro-Climate Conditions"

        # Tier 2: Statistical Telemetry Anomaly
        stat_tier = "OUTLIER" if is_statistical_outlier else "NORMAL"

        # Tier 3: Causal Reality Engine
        if is_causal_violation:
            causal_tier = "VIOLATED"
        elif len(violated_invariants) > 0:
            causal_tier = "SUSPICIOUS"
        else:
            causal_tier = "CONSISTENT"

        # Unified System Decision Matrix (from Teammate's Section 6)
        if causal_tier == "VIOLATED":
            system_decision = "ATTACK_VIOLATION"
            action = "INTERLOCK_ENGAGED"
            explanation = "Physical invariant breach detected. Automated irrigation controller locked in safe-mode to prevent crop sabotage."
        elif climate_tier in ["WARNING", "SEVERE"] and causal_tier == "CONSISTENT":
            system_decision = "GENUINE_CLIMATE_EVENT"
            action = "AUTOMATED_CLIMATE_RESPONSE"
            explanation = "Legitimate high-heat weather event. Physics verified. Automated irrigation increased to prevent plant wilting."
        elif stat_tier == "OUTLIER" and causal_tier == "CONSISTENT":
            system_decision = "INVESTIGATE_SENSOR_DRIFT"
            action = "FLAG_MAINTENANCE"
            explanation = "Statistical deviation detected, but energy-hydraulic conservation holds. Likely benign sensor calibration drift."
        else:
            system_decision = "NORMAL_OPERATION"
            action = "NOMINAL_MONITORING"
            explanation = "Agro-climate and irrigation physical loops fully synchronized with natural environmental laws."

        return {
            "tier1_climate": {
                "level": climate_tier,
                "label": climate_label
            },
            "tier2_statistical": {
                "status": stat_tier,
                "description": "Z-score and IQR moving window check"
            },
            "tier3_causal": {
                "status": causal_tier,
                "violated_invariants": violated_invariants
            },
            "system_decision": system_decision,
            "action": action,
            "explanation": explanation
        }


# Global singleton
agricultural_engine = AgriculturalDecisionEngine()
