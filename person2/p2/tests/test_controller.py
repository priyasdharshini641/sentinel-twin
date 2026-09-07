import unittest
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.controller import AttackController
from backend.attacks.false_injection import FalseInjection
from backend.attacks.gradual_drift import GradualDrift
from backend.attacks.pump_flow_attack import PumpFlowAttack
from backend.attacks.coordinated_attack import CoordinatedAttack


class TestAttackController(unittest.TestCase):
    def setUp(self):
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

    def test_configuration_example(self):
        """Validates the exact configuration example from specification:

        {
            "active": True,
            "type": "FALSE_INJECTION",
            "target": "temperature",
            "intensity": 0.8
        }
        """
        config = {
            "active": True,
            "type": "FALSE_INJECTION",
            "target": "temperature",
            "intensity": 0.8,
        }
        controller = AttackController(config)
        reported = controller.apply(self.ground_truth)

        # Temperature manipulated from 38.0 to 30.0
        self.assertEqual(reported.temperature, 30.0)

        # Non-target fields preserved
        for field in FROZEN_TELEMETRY_FIELDS:
            if field != "temperature":
                self.assertEqual(
                    getattr(reported, field),
                    getattr(self.ground_truth, field),
                    f"Non-target field '{field}' was modified!",
                )

        # Ground truth intact
        self.assertEqual(self.ground_truth.temperature, 38.0)
        self.assertIsNot(reported, self.ground_truth)

    def test_all_four_supported_attack_types(self):
        """Verifies controller correctly dispatches to all four supported attack types."""
        attack_configs = [
            (
                {
                    "active": True,
                    "type": "FALSE_INJECTION",
                    "target": "pressure",
                    "intensity": 1.0,
                },
                FalseInjection,
            ),
            (
                {
                    "active": True,
                    "type": "GRADUAL_DRIFT",
                    "target": "temperature",
                    "drift_rate": 0.5,
                },
                GradualDrift,
            ),
            (
                {
                    "active": True,
                    "type": "PUMP_FLOW_ATTACK",
                    "scenario": "PUMP_OFF_HIGH_FLOW",
                },
                PumpFlowAttack,
            ),
            (
                {
                    "active": True,
                    "type": "COORDINATED_ATTACK",
                    "scenario": "THERMAL",
                },
                CoordinatedAttack,
            ),
        ]

        for config, expected_cls in attack_configs:
            with self.subTest(attack_type=config["type"]):
                controller = AttackController(config)
                self.assertIsInstance(controller.current_attack, expected_cls)
                reported = controller.apply(self.ground_truth)
                self.assertIsInstance(reported, Telemetry)
                self.assertIsNot(reported, self.ground_truth)

    def test_inactive_controller_returns_unchanged_copy(self):
        """Guardrail #4: When inactive, reported telemetry is an unchanged copy of ground_truth."""
        config = {
            "active": False,
            "type": "FALSE_INJECTION",
            "target": "temperature",
            "intensity": 1.0,
        }
        controller = AttackController(config)
        reported = controller.apply(self.ground_truth)

        # Values identical
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        # Distinct instance
        self.assertIsNot(reported, self.ground_truth)
        # Ground truth unchanged
        self.assertEqual(self.ground_truth.temperature, 38.0)

    def test_stop_and_start_lifecycle(self):
        """Verifies stop() deactivates manipulation and start() reactivates it."""
        config = {
            "active": True,
            "type": "FALSE_INJECTION",
            "target": "temperature",
            "intensity": 0.8,
        }
        controller = AttackController(config)

        # 1. Active
        r1 = controller.apply(self.ground_truth)
        self.assertEqual(r1.temperature, 30.0)

        # 2. Stop -> Inactive
        controller.stop()
        self.assertFalse(controller.active)
        r2 = controller.apply(self.ground_truth)
        self.assertEqual(r2.temperature, 38.0)
        self.assertEqual(r2.to_dict(), self.ground_truth.to_dict())

        # 3. Start -> Active again
        controller.start()
        self.assertTrue(controller.active)
        r3 = controller.apply(self.ground_truth)
        self.assertEqual(r3.temperature, 30.0)

    def test_reset_functionality(self):
        """Verifies reset() clears internal state on stateful attacks like GradualDrift."""
        config = {
            "active": True,
            "type": "GRADUAL_DRIFT",
            "target": "temperature",
            "drift_rate": 0.75,
            "direction": -1.0,
        }
        controller = AttackController(config)

        # Step 1 and Step 2
        r1 = controller.apply(self.ground_truth)
        r2 = controller.apply(self.ground_truth)
        self.assertAlmostEqual(r2.temperature, 36.50, places=2)

        # Reset
        controller.reset()

        # Next apply starts from step 1 again
        r_reset = controller.apply(self.ground_truth)
        self.assertAlmostEqual(r_reset.temperature, r1.temperature, places=2)

    def test_ground_truth_is_never_mutated(self):
        """Guardrail #6: Multiple apply calls never mutate the original ground_truth."""
        original_dict = self.ground_truth.to_dict()
        controller = AttackController(
            {
                "active": True,
                "type": "COORDINATED_ATTACK",
                "scenario": "THERMAL",
            }
        )

        for _ in range(5):
            reported = controller.apply(self.ground_truth)
            self.assertEqual(self.ground_truth.to_dict(), original_dict)
            self.assertIsNot(reported, self.ground_truth)

    def test_attack_metadata_separation(self):
        """Guardrail #7: Metadata stays on controller/attack, not in Telemetry."""
        controller = AttackController(
            {
                "active": True,
                "type": "FALSE_INJECTION",
                "target": "humidity",
                "intensity": 0.5,
            }
        )
        meta = controller.get_metadata()
        self.assertTrue(meta["active"])
        self.assertEqual(meta["attack_type"], "FALSE_INJECTION")
        self.assertIsNotNone(meta["attack_metadata"])

        reported = controller.apply(self.ground_truth)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "type"))
        self.assertFalse(hasattr(reported, "attack_type"))
        self.assertFalse(hasattr(reported, "intensity"))

    def test_invalid_attack_type_raises_error(self):
        """Guardrail #8: Invalid attack types produce a clear error."""
        with self.assertRaises(ValueError) as ctx:
            AttackController({"type": "MALWARE_INJECTION", "active": True})
        self.assertIn("Invalid attack type", str(ctx.exception))
        self.assertIn("FALSE_INJECTION", str(ctx.exception))

    def test_missing_type_when_active_raises_error(self):
        """Configuring with active=True and no attack type raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            AttackController({"active": True})
        self.assertIn("must specify an attack 'type'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
