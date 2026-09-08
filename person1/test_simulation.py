import unittest
from datetime import datetime
try:
    from .simulator import PlantSimulator
    from .models import Telemetry
except ImportError:
    from simulator import PlantSimulator
    from models import Telemetry


class TestP1PhysicalSimulation(unittest.TestCase):
    """Verifies physical invariants and schema conformance for P1 Normal Simulation."""

    def setUp(self):
        self.sim = PlantSimulator(
            start_time=datetime(2026, 9, 7, 12, 0, 0),  # Solar midday
            default_pump_status="ON",
            default_pump_speed=75.0,
            seed=42,
        )

    def test_schema_conformance(self):
        """Verify all 11 fields exist with correct types and valid ranges."""
        tel = self.sim.step(dt_seconds=1.0)
        self.assertIsInstance(tel, Telemetry)

        # 1. Temperature (°C)
        self.assertIsInstance(tel.temperature, float)
        self.assertGreaterEqual(tel.temperature, 0.0)
        self.assertLessEqual(tel.temperature, 60.0)

        # 2. Humidity (%)
        self.assertIsInstance(tel.humidity, float)
        self.assertGreaterEqual(tel.humidity, 0.0)
        self.assertLessEqual(tel.humidity, 100.0)

        # 3. Solar Radiation (W/m²)
        self.assertIsInstance(tel.solar_radiation, float)
        self.assertGreaterEqual(tel.solar_radiation, 0.0)

        # 4. Cooling Load (kW)
        self.assertIsInstance(tel.cooling_load, float)
        self.assertGreater(tel.cooling_load, 0.0)

        # 5. Power Consumption (kW)
        self.assertIsInstance(tel.power_consumption, float)
        self.assertGreater(tel.power_consumption, tel.cooling_load / 5.0)

        # 6. Water Flow (L/min)
        self.assertIsInstance(tel.water_flow, float)
        self.assertGreaterEqual(tel.water_flow, 0.0)

        # 7. Tank Level (%)
        self.assertIsInstance(tel.tank_level, float)
        self.assertGreaterEqual(tel.tank_level, 0.0)
        self.assertLessEqual(tel.tank_level, 100.0)

        # 8. Pump Status ("ON" / "OFF")
        self.assertIn(tel.pump_status, ["ON", "OFF"])

        # 9. Pump Speed (%)
        self.assertIsInstance(tel.pump_speed, float)
        self.assertGreaterEqual(tel.pump_speed, 0.0)
        self.assertLessEqual(tel.pump_speed, 100.0)

        # 10. Pressure (bar)
        self.assertIsInstance(tel.pressure, float)
        self.assertGreater(tel.pressure, 0.5)

        # 11. Timestamp (datetime)
        self.assertIsInstance(tel.timestamp, datetime)

    def test_pump_off_invariants(self):
        """Invariant: When pump is OFF, flow must be 0, speed must be 0, pressure must be static."""
        self.sim.set_pump(status="OFF")
        tel = self.sim.step(dt_seconds=1.0)

        self.assertEqual(tel.pump_status, "OFF")
        self.assertEqual(tel.pump_speed, 0.0)
        self.assertEqual(tel.water_flow, 0.0, "Water flow must be 0.0 when pump is OFF")
        self.assertLessEqual(tel.pressure, 1.25, "Pressure should rest at static head when pump is OFF")

    def test_pump_on_invariants(self):
        """Invariant: When pump is ON, flow, speed, and pressure must scale appropriately."""
        self.sim.set_pump(status="ON", speed=80.0)
        tel = self.sim.step(dt_seconds=1.0)

        self.assertEqual(tel.pump_status, "ON")
        self.assertEqual(tel.pump_speed, 80.0)
        self.assertGreater(tel.water_flow, 80.0, "Flow rate should be significant at 80% speed")
        self.assertGreater(tel.pressure, 2.5, "Dynamic pressure should rise above 2.5 bar")

    def test_power_correlation(self):
        """Invariant: Power consumption with pump ON must be greater than with pump OFF."""
        # Baseline with pump OFF
        self.sim.set_pump(status="OFF")
        off_tel = self.sim.step(dt_seconds=1.0)

        # Compare with pump ON
        self.sim.set_pump(status="ON", speed=90.0)
        on_tel = self.sim.step(dt_seconds=1.0)

        self.assertGreater(
            on_tel.power_consumption,
            off_tel.power_consumption,
            "Total power must increase when pump is active",
        )

    def test_diurnal_solar_invariants(self):
        """Invariant: Solar radiation is 0 at night (midnight) and high at midday."""
        sim_night = PlantSimulator(start_time=datetime(2026, 9, 7, 1, 0, 0))
        night_tel = sim_night.step()
        self.assertEqual(night_tel.solar_radiation, 0.0, "Solar radiation at 1 AM must be 0 W/m²")

        sim_noon = PlantSimulator(start_time=datetime(2026, 9, 7, 12, 30, 0))
        noon_tel = sim_noon.step()
        self.assertGreater(noon_tel.solar_radiation, 700.0, "Solar radiation at solar noon must be high")

    def test_tank_level_continuity(self):
        """Invariant: Tank level must evolve continuously without discontinuous teleportation."""
        prev_level = self.sim.get_telemetry().tank_level
        for _ in range(10):
            tel = self.sim.step(dt_seconds=1.0)
            delta = abs(tel.tank_level - prev_level)
            self.assertLess(delta, 0.5, "Tank level changed too abruptly between 1-second steps")
            prev_level = tel.tank_level

    def test_serialization(self):
        """Verify Telemetry serializes to dictionary and deserializes back cleanly."""
        tel = self.sim.step()
        d = tel.to_dict()
        self.assertIsInstance(d["timestamp"], str)

        reconstructed = Telemetry.from_dict(d)
        self.assertEqual(reconstructed.temperature, tel.temperature)
        self.assertEqual(reconstructed.water_flow, tel.water_flow)
        self.assertEqual(reconstructed.pump_status, tel.pump_status)


if __name__ == "__main__":
    unittest.main()
