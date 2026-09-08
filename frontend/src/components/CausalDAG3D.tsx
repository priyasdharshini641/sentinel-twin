import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import { ShieldAlert } from "lucide-react";
import { CausalGraphResponse } from "../services/api";

interface CausalDAG3DProps {
  graph: CausalGraphResponse | null;
  isAttacked: boolean;
  activeDomain: string;
}

export const CausalDAG3D: React.FC<CausalDAG3DProps> = ({
  isAttacked,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight || 440;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x040507);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 140);

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // 3. Studio Lighting for Frosted Glass / Chrome Balls (Matching approved mockup)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 2.0);
    dirLight1.position.set(80, 100, 100);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x93c5fd, 1.2);
    dirLight2.position.set(-80, -60, -80);
    scene.add(dirLight2);

    // 4. Molecular Nodes & Positions (As seen in the approved mockup)
    const nodeCoords = [
      { id: "gps_speed", x: -20, y: 35, z: 10, label: "GPS SPEED" },
      { id: "imu_accel", x: 25, y: 40, z: -15, label: "IMU ACCEL" },
      { id: "baro_alt", x: -35, y: -5, z: -20, label: "BARO ALT" },
      { id: "gps_alt", x: 15, y: 0, z: 25, label: "GPS ALT" },
      { id: "rotor_rpm", x: -25, y: -45, z: 15, label: "ROTOR RPM" },
      { id: "battery", x: 30, y: -40, z: -10, label: "POWER" },
    ];

    const graphGroup = new THREE.Group();
    scene.add(graphGroup);

    // Chrome / Frosted Glass Material for the Spheres
    const sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      roughness: 0.15,
      metalness: 0.85,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      reflectivity: 0.9,
    });

    const sphereAlertMat = new THREE.MeshPhysicalMaterial({
      color: 0xd71920,
      roughness: 0.2,
      metalness: 0.8,
      emissive: 0x990000,
      emissiveIntensity: 0.4,
    });

    const sphereGeo = new THREE.SphereGeometry(7, 32, 32);

    nodeCoords.forEach((node) => {
      const isCompromised = isAttacked && (node.id === "gps_speed" || node.id === "gps_alt");
      const mesh = new THREE.Mesh(sphereGeo, isCompromised ? sphereAlertMat : sphereMat);
      mesh.position.set(node.x, node.y, node.z);
      graphGroup.add(mesh);
    });

    // Connecting Bonds (Fine white tensile cylinders)
    const bonds = [
      { from: 0, to: 1, fractured: isAttacked }, // GPS Speed -> IMU Accel (Newtonian Kinematics F=ma)
      { from: 2, to: 3, fractured: isAttacked }, // Baro Alt -> GPS Alt
      { from: 0, to: 4, fractured: isAttacked }, // GPS Speed -> Rotor RPM
      { from: 4, to: 5, fractured: false },      // Rotor RPM -> Power
      { from: 1, to: 3, fractured: false },
      { from: 2, to: 4, fractured: false },
      { from: 1, to: 5, fractured: false },
    ];

    bonds.forEach((bond) => {
      const p1 = new THREE.Vector3(nodeCoords[bond.from].x, nodeCoords[bond.from].y, nodeCoords[bond.from].z);
      const p2 = new THREE.Vector3(nodeCoords[bond.to].x, nodeCoords[bond.to].y, nodeCoords[bond.to].z);
      const dist = p1.distanceTo(p2);

      const bondGeo = new THREE.CylinderGeometry(0.6, 0.6, dist, 12);
      bondGeo.rotateX(Math.PI / 2);

      const bondMat = new THREE.MeshBasicMaterial({
        color: bond.fractured ? 0xd71920 : 0xffffff,
        transparent: true,
        opacity: bond.fractured ? 0.95 : 0.4,
      });

      const bondMesh = new THREE.Mesh(bondGeo, bondMat);
      bondMesh.position.copy(p1).lerp(p2, 0.5);
      bondMesh.lookAt(p2);
      graphGroup.add(bondMesh);
    });

    // 5. Mouse Drag Orbit Handlers
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevMousePos.x;
      const dy = e.clientY - prevMousePos.y;

      graphGroup.rotation.y += dx * 0.01;
      graphGroup.rotation.x += dy * 0.01;

      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => (isDragging = false);

    const dom = renderer.domElement;
    dom.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    // 6. Gentle Ambient Float Loop
    let animId: number;
    const animate = () => {
      if (!isDragging) {
        graphGroup.rotation.y += 0.003;
      }
      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };
    animate();

    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 440;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(animId);
      dom.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
    };
  }, [isAttacked]);

  return (
    <div className="h-full rounded-2xl polycarbonate-panel p-6 flex flex-col justify-between group relative overflow-hidden">
      {/* Header */}
      <div className="flex items-start justify-between z-10">
        <div>
          <span className="font-dot text-[10px] text-white/50 uppercase tracking-widest block">
            INVARIANT_DAG // 3D
          </span>
          <h3 className="text-xl font-light text-white tracking-tight font-editorial mt-0.5">
            Causal Reality Graph
          </h3>
        </div>

        <span
          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono-tech border ${
            isAttacked
              ? "bg-[#D71920]/20 text-[#D71920] border-[#D71920]/40 animate-pulse font-bold"
              : "bg-white/[0.05] text-white/80 border-white/20"
          }`}
        >
          {isAttacked ? "FRACTURED" : "NOMINAL"}
        </span>
      </div>

      {/* 3D WebGL Molecular Structure Canvas */}
      <div
        ref={mountRef}
        className="w-full flex-1 relative cursor-grab active:cursor-grabbing min-h-[360px]"
      />

      {/* Invariant Breach Toast */}
      {isAttacked && (
        <div className="p-3.5 rounded-xl bg-[#D71920]/15 border border-[#D71920]/40 text-xs font-mono-tech text-white shadow-xl mb-2 animate-fade-in">
          <div className="flex items-center space-x-2 text-[#D71920] font-bold mb-1">
            <ShieldAlert className="w-4 h-4" />
            <span>FRACTURED: NEWTON'S 2ND LAW</span>
          </div>
          <p className="text-white/70 text-[11px] leading-tight font-sans">
            GPS speed +25 m/s delta has 0.04 m/s² IMU reaction. Radio meaconing spoof detected.
          </p>
        </div>
      )}

      {/* Footer Info */}
      <div className="border-t border-white/[0.08] pt-3 flex items-center justify-between text-[11px] font-mono-tech text-white/50">
        <span>INTERACTIVE 3D (DRAG)</span>
        <span className="text-white/80">6 PHYSICAL BONDS</span>
      </div>
    </div>
  );
};
