# SENTINEL TWIN — Zero-Trust Cyber-Physical Reality Verification

> **SensorSentry: Cyber-Physical Sensor Spoofing Detection & Invariant Sensor Fusion**

SENTINEL TWIN is a **cyber-physical security platform** that uses a digital twin to simulate automated infrastructure, launch sensor spoofing attacks, and verify whether the overall physical reality created by the telemetry makes sense.

Instead of only asking:

> **"Is this sensor value abnormal?"**

SENTINEL TWIN asks:

> **"Does the reality created by all these sensor values make physical sense?"**

---

## 🚀 What It Does

The platform creates a simulated physical environment, generates realistic telemetry, introduces cyberattacks such as sensor spoofing and gradual drift, and analyzes the manipulated data using **statistical, temporal, and physical invariant checks**.

### Core Pipeline

```text
Digital Twin Simulation
        ↓
Ground Truth Telemetry
        ↓
Cyberattack / Sensor Spoofing
        ↓
Manipulated Telemetry
        ↓
Anomaly + Temporal Analysis
        ↓
Causal Reality Verification
        ↓
Trust Score + Risk Level
        ↓
Explanation + Mitigation
```

The ground-truth physical state remains separate from the attacker-controlled reported telemetry, allowing the system to evaluate how cyber manipulation affects the perceived state of the infrastructure.

---

## 🏭 Supported Industrial Scenarios

SENTINEL TWIN is designed as a flexible platform that can be adapted to different cyber-physical environments.

| Sector                   | Example Threat                 | Physical Reality Check                             |
| ------------------------ | ------------------------------ | -------------------------------------------------- |
| 🚁 Autonomous Drones     | GPS spoofing                   | GPS movement vs IMU/physical motion                |
| 💧 Smart Water           | Tank level & pressure spoofing | Flow, pressure, pump and tank relationships        |
| 🌱 Precision Agriculture | False drought readings         | Moisture, temperature and environmental conditions |
| ⚡ AI Data Centers        | Thermal sensor masking         | Power consumption vs thermal behavior              |

The current prototype focuses on **simulated cyber-physical infrastructure**, allowing the same architecture to be adapted to organization-specific digital twins and telemetry later.

---

## 🛡️ Attack Simulation

The platform includes a Red-Team attack environment for testing the resilience of the digital twin.

### Supported Attacks

* **False Data Injection (FDI)** — abrupt manipulation of sensor readings.
* **Gradual Sensor Drift** — slow, stealthy manipulation designed to remain believable.
* **Coordinated Multi-Sensor Spoofing** — manipulation of multiple telemetry streams simultaneously.
* **Physical/System Perturbations** — simulated changes to infrastructure behavior.

The attacker modifies the **reported telemetry**, while the underlying ground-truth simulation remains unchanged.

---

## 🧠 Causal Reality Engine

The key innovation is the **Causal Reality Engine**.

Traditional anomaly detection primarily looks for unusual values or statistical patterns.

SENTINEL TWIN additionally checks relationships between multiple signals.

For example:

```text
Pump ON
   ↓
Flow should increase
   ↓
Energy consumption should increase
   ↓
Tank level should respond accordingly
   ↓
Pressure should remain physically consistent
```

If an attacker manipulates one or more sensors while these relationships become inconsistent, the system identifies a **physical reality violation**.

### Detection Layers

1. **Statistical Analysis**
2. **Temporal Behavior Analysis**
3. **Physical/Causal Invariant Verification**
4. **Trust & Risk Scoring**
5. **Root-Cause Explanation**

---

## 📊 Traditional ML vs Causal Verification

A major goal of the project is to demonstrate the difference between detecting an unusual **number** and detecting an impossible **system state**.

```text
Traditional Anomaly Detection
        ↓
"Does this value look unusual?"

SENTINEL TWIN
        ↓
"Do all these values make physical sense together?"
```

The platform can compare conventional anomaly detection with its causal verification approach during simulated attacks.

> Benchmark values shown in the prototype represent simulated test scenarios and should not be interpreted as real-world performance guarantees.

---

## 🔍 Security Analysis

For every detected event, the system can provide:

* Anomaly status
* Violated physical invariant
* Sensor/system trust score
* Risk level
* Attack status
* Supporting evidence
* Plain-English explanation
* Recommended mitigation

This makes the detection process easier to understand than a purely black-box anomaly score.

---

## 🛠️ Mitigation

When telemetry becomes untrusted, the system can simulate defensive responses such as:

* Sensor channel quarantine
* Virtual telemetry estimation
* Safe-mode operation
* Redundant sensor reasoning
* Physical-state reconstruction

The objective is to maintain safe operation even when one or more reported telemetry streams cannot be trusted.

---

## 🧪 Verification

The project includes automated tests covering the simulation, attack scenarios, defense logic, and system integration.

Run the test suite with:

```bash
pytest -v
```

---

## 🌐 Running the Backend

Install the required dependencies and start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API documentation is available at:

```text
http://localhost:8000/docs
```

### Example API Capabilities

```text
GET  /api/domains
POST /api/domain/switch
POST /api/attack/launch
GET  /api/causal-graph
GET  /api/benchmark
POST /api/mitigate/safe-mode
GET  /api/forensics/dossier
WS   /api/ws/telemetry
```

---

## 🏗️ Technology Stack

### Backend

* Python
* FastAPI
* NumPy
* Pandas
* Scikit-learn
* WebSockets

### Frontend

* React
* Vite
* Tailwind CSS
* Recharts

### Security & Analysis

* Statistical anomaly detection
* Temporal analysis
* Physical invariants
* Causal reasoning
* Trust scoring
* Risk analysis
* SHA-256 evidence integrity

---

## 💡 Why SENTINEL TWIN?

Modern automated infrastructure increasingly depends on sensor data to make decisions.

If an attacker can manipulate that data without being detected, an automated system may make a completely wrong decision while believing everything is normal.

SENTINEL TWIN provides a way to **attack the digital representation of infrastructure and verify whether the resulting reality is physically believable**.

> **Don't just detect bad data. Verify the reality behind the data.**

---

## 📌 Project Status

SENTINEL TWIN is a **hackathon prototype** demonstrating adversarial digital twins, cyber-physical attack simulation, invariant-based verification, and trust-aware telemetry analysis.

The architecture is designed to be extended toward organization-specific digital twins and real-world infrastructure telemetry.
