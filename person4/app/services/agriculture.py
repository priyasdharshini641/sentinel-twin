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

    def evaluate_farming_matrix(
        self,
        telemetry: Dict[str, Any],
        compromised_sensors: List[str] = None,
        violated_invariants: List[str] = None,
        is_attack_active: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Evaluates current climate & field telemetry against the 7 core farming activities.
        Matches the team's canonical Farming Activity Matrix and reflects real-time
        attack scenarios and cyber-physical interlock disengagement.
        """
        compromised = set(compromised_sensors or [])
        violated = set(violated_invariants or [])

        temp = float(telemetry.get("temperature", 25.0))
        hum = float(telemetry.get("humidity", 50.0))
        solar = float(telemetry.get("solar_radiation", 500.0))
        flow = float(telemetry.get("water_flow", 0.0))
        pump_on = str(telemetry.get("pump_status", "OFF")).upper() == "ON"
        pump_speed = float(telemetry.get("pump_speed", 0.0))

        # Synthetic micro-climate indicators derived from physics
        if hum > 80.0 and solar < 250.0:
            rain = round(2.0 + (hum - 80.0) * 1.1, 1)
        elif hum > 90.0:
            rain = 7.5
        else:
            rain = 0.0

        wind = round(3.5 + 2.5 * max(0.0, (temp - 25.0) / 4.0) + 1.5 * (solar / 1000.0), 1)

        # Dynamic root-zone soil moisture (%)
        if rain > 3.0 or hum > 88.0:
            soil_moisture = min(96.0, 58.0 + rain * 2.2)
        elif temp > 35.0 and flow < 30.0:
            soil_moisture = max(18.0, 50.0 - (temp - 30.0) * 3.5)
        elif flow > 210.0 or float(telemetry.get("tank_level", 75.0)) > 90.0:
            soil_moisture = min(92.0, 65.0 + (max(0.0, flow - 210.0) / 20.0) * 25.0)
        else:
            soil_moisture = float(telemetry.get("soil_moisture", 55.0))

        matrix = []

        # 1. SOWING
        sow_status = Suitability.FAVORABLE
        sow_reason = "Optimal soil temperature and moisture window for seed germination."
        sow_temp_factor = "🟢"
        sow_rain_factor = "🟢" if rain == 0 else "🔴"

        if "temperature" in compromised and is_attack_active:
            sow_status = Suitability.UNFAVORABLE
            sow_reason = "🚨 CYBER-PHYSICAL INTERLOCK: Thermal telemetry breach detected. Sowing halted to prevent seed loss under false climate data."
            sow_temp_factor = "🔴"
        elif rain > 10.0:
            sow_status = Suitability.UNFAVORABLE
            sow_reason = f"Heavy precipitation ({rain:.1f} mm > 10 mm) causes seed washout, silt deposition, and seedling suffocation."
            sow_rain_factor = "🔴"
        elif temp > 35.0:
            sow_status = Suitability.UNFAVORABLE
            sow_reason = f"Severe thermal stress ({temp:.1f}°C > 35°C) inhibits seed germination and causes seedling desiccation."
            sow_temp_factor = "🔴"
        elif temp < 15.0 or temp > 32.0 or rain > 3.0:
            sow_status = Suitability.CAUTION
            sow_reason = f"Suboptimal conditions (Temp: {temp:.1f}°C, Rain: {rain:.1f} mm); germination speed retarded."
            sow_temp_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.SOWING.value,
            "status": sow_status.value,
            "reason": sow_reason,
            "factors": {"temp": sow_temp_factor, "humidity": "🟢" if hum <= 75 else "🟡", "rain": sow_rain_factor, "soil": "🟢" if 35 <= soil_moisture <= 70 else "🔴"}
        })

        # 2. IRRIGATION
        irr_status = Suitability.FAVORABLE
        irr_reason = "Irrigation active; water flow meeting crop evapotranspiration demand."
        irr_flow_factor = "🟢"

        if is_attack_active and ("water_flow" in compromised or "pressure" in compromised or "Actuator-Energy Coupling" in violated or "Bernoulli Flow-Pressure Balance" in violated or (pump_on and flow < 10.0)):
            irr_status = Suitability.UNFAVORABLE
            irr_reason = "🚨 CYBER-PHYSICAL INTERLOCK: Hydraulic/flow invariant fractured! Automated irrigation locked to protect pump motors and prevent crop flooding."
            irr_flow_factor = "🔴"
        elif rain > 2.0:
            irr_status = Suitability.UNFAVORABLE
            irr_reason = f"Natural precipitation active ({rain:.1f} mm > 2 mm). Irrigation shut off to conserve water."
            irr_flow_factor = "🟡"
        elif soil_moisture > 75.0:
            irr_status = Suitability.UNFAVORABLE
            irr_reason = f"Soil saturated ({soil_moisture:.1f}% > 75%). Over-watering risks root hypoxia and damping-off disease."
            irr_flow_factor = "🟡"
        elif soil_moisture < 35.0 or temp > 35.0:
            irr_status = Suitability.CAUTION
            irr_reason = f"Elevated thermal stress ({temp:.1f}°C, Soil: {soil_moisture:.1f}%); high evapotranspiration demand."
            irr_flow_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.IRRIGATION.value,
            "status": irr_status.value,
            "reason": irr_reason,
            "factors": {"temp": "🟡" if temp > 32 else "🟢", "solar": "🟡" if solar > 850 else "🟢", "rain": "🟢" if rain == 0 else "🔴", "soil": "🟡" if soil_moisture < 40 else ("🔴" if soil_moisture > 75 else "🟢")}
        })

        # 3. FERTILIZER APPLICATION
        fert_status = Suitability.FAVORABLE
        fert_reason = "Adequate soil moisture and calm winds optimal for uniform nutrient uptake."
        fert_rain_factor = "🟢" if rain <= 1.0 else "🔴"
        fert_wind_factor = "🟢"

        if rain > 1.0:
            fert_status = Suitability.UNFAVORABLE
            fert_reason = f"Precipitation ({rain:.1f} mm > 1.0 mm) risks severe nutrient leaching and fertilizer runoff into waterways."
            fert_rain_factor = "🔴"
        elif wind > 15.0:
            fert_status = Suitability.CAUTION
            fert_reason = f"High winds ({wind:.1f} km/h > 15 km/h) disrupt uniform granular distribution."
            fert_wind_factor = "🟡"
        elif temp > 36.0 or soil_moisture < 30.0:
            fert_status = Suitability.CAUTION
            fert_reason = f"Dry soil ({soil_moisture:.1f}%) and heat ({temp:.1f}°C) accelerate nitrogen volatilization."
            fert_wind_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.FERTILIZER.value,
            "status": fert_status.value,
            "reason": fert_reason,
            "factors": {"temp": "🟢" if temp <= 32 else "🟡", "humidity": "🟢" if hum <= 80 else "🟡", "rain": fert_rain_factor, "wind": fert_wind_factor}
        })

        # 4. PESTICIDE SPRAYING
        pest_status = Suitability.FAVORABLE
        pest_reason = "Calm winds, dry canopy, and safe temperature window suitable for foliar spraying."
        pest_temp_factor = "🟢"
        pest_rain_factor = "🟢" if rain == 0 else "🔴"
        pest_wind_factor = "🟢"

        if "temperature" in compromised and is_attack_active:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = "🚨 CYBER-PHYSICAL INTERLOCK: Thermal telemetry breach detected. Spraying halted to prevent toxic volatilization under unverified ambient heat."
            pest_temp_factor = "🔴"
        elif rain > 0.0:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = f"Precipitation active ({rain:.1f} mm). Rain will wash active chemical agents off foliage, rendering treatment ineffective."
            pest_rain_factor = "🔴"
        elif wind > 12.0:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = f"Wind speed ({wind:.1f} km/h > 12 km/h) creates severe chemical spray drift into non-target crops and populated zones."
            pest_wind_factor = "🔴"
        elif temp > 32.0:
            pest_status = Suitability.UNFAVORABLE
            pest_reason = f"High ambient temperature ({temp:.1f}°C > 32°C) causes rapid chemical volatilization and irreversible foliar leaf burn."
            pest_temp_factor = "🔴"

        matrix.append({
            "activity": FarmingActivity.PESTICIDE.value,
            "status": pest_status.value,
            "reason": pest_reason,
            "factors": {"temp": pest_temp_factor, "rain": pest_rain_factor, "wind": pest_wind_factor}
        })

        # 5. WEEDING
        weed_status = Suitability.FAVORABLE
        weed_reason = "Soil friability optimal for mechanical root extraction without root smear."
        weed_soil_factor = "🟢"

        if rain > 2.0 or soil_moisture > 70.0:
            weed_status = Suitability.UNFAVORABLE
            weed_reason = f"Soil waterlogged ({soil_moisture:.1f}% > 70%, Rain: {rain:.1f} mm). Heavy mud clogs machinery and damages root systems."
            weed_soil_factor = "🔴"
        elif temp > 38.0 or soil_moisture < 25.0:
            weed_status = Suitability.CAUTION
            weed_reason = f"Hard baked dry soil ({soil_moisture:.1f}%) increases draft resistance and blade wear."
            weed_soil_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.WEEDING.value,
            "status": weed_status.value,
            "reason": weed_reason,
            "factors": {"soil": weed_soil_factor, "rain": "🟢" if rain == 0 else "🔴"}
        })

        # 6. HARVESTING
        harv_status = Suitability.FAVORABLE
        harv_reason = "Dry canopy and firm field conditions suitable for harvesting combines."
        harv_rain_factor = "🟢" if rain == 0 else "🔴"
        harv_hum_factor = "🟢"

        if rain > 0.0:
            harv_status = Suitability.UNFAVORABLE
            harv_reason = f"Active precipitation ({rain:.1f} mm). Crop moisture damages ripe grain and causes severe harvester soil compaction."
            harv_rain_factor = "🔴"
        elif hum > 80.0:
            harv_status = Suitability.CAUTION
            harv_reason = f"High atmospheric humidity ({hum:.1f}% > 80%) increases post-harvest fungal infection and moulding risk."
            harv_hum_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.HARVESTING.value,
            "status": harv_status.value,
            "reason": harv_reason,
            "factors": {"humidity": harv_hum_factor, "rain": harv_rain_factor}
        })

        # 7. DRYING
        dry_status = Suitability.FAVORABLE
        dry_reason = "High solar irradiance and low humidity enable rapid post-harvest grain curing."
        dry_solar_factor = "🟢"
        dry_hum_factor = "🟢"

        if rain > 0.0 or hum > 75.0:
            dry_status = Suitability.UNFAVORABLE
            dry_reason = f"Atmospheric moisture (Humidity: {hum:.1f}%, Rain: {rain:.1f} mm) prevents grain moisture reduction and promotes aflatoxins."
            dry_hum_factor = "🔴"
        elif solar < 300.0:
            dry_status = Suitability.CAUTION
            dry_reason = f"Low solar irradiance ({solar:.1f} W/m² < 300 W/m²) prolongs required open-air drying time."
            dry_solar_factor = "🟡"

        matrix.append({
            "activity": FarmingActivity.DRYING.value,
            "status": dry_status.value,
            "reason": dry_reason,
            "factors": {"solar": dry_solar_factor, "humidity": dry_hum_factor, "rain": "🟢" if rain == 0 else "🔴"}
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
        hum = float(telemetry.get("humidity", 50.0))
        solar = float(telemetry.get("solar_radiation", 500.0))

        # Tier 1: Climate Severity
        if temp > 36.0 or solar > 950.0 or hum > 90.0:
            climate_tier = "SEVERE"
            climate_label = "Severe Heatwave / High Solar" if temp > 34.0 else "Torrential Rain / Deluge Conditions"
        elif temp > 32.0 or solar > 800.0 or hum > 80.0:
            climate_tier = "WARNING"
            climate_label = "Elevated Thermal & Evaporative Stress"
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
            explanation = "Legitimate climate event confirmed by physical invariant laws. Automated irrigation adjusted for evapotranspiration."
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
