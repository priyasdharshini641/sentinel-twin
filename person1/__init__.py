"""SENTINEL TWIN - P1 Physical Simulation Package.

Provides realistic, physics-grounded cyber-physical telemetry
for smart climate-responsive water and HVAC infrastructure.
"""

from .models import Telemetry
from .simulator import PlantSimulator

__all__ = ["Telemetry", "PlantSimulator"]
