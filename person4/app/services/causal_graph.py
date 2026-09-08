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

        # Extract invariant check results
        inv_map = {inv.invariant_id: inv for inv in defense.invariants}

        edges = [
            {
                "id": "edge_thermodynamics",
                "source": ["solar_radiation", "temperature"],
                "target": "cooling_load",
                "name": "Thermodynamic Thermal Balance",
                "equation": "Q = UA·(Tamb - Tset) + α·Solar",
                "law": "First Law of Thermodynamics",
                "violated": inv_map.get("INV_01_THERMODYNAMICS", {}).violated if "INV_01_THERMODYNAMICS" in inv_map else False,
                "residual": inv_map.get("INV_01_THERMODYNAMICS", {}).residual if "INV_01_THERMODYNAMICS" in inv_map else 0.0,
                "threshold": inv_map.get("INV_01_THERMODYNAMICS", {}).threshold if "INV_01_THERMODYNAMICS" in inv_map else 3.5,
                "status": "FRACTURED" if inv_map.get("INV_01_THERMODYNAMICS", {}).violated else "HEALTHY"
            },
            {
                "id": "edge_psychrometrics",
                "source": ["temperature"],
                "target": "humidity",
                "name": "Psychrometric Vapor Correlation",
                "equation": "es(T) = 0.61078·exp(17.27T / (T + 237.3))",
                "law": "August-Roche-Magnus Law",
                "violated": inv_map.get("INV_02_PSYCHROMETRICS", {}).violated if "INV_02_PSYCHROMETRICS" in inv_map else False,
                "residual": inv_map.get("INV_02_PSYCHROMETRICS", {}).residual if "INV_02_PSYCHROMETRICS" in inv_map else 0.0,
                "threshold": inv_map.get("INV_02_PSYCHROMETRICS", {}).threshold if "INV_02_PSYCHROMETRICS" in inv_map else 12.0,
                "status": "FRACTURED" if inv_map.get("INV_02_PSYCHROMETRICS", {}).violated else "HEALTHY"
            },
            {
                "id": "edge_hydraulic_flow",
                "source": ["pump_speed"],
                "target": "water_flow",
                "name": "Centrifugal Flow Coupling",
                "equation": "Qflow = 2.2 · Speed",
                "law": "Centrifugal Pump Impeller Law",
                "violated": inv_map.get("INV_03_HYDRAULIC_BALANCE", {}).violated if "INV_03_HYDRAULIC_BALANCE" in inv_map else False,
                "residual": inv_map.get("INV_03_HYDRAULIC_BALANCE", {}).residual if "INV_03_HYDRAULIC_BALANCE" in inv_map else 0.0,
                "threshold": inv_map.get("INV_03_HYDRAULIC_BALANCE", {}).threshold if "INV_03_HYDRAULIC_BALANCE" in inv_map else 25.0,
                "status": "FRACTURED" if inv_map.get("INV_03_HYDRAULIC_BALANCE", {}).violated else "HEALTHY"
            },
            {
                "id": "edge_motor_affinity",
                "source": ["pump_speed", "cooling_load"],
                "target": "power_consumption",
                "name": "Actuator-Energy Coupling",
                "equation": "P = 0.78·Qchiller + 0.4 + 2.8·(Speed/100)³",
                "law": "Motor Affinity & Compressor Thermodynamics",
                "violated": inv_map.get("INV_04_MOTOR_AFFINITY", {}).violated if "INV_04_MOTOR_AFFINITY" in inv_map else False,
                "residual": inv_map.get("INV_04_MOTOR_AFFINITY", {}).residual if "INV_04_MOTOR_AFFINITY" in inv_map else 0.0,
                "threshold": inv_map.get("INV_04_MOTOR_AFFINITY", {}).threshold if "INV_04_MOTOR_AFFINITY" in inv_map else 3.0,
                "status": "FRACTURED" if inv_map.get("INV_04_MOTOR_AFFINITY", {}).violated else "HEALTHY"
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
