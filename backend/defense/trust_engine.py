"""Trust Engine module.

Maintains and dynamically updates trust scores for individual physical telemetry
sensors based on evidence from invariant evaluation, derives overall system trust,
and maps system trust to operational risk levels. Operates without access to
attack ground-truth or simulation metadata.
"""

from typing import Dict, List, Optional, Sequence, Set


class TrustEngine:
    """Manages sensor trust scores, penalty applications, recovery, system trust, and risk levels."""

    # Exactly 10 physical sensors from the frozen shared contract (timestamp excluded)
    KNOWN_SENSORS: List[str] = [
        "temperature",
        "humidity",
        "solar_radiation",
        "cooling_load",
        "power_consumption",
        "water_flow",
        "tank_level",
        "pump_status",
        "pump_speed",
        "pressure",
    ]

    # Default invariant-to-sensor mapping:
    # - THERMODYNAMIC_BALANCE maps to thermal subsystem sensors.
    # - ACTUATOR_ENERGY_COUPLING maps to actuator/hydraulic subsystem sensors.
    # - TEMPORAL_CONTINUITY and SENSOR_CROSS_CONSISTENCY do NOT blindly penalize
    #   broad sensor sets by default; they rely on precise evidence (implicated_sensors)
    #   or conservative user-configured mappings.
    DEFAULT_INVARIANT_MAP: Dict[str, List[str]] = {
        "THERMODYNAMIC_BALANCE": [
            "temperature",
            "solar_radiation",
            "cooling_load",
            "power_consumption",
            "humidity",
        ],
        "ACTUATOR_ENERGY_COUPLING": [
            "pump_status",
            "pump_speed",
            "water_flow",
            "pressure",
            "power_consumption",
        ],
        "TEMPORAL_CONTINUITY": [],
        "SENSOR_CROSS_CONSISTENCY": [],
    }

    def __init__(
        self,
        trust_config: Optional[Dict[str, float]] = None,
        invariant_map: Optional[Dict[str, Sequence[str]]] = None,
        sensor_weights: Optional[Dict[str, float]] = None,
        risk_thresholds: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initializes the TrustEngine with default trust scores.

        Args:
            trust_config: Optional dictionary of configurable trust parameters.
            invariant_map: Optional mapping of invariant names to implicated sensors.
            sensor_weights: Optional dictionary of weights for system trust derivation.
            risk_thresholds: Optional dictionary of thresholds for risk level mapping.
        """
        # Configurable trust dynamics parameters
        self.trust_config: Dict[str, float] = {
            "default_trust": 100.0,
            "minimum_trust": 0.0,
            "maximum_trust": 100.0,
            "base_penalty": 15.0,
            "recovery_amount": 2.0,
        }
        if trust_config:
            self.trust_config.update(trust_config)

        # Invariant-to-sensor mapping (configurable)
        self.invariant_map: Dict[str, List[str]] = {
            k: list(v) for k, v in self.DEFAULT_INVARIANT_MAP.items()
        }
        if invariant_map:
            for k, v in invariant_map.items():
                self.invariant_map[k] = list(v)

        # Configurable sensor weights for system trust calculation (defaults to 1.0 each)
        self.sensor_weights: Dict[str, float] = {
            sensor: 1.0 for sensor in self.KNOWN_SENSORS
        }
        if sensor_weights:
            for s, w in sensor_weights.items():
                if s in self.KNOWN_SENSORS and w >= 0.0:
                    self.sensor_weights[s] = float(w)

        # Configurable risk thresholds for mapping system trust score to risk levels
        # Frozen defaults:
        # System Trust 76–100 -> LOW     (score > 75.0)
        # System Trust 51–75  -> MEDIUM  (50.0 < score <= 75.0)
        # System Trust 26–50  -> HIGH    (25.0 < score <= 50.0)
        # System Trust 0–25   -> CRITICAL(score <= 25.0)
        self.risk_thresholds: Dict[str, float] = {
            "low_threshold": 75.0,
            "medium_threshold": 50.0,
            "high_threshold": 25.0,
        }
        if risk_thresholds:
            self.risk_thresholds.update(risk_thresholds)

        # Internal tracking state
        self._scores: Dict[str, float] = {}
        self._consecutive_violations: Dict[str, int] = {}
        self.reset()

    def reset(self) -> None:
        """Restores every sensor trust score to default (100.0) and clears violation state."""
        default_val = self.trust_config["default_trust"]
        self._scores = {sensor: float(default_val) for sensor in self.KNOWN_SENSORS}
        self._consecutive_violations = {sensor: 0 for sensor in self.KNOWN_SENSORS}

    def get_sensor_trust(self) -> Dict[str, float]:
        """Returns the current trust scores for all known sensors.

        Returns:
            Dict[str, float]: Copy of sensor trust scores dictionary.
        """
        return dict(self._scores)

    def get_system_trust_score(self) -> float:
        """Calculates the overall system trust score as a weighted average of sensor trust.

        Returns:
            float: Overall system trust score clamped strictly between 0.0 and 100.0.
        """
        total_weight = sum(self.sensor_weights.get(s, 1.0) for s in self.KNOWN_SENSORS)
        if total_weight <= 0.0:
            # Fallback to unweighted arithmetic mean if all weights are zero
            total_score = sum(self._scores[s] for s in self.KNOWN_SENSORS)
            avg_score = total_score / len(self.KNOWN_SENSORS)
        else:
            weighted_sum = sum(
                self._scores[s] * self.sensor_weights.get(s, 1.0)
                for s in self.KNOWN_SENSORS
            )
            avg_score = weighted_sum / total_weight

        # Strictly clamp within configured trust boundaries
        min_t = self.trust_config["minimum_trust"]
        max_t = self.trust_config["maximum_trust"]
        clamped_score = max(min_t, min(max_t, avg_score))
        return round(clamped_score, 2)

    def get_risk_level(self) -> str:
        """Determines the operational risk level strictly from current system trust.

        Frozen Risk Mapping:
            System Trust 76–100 -> 'LOW'     (score > 75.0)
            System Trust 51–75  -> 'MEDIUM'  (50.0 < score <= 75.0)
            System Trust 26–50  -> 'HIGH'    (25.0 < score <= 50.0)
            System Trust 0–25   -> 'CRITICAL'(score <= 25.0)

        Returns:
            str: Exactly one of 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'.
        """
        score = self.get_system_trust_score()
        low_t = self.risk_thresholds.get("low_threshold", 75.0)
        med_t = self.risk_thresholds.get("medium_threshold", 50.0)
        high_t = self.risk_thresholds.get("high_threshold", 25.0)

        if score > low_t:
            return "LOW"
        elif score > med_t:
            return "MEDIUM"
        elif score > high_t:
            return "HIGH"
        else:
            return "CRITICAL"

    def update_from_violations(
        self,
        violated_invariants: Sequence[str],
        implicated_sensors: Optional[Sequence[str]] = None,
    ) -> Dict[str, float]:
        """Updates sensor trust scores based on detected invariant violations.

        Penalizes implicated sensors and applies gradual recovery to non-implicated
        sensors. All scores are strictly clamped between minimum_trust and maximum_trust.

        Args:
            violated_invariants: Sequence of violated invariant names.
            implicated_sensors: Optional explicit override specifying exactly
                which sensors are implicated. Unknown sensor names are safely ignored.

        Returns:
            Dict[str, float]: Updated sensor trust scores dictionary.
        """
        # Determine the set of sensors to penalize
        penalized_set: Set[str] = set()

        if implicated_sensors is not None:
            # Explicit evidence: only penalize valid known sensors in the list
            for s in implicated_sensors:
                if s in self.KNOWN_SENSORS:
                    penalized_set.add(s)
        else:
            # Fall back to invariant-to-sensor mapping
            for inv in violated_invariants:
                sensors_for_inv = self.invariant_map.get(inv, [])
                for s in sensors_for_inv:
                    if s in self.KNOWN_SENSORS:
                        penalized_set.add(s)

        min_t = self.trust_config["minimum_trust"]
        max_t = self.trust_config["maximum_trust"]
        penalty = self.trust_config["base_penalty"]
        recovery = self.trust_config["recovery_amount"]

        # Update scores for all sensors
        for sensor in self.KNOWN_SENSORS:
            current_score = self._scores[sensor]

            if sensor in penalized_set:
                # Implicated sensor: apply trust penalty
                self._consecutive_violations[sensor] += 1
                new_score = max(min_t, current_score - penalty)
                self._scores[sensor] = round(new_score, 2)
            else:
                # Non-implicated sensor: apply gradual recovery
                self._consecutive_violations[sensor] = 0
                new_score = min(max_t, current_score + recovery)
                self._scores[sensor] = round(new_score, 2)

        return self.get_sensor_trust()

    def get_trust_band(self, sensor_name: str) -> str:
        """Returns the categorical trust band for a given sensor.

        Bands:
            90.0 <= score <= 100.0 -> 'Highly Trusted'
            75.0 <= score < 90.0   -> 'Trusted'
            50.0 <= score < 75.0   -> 'Suspicious'
            25.0 <= score < 50.0   -> 'Low Trust'
            0.0  <= score < 25.0   -> 'Untrusted'

        Args:
            sensor_name: Target sensor identifier.

        Returns:
            str: Trust band category, or 'Unknown' if sensor is unrecognized.
        """
        if sensor_name not in self._scores:
            return "Unknown"

        score = self._scores[sensor_name]
        if score >= 90.0:
            return "Highly Trusted"
        elif score >= 75.0:
            return "Trusted"
        elif score >= 50.0:
            return "Suspicious"
        elif score >= 25.0:
            return "Low Trust"
        else:
            return "Untrusted"
