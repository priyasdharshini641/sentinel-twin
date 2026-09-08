import React, { useEffect, useRef, useState } from "react";
import { Activity, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";
import { CausalGraphResponse } from "../services/api";

interface CausalDAG3DProps {
  graph: CausalGraphResponse | null;
  isAttacked: boolean;
  activeDomain: string;
}

export const CausalDAG3D: React.FC<CausalDAG3DProps> = ({
  graph,
  isAttacked,
  activeDomain,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [rotation, setRotation] = useState({ x: 20, y: 15 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Fallback nodes if API is loading
  const nodes = graph?.nodes?.length
    ? graph.nodes
    : [
        { id: "gps_speed", label: "GPS Ground Speed", value: "39.6 m/s", type: "radio_sensor" },
        { id: "imu_accel", label: "IMU Accelerometer", value: "0.04 m/s²", type: "inertial_sensor" },
        { id: "baro_alt", label: "Barometric Altimeter", value: "120.0 m", type: "pressure_sensor" },
        { id: "gps_alt", label: "GPS Radio Altitude", value: "102.1 m", type: "radio_sensor" },
        { id: "rotor_rpm", label: "Rotor Thrust RPM", value: "6810 RPM", type: "actuator" },
        { id: "battery_current", label: "Battery Current", value: "24.6 A", type: "electrical" },
      ];

  // 3D Positions for the nodes arranged in an organic molecular cluster (as in the approved image)
  const nodePositions: Record<string, { x: number; y: number; z: number }> = {
    gps_speed: { x: 0, y: -80, z: 20 },
    imu_accel: { x: -65, y: -10, z: -30 },
    baro_alt: { x: 65, y: -20, z: -20 },
    gps_alt: { x: 50, y: 60, z: 40 },
    rotor_rpm: { x: -50, y: 70, z: 10 },
    battery_current: { x: 0, y: 110, z: -40 },
  };

  const edges = [
    { from: "imu_accel", to: "gps_speed", law: "Newton's 2nd Law (F=m·a)", fractured: isAttacked },
    { from: "baro_alt", to: "gps_alt", law: "Barometric Lapse Rate", fractured: isAttacked },
    { from: "rotor_rpm", to: "gps_speed", law: "Rotor Aerodynamic Thrust", fractured: isAttacked },
    { from: "battery_current", to: "rotor_rpm", law: "Electromotive Power", fractured: false },
    { from: "imu_accel", to: "rotor_rpm", law: "Body Frame Torque Coupling", fractured: false },
  ];

  useEffect(() => {
    let animId: number;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let time = 0;

    const render = () => {
      time += 0.03;
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      const cx = width / 2;
      const cy = height / 2;

      // 3D Perspective Projection Matrix
      const radX = (rotation.x * Math.PI) / 180;
      const radY = (rotation.y * Math.PI) / 180;

      const project = (x: number, y: number, z: number) => {
        let x1 = x * Math.cos(radY) + z * Math.sin(radY);
        let z1 = -x * Math.sin(radY) + z * Math.cos(radY);

        let y2 = y * Math.cos(radX) - z1 * Math.sin(radX);
        let z2 = y * Math.sin(radX) + z1 * Math.cos(radX);

        const fov = 350;
        const scale = fov / (fov + z2 + 200);

        return {
          px: cx + x1 * scale,
          py: cy + y2 * scale,
          scale,
          depth: z2,
        };
      };

      // 1. Draw Connecting Physical Bond Edges
      edges.forEach((edge) => {
        const p1 = nodePositions[edge.from] || { x: -30, y: -20, z: 0 };
        const p2 = nodePositions[edge.to] || { x: 30, y: 20, z: 0 };

        const proj1 = project(p1.x, p1.y, p1.z);
        const proj2 = project(p2.x, p2.y, p2.z);

        ctx.beginPath();
        ctx.moveTo(proj1.px, proj1.py);

        if (edge.fractured) {
          // Lightning crack / jagged fracture line when invariant is broken
          const midX = (proj1.px + proj2.px) / 2 + Math.sin(time * 15) * 6;
          const midY = (proj1.py + proj2.py) / 2 + Math.cos(time * 15) * 6;
          ctx.lineTo(midX, midY);
          ctx.lineTo(proj2.px, proj2.py);
          ctx.strokeStyle = "rgba(239, 68, 68, 0.9)";
          ctx.lineWidth = 2.5;
          ctx.stroke();

          // Fracture Spark Glow
          ctx.fillStyle = "rgba(239, 68, 68, 0.3)";
          ctx.beginPath();
          ctx.arc(midX, midY, 8 + Math.sin(time * 20) * 3, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Smooth tensile rod with traveling laser energy pulse
          ctx.lineTo(proj2.px, proj2.py);
          ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
          ctx.lineWidth = 1.6;
          ctx.stroke();

          // Traveling conservation pulse particle
          const pulseT = (time % 1.5) / 1.5;
          const pulseX = proj1.px + (proj2.px - proj1.px) * pulseT;
          const pulseY = proj1.py + (proj2.py - proj1.py) * pulseT;

          ctx.fillStyle = "#ffffff";
          ctx.beginPath();
          ctx.arc(pulseX, pulseY, 2.5, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // 2. Draw 3D Frosted Glass / Chrome Spheres (matching the approved mockup)
      const sortedNodes = nodes
        .map((n) => {
          const pos = nodePositions[n.id] || { x: 0, y: 0, z: 0 };
          const p = project(pos.x, pos.y, pos.z);
          return { ...n, ...p };
        })
        .sort((a, b) => b.depth - a.depth);

      sortedNodes.forEach((node) => {
        const radius = 18 * node.scale;

        // Outer glow
        const glowGrad = ctx.createRadialGradient(
          node.px - radius * 0.3,
          node.py - radius * 0.3,
          radius * 0.1,
          node.px,
          node.py,
          radius * 1.5
        );

        if (isAttacked && (node.id === "gps_speed" || node.id === "gps_alt")) {
          glowGrad.addColorStop(0, "rgba(254, 202, 202, 0.9)");
          glowGrad.addColorStop(0.5, "rgba(239, 68, 68, 0.7)");
          glowGrad.addColorStop(1, "rgba(185, 28, 28, 0.1)");
        } else {
          // Frosted chrome / white sheen as shown in user's image
          glowGrad.addColorStop(0, "rgba(255, 255, 255, 0.95)");
          glowGrad.addColorStop(0.4, "rgba(209, 213, 219, 0.6)");
          glowGrad.addColorStop(1, "rgba(107, 114, 128, 0.15)");
        }

        ctx.fillStyle = glowGrad;
        ctx.beginPath();
        ctx.arc(node.px, node.py, radius, 0, Math.PI * 2);
        ctx.fill();

        // White specular rim highlight
        ctx.strokeStyle = isAttacked && (node.id === "gps_speed" || node.id === "gps_alt")
          ? "#ef4444"
          : "rgba(255, 255, 255, 0.85)";
        ctx.lineWidth = 1;
        ctx.stroke();

        // Node Label
        ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
        ctx.font = "10px monospace";
        ctx.textAlign = "center";
        ctx.fillText(node.label, node.px, node.py + radius + 12);
      });

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [rotation, isAttacked, nodes]);

  // Drag Orbit Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    setRotation((prev) => ({
      x: Math.max(-40, Math.min(60, prev.x - dy * 0.4)),
      y: prev.y + dx * 0.4,
    }));
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => setIsDragging(false);

  return (
    <div className="h-full rounded-2xl glass-panel p-6 flex flex-col justify-between group transition-all duration-300 relative overflow-hidden">
      {/* Header */}
      <div className="flex items-start justify-between z-10">
        <div>
          <span className="text-[10px] tracking-widest text-white/50 font-mono uppercase">
            PHYSICAL INVARIANT DAG
          </span>
          <h3 className="text-xl font-normal text-white tracking-tight mt-0.5">
            Causal Reality Graph
          </h3>
        </div>

        <span
          className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
            isAttacked
              ? "bg-red-950/80 text-red-400 border-red-500/40 animate-pulse"
              : "bg-emerald-950/80 text-emerald-400 border-emerald-500/40"
          }`}
        >
          {isAttacked ? "FRACTURED" : "NOMINAL"}
        </span>
      </div>

      {/* 3D Molecular Graph Canvas */}
      <div
        className="w-full flex-1 relative cursor-grab active:cursor-grabbing flex items-center justify-center min-h-[380px]"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <canvas
          ref={canvasRef}
          width={360}
          height={420}
          className="w-full h-full object-contain"
        />

        {/* Floating Invariant Fracture Toast */}
        {isAttacked && (
          <div className="absolute bottom-4 inset-x-4 bg-red-950/90 border border-red-500/40 rounded-xl p-3 backdrop-blur-md text-[11px] font-mono text-red-200 shadow-xl animate-fade-in">
            <div className="flex items-center space-x-2 text-red-400 font-semibold mb-1">
              <ShieldAlert className="w-4 h-4" />
              <span>BOND FRACTURE: F = m·a</span>
            </div>
            <p className="text-white/70 text-[10px]">
              GPS velocity delta (39.6 m/s) contradicts piezoelectric IMU accelerometer (0.04 m/s²).
            </p>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="border-t border-white/[0.08] pt-3 flex items-center justify-between text-[11px] font-mono text-white/50">
        <span>INTERACTIVE ORBIT (DRAG)</span>
        <span className="text-white/80">6 PHYSICAL BONDS</span>
      </div>
    </div>
  );
};
