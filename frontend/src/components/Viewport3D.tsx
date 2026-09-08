import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Layers, RotateCcw, Radio, Activity } from "lucide-react";
import { SystemStatus } from "../services/api";

interface Viewport3DProps {
  status: SystemStatus | null;
  activeDomain: string;
}

export const Viewport3D: React.FC<Viewport3DProps> = ({
  status,
  activeDomain,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [explodedView, setExplodedView] = useState(false);

  const isAttacked =
    Boolean(status?.attack_state?.is_active) ||
    status?.system_mode === "UNDER_ATTACK" ||
    status?.system_mode === "DETECTED";

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight || 340;

    // 1. Scene & Camera Setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x040507);
    scene.fog = new THREE.FogExp2(0x040507, 0.0025);

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(120, 95, 140);
    camera.lookAt(0, 0, 0);

    // 2. WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // 3. Lighting (Studio Gruhl / Nothing Rim Lighting)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
    keyLight.position.set(100, 150, 100);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x60a5fa, 0.9);
    fillLight.position.set(-100, 50, -100);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 1.2);
    rimLight.position.set(0, -50, -100);
    scene.add(rimLight);

    // 4. Perspective Isometric Grid Floor (Matching approved mockup)
    const gridHelper = new THREE.GridHelper(260, 26, 0x374151, 0x1f2937);
    gridHelper.position.y = -35;
    scene.add(gridHelper);

    // 5. Dual Trajectory Splines
    // True Inertial Trajectory (White Line)
    const trueCurve = new THREE.LineCurve3(
      new THREE.Vector3(-120, -34, -40),
      new THREE.Vector3(120, -34, 40)
    );
    const trueGeo = new THREE.TubeGeometry(trueCurve, 64, 0.8, 8, false);
    const trueMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const truePath = new THREE.Mesh(trueGeo, trueMat);
    scene.add(truePath);

    // Red Spoofed Trajectory (Curved Divergence into restricted airspace)
    let spoofedPath: THREE.Mesh | null = null;
    if (isAttacked) {
      const spoofCurve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(-20, -34, -7),
        new THREE.Vector3(50, -34, 45),
        new THREE.Vector3(120, -34, 95)
      );
      const spoofGeo = new THREE.TubeGeometry(spoofCurve, 64, 1.2, 8, false);
      const spoofMat = new THREE.MeshBasicMaterial({ color: 0xd71920 });
      spoofedPath = new THREE.Mesh(spoofGeo, spoofMat);
      scene.add(spoofedPath);
    }

    // 6. Drone Model Assembly Group
    const droneGroup = new THREE.Group();
    scene.add(droneGroup);

    // Materials
    const chassisMat = new THREE.MeshStandardMaterial({
      color: isAttacked ? 0x221215 : 0x181a20,
      roughness: 0.3,
      metalness: 0.85,
    });
    const carbonMat = new THREE.MeshStandardMaterial({
      color: 0x111317,
      roughness: 0.4,
      metalness: 0.7,
    });
    const rotorMat = new THREE.MeshStandardMaterial({
      color: isAttacked ? 0xd71920 : 0xe5e7eb,
      roughness: 0.2,
      metalness: 0.9,
    });
    const ledRedMat = new THREE.MeshBasicMaterial({ color: 0xd71920 });
    const ledGreenMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x111827,
      roughness: 0.1,
      metalness: 0.1,
      transmission: 0.7,
      transparent: true,
    });

    // Fuselage Central Body
    const bodyGeo = new THREE.BoxGeometry(22, 7, 36);
    const bodyMesh = new THREE.Mesh(bodyGeo, chassisMat);
    bodyMesh.castShadow = true;
    droneGroup.add(bodyMesh);

    // Cockpit Canopy
    const canopyGeo = new THREE.CylinderGeometry(6, 9, 20, 16);
    canopyGeo.rotateX(Math.PI / 2);
    const canopyMesh = new THREE.Mesh(canopyGeo, glassMat);
    canopyMesh.position.set(0, 4.5, 2);
    droneGroup.add(canopyMesh);

    // Camera Gimbal Pod
    const gimbalGeo = new THREE.SphereGeometry(4, 16, 16);
    const gimbalMesh = new THREE.Mesh(gimbalGeo, carbonMat);
    gimbalMesh.position.set(0, -3.5, 18);
    droneGroup.add(gimbalMesh);

    // Internal MEMS Sensor (Visible when Exploded View active)
    const memsGroup = new THREE.Group();
    const pcbGeo = new THREE.BoxGeometry(10, 1.5, 10);
    const pcbMat = new THREE.MeshStandardMaterial({ color: 0x065f46, roughness: 0.5 });
    const pcbMesh = new THREE.Mesh(pcbGeo, pcbMat);
    memsGroup.add(pcbMesh);

    const chipGeo = new THREE.BoxGeometry(4, 1.8, 4);
    const chipMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
    const chipMesh = new THREE.Mesh(chipGeo, chipMat);
    chipMesh.position.y = 1;
    memsGroup.add(chipMesh);
    memsGroup.position.set(0, explodedView ? 16 : 0, 0);
    droneGroup.add(memsGroup);

    // 4 Motor Arms & Rotors
    const armPositions = [
      { x: -28, z: -24, rot: Math.PI / 4, led: ledGreenMat },
      { x: 28, z: -24, rot: -Math.PI / 4, led: ledGreenMat },
      { x: -28, z: 24, rot: (3 * Math.PI) / 4, led: ledRedMat },
      { x: 28, z: 24, rot: -(3 * Math.PI) / 4, led: ledRedMat },
    ];

    const rotorMeshes: THREE.Mesh[] = [];

    armPositions.forEach((pos) => {
      // Carbon Arm Boom
      const armGeo = new THREE.CylinderGeometry(1.4, 1.4, 34, 12);
      armGeo.rotateZ(Math.PI / 2);
      armGeo.rotateY(pos.rot);
      const armMesh = new THREE.Mesh(armGeo, carbonMat);
      armMesh.position.set(pos.x * 0.5, 0, pos.z * 0.5);
      droneGroup.add(armMesh);

      // Motor Hub
      const motorGeo = new THREE.CylinderGeometry(3.5, 3.5, 6, 16);
      const motorMesh = new THREE.Mesh(motorGeo, carbonMat);
      motorMesh.position.set(pos.x, 1, pos.z);
      droneGroup.add(motorMesh);

      // Tip LED
      const ledGeo = new THREE.SphereGeometry(1, 8, 8);
      const ledMesh = new THREE.Mesh(ledGeo, pos.led);
      ledMesh.position.set(pos.x * 1.08, -1, pos.z * 1.08);
      droneGroup.add(ledMesh);

      // Propeller Blades
      const propGeo = new THREE.BoxGeometry(22, 0.4, 2.2);
      const propMesh = new THREE.Mesh(propGeo, rotorMat);
      propMesh.position.set(pos.x, 4.5, pos.z);
      droneGroup.add(propMesh);
      rotorMeshes.push(propMesh);
    });

    // Altitude offset
    droneGroup.position.y = 8;

    // 7. Interactive Orbit Controls via Mouse Drag
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };
    let spherical = { radius: 190, theta: 0.8, phi: 1.05 };

    const updateCameraPos = () => {
      camera.position.x = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
      camera.position.y = spherical.radius * Math.cos(spherical.phi);
      camera.position.z = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
      camera.lookAt(0, 0, 0);
    };
    updateCameraPos();

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevMousePos.x;
      const dy = e.clientY - prevMousePos.y;

      spherical.theta -= dx * 0.008;
      spherical.phi = Math.max(0.2, Math.min(Math.PI / 2 - 0.05, spherical.phi - dy * 0.008));

      updateCameraPos();
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => (isDragging = false);

    const dom = renderer.domElement;
    dom.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    // 8. Animation Loop
    let animId: number;
    let lastTime = performance.now();

    const animate = () => {
      const now = performance.now();
      const delta = (now - lastTime) / 1000;
      lastTime = now;
      const elapsed = now / 1000;

      // Spin Propeller Rotors
      const spinSpeed = isAttacked ? 40 : 25;
      rotorMeshes.forEach((prop, i) => {
        prop.rotation.y += spinSpeed * delta * (i % 2 === 0 ? 1 : -1);
      });

      // Gentle natural hovering bobbing physics
      droneGroup.position.y = 8 + Math.sin(elapsed * 2) * 1.5;
      droneGroup.rotation.z = Math.sin(elapsed * 1.5) * 0.03;
      droneGroup.rotation.x = Math.cos(elapsed * 1.2) * 0.02;

      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };

    animate();

    // Resize handler
    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 340;
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
  }, [isAttacked, explodedView, activeDomain]);

  return (
    <div className="relative rounded-2xl polycarbonate-panel p-5 overflow-hidden flex flex-col justify-between group">
      {/* Top Header Row with Nothing Tech Micro-Badges */}
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center space-x-2.5">
          <div className="flex items-center space-x-1.5 font-dot text-[10px] text-white/80 uppercase">
            <span className="w-1.5 h-1.5 rounded-full bg-[#D71920] animate-pulse" />
            <span>( • LIVE_3D_ISOMETRIC )</span>
          </div>
          <span className="text-white/20 font-mono-tech">|</span>
          <span className="font-mono-tech text-xs text-white/60 uppercase tracking-wider">
            {activeDomain === "autonomous_drone"
              ? "UAV_KINEMATICS // DUAL_TRAJECTORY"
              : activeDomain === "smart_water"
              ? "HYDRAULIC_GRID // BERNOULLI_FLOW"
              : activeDomain === "precision_agri"
              ? "AGRI_PIVOT // PENMAN_MONTEITH"
              : "GPU_CLUSTER // 1ST_LAW_THERMO"}
          </span>
        </div>

        {/* Viewport Control Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setExplodedView(!explodedView)}
            className={`px-3 py-1 rounded-full text-[10px] font-mono-tech border transition-all flex items-center space-x-1.5 ${
              explodedView
                ? "bg-white text-black border-white font-bold shadow-lg shadow-white/20"
                : "text-white/60 border-white/10 hover:text-white hover:bg-white/[0.05]"
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>{explodedView ? "ASSEMBLED" : "EXPLODED_MEMS"}</span>
          </button>
        </div>
      </div>

      {/* 3D WebGL Canvas Mount Container */}
      <div
        ref={mountRef}
        className="w-full h-[330px] relative cursor-grab active:cursor-grabbing rounded-xl overflow-hidden mt-2"
      />

      {/* Bottom Trajectory Legend Strip matching approved mockup */}
      <div className="flex items-center justify-between pt-3 border-t border-white/[0.08] text-[11px] font-mono-tech text-white/60">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-0.5 bg-white inline-block rounded-full" />
            <span className="text-white/90">TRUE INERTIAL ROUTE</span>
          </div>
          {isAttacked && (
            <div className="flex items-center space-x-2">
              <span className="w-3 h-0.5 bg-[#D71920] inline-block rounded-full" />
              <span className="text-[#D71920] font-bold">SPOOFED GPS (+25 m/s)</span>
            </div>
          )}
        </div>

        <div className="text-[10px] text-white/40 tracking-wider">
          ORBIT // DRAG TO ROTATE
        </div>
      </div>
    </div>
  );
};
