"""P3 Defense / Causal Reality Module (Person 3).

Sentinel Twin Cyber-Physical Truth Verification and Defense Engine.
"""

try:
    from person3.causal_engine import CausalEngine
    from person3.trust_engine import TrustEngine
    from person3.detective_explainer import DetectiveExplainer
    from person3.defense_pipeline import DefensePipeline
except ImportError:
    from backend.defense.causal_engine import CausalEngine
    from backend.defense.trust_engine import TrustEngine
    from backend.defense.detective_explainer import DetectiveExplainer
    from backend.defense.defense_pipeline import DefensePipeline

__all__ = [
    "CausalEngine",
    "TrustEngine",
    "DetectiveExplainer",
    "DefensePipeline",
]
