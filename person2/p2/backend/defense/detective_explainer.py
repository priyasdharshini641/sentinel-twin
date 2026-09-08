"""Detective Explainer module.

Converts detected physical invariant violations, sensor trust scores, and risk
levels into concise, neutral forensic explanations and defensive operational
recommendations. Operates strictly on established defense engine outputs without
attack metadata, ground truth, or attack classification.
"""

from typing import Dict, List, Optional, Sequence


class DetectiveExplainer:
    """Generates plain-English explanations and defensive recommendations from defense outputs."""

    # Standard invariant explanation clauses
    INVARIANT_EXPLANATIONS: Dict[str, str] = {
        "THERMODYNAMIC_BALANCE": (
            "Telemetry is inconsistent with the expected thermal relationship between "
            "environmental conditions, temperature, cooling demand, and power."
        ),
        "ACTUATOR_ENERGY_COUPLING": (
            "Pump-related telemetry is inconsistent across pump state, speed, flow, "
            "pressure, and power."
        ),
        "TEMPORAL_CONTINUITY": (
            "Telemetry shows an abnormal change relative to recent system behavior."
        ),
        "SENSOR_CROSS_CONSISTENCY": (
            "Related sensors are reporting values that are inconsistent with one another."
        ),
    }

    # Standard invariant operational recommendations
    INVARIANT_RECOMMENDATIONS: Dict[str, str] = {
        "THERMODYNAMIC_BALANCE": (
            "Review the low-trust thermal telemetry and validate the affected environmental "
            "and cooling sensors."
        ),
        "ACTUATOR_ENERGY_COUPLING": (
            "Validate pump state, speed, flow, pressure, and power telemetry before relying "
            "on the actuator state."
        ),
        "TEMPORAL_CONTINUITY": (
            "Review the affected telemetry against recent readings and investigate persistent "
            "deviations."
        ),
        "SENSOR_CROSS_CONSISTENCY": (
            "Cross-check the related sensors and validate the inconsistent measurements."
        ),
    }

    # Risk level contextual explanation sentences
    RISK_EXPLANATIONS: Dict[str, str] = {
        "LOW": "Current telemetry shows a detected inconsistency, but overall system trust remains high.",
        "MEDIUM": "Detected inconsistencies have reduced overall system trust to a moderate-risk state.",
        "HIGH": "Detected inconsistencies have significantly reduced system trust and require investigation.",
        "CRITICAL": "System trust is critically low and the affected telemetry should be treated as unreliable.",
    }

    # Risk level operational action guidance
    RISK_RECOMMENDATIONS: Dict[str, str] = {
        "HIGH": "Prioritize investigation of low-trust telemetry before using it for automated control decisions.",
        "CRITICAL": "Isolate or reject low-trust telemetry from automated control decisions until the measurements are validated.",
    }

    def explain(
        self,
        violated_invariants: Optional[Sequence[str]] = None,
        sensor_trust_scores: Optional[Dict[str, float]] = None,
        system_trust_score: Optional[float] = None,
        risk_level: Optional[str] = None,
    ) -> str:
        """Produces a concise, neutral plain-English explanation of detected inconsistencies.

        Args:
            violated_invariants: Sequence of violated physical invariant names.
            sensor_trust_scores: Optional mapping of sensor names to trust scores (0-100).
            system_trust_score: Optional overall system trust score (0-100).
            risk_level: Optional operational risk level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').

        Returns:
            str: Deterministic, neutral plain-English explanation.
        """
        invariants = list(violated_invariants) if violated_invariants is not None else []

        # If no invariants are violated, system is physically consistent
        if not invariants:
            return "Telemetry is consistent with the currently evaluated physical relationships."

        parts: List[str] = []

        # 1. Primary invariant evidence
        invariant_texts: List[str] = []
        for inv in invariants:
            if inv in self.INVARIANT_EXPLANATIONS:
                invariant_texts.append(self.INVARIANT_EXPLANATIONS[inv])
            else:
                invariant_texts.append(
                    f"An unspecified consistency condition ({inv}) was violated."
                )

        parts.append(" ".join(invariant_texts))

        # 2. Sensor trust context (identify sensors with low trust < 50 without accusatory language)
        if sensor_trust_scores:
            low_trust_sensors = [
                s for s, score in sensor_trust_scores.items()
                if score is not None and score < 50.0
            ]
            if low_trust_sensors:
                low_trust_sensors.sort()
                sensor_list_str = ", ".join(low_trust_sensors)
                if len(low_trust_sensors) == 1:
                    sensor_display = low_trust_sensors[0].replace("_", " ").capitalize()
                    parts.append(
                        f"{sensor_display} telemetry has low trust and is contributing "
                        f"to the detected inconsistency."
                    )
                else:
                    parts.append(
                        f"Low-trust telemetry identified for {sensor_list_str}, contributing "
                        f"to the detected inconsistency."
                    )

        # 3. Risk level context (if provided and recognized)
        if risk_level and risk_level.upper() in self.RISK_EXPLANATIONS:
            parts.append(self.RISK_EXPLANATIONS[risk_level.upper()])

        return " ".join(parts)

    def recommend_action(
        self,
        violated_invariants: Optional[Sequence[str]] = None,
        sensor_trust_scores: Optional[Dict[str, float]] = None,
        system_trust_score: Optional[float] = None,
        risk_level: Optional[str] = None,
    ) -> str:
        """Provides defensive, non-destructive operational recommendations.

        Args:
            violated_invariants: Sequence of violated physical invariant names.
            sensor_trust_scores: Optional mapping of sensor names to trust scores (0-100).
            system_trust_score: Optional overall system trust score (0-100).
            risk_level: Optional operational risk level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').

        Returns:
            str: Deterministic defensive operational recommendation.
        """
        invariants = list(violated_invariants) if violated_invariants is not None else []

        # If no invariants are violated, maintain normal monitoring
        if not invariants:
            return "Continue monitoring the system."

        recs: List[str] = []

        # 1. Specific invariant-based operational actions
        for inv in invariants:
            if inv in self.INVARIANT_RECOMMENDATIONS:
                recs.append(self.INVARIANT_RECOMMENDATIONS[inv])
            else:
                recs.append(
                    "Inspect the affected telemetry and verify physical sensor readings."
                )

        # 2. Risk-based operational safeguards (e.g. HIGH, CRITICAL)
        if risk_level and risk_level.upper() in self.RISK_RECOMMENDATIONS:
            recs.append(self.RISK_RECOMMENDATIONS[risk_level.upper()])

        return " ".join(recs)
