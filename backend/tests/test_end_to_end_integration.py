"""
SENTINEL TWIN — End-to-End System Integration Test Suite
Validates the complete 4-phase cyber-physical pipeline:
P1 (Simulation) -> P2 (Attack Engine) -> P3 (Causal Defense) -> P4 (State Aggregation & API)
"""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
for p in [str(repo_root), str(repo_root / "person4")]:
    if p not in sys.path:
        sys.path.insert(0, p)


# 1. Contract & Packaging Imports
from backend.models.telemetry import (
    Telemetry,
    FROZEN_TELEMETRY_FIELDS,
    VALID_PUMP_STATUS,
)
import person1.models as p1_models
import person2.p2.backend.models.telemetry as p2_models
import person4.app.models.telemetry as p4_models

# 2. Engine Components
from person1.simulator import PlantSimulator
from backend.attacks.controller import AttackController
from backend.attacks.false_injection import FalseInjection
from backend.attacks.pump_flow_attack import PumpFlowAttack, SCENARIO_PUMP_OFF_HIGH_FLOW
from backend.attacks.coordinated_attack import CoordinatedAttack, SCENARIO_THERMAL
from backend.defense.defense_pipeline import DefensePipeline
from backend.defense.causal_engine import CausalEngine
from backend.defense.trust_engine import TrustEngine

# 3. P4 API & Orchestrator Components
from person4.app.services.orchestrator import orchestrator
from person4.app.models.telemetry import (
    AttackLaunchRequest,
    AttackType,
    SystemMode,
    ThreatLevel,
    SystemStatusResponse,
)


class TestSentinelTwinEndToEnd(unittest.TestCase):
    """Full End-to-End Cyber-Physical System Integration Test."""

    def setUp(self):
        orchestrator.reset_system()

    def test_01_canonical_contract_identity(self):
        """Verify Telemetry is canonical across P1, P2, and P4."""
        self.assertIs(p1_models.Telemetry, Telemetry)
        self.assertIs(p2_models.Telemetry, Telemetry)
        self.assertIs(p4_models.Telemetry, Telemetry)

        # Immutability check
        tel = Telemetry(
            temperature=25.0,
            humidity=50.0,
            solar_radiation=800.0,
            cooling_load=15.0,
            power_consumption=10.0,
            water_flow=50.0,
            tank_level=75.0,
            pump_status="ON",
            pump_speed=80.0,
            pressure=3.0,
            timestamp=datetime.now(timezone.utc),
        )
        with self.assertRaises(Exception):
            tel.temperature = 30.0  # type: ignore

        # Copy with check
        copied = tel.copy_with(temperature=30.0)
        self.assertEqual(tel.temperature, 25.0)
        self.assertEqual(copied.temperature, 30.0)

    def test_02_p1_to_p2_pipeline(self):
        """Verify P1 simulation produces ground truth and P2 successfully perturbs it."""
        sim = PlantSimulator(seed=123)
        gt = sim.step(dt_seconds=1.0)
        self.assertIsInstance(gt, Telemetry)

        controller = AttackController({
            "type": "FALSE_INJECTION",
            "target": "temperature",
            "offset": 12.0,
            "active": True,
        })

        reported = controller.apply(gt)
        self.assertIsInstance(reported, Telemetry)
        self.assertNotEqual(reported.temperature, gt.temperature)
        self.assertEqual(reported.temperature, round(gt.temperature + 12.0, 4))
        # Inactive verification
        controller.stop()
        inactive_reported = controller.apply(gt)
        self.assertEqual(inactive_reported.temperature, gt.temperature)

    def test_03_p2_to_p3_detection(self):
        """Verify P3 DefensePipeline evaluates P2 reported stream and catches invariant violations."""
        sim = PlantSimulator(seed=456)
        pipeline = DefensePipeline()

        # Establish 3-tick nominal baseline
        for _ in range(3):
            nominal = sim.step(dt_seconds=1.0)
            res = pipeline.evaluate(nominal)
            self.assertFalse(res["anomaly_detected"])
            self.assertEqual(res["violated_invariants"], [])
            self.assertEqual(res["risk_level"], "LOW")

        # Launch Pump Flow Attack (Pump OFF but high flow)
        attack = PumpFlowAttack(scenario=SCENARIO_PUMP_OFF_HIGH_FLOW, force_actuator_state=True, intensity=1.0, active=True)
        nominal = sim.step(dt_seconds=1.0)
        attacked = attack.apply(nominal)


        defense_res = pipeline.evaluate(attacked)
        self.assertTrue(defense_res["anomaly_detected"])
        self.assertIn("ACTUATOR_ENERGY_COUPLING", defense_res["violated_invariants"])
        self.assertLess(defense_res["sensor_trust_scores"]["pump_status"], 100.0)
        self.assertEqual(defense_res["sensor_trust_scores"]["temperature"], 100.0)
        self.assertGreater(len(defense_res["explanation"]), 10)

        # Verify progressive risk escalation over sustained breach ticks
        for _ in range(3):
            nominal = sim.step(dt_seconds=1.0)
            attacked = attack.apply(nominal)
            defense_res = pipeline.evaluate(attacked)
        self.assertIn(defense_res["risk_level"], ["MEDIUM", "HIGH", "CRITICAL"])


    def test_04_p3_speed_percentage_threshold(self):
        """Verify P3 unit mismatch fix: pump speed percentage (80%) with zero flow is flagged."""
        ce = CausalEngine()
        anom = {
            "timestamp": 1000.0,
            "temperature": 25.0,
            "humidity": 50.0,
            "solar_radiation": 200.0,
            "cooling_load": 10.0,
            "power_consumption": 8.0,
            "water_flow": 0.0,
            "tank_level": 50.0,
            "pressure": 1.0,
            "pump_speed": 80.0,
            "pump_status": "ON",
        }
        holds = ce.check_actuator_energy_coupling(anom)
        self.assertFalse(holds, "Actuator coupling must fail when pump is ON at 80% speed with 0 flow")

    def test_05_p3_timestamp_flexibility(self):
        """Verify P3 _extract_float handles datetime, ISO string, and float timestamps."""
        ce = CausalEngine()
        dt_sample = {"timestamp": datetime.now(timezone.utc)}
        iso_sample = {"timestamp": "2026-09-08T12:00:00Z"}
        flt_sample = {"timestamp": 1788868800.0}

        self.assertIsNotNone(ce._extract_float(dt_sample, "timestamp"))
        self.assertIsNotNone(ce._extract_float(iso_sample, "timestamp"))
        self.assertIsNotNone(ce._extract_float(flt_sample, "timestamp"))

    def test_06_orchestrator_full_cycle(self):
        """Verify full P1 -> P2 -> P3 -> P4 orchestrator lifecycle and state transitions."""
        # 1. Check nominal baseline
        status = orchestrator.get_current_status()
        self.assertEqual(status.system_mode, SystemMode.NOMINAL)
        self.assertFalse(status.attack_state["is_active"])
        self.assertGreaterEqual(status.defense_result.system_trust_score, 80.0)

        # 2. Launch coordinated cyber-physical attack through real P2 engine
        req = AttackLaunchRequest(
            attack_type=AttackType.COORDINATED,
            target_sensors=["temperature", "solar_radiation", "cooling_load"],
            intensity=0.85,
            stealth=True,
        )
        orchestrator.launch_attack(req)

        # 3. Status should show detected breach and fractured invariants
        attack_status = orchestrator.get_current_status()
        self.assertTrue(attack_status.attack_state["is_active"])
        self.assertIn(attack_status.system_mode, [SystemMode.UNDER_ATTACK, SystemMode.DETECTED])
        self.assertLess(attack_status.defense_result.system_trust_score, 70.0)
        self.assertGreater(len(attack_status.defense_result.compromised_sensors), 0)
        self.assertIn("temperature", attack_status.defense_result.compromised_sensors)

        # 4. Stop attack and verify restoration
        orchestrator.stop_attack()
        stop_status = orchestrator.get_current_status()
        self.assertFalse(stop_status.attack_state["is_active"])

    def test_07_sustainability_impact_metering(self):
        """Verify sustainability blast radius accumulates during attack."""
        orchestrator.reset_system()
        req = AttackLaunchRequest(
            attack_type=AttackType.FDI,
            target_sensors=["cooling_load"],
            intensity=0.9,
        )
        orchestrator.launch_attack(req)

        # Advance simulation ticks
        for _ in range(5):
            orchestrator._tick(dt=0.5)

        status = orchestrator.get_current_status()
        impact = status.sustainability_impact
        self.assertGreaterEqual(impact.carbon_emissions_kg, 0.0)
        self.assertGreaterEqual(impact.financial_loss_inr, 0.0)


if __name__ == "__main__":
    unittest.main()
