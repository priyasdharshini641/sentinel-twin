import unittest
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.false_injection import (
    FalseInjection,
    SUPPORTED_SENSORS,
    SENSOR_BOUNDS,
)


class TestFalseInjectionAttack(unittest.TestCase):
    def setUp(self):
        self.ground_truth = Telemetry(
            temperature=38.0,
            humidity=60.0,
            solar_radiation=850.0,
            cooling_load=15.0,
            power_consumption=18.0,
            water_flow=50.0,
            tank_level=70.0,
            pump_status="ON",
            pump_speed=80.0,
            pressure=3.5,
            timestamp="2026-09-07T14:30:00Z",
        )

    def test_example_from_specification(self):
        """Validates the exact example: temperature 38.0 -> 30.0 with intensity=0.8."""
        attack = FalseInjection(target="temperature", intensity=0.8)
        reported = attack.apply(self.ground_truth)

        # Target value changes to 30.0
        self.assertEqual(reported.temperature, 30.0)

        # Ground truth remains unchanged
        self.assertEqual(self.ground_truth.temperature, 38.0)
        self.assertIsNot(reported, self.ground_truth)

        # Non-target values remain unchanged
        for field in FROZEN_TELEMETRY_FIELDS:
            if field != "temperature":
                self.assertEqual(
                    getattr(reported, field),
                    getattr(self.ground_truth, field),
                    f"Field '{field}' was unexpectedly modified",
                )

    def test_target_value_changes(self):
        """Verifies that the target value changes according to configured attack."""
        attack = FalseInjection(target="pressure", intensity=1.0, direction=-1.0)
        reported = attack.apply(self.ground_truth)

        self.assertNotEqual(reported.pressure, self.ground_truth.pressure)
        self.assertEqual(reported.pressure, 2.0)

    def test_non_target_values_remain_unchanged(self):
        """Verifies that all non-target fields remain identical to ground truth."""
        attack = FalseInjection(target="water_flow", intensity=0.5)
        reported = attack.apply(self.ground_truth)

        for field in FROZEN_TELEMETRY_FIELDS:
            if field != "water_flow":
                self.assertEqual(
                    getattr(reported, field),
                    getattr(self.ground_truth, field),
                    f"Non-target field '{field}' changed!",
                )

    def test_ground_truth_remains_unchanged(self):
        """Verifies that the original ground truth instance is never mutated."""
        original_dict = self.ground_truth.to_dict()
        attack = FalseInjection(target="cooling_load", intensity=0.9)
        reported = attack.apply(self.ground_truth)

        self.assertEqual(self.ground_truth.to_dict(), original_dict)
        self.assertIsNot(reported, self.ground_truth)

    def test_intensity_changes_attack_magnitude(self):
        """Verifies that higher intensity increases the manipulation magnitude proportionally."""
        attack_low = FalseInjection(target="temperature", intensity=0.4)
        attack_high = FalseInjection(target="temperature", intensity=0.8)

        reported_low = attack_low.apply(self.ground_truth)
        reported_high = attack_high.apply(self.ground_truth)

        delta_low = abs(reported_low.temperature - self.ground_truth.temperature)
        delta_high = abs(reported_high.temperature - self.ground_truth.temperature)

        self.assertAlmostEqual(delta_low, 4.0)
        self.assertAlmostEqual(delta_high, 8.0)
        self.assertGreater(delta_high, delta_low)

    def test_all_supported_sensors(self):
        """Verifies that all 9 required sensors can be individually targeted."""
        expected_sensors = {
            "temperature",
            "humidity",
            "solar_radiation",
            "cooling_load",
            "power_consumption",
            "water_flow",
            "tank_level",
            "pump_speed",
            "pressure",
        }
        self.assertTrue(expected_sensors.issubset(SUPPORTED_SENSORS))

        for sensor in expected_sensors:
            attack = FalseInjection(target=sensor, intensity=0.5)
            reported = attack.apply(self.ground_truth)

            # Target sensor changed
            self.assertNotEqual(
                getattr(reported, sensor),
                getattr(self.ground_truth, sensor),
                f"Sensor '{sensor}' should have changed.",
            )

            # Non-target fields remained identical
            for field in FROZEN_TELEMETRY_FIELDS:
                if field != sensor:
                    self.assertEqual(
                        getattr(reported, field),
                        getattr(self.ground_truth, field),
                        f"Non-target sensor '{field}' changed while targeting '{sensor}'.",
                    )

    def test_physical_sanity_bounds_clipping(self):
        """Verifies manipulated values are kept within physical sanity bounds."""
        # Test lower bound clipping on tank_level (bound min is 0.0)
        attack_low = FalseInjection(target="tank_level", offset=-500.0, intensity=1.0)
        reported_low = attack_low.apply(self.ground_truth)
        self.assertEqual(reported_low.tank_level, SENSOR_BOUNDS["tank_level"][0])

        # Test upper bound clipping on tank_level (bound max is 100.0)
        attack_high = FalseInjection(target="tank_level", offset=500.0, intensity=1.0)
        reported_high = attack_high.apply(self.ground_truth)
        self.assertEqual(reported_high.tank_level, SENSOR_BOUNDS["tank_level"][1])

    def test_attack_metadata_not_in_telemetry(self):
        """Guardrail: Attack metadata must never be injected into Telemetry object."""
        attack = FalseInjection(target="humidity", intensity=0.6)
        metadata = attack.get_metadata()

        self.assertEqual(metadata["name"], "FALSE_INJECTION")
        self.assertEqual(metadata["target_field"], "humidity")
        self.assertEqual(metadata["intensity"], 0.6)

        reported = attack.apply(self.ground_truth)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "target"))
        self.assertFalse(hasattr(reported, "intensity"))

    def test_unsupported_target_raises_value_error(self):
        """Validates that targeting invalid sensors or discrete fields raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            FalseInjection(target="invalid_sensor")
        self.assertIn("not supported by FalseInjection", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            FalseInjection(target="timestamp")
        self.assertIn("not supported by FalseInjection", str(ctx.exception))

    def test_inactive_attack_returns_new_copy(self):
        """Verifies inactive FalseInjection returns a new independent copy of telemetry."""
        attack = FalseInjection(target="temperature", intensity=0.8, active=False)
        reported = attack.apply(self.ground_truth)
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        self.assertIsNot(reported, self.ground_truth)


if __name__ == "__main__":
    unittest.main()
