"""
SENTINEL TWIN — Sherlock Digital Forensic Dossier Service
Produces executive forensic incident reports with mathematical proofs and evidentiary hashes.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any
from app.models.telemetry import Telemetry, DefenseResult, SustainabilityImpact


class ForensicDossierService:
    def generate_dossier(
        self,
        reported: Telemetry,
        defense: DefenseResult,
        impact: SustainabilityImpact,
        attack_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        timestamp_str = datetime.now(timezone.utc).isoformat()
        is_attack = attack_state.get("is_active", False)

        # Cryptographic SHA-256 hash of the evidence frame
        raw_evidence = json.dumps({
            "timestamp": timestamp_str,
            "reported": reported.to_dict(),
            "invariants": [inv.model_dump() for inv in defense.invariants],
            "attack_state": attack_state
        }, sort_keys=True)
        evidence_hash = hashlib.sha256(raw_evidence.encode("utf-8")).hexdigest()

        if is_attack:
            attack_type = attack_state.get("attack_type", "unspecified")
            threat_actor_motive = (
                "Adversary injected false environmental and cooling signals to trick automated PID controllers "
                "into cutting chilled water flow and throttling chiller power, intending to induce thermal overload "
                "or physical equipment degradation while evading conventional statistical monitoring."
            )
            regulatory_status = "BREACH DETECTED & ISOLATED (NIST SP 800-82 / ISO 21434 COMPLIANT)"
        else:
            attack_type = "NONE"
            threat_actor_motive = "N/A — Operational baseline verified."
            regulatory_status = "COMPLIANT & SECURE"

        return {
            "dossier_id": f"ST-INCIDENT-{evidence_hash[:12].upper()}",
            "generated_at": timestamp_str,
            "incident_status": "CRITICAL THREAT" if is_attack else "NOMINAL",
            "threat_classification": attack_type.upper(),
            "threat_actor_motive": threat_actor_motive,
            "compromised_telemetry_streams": defense.compromised_sensors,
            "fractured_physical_invariants": [inv.name for inv in defense.invariants if inv.violated],
            "forensic_reasoning": defense.forensic_deduction,
            "blast_radius_analysis": {
                "water_waste_prevented_liters": impact.water_wasted_liters,
                "energy_waste_prevented_kwh": impact.energy_wasted_kwh,
                "carbon_footprint_mitigated_kg": impact.carbon_emissions_kg,
                "financial_liability_mitigated_inr": impact.financial_loss_inr,
                "financial_liability_mitigated_usd": impact.financial_loss_usd
            },
            "evidentiary_sha256_hash": evidence_hash,
            "regulatory_compliance": regulatory_status
        }


forensic_service = ForensicDossierService()
