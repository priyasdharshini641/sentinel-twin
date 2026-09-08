import React from "react";
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
  const titles: Record<string, string> = {
    autonomous_drone: "Autonomous defense drone.",
    smart_water: "Smart municipal water.",
    precision_agri: "Precision agriculture.",
    datacenter_gpu: "Hyperscale AI datacenter.",
  };

  const activeTitle = titles[activeDomain] || titles.autonomous_drone;

  return (
    <div className="flex flex-col justify-between h-full py-2 pr-2">
      <div className="space-y-6">
        {/* Small Tracking-Widest Tag matching approved mockup */}
        <span className="font-mono-tech text-xs tracking-[0.25em] text-white/50 uppercase block">
          SENTINEL SENTRY
        </span>

        {/* Massive Editorial Headline matching approved mockup */}
        <h1 className="text-4xl sm:text-5xl lg:text-[54px] font-light tracking-tight text-white leading-[1.08] font-editorial">
          {activeTitle}
        </h1>

        {/* Paragraph matching exact mockup typography */}
        <p className="text-sm text-white/60 font-light leading-relaxed max-w-sm font-sans">
          A full dark mode luxury editorial web interface for SENTINEL SENTRY, inspired by the sophisticated product reveals and layouts on Apple.com and the typographic layouts and minimalist design sensibilities of Studio Gruhl. 3D motifs throughout.
        </p>

        {/* Quality Footnote matching approved mockup */}
        <div className="text-xs font-mono-tech text-white/50 pt-1">
          <span>Usage quality. #FFFFFF.</span>
        </div>

        {/* Solid White Pill CTA Button matching approved mockup */}
        <div className="pt-2 flex items-center space-x-3">
          <button
            onClick={onOpenBenchmark}
            className="px-7 py-3 rounded-full bg-white text-black text-xs font-medium tracking-wide hover:bg-neutral-200 transition-all duration-300 shadow-xl shadow-white/10 active:scale-95"
          >
            Learn more
          </button>

          <button
            onClick={onOpenAudit}
            className="px-5 py-3 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/15 text-xs text-white/80 font-mono-tech tracking-wider transition-all duration-300"
          >
            Audit Report
          </button>
        </div>
      </div>

      {/* Live Physical Invariant Badge */}
      <div className="border-t border-white/[0.08] pt-4 mt-8 flex items-center justify-between font-mono-tech text-[11px] text-white/50">
        <span>INVARIANT STATUS</span>
        <span className="text-white/90">
          {activeDomain === "autonomous_drone"
            ? "NEWTONIAN KINEMATICS (F = m·a)"
            : activeDomain === "smart_water"
            ? "BERNOULLI HYDRAULIC CONSERVATION"
            : activeDomain === "precision_agri"
            ? "PENMAN-MONTEITH ENERGY BALANCE"
            : "FIRST LAW THERMODYNAMICS"}
        </span>
      </div>
    </div>
  );
};
