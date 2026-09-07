import unittest
from dataclasses import FrozenInstanceError
from backend.models.telemetry import Telemetry, FROZEN_TELEMETRY_FIELDS
from backend.attacks.base_attack import BaseAttack


class MockTemperatureAttack(BaseAttack):
    """Simple concrete attack used to test the BaseAttack interface."""

    def __init__(self, offset: float = 10.0, active: bool = True):
        super().__init__(
            name="MOCK_TEMPERATURE_ATTACK",
            target_field="temperature",
            intensity=offset,
            active=active,
        )
        self.offset = offset

    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        return ground_truth.copy_with(
            temperature=ground_truth.temperature + self.offset
        )


class TestGroundTruthImmutabilityAndContract(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "temperature": 24.5,
            "humidity": 55.0,
            "solar_radiation": 800.0,
            "cooling_load": 12.4,
            "power_consumption": 15.2,
            "water_flow": 45.0,
            "tank_level": 78.5,
            "pump_status": "ON",
            "pump_speed": 85.0,
            "pressure": 3.2,
            "timestamp": "2026-09-07T12:00:00Z",
        }
        self.ground_truth = Telemetry.from_dict(self.sample_data)

    def test_frozen_fields_match_contract(self):
        """Validates that Telemetry has exactly the 11 frozen contract fields."""
        expected_fields = {
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
        self.assertEqual(FROZEN_TELEMETRY_FIELDS, expected_fields)
        self.assertEqual(set(self.ground_truth.to_dict().keys()), expected_fields)

    def test_direct_mutation_raises_frozen_instance_error(self):
        """Guardrail #1 & #2: Telemetry cannot be modified in-place."""
        with self.assertRaises(FrozenInstanceError):
            self.ground_truth.temperature = 99.0

        with self.assertRaises(FrozenInstanceError):
            self.ground_truth.pump_status = "OFF"

    def test_adding_arbitrary_attribute_raises_frozen_instance_error(self):
        """Guardrail #5: Attack metadata cannot be injected into Telemetry."""
        with self.assertRaises(FrozenInstanceError):
            self.ground_truth.attack_type = "FALSE_INJECTION"

    def test_copy_with_rejects_extra_fields(self):
        """Ensures copy_with strictly forbids setting metadata fields."""
        with self.assertRaises(ValueError) as ctx:
            self.ground_truth.copy_with(attack_type="FALSE_INJECTION")
        self.assertIn("Attack metadata must remain separate", str(ctx.exception))

    def test_from_dict_rejects_extraneous_fields(self):
        """Ensures deserialization rejects foreign fields or injected metadata."""
        polluted_data = dict(self.sample_data)
        polluted_data["attack_active"] = True
        with self.assertRaises(ValueError) as ctx:
            Telemetry.from_dict(polluted_data)
        self.assertIn("disallowed extra fields", str(ctx.exception))

    def test_from_dict_rejects_missing_fields(self):
        """Ensures deserialization enforces all 11 required contract fields."""
        incomplete_data = dict(self.sample_data)
        del incomplete_data["cooling_load"]
        with self.assertRaises(ValueError) as ctx:
            Telemetry.from_dict(incomplete_data)
        self.assertIn("missing required fields", str(ctx.exception))

    def test_mock_attack_preserves_ground_truth(self):
        """Guardrail #1 & #2: Applying an attack leaves ground_truth untouched."""
        snapshot_before = self.ground_truth.to_dict()

        attack = MockTemperatureAttack(offset=15.0)
        reported = attack.apply(self.ground_truth)

        # 1. Ground truth must remain completely identical
        self.assertEqual(self.ground_truth.to_dict(), snapshot_before)

        # 2. Reported telemetry must be a distinct object
        self.assertIsNot(reported, self.ground_truth)

        # 3. Targeted field was altered as expected
        self.assertEqual(reported.temperature, 39.5)

        # 4. All untargeted fields remain sacred and identical
        for field in FROZEN_TELEMETRY_FIELDS:
            if field != "temperature":
                self.assertEqual(
                    getattr(reported, field),
                    getattr(self.ground_truth, field),
                    f"Untargeted field '{field}' was modified!",
                )

    def test_attack_metadata_is_kept_separate(self):
        """Guardrail #5: Metadata lives on the attack object, not on Telemetry."""
        attack = MockTemperatureAttack(offset=10.0)
        metadata = attack.get_metadata()

        self.assertEqual(metadata["name"], "MOCK_TEMPERATURE_ATTACK")
        self.assertEqual(metadata["target_field"], "temperature")
        self.assertEqual(metadata["intensity"], 10.0)
        self.assertTrue(metadata["active"])

        reported = attack.apply(self.ground_truth)
        self.assertEqual(set(reported.to_dict().keys()), FROZEN_TELEMETRY_FIELDS)
        self.assertFalse(hasattr(reported, "attack_name"))
        self.assertFalse(hasattr(reported, "metadata"))

    def test_inactive_attack_leaves_telemetry_unchanged(self):
        """Verifies an inactive attack passes telemetry through as an unmodified copy."""
        inactive_attack = MockTemperatureAttack(offset=10.0, active=False)
        reported = inactive_attack.apply(self.ground_truth)
        self.assertEqual(reported.to_dict(), self.ground_truth.to_dict())
        self.assertIsNot(reported, self.ground_truth)

    def test_validation_rules(self):
        """Ensures pump_status and ISO-8601 validation work as expected."""
        with self.assertRaises(ValueError) as ctx:
            self.ground_truth.copy_with(pump_status="STANDBY")
        self.assertIn("Invalid pump_status", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.ground_truth.copy_with(timestamp="not-a-timestamp")
        self.assertIn("Invalid timestamp", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
