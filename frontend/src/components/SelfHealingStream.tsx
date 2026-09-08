import React from "react";
import { ShieldCheck, Activity, DollarSign, Leaf, Zap, Droplets } from "lucide-react";
import { SystemStatus } from "../services/api";

interface SelfHealingStreamProps {
  status: SystemStatus | null;
  activeDomain: string;
}

export const SelfHealingStream: React.FC<SelfHealingStreamProps> = ({
  status,
  activeDomain,
}) => {
  const isAttacked = status?.attack_state?.is_active || status?.system_mode === "UNDER_ATTACK" || status?.system_mode === "DETECTED";
  const isHealing = status?.system_mode === "HEALING";

  // Telemetry attributes based on active domain
  const telem = status?.reported_telemetry || {};
  const truth = status?.ground_truth || {};

  return (
    <div className="rounded-2xl glass-panel p-6 border border-white/[0.08] transition-all duration-300">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-white/[0.08] gap-4">
        <div>
          <span className="text-[10px] tracking-widest text-white/50 font-mono uppercase">
            PHYSICAL TELEMETRY STREAM & ESG AUDIT
          </span>
          <h3 className="text-xl font-normal text-white tracking-tight">
            Zero-Downtime Virtual Sensor Imputation
          </h3>
        </div>

        {/* Plant Continuity Badge */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>100% OPERATIONAL CONTINUITY</span>
        </div>
      </div>

      {/* 3-Column Reality Comparison Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 font-mono text-xs">
        {/* Column 1: Attacker's Fabricated Lie */}
        <div className="p-4 rounded-xl bg-red-950/15 border border-red-500/20 space-y-2">
          <span className="text-red-400 font-semibold text-[11px] block">
            1. ATTACKER'S REPORTED SIGNAL
          </span>
          <div className="space-y-1.5 text-white/80 text-[11px]">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">GPS Speed:</span>
                  <span className="text-red-400 font-bold">{isAttacked ? "39.6 m/s" : "14.5 m/s"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">GPS Altitude:</span>
                  <span className="text-red-400">{isAttacked ? "102.1 m" : "120.0 m"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Signal Integrity:</span>
                  <span className="text-red-400">{isAttacked ? "MEACONING SPOOF" : "NOMINAL"}</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Reported Sensor:</span>
                  <span className="text-red-400 font-bold">{isAttacked ? "+45% SKEW" : "NOMINAL"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Channel Health:</span>
                  <span className="text-red-400">{isAttacked ? "COMPROMISED" : "HEALTHY"}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Column 2: Ground Truth Reality */}
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.08] space-y-2">
          <span className="text-white/60 font-semibold text-[11px] block">
            2. PHYSICAL GROUND TRUTH
          </span>
          <div className="space-y-1.5 text-white/80 text-[11px]">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">IMU Accel:</span>
                  <span className="text-white">0.04 m/s²</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Baro Altitude:</span>
                  <span className="text-white">120.0 m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Rotor RPM:</span>
                  <span className="text-white">6,810 RPM</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Internal State:</span>
                  <span className="text-white">NOMINAL STABLE</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Physics Law:</span>
                  <span className="text-white">CONSERVED</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Column 3: Sentinel Twin Inverted Self-Healing */}
        <div className="p-4 rounded-xl bg-emerald-950/15 border border-emerald-500/25 space-y-2">
          <span className="text-emerald-400 font-semibold text-[11px] block">
            3. RECONSTRUCTED VIRTUAL SENSOR
          </span>
          <div className="space-y-1.5 text-white/80 text-[11px]">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Dead-Reckoning:</span>
                  <span className="text-emerald-400 font-bold">14.50 m/s (CLEAN)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Spoofed GPS:</span>
                  <span className="text-emerald-400 font-semibold">QUARANTINED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Flight Safety:</span>
                  <span className="text-emerald-300">100% COLLISION AVOIDED</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Virtual Imputation:</span>
                  <span className="text-emerald-400 font-bold">ACTIVE (0ms DOWNTIME)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Controller Shield:</span>
                  <span className="text-emerald-400 font-semibold">INSULATED</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Sustainability ESG Ticker Strip */}
      <div className="mt-4 pt-4 border-t border-white/[0.08] grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
        <div className="p-3 rounded-lg bg-black/40 border border-white/5 flex items-center space-x-3">
          <Droplets className="w-4 h-4 text-cyan-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">WATER SAVED</span>
            <span className="text-white font-bold">1,420 L</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-black/40 border border-white/5 flex items-center space-x-3">
          <Zap className="w-4 h-4 text-amber-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">ENERGY SAVED</span>
            <span className="text-white font-bold">48.5 kWh</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-black/40 border border-white/5 flex items-center space-x-3">
          <Leaf className="w-4 h-4 text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">CARBON AVOIDED</span>
            <span className="text-white font-bold">39.7 kg CO₂</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-black/40 border border-white/5 flex items-center space-x-3">
          <DollarSign className="w-4 h-4 text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">DAMAGES AVERTED</span>
            <span className="text-emerald-400 font-bold">₹ 142,500</span>
          </div>
        </div>
      </div>
    </div>
  );
};
