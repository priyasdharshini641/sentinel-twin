"""
SENTINEL TWIN — Cyber-Physical Causal Graph Engine
Represents the plant as a Directed Acyclic Graph (DAG) with physical invariant edges.
Calculates real-time edge stress, residuals, and fractures.
"""

from typing import Dict, Any, List
from app.models.telemetry import Telemetry, DefenseResult


class CausalGraphService:
    def get_graph_topology(self, reported: Telemetry, defense: DefenseResult) -> Dict[str, Any]:
        """
        Builds the active cyber-physical graph with live node values and edge stresses.
        """
        nodes = [
            {"id": "solar_radiation", "label": "Solar Radiation", "value": f"{reported.solar_radiation:.0f} W/m²", "type": "environmental"},
            {"id": "temperature", "label": "Ambient Temp", "value": f"{reported.temperature:.1f} °C", "type": "environmental"},
            {"id": "humidity", "label": "Relative Humidity", "value": f"{reported.humidity:.1f} %", "type": "environmental"},
            {"id": "cooling_load", "label": "Cooling Load", "value": f"{reported.cooling_load:.1f} kW", "type": "thermal_plant"},
            {"id": "power_consumption", "label": "Power Draw", "value": f"{reported.power_consumption:.2f} kW", "type": "electrical"},
            {"id": "pump_speed", "label": "Pump Speed", "value": f"{reported.pump_speed:.1f} %", "type": "actuator"},
            {"id": "water_flow", "label": "Water Flow", "value": f"{reported.water_flow:.1f} L/min", "type": "hydraulic"},
            {"id": "pressure", "label": "Hydraulic Pressure", "value": f"{reported.pressure:.2f} bar", "type": "hydraulic"},
            {"id": "tank_level", "label": "Tank Level", "value": f"{reported.tank_level:.1f} %", "type": "storage"}
        ]

        # Extract invariant check results robustly (supporting both models and dicts)
        def find_inv(*ids: str):
            for inv in (defense.invariants or []):
                iid = getattr(inv, "invariant_id", None) or (inv.get("invariant_id") if isinstance(inv, dict) else None)
                if iid in ids:
                    return inv
            return None

        def is_violated(inv) -> bool:
            if inv is None:
                return False
            if isinstance(inv, dict):
                return bool(inv.get("violated", False))
            return bool(getattr(inv, "violated", False))

        def get_residual(inv, default: float = 0.0) -> float:
            if inv is None:
                return default
            if isinstance(inv, dict):
                return float(inv.get("residual", default))
            return float(getattr(inv, "residual", default))

        def get_threshold(inv, default: float = 1.0) -> float:
            if inv is None:
                return default
            if isinstance(inv, dict):
                return float(inv.get("threshold", default))
            return float(getattr(inv, "threshold", default))

        inv1 = find_inv("INV_01_THERMODYNAMICS", "THERMODYNAMIC_BALANCE")
        inv2 = find_inv("INV_02_PSYCHROMETRICS", "INV_03_TEMPORAL_CONTINUITY", "TEMPORAL_CONTINUITY")
        inv3 = find_inv("INV_03_HYDRAULIC_BALANCE", "INV_04_CROSS_CONSISTENCY", "SENSOR_CROSS_CONSISTENCY")
        inv4 = find_inv("INV_04_MOTOR_AFFINITY", "INV_02_ACTUATOR_COUPLING", "ACTUATOR_ENERGY_COUPLING")

        edges = [
            {
                "id": "edge_thermodynamics",
                "source": ["solar_radiation", "temperature"],
                "target": "cooling_load",
                "name": "Thermodynamic Thermal Balance",
                "equation": "Q = UA·(Tamb - Tset) + α·Solar",
                "law": "First Law of Thermodynamics",
                "violated": is_violated(inv1),
                "residual": get_residual(inv1, 0.0),
                "threshold": get_threshold(inv1, 3.5),
                "status": "FRACTURED" if is_violated(inv1) else "HEALTHY"
            },
            {
                "id": "edge_psychrometrics",
                "source": ["temperature"],
                "target": "humidity",
                "name": "Psychrometric Vapor Correlation",
                "equation": "es(T) = 0.61078·exp(17.27T / (T + 237.3))",
                "law": "August-Roche-Magnus Law",
                "violated": is_violated(inv2),
                "residual": get_residual(inv2, 0.0),
                "threshold": get_threshold(inv2, 12.0),
                "status": "FRACTURED" if is_violated(inv2) else "HEALTHY"
            },
            {
                "id": "edge_hydraulic_flow",
                "source": ["pump_speed"],
                "target": "water_flow",
                "name": "Centrifugal Flow Coupling",
                "equation": "Qflow = 2.2 · Speed",
                "law": "Centrifugal Pump Impeller Law",
                "violated": is_violated(inv3),
                "residual": get_residual(inv3, 0.0),
                "threshold": get_threshold(inv3, 25.0),
                "status": "FRACTURED" if is_violated(inv3) else "HEALTHY"
            },
            {
                "id": "edge_motor_affinity",
                "source": ["pump_speed", "cooling_load"],
                "target": "power_consumption",
                "name": "Actuator-Energy Coupling",
                "equation": "P = 0.78·Qchiller + 0.4 + 2.8·(Speed/100)³",
                "law": "Motor Affinity & Compressor Thermodynamics",
                "violated": is_violated(inv4),
                "residual": get_residual(inv4, 0.0),
                "threshold": get_threshold(inv4, 3.0),
                "status": "FRACTURED" if is_violated(inv4) else "HEALTHY"
            }
        ]


        total_bonds = len(edges)
        broken_bonds = sum(1 for e in edges if e["status"] == "FRACTURED")

        return {
            "graph_health": "COMPROMISED" if broken_bonds > 0 else "PRISTINE",
            "total_bonds": total_bonds,
            "broken_bonds": broken_bonds,
            "nodes": nodes,
            "edges": edges
        }


causal_graph_service = CausalGraphService()
