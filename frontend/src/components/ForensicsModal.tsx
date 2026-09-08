import React from "react";
import { X, ShieldCheck, FileText, Lock, Copy, Check } from "lucide-react";
import { ForensicDossier } from "../services/api";

interface ForensicsModalProps {
  isOpen: boolean;
  onClose: () => void;
  dossier: ForensicDossier | null;
}

export const ForensicsModal: React.FC<ForensicsModalProps> = ({
  isOpen,
  onClose,
  dossier,
}) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!dossier) return;
    navigator.clipboard.writeText(JSON.stringify(dossier, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fade-in">
      <div className="relative w-full max-w-2xl rounded-2xl glass-panel p-8 border border-white/20 shadow-2xl bg-[#090b10]/95">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-1.5 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-6 border-b border-white/10 pb-4">
          <div className="w-10 h-10 rounded-xl bg-white/[0.06] border border-white/15 flex items-center justify-center text-white">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono tracking-widest text-emerald-400 uppercase">
                CYBER-PHYSICAL INCIDENT DOSSIER
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/80">
                NIST SP 800-82 REV 3
              </span>
            </div>
            <h2 className="text-xl font-normal text-white tracking-tight">
              {dossier?.dossier_id || "ST-DRONE-NAV-D3947E2679"}
            </h2>
          </div>
        </div>

        {/* Forensic Content */}
        <div className="space-y-6 text-xs font-mono">
          {/* Sector & Threat Classification */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08]">
              <span className="text-white/40 block text-[10px] uppercase">SECTOR JURISDICTION</span>
              <span className="text-white text-sm font-sans mt-0.5 block">
                {dossier?.sector || "Aerospace & Autonomous UAV Fleets"}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/30">
              <span className="text-red-400/80 block text-[10px] uppercase">THREAT CLASSIFICATION</span>
              <span className="text-red-300 text-sm font-sans mt-0.5 block font-medium">
                {dossier?.threat_classification || "RF SATELLITE GPS MEACONING"}
              </span>
            </div>
          </div>

          {/* Plain English Root Cause Deduction */}
          <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] space-y-2">
            <span className="text-white/50 block text-[10px] uppercase tracking-wider">
              SHERLOCK CAUSAL PROOF & DEDUCTIVE REASONING
            </span>
            <p className="text-white/90 text-xs font-sans leading-relaxed">
              {dossier?.forensic_proof ||
                "Radio GPS spoofing detected. GPS ground speed reported at 39.6 m/s and altitude at 102.1 m. However, internal IMU accelerometer reports level 0.05 m/s² and barometric altimeter registers steady 120.0 m. In accordance with Newton's Second Law of Motion (F=m·a), an aircraft cannot accelerate eastward at 25 m/s without internal inertial force reaction. GPS receiver is tracking an adversarial spoofed radio signal."}
            </p>
          </div>

          {/* Mitigation Executed */}
          <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 space-y-1">
            <span className="text-emerald-400 block text-[10px] uppercase tracking-wider flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>ZERO-DOWNTIME AUTONOMOUS MITIGATION</span>
            </span>
            <p className="text-emerald-200 text-xs font-sans">
              {dossier?.mitigation_action ||
                "GPS receiver quarantined. Inertial Dead-Reckoning engaged. Flight trajectory restored to 14.5 m/s nominal hover. Mid-air collision averted."}
            </p>
          </div>

          {/* Evidentiary SHA-256 Hash */}
          <div className="p-3.5 rounded-xl bg-black/60 border border-white/10 flex items-center justify-between">
            <div className="flex items-center space-x-2.5 overflow-hidden">
              <Lock className="w-4 h-4 text-white/50 shrink-0" />
              <div className="overflow-hidden">
                <span className="text-[10px] text-white/40 block">CRYPTOGRAPHIC EVIDENCE SEAL (SHA-256)</span>
                <span className="text-white/90 text-[11px] truncate block font-mono">
                  {dossier?.evidentiary_sha256_hash ||
                    "d3947e267929884d03f60bbaf3a8affc3e2bbd8dab2df5fdc6fe117d6b5401ec"}
                </span>
              </div>
            </div>

            <button
              onClick={handleCopy}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors shrink-0 ml-3"
              title="Copy Evidence Report"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between">
          <span className="text-[11px] font-mono text-white/40">
            DIGITALLY SIGNED BY SENTINEL CAUSAL ENGINE
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-full bg-white text-black text-xs font-medium hover:bg-neutral-200 transition-colors"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};
