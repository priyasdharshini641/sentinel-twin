import math
import random
from datetime import datetime


class EnvironmentModel:
    """Models diurnal environmental physics: solar radiation, ambient temperature, and humidity.
    
    Invariants:
    - Solar radiation is 0 W/m² before sunrise and after sunset; peaks near midday.
    - Temperature lags solar radiation by approximately 2 hours due to thermal mass.
    - Humidity has an inverse relationship with temperature (psychrometric physics).
    """

    def __init__(
        self,
        base_temp_min: float = 22.0,
        base_temp_max: float = 35.0,
        peak_solar: float = 950.0,
        sunrise_hour: float = 6.0,
        sunset_hour: float = 19.0,
        seed: int = 42,
    ):
        self.base_temp_min = base_temp_min
        self.base_temp_max = base_temp_max
        self.peak_solar = peak_solar
        self.sunrise_hour = sunrise_hour
        self.sunset_hour = sunset_hour
        self.rng = random.Random(seed)

    def calculate(self, current_time: datetime) -> tuple[float, float, float]:
        """Calculate (temperature, humidity, solar_radiation) for a given timestamp."""
        hour_of_day = (
            current_time.hour
            + current_time.minute / 60.0
            + current_time.second / 3600.0
        )

        # 1. Solar Radiation (half-sine wave between sunrise and sunset)
        if self.sunrise_hour <= hour_of_day <= self.sunset_hour:
            daylight_duration = self.sunset_hour - self.sunrise_hour
            phase = (hour_of_day - self.sunrise_hour) / daylight_duration
            solar = self.peak_solar * math.sin(phase * math.pi)
            # Add subtle atmospheric variance (+/- 1.5%)
            solar += self.rng.gauss(0, 5.0)
            solar = max(0.0, solar)
        else:
            solar = 0.0

        # 2. Temperature (lagged by ~2.5 hours after solar peak)
        # Minimum occurs around 05:00, maximum around 14:30
        temp_phase = (hour_of_day - 5.0) / 24.0 * 2 * math.pi
        temp_amplitude = (self.base_temp_max - self.base_temp_min) / 2.0
        temp_midpoint = (self.base_temp_max + self.base_temp_min) / 2.0
        temp = temp_midpoint - temp_amplitude * math.cos(temp_phase)
        # Small thermal sensor noise (+/- 0.05 °C)
        temp += self.rng.gauss(0, 0.05)
        temp = round(temp, 2)

        # 3. Relative Humidity (inversely correlated with temperature)
        # When temp is min (22°C) -> humidity ~ 78%
        # When temp is max (35°C) -> humidity ~ 38%
        norm_temp = (temp - self.base_temp_min) / max(1.0, (self.base_temp_max - self.base_temp_min))
        humidity = 78.0 - (norm_temp * 40.0)
        humidity += self.rng.gauss(0, 0.2)
        humidity = max(10.0, min(95.0, round(humidity, 1)))

        return temp, humidity, round(solar, 1)
