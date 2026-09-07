# Sentinel Twin — Person 3 (P3) Defense / Causal Reality Engine

**Author / Maintainer:** Varshaa (`lvarshaa4@gmail.com`)  
**Component:** P3 — Causal Reality & Cyber-Physical Truth Verification

---

## 1. Overview & Architecture

The **P3 Defense Engine** is an intelligent, zero-trust cyber-physical verification layer. It receives strictly reported telemetry streams (from P2 Attack Perturbation or raw sensors) and determines physical truth solely through immutable physical conservation laws, dynamic sensor trust scoring, and detective causal forensics.

```
Reported Telemetry (11 fields)
             ↓
       CausalEngine
   [4 Physical Invariants]
             ↓
     Violated Invariants
             ↓
        TrustEngine
 [Sensor Trust (0-100) & Risk]
             ↓
     DetectiveExplainer
 [Forensic Deduc. & Recommendations]
             ↓
     DefensePipeline
  [Structured Defense Result]
```

### Strict Security Boundary
- P3 operates **exclusively** on reported telemetry.
- P3 **never** receives or inspects ground truth, attack types, attack intensity, attack metadata, or adversary labels.

---

## 2. Core Physical Invariants (`CausalEngine`)

1. **`THERMODYNAMIC_BALANCE`**:
   - First Law of Thermodynamics / Conservation of Energy.
   - Relational coupling between solar radiation, ambient temperature, humidity, cooling load, and electrical power consumption.
   - Coefficient of Performance (COP) bounds checking.

2. **`ACTUATOR_ENERGY_COUPLING`**:
   - Pump actuator operational consistency.
   - Hydraulic delivery (`water_flow`, `pressure`) coupled with pump status, speed, and electrical power consumption.

3. **`TEMPORAL_CONTINUITY`**:
   - Rolling 5-reading historical window.
   - Robust median and Median Absolute Deviation (MAD) scale estimation.
   - Sudden jump ($Z$-score) and persistent directional drift detection.

4. **`SENSOR_CROSS_CONSISTENCY`**:
   - Multi-sensor consensus across three subsystem groups:
     1. Pump State Consensus (`pump_status`, `pump_speed`, `water_flow`, `pressure`)
     2. Thermal State Consensus (`temperature`, `solar_radiation`, `cooling_load`, `power_consumption`)
     3. Water System Consensus (`water_flow`, `tank_level`, `pressure`)

---

## 3. Dynamic Trust Engine (`TrustEngine`)

- Tracks individual trust scores for **10 physical sensors** strictly clamped between `[0.0, 100.0]` (defaults to `100.0`).
- **Targeted Penalties**: Applies penalties only to sensors causally implicated by detected invariant violations.
- **Gradual Recovery**: Nominal readings trigger incremental recovery (`+2.0` per step).
- **System Trust Score**: Weighted aggregation representing overall telemetry confidence (`0.0–100.0`).
- **Bounded Risk Levels**:
  - `76.0 – 100.0`: **LOW**
  - `51.0 – 75.0`: **MEDIUM**
  - `26.0 – 50.0`: **HIGH**
  - `0.0 – 25.0`: **CRITICAL**

---

## 4. Detective Explainer (`DetectiveExplainer`)

- Deterministic, non-destructive forensic deduction.
- Generates plain-English diagnostic explanations and actionable operational recommendations without speculating on attacker identities or assuming ground truth.

---

## 5. Output Contract

```json
{
  "anomaly_detected": false,
  "violated_invariants": [],
  "sensor_trust_scores": {
    "temperature": 100.0,
    "humidity": 100.0,
    "solar_radiation": 100.0,
    "cooling_load": 100.0,
    "power_consumption": 100.0,
    "water_flow": 100.0,
    "tank_level": 100.0,
    "pump_status": 100.0,
    "pump_speed": 100.0,
    "pressure": 100.0
  },
  "system_trust_score": 100.0,
  "risk_level": "LOW",
  "explanation": "Nominal operational telemetry. All reported physical relationships conform to expected baseline invariants.",
  "recommended_action": "Maintain nominal supervisory monitoring. No manual or automated defensive intervention required."
}
```

---

## 6. Quick Start & Usage

```python
from person3 import DefensePipeline

pipeline = DefensePipeline()

# Evaluate telemetry dictionary or object
result = pipeline.evaluate(telemetry)

print(result["anomaly_detected"])
print(result["system_trust_score"])
print(result["risk_level"])
print(result["explanation"])
```
