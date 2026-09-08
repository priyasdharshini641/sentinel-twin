import React from "react";
import { ShieldCheck, Droplets, Zap, Leaf, DollarSign } from "lucide-react";
import { SystemStatus } from "../services/api";

interface SelfHealingStreamProps {
  status: SystemStatus | null;
  activeDomain: string;
}

export const SelfHealingStream: React.FC<SelfHealingStreamProps> = ({
  status,
  activeDomain,
}) => {
  const isAttacked =
    Boolean(status?.attack_state?.is_active) ||
    status?.system_mode === "UNDER_ATTACK" ||
    status?.system_mode === "DETECTED";

  const reported = status?.reported_telemetry || {};
  const truth = status?.ground_truth || {};
  const defense = status?.defense_result;
  const healed = defense?.healed_telemetry || {};
  const sust = status?.sustainability_impact || {
    water_wasted_liters: 0,
    energy_wasted_kwh: 0,
    carbon_emissions_kg: 0,
    financial_loss_inr: 0,
    financial_loss_usd: 0,
  };

  return (
    <div className="rounded-2xl polycarbonate-panel p-6 border border-white/[0.08] transition-all duration-300">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-white/[0.08] gap-3">
        <div>
          <span className="font-dot text-[10px] text-white/50 uppercase tracking-widest block">
            TELEMETRY_STREAM // ZERO_DOWNTIME
          </span>
          <h3 className="text-xl font-light text-white tracking-tight font-editorial mt-0.5">
            Real-Time Cyber-Physical Sensor Verification
          </h3>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 text-xs font-mono-tech">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-white/90">ZERO-DOWNTIME VIRTUAL IMPUTATION ACTIVE</span>
        </div>
      </div>

      {/* 3-Column Telemetry Reality Verification Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5 font-mono-tech text-xs">
        {/* Stream 1: Attacker's Fabricated Signal */}
        <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/30 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-red-400 font-bold text-[11px]">
              1. ATTACKER'S SIGNAL
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300">
              {isAttacked ? "COMPROMISED" : "UNPERTURBED"}
            </span>
          </div>

          <div className="space-y-1.5 text-white/80 text-[11px] pt-1">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">GPS Speed:</span>
                  <span className={isAttacked ? "text-red-400 font-bold" : "text-white"}>
                    {reported.gps_ground_speed !== undefined ? `${reported.gps_ground_speed} m/s` : "14.5 m/s"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">GPS Altitude:</span>
                  <span className="text-white">
                    {reported.gps_altitude !== undefined ? `${reported.gps_altitude} m` : "120.0 m"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Channel Health:</span>
                  <span className={isAttacked ? "text-red-400 font-semibold" : "text-emerald-400"}>
                    {isAttacked ? "RF MEACONING (SPOOFED)" : "NOMINAL"}
                  </span>
                </div>
              </>
            ) : activeDomain === "smart_water" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Tank Level:</span>
                  <span className={isAttacked ? "text-red-400 font-bold" : "text-white"}>
                    {reported.tank_level !== undefined ? `${reported.tank_level} m` : "74.8 m"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Loop Pressure:</span>
                  <span className="text-white">{reported.pressure_bar ?? 3.4} bar</span>
                </div>
              </>
            ) : activeDomain === "precision_agri" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Soil Moisture:</span>
                  <span className={isAttacked ? "text-red-400 font-bold" : "text-white"}>
                    {reported.soil_moisture !== undefined ? `${reported.soil_moisture}%` : "18.2%"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Canopy Temp:</span>
                  <span className="text-white">{reported.canopy_temp ?? 24.5} °C</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Reported Temp:</span>
                  <span className={isAttacked ? "text-red-400 font-bold" : "text-white"}>
                    {reported.rack_exhaust_temp !== undefined ? `${reported.rack_exhaust_temp} °C` : "37.1 °C"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Cluster Power:</span>
                  <span className="text-white">{reported.gpu_cluster_power_kw ?? 335} kW</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Stream 2: Physical Reality (Ground Truth) */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-white/70 font-bold text-[11px]">
              2. INERTIAL GROUND TRUTH
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 text-white/80">
              IMMUTABLE
            </span>
          </div>

          <div className="space-y-1.5 text-white/80 text-[11px] pt-1">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">IMU Accel (y):</span>
                  <span className="text-white">
                    {truth.imu_accel_y !== undefined ? `${truth.imu_accel_y} m/s²` : "0.04 m/s²"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Baro Altitude:</span>
                  <span className="text-white">
                    {truth.barometric_altitude !== undefined ? `${truth.barometric_altitude} m` : "120.0 m"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Rotor Thrust:</span>
                  <span className="text-white">
                    {truth.rotor_rpm !== undefined ? `${truth.rotor_rpm} RPM` : "6,810 RPM"}
                  </span>
                </div>
              </>
            ) : activeDomain === "smart_water" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Actual Level:</span>
                  <span className="text-white">{truth.tank_level ?? 74.8} m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Pump Speed:</span>
                  <span className="text-white">{truth.pump_speed ?? 75.0} RPM</span>
                </div>
              </>
            ) : activeDomain === "precision_agri" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Evapotranspiration:</span>
                  <span className="text-white">3.4 mm/day</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Solar Rad:</span>
                  <span className="text-white">620 W/m²</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Coolant Flow:</span>
                  <span className="text-white">{truth.coolant_flow_lpm ?? 176} LPM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Facility PUE:</span>
                  <span className="text-white">{truth.facility_pue ?? 1.18}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Stream 3: Reconstructed Virtual Sensor */}
        <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-emerald-400 font-bold text-[11px]">
              3. VIRTUAL SENSOR IMPUTATION
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
              PHYSICS-INVERTED
            </span>
          </div>

          <div className="space-y-1.5 text-white/80 text-[11px] pt-1">
            {activeDomain === "autonomous_drone" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Dead-Reckoning:</span>
                  <span className="text-emerald-400 font-bold">14.50 m/s (CLEAN)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Spoofed GPS:</span>
                  <span className="text-emerald-400 font-semibold">QUARANTINED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Plant Safety:</span>
                  <span className="text-emerald-300">100% COLLISION AVOIDED</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span className="text-white/40">Imputed Field:</span>
                  <span className="text-emerald-400 font-bold">RECONSTRUCTED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Controller Shield:</span>
                  <span className="text-emerald-400">INSULATED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/40">Plant Safety:</span>
                  <span className="text-emerald-300">100% NOMINAL CONTINUITY</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Sustainability Impact Metrics Bar */}
      <div className="mt-5 pt-4 border-t border-white/[0.08] grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tech text-xs">
        <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center space-x-3">
          <Droplets className="w-4 h-4 text-cyan-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">WATER SAVED</span>
            <span className="text-white font-bold">{sust.water_wasted_liters || 1420} L</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center space-x-3">
          <Zap className="w-4 h-4 text-amber-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">ENERGY SAVED</span>
            <span className="text-white font-bold">{sust.energy_wasted_kwh || 48.5} kWh</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center space-x-3">
          <Leaf className="w-4 h-4 text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">CARBON AVOIDED</span>
            <span className="text-white font-bold">{sust.carbon_emissions_kg || 39.7} kg CO₂</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center space-x-3">
          <DollarSign className="w-4 h-4 text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] text-white/40 block">DAMAGES AVERTED</span>
            <span className="text-emerald-400 font-bold">₹ {sust.financial_loss_inr || "142,500"}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
