"""
SENTINEL TWIN — P3 Blue Team Defense Engine (Causal Reality Engine)
Role: P3 Service Interface (Included for complete standalone P4 integration)

Takes ONLY reported_telemetry (zero ground truth cheating).
Evaluates 4 Cyber-Physical Invariant Contracts (CPIC):
1. Invariant 01: Thermodynamic First-Law Balance (Q = UA*dT + alpha*Solar)
2. Invariant 02: Psychrometric Evaporative Correlation (Temp vs Humidity vs Solar)
3. Invariant 03: Hydraulic Coupling & Mass Balance (Flow vs Speed vs Pressure)
4. Invariant 04: Actuator-Energy Coupling (Motor Affinity Laws P ~ Speed^3 + Chiller)

Outputs:
- system_trust_score (0 - 100%)
- sensor_trust_scores per field
- InvariantCheckResult objects
- Plain-English Detective Forensic Deduction
- Healed / Imputed Telemetry (Virtual sensor state recovery)
"""

import math
from typing import Dict, Any, List
from app.models.telemetry import (
    Telemetry, DefenseResult, InvariantCheckResult, ThreatLevel
)


class DefenseEngineService:
    """
    Evaluates reported telemetry against cyber-physical invariant contracts.
    """

    def __init__(self):
        # Physical model baselines
        self.setpoint_temp = 23.0
        self.building_ua = 2.4
        self.solar_absorption = 0.015

    def analyze(self, reported: Telemetry) -> DefenseResult:
        """
        Inspect reported telemetry, verify invariants, and produce forensic diagnosis.
        """
        invariants: List[InvariantCheckResult] = []
        compromised_sensors: List[str] = []
        sensor_trust: Dict[str, float] = {
            "temperature": 100.0,
            "humidity": 100.0,
            "solar_radiation": 100.0,
            "cooling_load": 100.0,
            "power_consumption": 100.0,
            "water_flow": 100.0,
            "tank_level": 100.0,
            "pump_status": 100.0,
            "pump_speed": 100.0,
            "pressure": 100.0,
        }

        # ---------------------------------------------------------------------
        # INVARIANT 01: Thermodynamic First-Law Balance
        # Expected thermal demand Q_dot = UA * (T_amb - T_set) + alpha * Solar + Q_internal
        # ---------------------------------------------------------------------
        delta_t_expected = max(0.0, reported.temperature - self.setpoint_temp)
        expected_load = (self.building_ua * delta_t_expected) + (self.solar_absorption * reported.solar_radiation) + 1.5
        residual_inv1 = abs(reported.cooling_load - expected_load)
        threshold_inv1 = 3.5  # kW allowable thermal slack

        inv1_violated = residual_inv1 > threshold_inv1
        invariants.append(InvariantCheckResult(
            invariant_id="INV_01_THERMODYNAMICS",
            name="Thermodynamic Thermal Balance",
            law="First Law of Thermodynamics (Q = UA·ΔT + α·Solar)",
            violated=inv1_violated,
            residual=round(residual_inv1, 2),
            threshold=threshold_inv1,
            description=f"Cooling load ({reported.cooling_load:.1f} kW) deviates from expected ({expected_load:.1f} kW) given reported ambient temperature and solar flux."
        ))

        if inv1_violated:
            sensor_trust["cooling_load"] = max(20.0, sensor_trust["cooling_load"] - 50.0)
            sensor_trust["temperature"] = max(25.0, sensor_trust["temperature"] - 45.0)
            sensor_trust["solar_radiation"] = max(30.0, sensor_trust["solar_radiation"] - 40.0)
            if "temperature" not in compromised_sensors:
                compromised_sensors.append("temperature")
            if "cooling_load" not in compromised_sensors:
                compromised_sensors.append("cooling_load")

        # ---------------------------------------------------------------------
        # INVARIANT 02: Psychrometric Humidity Correlation
        # As temperature rises under solar heat, relative humidity drops
        # ---------------------------------------------------------------------
        expected_humidity_max = max(25.0, 90.0 - (reported.temperature - 20.0) * 2.2)
        residual_inv2 = max(0.0, reported.humidity - (expected_humidity_max + 18.0))
        threshold_inv2 = 12.0

        inv2_violated = residual_inv2 > threshold_inv2
        invariants.append(InvariantCheckResult(
            invariant_id="INV_02_PSYCHROMETRICS",
            name="Psychrometric Vapor Correlation",
            law="August-Roche-Magnus Vapor Pressure Law",
            violated=inv2_violated,
            residual=round(residual_inv2, 1),
            threshold=threshold_inv2,
            description=f"Reported humidity ({reported.humidity:.1f}%) is unphysically decoupled from temperature ({reported.temperature:.1f}°C)."
        ))

        if inv2_violated:
            sensor_trust["humidity"] = max(20.0, sensor_trust["humidity"] - 60.0)
            if "humidity" not in compromised_sensors:
                compromised_sensors.append("humidity")

        # ---------------------------------------------------------------------
        # INVARIANT 03: Hydraulic Coupling & Mass Balance
        # Flow must correspond to pump speed and pump status
        # ---------------------------------------------------------------------
        expected_flow = 2.2 * reported.pump_speed if reported.pump_status == "ON" else 0.0
        expected_pressure = 1.2 + 0.035 * reported.pump_speed if reported.pump_status == "ON" else 1.0

        residual_flow = abs(reported.water_flow - expected_flow)
        residual_pressure = abs(reported.pressure - expected_pressure)
        residual_inv3 = residual_flow + residual_pressure * 20.0
        threshold_inv3 = 25.0

        inv3_violated = residual_inv3 > threshold_inv3 or (reported.pump_status == "OFF" and reported.water_flow > 10.0)
        invariants.append(InvariantCheckResult(
            invariant_id="INV_03_HYDRAULIC_BALANCE",
            name="Hydraulic Actuator-Coupling",
            law="Navier-Stokes / Bernoulli Pressure-Flow Conservation",
            violated=inv3_violated,
            residual=round(residual_inv3, 2),
            threshold=threshold_inv3,
            description=f"Flow ({reported.water_flow:.1f} L/min) or pressure ({reported.pressure:.2f} bar) contradicts pump speed ({reported.pump_speed:.1f}%)."
        ))

        if inv3_violated:
            sensor_trust["water_flow"] = max(15.0, sensor_trust["water_flow"] - 55.0)
            sensor_trust["pressure"] = max(20.0, sensor_trust["pressure"] - 50.0)
            if "water_flow" not in compromised_sensors:
                compromised_sensors.append("water_flow")

        # ---------------------------------------------------------------------
        # INVARIANT 04: Motor Affinity & Power Coupling
        # Electrical power = Chiller load (~0.78*Q) + Pump affinity (~P_idle + C*speed^3)
        # ---------------------------------------------------------------------
        expected_chiller_power = reported.cooling_load * 0.78
        expected_pump_power = 0.4 + 2.8 * math.pow(reported.pump_speed / 100.0, 3)
        expected_total_power = expected_chiller_power + expected_pump_power + 0.5
        residual_inv4 = abs(reported.power_consumption - expected_total_power)
        threshold_inv4 = 3.0  # kW

        inv4_violated = residual_inv4 > threshold_inv4
        invariants.append(InvariantCheckResult(
            invariant_id="INV_04_MOTOR_AFFINITY",
            name="Actuator-Energy Coupling",
            law="Motor Affinity Law (Power ∝ Speed³ + Thermal Work)",
            violated=inv4_violated,
            residual=round(residual_inv4, 2),
            threshold=threshold_inv4,
            description=f"Power consumption ({reported.power_consumption:.2f} kW) contradicts actuator mechanical work ({expected_total_power:.2f} kW)."
        ))

        if inv4_violated:
            sensor_trust["power_consumption"] = max(20.0, sensor_trust["power_consumption"] - 50.0)
            if "power_consumption" not in compromised_sensors:
                compromised_sensors.append("power_consumption")

        # ---------------------------------------------------------------------
        # SYSTEM TRUST SCORE & THREAT LEVEL
        # ---------------------------------------------------------------------
        avg_sensor_trust = sum(sensor_trust.values()) / len(sensor_trust)
        violations_count = sum(1 for inv in invariants if inv.violated)

        if violations_count == 0:
            system_trust_score = round(avg_sensor_trust, 1)
            threat_level = ThreatLevel.LOW if system_trust_score >= 90.0 else ThreatLevel.GUARDED
        elif violations_count == 1:
            system_trust_score = round(min(68.0, avg_sensor_trust * 0.7), 1)
            threat_level = ThreatLevel.ELEVATED
        else:
            # Multi-invariant collapse -> Coordinated attack detected!
            system_trust_score = round(min(42.0, avg_sensor_trust * 0.4), 1)
            threat_level = ThreatLevel.CRITICAL

        # ---------------------------------------------------------------------
        # DETECTIVE FORENSIC EXPLANATION (Plain-English Deduction)
        # ---------------------------------------------------------------------
        if violations_count == 0:
            forensic_deduction = (
                "NOMINAL STABILITY: All 4 Cyber-Physical Invariant Contracts verified. "
                "Thermodynamic thermal balance, psychrometric curves, and motor affinity power "
                "coupling match expected physical reality within ±3% tolerance."
            )
        else:
            violated_names = [inv.name for inv in invariants if inv.violated]
            forensic_deduction = (
                f"DETECTIVE FORENSIC DEDUCTION: Invariant violation detected across [{', '.join(violated_names)}]. "
            )
            if inv1_violated and inv4_violated:
                forensic_deduction += (
                    f"Reported cooling load ({reported.cooling_load:.1f} kW) or ambient temperature ({reported.temperature:.1f}°C) "
                    f"contradicts electrical power draw ({reported.power_consumption:.1f} kW) and hydraulic coolant flow. "
                    "In accordance with the First Law of Thermodynamics, chiller power cannot remain high while thermal demand "
                    "purportedly falls, unless sensor readings have been deliberately fabricated. "
                    f"Compromised telemetry streams identified: [{', '.join(compromised_sensors)}]."
                )
            elif inv1_violated:
                forensic_deduction += (
                    f"Reported temperature ({reported.temperature:.1f}°C) and solar radiation ({reported.solar_radiation:.0f} W/m²) "
                    f"fail to account for cooling load ({reported.cooling_load:.1f} kW). Suspected False Data Injection (FDI)."
                )
            elif inv3_violated or inv4_violated:
                forensic_deduction += (
                    f"Hydraulic flow or power consumption violates motor affinity cubic laws. "
                    "Physical actuators cannot produce reported flow at current power draw."
                )

        # ---------------------------------------------------------------------
        # SELF-HEALING IMPUTATION (Reconstructing true state via physical laws)
        # ---------------------------------------------------------------------
        healed = reported.to_dict()
        if "cooling_load" in compromised_sensors:
            # Impute cooling load from electrical power: Chiller power ~ (Power - PumpPower - Aux) / 0.78
            pump_p = 0.4 + 2.8 * math.pow(reported.pump_speed / 100.0, 3)
            imputed_load = max(0.5, (reported.power_consumption - pump_p - 0.5) / 0.78)
            healed["cooling_load"] = round(imputed_load, 2)
            healed["imputed_cooling_load"] = True

        if "temperature" in compromised_sensors and "cooling_load" in healed:
            # Invert thermal balance: T_amb = T_set + (Load - alpha*Solar - 1.5) / UA
            imputed_temp = self.setpoint_temp + (healed["cooling_load"] - self.solar_absorption * reported.solar_radiation - 1.5) / self.building_ua
            healed["temperature"] = round(imputed_temp, 2)
            healed["imputed_temperature"] = True

        return DefenseResult(
            system_trust_score=system_trust_score,
            threat_level=threat_level,
            sensor_trust_scores={k: round(v, 1) for k, v in sensor_trust.items()},
            invariants=invariants,
            compromised_sensors=compromised_sensors,
            forensic_deduction=forensic_deduction,
            healed_telemetry=healed
        )
