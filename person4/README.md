# SENTINEL TWIN — Cyber-Physical Reality Engine & API
> **Problem Statement:** PS 18 SensorSentry — Spoofing Detection & Sensor Fusion  
> **Team Role:** **P4 — API & System Integration Engineer**  
> **Maintainer:** `ghemanya2301@gmail.com`  
> **Core Mission:** Cyber-Physical Truth Verification for automated climate infrastructure using Thermodynamic, Psychrometric, Hydraulic, and Motor Affinity Invariants.

---

## 📌 Architecture & Team Integration (P1 → P2 → P3 → P4)

This repository houses the central production API and pipeline orchestrator built for the **SENTINEL TWIN** platform. It integrates all 4 core layers of the system:

```
┌────────────────────────────────────────────────────────┐
│  P1: Physical Simulation Service (simulation.py)       │
│  Generates pristine ground truth telemetry (11 fields) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  P2: Red Team Attack Engine (attack_engine.py)         │
│  Applies FDI, Gradual Drift, Coordinated Spoofing      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  P3: Blue Team Causal Reality Engine (defense.py)      │
│  Evaluates 4 Physical Invariants, generates forensic   │
│  detective explanations and self-healing virtual state │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  P4: FastAPI System Integration & API (orchestrator)   │
│  Thread-safe state manager, 2 Hz async ticker,         │
│  REST endpoints, WebSocket broadcaster, and metrics    │
└────────────────────────────────────────────────────────┘
```

---

## 📋 The Frozen 11-Field Telemetry Contract

Every sensor reading in the pipeline strictly adheres to this contract:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Telemetry:
    temperature: float          # °C (Ambient Outdoor Temperature)
    humidity: float             # % (Relative Humidity)
    solar_radiation: float      # W/m² (Solar Irradiance)
    cooling_load: float         # kW (Cooling Thermal Load)
    power_consumption: float    # kW (Total Electrical Draw)
    water_flow: float           # L/min (Chilled Water / Irrigation Flow)
    tank_level: float           # % (Buffer / Storage Tank Level)
    pump_status: str            # 'ON' / 'OFF'
    pump_speed: float           # % (VFD Pump Speed 0-100%)
    pressure: float             # bar (Hydraulic Loop Pressure)
    timestamp: datetime         # ISO-8601 Timestamp
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/system/status` | Current unified state (ground truth, reported, defense, blast radius) |
| `GET` | `/api/telemetry/history?limit=60` | Last N ticks for live frontend line charts |
| `POST` | `/api/attack/launch` | Launch FDI, Drift, or Coordinated attack |
| `POST` | `/api/attack/stop` | Terminate active attack and restore telemetry |
| `POST` | `/api/system/reset` | Reset simulation time, meters, and counters |
| `GET` | `/api/system/invariants` | List of 4 Cyber-Physical Invariant equations |
| `WS` | `/api/ws/telemetry` | 2 Hz low-latency live WebSocket stream |

### Sample Attack Payload (`POST /api/attack/launch`):
```json
{
  "attack_type": "coordinated",
  "target_sensors": ["temperature", "solar_radiation", "cooling_load"],
  "intensity": 0.85,
  "stealth": true
}
```

---

## 🛠️ Step-by-Step Git Repository Setup

To link this code to your personal or team Git repository under `ghemanya2301@gmail.com`:

```bash
# 1. Initialize git in the project root
git init

# 2. Configure your committer identity
git config user.name "Hemanya G"
git config user.email "ghemanya2301@gmail.com"

# 3. Stage all files
git add .

# 4. Create your initial commit
git commit -m "feat(p4): complete api, pipeline orchestrator, and physical invariants"

# 5. Connect to your remote repository (replace with your GitHub / GitLab URL)
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 6. Push code to remote
git push -u origin main
```
