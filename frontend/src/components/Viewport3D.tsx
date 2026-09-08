import React, { useEffect, useRef, useState } from "react";
import { Maximize2, RotateCcw, Cpu, Layers } from "lucide-react";
import { SystemStatus } from "../services/api";

interface Viewport3DProps {
  status: SystemStatus | null;
  activeDomain: string;
  onLaunchAttack: () => void;
  onSafeMode: () => void;
}

export const Viewport3D: React.FC<Viewport3DProps> = ({
  status,
  activeDomain,
  onLaunchAttack,
  onSafeMode,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [rotation, setRotation] = useState({ x: 25, y: -40 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [explodedView, setExplodedView] = useState(false);
  const [rotorAngle, setRotorAngle] = useState(0);

  const isAttacked = status?.attack_state?.is_active || status?.system_mode === "UNDER_ATTACK" || status?.system_mode === "DETECTED";
  const isHealing = status?.system_mode === "HEALING";

  // Animation frame loop
  useEffect(() => {
    let animId: number;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let localRotor = 0;

    const render = () => {
      localRotor += isAttacked ? 0.35 : 0.2;
      setRotorAngle(localRotor);

      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      const cx = width / 2;
      const cy = height / 2 + 10;

      // 3D Perspective Projection Matrix Helper
      const radX = (rotation.x * Math.PI) / 180;
      const radY = (rotation.y * Math.PI) / 180;

      const project = (x: number, y: number, z: number) => {
        // Rotate around Y
        let x1 = x * Math.cos(radY) + z * Math.sin(radY);
        let z1 = -x * Math.sin(radY) + z * Math.cos(radY);

        // Rotate around X
        let y2 = y * Math.cos(radX) - z1 * Math.sin(radX);
        let z2 = y * Math.sin(radX) + z1 * Math.cos(radX);

        // Perspective factor
        const fov = 400;
        const scale = fov / (fov + z2 + 200);

        return {
          px: cx + x1 * scale,
          py: cy + y2 * scale,
          scale,
          depth: z2,
        };
      };

      // 1. Draw Perspective Grid Floor (as shown in approved mockup)
      ctx.strokeStyle = "rgba(255, 255, 255, 0.07)";
      ctx.lineWidth = 1;
      const gridSize = 180;
      const gridStep = 30;
      const groundY = 90;

      for (let x = -gridSize; x <= gridSize; x += gridStep) {
        const p1 = project(x, groundY, -gridSize);
        const p2 = project(x, groundY, gridSize);
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        ctx.stroke();
      }

      for (let z = -gridSize; z <= gridSize; z += gridStep) {
        const p1 = project(-gridSize, groundY, z);
        const p2 = project(gridSize, groundY, z);
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        ctx.stroke();
      }

      // 2. Draw Dual Flight Trajectory Lines (Red Spoofed vs Emerald True Reality)
      // True Reality Path (Straight stable trajectory)
      ctx.beginPath();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.85)";
      ctx.lineWidth = 2.5;
      for (let t = -160; t <= 160; t += 10) {
        const pt = project(t, groundY - 5, t * 0.4);
        if (t === -160) ctx.moveTo(pt.px, pt.py);
        else ctx.lineTo(pt.px, pt.py);
      }
      ctx.stroke();

      // Red Spoofed Trajectory (Diverges dramatically into restricted air/ground when under attack)
      if (isAttacked || isHealing) {
        ctx.beginPath();
        ctx.strokeStyle = "rgba(239, 68, 68, 0.9)";
        ctx.lineWidth = 2.5;
        ctx.setLineDash([4, 4]);
        for (let t = -40; t <= 180; t += 10) {
          const divergence = Math.pow((t + 40) / 70, 2) * 22;
          const pt = project(t, groundY - 5, t * 0.4 + divergence);
          if (t === -40) ctx.moveTo(pt.px, pt.py);
          else ctx.lineTo(pt.px, pt.py);
        }
        ctx.stroke();
        ctx.setLineDash([]); // Reset line dash
      }

      // 3. Render 3D Model Motif according to active domain
      if (activeDomain === "autonomous_drone") {
        renderDrone(ctx, project, localRotor, explodedView, isAttacked);
      } else if (activeDomain === "smart_water") {
        renderWaterTank(ctx, project, localRotor, isAttacked);
      } else if (activeDomain === "precision_agri") {
        renderAgriPivot(ctx, project, localRotor, isAttacked);
      } else {
        renderDataCenter(ctx, project, localRotor, isAttacked);
      }

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [rotation, explodedView, isAttacked, isHealing, activeDomain]);

  // Mouse Orbit Drag Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    setRotation((prev) => ({
      x: Math.max(5, Math.min(80, prev.x - dy * 0.4)),
      y: prev.y + dx * 0.4,
    }));
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => setIsDragging(false);

  return (
    <div className="relative rounded-2xl glass-panel p-6 overflow-hidden flex flex-col justify-between group transition-all duration-300">
      {/* Top Floating Telemetry Overlay */}
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center space-x-2">
          <span className="flex h-2 w-2 relative">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              isAttacked ? "bg-red-400" : "bg-emerald-400"
            }`} />
            <span className={`relative inline-flex rounded-full h-2 w-2 ${
              isAttacked ? "bg-red-500" : "bg-emerald-500"
            }`} />
          </span>
          <span className="font-mono text-xs uppercase tracking-widest text-white/70">
            {activeDomain === "autonomous_drone"
              ? "UAV SENSOR FUSION VIEWPORT"
              : activeDomain === "smart_water"
              ? "MUNICIPAL HYDRAULIC RESERVOIR"
              : activeDomain === "precision_agri"
              ? "PENMAN-MONTEITH CANOPY TWIN"
              : "GPU THERMAL FLUID CLUSTER"}
          </span>
        </div>

        {/* Orbit & View Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setExplodedView(!explodedView)}
            className={`px-2.5 py-1 rounded-md text-[10px] font-mono border transition-all flex items-center space-x-1.5 ${
              explodedView
                ? "bg-white text-black border-white font-medium shadow-md shadow-white/10"
                : "text-white/60 border-white/10 hover:text-white hover:bg-white/[0.04]"
            }`}
            title="Toggle Exploded Hardware Sensor View"
          >
            <Layers className="w-3 h-3" />
            <span>{explodedView ? "CHASSIS ASSEMBLED" : "EXPLODED SENSORS"}</span>
          </button>
          
          <button
            onClick={() => setRotation({ x: 25, y: -40 })}
            className="p-1 rounded-md text-white/50 hover:text-white hover:bg-white/10 border border-white/10 transition-colors"
            title="Reset Camera Angle"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Viewport (Supports interactive mouse rotate) */}
      <div
        className="w-full h-[340px] relative cursor-grab active:cursor-grabbing flex items-center justify-center"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <canvas
          ref={canvasRef}
          width={640}
          height={340}
          className="w-full h-full object-contain"
        />

        {/* Trajectory Legend Badge */}
        <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center space-x-4 text-[10px] font-mono pointer-events-none">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-0.5 bg-white inline-block rounded-full" />
            <span className="text-white/80">INERTIAL REALITY</span>
          </div>
          {isAttacked && (
            <div className="flex items-center space-x-1.5">
              <span className="w-2.5 h-0.5 bg-red-500 inline-block rounded-full animate-pulse" />
              <span className="text-red-400 font-semibold">SPOOFED GPS (+25 m/s)</span>
            </div>
          )}
        </div>

        {/* Status Prompt */}
        {isAttacked && (
          <div className="absolute top-4 right-4 bg-red-950/80 backdrop-blur-md px-3 py-1 rounded-md border border-red-500/40 text-[10px] font-mono text-red-300 flex items-center space-x-1.5 animate-pulse">
            <span>🚨 SATELLITE MEACONING DETECTED</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------------
// 3D MODEL MOTIF DRAWING ROUTINES (Isometric Canvas Math)
// ----------------------------------------------------------------------------

function renderDrone(
  ctx: CanvasRenderingContext2D,
  project: (x: number, y: number, z: number) => { px: number; py: number; scale: number },
  rotorAngle: number,
  exploded: boolean,
  isAttacked: boolean
) {
  const explodeOffset = exploded ? 28 : 0;
  const droneY = -15;

  // 1. Center Fuselage Body (Chrome / Matte Dark Gray)
  const bodyPoints = [
    project(-25, droneY - explodeOffset, -15),
    project(25, droneY - explodeOffset, -15),
    project(32, droneY - explodeOffset, 0),
    project(20, droneY - explodeOffset, 20),
    project(-20, droneY - explodeOffset, 20),
    project(-32, droneY - explodeOffset, 0),
  ];

  ctx.beginPath();
  bodyPoints.forEach((p, idx) => {
    if (idx === 0) ctx.moveTo(p.px, p.py);
    else ctx.lineTo(p.px, p.py);
  });
  ctx.closePath();
  ctx.fillStyle = isAttacked ? "#2a1515" : "#1e2128";
  ctx.fill();
  ctx.strokeStyle = isAttacked ? "#ef4444" : "#e5e7eb";
  ctx.lineWidth = 1.6;
  ctx.stroke();

  // Cockpit canopy reflective metallic highlight
  const canopy = [
    project(-10, droneY - 6 - explodeOffset, -8),
    project(10, droneY - 6 - explodeOffset, -8),
    project(12, droneY - 6 - explodeOffset, 6),
    project(-12, droneY - 6 - explodeOffset, 6),
  ];
  ctx.beginPath();
  canopy.forEach((p, idx) => {
    if (idx === 0) ctx.moveTo(p.px, p.py);
    else ctx.lineTo(p.px, p.py);
  });
  ctx.closePath();
  ctx.fillStyle = isAttacked ? "rgba(239, 68, 68, 0.4)" : "rgba(255, 255, 255, 0.35)";
  ctx.fill();
  ctx.stroke();

  // Internal MEMS Sensors (Rendered when exploded view active)
  if (exploded) {
    const memsPos = project(0, droneY + 12, 0);
    ctx.fillStyle = "#10b981";
    ctx.beginPath();
    ctx.arc(memsPos.px, memsPos.py, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#ffffff";
    ctx.font = "9px monospace";
    ctx.fillText("IMU (Piezoelectric MEMS)", memsPos.px + 8, memsPos.py + 3);
  }

  // 2. Four Motor Arms
  const armOffsets = [
    { x: -55, z: -40 },
    { x: 55, z: -40 },
    { x: -55, z: 40 },
    { x: 55, z: 40 },
  ];

  armOffsets.forEach((arm) => {
    const root = project(arm.x * 0.35, droneY, arm.z * 0.35);
    const end = project(arm.x, droneY, arm.z);

    // Carbon fiber arm strut
    ctx.beginPath();
    ctx.moveTo(root.px, root.py);
    ctx.lineTo(end.px, end.py);
    ctx.strokeStyle = "#4b5563";
    ctx.lineWidth = 3;
    ctx.stroke();

    // Motor Hub
    ctx.beginPath();
    ctx.arc(end.px, end.py, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = "#9ca3af";
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Spinning Rotor Blades
    const rLen = 22;
    const rX = Math.cos(rotorAngle) * rLen;
    const rZ = Math.sin(rotorAngle) * rLen;

    const b1 = project(arm.x + rX, droneY - 2, arm.z + rZ);
    const b2 = project(arm.x - rX, droneY - 2, arm.z - rZ);

    ctx.beginPath();
    ctx.moveTo(b1.px, b1.py);
    ctx.lineTo(b2.px, b2.py);
    ctx.strokeStyle = isAttacked ? "rgba(239, 68, 68, 0.85)" : "rgba(255, 255, 255, 0.85)";
    ctx.lineWidth = 2;
    ctx.stroke();
  });
}

function renderWaterTank(
  ctx: CanvasRenderingContext2D,
  project: (x: number, y: number, z: number) => { px: number; py: number; scale: number },
  rotorAngle: number,
  isAttacked: boolean
) {
  // Translucent Cylinder Tank
  const r = 40;
  const topY = -40;
  const botY = 40;

  // Water level
  const waterLevelY = isAttacked ? 10 : -15;

  ctx.strokeStyle = "rgba(6, 182, 212, 0.8)";
  ctx.fillStyle = isAttacked ? "rgba(239, 68, 68, 0.3)" : "rgba(6, 182, 212, 0.25)";

  ctx.beginPath();
  for (let a = 0; a <= Math.PI * 2; a += 0.2) {
    const pt = project(Math.cos(a) * r, waterLevelY, Math.sin(a) * r);
    if (a === 0) ctx.moveTo(pt.px, pt.py);
    else ctx.lineTo(pt.px, pt.py);
  }
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Draw Tank Glass Outline
  const pTop = project(0, topY, 0);
  const pBot = project(0, botY, 0);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
  ctx.lineWidth = 1.5;
  ctx.strokeRect(pTop.px - 35, pTop.py, 70, pBot.py - pTop.py);

  // Pump Turbine
  const pumpPt = project(60, botY - 5, 0);
  ctx.fillStyle = "#374151";
  ctx.beginPath();
  ctx.arc(pumpPt.px, pumpPt.py, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
}

function renderAgriPivot(
  ctx: CanvasRenderingContext2D,
  project: (x: number, y: number, z: number) => { px: number; py: number; scale: number },
  rotorAngle: number,
  isAttacked: boolean
) {
  // Center Pivot Tower
  const center = project(0, 30, 0);
  const top = project(0, -30, 0);
  ctx.beginPath();
  ctx.moveTo(center.px, center.py);
  ctx.lineTo(top.px, top.py);
  ctx.strokeStyle = "#9ca3af";
  ctx.lineWidth = 3;
  ctx.stroke();

  // Pivot Arm Rotating across crop field
  const armLen = 80;
  const aX = Math.cos(rotorAngle * 0.1) * armLen;
  const aZ = Math.sin(rotorAngle * 0.1) * armLen;
  const armEnd = project(aX, -20, aZ);

  ctx.beginPath();
  ctx.moveTo(top.px, top.py);
  ctx.lineTo(armEnd.px, armEnd.py);
  ctx.strokeStyle = isAttacked ? "#ef4444" : "#10b981";
  ctx.lineWidth = 2.5;
  ctx.stroke();
}

function renderDataCenter(
  ctx: CanvasRenderingContext2D,
  project: (x: number, y: number, z: number) => { px: number; py: number; scale: number },
  rotorAngle: number,
  isAttacked: boolean
) {
  // Server Rack Isometric Cuboid
  const rackH = 70;
  const rackW = 45;
  const rackD = 40;

  const pts = [
    project(-rackW, -rackH, -rackD),
    project(rackW, -rackH, -rackD),
    project(rackW, rackH, -rackD),
    project(-rackW, rackH, -rackD),
  ];

  ctx.beginPath();
  pts.forEach((p, idx) => (idx === 0 ? ctx.moveTo(p.px, p.py) : ctx.lineTo(p.px, p.py)));
  ctx.closePath();
  ctx.fillStyle = isAttacked ? "#351515" : "#131720";
  ctx.fill();
  ctx.strokeStyle = isAttacked ? "#ef4444" : "rgba(255, 255, 255, 0.25)";
  ctx.lineWidth = 1.8;
  ctx.stroke();

  // Glowing Server Blade LEDs
  for (let i = -50; i < 50; i += 12) {
    const p1 = project(-35, i, -rackD - 1);
    const p2 = project(35, i, -rackD - 1);
    ctx.beginPath();
    ctx.moveTo(p1.px, p1.py);
    ctx.lineTo(p2.px, p2.py);
    ctx.strokeStyle = isAttacked ? "#ef4444" : "#06b6d4";
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}
