"""
SENTINEL TWIN — Telemetry Models & Serialization
Role: P4 (API & System Integration Engineer)
Frozen Contract: 11 Telemetry Fields
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# 1. FROZEN TEAM CONTRACT: Telemetry Dataclass
# ============================================================================
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to JSON-serializable dictionary with ISO timestamp."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


# ============================================================================
# 2. ENUMS FOR API CONTRACTS
# ============================================================================
class AttackType(str, Enum):
    FDI = "fdi"                          # False Data Injection (abrupt jump)
    DRIFT = "drift"                      # Gradual Stealth Drift
    COORDINATED = "coordinated"          # Multi-Sensor Coordinated Spoofing
    FREEZE = "freeze"                    # Sensor Freeze / Stale Value
    NOISE = "noise"                      # High-Variance Noise Injection


class SystemMode(str, Enum):
    NOMINAL = "NOMINAL"                  # Healthy, all invariants verified
    UNDER_ATTACK = "UNDER_ATTACK"        # Active spoofing attack running
    DETECTED = "DETECTED"                # Breach caught by Causal Reality Engine
    HEALING = "HEALING"                  # Sensor isolated, virtual imputation active


class ThreatLevel(str, Enum):
    LOW = "LOW"
    GUARDED = "GUARDED"
    ELEVATED = "ELEVATED"
    CRITICAL = "CRITICAL"


# ============================================================================
# 3. REQUEST / RESPONSE SCHEMAS
# ============================================================================
class AttackLaunchRequest(BaseModel):
    attack_type: AttackType = Field(
        default=AttackType.COORDINATED,
        description="Type of spoofing attack to execute"
    )
    target_sensors: List[str] = Field(
        default_factory=lambda: ["temperature", "solar_radiation", "cooling_load"],
        description="Sensor field names to compromise"
    )
    intensity: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Attack intensity / perturbation magnitude ratio (0.0 to 1.0)"
    )
    stealth: bool = Field(
        default=True,
        description="Apply adaptive rate-limiting to evade simple delta thresholds"
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Auto-terminate attack after N seconds (None = continuous until stopped)"
    )


class InvariantCheckResult(BaseModel):
    invariant_id: str = Field(..., description="e.g. INV_01_THERMODYNAMICS")
    name: str = Field(..., description="Human-readable invariant title")
    law: str = Field(..., description="Physical law governing the relationship")
    violated: bool = Field(..., description="True if invariant residual exceeded threshold")
    residual: float = Field(..., description="Calculated deviation from expected physics")
    threshold: float = Field(..., description="Maximum acceptable physical tolerance")
    description: str = Field(..., description="Forensic context on invariant check")


class DefenseResult(BaseModel):
    system_trust_score: float = Field(..., ge=0.0, le=100.0, description="Overall infrastructure trust index (0-100)")
    threat_level: ThreatLevel = Field(..., description="Current threat classification")
    sensor_trust_scores: Dict[str, float] = Field(..., description="Individual trust scores per telemetry field (0-100)")
    invariants: List[InvariantCheckResult] = Field(..., description="Physical invariant checks")
    compromised_sensors: List[str] = Field(..., description="List of sensors identified as fabricated")
    forensic_deduction: str = Field(..., description="Plain-English detective explanation of attack physics")
    healed_telemetry: Dict[str, Any] = Field(..., description="Synthesized true state via physical imputation")


class SustainabilityImpact(BaseModel):
    water_wasted_liters: float = Field(..., description="Accumulated water lost due to false control actions")
    energy_wasted_kwh: float = Field(..., description="Accumulated excess electrical energy consumed")
    carbon_emissions_kg: float = Field(..., description="Avoidable kg CO2e emissions (0.82 kg/kWh)")
    financial_loss_inr: float = Field(..., description="Estimated direct financial loss in Indian Rupees (₹)")
    financial_loss_usd: float = Field(..., description="Estimated direct financial loss in US Dollars ($)")


class SystemStatusResponse(BaseModel):
    timestamp: str = Field(..., description="ISO-8601 timestamp of snapshot")
    system_mode: SystemMode = Field(..., description="Overall system operational status")
    tick_index: int = Field(..., description="Monotonically increasing simulation tick counter")
    ground_truth: Dict[str, Any] = Field(..., description="Uncorrupted physical ground truth (P1)")
    reported_telemetry: Dict[str, Any] = Field(..., description="Potentially spoofed telemetry stream (P2)")
    attack_state: Dict[str, Any] = Field(..., description="Active attack metadata (P2)")
    defense_result: DefenseResult = Field(..., description="Causal verification & forensic deductions (P3)")
    sustainability_impact: SustainabilityImpact = Field(..., description="Sustainability blast radius impact")


class GenericResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
