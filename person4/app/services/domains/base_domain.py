"""
Base Digital Twin Domain Interface
Each enterprise domain implements physical simulation, attack perturbations,
invariant verification, and virtual sensor self-healing.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseDigitalTwinDomain(ABC):
    domain_id: str
    domain_name: str
    sector_category: str
    enterprise_client_examples: List[str]
    real_world_threat: str
    visualization_type: str

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def step_truth(self, dt: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def apply_attack(self, truth: Dict[str, Any], dt: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def evaluate_invariants(self, reported: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_causal_graph(self, reported: Dict[str, Any], defense: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def evaluate_benchmark(self, reported: Dict[str, Any], defense: Dict[str, Any], is_attack: bool) -> Dict[str, Any]:
        pass

    @abstractmethod
    def self_heal(self, reported: Dict[str, Any], defense: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_forensic_dossier(self, reported: Dict[str, Any], defense: Dict[str, Any], impact: Any, attack_state: Dict[str, Any]) -> Dict[str, Any]:
        pass
