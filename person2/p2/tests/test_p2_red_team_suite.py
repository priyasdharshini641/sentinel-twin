import copy
import unittest
from dataclasses import FrozenInstanceError

from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.base_attack import BaseAttack
from backend.attacks.false_injection import FalseInjection
from backend.attacks.gradual_drift import GradualDrift
from backend.attacks.pump_flow_attack import (
    PumpFlowAttack,
    PUMP_RELATED_FIELDS,
    SCENARIO_PUMP_OFF_HIGH_FLOW,
    SCENARIO_PUMP_ON_LOW_ENERGY,
)
from backend.attacks.coordinated_attack import (
    CoordinatedAttack,
    SCENARIO_THERMAL,
    SCENARIO_PUMP,
    THERMAL_COORDINATED_FIELDS,
    PUMP_COORDINATED_FIELDS,
)
from backend.attacks.controller import AttackController


class TestP2RedTeamSuite(unittest.TestCase):
    """Complete P2 Attack / Red Team Test Suite.

    Validates only attack behavior and contract compliance.
    Does NOT implement or test P3 defense, anomaly detection, or risk scoring.
    """

    def setUp(self):
        # Baseline ground truth telemetry representing healthy operating state
        self.ground_truth = Telemetry(
            temperature=38.0,
            humidity=55.0,
            solar_radiation=850.0,
            cooling_load=15.0,
            power_consumption=20.0,
            water_flow=50.0,
            tank_level=75.0,
            pump_status="ON",
            pump_speed=80.0,
            pressure=3.5,
            timestamp="2026-09-07T12:00:00Z",
        )

        # Baseline ground truth telemetry with pump OFF
        self.ground_truth_pump_off = Telemetry(
            temperature=24.0,
            humidity=50.0,
            solar_radiation=400.0,
            cooling_load=5.0,
            power_consumption=0.0,
            water_flow=0.0,
            tank_level=80.0,
            pump_status="OFF",
            pump_speed=0.0,
            pressure=0.5,
            timestamp="2026-09-07T08:00:00Z",
        )

    # =========================================================================
    # TEST 1 — NORMAL (Attack inactive)
    # =========================================================================
    def test_1_normal_inactive_attack(self):
        """TEST 1 — NORMAL: Attack inactive.

        Expected:
        - Reported telemetry equals ground truth in values.
        - Ground truth remains unchanged.
        """
        controller = AttackController(
            {
                "active": False,
                "type": "FALSE_INJECTION",
                "target": "temperature",
                "intensity": 0.8,
            }
        )

        original_snapshot = copy.deepcopy(self.ground_truth.to_dict())
        reported = controller.apply(self.ground_truth)

        # Reported telemetry equals ground truth in values
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        self.assertEqual(reported.temperature, 38.0)

        # Ground truth remains completely unchanged
        self.assertEqual(self.ground_truth.to_dict(), original_snapshot)
        self.assertEqual(self.ground_truth.temperature, 38.0)

        # Reported is a separate Telemetry object
        self.assertIsNot(reported, self.ground_truth)

    # =========================================================================
    # TEST 2 — FALSE INJECTION
    # =========================================================================
    def test_2_false_injection(self):
        """TEST 2 — FALSE INJECTION: Target temperature.

        Example:
        - ground_truth temperature = 38
        Expected:
        - reported temperature is manipulated.
        - All unrelated fields remain unchanged.
        - ground_truth remains 38.
        """
        attack = FalseInjection(target="temperature", intensity=0.8)
        reported = attack.apply(self.ground_truth)

        # Reported temperature is manipulated (38.0 -> 30.0)
        self.assertNotEqual(reported.temperature, self.ground_truth.temperature)
        self.assertEqual(reported.temperature, 30.0)

        # All unrelated fields remain unchanged
        for field in FROZEN_TELEMETRY_FIELDS:
            if field != "temperature":
                self.assertEqual(
                    getattr(reported, field),
                    getattr(self.ground_truth, field),
                    f"Unrelated field '{field}' was modified!",
                )

        # Ground truth remains 38
        self.assertEqual(self.ground_truth.temperature, 38.0)
        self.assertIsNot(reported, self.ground_truth)

    # =========================================================================
    # TEST 3 — GRADUAL DRIFT
    # =========================================================================
    def test_3_gradual_drift(self):
        """TEST 3 — GRADUAL DRIFT: Repeatedly apply attack.

        Expected:
        - Target value changes progressively rather than jumping immediately
          to the final value.
        - reset() restores attack state.
        """
        attack = GradualDrift(
            target="temperature",
            drift_rate=0.75,
            direction=-1.0,
            final_value=35.0,
        )

        readings = []
        for _ in range(4):
            r = attack.apply(self.ground_truth)
            readings.append(r.temperature)

        # 1. Target value changes progressively without jumping directly to 35.0
        self.assertAlmostEqual(readings[0], 37.25, places=2)
        self.assertAlmostEqual(readings[1], 36.50, places=2)
        self.assertAlmostEqual(readings[2], 35.75, places=2)
        self.assertAlmostEqual(readings[3], 35.00, places=2)

        # Strictly monotonic decrease towards manipulated value
        self.assertGreater(readings[0], readings[1])
        self.assertGreater(readings[1], readings[2])
        self.assertGreater(readings[2], readings[3])

        # 2. reset() restores attack state
        attack.reset()
        r_after_reset = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r_after_reset.temperature, readings[0], places=2)

        # Ground truth untouched
        self.assertEqual(self.ground_truth.temperature, 38.0)

    # =========================================================================
    # TEST 4 — PUMP/FLOW ATTACK
    # =========================================================================
    def test_4_pump_flow_attack(self):
        """TEST 4 — PUMP/FLOW ATTACK.

        Expected:
        - Pump-related telemetry fields are manipulated according to selected scenario.
        - Unrelated fields remain unchanged.
        - Ground truth remains unchanged.
        """
        # Scenario A: Pump OFF but reported flow/pressure remain high
        attack_off = PumpFlowAttack(
            scenario=SCENARIO_PUMP_OFF_HIGH_FLOW,
            intensity=1.0,
        )
        reported_off = attack_off.apply(self.ground_truth_pump_off)

        self.assertEqual(reported_off.pump_status, "OFF")
        self.assertEqual(reported_off.pump_speed, 0.0)
        self.assertGreater(reported_off.water_flow, 40.0)
        self.assertGreater(reported_off.pressure, 3.0)

        # Unrelated fields remain unchanged
        unrelated_off = FROZEN_TELEMETRY_FIELDS - PUMP_RELATED_FIELDS
        for field in unrelated_off:
            self.assertEqual(
                getattr(reported_off, field),
                getattr(self.ground_truth_pump_off, field),
                f"Unrelated field '{field}' was modified in pump OFF attack!",
            )

        # Scenario B: Pump ON but reported power consumption is abnormally low
        attack_on = PumpFlowAttack(
            scenario=SCENARIO_PUMP_ON_LOW_ENERGY,
            intensity=1.0,
        )
        reported_on = attack_on.apply(self.ground_truth)

        self.assertEqual(reported_on.pump_status, "ON")
        self.assertLess(reported_on.power_consumption, 4.0)

        unrelated_on = FROZEN_TELEMETRY_FIELDS - PUMP_RELATED_FIELDS
        for field in unrelated_on:
            self.assertEqual(
                getattr(reported_on, field),
                getattr(self.ground_truth, field),
                f"Unrelated field '{field}' was modified in pump ON attack!",
            )

        # Ground truths remain unchanged
        self.assertEqual(self.ground_truth_pump_off.water_flow, 0.0)
        self.assertEqual(self.ground_truth.power_consumption, 20.0)

    # =========================================================================
    # TEST 5 — COORDINATED ATTACK
    # =========================================================================
    def test_5_coordinated_attack(self):
        """TEST 5 — COORDINATED ATTACK.

        Expected:
        - Multiple selected telemetry fields change together.
        - Unrelated fields remain unchanged.
        - Ground truth remains unchanged.
        """
        attack = CoordinatedAttack(
            scenario=SCENARIO_THERMAL,
            intensity=1.0,
            direction=-1.0,
        )
        reported = attack.apply(self.ground_truth)

        # 1. Multiple selected thermal fields change together in coordinated lockstep
        self.assertLess(reported.temperature, self.ground_truth.temperature)
        self.assertLess(reported.solar_radiation, self.ground_truth.solar_radiation)
        self.assertLess(reported.cooling_load, self.ground_truth.cooling_load)
        self.assertLess(reported.power_consumption, self.ground_truth.power_consumption)

        # 2. Unrelated fields remain unchanged
        unrelated_thermal = FROZEN_TELEMETRY_FIELDS - THERMAL_COORDINATED_FIELDS
        for field in unrelated_thermal:
            self.assertEqual(
                getattr(reported, field),
                getattr(self.ground_truth, field),
                f"Unrelated field '{field}' was modified in coordinated attack!",
            )

        # 3. Ground truth remains unchanged
        self.assertEqual(self.ground_truth.temperature, 38.0)
        self.assertEqual(self.ground_truth.solar_radiation, 850.0)

    # =========================================================================
    # TEST 6 — GROUND TRUTH IMMUTABILITY
    # =========================================================================
    def test_6_ground_truth_immutability(self):
        """TEST 6 — GROUND TRUTH IMMUTABILITY.

        For every attack:
            original = copy(ground_truth)
            reported = attack.apply(ground_truth)
        Assert:
            ground_truth == original
        """
        attacks = [
            FalseInjection(target="temperature", intensity=1.0),
            GradualDrift(target="pressure", drift_rate=0.5),
            PumpFlowAttack(scenario=SCENARIO_PUMP_OFF_HIGH_FLOW),
            PumpFlowAttack(scenario=SCENARIO_PUMP_ON_LOW_ENERGY),
            CoordinatedAttack(scenario=SCENARIO_THERMAL),
            CoordinatedAttack(scenario=SCENARIO_PUMP),
            AttackController(
                {
                    "active": True,
                    "type": "FALSE_INJECTION",
                    "target": "humidity",
                    "intensity": 0.5,
                }
            ),
            AttackController({"active": False}),
        ]

        for attack in attacks:
            with self.subTest(attack=attack.name if hasattr(attack, "name") else "Controller"):
                original = copy.deepcopy(self.ground_truth)
                reported = attack.apply(self.ground_truth)

                # Ground truth must be identical to original in values and fields
                self.assertEqual(self.ground_truth, original)
                self.assertEqual(self.ground_truth.to_dict(), original.to_dict())
                self.assertIsNot(reported, self.ground_truth)

        # Direct in-place mutation must be impossible
        with self.assertRaises(FrozenInstanceError):
            self.ground_truth.temperature = 99.9

    # =========================================================================
    # TEST 7 — STOP ATTACK
    # =========================================================================
    def test_7_stop_attack(self):
        """TEST 7 — STOP ATTACK.

        After stopping/disabling the attack:
        - Reported telemetry returns to normal unmodified telemetry.
        """
        controller = AttackController(
            {
                "active": True,
                "type": "FALSE_INJECTION",
                "target": "temperature",
                "intensity": 0.8,
            }
        )

        # While active: temperature is manipulated
        r_active = controller.apply(self.ground_truth)
        self.assertEqual(r_active.temperature, 30.0)

        # Stop the attack
        controller.stop()
        self.assertFalse(controller.active)

        # After stopping: returns normal unmodified telemetry
        r_stopped = controller.apply(self.ground_truth)
        self.assertEqual(r_stopped.temperature, self.ground_truth.temperature)
        self.assertEqual(r_stopped.to_dict(), self.ground_truth.to_dict())
        self.assertIsNot(r_stopped, self.ground_truth)

    # =========================================================================
    # TEST 8 — TELEMETRY CONTRACT
    # =========================================================================
    def test_8_telemetry_contract(self):
        """TEST 8 — TELEMETRY CONTRACT.

        Verify that every attack returns the same Telemetry schema
        and uses the frozen field names and units:
        - temperature: °C
        - humidity: %
        - solar_radiation: W/m²
        - cooling_load: kW
        - power_consumption: kW
        - water_flow: L/min
        - tank_level: %
        - pump_status: ON/OFF
        - pump_speed: %
        - pressure: bar
        - timestamp: ISO-8601
        """
        attacks: list[BaseAttack] = [
            FalseInjection(target="temperature", intensity=0.5),
            GradualDrift(target="humidity", drift_rate=1.0),
            PumpFlowAttack(scenario=SCENARIO_PUMP_OFF_HIGH_FLOW),
            PumpFlowAttack(scenario=SCENARIO_PUMP_ON_LOW_ENERGY),
            CoordinatedAttack(scenario=SCENARIO_THERMAL),
            CoordinatedAttack(scenario=SCENARIO_PUMP),
        ]

        expected_contract_fields = {
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
            "timestamp",
        }

        for attack in attacks:
            with self.subTest(attack_name=attack.name):
                reported = attack.apply(self.ground_truth)

                # 1. Must return a Telemetry instance
                self.assertIsInstance(reported, Telemetry)

                # 2. Schema fields must exactly match frozen contract
                reported_dict = reported.to_dict()
                self.assertEqual(set(reported_dict.keys()), expected_contract_fields)

                # 3. Specific field types and enums match the contract
                self.assertIsInstance(reported.temperature, float)
                self.assertIsInstance(reported.humidity, float)
                self.assertIsInstance(reported.solar_radiation, float)
                self.assertIsInstance(reported.cooling_load, float)
                self.assertIsInstance(reported.power_consumption, float)
                self.assertIsInstance(reported.water_flow, float)
                self.assertIsInstance(reported.tank_level, float)
                self.assertIn(reported.pump_status, {"ON", "OFF"})
                self.assertIsInstance(reported.pump_speed, float)
                self.assertIsInstance(reported.pressure, float)
                self.assertIsInstance(reported.timestamp, str)

                # 4. No attack metadata attached to Telemetry
                self.assertFalse(hasattr(reported, "attack_type"))
                self.assertFalse(hasattr(reported, "intensity"))
                self.assertFalse(hasattr(reported, "metadata"))


if __name__ == "__main__":
    unittest.main()
