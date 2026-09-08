"""Causal Reality Engine module.

Evaluates physical invariant compliance on reported telemetry.
Operates strictly on reported telemetry without access to attack ground-truth
or simulation metadata.
"""

from collections import deque
from datetime import datetime
import math
from typing import Any, Dict, List, Optional, Sequence



class CausalEngine:
    """Evaluates physical invariants across reported telemetry to detect anomalies."""

    def __init__(
        self,
        window_size: int = 5,
        thermo_config: Optional[Dict[str, float]] = None,
        actuator_config: Optional[Dict[str, float]] = None,
        temporal_config: Optional[Dict[str, float]] = None,
        cross_consistency_config: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initializes the CausalEngine.

        Args:
            window_size: Number of past telemetry snapshots to retain for
                temporal continuity and rate-of-change analysis. Defaults to 5.
            thermo_config: Optional dictionary of calibratable coefficients for
                thermodynamic balance verification.
            actuator_config: Optional dictionary of calibratable coefficients for
                actuator energy coupling verification.
            temporal_config: Optional dictionary of calibratable coefficients for
                temporal continuity and rate-of-change verification.
            cross_consistency_config: Optional dictionary of calibratable coefficients for
                sensor cross-consistency verification.
        """
        self.window_size: int = window_size
        self.history: deque[Any] = deque(maxlen=window_size)

        # Calibratable thermodynamic consistency parameters.
        # These parameters reflect physical energy balance and relational bounds,
        # designed to be calibrated with normal P1 baseline data.
        self.thermo_config: Dict[str, float] = {
            "min_cop": 0.2,               # Minimum plausible coefficient of performance (cooling_load / power)
            "max_cop": 15.0,              # Maximum plausible coefficient of performance
            "temp_delta_epsilon": 0.05,   # Noise threshold for temperature change significance
            "solar_delta_epsilon": 5.0,   # Noise threshold for solar radiation change significance
            "cooling_delta_epsilon": 0.1, # Noise threshold for cooling load change significance
            "power_delta_epsilon": 0.1,   # Noise threshold for power change significance
        }
        if thermo_config:
            self.thermo_config.update(thermo_config)

        # Calibratable actuator energy coupling parameters.
        # These parameters reflect turbomachinery affinity laws and work-energy coupling,
        # designed to be calibrated with normal P1 baseline data.
        self.actuator_config: Dict[str, float] = {
            "speed_delta_epsilon": 10.0,       # Significant RPM change threshold
            "flow_delta_epsilon": 0.1,        # Significant flow change threshold
            "pressure_delta_epsilon": 0.05,   # Significant pressure change threshold
            "power_delta_epsilon": 0.1,       # Significant power change threshold
            "min_active_speed": 1.0,          # Stopped vs running speed boundary
            "min_active_flow": 0.05,          # Zero vs flowing threshold
            "min_active_pressure": 0.05,      # Ambient vs active pressure threshold
        }
        if actuator_config:
            self.actuator_config.update(actuator_config)

        # Calibratable temporal continuity parameters.
        # Uses recent behavioral baseline (median and scale) to detect abrupt jumps
        # and persistent directional drift.
        self.temporal_config: Dict[str, float] = {
            "max_jump_z": 4.5,            # Z-score multiplier for sudden abrupt jump detection
            "min_jump_delta": 0.5,        # Minimum absolute delta to consider an abrupt jump
            "min_drift_steps": 4.0,       # Minimum consecutive unidirectional steps for drift
            "drift_scale_factor": 2.5,    # Cumulative drift multiplier relative to scale
            "min_drift_delta": 1.0,       # Minimum cumulative absolute delta for drift detection
            "noise_floor": 0.05,          # Baseline noise floor to avoid zero division
            "nominal_dt": 1.0,            # Nominal sampling interval in seconds
        }
        if temporal_config:
            self.temporal_config.update(temporal_config)

        # Calibratable sensor cross-consistency relationship tolerances.
        # These parameters represent relational coupling tolerances to be learned
        # from normal P1 simulation behavior, rather than universal absolute limits.
        self.cross_consistency_config: Dict[str, float] = {
            # Group 1: Pump State Consensus Tolerances
            "min_active_speed": 1.0,               # Calibration threshold for stationary vs rotating pump
            "min_active_flow": 0.05,               # Calibration threshold for zero vs active flow
            "min_active_pressure": 0.05,           # Calibration threshold for ambient vs pressurized line
            "active_speed_threshold": 10.0,        # Calibratable speed threshold (in %) where hydraulic output is expected

            # Group 2: Thermal Cross-Sensor Relational Tolerances
            "solar_change_tolerance": 50.0,        # Minimum solar change considered significant for consensus
            "temp_divergence_tolerance": 0.5,      # Temperature divergence threshold when solar shifts
            "cooling_response_tolerance": 0.2,     # Expected cooling load response margin

            # Group 3: Water System Relational Tolerances
            "min_tank_suction": 0.1,               # Minimum tank suction level required for active flow
            "tank_divergence_tolerance": 2.0,      # Maximum unexpected tank deviation against established trend
        }
        if cross_consistency_config:
            self.cross_consistency_config.update(cross_consistency_config)

    def calibrate_thermodynamics(self, baseline_data: Sequence[Any]) -> None:
        """Calibrates thermodynamic parameters using normal baseline simulation data.

        Args:
            baseline_data: Sequence of uncompromised telemetry snapshots.
        """
        # Placeholder for empirical calibration using normal P1 simulation dataset.
        pass

    def calibrate_actuator(self, baseline_data: Sequence[Any]) -> None:
        """Calibrates actuator coupling parameters using normal baseline simulation data.

        Args:
            baseline_data: Sequence of uncompromised telemetry snapshots.
        """
        # Placeholder for empirical calibration using normal P1 simulation dataset.
        pass

    def calibrate_temporal(self, baseline_data: Sequence[Any]) -> None:
        """Calibrates temporal continuity parameters using normal baseline simulation data.

        Args:
            baseline_data: Sequence of uncompromised telemetry snapshots.
        """
        # Placeholder for empirical calibration using normal P1 simulation dataset.
        pass

    def calibrate_cross_consistency(self, baseline_data: Sequence[Any]) -> None:
        """Calibrates sensor cross-consistency parameters using normal baseline simulation data.

        Learns normal operational thresholds, cross-sensor response margins,
        and behavioral tolerances from uncompromised physical runs.

        Args:
            baseline_data: Sequence of uncompromised telemetry snapshots.
        """
        # Placeholder for empirical calibration using normal P1 simulation dataset.
        pass

    def _extract_float(self, telemetry: Any, key: str) -> Optional[float]:
        """Safely extracts a numeric float value from a telemetry snapshot.

        Supports both dictionary mapping and object attribute access.
        Returns None if key is absent, None, or cannot be parsed as a finite float.
        """
        if telemetry is None:
            return None
        val = None
        if isinstance(telemetry, dict):
            val = telemetry.get(key)
        else:
            val = getattr(telemetry, key, None)
        if val is None:
            return None
        if key == "timestamp":
            if isinstance(val, (int, float)):
                f = float(val)
                return f if not (math.isnan(f) or math.isinf(f)) else None
            if isinstance(val, datetime):
                return val.timestamp()
            if isinstance(val, str):
                try:
                    dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                    return dt.timestamp()
                except Exception:
                    pass
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        except (ValueError, TypeError):
            return None


    def _extract_status(self, telemetry: Any, key: str) -> Optional[int]:
        """Safely extracts a binary status (1 for ON, 0 for OFF) from telemetry.

        Supports bool, numeric, and string representations.
        Returns None if key is absent, None, or unrecognized.
        """
        if telemetry is None:
            return None
        val = None
        if isinstance(telemetry, dict):
            val = telemetry.get(key)
        else:
            val = getattr(telemetry, key, None)
        if val is None:
            return None
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
            return 1 if val > 0.5 else 0
        if isinstance(val, str):
            val_str = val.strip().lower()
            if val_str in ("1", "true", "on", "active", "running"):
                return 1
            if val_str in ("0", "false", "off", "inactive", "stopped"):
                return 0
        return None

    def check_thermodynamic_balance(
        self,
        telemetry: Any,
        history: Optional[Sequence[Any]] = None,
    ) -> bool:
        """Evaluates the THERMODYNAMIC_BALANCE physical invariant.

        Verifies relational consistency between environmental thermal input
        (solar_radiation, temperature, humidity) and cooling effort/energy
        (cooling_load, power_consumption). Detects causal contradictions rather
        than relying on fixed numerical bounds.

        Args:
            telemetry: Current reported telemetry snapshot.
            history: Optional historical telemetry sequence. If omitted,
                self.history is used.

        Returns:
            bool: True if the invariant appears consistent, False if violated.
        """
        # 1. Extract the five relevant telemetry values safely
        temp = self._extract_float(telemetry, "temperature")
        hum = self._extract_float(telemetry, "humidity")
        solar = self._extract_float(telemetry, "solar_radiation")
        cooling = self._extract_float(telemetry, "cooling_load")
        power = self._extract_float(telemetry, "power_consumption")

        # Missing or malformed essential fields indicate inconsistency / failure to verify
        if temp is None or hum is None or solar is None or cooling is None or power is None:
            return False

        # 2. Intra-snapshot physical coupling: Cooling work requires power consumption
        if cooling > self.thermo_config["cooling_delta_epsilon"]:
            if power <= 0.0:
                # Active cooling work reported without power consumption violates First Law
                return False
            cop = cooling / power
            if cop < self.thermo_config["min_cop"] or cop > self.thermo_config["max_cop"]:
                # Coefficient of performance outside physically possible bounds
                return False

        if cooling < 0.0 or power < 0.0 or solar < 0.0 or hum < 0.0:
            # Physical state variables cannot be negative
            return False

        # 3. Inter-snapshot relational consistency (if historical context is available)
        hist = history if history is not None else self.history
        if hist and len(hist) > 0:
            prev = hist[-1]
            prev_temp = self._extract_float(prev, "temperature")
            prev_solar = self._extract_float(prev, "solar_radiation")
            prev_cooling = self._extract_float(prev, "cooling_load")
            prev_power = self._extract_float(prev, "power_consumption")

            # Only proceed with relational comparisons if previous values are valid
            if (
                prev_temp is not None
                and prev_solar is not None
                and prev_cooling is not None
                and prev_power is not None
            ):
                delta_temp = temp - prev_temp
                delta_solar = solar - prev_solar
                delta_cooling = cooling - prev_cooling
                delta_power = power - prev_power

                # Contradiction A: High/steady solar influx, cooling not increased, but temp suddenly plunges
                # (Heat input remains steady while cooling extraction did not increase, so sudden drop is non-causal)
                if (
                    prev_solar > self.thermo_config["solar_delta_epsilon"]
                    and delta_solar >= -self.thermo_config["solar_delta_epsilon"]
                    and delta_cooling <= self.thermo_config["cooling_delta_epsilon"]
                    and delta_temp < -self.thermo_config["temp_delta_epsilon"]
                ):
                    return False

                # Contradiction B: Solar radiation increases significantly, but temperature and cooling move incompatibly
                # (Heat influx rose, cooling did not rise, yet temperature dropped)
                if (
                    delta_solar > self.thermo_config["solar_delta_epsilon"]
                    and delta_cooling <= self.thermo_config["cooling_delta_epsilon"]
                    and delta_temp < -self.thermo_config["temp_delta_epsilon"]
                ):
                    return False

                # Contradiction C: Cooling load surge decoupled from actuator power draw
                # (Significant cooling increase cannot coincide with significant power drop)
                if (
                    delta_cooling > self.thermo_config["cooling_delta_epsilon"]
                    and delta_power < -self.thermo_config["power_delta_epsilon"]
                ):
                    return False

        return True

    def check_actuator_energy_coupling(
        self,
        telemetry: Any,
        history: Optional[Sequence[Any]] = None,
    ) -> bool:
        """Evaluates the ACTUATOR_ENERGY_COUPLING physical invariant.

        Verifies causal consistency between actuator command/state (pump_status, pump_speed),
        hydraulic delivery (water_flow, pressure), and power consumption. Detects contradictions
        such as pump OFF with active flow, pump deceleration with flow surge, or work performed
        without electrical power.

        Args:
            telemetry: Current reported telemetry snapshot.
            history: Optional historical telemetry sequence. If omitted,
                self.history is used.

        Returns:
            bool: True if actuator/energy relationships appear consistent,
                False if violated.
        """
        # 1. Safely extract actuator and hydraulic telemetry fields
        status = self._extract_status(telemetry, "pump_status")
        speed = self._extract_float(telemetry, "pump_speed")
        flow = self._extract_float(telemetry, "water_flow")
        pressure = self._extract_float(telemetry, "pressure")
        power = self._extract_float(telemetry, "power_consumption")

        # Missing or malformed essential fields indicate failure to verify
        if (
            status is None
            or speed is None
            or flow is None
            or pressure is None
            or power is None
        ):
            return False

        # Non-negative physical state constraints
        if speed < 0.0 or flow < 0.0 or pressure < 0.0 or power < 0.0:
            return False

        min_speed = self.actuator_config["min_active_speed"]
        min_flow = self.actuator_config["min_active_flow"]

        # CASE 1: Pump OFF and speed 0, but active pumping/flow is reported
        if status == 0 and speed <= min_speed:
            if flow > min_flow:
                return False

        # CASE 2: Command / Actuator state contradiction
        # Commanded ON but stopped (speed 0) while reporting active flow
        if status == 1 and speed <= min_speed and flow > min_flow:
            return False
        # Commanded OFF but motor spinning at active speed
        if status == 0 and speed > min_speed:
            return False

        # CASE 3: Pump commanded ON and rotating at active operating speed, but zero flow is reported
        active_speed_thresh = self.cross_consistency_config.get("active_speed_threshold", 10.0)
        if status == 1 and speed >= active_speed_thresh and flow <= min_flow:
            return False


        # CASE 4: Active hydraulic work reported without power or without operating speed
        if flow > min_flow:
            if power <= 0.0:
                # Fluid cannot be actively pumped with zero electrical power
                return False
            if speed <= min_speed:
                # Fluid cannot be actively pumped if pump is stopped
                return False

        # Inter-snapshot relational consistency (if historical context is available)
        hist = history if history is not None else self.history
        if hist and len(hist) > 0:
            prev = hist[-1]
            prev_status = self._extract_status(prev, "pump_status")
            prev_speed = self._extract_float(prev, "pump_speed")
            prev_flow = self._extract_float(prev, "water_flow")
            prev_pressure = self._extract_float(prev, "pressure")
            prev_power = self._extract_float(prev, "power_consumption")

            if (
                prev_status is not None
                and prev_speed is not None
                and prev_flow is not None
                and prev_pressure is not None
                and prev_power is not None
            ):
                delta_speed = speed - prev_speed
                delta_flow = flow - prev_flow
                delta_pressure = pressure - prev_pressure
                delta_power = power - prev_power

                speed_eps = self.actuator_config["speed_delta_epsilon"]
                flow_eps = self.actuator_config["flow_delta_epsilon"]
                press_eps = self.actuator_config["pressure_delta_epsilon"]
                power_eps = self.actuator_config["power_delta_epsilon"]

                # CASE 5: Pump speed decreases substantially, but flow or pressure surges
                # (Turbomachinery affinity laws: Q ~ N, P ~ N^2. Deceleration cannot produce higher flow/head)
                if delta_speed < -speed_eps:
                    if delta_flow > flow_eps or delta_pressure > press_eps:
                        return False

                # CASE 3: Pump speed increases substantially, but flow and pressure both collapse
                # or power consumption drops significantly despite higher speed
                if delta_speed > speed_eps:
                    if delta_flow < -flow_eps and delta_pressure < -press_eps:
                        return False
                    if delta_power < -power_eps:
                        return False

                # Additional Energy Coupling: Fluid work surges (both flow and pressure surge)
                # but electrical power consumption drops significantly
                if delta_flow > flow_eps and delta_pressure > press_eps and delta_power < -power_eps:
                    return False

        return True

    def check_temporal_continuity(
        self,
        telemetry: Any,
        history: Optional[Sequence[Any]] = None,
    ) -> bool:
        """Evaluates the TEMPORAL_CONTINUITY physical invariant.

        Determines whether reported telemetry evolves continuously and plausibly
        over time based on recent history. Detects abrupt jumps and gradual
        persistent directional drift without hardcoded absolute sensor limits.

        Args:
            telemetry: Current reported telemetry snapshot.
            history: Optional sequence of prior telemetry snapshots. If None,
                internal history buffer is used.

        Returns:
            bool: True if the invariant holds, False if violated.
        """
        hist = history if history is not None else self.history
        if not hist or len(hist) == 0:
            # Baseline cannot be established on empty history; no violation
            return True

        # Extract timestamp context if available for chronological scaling
        prev_reading = hist[-1]
        prev_ts = self._extract_float(prev_reading, "timestamp")
        curr_ts = self._extract_float(telemetry, "timestamp")

        time_factor = 1.0
        if prev_ts is not None and curr_ts is not None:
            dt = curr_ts - prev_ts
            if dt > 0.0:
                nominal_dt = self.temporal_config.get("nominal_dt", 1.0)
                time_factor = math.sqrt(max(1.0, dt / nominal_dt))

        channels = [
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

        for ch in channels:
            curr_val = self._extract_float(telemetry, ch)
            if curr_val is None:
                continue

            # Gather historical series for this channel
            hist_vals: List[float] = []
            for h in hist:
                v = self._extract_float(h, ch)
                if v is not None:
                    hist_vals.append(v)

            if len(hist_vals) == 0:
                continue

            full_series = hist_vals + [curr_val]
            n_hist = len(hist_vals)

            # Current step relative to previous value
            prev_val = hist_vals[-1]
            raw_step = abs(curr_val - prev_val)
            norm_step = raw_step / time_factor

            # Historical step differences
            hist_steps = [
                abs(hist_vals[i] - hist_vals[i - 1])
                for i in range(1, n_hist)
            ]

            # Robust baseline (median) and scale (MAD) from history
            sorted_hist = sorted(hist_vals)
            mid = n_hist // 2
            median_hist = (
                (sorted_hist[mid - 1] + sorted_hist[mid]) / 2.0
                if n_hist % 2 == 0
                else sorted_hist[mid]
            )

            abs_devs = sorted(abs(v - median_hist) for v in hist_vals)
            mad = (
                (abs_devs[mid - 1] + abs_devs[mid]) / 2.0
                if n_hist % 2 == 0
                else abs_devs[mid]
            )
            robust_sigma = 1.4826 * mad

            step_scale = (
                sorted(hist_steps)[len(hist_steps) // 2]
                if hist_steps
                else 0.0
            )

            noise_floor = self.temporal_config["noise_floor"]
            dynamic_floor = max(noise_floor, 0.01 * (abs(median_hist) + 1.0))
            scale = max(robust_sigma, step_scale, dynamic_floor)

            # 1. Abrupt jump detection
            if n_hist >= 2:
                z_jump = norm_step / scale
                min_jump_delta = max(
                    self.temporal_config["min_jump_delta"], dynamic_floor
                )
                if (
                    z_jump > self.temporal_config["max_jump_z"]
                    and norm_step > min_jump_delta
                ):
                    return False

            # 2. Gradual persistent directional drift detection
            deltas = [
                full_series[i] - full_series[i - 1]
                for i in range(1, len(full_series))
            ]
            if len(deltas) >= int(self.temporal_config["min_drift_steps"]):
                epsilon = self.temporal_config["noise_floor"] * 0.5
                significant_deltas = [d for d in deltas if abs(d) > epsilon]

                if len(significant_deltas) >= int(self.temporal_config["min_drift_steps"]):
                    all_positive = all(d > 0 for d in significant_deltas)
                    all_negative = all(d < 0 for d in significant_deltas)

                    if all_positive or all_negative:
                        cumulative_drift = abs(full_series[-1] - full_series[0])
                        min_drift_delta = max(
                            self.temporal_config["min_drift_delta"], dynamic_floor
                        )
                        drift_ratio = cumulative_drift / scale
                        if (
                            drift_ratio >= self.temporal_config["drift_scale_factor"]
                            and cumulative_drift >= min_drift_delta
                        ):
                            return False

        return True

    def check_sensor_cross_consistency(
        self,
        telemetry: Any,
        history: Optional[Sequence[Any]] = None,
    ) -> bool:
        """Evaluates the SENSOR_CROSS_CONSISTENCY physical invariant.

        Determines whether related sensors collectively agree about the physical
        operating state across three relationship groups using calibratable
        relational tolerances and recent history baselines:
        1. Pump State (pump_status, pump_speed, water_flow, pressure)
        2. Thermal State (temperature, solar_radiation, cooling_load, power)
        3. Water System (water_flow, tank_level, pressure)

        Args:
            telemetry: Current reported telemetry snapshot.
            history: Optional historical telemetry sequence. If omitted,
                self.history is used.

        Returns:
            bool: True if cross-sensor relationships appear consistent,
                False if a cross-sensor contradiction is detected.
        """
        hist = history if history is not None else self.history

        # Safely extract relevant sensor values
        status = self._extract_status(telemetry, "pump_status")
        speed = self._extract_float(telemetry, "pump_speed")
        flow = self._extract_float(telemetry, "water_flow")
        pressure = self._extract_float(telemetry, "pressure")
        power = self._extract_float(telemetry, "power_consumption")

        temp = self._extract_float(telemetry, "temperature")
        solar = self._extract_float(telemetry, "solar_radiation")
        cooling = self._extract_float(telemetry, "cooling_load")
        tank = self._extract_float(telemetry, "tank_level")

        cfg = self.cross_consistency_config
        min_speed = cfg["min_active_speed"]
        min_flow = cfg["min_active_flow"]
        min_press = cfg["min_active_pressure"]

        # ==========================================================
        # RELATIONSHIP GROUP 1: Pump State Consensus
        # ==========================================================
        if status is not None and speed is not None and flow is not None and pressure is not None:
            # Contradiction 1A: Supervisory command and tachometer report stopped/OFF,
            # while flowmeter and pressure transducer report active pumping
            if status == 0 and speed <= min_speed:
                if flow > min_flow and pressure > min_press:
                    return False

            # Contradiction 1B: Pump is commanded ON at running operating speed,
            # but hydraulic delivery is entirely absent
            active_speed_thresh = cfg.get("active_speed_threshold", 1000.0)
            if status == 1 and speed >= active_speed_thresh:
                if flow <= min_flow and pressure <= min_press:
                    return False

        # ==========================================================
        # RELATIONSHIP GROUP 2: Thermal State Consensus
        # Evaluated relative to established recent baseline rather than universal limits
        # ==========================================================
        if temp is not None and solar is not None and cooling is not None:
            if hist and len(hist) > 0:
                prev = hist[-1]
                prev_temp = self._extract_float(prev, "temperature")
                prev_solar = self._extract_float(prev, "solar_radiation")
                prev_cooling = self._extract_float(prev, "cooling_load")

                if prev_temp is not None and prev_solar is not None and prev_cooling is not None:
                    delta_solar = solar - prev_solar
                    delta_temp = temp - prev_temp
                    delta_cooling = cooling - prev_cooling

                    solar_tol = cfg.get("solar_change_tolerance", 50.0)
                    temp_tol = cfg.get("temp_divergence_tolerance", 0.5)
                    cooling_tol = cfg.get("cooling_response_tolerance", 0.2)

                    # Contradiction 2A: Solar influx increases significantly, but temperature drops
                    # significantly without a corresponding increase in cooling extraction.
                    # Solar sensor says heat input rose, cooling sensor says heat extraction didn't rise,
                    # yet temperature sensor reports significant cooling. The three sensors collectively disagree.
                    if (
                        delta_solar > solar_tol
                        and delta_temp < -temp_tol
                        and delta_cooling <= cooling_tol
                    ):
                        return False

                    # Contradiction 2B: Solar influx drops significantly, but temperature rises
                    # significantly while cooling extraction increased.
                    if (
                        delta_solar < -solar_tol
                        and delta_temp > temp_tol
                        and delta_cooling > cooling_tol
                    ):
                        return False

            # Contradiction 2C: Active cooling load claimed, but electrical power is completely absent
            if power is not None:
                cooling_tol = cfg.get("cooling_response_tolerance", 0.2)
                if cooling > cooling_tol and power <= 0.0:
                    return False

        # ==========================================================
        # RELATIONSHIP GROUP 3: Water System Consensus
        # Evaluated relative to established recent trend rather than universal limits
        # ==========================================================
        if flow is not None and tank is not None:
            min_suction = cfg.get("min_tank_suction", 0.1)

            # Contradiction 3A: Active flow and pressure reported from an empty/unprimed tank
            if tank <= min_suction and flow > min_flow:
                if pressure is not None and pressure > min_press:
                    return False

            # Contradiction 3B: Sustained water delivery while tank behavior contradicts recent operating trend
            if hist and len(hist) >= 2:
                recent_flows = [self._extract_float(h, "water_flow") for h in hist]
                valid_flows = [f for f in recent_flows if f is not None]

                if len(valid_flows) >= 2 and all(f > min_flow for f in valid_flows) and flow > min_flow:
                    hist_tanks = [self._extract_float(h, "tank_level") for h in hist]
                    valid_tanks = [tl for tl in hist_tanks if tl is not None]

                    if len(valid_tanks) >= 2:
                        prev_tank = valid_tanks[-1]
                        tank_delta = tank - prev_tank
                        tank_divergence = cfg.get("tank_divergence_tolerance", 2.0)

                        # If historical trend under sustained delivery was steady or declining,
                        # an abrupt tank surge contradicts the flow delivery state
                        hist_net_change = valid_tanks[-1] - valid_tanks[0]
                        if hist_net_change <= 0.1 and tank_delta > tank_divergence:
                            return False

        return True

    def evaluate(
        self,
        telemetry: Any,
        history: Optional[Sequence[Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluates reported telemetry snapshot against physical invariants.

        Args:
            telemetry: Current reported telemetry snapshot.
            history: Optional historical telemetry sequence for temporal analysis.

        Returns:
            Dict[str, Any]: Evaluation result containing:
                - 'anomaly_detected': bool indicating whether any invariant was breached.
                - 'violated_invariants': list of violated invariant identifiers.
        """
        violated_invariants: List[str] = []

        # 1. Evaluate THERMODYNAMIC_BALANCE invariant
        if not self.check_thermodynamic_balance(telemetry, history=history):
            violated_invariants.append("THERMODYNAMIC_BALANCE")

        # 2. Evaluate ACTUATOR_ENERGY_COUPLING invariant
        if not self.check_actuator_energy_coupling(telemetry, history=history):
            violated_invariants.append("ACTUATOR_ENERGY_COUPLING")

        # 3. Evaluate TEMPORAL_CONTINUITY invariant
        if not self.check_temporal_continuity(telemetry, history=history):
            violated_invariants.append("TEMPORAL_CONTINUITY")

        # 4. Evaluate SENSOR_CROSS_CONSISTENCY invariant
        if not self.check_sensor_cross_consistency(telemetry, history=history):
            violated_invariants.append("SENSOR_CROSS_CONSISTENCY")

        # Append current telemetry snapshot to rolling history window AFTER all evaluations
        self.history.append(telemetry)

        anomaly_detected = len(violated_invariants) > 0
        return {
            "anomaly_detected": anomaly_detected,
            "violated_invariants": violated_invariants,
        }
