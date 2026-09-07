"""
SENTINEL TWIN — P4 Backend Verification Suite
Tests the complete API layer, schema contract, attack triggers, and invariant defense.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.orchestrator import orchestrator

client = TestClient(app)


def setup_function():
    """Reset orchestrator state before each test."""
    orchestrator.reset_system()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["role"] == "P4 Integration & API Layer"


def test_system_status_frozen_11_fields_contract():
    """Verify that both ground_truth and reported_telemetry contain all 11 required fields."""
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()

    required_fields = [
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
        "timestamp"
    ]

    for stream in ["ground_truth", "reported_telemetry"]:
        assert stream in data
        stream_data = data[stream]
        for field in required_fields:
            assert field in stream_data, f"Missing required field '{field}' in {stream}"

    # Verify nominal baseline state
    assert data["defense_result"]["system_trust_score"] >= 80.0
    assert data["system_mode"] == "NOMINAL"


def test_attack_launch_and_defense_detection():
    """Launch a coordinated cyber-physical attack and verify defense triggers."""
    payload = {
        "attack_type": "coordinated",
        "target_sensors": ["temperature", "solar_radiation", "cooling_load"],
        "intensity": 0.85,
        "stealth": True
    }

    response = client.post("/api/attack/launch", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"

    # Fetch status after attack
    status_resp = client.get("/api/system/status")
    status_data = status_resp.json()

    # Attack should be active and detected
    assert status_data["attack_state"]["is_active"] is True
    assert status_data["attack_state"]["attack_type"] == "coordinated"
    assert status_data["system_mode"] in ["UNDER_ATTACK", "DETECTED"]

    # Trust score should have collapsed due to physical invariant violation
    defense = status_data["defense_result"]
    assert defense["system_trust_score"] < 70.0
    assert len(defense["compromised_sensors"]) > 0
    assert "temperature" in defense["compromised_sensors"]

    # Invariants should be flagged
    violated_invariants = [inv for inv in defense["invariants"] if inv["violated"]]
    assert len(violated_invariants) >= 1

    # Detective forensic deduction should be populated
    assert "DETECTIVE FORENSIC DEDUCTION" in defense["forensic_deduction"]

    # Self-healing virtual telemetry should be imputed
    assert "imputed_cooling_load" in defense["healed_telemetry"] or "imputed_temperature" in defense["healed_telemetry"]


def test_attack_stop():
    """Verify stopping an attack restores nominal state."""
    # Launch attack
    client.post("/api/attack/launch", json={"attack_type": "fdi", "target_sensors": ["temperature"]})

    # Stop attack
    stop_resp = client.post("/api/attack/stop")
    assert stop_resp.status_code == 200

    status = client.get("/api/system/status").json()
    assert status["attack_state"]["is_active"] is False


def test_telemetry_history():
    """Verify history buffer endpoint returns sequential time-series ticks."""
    response = client.get("/api/telemetry/history?limit=10")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert "temperature_truth" in history[0]
    assert "temperature_reported" in history[0]


def test_system_reset():
    """Verify system reset endpoint zeroes out counters."""
    response = client.post("/api/system/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"


def test_health_check_dynamic_under_attack():
    """Verify that /health dynamically transitions to COMPROMISED during an attack."""
    # 1. Check nominal
    resp_nom = client.get("/health").json()
    assert resp_nom["status"] == "HEALTHY"
    assert resp_nom["cyber_physical_health"] == "NOMINAL"

    # 2. Launch attack
    client.post("/api/attack/launch", json={"attack_type": "coordinated", "intensity": 0.8})

    # 3. Health check should reflect physical compromise
    resp_attack = client.get("/health").json()
    assert "COMPROMISED" in resp_attack["status"]
    assert resp_attack["cyber_physical_health"] == "COMPROMISED"
    assert resp_attack["active_attack"] is True
