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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System Health"])
async def health_check():
    """Health check endpoint for container orchestrators and monitoring probes."""
    return {
        "status": "HEALTHY",
        "service": "sentinel-twin-backend",
        "role": "P4 Integration & API Layer",
        "orchestrator_running": orchestrator.is_running,
        "tick_index": orchestrator.tick_index
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
