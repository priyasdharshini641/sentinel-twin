"""
SENTINEL TWIN — Multi-Sector Domain Manager
Coordinates switching between the 4 Enterprise Digital Twin Domains:
1. autonomous_drone : Drone GPS Spoofing & Inertial Fusion (PS 18 Core)
2. smart_water      : Municipal Water Grid & Bernoulli Hydraulics
3. precision_agri   : Precision Agriculture & Evapotranspiration
4. datacenter_gpu   : Cloud Hyperscale AI Data Center & Silicon Thermodynamics
"""

from typing import Dict, Any, List
from app.services.domains.drone_domain import drone_domain
from app.services.domains.agri_domain import agri_domain
from app.services.domains.datacenter_domain import datacenter_domain


class DomainManager:
    def __init__(self):
        self.active_domain_id = "smart_water"  # Default domain (our frozen 11-field infrastructure)

    def list_available_domains(self) -> List[Dict[str, Any]]:
        return [
            {
                "domain_id": "autonomous_drone",
                "title": "Autonomous Drone Fleet & GPS Navigation",
                "icon": "Plane",
                "sector": "Aerospace & Autonomous Robotics",
                "core_physics_law": "Newtonian Kinematic Coupling (F = m·a)",
                "threat_scenario": "RF Satellite GPS Spoofing & Trajectory Hijacking",
                "enterprise_clients": ["Wing Delivery", "Amazon Prime Air", "Skydio UAV", "Joby Air Taxi"],
                "visualization_type": "3d_drone_flight_cockpit"
            },
            {
                "domain_id": "smart_water",
                "title": "Smart Municipal Water & Climate Infrastructure",
                "icon": "Droplets",
                "sector": "Municipal Utilities & Smart Infrastructure",
                "core_physics_law": "Bernoulli Hydraulic Conservation & First Law Thermodynamics",
                "threat_scenario": "Oldsmar Water Attack / Pump Cavitation / Coordinated Spoofing",
                "enterprise_clients": ["American Water", "Veolia", "Municipal Water Grids"],
                "visualization_type": "3d_water_pumping_facility"
            },
            {
                "domain_id": "precision_agri",
                "title": "Climate-Responsive Precision Agriculture",
                "icon": "Sprout",
                "sector": "AgTech & Food Supply Security",
                "core_physics_law": "Penman-Monteith Evapotranspiration Energy Balance",
                "threat_scenario": "Soil Moisture Probe Tampering / False Drought Induced Root Rot",
                "enterprise_clients": ["John Deere Autonomous Pivots", "Bayer Crop Science"],
                "visualization_type": "3d_smart_agri_pivot_field"
            },
            {
                "domain_id": "datacenter_gpu",
                "title": "Cloud Hyperscale AI Data Center & GPU Cluster",
                "icon": "Server",
                "sector": "Cloud Infrastructure & High-Performance Computing",
                "core_physics_law": "First Law Silicon Heat Dissipation (Q_thermal == P_electrical)",
                "threat_scenario": "AI GPU Thermal Masking / Induced Silicon Thermal Runaway",
                "enterprise_clients": ["AWS Hyperscale", "Microsoft Azure AI", "Equinix", "NVIDIA SuperPOD"],
                "visualization_type": "3d_ai_server_rack_thermal"
            }
        ]

    def set_active_domain(self, domain_id: str) -> Dict[str, Any]:
        valid_ids = ["autonomous_drone", "smart_water", "precision_agri", "datacenter_gpu"]
        if domain_id not in valid_ids:
            raise ValueError(f"Unknown domain '{domain_id}'. Valid domains: {valid_ids}")
        self.active_domain_id = domain_id
        return {
            "status": "DOMAIN_SWITCHED",
            "active_domain": domain_id,
            "message": f"Digital Twin successfully transitioned to '{domain_id}'."
        }

    def get_domain_service(self, domain_id: str = None):
        target = domain_id or self.active_domain_id
        if target == "autonomous_drone":
            return drone_domain
        elif target == "precision_agri":
            return agri_domain
        elif target == "datacenter_gpu":
            return datacenter_domain
        return None  # None defaults to our core orchestrator (smart_water)


domain_manager = DomainManager()
