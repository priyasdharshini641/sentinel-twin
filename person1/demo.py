import json
import time
from datetime import datetime

from models import Telemetry
from simulator import PlantSimulator


def print_banner():
    print("=" * 115)
    print("  SENTINEL TWIN - P1 PHYSICAL SIMULATION DEMO (GROUND TRUTH)")
    print("=" * 115)
    print(f"{'Timestamp':<10} | {'Temp':<7} | {'Hum':<6} | {'Solar':<9} | {'CoolLoad':<8} | {'Power':<7} | {'Flow':<8} | {'Tank':<6} | {'Pump':<6} | {'Speed':<6} | {'Pres':<6}")
    print("-" * 115)


def print_telemetry_row(t: Telemetry):
    ts = t.timestamp.strftime("%H:%M:%S")
    print(
        f"{ts:<10} | {t.temperature:>5.1f}C | {t.humidity:>4.1f}% | {t.solar_radiation:>6.1f}W/m | "
        f"{t.cooling_load:>6.1f}kW | {t.power_consumption:>5.1f}kW | {t.water_flow:>5.1f}L/m | {t.tank_level:>4.1f}% | "
        f"{t.pump_status:<6} | {t.pump_speed:>5.1f}% | {t.pressure:>4.2f}b"
    )


def main():
    print_banner()

    sim = PlantSimulator(
        start_time=datetime(2026, 9, 7, 11, 0, 0),
        default_pump_status="ON",
        default_pump_speed=75.0,
    )

    print(">> Phase 1: Normal steady-state operation (Pump ON, Speed: 75%)...")
    for _ in range(5):
        t = sim.step(dt_seconds=1.0)
        print_telemetry_row(t)

    print("\n>> Phase 2: Actuator Event: Turning Pump OFF...")
    sim.set_pump(status="OFF")
    for _ in range(5):
        t = sim.step(dt_seconds=1.0)
        print_telemetry_row(t)

    print("\n>> Phase 3: Actuator Event: Turning Pump back ON at 90% speed...")
    sim.set_pump(status="ON", speed=90.0)
    for _ in range(5):
        t = sim.step(dt_seconds=1.0)
        print_telemetry_row(t)

    print("-" * 115)
    print("\n>> Sample Ground Truth Telemetry Export (P1 Output for P2 / P3 / P4):")
    sample_dict = sim.get_telemetry().to_dict()
    print(json.dumps(sample_dict, indent=2))
    print("=" * 115)


if __name__ == "__main__":
    main()
