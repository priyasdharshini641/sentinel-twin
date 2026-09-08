import React from "react";
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
  const isAttacked =
    Boolean(status?.attack_state?.is_active) ||
    status?.system_mode === "UNDER_ATTACK" ||
    status?.system_mode === "DETECTED";

  const trustScore = status?.defense_result?.system_trust_score ?? 100;

  const domains = [
    { id: "autonomous_drone", label: "Autonomous Drone" },
    { id: "smart_water", label: "Smart Water" },
    { id: "precision_agri", label: "Precision Agri" },
    { id: "datacenter_gpu", label: "AI Datacenter" },
  ];

  return (
    <header className="w-full border-b border-white/[0.08] bg-black/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
        {/* Left: Exact Logo & Wordmark matching approved mockup */}
        <div
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => onSelectDomain("autonomous_drone")}
        >
          {/* Stylized Triple Line / S Logo as seen in mockup */}
          <svg
            viewBox="0 0 32 32"
            className="w-7 h-7 text-white stroke-[2.2] transition-transform group-hover:scale-105"
            fill="none"
            stroke="currentColor"
          >
            <path d="M6 10L16 5L26 10L16 15L6 10Z" />
            <path d="M6 16L16 21L26 16" />
            <path d="M6 22L16 27L26 22" />
          </svg>
          <span className="font-editorial text-sm font-semibold tracking-[0.18em] text-white uppercase">
            SENTINEL SENTRY
          </span>
        </div>

        {/* Center: Editorial Nav Links matching the approved mockup */}
        <nav className="hidden md:flex items-center space-x-9 text-xs tracking-wider text-white/70 font-sans">
          <button
            onClick={() => onSelectDomain("autonomous_drone")}
            className={`hover:text-white transition-colors ${
              activeDomain === "autonomous_drone" ? "text-white font-medium" : ""
            }`}
          >
            Featured
          </button>
          
          {/* Domain Dropdown / Pill Switcher */}
          <div className="flex items-center space-x-1 p-1 rounded-full bg-white/[0.04] border border-white/10">
            {domains.map((dom) => (
              <button
                key={dom.id}
                onClick={() => onSelectDomain(dom.id)}
                className={`px-3 py-1 rounded-full text-[11px] font-mono-tech transition-all ${
                  activeDomain === dom.id
                    ? "bg-white text-black font-bold shadow-md shadow-white/10"
                    : "text-white/60 hover:text-white"
                }`}
              >
                {dom.label}
              </button>
            ))}
          </div>

          <a href="#products" className="hover:text-white transition-colors">
            Products
          </a>
          <a href="#solutions" className="hover:text-white transition-colors">
            Solutions
          </a>
          <button onClick={onOpenAudit} className="hover:text-white transition-colors">
            Contact Us
          </button>
        </nav>

        {/* Right: Live Trust Badge & Contact Us Pill matching mockup */}
        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 font-mono-tech text-xs bg-white/[0.04] px-3 py-1 rounded-full border border-white/10">
            <span
              className={`w-2 h-2 rounded-full ${
                isAttacked ? "bg-[#D71920] animate-ping" : "bg-emerald-400"
              }`}
            />
            <span className="text-white/90">
              TRUST: {trustScore.toFixed(0)}%
            </span>
          </div>

          <button
            onClick={onOpenAudit}
            className="px-5 py-1.5 rounded-full border border-white/30 text-xs font-sans text-white hover:bg-white hover:text-black transition-all duration-300 font-normal tracking-wide"
          >
            Contact Us
          </button>
        </div>
      </div>
    </header>
  );
};
