from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from backend.models.telemetry import Telemetry


class BaseAttack(ABC):
    """Abstract Base Class for P2 Attack Engine.

    Flow:
        GROUND TRUTH TELEMETRY -> P2 ATTACK ENGINE -> REPORTED TELEMETRY

    CRITICAL GUARDRAILS:
    1. NEVER MODIFY GROUND TRUTH:
       `apply(ground_truth)` must leave the input object 100% unchanged.
       Inactive apply() must return an independent copy and never the same object reference.
    2. GROUND TRUTH IS SACRED:
       Fields not targeted by the attack must remain identical in reported telemetry.
    3. P2 MUST NOT DETECT ITS OWN ATTACK:
       No anomaly detection, consistency checks, or risk scoring.
    4. DO NOT CHEAT:
       No P3 detection simulation or defensive workarounds.
    5. KEEP ATTACK METADATA SEPARATE:
       Attack configuration/state is isolated inside the attack instance and
       must NEVER be attached or injected into Telemetry objects.
    6. SCHEMA SYMMETRY:
       Takes Telemetry, returns Telemetry.
    7. NO RANDOM COMPLEXITY:
       Simple, deterministic, testable simulation.
    """

    def __init__(
        self,
        name: str,
        target_field: Optional[str] = None,
        intensity: float = 0.0,
        active: bool = True,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.target_field = target_field
        self.intensity = intensity
        self.active = active
        self.params = kwargs

    def get_metadata(self) -> Dict[str, Any]:
        """Returns internal attack configuration and execution metadata.

        Guaranteed separate from the Telemetry schema.
        """
        return {
            "name": self.name,
            "target_field": self.target_field,
            "intensity": self.intensity,
            "active": self.active,
            "params": dict(self.params),
        }

    def apply(self, telemetry: Telemetry) -> Telemetry:
        """Applies attack transformation to incoming telemetry.

        Enforces input type, respects active flag, and guarantees
        Telemetry -> Telemetry contract symmetry.
        When inactive, returns a NEW unchanged copy of input telemetry.
        """
        if not isinstance(telemetry, Telemetry):
            raise TypeError(
                f"Expected Telemetry instance, got {type(telemetry).__name__}"
            )

        if not self.active:
            # Inactive: return an independent unchanged copy of telemetry
            return telemetry.copy_with()

        reported = self._apply_attack(telemetry)

        if not isinstance(reported, Telemetry):
            raise TypeError(
                f"Attack '{self.name}' must return a Telemetry instance, got {type(reported).__name__}"
            )

        return reported

    @abstractmethod
    def _apply_attack(self, ground_truth: Telemetry) -> Telemetry:
        """Concrete attack logic implemented by subclasses.

        Must produce and return a new Telemetry instance.
        Must NEVER mutate ground_truth.
        """
        pass
