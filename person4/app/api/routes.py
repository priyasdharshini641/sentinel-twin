"""
SENTINEL TWIN — API Routes & WebSocket Stream
Role: P4 (API & System Integration Engineer)

Endpoints:
- GET  /api/system/status     : Full current snapshot of physical twin, attack, and defense
- GET  /api/telemetry/history : Time-series history buffer for frontend charts
- POST /api/attack/launch     : Red team attack injector
- POST /api/attack/stop       : Halt ongoing attack
- POST /api/system/reset      : Reset plant physics and counters
- GET  /api/system/invariants : Detail on the 4 Cyber-Physical Invariant Contracts
- WS   /api/ws/telemetry      : Live real-time WebSocket telemetry stream
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException

from app.models.telemetry import (
    CustomAttackRequest,
    SystemStatusResponse, AttackLaunchRequest, GenericResponse,
    ThreatLevel
)
from app.services.orchestrator import orchestrator


router = APIRouter(prefix="/api", tags=["Sentinel Twin System API"])

# -----------------------------------------------------------------------------
# 0. MULTI-SECTOR ENTERPRISE DOMAIN SWITCHER
# -----------------------------------------------------------------------------
from app.services.domains.domain_manager import domain_manager

@router.get(
    "/domains",
    summary="List Enterprise Digital Twin Domains",
    description="Returns metadata for the 4 distinct enterprise sectors: Autonomous Drone GPS Spoofing, Smart Municipal Water, Precision Agriculture, and Hyperscale AI Data Center."
)
async def list_domains():
    return {
        "active_domain": domain_manager.active_domain_id,
        "available_domains": domain_manager.list_available_domains()
    }


@router.post(
    "/domain/switch",
    summary="Switch Active Enterprise Digital Twin Domain",
    description="Transitions the digital twin engine to a different enterprise sector (e.g. 'autonomous_drone', 'smart_water', 'precision_agri', 'datacenter_gpu')."
)
async def switch_domain(domain_id: str = Query(..., description="Target sector ID")):
    try:
        res = domain_manager.set_active_domain(domain_id)
        # Trigger attack toggle in that domain if requested
        service = domain_manager.get_domain_service(domain_id)
        if service:
            service.reset()
        return GenericResponse(status="SUCCESS", message=res["message"], data=res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# -----------------------------------------------------------------------------
# 1. REST ENDPOINTS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 1. REST ENDPOINTS (DOMAIN-AWARE)
# -----------------------------------------------------------------------------
@router.get(
    "/system/status",
    summary="Get Current System Status",
    description="Returns the real-time unified state including ground truth, reported telemetry, causal defense, and blast radius for the active enterprise domain."
)
async def get_system_status():
    active_service = domain_manager.get_domain_service()
    if active_service:
        truth = active_service.step_truth(dt=0.5)
        reported = active_service.apply_attack(truth, dt=0.5)
        defense = active_service.evaluate_invariants(reported)

        norm_invariants = []
        for inv in defense.get("invariants", []):
            norm_invariants.append({
                "invariant_id": inv.get("id") or inv.get("invariant_id") or "INV_DOMAIN",
                "name": inv.get("name", "Domain Invariant"),
                "law": inv.get("law", "Domain Physical Law"),
                "violated": bool(inv.get("violated", False)),
                "residual": float(inv.get("residual", 0.0)),
                "threshold": float(inv.get("threshold", 1.0)),
                "description": str(inv.get("description", "")),
            })

        sensor_trust = defense.get("sensor_trust_scores", {})
        if not sensor_trust:
            sensor_trust = {k: (30.0 if k in defense.get("compromised_sensors", []) else 100.0) for k in reported.keys()}

        healed = defense.get("healed_telemetry", dict(reported))

        threat = defense.get("threat_level", "LOW")
        mode = "DETECTED" if threat != "LOW" else "NOMINAL"

        defense_result = {
            "system_trust_score": float(defense.get("system_trust_score", 100.0)),
            "threat_level": threat,
            "sensor_trust_scores": sensor_trust,
            "invariants": norm_invariants,
            "compromised_sensors": defense.get("compromised_sensors", []),
            "forensic_deduction": defense.get("forensic_deduction", "Domain telemetry verified."),
            "healed_telemetry": healed,
        }

        sustainability = {
            "water_wasted_liters": 0.0,
            "energy_wasted_kwh": 0.0,
            "carbon_emissions_kg": 0.0,
            "financial_loss_inr": 0.0,
            "financial_loss_usd": 0.0,
        }

        return {
            "timestamp": truth.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "active_domain": domain_manager.active_domain_id,
            "system_mode": mode,
            "tick_index": orchestrator.tick_index,
            "ground_truth": truth,
            "reported_telemetry": reported,
            "defense_result": defense_result,
            "attack_state": {
                "is_active": active_service.is_attack_active,
                "active": active_service.is_attack_active,
                "attack_type": "radio_gps_spoofing" if active_service.is_attack_active else "NONE",
                "type": "radio_gps_spoofing" if active_service.is_attack_active else "NONE",
            },
            "sustainability_impact": sustainability,
        }
    return orchestrator.get_current_status()



@router.get(
    "/telemetry/history",
    response_model=List[Dict[str, Any]],
    summary="Get Historical Telemetry Trend",
    description="Returns the last N simulation ticks for live frontend line charts and trend analysis."
)
async def get_telemetry_history(
    limit: int = Query(default=60, ge=10, le=120, description="Number of historical ticks to retrieve")
):
    return orchestrator.get_history(limit=limit)


@router.post(
    "/attack/launch",
    response_model=GenericResponse,
    summary="Launch Cyber-Physical Attack",
    description="Injects false data, gradual drift, coordinated spoofing, or radio GPS spoofing into the active domain."
)
async def launch_attack(request: AttackLaunchRequest):
    active_service = domain_manager.get_domain_service()
    if active_service:
        active_service.is_attack_active = True
        return GenericResponse(
            status="SUCCESS",
            message=f"Attack activated for active domain '{domain_manager.active_domain_id}'.",
            data={"domain": domain_manager.active_domain_id, "is_attack_active": True}
        )
    result = orchestrator.launch_attack(request)
    return GenericResponse(
        status="SUCCESS",
        message=f"Attack '{request.attack_type.value}' successfully launched on {request.target_sensors}.",
        data=result
    )


@router.post(
    "/attack/stop",
    response_model=GenericResponse,
    summary="Stop Active Cyber-Physical Attack",
    description="Terminates all active perturbations and restores reported telemetry to ground truth."
)
async def stop_attack():
    active_service = domain_manager.get_domain_service()
    if active_service:
        active_service.is_attack_active = False
        return GenericResponse(
            status="SUCCESS",
            message=f"Attack stopped for domain '{domain_manager.active_domain_id}'. Telemetry restored to nominal truth.",
            data={"domain": domain_manager.active_domain_id, "is_attack_active": False}
        )
    result = orchestrator.stop_attack()
    return GenericResponse(
        status="SUCCESS",
        message=result.get("message", "Attack stopped."),
        data=result
    )


@router.post(
    "/system/reset",
    response_model=GenericResponse,
    summary="Reset Digital Twin",
    description="Resets the physical simulation time, clears red team vectors, and zeroes sustainability impact meters."
)
async def reset_system():
    result = orchestrator.reset_system()
    return GenericResponse(
        status="SUCCESS",
        message=result.get("message", "System reset."),
        data=result
    )


@router.get(
    "/system/invariants",
    summary="List Cyber-Physical Invariant Contracts",
    description="Returns metadata and mathematical governing laws of the 4 physical invariants."
)
async def get_invariants():
    status = orchestrator.get_current_status()
    return {
        "count": len(status.defense_result.invariants),
        "invariants": status.defense_result.invariants
    }


# -----------------------------------------------------------------------------
# 2. WEBSOCKET REAL-TIME BROADCASTER
# -----------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_status(self, snapshot: SystemStatusResponse):
        payload = snapshot.model_dump_json()
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Continuous real-time telemetry stream for high-fps UI animations.
    Pushes fresh snapshots at 2 Hz or responds to client pings.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Broadcast snapshot every 500ms
            snapshot = orchestrator.get_current_status()
            await websocket.send_text(snapshot.model_dump_json())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except asyncio.CancelledError:
        manager.disconnect(websocket)
        raise
    except Exception as exc:
        logging.getLogger("uvicorn.error").warning(f"WebSocket closed: {exc}")
        manager.disconnect(websocket)



# -----------------------------------------------------------------------------
# 3. STANDOUT INNOVATION ENDPOINTS
# -----------------------------------------------------------------------------
@router.get(
    "/benchmark",
    summary="Live ML Benchmark (Isolation Forest vs Causal Reality Engine)",
    description="Mathematical proof: Traditional ML is fooled by coordinated stealth spoofing, while Sentinel Twin catches it."
)
async def get_benchmark():
    active_service = domain_manager.get_domain_service()
    if active_service:
        truth = active_service.step_truth(dt=0.0)
        reported = active_service.apply_attack(truth, dt=0.0)
        defense = active_service.evaluate_invariants(reported)
        return active_service.evaluate_benchmark(reported, defense, active_service.is_attack_active)
    return orchestrator.get_benchmark_comparison()


@router.get(
    "/causal-graph",
    summary="Structured Cyber-Physical Causal DAG Graph",
    description="Directed graph topology with real-time physical invariant bonds for the active domain."
)
async def get_causal_graph():
    active_service = domain_manager.get_domain_service()
    if active_service:
        truth = active_service.step_truth(dt=0.0)
        reported = active_service.apply_attack(truth, dt=0.0)
        defense = active_service.evaluate_invariants(reported)
        return active_service.get_causal_graph(reported, defense)
    return orchestrator.get_causal_graph()


@router.post(
    "/attack/custom",
    summary="Judge's Live Hacker Sandbox",
    description="Allows judges or red-teamers to inject custom sensor perturbations live on stage to test system resilience."
)
async def launch_custom_attack(request: CustomAttackRequest):
    result = orchestrator.launch_custom_attack(request)
    return GenericResponse(
        status="SUCCESS",
        message=f"Custom hacker injection active from '{request.hacker_alias}'.",
        data=result
    )


@router.post(
    "/mitigate/safe-mode",
    summary="Zero-Downtime Safe-Mode Virtual Sensor Imputation",
    description="Activates real-time virtual telemetry imputation by inverting physical invariant laws to insulate automated controllers."
)
async def activate_safe_mode():
    active_service = domain_manager.get_domain_service()
    if active_service:
        truth = active_service.step_truth(dt=0.0)
        reported = active_service.apply_attack(truth, dt=0.0)
        defense = active_service.evaluate_invariants(reported)
        res = active_service.self_heal(reported, defense)
        return {
            "status": "SUCCESS",
            "domain": domain_manager.active_domain_id,
            "mitigation": {"status": "SAFE_MODE_ENGAGED", "mode": "VIRTUAL_IMPUTATION_ACTIVE"},
            "telemetry_stream": res
        }
    res = orchestrator.activate_safe_mode()
    stream = orchestrator.get_healed_stream()
    return {
        "status": "SUCCESS",
        "mitigation": res,
        "telemetry_stream": stream
    }


@router.get(
    "/forensics/dossier",
    summary="Sherlock Digital Forensic Incident Dossier",
    description="Generates an executive forensic security incident dossier with cryptographic SHA-256 evidence digest and plain-English deduction."
)
async def get_forensic_dossier():
    active_service = domain_manager.get_domain_service()
    if active_service:
        truth = active_service.step_truth(dt=0.0)
        reported = active_service.apply_attack(truth, dt=0.0)
        defense = active_service.evaluate_invariants(reported)
        return active_service.generate_forensic_dossier(
            reported, defense, None, {"is_active": active_service.is_attack_active}
        )
    return orchestrator.get_forensic_dossier()


# -----------------------------------------------------------------------------
# 4. CLIMATE-SMART AGRICULTURE & DECISION MATRIX ENDPOINTS
# -----------------------------------------------------------------------------
from app.services.agriculture import agricultural_engine


@router.get(
    "/agriculture/matrix",
    summary="7-Activity Farming Suitability Matrix",
    description="Evaluates real-time agro-climate and irrigation parameters across Sowing, Irrigation, Fertilizer, Pesticide, Weeding, Harvesting, and Drying."
)
async def get_farming_matrix():
    status = orchestrator.get_current_status()
    violated = [inv.name for inv in status.defense_result.invariants if inv.violated]
    compromised = status.defense_result.compromised_sensors or []
    attack_active = status.attack_state.get("is_active", False) if isinstance(status.attack_state, dict) else getattr(status.attack_state, "is_active", False)
    is_attack = attack_active or len(violated) > 0

    matrix = agricultural_engine.evaluate_farming_matrix(
        telemetry=status.reported_telemetry,
        compromised_sensors=compromised,
        violated_invariants=violated,
        is_attack_active=is_attack
    )
    return {
        "crop_stage": agricultural_engine.crop_stage,
        "activities_count": len(matrix),
        "matrix": matrix
    }


@router.get(
    "/agriculture/decision",
    summary="3-Tier Agro-Cyber Decision Engine",
    description="Synthesizes Climate Severity (Tier 1), Statistical Outlier (Tier 2), and Causal Reality (Tier 3) into an automated irrigation decision."
)
async def get_agricultural_decision():
    status = orchestrator.get_current_status()
    # Check if any invariant violated
    violated = [inv.name for inv in status.defense_result.invariants if inv.violated]
    is_causal = len(violated) > 0
    attack_active = status.attack_state.get("is_active", False) if isinstance(status.attack_state, dict) else getattr(status.attack_state, "is_active", False)
    is_outlier = status.defense_result.threat_level.value in ["ELEVATED", "CRITICAL"] or attack_active

    decision = agricultural_engine.compute_3tier_decision(
        telemetry=status.reported_telemetry,
        is_statistical_outlier=is_outlier,
        is_causal_violation=is_causal,
        violated_invariants=violated
    )
    return decision
