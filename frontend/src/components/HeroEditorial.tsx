import React from "react";
import { ArrowUpRight, ShieldCheck, Zap, Download } from "lucide-react";
import { SystemStatus } from "../services/api";

interface HeroEditorialProps {
  status: SystemStatus | null;
  activeDomain: string;
  onOpenAudit: () => void;
  onOpenBenchmark: () => void;
}

export const HeroEditorial: React.FC<HeroEditorialProps> = ({
  status,
  activeDomain,
  onOpenAudit,
  onOpenBenchmark,
}) => {
  const domainTitles: Record<string, { title: string; subtitle: string; client: string; invariant: string }> = {
    autonomous_drone: {
      title: "Autonomous defense drone.",
      subtitle: "RF Satellite GPS Spoofing & Trajectory Hijack Mitigation",
      client: "Wing Delivery • Amazon Prime Air • Skydio UAV",
      invariant: "Newton's Kinematic Law (F = m·a)",
    },
    smart_water: {
      title: "Smart municipal water.",
      subtitle: "Oldsmar-Style Reservoir Level & Pressure Spoofing",
      client: "American Water • Veolia • Municipal Grids",
      invariant: "Bernoulli Head Loss & Pump Affinity",
    },
    precision_agri: {
      title: "Precision agriculture.",
      subtitle: "Soil Moisture Probe Tampering & False Drought Evapotranspiration",
      client: "John Deere Pivots • Bayer Crop Science",
      invariant: "Penman-Monteith Energy Balance",
    },
    datacenter_gpu: {
      title: "Hyperscale AI datacenter.",
      subtitle: "320 kW GPU Silicon Thermal Masking & Runaway Protection",
      client: "AWS Hyperscale • Azure AI • NVIDIA SuperPOD",
      invariant: "First Law Thermodynamics (Q_thermal == P_elec)",
    },
  };

  const current = domainTitles[activeDomain] || domainTitles.autonomous_drone;

  return (
    <div className="flex flex-col justify-between h-full pr-4 py-2">
      <div className="space-y-6">
        {/* Category Pill Tag as seen in mockup */}
        <div className="flex items-center space-x-2">
          <span className="text-[11px] uppercase tracking-[0.25em] text-white/50 font-mono font-medium">
            SENTINEL SENTRY
          </span>
          <span className="w-1 h-1 rounded-full bg-white/30" />
          <span className="text-[10px] tracking-wider text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/20">
            VERIFIED PHYSICAL TWIN
          </span>
        </div>

        {/* Massive Editorial Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-light tracking-tight text-white leading-[1.08] font-sans">
          {current.title}
        </h1>

        {/* Editorial Body Text matching the approved mockup */}
        <p className="text-sm md:text-base text-white/60 font-light leading-relaxed max-w-md">
          A full dark mode luxury editorial web interface for SENTINEL SENTRY, inspired by Apple.com and the typographic layouts and minimalist design sensibilities of Studio Gruhl. 3D motifs throughout.
        </p>

        {/* Usage Quality Badge matching mockup */}
        <div className="flex items-center space-x-3 text-xs text-white/40 font-mono pt-1">
          <span>Uisage quality. #FFFFFF.</span>
          <span>•</span>
          <span className="text-white/70">{current.invariant}</span>
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center space-x-4 pt-2">
          {/* Pure White Pill Button as seen in mockup */}
          <button
            onClick={onOpenBenchmark}
            className="px-6 py-2.5 rounded-full bg-white text-black text-xs font-medium tracking-wider hover:bg-neutral-200 transition-all duration-300 shadow-xl shadow-white/10 flex items-center space-x-2 active:scale-95"
          >
            <span>Learn more</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onOpenAudit}
            className="px-5 py-2.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/15 text-xs text-white/90 font-mono tracking-wider transition-all duration-300 flex items-center space-x-2"
          >
            <Download className="w-3.5 h-3.5 text-white/60" />
            <span>Audit Dossier</span>
          </button>
        </div>
      </div>

      {/* Enterprise Validation Footer */}
      <div className="border-t border-white/[0.08] pt-4 mt-8">
        <span className="text-[10px] font-mono uppercase tracking-widest text-white/40 block mb-1">
          ENTERPRISE DEPLOYMENTS
        </span>
        <p className="text-xs text-white/70 font-mono">
          {current.client}
        </p>
      </div>
    </div>
  );
};
