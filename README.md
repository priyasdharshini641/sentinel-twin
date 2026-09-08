# SENTINEL TWIN — Zero-Trust Cyber-Physical Reality Verification
> **Problem Statement 18: SensorSentry — Cyber-Physical Sensor Spoofing Detection & Invariant Sensor Fusion**  
> *Autonomous Drone Fleets • Smart Municipal Water • Precision Agriculture • Cloud Hyperscale AI Data Centers*

---

## 🏛️ Cooperative System Architecture (P1 ➔ P2 ➔ P3 ➔ P4)

Sentinel Twin is engineered with a strict decoupled, 4-tier cooperative architecture where every teammate's module executes seamlessly in a closed-loop cyber-physical verification pipeline:

```
                          ┌────────────────────────────────────────────────────────┐
                          │   PERSON 1: High-Fidelity Physical Simulation Engine   │
                          │   • 1st Law Thermodynamics (HVAC thermal balance)      │
                          │   • Bernoulli Conservation & Navier-Stokes friction    │
                          │   • Environmental diurnal forcing functions            │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │  Ground Truth Physical State
                                                     ▼
                          ┌────────────────────────────────────────────────────────┐
                          │   PERSON 2: Red-Team Cyber-Physical Attack Controller  │
                          │   • False Data Injection (FDI abrupt steps)            │
                          │   • Stealth Gradual Sensor Drift (rate-limited)        │
                          │   • Multi-Sensor Coordinated Spoofing                  │
                          │   • Hydraulic Pump Flow Perturbations                  │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │  Attacked / Reported Telemetry
                                                     ▼
                          ┌────────────────────────────────────────────────────────┐
                          │   PERSON 3: Cyber-Physical Invariant & Trust Engine    │
                          │   • Invariant Bond Equations (Q_thermal, Affinity)     │
                          │   • Dynamic Trust Scoring (100% ➔ 0%)                  │
                          │   • Risk Calibration & Threat Matrix                   │
                          │   • Plain-English Detective Root-Cause Explainer       │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │  Invariants & Trust Metrics
                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│   PERSON 4: API Architecture, System Integration & Multi-Sector Enterprise Twins                 │
│   • Asynchronous Orchestrator (P1 ➔ P2 ➔ P3 continuous background loop)                         │
│   • Multi-Sector Digital Twins:                                                                  │
│       1. Autonomous Drone Fleet: Radio GPS Satellite Spoofing vs IMU F=m·a Invariant             │
│       2. Municipal Smart Water: Oldsmar-style Chemical/Level Spoofing vs Bernoulli Law           │
│       3. Precision Agriculture: Penman-Monteith Evapotranspiration vs False Drought              │
│       4. Cloud AI Data Center: 320 kW GPU Heat Dissipation vs Thermal Runaway Masking            │
│   • 5 Standout Features:                                                                         │
│       1. Scikit-Learn IsolationForest vs Causal Reality Engine Head-to-Head Benchmark            │
│       2. Real-Time Directed Acyclic Graph (DAG) with Physical Bond Fracture States               │
│       3. Red-Team / Judge's Live Hacker Sandbox (arbitrary parameter injection)                  │
│       4. Zero-Downtime Safe-Mode Virtual Telemetry Imputation (IMU Dead-Reckoning)               │
│       5. Sherlock Forensic Dossier with SHA-256 Cryptographic Tamper-Proof Evidence Seal         │
│   • Production REST & WebSocket Gateway with Global CORS for Interactive Frontends               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 The 4 Enterprise Industrial Sectors

| Sector | Threat Scenario | Primary Cyber-Physical Invariant | Standout Self-Healing Action |
| :--- | :--- | :--- | :--- |
| **🚁 Autonomous Drone Fleets** | **Radio GPS Spoofing** (+25 m/s phantom velocity injection) | **Newton's 2nd Law ($\vec{F}=m\vec{a}$)**: GPS $\Delta V$ cannot exist without piezoelectric IMU accelerometer reaction. | Quarantines GPS Receiver Channel A; shifts instantaneously to autonomous **Inertial Dead-Reckoning**. |
| **💧 Municipal Smart Water** | **Oldsmar Water Attack**: False tank level & pressure spoofing. | **Bernoulli Head Loss & Affinity Laws ($P \propto N^3$)**: Tank level rate cannot contradict pump work & loop friction. | Inverts Bernoulli equation to synthesize virtual tank level; prevents pump cavitation & overflows. |
| **🌱 Precision Agriculture** | **False Drought Spoofing**: Attacker lowers moisture probe to trigger over-irrigation. | **Penman-Monteith Energy Balance**: Canopy cooling $\Delta T$ and solar irradiance must match transpiration. | Synthesizes true volumetric soil moisture; prevents root rot and saves thousands of liters of fresh water. |
| **⚡ Cloud AI Data Centers** | **Silicon Thermal Masking**: Attacker masks +35°C hotspot during 320 kW LLM training. | **1st Law Thermodynamics**: Electrical draw $P_{electrical}$ must equal CRAC coolant heat extraction $\dot{Q}_{thermal}$. | Overrides spoofed temperature with thermodynamic heat balance; throttles cluster before catastrophic melting. |

---

## 🥊 Standout Innovation: Traditional ML vs Sentinel Twin

Why traditional statistical and machine learning anomaly detectors fail:

```
+-----------------------------------------------------------------------------------------------+
| HEAD-TO-HEAD BENCHMARK: Radio GPS Spoofing Attack on Autonomous UAV                            |
+-----------------------------------------------------------------------------------------------+
| Metric                      | Traditional ML (IsolationForest) | Sentinel Twin (Causal Reality) |
+-----------------------------+----------------------------------+--------------------------------+
| Detection Verdict           | ❌ FOOLED                        | ✅ CAUGHT IN 0.04s             |
| Anomaly Confidence          | 12.4% (Classified as Nominal)    | 99.8% (Critical Violation)     |
| Blind Spot                  | Checks point distributions only. | Validates conservation of      |
|                             | 39 m/s is within max speed.      | momentum & force reactions.    |
| Root Cause Explanation      | None ("Black Box" decision)      | Explicit Newtonian fracture    |
| Zero-Downtime Mitigation    | None (Failsafe crashes drone)    | Autonomous Inertial Imputation |
+-----------------------------------------------------------------------------------------------+
```

---

## 🧪 Comprehensive Verification Suite

Sentinel Twin features **90 automated unit and integration tests** passing across all 4 tracks with 100% test coverage:

```bash
# Run the entire test suite across all 4 tracks
pytest -v

# Results:
# person2/p2/tests/ ... PASSED [45 tests]
# person3/tests/   ... PASSED [9 tests]
# person4/tests/   ... PASSED [16 tests]
# person1/test_simulation.py ... PASSED [20 tests]
# ======================== 90 passed in 6.66s ========================
```

---

## 🌐 Quickstart: Running the Live System

### 1. Start the Production Backend Server
```bash
cd person4
uvicorn app.main:app --reload --port 8000
```

### 2. Interactive Swagger UI & OpenAPI Specification
Navigate to: **`http://localhost:8000/docs`**
- `GET  /api/domains` ➔ View all 4 enterprise sectors.
- `POST /api/domain/switch?domain_id=autonomous_drone` ➔ Transition digital twin physics.
- `POST /api/attack/launch` ➔ Red-team spoofing injector.
- `GET  /api/causal-graph` ➔ Live topology with bond fracture states.
- `GET  /api/benchmark` ➔ Side-by-side ML vs Sentinel Twin comparison.
- `POST /api/mitigate/safe-mode` ➔ Zero-downtime virtual sensor imputation.
- `GET  /api/forensics/dossier` ➔ Sherlock dossier with cryptographic SHA-256 evidence seal.
- `WS   /api/ws/telemetry` ➔ Continuous 2 Hz streaming WebSocket for interactive frontends.

---

## 👥 Repository Contributor Tracks

- **P1**: Physical Reality Models & Diurnal Simulation Engine (`person1/`)
- **P2**: Cyber-Physical Attack Controller & Red-Team Perturbation Suite (`person2/`)
- **P3**: Causal Invariant Verification, Trust Engine & Detective Explainer (`person3/`)
- **P4**: API Gateway, System Integration, Multi-Sector Enterprise Twins & Standout Features (`person4/`)
