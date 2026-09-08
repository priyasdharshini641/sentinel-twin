"""
SENTINEL TWIN — Main Application Entrypoint
Role: P4 (API & System Integration Engineer)
Problem Statement: PS 18 SensorSentry — Spoofing Detection & Sensor Fusion
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import router as api_router
from app.services.orchestrator import orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage lifecycle: Start background simulation ticker on startup; cancel on shutdown."""
    print("[SENTINEL TWIN] Initializing Cyber-Physical Simulation Loop...")
    await orchestrator.start()
    yield
    print("[SENTINEL TWIN] Shutting down simulation ticker...")
    await orchestrator.stop()


app = FastAPI(
    title="SENTINEL TWIN — Cyber-Physical Reality Engine",
    description=(
        "Production backend for Cyber-Physical Truth Verification and Sensor Spoofing Detection. "
        "Evaluates high-dimensional telemetry against thermodynamic, psychrometric, and motor affinity invariants."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for all frontend development servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


import os
from fastapi.responses import RedirectResponse, FileResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Mount API routes
app.include_router(api_router)


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    """Serve the Cyber-Physical Reality Dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System Health"])
async def health():
    """
    Dual-Layer Health Check:
    1. Software Service Health: Is FastAPI and the background simulation thread running?
    2. Cyber-Physical Health: Is the physical digital twin secure, or is an attack actively corrupting telemetry?
    """
    snapshot = orchestrator.get_current_status()
    is_attack_active = snapshot.attack_state.get("is_active", False)
    threat = snapshot.defense_result.threat_level.value
    trust = snapshot.defense_result.system_trust_score

    if is_attack_active:
        overall_status = f"COMPROMISED ({snapshot.system_mode.value})"
    else:
        overall_status = "HEALTHY"

    return {
        "status": overall_status,
        "service_health": "ONLINE",
        "cyber_physical_health": "COMPROMISED" if is_attack_active else "NOMINAL",
        "threat_level": threat,
        "system_trust_score": trust,
        "active_attack": is_attack_active,
        "attack_type": snapshot.attack_state.get("attack_type") if is_attack_active else None,
        "role": "P4 Integration & API Layer",
        "orchestrator_running": orchestrator.is_running,
        "tick_index": orchestrator.tick_index
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
