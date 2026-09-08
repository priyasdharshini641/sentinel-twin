import React, { useEffect, useState } from "react";
import { Header } from "./components/Header";
import { HeroEditorial } from "./components/HeroEditorial";
import { Viewport3D } from "./components/Viewport3D";
import { BrushedDial } from "./components/BrushedDial";
import { CausalDAG3D } from "./components/CausalDAG3D";
import { SelfHealingStream } from "./components/SelfHealingStream";
import { ForensicsModal } from "./components/ForensicsModal";
import { BenchmarkSplit } from "./components/BenchmarkSplit";
import {
  api,
  SystemStatus,
  CausalGraphResponse,
  BenchmarkComparison,
  ForensicDossier,
} from "./services/api";

export function App() {
  const [activeDomain, setActiveDomain] = useState<string>("autonomous_drone");
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [causalGraph, setCausalGraph] = useState<CausalGraphResponse | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkComparison | null>(null);
  const [dossier, setDossier] = useState<ForensicDossier | null>(null);
  const [intensity, setIntensity] = useState<number>(0.75);

  const [isForensicsOpen, setIsForensicsOpen] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);

  // Poll system status and causal graph
  const fetchData = async () => {
    try {
      const s = await api.getSystemStatus();
      setStatus(s);
      if (s.active_domain && s.active_domain !== activeDomain) {
        setActiveDomain(s.active_domain);
      }
    } catch {
      // Backend polling error caught gracefully
    }

    try {
      const cg = await api.getCausalGraph();
      setCausalGraph(cg);
    } catch {}

    try {
      const bm = await api.getBenchmark();
      setBenchmark(bm);
    } catch {}

    try {
      const dos = await api.getForensicsDossier();
      setDossier(dos);
    } catch {}
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1500);
    return () => clearInterval(interval);
  }, [activeDomain]);

  const handleSelectDomain = async (domainId: string) => {
    setActiveDomain(domainId);
    try {
      await api.switchDomain(domainId);
      await fetchData();
    } catch (err) {
      console.error("Failed to switch domain:", err);
    }
  };

  const handleLaunchAttack = async () => {
    try {
      const targetSensors =
        activeDomain === "autonomous_drone"
          ? ["gps_ground_speed"]
          : activeDomain === "smart_water"
          ? ["tank_level", "pressure_bar"]
          : activeDomain === "precision_agri"
          ? ["soil_moisture"]
          : ["gpu_temperature"];

      await api.launchAttack("coordinated", targetSensors, intensity);
      await fetchData();
    } catch (err) {
      console.error("Failed to launch attack:", err);
    }
  };

  const handleStopAttack = async () => {
    try {
      await api.stopAttack();
      await fetchData();
    } catch (err) {
      console.error("Failed to stop attack:", err);
    }
  };

  const handleEngageSafeMode = async () => {
    try {
      await api.activateSafeMode();
      await fetchData();
    } catch (err) {
      console.error("Failed to engage safe mode:", err);
    }
  };

  const isAttacking =
    Boolean(status?.attack_state?.is_active) ||
    status?.system_mode === "UNDER_ATTACK" ||
    status?.system_mode === "DETECTED";

  return (
    <div className="min-h-screen bg-[#050608] text-white flex flex-col selection:bg-white selection:text-black">
      {/* 1. Header Navigation Bar */}
      <Header
        status={status}
        activeDomain={activeDomain}
        onSelectDomain={handleSelectDomain}
        onOpenAudit={() => setIsForensicsOpen(true)}
      />

      {/* 2. Main High-End Editorial Command Center (Matching the Approved Mockup) */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Top 3-Column Editorial Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Left Column (Editorial Typography & CTAs) - 4 cols */}
          <div className="lg:col-span-4 flex flex-col">
            <HeroEditorial
              status={status}
              activeDomain={activeDomain}
              onOpenAudit={() => setIsForensicsOpen(true)}
              onOpenBenchmark={() => setIsBenchmarkOpen(true)}
            />
          </div>

          {/* Center Column (Viewport 3D Dual-Trajectory + Brushed Titanium Dial) - 5 cols */}
          <div className="lg:col-span-5 flex flex-col space-y-6">
            {/* Center Top: 3D Motif & Dual Trajectory */}
            <Viewport3D
              status={status}
              activeDomain={activeDomain}
            />

            {/* Center Bottom: 3D Brushed Titanium Dial with Micro-LEDs */}
            <BrushedDial
              intensity={intensity}
              onIntensityChange={setIntensity}
              isAttacking={isAttacking}
              onTriggerAttack={handleLaunchAttack}
              onStopAttack={handleStopAttack}
              onEngageSafeMode={handleEngageSafeMode}
            />
          </div>

          {/* Right Column (3D Molecular Causal Graph) - 3 cols */}
          <div className="lg:col-span-3 flex flex-col">
            <CausalDAG3D
              graph={causalGraph}
              isAttacked={isAttacking}
              activeDomain={activeDomain}
            />
          </div>
        </div>

        {/* Bottom Full-Width Module: Zero-Downtime Self-Healing Stream & ESG Ticker */}
        <div className="w-full">
          <SelfHealingStream
            status={status}
            activeDomain={activeDomain}
          />
        </div>
      </main>

      {/* Footer Branding */}
      <footer className="border-t border-white/[0.08] py-6 px-6 bg-black/40 text-center text-xs text-white/40 font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>SENTINEL TWIN • ZERO-TRUST REALITY VERIFICATION ENGINE</span>
          <span>NIST SP 800-82 REV 3 & CYBER-PHYSICAL INVARIANT AUDITING</span>
        </div>
      </footer>

      {/* Modals */}
      <ForensicsModal
        isOpen={isForensicsOpen}
        onClose={() => setIsForensicsOpen(false)}
        dossier={dossier}
      />

      <BenchmarkSplit
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
        benchmark={benchmark}
      />
    </div>
  );
}

export default App;
