import React from "react";
import { Shield, ShieldAlert, ShieldCheck, Radio, Plane, Droplets, Sprout, Server } from "lucide-react";
import { SystemStatus } from "../services/api";

interface HeaderProps {
  status: SystemStatus | null;
  activeDomain: string;
  onSelectDomain: (domainId: string) => void;
  onOpenAudit: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  status,
  activeDomain,
  onSelectDomain,
  onOpenAudit,
}) => {
  const isAttacked = status?.attack_state?.is_active || status?.system_mode === "UNDER_ATTACK" || status?.system_mode === "DETECTED";
  const trustScore = status?.defense_result?.system_trust_score ?? 100;

  const domains = [
    { id: "autonomous_drone", name: "Drone Fleet", icon: Plane },
    { id: "smart_water", name: "Smart Water", icon: Droplets },
    { id: "precision_agri", name: "Precision Agri", icon: Sprout },
    { id: "datacenter_gpu", name: "AI Data Center", icon: Server },
  ];

  return (
    <header className="w-full border-b border-white/[0.08] bg-black/60 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Left: Brand / Logo as seen in the approved design */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectDomain("autonomous_drone")}>
          <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-white/[0.05] border border-white/15">
            {/* Stylized Double-S / Hexagonal Shield Motif */}
            <svg viewBox="0 0 24 24" className="w-5 h-5 text-white stroke-[1.8]" fill="none" stroke="currentColor">
              <path d="M4 7l8-4 8 4v10l-8 4-8-4V7z" />
              <path d="M8 10c0-1.5 1.5-2.5 4-2.5s4 1 4 2.5-3 2.5-4 3c-1.5.5-4 1.5-4 3s1.5 2.5 4 2.5 4-1 4-2.5" />
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="font-medium tracking-[0.2em] text-xs text-white uppercase">SENTINEL SENTRY</span>
            <span className="text-[9px] tracking-widest text-white/40 uppercase font-mono">Reality Verification Twin</span>
          </div>
        </div>

        {/* Center: Editorial Nav Links matching the approved mockup */}
        <nav className="hidden md:flex items-center space-x-8 text-xs text-white/60 tracking-wider">
          <button 
            onClick={() => onSelectDomain("autonomous_drone")}
            className={`hover:text-white transition-colors uppercase ${activeDomain === "autonomous_drone" ? "text-white font-medium" : ""}`}
          >
            Featured
          </button>
          
          {/* Domain Dropdown / Fast Switcher */}
          <div className="flex items-center space-x-1 p-1 rounded-full bg-white/[0.03] border border-white/[0.08]">
            {domains.map((dom) => {
              const Icon = dom.icon;
              const isActive = activeDomain === dom.id;
              return (
                <button
                  key={dom.id}
                  onClick={() => onSelectDomain(dom.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] transition-all duration-200 ${
                    isActive
                      ? "bg-white text-black font-semibold shadow-lg shadow-white/10"
                      : "text-white/60 hover:text-white hover:bg-white/[0.06]"
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  <span>{dom.name}</span>
                </button>
              );
            })}
          </div>

          <a href="#benchmark" className="hover:text-white transition-colors uppercase">Benchmark</a>
          <button onClick={onOpenAudit} className="hover:text-white transition-colors uppercase">Forensics</button>
        </nav>

        {/* Right: Threat Beacon & Contact Us button */}
        <div className="flex items-center space-x-4">
          {/* System Trust Pill */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.08]">
            <div className="relative flex items-center justify-center">
              <span
                className={`w-2 h-2 rounded-full ${
                  trustScore > 80 ? "bg-emerald-400" : trustScore > 40 ? "bg-amber-400" : "bg-red-500 animate-ping"
                }`}
              />
              <span
                className={`absolute w-2 h-2 rounded-full ${
                  trustScore > 80 ? "bg-emerald-400" : trustScore > 40 ? "bg-amber-400" : "bg-red-500"
                }`}
              />
            </div>
            <span className="font-mono text-xs text-white/90 font-medium">
              TRUST: {trustScore.toFixed(0)}%
            </span>
          </div>

          {/* Contact Us Outline Pill as shown on top right of mockup */}
          <button
            onClick={onOpenAudit}
            className="px-4 py-1.5 rounded-full border border-white/20 text-xs text-white hover:bg-white hover:text-black transition-all duration-300 tracking-wider font-medium"
          >
            Audit Dossier
          </button>
        </div>
      </div>
    </header>
  );
};
