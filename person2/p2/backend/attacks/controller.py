from typing import Any, Dict, Optional, Type
from backend.models.telemetry import Telemetry
from backend.attacks.base_attack import BaseAttack
from backend.attacks.false_injection import FalseInjection
from backend.attacks.gradual_drift import GradualDrift
from backend.attacks.pump_flow_attack import PumpFlowAttack
from backend.attacks.coordinated_attack import CoordinatedAttack

SUPPORTED_ATTACKS: Dict[str, Type[BaseAttack]] = {
    "FALSE_INJECTION": FalseInjection,
    "GRADUAL_DRIFT": GradualDrift,
    "PUMP_FLOW_ATTACK": PumpFlowAttack,
    "COORDINATED_ATTACK": CoordinatedAttack,
}

ATTACK_TYPE_ALIASES: Dict[str, str] = {
    "FALSE_INJECTION": "FALSE_INJECTION",
    "FALSEDATAINJECTION": "FALSE_INJECTION",
    "GRADUAL_DRIFT": "GRADUAL_DRIFT",
    "GRADUALDRIFT": "GRADUAL_DRIFT",
    "DRIFT": "GRADUAL_DRIFT",
    "PUMP_FLOW_ATTACK": "PUMP_FLOW_ATTACK",
    "PUMP_FLOW": "PUMP_FLOW_ATTACK",
    "PUMPFLOW": "PUMP_FLOW_ATTACK",
    "COORDINATED_ATTACK": "COORDINATED_ATTACK",
    "COORDINATED": "COORDINATED_ATTACK",
}


class AttackController:
    """P2 Attack Engine Controller.

    Provides a unified interface for configuring, activating, resetting,
    and executing attacks against telemetry streams.

    Flow:
        GROUND TRUTH TELEMETRY -> AttackController.apply() -> REPORTED TELEMETRY

    CRITICAL GUARDRAILS:
    1. NEVER MODIFY GROUND TRUTH: Original Telemetry object remains sacred.
    2. INACTIVE GUARANTEE: Inactive state returns an unchanged copy of ground_truth.
    3. STRICT SEPARATION: Attack metadata stays inside controller/attack state;
       never injected into Telemetry.
    4. NO DEFENSE LOGIC: Does not calculate anomaly scores, trust, risk, or causal checks.
    5. INDEPENDENT FROM P3: Operates purely as a Red Team simulation module.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.active: bool = False
        self.current_attack: Optional[BaseAttack] = None
        self._raw_config: Dict[str, Any] = {}

        if config is not None:
            self.configure(config)

    def configure(self, config: Dict[str, Any]) -> None:
        """Configures the controller and instantiates the selected attack."""
        if not isinstance(config, dict):
            raise TypeError(f"Config must be a dictionary, got {type(config).__name__}")

        self._raw_config = dict(config)
        raw_type = config.get("type") or config.get("attack_type")
        self.active = bool(config.get("active", True))

        if not raw_type:
            if self.active:
                raise ValueError(
                    "Attack configuration must specify an attack 'type' when active=True."
                )
            self.current_attack = None
            return

        normalized_type = str(raw_type).strip().upper()
        canonical_type = ATTACK_TYPE_ALIASES.get(normalized_type)

        if canonical_type is None or canonical_type not in SUPPORTED_ATTACKS:
            supported = sorted(SUPPORTED_ATTACKS.keys())
            raise ValueError(
                f"Invalid attack type '{raw_type}'. Supported attack types: {supported}"
            )

        attack_cls = SUPPORTED_ATTACKS[canonical_type]

        # Extract attack kwargs excluding controller-level meta keys
        reserved_keys = {"type", "attack_type", "active"}
        attack_kwargs = {k: v for k, v in config.items() if k not in reserved_keys}
        attack_kwargs["active"] = self.active

        self.current_attack = attack_cls(**attack_kwargs)

    def apply(self, ground_truth: Telemetry) -> Telemetry:
        """Executes the active attack against ground truth telemetry.

        Returns:
            A new Telemetry instance representing reported telemetry.
            When inactive, returns an unchanged copy of ground_truth.
        """
        if not isinstance(ground_truth, Telemetry):
            raise TypeError(
                f"Expected ground_truth of type Telemetry, got {type(ground_truth).__name__}"
            )

        if not self.active or self.current_attack is None:
            # Inactive: return an unchanged copy of ground_truth
            return ground_truth.copy_with()

        return self.current_attack.apply(ground_truth)

    def stop(self) -> None:
        """Deactivates the attack without losing current attack configuration."""
        self.active = False
        if self.current_attack is not None:
            self.current_attack.active = False

    def start(self) -> None:
        """Activates the configured attack."""
        if self.current_attack is None:
            raise RuntimeError("Cannot start AttackController: no attack has been configured.")
        self.active = True
        self.current_attack.active = True

    def reset(self) -> None:
        """Resets the internal state of the controller and any stateful attack."""
        if self.current_attack is not None and hasattr(self.current_attack, "reset"):
            self.current_attack.reset()

    def get_metadata(self) -> Dict[str, Any]:
        """Returns controller and active attack metadata.

        Guaranteed separate from the Telemetry schema.
        """
        return {
            "active": self.active,
            "attack_type": self.current_attack.name if self.current_attack else None,
            "attack_metadata": (
                self.current_attack.get_metadata() if self.current_attack else None
            ),
        }
