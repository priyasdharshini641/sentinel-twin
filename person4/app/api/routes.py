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
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException

from app.models.telemetry import (
    CustomAttackRequest,
    SystemStatusResponse, AttackLaunchRequest, GenericResponse
)
from app.services.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["Sentinel Twin System API"])


# -----------------------------------------------------------------------------
# 1. REST ENDPOINTS
# -----------------------------------------------------------------------------
@router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    summary="Get Current System Status",
    description="Returns the real-time unified state including P1 ground truth, P2 reported telemetry, P3 causal defense, and sustainability impact."
)
async def get_system_status():
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
    description="Injects false data, gradual drift, coordinated spoofing, or freeze attacks into the telemetry stream."
)
async def launch_attack(request: AttackLaunchRequest):
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
    except Exception:
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
    return orchestrator.get_benchmark_comparison()


@router.get(
    "/causal-graph",
    summary="Structured Cyber-Physical Causal DAG Graph",
    description="Directed graph topology with real-time physical invariant bonds (Thermodynamics, Bernoulli, Motor Affinity) and fracture states."
)
async def get_causal_graph():
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
    matrix = agricultural_engine.evaluate_farming_matrix(status.reported_telemetry)
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
    is_outlier = status.defense_result.threat_level.value in ["ELEVATED", "CRITICAL"]

    decision = agricultural_engine.compute_3tier_decision(
        telemetry=status.reported_telemetry,
        is_statistical_outlier=is_outlier,
        is_causal_violation=is_causal,
        violated_invariants=violated
    )
    return decision
