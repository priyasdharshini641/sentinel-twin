import React, { useState, useRef, useEffect } from "react";
import { Zap, ShieldCheck, Square } from "lucide-react";

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

    const clampedDeg = Math.max(-135, Math.min(135, deg));
    setAngle(clampedDeg);

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

  // Generate 42 radial micro-LED ticks encircling the dial from -135deg to +135deg
  const totalTicks = 38;
  const ticks = Array.from({ length: totalTicks }).map((_, idx) => {
    const tickAngle = -135 + (idx / (totalTicks - 1)) * 270;
    const isLit = tickAngle <= angle;
    return { angle: tickAngle, isLit };
  });

  return (
    <div className="rounded-2xl polycarbonate-panel p-6 flex flex-col justify-between group transition-all duration-300">
      {/* Title block matching the exact approved mockup text */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-2xl font-light text-white tracking-tight font-editorial">
            3D brushed titanium dial
          </h3>
          <p className="text-xs text-white/50 tracking-wider font-mono-tech mt-0.5">
            Micro-LED tick marks
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="font-dot text-[11px] px-2.5 py-1 rounded bg-white/[0.06] border border-white/10 text-white/90">
            {(intensity * 100).toFixed(0)}% GAIN
          </span>
        </div>
      </div>

      {/* Main Interactive Dial and Controls Container */}
      <div className="flex flex-col sm:flex-row items-center justify-between mt-6 gap-6">
        {/* The Photorealistic Brushed Titanium Dial Widget */}
        <div className="relative w-44 h-44 flex items-center justify-center select-none cursor-grab active:cursor-grabbing">
          {/* Radial Micro-LED Ticks */}
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
                        ? "h-3 bg-[#D71920] shadow-[0_0_10px_#D71920]"
                        : "h-3 bg-white shadow-[0_0_8px_#ffffff]"
                      : "h-1.5 bg-white/20"
                  }`}
                />
                <div className="w-1 h-1 opacity-0" />
              </div>
            ))}
          </div>

          {/* Titanium Dial Knob (With Realistic Anisotropic Sheen & Knurled Bevel) */}
          <div
            ref={dialRef}
            onPointerDown={() => setIsDragging(true)}
            className="w-28 h-28 rounded-full titanium-finish relative flex items-center justify-center shadow-2xl transition-transform active:scale-98"
            style={{ transform: `rotate(${angle}deg)` }}
          >
            {/* Concentric Knurling Outer Rim */}
            <div className="w-26 h-26 rounded-full border border-white/30 flex items-center justify-center">
              {/* Dial Face Anisotropic Reflected Texture */}
              <div className="w-24 h-24 rounded-full titanium-dial-face relative flex items-center justify-center shadow-inner">
                {/* Center Machined Recessed Hub */}
                <div className="w-14 h-14 rounded-full bg-gradient-to-b from-[#2b2e36] to-[#121418] border border-white/25 shadow-md flex items-center justify-center">
                  <span className="font-dot text-[10px] text-white/60 tracking-tighter">
                    {(intensity * 50).toFixed(0)}m/s
                  </span>
                </div>

                {/* White Indicator Notch / Laser Slit */}
                <div className="absolute top-1.5 w-1 h-4 bg-white rounded-full shadow-[0_0_6px_#ffffff]" />
              </div>
            </div>
          </div>
        </div>

        {/* Tactical Execution Action Buttons */}
        <div className="flex flex-col space-y-3 flex-1 w-full sm:w-auto">
          {!isAttacking ? (
            <button
              onClick={onTriggerAttack}
              className="w-full py-3 px-4 rounded-full bg-white text-black hover:bg-neutral-200 transition-all duration-300 text-xs font-mono-tech font-bold tracking-wider flex items-center justify-center space-x-2 shadow-xl shadow-white/10 active:scale-95"
            >
              <Zap className="w-4 h-4 text-[#D71920]" />
              <span>INJECT GPS SPOOFING (+25 m/s)</span>
            </button>
          ) : (
            <button
              onClick={onStopAttack}
              className="w-full py-3 px-4 rounded-full bg-[#D71920] hover:bg-red-700 text-white transition-all duration-300 text-xs font-mono-tech font-bold tracking-wider flex items-center justify-center space-x-2 shadow-xl shadow-red-600/30 animate-pulse"
            >
              <Square className="w-4 h-4" />
              <span>HALT ADVERSARIAL PERTURBATION</span>
            </button>
          )}

          <button
            onClick={onEngageSafeMode}
            className="w-full py-3 px-4 rounded-full bg-white/[0.05] hover:bg-white/[0.12] border border-white/20 text-white transition-all duration-300 text-xs font-mono-tech tracking-wider flex items-center justify-center space-x-2"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>ENGAGE INERTIAL DEAD-RECKONING</span>
          </button>
        </div>
      </div>
    </div>
  );
};
