"""Defense Pipeline module.

Combines CausalEngine, TrustEngine, and DetectiveExplainer into a unified,
resilient cyber-physical defense workflow. Accepts strictly reported telemetry
without access to attack ground-truth, attack metadata, or simulation labels.
"""

from typing import Any, Dict, List, Optional, Sequence, Set

from backend.defense.causal_engine import CausalEngine
from backend.defense.detective_explainer import DetectiveExplainer
from backend.defense.trust_engine import TrustEngine


class DefensePipeline:
    """Orchestrates causal validation, dynamic trust tracking, and forensic explanation."""

    THERMAL_SENSORS: List[str] = [
        "temperature",
        "humidity",
        "solar_radiation",
        "cooling_load",
        "power_consumption",
    ]

    ACTUATOR_SENSORS: List[str] = [
        "pump_status",
        "pump_speed",
        "water_flow",
        "pressure",
        "power_consumption",
    ]

    TEMPORAL_CHANNELS: List[str] = [
        "temperature",
        "humidity",
        "solar_radiation",
        "cooling_load",
        "power_consumption",
        "water_flow",
        "tank_level",
        "pressure",
        "pump_speed",
    ]

    def __init__(
        self,
        causal_engine: Optional[CausalEngine] = None,
        trust_engine: Optional[TrustEngine] = None,
        detective_explainer: Optional[DetectiveExplainer] = None,
    ) -> None:
        """Initializes the DefensePipeline with default or injected components.

        Args:
            causal_engine: Optional custom CausalEngine instance.
            trust_engine: Optional custom TrustEngine instance.
            detective_explainer: Optional custom DetectiveExplainer instance.
        """
        self.causal_engine: CausalEngine = (
            causal_engine if causal_engine is not None else CausalEngine()
        )
        self.trust_engine: TrustEngine = (
            trust_engine if trust_engine is not None else TrustEngine()
        )
        self.detective_explainer: DetectiveExplainer = (
            detective_explainer if detective_explainer is not None else DetectiveExplainer()
        )

    def _identify_temporal_implicated_sensors(
        self,
        telemetry: Any,
        prior_history: Sequence[Any],
    ) -> List[str]:
        """Identifies specific sensor channel(s) triggering a temporal continuity violation.

        Uses CausalEngine's check_temporal_continuity to evaluate each channel individually
        against the prior historical baseline without duplicating physical formulas.

        Args:
            telemetry: Current reported telemetry snapshot.
            prior_history: Telemetry history snapshot prior to appending current telemetry.

        Returns:
            List[str]: List of implicated sensor names.
        """
        if not prior_history:
            return []

        implicated: List[str] = []
        curr_ts = self.causal_engine._extract_float(telemetry, "timestamp")

        for ch in self.TEMPORAL_CHANNELS:
            val = self.causal_engine._extract_float(telemetry, ch)
            if val is None:
                continue

            probe: Dict[str, Any] = {ch: val}
            if curr_ts is not None:
                probe["timestamp"] = curr_ts

            if not self.causal_engine.check_temporal_continuity(probe, history=prior_history):
                implicated.append(ch)

        return implicated

    def _identify_cross_consistency_implicated_sensors(
        self,
        telemetry: Any,
        prior_history: Sequence[Any],
    ) -> List[str]:
        """Identifies sensor channel(s) triggering a cross-sensor consistency contradiction.

        Uses CausalEngine's check_sensor_cross_consistency to evaluate relationship groups
        against the prior baseline without duplicating physical formulas or thresholds.

        Args:
            telemetry: Current reported telemetry snapshot.
            prior_history: Telemetry history snapshot prior to appending current telemetry.

        Returns:
            List[str]: Implicated sensor names.
        """
        implicated: Set[str] = set()

        # Group 1: Pump State Consensus
        status = self.causal_engine._extract_status(telemetry, "pump_status")
        speed = self.causal_engine._extract_float(telemetry, "pump_speed")
        flow = self.causal_engine._extract_float(telemetry, "water_flow")
        pressure = self.causal_engine._extract_float(telemetry, "pressure")

        if status is not None and speed is not None and flow is not None and pressure is not None:
            probe_pump = {
                "pump_status": status,
                "pump_speed": speed,
                "water_flow": flow,
                "pressure": pressure,
            }
            if not self.causal_engine.check_sensor_cross_consistency(probe_pump, history=prior_history):
                implicated.update(["pump_status", "pump_speed", "water_flow", "pressure"])

        # Group 2: Thermal State Consensus
        temp = self.causal_engine._extract_float(telemetry, "temperature")
        solar = self.causal_engine._extract_float(telemetry, "solar_radiation")
        cooling = self.causal_engine._extract_float(telemetry, "cooling_load")
        power = self.causal_engine._extract_float(telemetry, "power_consumption")

        if temp is not None and solar is not None and cooling is not None:
            # Check 2A / 2B (solar vs temp divergence)
            probe_thermal_dyn = {
                "temperature": temp,
                "solar_radiation": solar,
                "cooling_load": cooling,
                "power_consumption": 9999.0,  # Ensure 2C (zero power) doesn't mask 2A/2B
            }
            if not self.causal_engine.check_sensor_cross_consistency(probe_thermal_dyn, history=prior_history):
                implicated.update(["temperature", "solar_radiation", "cooling_load"])

            # Check 2C (active cooling without electrical power)
            if power is not None:
                cooling_tol = self.causal_engine.cross_consistency_config.get(
                    "cooling_response_tolerance", 0.2
                )
                if cooling > cooling_tol and power <= 0.0:
                    implicated.update(["cooling_load", "power_consumption"])

        # Group 3: Water System Consensus
        tank = self.causal_engine._extract_float(telemetry, "tank_level")
        if flow is not None and tank is not None:
            probe_water: Dict[str, Any] = {"water_flow": flow, "tank_level": tank}
            if pressure is not None:
                probe_water["pressure"] = pressure

            if not self.causal_engine.check_sensor_cross_consistency(probe_water, history=prior_history):
                min_suction = self.causal_engine.cross_consistency_config.get("min_tank_suction", 0.1)
                if tank <= min_suction and pressure is not None:
                    implicated.update(["tank_level", "water_flow", "pressure"])
                else:
                    implicated.update(["tank_level", "water_flow"])

        return sorted(list(implicated))

    def evaluate(self, telemetry: Any) -> Dict[str, Any]:
        """Evaluates one reported telemetry snapshot through the full defense pipeline.

        Args:
            telemetry: Reported telemetry snapshot (dictionary or object).

        Returns:
            Dict[str, Any]: Structured defense outcome adhering strictly to contract:
                - anomaly_detected: bool
                - violated_invariants: List[str]
                - sensor_trust_scores: Dict[str, float]
                - system_trust_score: float
                - risk_level: str
                - explanation: str
                - recommended_action: str
        """
        # 1. Capture snapshot of historical baseline prior to evaluation
        prior_history = list(self.causal_engine.history)

        # 2. Evaluate physical invariants via CausalEngine
        causal_result = self.causal_engine.evaluate(telemetry)
        violated_invariants = causal_result.get("violated_invariants", [])
        anomaly_detected = causal_result.get("anomaly_detected", False)

        # 3. Determine implicated sensors strictly from causal evidence
        implicated: Set[str] = set()
        if "THERMODYNAMIC_BALANCE" in violated_invariants:
            implicated.update(self.THERMAL_SENSORS)

        if "ACTUATOR_ENERGY_COUPLING" in violated_invariants:
            implicated.update(self.ACTUATOR_SENSORS)

        if "TEMPORAL_CONTINUITY" in violated_invariants:
            temporal_sensors = self._identify_temporal_implicated_sensors(telemetry, prior_history)
            implicated.update(temporal_sensors)

        if "SENSOR_CROSS_CONSISTENCY" in violated_invariants:
            cross_sensors = self._identify_cross_consistency_implicated_sensors(telemetry, prior_history)
            implicated.update(cross_sensors)

        # 4. Update TrustEngine dynamically
        if violated_invariants:
            implicated_list = sorted(list(implicated))
            self.trust_engine.update_from_violations(
                violated_invariants,
                implicated_sensors=implicated_list,
            )
        else:
            self.trust_engine.update_from_violations([])

        # 5. Retrieve current trust metrics and operational risk level
        sensor_trust_scores = self.trust_engine.get_sensor_trust()
        system_trust_score = self.trust_engine.get_system_trust_score()
        risk_level = self.trust_engine.get_risk_level()

        # 6. Generate forensic explanation and defensive recommendation
        explanation = self.detective_explainer.explain(
            violated_invariants=violated_invariants,
            sensor_trust_scores=sensor_trust_scores,
            system_trust_score=system_trust_score,
            risk_level=risk_level,
        )
        recommended_action = self.detective_explainer.recommend_action(
            violated_invariants=violated_invariants,
            sensor_trust_scores=sensor_trust_scores,
            system_trust_score=system_trust_score,
            risk_level=risk_level,
        )

        # 7. Return strictly contracted defense dictionary
        return {
            "anomaly_detected": anomaly_detected,
            "violated_invariants": violated_invariants,
            "sensor_trust_scores": sensor_trust_scores,
            "system_trust_score": system_trust_score,
            "risk_level": risk_level,
            "explanation": explanation,
            "recommended_action": recommended_action,
        }
