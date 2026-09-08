/**
 * SENTINEL TWIN / SENTINEL SENTRY — API Service Layer
 * Interfaces directly with FastAPI backend on port 8000.
 */

const API_BASE = "http://localhost:8000/api";

export interface DomainInfo {
  domain_id: string;
  title: string;
  icon: string;
  sector: string;
  core_physics_law: string;
  threat_scenario: string;
  enterprise_clients: string[];
  visualization_type: string;
}

export interface InvariantRecord {
  id: string;
  name: string;
  law: string;
  violated: boolean;
  residual: number;
  threshold: number;
  description: string;
}

export interface DefenseResult {
  system_trust_score: number;
  threat_level: "LOW" | "GUARDED" | "ELEVATED" | "CRITICAL";
  compromised_sensors: string[];
  invariants: InvariantRecord[];
  forensic_deduction: string;
  healed_telemetry?: Record<string, any>;
}

export interface SustainabilityImpact {
  water_wasted_liters: number;
  energy_wasted_kwh: number;
  carbon_emissions_kg: number;
  financial_loss_inr: number;
  financial_loss_usd: number;
}

export interface SystemStatus {
  timestamp: string;
  active_domain: string;
  system_mode: "NOMINAL" | "UNDER_ATTACK" | "DETECTED" | "HEALING";
  tick_index?: number;
  ground_truth: Record<string, any>;
  reported_telemetry: Record<string, any>;
  defense_result: DefenseResult;
  attack_state: {
    is_active: boolean;
    active?: boolean;
    attack_type?: string;
    type?: string;
    intensity?: number;
    target_sensors?: string[];
  };
  sustainability_impact?: SustainabilityImpact;
}

export interface CausalNode {
  id: string;
  label: string;
  value: string;
  type: string;
}

export interface CausalEdge {
  id: string;
  source: string[] | string;
  target: string;
  name: string;
  equation: string;
  law: string;
  status: "HEALTHY" | "FRACTURED";
  residual?: number;
}

export interface CausalGraphResponse {
  graph_health: "PRISTINE" | "COMPROMISED";
  nodes: CausalNode[];
  edges: CausalEdge[];
}

export interface BenchmarkComparison {
  traditional_ml: {
    model_name: string;
    anomaly_detected: boolean;
    status: string;
    blind_spot: string;
    confidence?: number;
  };
  causal_reality_engine: {
    model_name: string;
    anomaly_detected: boolean;
    status: string;
    system_trust_score: number;
    detection_latency_ms?: number;
    explanation?: string;
  };
}

export interface ForensicDossier {
  dossier_id: string;
  sector: string;
  threat_classification: string;
  threat_actor_motive: string;
  forensic_proof: string;
  mitigation_action: string;
  evidentiary_sha256_hash: string;
}

export interface SafeModeResponse {
  status: string;
  domain: string;
  mitigation: {
    status: string;
    mode: string;
  };
  telemetry_stream: {
    safe_mode_active: boolean;
    navigation_mode: string;
    quarantined_sensors: string[];
    flight_safety_continuity: string;
    healed_telemetry: Record<string, any>;
  };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  return await res.json();
}

export const api = {
  async getDomains(): Promise<{ active_domain: string; available_domains: DomainInfo[] }> {
    return request("/domains");
  },

  async switchDomain(domainId: string): Promise<any> {
    return request(`/domain/switch?domain_id=${encodeURIComponent(domainId)}`, {
      method: "POST",
    });
  },

  async getSystemStatus(): Promise<SystemStatus> {
    return request("/system/status");
  },

  async getCausalGraph(): Promise<CausalGraphResponse> {
    return request("/causal-graph");
  },

  async getBenchmark(): Promise<BenchmarkComparison> {
    return request("/benchmark");
  },

  async launchAttack(attackType: string = "coordinated", targetSensors: string[] = ["gps_ground_speed"], intensity: number = 0.8): Promise<any> {
    return request("/attack/launch", {
      method: "POST",
      body: JSON.stringify({
        attack_type: attackType,
        target_sensors: targetSensors,
        intensity: Math.min(1.0, Math.max(0.0, intensity)),
        stealth: true,
      }),
    });
  },

  async stopAttack(): Promise<any> {
    return request("/attack/stop", {
      method: "POST",
    });
  },

  async activateSafeMode(): Promise<SafeModeResponse> {
    return request("/mitigate/safe-mode", {
      method: "POST",
    });
  },

  async getForensicsDossier(): Promise<ForensicDossier> {
    return request("/forensics/dossier");
  },

  async getTelemetryHistory(limit: number = 60): Promise<any[]> {
    return request(`/telemetry/history?limit=${limit}`);
  },
};
