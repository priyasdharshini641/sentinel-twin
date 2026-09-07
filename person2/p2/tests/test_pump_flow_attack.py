import unittest
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.pump_flow_attack import (
    PumpFlowAttack,
    PUMP_RELATED_FIELDS,
    SCENARIO_PUMP_OFF_HIGH_FLOW,
    SCENARIO_PUMP_ON_LOW_ENERGY,
    SCENARIO_CUSTOM,
)


class TestPumpFlowAttack(unittest.TestCase):
    def setUp(self):
        # Baseline plant state with pump OFF and low hydraulic activity
        self.ground_truth_off = Telemetry(
            temperature=22.0,
            humidity=50.0,
            solar_radiation=400.0,
            cooling_load=5.0,
            power_consumption=0.0,
            water_flow=0.0,
            tank_level=80.0,
            pump_status="OFF",
            pump_speed=0.0,
            pressure=0.5,
            timestamp="2026-09-07T10:00:00Z",
        )

        # Baseline plant state with pump ON and high hydraulic activity
        self.ground_truth_on = Telemetry(
            temperature=26.0,
            humidity=60.0,
            solar_radiation=850.0,
            cooling_load=15.0,
            power_consumption=16.0,
            water_flow=55.0,
            tank_level=70.0,
            pump_status="ON",
            pump_speed=85.0,
            pressure=3.6,
            timestamp="2026-09-07T14:00:00Z",
        )

    def test_scenario_pump_off_high_flow(self):
        """Scenario 1: Pump is OFF but reported flow and pressure are high."""
        attack = PumpFlowAttack(
            scenario=SCENARIO_PUMP_OFF_HIGH_FLOW,
            intensity=1.0,
        )
        reported = attack.apply(self.ground_truth_off)

        # Manipulated hydraulic fields
        self.assertEqual(reported.pump_status, "OFF")
        self.assertEqual(reported.pump_speed, 0.0)
        self.assertGreater(reported.water_flow, 40.0)
        self.assertGreater(reported.pressure, 3.0)

        # Ground truth must remain completely unmodified
        self.assertEqual(self.ground_truth_off.water_flow, 0.0)
        self.assertEqual(self.ground_truth_off.pressure, 0.5)
        self.assertIsNot(reported, self.ground_truth_off)

        # Non-hydraulic telemetry fields must remain identical
        unrelated_fields = FROZEN_TELEMETRY_FIELDS - PUMP_RELATED_FIELDS
        for field in unrelated_fields:
            self.assertEqual(
                getattr(reported, field),
                getattr(self.ground_truth_off, field),
                f"Unrelated field '{field}' was modified!",
            )

    def test_scenario_pump_on_low_energy(self):
        """Scenario 2: Pump is ON but reported energy consumption is abnormally low."""
        attack = PumpFlowAttack(
            scenario=SCENARIO_PUMP_ON_LOW_ENERGY,
            intensity=1.0,
        )
        reported = attack.apply(self.ground_truth_on)

        # Manipulated power consumption
        self.assertEqual(reported.pump_status, "ON")
        self.assertEqual(reported.pump_speed, 85.0)
        self.assertEqual(reported.water_flow, 55.0)
        self.assertEqual(reported.pressure, 3.6)
        # Power should be reduced drastically (e.g. < 4.0 kW from 16.0 kW)
        self.assertLess(reported.power_consumption, 4.0)

        # Ground truth power consumption untouched
        self.assertEqual(self.ground_truth_on.power_consumption, 16.0)
        self.assertIsNot(reported, self.ground_truth_on)

        # Unrelated fields preserved
        unrelated_fields = FROZEN_TELEMETRY_FIELDS - PUMP_RELATED_FIELDS
        for field in unrelated_fields:
            self.assertEqual(
                getattr(reported, field),
                getattr(self.ground_truth_on, field),
                f"Unrelated field '{field}' was modified!",
            )

    def test_intensity_scales_manipulation(self):
        """Verifies that intensity controls the magnitude of manipulation."""
        attack_half = PumpFlowAttack(
            scenario=SCENARIO_PUMP_OFF_HIGH_FLOW,
            intensity=0.5,
            target_flow=60.0,
            target_pressure=4.0,
        )
        attack_full = PumpFlowAttack(
            scenario=SCENARIO_PUMP_OFF_HIGH_FLOW,
            intensity=1.0,
            target_flow=60.0,
            target_pressure=4.0,
        )

        r_half = attack_half.apply(self.ground_truth_off)
        r_full = attack_full.apply(self.ground_truth_off)

        self.assertEqual(r_half.water_flow, 30.0)
        self.assertEqual(r_full.water_flow, 60.0)
        self.assertEqual(r_half.pressure, 2.0)
        self.assertEqual(r_full.pressure, 4.0)

    def test_custom_scenario(self):
        """Verifies custom scenario allowing specific actuator combinations."""
        attack = PumpFlowAttack(
            scenario=SCENARIO_CUSTOM,
            target_pump_status="OFF",
            target_pump_speed=0.0,
            target_flow=45.0,
            target_pressure=3.0,
            target_power=1.0,
            intensity=1.0,
        )
        reported = attack.apply(self.ground_truth_on)

        self.assertEqual(reported.pump_status, "OFF")
        self.assertEqual(reported.pump_speed, 0.0)
        self.assertEqual(reported.water_flow, 45.0)
        self.assertEqual(reported.pressure, 3.0)
        self.assertEqual(reported.power_consumption, 1.0)

    def test_attack_metadata_separation(self):
        """Guardrail: Attack metadata is never inserted into Telemetry."""
        attack = PumpFlowAttack(scenario=SCENARIO_PUMP_OFF_HIGH_FLOW, intensity=0.9)
        metadata = attack.get_metadata()

        self.assertEqual(metadata["name"], "PUMP_FLOW_ATTACK")
        self.assertEqual(metadata["scenario"], SCENARIO_PUMP_OFF_HIGH_FLOW)
        self.assertEqual(metadata["intensity"], 0.9)

        reported = attack.apply(self.ground_truth_off)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "scenario"))
        self.assertFalse(hasattr(reported, "intensity"))

    def test_invalid_scenario_raises_error(self):
        """Ensures passing an invalid scenario raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            PumpFlowAttack(scenario="INVALID_SCENARIO")
        self.assertIn("Unknown scenario", str(ctx.exception))

    def test_inactive_attack_returns_new_copy(self):
        """Verifies inactive PumpFlowAttack returns a new independent copy of telemetry."""
        attack = PumpFlowAttack(scenario="ghost_flow", active=False)
        reported = attack.apply(self.ground_truth_off)
        self.assertEqual(reported.to_dict(), self.ground_truth_off.to_dict())
        self.assertIsNot(reported, self.ground_truth_off)


if __name__ == "__main__":
    unittest.main()
