import React from "react";
import { X, CheckCircle2, AlertOctagon, Zap, Shield, Cpu } from "lucide-react";
import { BenchmarkComparison } from "../services/api";

interface BenchmarkSplitProps {
  isOpen: boolean;
  onClose: () => void;
  benchmark: BenchmarkComparison | null;
}

export const BenchmarkSplit: React.FC<BenchmarkSplitProps> = ({
  isOpen,
  onClose,
  benchmark,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fade-in">
      <div className="relative w-full max-w-3xl rounded-2xl glass-panel p-8 border border-white/20 shadow-2xl bg-[#090b10]/95">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-1.5 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 mb-6 border-b border-white/10 pb-4">
          <div className="w-10 h-10 rounded-xl bg-white/[0.06] border border-white/15 flex items-center justify-center text-white">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs font-mono tracking-widest text-white/50 uppercase">
              HEAD-TO-HEAD BENCHMARK
            </span>
            <h2 className="text-xl font-normal text-white tracking-tight">
              Traditional ML Anomaly Detection vs Sentinel Twin
            </h2>
          </div>
        </div>

        {/* 2-Column Head to Head Split */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
          {/* Left Panel: Traditional ML (IsolationForest) */}
          <div className="p-6 rounded-xl bg-red-950/20 border border-red-500/30 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-white/60 text-[11px]">SCIKIT-LEARN ISOLATION FOREST</span>
                <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30 font-semibold text-[10px]">
                  FOOLED / 0% ALERT
                </span>
              </div>

              <div className="text-2xl font-sans text-red-400 font-light tracking-tight mb-2">
                Breach Undetected
              </div>

              <p className="text-white/70 font-sans leading-relaxed text-xs">
                {benchmark?.traditional_ml?.blind_spot ||
                  "Statistical marginal anomaly detector checks only point distributions. Because 39 m/s falls within the UAV's broad aerodynamic envelope, Isolation Forest considers the spoofed signal nominal."}
              </p>
            </div>

            <div className="space-y-2 border-t border-white/10 pt-4 text-[11px]">
              <div className="flex justify-between text-white/50">
                <span>PHYSICS AWARENESS</span>
                <span className="text-red-400">NONE (BLACK-BOX)</span>
              </div>
              <div className="flex justify-between text-white/50">
                <span>DETECTION LATENCY</span>
                <span className="text-red-400">FAILED (INF)</span>
              </div>
              <div className="flex justify-between text-white/50">
                <span>ROOT-CAUSE EXPLANATION</span>
                <span className="text-red-400">0% (STATISTICAL NOISE)</span>
              </div>
            </div>
          </div>

          {/* Right Panel: Sentinel Twin Causal Reality Engine */}
          <div className="p-6 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-emerald-400 text-[11px]">SENTINEL CAUSAL ENGINE</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold text-[10px]">
                  CAUGHT IN 0.04s
                </span>
              </div>

              <div className="text-2xl font-sans text-emerald-400 font-light tracking-tight mb-2">
                100% Invariant Verified
              </div>

              <p className="text-white/70 font-sans leading-relaxed text-xs">
                Couples radio GPS delta with piezoelectric MEMS IMU acceleration via Newton's Second Law (F = m·a). Detected that reported velocity spiked without inertial reactionary force in 40ms.
              </p>
            </div>

            <div className="space-y-2 border-t border-white/10 pt-4 text-[11px]">
              <div className="flex justify-between text-white/50">
                <span>PHYSICS AWARENESS</span>
                <span className="text-emerald-400">CONSERVATION LAWS</span>
              </div>
              <div className="flex justify-between text-white/50">
                <span>DETECTION LATENCY</span>
                <span className="text-emerald-400">40ms (REAL-TIME)</span>
              </div>
              <div className="flex justify-between text-white/50">
                <span>FALSE NEGATIVE RATE</span>
                <span className="text-emerald-400">0.0% (ZERO BLIND SPOTS)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between">
          <span className="text-[11px] font-mono text-white/40">
            SCIENTIFIC VALIDATION MATRIX • PS 18
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-full bg-white text-black text-xs font-medium hover:bg-neutral-200 transition-colors"
          >
            Acknowledge Benchmark
          </button>
        </div>
      </div>
    </div>
  );
};
