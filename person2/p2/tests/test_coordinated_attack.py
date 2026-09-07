import unittest
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.coordinated_attack import (
    CoordinatedAttack,
    SCENARIO_THERMAL,
    SCENARIO_PUMP,
    THERMAL_COORDINATED_FIELDS,
    PUMP_COORDINATED_FIELDS,
)


class TestCoordinatedAttack(unittest.TestCase):
    def setUp(self):
        self.ground_truth = Telemetry(
            temperature=36.0,
            humidity=55.0,
            solar_radiation=800.0,
            cooling_load=20.0,
            power_consumption=25.0,
            water_flow=60.0,
            tank_level=75.0,
            pump_status="ON",
            pump_speed=85.0,
            pressure=4.0,
            timestamp="2026-09-07T13:00:00Z",
        )

    def test_thermal_scenario_multiple_fields_change(self):
        """Validates that thermal scenario simultaneously modifies:

        temperature, solar_radiation, cooling_load, and power_consumption.
        """
        attack = CoordinatedAttack(
            scenario=SCENARIO_THERMAL,
            intensity=1.0,
            direction=-1.0,
        )
        reported = attack.apply(self.ground_truth)

        # 1. Verify all 4 thermal fields changed
        self.assertNotEqual(reported.temperature, self.ground_truth.temperature)
        self.assertNotEqual(reported.solar_radiation, self.ground_truth.solar_radiation)
        self.assertNotEqual(reported.cooling_load, self.ground_truth.cooling_load)
        self.assertNotEqual(reported.power_consumption, self.ground_truth.power_consumption)

        # Coordinated suppression moves all downwards
        self.assertLess(reported.temperature, self.ground_truth.temperature)
        self.assertLess(reported.solar_radiation, self.ground_truth.solar_radiation)
        self.assertLess(reported.cooling_load, self.ground_truth.cooling_load)
        self.assertLess(reported.power_consumption, self.ground_truth.power_consumption)

        # 2. Verify ground_truth remains completely unchanged
        self.assertEqual(self.ground_truth.temperature, 36.0)
        self.assertEqual(self.ground_truth.solar_radiation, 800.0)
        self.assertIsNot(reported, self.ground_truth)

        # 3. Verify unrelated fields remain unchanged
        unrelated_fields = FROZEN_TELEMETRY_FIELDS - THERMAL_COORDINATED_FIELDS
        for field in unrelated_fields:
            self.assertEqual(
                getattr(reported, field),
                getattr(self.ground_truth, field),
                f"Unrelated field '{field}' was unexpectedly modified in thermal attack!",
            )

    def test_pump_scenario_multiple_fields_change(self):
        """Validates that pump scenario simultaneously modifies:

        pump_status, pump_speed, water_flow, pressure, and power_consumption.
        """
        attack = CoordinatedAttack(
            scenario=SCENARIO_PUMP,
            intensity=1.0,
            direction=-1.0,
        )
        reported = attack.apply(self.ground_truth)

        # 1. Verify intended pump fields changed
        self.assertNotEqual(reported.pump_speed, self.ground_truth.pump_speed)
        self.assertNotEqual(reported.water_flow, self.ground_truth.water_flow)
        self.assertNotEqual(reported.pressure, self.ground_truth.pressure)
        self.assertNotEqual(reported.power_consumption, self.ground_truth.power_consumption)

        # Coordinated throttle moves hydraulic continuous values down
        self.assertLess(reported.pump_speed, self.ground_truth.pump_speed)
        self.assertLess(reported.water_flow, self.ground_truth.water_flow)
        self.assertLess(reported.pressure, self.ground_truth.pressure)
        self.assertLess(reported.power_consumption, self.ground_truth.power_consumption)

        # 2. Verify ground truth is preserved
        self.assertEqual(self.ground_truth.pump_speed, 85.0)
        self.assertEqual(self.ground_truth.water_flow, 60.0)
        self.assertIsNot(reported, self.ground_truth)

        # 3. Verify unrelated fields remain unchanged
        unrelated_fields = FROZEN_TELEMETRY_FIELDS - PUMP_COORDINATED_FIELDS
        for field in unrelated_fields:
            self.assertEqual(
                getattr(reported, field),
                getattr(self.ground_truth, field),
                f"Unrelated field '{field}' was modified in pump attack!",
            )

    def test_intensity_affects_manipulation_magnitude(self):
        """Verifies that attack intensity scales the magnitude of coordinated changes."""
        attack_half = CoordinatedAttack(scenario=SCENARIO_THERMAL, intensity=0.5, direction=-1.0)
        attack_full = CoordinatedAttack(scenario=SCENARIO_THERMAL, intensity=1.0, direction=-1.0)

        r_half = attack_half.apply(self.ground_truth)
        r_full = attack_full.apply(self.ground_truth)

        delta_temp_half = abs(r_half.temperature - self.ground_truth.temperature)
        delta_temp_full = abs(r_full.temperature - self.ground_truth.temperature)
        self.assertAlmostEqual(delta_temp_half * 2.0, delta_temp_full, places=2)

        delta_solar_half = abs(r_half.solar_radiation - self.ground_truth.solar_radiation)
        delta_solar_full = abs(r_full.solar_radiation - self.ground_truth.solar_radiation)
        self.assertAlmostEqual(delta_solar_half * 2.0, delta_solar_full, places=2)

        delta_power_half = abs(r_half.power_consumption - self.ground_truth.power_consumption)
        delta_power_full = abs(r_full.power_consumption - self.ground_truth.power_consumption)
        self.assertAlmostEqual(delta_power_half * 2.0, delta_power_full, places=2)

    def test_coordinated_boost_direction(self):
        """Verifies that direction=1.0 coordinates multiple values upwards."""
        attack = CoordinatedAttack(scenario=SCENARIO_THERMAL, intensity=0.5, direction=1.0)
        reported = attack.apply(self.ground_truth)

        self.assertGreater(reported.temperature, self.ground_truth.temperature)
        self.assertGreater(reported.solar_radiation, self.ground_truth.solar_radiation)
        self.assertGreater(reported.cooling_load, self.ground_truth.cooling_load)
        self.assertGreater(reported.power_consumption, self.ground_truth.power_consumption)

    def test_attack_metadata_kept_separate(self):
        """Guardrail: Attack metadata exists in get_metadata() and never in Telemetry."""
        attack = CoordinatedAttack(scenario=SCENARIO_THERMAL, intensity=0.8)
        meta = attack.get_metadata()

        self.assertEqual(meta["name"], "COORDINATED_ATTACK")
        self.assertEqual(meta["scenario"], SCENARIO_THERMAL)
        self.assertEqual(meta["intensity"], 0.8)
        self.assertIn("target_fields", meta)

        reported = attack.apply(self.ground_truth)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "scenario"))
        self.assertFalse(hasattr(reported, "target_fields"))

    def test_inactive_attack_returns_new_copy(self):
        """Verifies inactive CoordinatedAttack returns a new independent copy of telemetry."""
        attack = CoordinatedAttack(scenario="thermal", active=False)
        reported = attack.apply(self.ground_truth)
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        self.assertIsNot(reported, self.ground_truth)


if __name__ == "__main__":
    unittest.main()
