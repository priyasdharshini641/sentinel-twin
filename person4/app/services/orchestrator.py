from app.services.benchmark import benchmark_service
from app.services.causal_graph import causal_graph_service
from app.services.self_healing import self_healing_service
from app.services.forensics import forensic_service
"""
SENTINEL TWIN — P4 Core Integration Orchestrator
Role: P4 (System Pipeline & Integration Engineer)

Responsibilities:
1. Orchestrates the 4-phase cyber-physical pipeline:
   P1 (Ground Truth) -> P2 (Attack Perturbation) -> P3 (Causal Defense) -> P4 (State Aggregation)
2. Maintains thread-safe current state and a circular history buffer for live frontend charting.
3. Provides asynchronous background ticking (default 2 Hz for smooth UI dashboards).
4. Exposes clean methods for attack triggers and system resets.
"""

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.models.telemetry import (
    Telemetry, SystemMode, ThreatLevel, SystemStatusResponse,
    AttackLaunchRequest, DefenseResult, SustainabilityImpact
)
from app.services.p1_simulation import SimulationService
from app.services.p2_attack_engine import AttackEngineService
from app.services.p3_defense_engine import DefenseEngineService
from app.services.sustainability import SustainabilityService


class Orchestrator:
    """
    Central pipeline coordinator connecting P1, P2, P3, and P4.
    """

    def __init__(self, history_limit: int = 120):
        self.p1 = SimulationService()
        self.p2 = AttackEngineService()
        self.p3 = DefenseEngineService()
        self.sustainability = SustainabilityService()

        self.tick_index: int = 0
        self.tick_rate_hz: float = 2.0
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None

        # Ring buffer for telemetry trends (last 120 ticks)
        self.history: deque = deque(maxlen=history_limit)

        # Initialize baseline state immediately
        self._last_snapshot: Optional[SystemStatusResponse] = None
        self._tick(dt=0.5)

    def _determine_system_mode(self, threat: ThreatLevel) -> SystemMode:
        if self.p2.is_active:
            if threat in [ThreatLevel.ELEVATED, ThreatLevel.CRITICAL]:
                return SystemMode.DETECTED
            return SystemMode.UNDER_ATTACK
        return SystemMode.NOMINAL

    def _tick(self, dt: float):
        """Execute one complete cycle of the cyber-physical pipeline."""
        self.tick_index += 1

        # Phase 1: P1 generates pristine ground truth
        truth = self.p1.step(dt=dt)

        # Phase 2: P2 perturbs ground truth into reported stream
        reported = self.p2.apply(truth, dt=dt)

        # Phase 3: P3 verifies invariants and generates forensic deduction
        defense = self.p3.analyze(reported)

        # Phase 4: Sustainability tracks cumulative resource blast radius
        impact = self.sustainability.update(truth, reported, defense, dt=dt)

        # Phase 5: P4 aggregates into a unified immutable snapshot
        mode = self._determine_system_mode(defense.threat_level)
        snapshot = SystemStatusResponse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            system_mode=mode,
            tick_index=self.tick_index,
            ground_truth=truth.to_dict(),
            reported_telemetry=reported.to_dict(),
            attack_state=self.p2.get_attack_state(),
            defense_result=defense,
            sustainability_impact=impact
        )

        self._last_snapshot = snapshot
        # Store lightweight trend point in history
        self.history.append({
            "tick": self.tick_index,
            "timestamp": snapshot.timestamp,
            "temperature_truth": truth.temperature,
            "temperature_reported": reported.temperature,
            "cooling_load_truth": truth.cooling_load,
            "cooling_load_reported": reported.cooling_load,
            "power_truth": truth.power_consumption,
            "power_reported": reported.power_consumption,
            "water_flow_truth": truth.water_flow,
            "water_flow_reported": reported.water_flow,
            "system_trust_score": defense.system_trust_score,
            "threat_level": defense.threat_level.value,
            "is_attack_active": self.p2.is_active
        })

    async def start(self):
        """Start the background simulation loop."""
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Stop background simulation loop."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        """Continuous async simulation ticker."""
        interval = 1.0 / self.tick_rate_hz
        while self.is_running:
            try:
                self._tick(dt=interval)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue loop
                print(f"[Orchestrator Error]: {e}")
                await asyncio.sleep(interval)

    # -------------------------------------------------------------------------
    # Public Controller Actions
    # -------------------------------------------------------------------------
    def get_current_status(self) -> SystemStatusResponse:
        """Get latest unified snapshot."""
        if self._last_snapshot is None:
            self._tick(0.5)
        return self._last_snapshot

    def get_history(self, limit: int = 60) -> List[Dict[str, Any]]:
        """Return the most recent N history ticks for dashboard charting."""
        items = list(self.history)
        return items[-limit:]

    def launch_attack(self, request: AttackLaunchRequest) -> Dict[str, Any]:
        """Trigger an attack through P2."""
        result = self.p2.launch_attack(request)
        # Advance a tick immediately to reflect the attack state in current status
        self._tick(dt=0.1)
        return result

    def stop_attack(self) -> Dict[str, Any]:
        """Stop running attack through P2."""
        result = self.p2.stop_attack()
        self._tick(dt=0.1)
        return result

    def reset_system(self) -> Dict[str, Any]:
        """Reset all plant simulation, red team, and sustainability metrics."""
        self.p1.reset()
        self.p2.reset()
        self.sustainability.reset()
        self.history.clear()
        self.tick_index = 0
        self._tick(dt=0.1)
        return {
            "status": "SYSTEM_RESET",
            "message": "Physical digital twin, red team vectors, and sustainability meters reset to nominal."
        }



    def launch_custom_attack(self, request) -> Dict[str, Any]:
        result = self.p2.launch_custom_attack(request)
        self._tick(dt=0.1)
        return result

    def get_benchmark_comparison(self) -> Dict[str, Any]:
        status = self.get_current_status()
        truth = self.p1.step(dt=0.0)
        reported = self.p2.apply(truth, dt=0.0)
        return benchmark_service.evaluate(reported, status.defense_result, self.p2.is_active)

    def get_causal_graph(self) -> Dict[str, Any]:
        status = self.get_current_status()
        truth = self.p1.step(dt=0.0)
        reported = self.p2.apply(truth, dt=0.0)
        return causal_graph_service.get_graph_topology(reported, status.defense_result)

    def get_forensic_dossier(self) -> Dict[str, Any]:
        status = self.get_current_status()
        truth = self.p1.step(dt=0.0)
        reported = self.p2.apply(truth, dt=0.0)
        return forensic_service.generate_dossier(
            reported, status.defense_result, status.sustainability_impact, self.p2.get_attack_state()
        )

    def activate_safe_mode(self) -> Dict[str, Any]:
        return self_healing_service.activate_safe_mode()

    def get_healed_stream(self) -> Dict[str, Any]:
        status = self.get_current_status()
        truth = self.p1.step(dt=0.0)
        reported = self.p2.apply(truth, dt=0.0)
        return self_healing_service.generate_reconstructed_stream(reported, status.defense_result)


# Global singleton instance for FastAPI injection
orchestrator = Orchestrator()
