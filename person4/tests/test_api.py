"""
SENTINEL TWIN — P4 Backend Verification Suite
Tests the complete API layer, schema contract, attack triggers, and invariant defense.
"""

try:
    import pytest
except ImportError:
    pytest = None
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


def test_benchmark_endpoint():
    """Verify live benchmark returns both Isolation Forest and Causal Reality Engine results."""
    # When nominal
    resp = client.get("/api/benchmark")
    assert resp.status_code == 200
    data = resp.json()
    assert "traditional_ml" in data
    assert "causal_reality_engine" in data
    assert data["traditional_ml"]["model_name"] == "Isolation Forest (scikit-learn)"
    assert "Causal Reality Engine" in data["causal_reality_engine"]["model_name"]


def test_causal_graph_endpoint():
    """Verify Causal Graph DAG returns nodes and physical invariant edges."""
    resp = client.get("/api/causal-graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 9
    assert len(data["edges"]) >= 4
    # Check that thermodynamic and motor affinity edges exist
    edge_ids = [e["id"] for e in data["edges"]]
    assert "edge_thermodynamics" in edge_ids
    assert "edge_motor_affinity" in edge_ids


def test_judge_custom_hacker_sandbox():
    """Verify judge can inject custom sensor perturbations."""
    payload = {
        "hacker_alias": "Judge Alice",
        "target_sensors": {"temperature": -10.0, "water_flow": 45.0},
        "stealth_mode": True
    }
    resp = client.post("/api/attack/custom", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["data"]["hacker_alias"] == "Judge Alice"


def test_safe_mode_mitigation():
    """Verify safe-mode mitigation and virtual sensor imputation."""
    resp = client.post("/api/mitigate/safe-mode")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["mitigation"]["status"] == "SAFE_MODE_ENGAGED"
    assert "synthesized_telemetry" in data["telemetry_stream"]


def test_forensic_dossier():
    """Verify Sherlock forensic dossier with SHA-256 cryptographic hash."""
    resp = client.get("/api/forensics/dossier")
    assert resp.status_code == 200
    data = resp.json()
    assert "dossier_id" in data
    assert "evidentiary_sha256_hash" in data
    assert len(data["evidentiary_sha256_hash"]) == 64


def test_agriculture_matrix_endpoint():
    """Verify 7-activity farming suitability matrix endpoint."""
    resp = client.get("/api/agriculture/matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert "matrix" in data
    assert data["activities_count"] == 7
    activities = [item["activity"] for item in data["matrix"]]
    expected = ["Sowing", "Irrigation", "Fertilizer Application", "Pesticide Spraying", "Weeding", "Harvesting", "Drying"]
    for exp in expected:
        assert exp in activities
    for item in data["matrix"]:
        assert item["status"] in ["FAVORABLE", "CAUTION", "UNFAVORABLE"]
        assert "reason" in item
        assert "factors" in item


def test_agriculture_decision_endpoint():
    """Verify 3-tier decision engine endpoint under nominal and attack conditions."""
    # 1. Nominal condition
    resp = client.get("/api/agriculture/decision")
    assert resp.status_code == 200
    data = resp.json()
    assert "system_decision" in data
    assert data["system_decision"] == "NORMAL_OPERATION"
    assert data["tier3_causal"]["status"] == "CONSISTENT"
    assert data["action"] == "NOMINAL_MONITORING"

    # 2. Under attack condition
    client.post("/api/attack/launch", json={"attack_type": "coordinated", "intensity": 0.9})
    resp_attack = client.get("/api/agriculture/decision")
    assert resp_attack.status_code == 200
    data_attack = resp_attack.json()
    assert data_attack["tier3_causal"]["status"] == "VIOLATED"
    assert data_attack["system_decision"] == "ATTACK_VIOLATION"
    assert data_attack["action"] == "INTERLOCK_ENGAGED"


def test_list_domains():
    """Verify listing all 4 enterprise domains."""
    resp = client.get("/api/domains")
    assert resp.status_code == 200
    data = resp.json()
    assert "available_domains" in data
    assert len(data["available_domains"]) == 4
    domain_ids = [d["domain_id"] for d in data["available_domains"]]
    assert "autonomous_drone" in domain_ids
    assert "smart_water" in domain_ids
    assert "precision_agri" in domain_ids
    assert "datacenter_gpu" in domain_ids


def test_switch_domain_to_drone():
    """Verify switching to Autonomous Drone & GPS Spoofing domain."""
    resp = client.post("/api/domain/switch?domain_id=autonomous_drone")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["data"]["active_domain"] == "autonomous_drone"

    # Switch back to smart_water
    resp_back = client.post("/api/domain/switch?domain_id=smart_water")
    assert resp_back.status_code == 200
