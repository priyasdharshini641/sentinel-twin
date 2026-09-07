"""P3 Defense Suite Integration Tests (Person 3)."""

import inspect
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from person3.causal_engine import CausalEngine
from person3.trust_engine import TrustEngine
from person3.detective_explainer import DetectiveExplainer
from person3.defense_pipeline import DefensePipeline


def normal_snapshot(i=0):
    return {
        "timestamp": 1000.0 + i * 1.0,
        "temperature": 25.0 + i * 0.05,
        "humidity": 50.0 - i * 0.02,
        "solar_radiation": 100.0 + i * 0.5,
        "cooling_load": 10.0,
        "power_consumption": 3.5,
        "water_flow": 5.0,
        "tank_level": 50.0 - i * 0.01,
        "pressure": 2.0,
        "pump_speed": 1500.0,
        "pump_status": 1,
    }


def test_normal_telemetry():
    pipeline = DefensePipeline()
    res = None
    for i in range(5):
        res = pipeline.evaluate(normal_snapshot(i))
    assert res is not None
    assert res["anomaly_detected"] is False
    assert res["violated_invariants"] == []
    assert res["system_trust_score"] == 100.0
    assert res["risk_level"] == "LOW"
    assert set(res.keys()) == {
        "anomaly_detected",
        "violated_invariants",
        "sensor_trust_scores",
        "system_trust_score",
        "risk_level",
        "explanation",
        "recommended_action",
    }


def test_thermodynamic_inconsistency():
    pipeline = DefensePipeline()
    for i in range(3):
        pipeline.evaluate(normal_snapshot(i))
    anom = normal_snapshot(3)
    anom["power_consumption"] = 0.0
    res = pipeline.evaluate(anom)
    assert res["anomaly_detected"] is True
    assert "THERMODYNAMIC_BALANCE" in res["violated_invariants"]
    assert res["sensor_trust_scores"]["temperature"] < 100.0
    assert res["sensor_trust_scores"]["tank_level"] == 100.0


def test_actuator_inconsistency():
    pipeline = DefensePipeline()
    for i in range(3):
        pipeline.evaluate(normal_snapshot(i))
    anom = normal_snapshot(3)
    anom["pump_status"] = 0
    anom["pump_speed"] = 0.0
    res = pipeline.evaluate(anom)
    assert res["anomaly_detected"] is True
    assert "ACTUATOR_ENERGY_COUPLING" in res["violated_invariants"]
    assert res["sensor_trust_scores"]["pump_status"] < 100.0
    assert res["sensor_trust_scores"]["temperature"] == 100.0


def test_temporal_anomaly():
    pipeline = DefensePipeline()
    for i in range(4):
        pipeline.evaluate(normal_snapshot(i))
    anom = normal_snapshot(4)
    anom["temperature"] = 95.0
    res = pipeline.evaluate(anom)
    assert "TEMPORAL_CONTINUITY" in res["violated_invariants"]
    assert res["sensor_trust_scores"]["temperature"] < 100.0
    assert res["sensor_trust_scores"]["tank_level"] == 100.0


def test_multiple_invariant_violations():
    pipeline = DefensePipeline()
    for i in range(3):
        pipeline.evaluate(normal_snapshot(i))
    anom = normal_snapshot(3)
    anom["pump_status"] = 0
    anom["pump_speed"] = 0.0
    anom["power_consumption"] = 0.0
    res = pipeline.evaluate(anom)
    assert len(res["violated_invariants"]) >= 2
    assert res["system_trust_score"] < 100.0
    assert len(res["explanation"]) > 0
    assert len(res["recommended_action"]) > 0


def test_recovery_progression():
    pipeline = DefensePipeline()
    for i in range(3):
        pipeline.evaluate(normal_snapshot(i))
    anom = normal_snapshot(3)
    anom["pump_status"] = 0
    res_anom = pipeline.evaluate(anom)
    assert res_anom["sensor_trust_scores"]["pump_status"] == 85.0

    res_rec = pipeline.evaluate(normal_snapshot(4))
    assert res_rec["sensor_trust_scores"]["pump_status"] == 87.0
    assert res_rec["sensor_trust_scores"]["pump_status"] < 100.0


def test_risk_consistency():
    pipeline = DefensePipeline()
    pipeline.trust_engine._scores = {s: 100.0 for s in TrustEngine.KNOWN_SENSORS}
    assert pipeline.trust_engine.get_risk_level() == "LOW"
    pipeline.trust_engine._scores = {s: 75.0 for s in TrustEngine.KNOWN_SENSORS}
    assert pipeline.trust_engine.get_risk_level() == "MEDIUM"
    pipeline.trust_engine._scores = {s: 50.0 for s in TrustEngine.KNOWN_SENSORS}
    assert pipeline.trust_engine.get_risk_level() == "HIGH"
    pipeline.trust_engine._scores = {s: 25.0 for s in TrustEngine.KNOWN_SENSORS}
    assert pipeline.trust_engine.get_risk_level() == "CRITICAL"


def test_no_attack_metadata_exposure():
    pipeline = DefensePipeline()
    sig = inspect.signature(pipeline.evaluate)
    assert list(sig.parameters.keys()) == ["telemetry"]
    src = inspect.getsource(DefensePipeline)
    for forbidden in [
        "attack_type",
        "attack_detected",
        "attack_confidence",
        "ground_truth",
        "attack_metadata",
        "attacker",
        "classification",
    ]:
        assert forbidden not in src.lower()


def test_component_injection():
    ce = CausalEngine()
    te = TrustEngine()
    de = DetectiveExplainer()
    pipeline = DefensePipeline(causal_engine=ce, trust_engine=te, detective_explainer=de)
    assert pipeline.causal_engine is ce
    assert pipeline.trust_engine is te
    assert pipeline.detective_explainer is de


if __name__ == "__main__":
    test_normal_telemetry()
    test_thermodynamic_inconsistency()
    test_actuator_inconsistency()
    test_temporal_anomaly()
    test_multiple_invariant_violations()
    test_recovery_progression()
    test_risk_consistency()
    test_no_attack_metadata_exposure()
    test_component_injection()
    print("All Person 3 defense suite tests passed successfully!")
