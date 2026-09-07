import unittest
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.gradual_drift import GradualDrift, SENSOR_BOUNDS


class TestGradualDriftAttack(unittest.TestCase):
    def setUp(self):
        self.ground_truth = Telemetry(
            temperature=38.0,
            humidity=55.0,
            solar_radiation=800.0,
            cooling_load=12.0,
            power_consumption=15.0,
            water_flow=45.0,
            tank_level=75.0,
            pump_status="ON",
            pump_speed=80.0,
            pressure=3.2,
            timestamp="2026-09-07T12:00:00Z",
        )

    def test_gradual_drift_sequence_temperature(self):
        """Validates the sequence:

        38.0 -> approx 37.x -> lower -> lower again -> 35.0
        """
        attack = GradualDrift(
            target="temperature",
            drift_rate=0.75,
            direction=-1.0,
            final_value=35.0,
        )

        # Reading 1
        r1 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r1.temperature, 37.25, places=2)
        self.assertTrue(37.0 <= r1.temperature < 38.0)

        # Reading 2 (lower than previous)
        r2 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r2.temperature, 36.50, places=2)
        self.assertLess(r2.temperature, r1.temperature)

        # Reading 3 (lower again)
        r3 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r3.temperature, 35.75, places=2)
        self.assertLess(r3.temperature, r2.temperature)

        # Reading 4 (reaches configured final value)
        r4 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r4.temperature, 35.00, places=2)
        self.assertLess(r4.temperature, r3.temperature)

        # Reading 5 (holds at final value without overshooting)
        r5 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r5.temperature, 35.00, places=2)

    def test_ground_truth_never_mutated_during_drift(self):
        """Verifies that ground truth remains strictly unchanged through multiple apply() calls."""
        original_dict = self.ground_truth.to_dict()
        attack = GradualDrift(target="temperature", drift_rate=0.8)

        for _ in range(5):
            reported = attack.apply(self.ground_truth)
            self.assertEqual(self.ground_truth.to_dict(), original_dict)
            self.assertIsNot(reported, self.ground_truth)

    def test_non_target_values_remain_unchanged(self):
        """Verifies that non-target telemetry fields are preserved exactly at each step."""
        attack = GradualDrift(target="pressure", drift_rate=0.2, direction=-1.0)

        for _ in range(4):
            reported = attack.apply(self.ground_truth)
            for field in FROZEN_TELEMETRY_FIELDS:
                if field != "pressure":
                    self.assertEqual(
                        getattr(reported, field),
                        getattr(self.ground_truth, field),
                        f"Non-target field '{field}' changed!",
                    )

    def test_reset_restores_internal_state(self):
        """Verifies that reset() correctly clears step count and accumulated drift."""
        attack = GradualDrift(target="temperature", drift_rate=0.75, direction=-1.0)

        # Apply two steps
        r1 = attack.apply(self.ground_truth)
        r2 = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r2.temperature, 36.50, places=2)
        self.assertEqual(attack.steps, 2)
        self.assertAlmostEqual(attack.accumulated_drift, -1.50, places=2)

        # Reset the attack
        attack.reset()
        self.assertEqual(attack.steps, 0)
        self.assertEqual(attack.accumulated_drift, 0.0)

        # Next apply should start fresh from step 1
        r_reset = attack.apply(self.ground_truth)
        self.assertAlmostEqual(r_reset.temperature, r1.temperature, places=2)
        self.assertEqual(attack.steps, 1)

    def test_intensity_scales_drift_rate(self):
        """Verifies that higher intensity results in larger per-step drift."""
        attack_slow = GradualDrift(target="humidity", drift_rate=1.0, intensity=0.5, direction=-1.0)
        attack_fast = GradualDrift(target="humidity", drift_rate=1.0, intensity=2.0, direction=-1.0)

        r_slow = attack_slow.apply(self.ground_truth)
        r_fast = attack_fast.apply(self.ground_truth)

        delta_slow = abs(r_slow.humidity - self.ground_truth.humidity)
        delta_fast = abs(r_fast.humidity - self.ground_truth.humidity)

        self.assertAlmostEqual(delta_slow, 0.5, places=2)
        self.assertAlmostEqual(delta_fast, 2.0, places=2)
        self.assertGreater(delta_fast, delta_slow)

    def test_physical_sanity_bounds_clipping(self):
        """Verifies that gradual drift respects physical bounds (e.g. tank_level >= 0.0)."""
        # Start at 75.0, drift down by 30.0 per step
        attack = GradualDrift(target="tank_level", drift_rate=30.0, direction=-1.0)
        attack.apply(self.ground_truth)  # 45.0
        attack.apply(self.ground_truth)  # 15.0
        r3 = attack.apply(self.ground_truth)  # would be -15.0, clipped to 0.0

        min_tank = SENSOR_BOUNDS["tank_level"][0]
        self.assertEqual(r3.tank_level, min_tank)

    def test_attack_metadata_kept_separate(self):
        """Guardrail: Internal state is in get_metadata() but never in Telemetry."""
        attack = GradualDrift(target="cooling_load", drift_rate=0.5)
        attack.apply(self.ground_truth)

        meta = attack.get_metadata()
        self.assertEqual(meta["name"], "GRADUAL_DRIFT")
        self.assertEqual(meta["target_field"], "cooling_load")
        self.assertEqual(meta["steps"], 1)
        self.assertIn("accumulated_drift", meta)

        reported = attack.apply(self.ground_truth)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "steps"))
        self.assertFalse(hasattr(reported, "accumulated_drift"))

    def test_inactive_attack_returns_new_copy(self):
        """Verifies inactive GradualDrift returns a new independent copy of telemetry."""
        attack = GradualDrift(target="temperature", drift_rate=0.5, active=False)
        reported = attack.apply(self.ground_truth)
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        self.assertIsNot(reported, self.ground_truth)


if __name__ == "__main__":
    unittest.main()
