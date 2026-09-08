import React, { useState, useRef, useEffect } from "react";
import { Zap, ShieldCheck, AlertTriangle, Play, Square } from "lucide-react";

interface BrushedDialProps {
  intensity: number;
  onIntensityChange: (value: number) => void;
  isAttacking: boolean;
  onTriggerAttack: () => void;
  onStopAttack: () => void;
  onEngageSafeMode: () => void;
}

export const BrushedDial: React.FC<BrushedDialProps> = ({
  intensity,
  onIntensityChange,
  isAttacking,
  onTriggerAttack,
  onStopAttack,
  onEngageSafeMode,
}) => {
  const dialRef = useRef<HTMLDivElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [angle, setAngle] = useState(intensity * 270 - 135); // -135deg to +135deg

  // Sync angle if intensity changes from parent
  useEffect(() => {
    setAngle(intensity * 270 - 135);
  }, [intensity]);

  const handlePointerMove = (e: PointerEvent) => {
    if (!isDragging || !dialRef.current) return;
    const rect = dialRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    const dx = e.clientX - cx;
    const dy = e.clientY - cy;

    let deg = (Math.atan2(dy, dx) * 180) / Math.PI + 90;
    if (deg > 180) deg -= 360;

    // Clamp between -135 and +135
    const clampedDeg = Math.max(-135, Math.min(135, deg));
    setAngle(clampedDeg);

    // Map to 0.0 - 1.0 intensity
    const normalized = (clampedDeg + 135) / 270;
    onIntensityChange(parseFloat(normalized.toFixed(2)));
  };

  const handlePointerUp = () => setIsDragging(false);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("pointermove", handlePointerMove);
      window.addEventListener("pointerup", handlePointerUp);
    }
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDragging]);

  // Generate radial micro-LED ticks (40 ticks from -135deg to +135deg)
  const totalTicks = 36;
  const ticks = Array.from({ length: totalTicks }).map((_, idx) => {
    const tickAngle = -135 + (idx / (totalTicks - 1)) * 270;
    const isLit = tickAngle <= angle;
    return { angle: tickAngle, isLit };
  });

  return (
    <div className="rounded-2xl glass-panel p-6 flex flex-col justify-between group transition-all duration-300">
      {/* Title block matching the approved mockup */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl md:text-2xl font-normal text-white tracking-tight">
            3D brushed titanium dial
          </h3>
          <p className="text-xs text-white/50 tracking-wider font-mono mt-1">
            Micro-LED tick marks • Adversarial Drift Injector
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs px-2 py-0.5 rounded bg-white/[0.06] border border-white/10 text-white/80">
            {(intensity * 100).toFixed(0)}% GAIN
          </span>
        </div>
      </div>

      {/* Main Dial and Controls Container */}
      <div className="flex items-center justify-between mt-6">
        {/* The Brushed Titanium Dial Widget */}
        <div className="relative w-36 h-36 flex items-center justify-center select-none cursor-grab active:cursor-grabbing">
          {/* Outer Radial Micro-LED Ticks */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            {ticks.map((t, idx) => (
              <div
                key={idx}
                className="absolute w-0.5 h-full flex flex-col justify-between items-center"
                style={{ transform: `rotate(${t.angle}deg)` }}
              >
                <div
                  className={`w-1 rounded-full transition-all duration-150 ${
                    t.isLit
                      ? isAttacking
                        ? "h-2.5 bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.9)]"
                        : "h-2.5 bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]"
                      : "h-1 bg-white/20"
                  }`}
                />
                <div className="w-1 h-1 opacity-0" />
              </div>
            ))}
          </div>

          {/* Rotary Dial Body (Brushed Titanium finish) */}
          <div
            ref={dialRef}
            onPointerDown={() => setIsDragging(true)}
            className="w-24 h-24 rounded-full brushed-metal relative flex items-center justify-center shadow-2xl transition-transform active:scale-95"
            style={{ transform: `rotate(${angle}deg)` }}
          >
            {/* Dial Face Texture */}
            <div className="w-20 h-20 rounded-full dial-face relative flex items-center justify-center shadow-inner">
              {/* Center Machined Bevel */}
              <div className="w-12 h-12 rounded-full bg-gradient-to-b from-[#2a2d34] to-[#16181d] border border-white/20 shadow-md flex items-center justify-center">
                <span className="text-[10px] font-mono text-white/50 tracking-tighter">
                  {(intensity * 100).toFixed(0)}
                </span>
              </div>

              {/* Indicator Notch / Slit Line */}
              <div className="absolute top-1.5 w-1 h-3.5 bg-white rounded-full shadow-[0_0_4px_#ffffff]" />
            </div>
          </div>
        </div>

        {/* Tactical Execution Actions */}
        <div className="flex flex-col space-y-3 flex-1 pl-6">
          {!isAttacking ? (
            <button
              onClick={onTriggerAttack}
              className="w-full py-2.5 px-4 rounded-xl bg-white/10 hover:bg-red-500 hover:text-white border border-white/20 hover:border-red-400 transition-all duration-300 text-xs font-mono font-medium tracking-wider flex items-center justify-center space-x-2 shadow-lg group"
            >
              <Zap className="w-3.5 h-3.5 text-red-400 group-hover:text-white" />
              <span>INJECT GPS SPOOFING (+25 m/s)</span>
            </button>
          ) : (
            <button
              onClick={onStopAttack}
              className="w-full py-2.5 px-4 rounded-xl bg-red-600 hover:bg-red-700 text-white border border-red-500 transition-all duration-300 text-xs font-mono font-medium tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-red-600/30 animate-pulse"
            >
              <Square className="w-3.5 h-3.5" />
              <span>HALT ADVERSARIAL ATTACK</span>
            </button>
          )}

          <button
            onClick={onEngageSafeMode}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-500/10 hover:bg-emerald-500 hover:text-black border border-emerald-500/30 text-emerald-400 hover:border-emerald-400 transition-all duration-300 text-xs font-mono font-medium tracking-wider flex items-center justify-center space-x-2"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>ENGAGE INERTIAL SELF-HEALING</span>
          </button>
        </div>
      </div>
    </div>
  );
};
