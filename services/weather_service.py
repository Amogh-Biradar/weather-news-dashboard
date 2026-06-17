#!/usr/bin/env python3
"""
Weather Service - Local weather mock data generator with terminal display.
Generates realistic weather data with temperature cycles, forecasts, and proper formatting.
"""

import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from .service import BaseService
from data.weather import WeatherReading, ForecastReading
from config import Config


class WeatherService(BaseService):
    """
    Service for generating and displaying weather data.
    
    Features:
    - Generates realistic mock weather data (since no live API key)
    - Realistic temperature variation with day/night cycle
    - Generates forecast readings every 3 hours for the next 24 hours
    - Uses emoji for weather conditions
    - Temperature conversion: C to F = (c * 9/5) + 32
    - Calculates feels-like temperature with adjustment
    - Includes wind speed in km/h and mph
    - Generates humidity, pressure, cloud cover, visibility data
    - Tracks observation timestamp for cache invalidation
    
    Configuration:
    - provider: "mock" (default) or "open-meteo"/"openweathermap"
    - default_city: Default city name for location
    - cache_duration: Cache expiration in seconds (default: 3600, i.e., 1 hour)
    - cache_file: Path to cache file (default: config.DATA_CACHE_FILE)
    """

    # ===== Emoji Map for Weather Conditions =====
    WEATHER_EMOJI = {
        "Clear sky": "☀️",
        "Partly cloudy": "⛅",
        "Overcast": "☁️",
        "Light rain": "🌦️",
        "Moderate rain": "🌧️",
        "Heavy rain": "🌧️",
        "Light snow": "❄️",
        "Snow": "❄️",
        "Thunderstorm": "⛈️",
        "Fog": "🌫️",
        "Haze": "🌫️",
        "Drizzle": "🌦️",
        "Freezing rain": "🌧️",
        "Ice": "❄️",
    }

    # ===== Realistic Temperature Pattern =====
    # Hourly temperature variation (deviation from base temp)
    TEMP_DEVIATIONS = [
        0.0, 0.3, 0.5, 0.7, 0.5, 0.2,  # 0-6h (early morning/night)
        -0.5, -0.8, -1.0, -1.2, -1.0, -0.8,  # 6-12h (midnight/early morning)
        -0.5, 0.0, 0.8, 1.5, 2.0, 2.5,  # 12-18h (dawn/morning/early afternoon)
        2.8, 3.0, 2.8, 2.5, 2.0, 1.5,  # 18-24h (midday/afternoon/evening)
    ]

    # ===== Weather Pattern Probabilities =====
    # Likelihood of each weather type at different times of day
    DAY_WEATHER = [
        "Clear sky",  # 0-6h (morning) - 40% clear, 40% cloudy, 20% rain
        "Partly cloudy",  # 6-12h (noon) - 30% clear, 50% partly cloudy, 20% rain
        "Clear sky",  # 12-18h (afternoon) - 40% clear, 40% partly cloudy, 20% other
        "Thunderstorm",  # 18-24h (evening/night) - 30% partly cloudy, 40% overcast, 30% rain/snow
    ]

    def __init__(self, config=None):
        super().__init__("WeatherService", config)
        
        # Helper to handle both Config class (attribute access) and dict (dict access)
        def _get_val(key, default):
            if config is None:
                return default
            if hasattr(config, key):
                v = getattr(config, key)
                return v if v is not None else default
            return self.config.get(key, default) if isinstance(self.config, dict) else default
        
        self._provider = _get_val("WEATHER_PROVIDER", "mock")
        self._default_city = _get_val("DEFAULT_CITY", "New York")
        self._cache_file = _get_val("DATA_CACHE_FILE", "/Users/amoghb/.openclaw/workspace/news_cache.json")
        self._cache_duration = _get_val("cache_duration", 3600)  # 1 hour
        
        # Weather data storage
        self._current: Optional[WeatherReading] = None
        self._forecast: List[ForecastReading] = []
        self._summary: Optional[Any] = None
        
        # For mock data generation
        self._base_temp = 18.0  # Base temperature in Celsius
        self._base_humidity = 60  # Base humidity percentage
        self._base_pressure = 1013  # Base pressure in hPa

    def _calculate_fahrenheit(self, celsius: float) -> float:
        """
        Convert Celsius to Fahrenheit using the standard formula.
        
        Args:
            celsius: Temperature in Celsius
            
        Returns:
            Temperature in Fahrenheit
        """
        return (celsius * 9/5) + 32

    def _get_hour_pattern(self, hour: int) -> tuple:
        """
        Get temperature deviation and weather type for a given hour.
        
        Args:
            hour: Hour of the day (0-23)
            
        Returns:
            Tuple of (temp_deviation, weather_type)
        """
        # Determine which pattern range
        if hour < 6:
            index = 0
        elif hour < 12:
            index = 6
        elif hour < 18:
            index = 12
        else:
            index = 18
            
        temp_dev = self.TEMP_DEVIATIONS[index]
        
        # Determine weather type based on time of day
        weather_roll = random.random()
        if hour < 6:
            # Night - clearer skies
            if weather_roll < 0.4:
                weather = "Clear sky"
            elif weather_roll < 0.8:
                weather = "Partly cloudy"
            else:
                weather = random.choice(["Overcast", "Light rain", "Thunderstorm"])
        elif hour < 12:
            # Early morning
            if weather_roll < 0.4:
                weather = "Clear sky"
            elif weather_roll < 0.8:
                weather = "Partly cloudy"
            else:
                weather = "Overcast"
        elif hour < 18:
            # Day
            if weather_roll < 0.5:
                weather = "Clear sky"
            elif weather_roll < 0.8:
                weather = "Partly cloudy"
            else:
                weather = random.choice(["Overcast", "Light rain", "Thunderstorm"])
        else:
            # Evening
            if weather_roll < 0.5:
                weather = "Clear sky"
            elif weather_roll < 0.8:
                weather = "Overcast"
            else:
                weather = random.choice(["Partly cloudy", "Light rain", "Thunderstorm", "Fog"])
                
        return temp_dev, weather

    def _generate_mock_current(self, city: str = None, hour: int = None) -> WeatherReading:
        """
        Generate realistic mock weather data for current conditions.
        
        Temperature follows day/night cycle:
        - Colder at night (base temp - 3 to -8)
        - Warmer during day (base temp + 2 to +5)
        - Smooth transition at dawn/dusk
        
        Args:
            city: City name (currently unused in mock mode)
            hour: Hour for base temperature calculation (defaults to current time)
            
        Returns:
            WeatherReading object with complete current conditions
        """
        # Get hour for temperature calculation (default to current hour)
        if hour is None:
            now = datetime.now(timezone.utc)
            hour = now.hour
            
        # Calculate temperature based on time of day
        base_temp = self._base_temp + self.TEMP_DEVIATIONS[hour % 24]
        
        # Weather conditions based on time
        temp_dev, weather = self._get_hour_pattern(hour)
        temperature = base_temp + temp_dev
        
        # Humidity varies inversely with temperature
        if 6 <= hour <= 20:  # Daytime - lower humidity
            humidity = max(40, self._base_humidity + random.randint(-5, 10))
        else:  # Nighttime - higher humidity
            humidity = min(90, self._base_humidity + random.randint(5, 15))
            
        # Pressure varies slightly (typically stable)
        pressure = self._base_pressure + random.randint(-5, 5)
        
        # Wind speed (light to moderate)
        wind_speed = random.uniform(5, 15)
        
        # Cloud cover based on weather type
        cloud_cover = {
            "Clear sky": random.uniform(0, 20),
            "Partly cloudy": random.uniform(20, 50),
            "Overcast": random.uniform(50, 80),
            "Light rain": random.uniform(50, 70),
            "Moderate rain": random.uniform(60, 80),
            "Heavy rain": random.uniform(70, 90),
            "Light snow": random.uniform(50, 70),
            "Snow": random.uniform(60, 85),
            "Thunderstorm": random.uniform(60, 90),
            "Fog": random.uniform(85, 100),
            "Haze": random.uniform(50, 80),
            "Drizzle": random.uniform(50, 70),
        }.get(weather, random.uniform(20, 50))
        
        # Visibility varies with conditions
        visibility = {
            "Clear sky": 15.0,  # km
            "Partly cloudy": 12.0,
            "Overcast": 10.0,
            "Light rain": 8.0,
            "Moderate rain": 5.0,
            "Heavy rain": 3.0,
            "Light snow": 6.0,
            "Snow": 2.0,
            "Thunderstorm": 1.0,
            "Fog": 1.0,
            "Haze": 5.0,
            "Drizzle": 7.0,
        }.get(weather, 10.0)
        
        # Feels like temperature (simple adjustment based on wind)
        feels_like = temperature - (wind_speed / 10) * 1.5 if wind_speed > 5 else temperature
        
        # Calculate mph
        wind_speed_mph = wind_speed * 0.621371
        
        # Calculate feels like in Fahrenheit
        feels_like_f = self._calculate_fahrenheit(feels_like)
        
        return WeatherReading(
            temperature_c=round(temperature, 1),
            temperature_f=round(self._calculate_fahrenheit(temperature), 0),
            feels_like_c=round(feels_like, 1),
            feels_like_f=round(feels_like_f, 0),
            weather_desc=weather,
            wind_speed_kmh=round(wind_speed, 1),
            wind_speed_mph=round(wind_speed_mph, 1),
            wind_direction=random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            humidity=round(humidity, 0),
            pressure_mb=round(pressure, 1),
            visibility_km=round(visibility, 1),
            cloud_cover=round(cloud_cover, 1),
            is_day=6 <= hour <= 18,
            observation_time=int(time.time()),
        )

    def _generate_hourly_forecast(self, hours_ahead: int = 24, base: Optional[WeatherReading] = None) -> List[ForecastReading]:
        """
        Generate hourly weather forecast using pattern-based simulation.
        
        Creates readings every 3 hours for realistic hourly representation.
        Temperature follows day/night cycle with gradual changes.
        Weather patterns shift over time based on typical atmospheric behavior.
        
        Args:
            hours_ahead: Number of hours to forecast (default: 24)
            base: Base weather reading to build forecast from (None = generate fresh)
            
        Returns:
            List of ForecastReading objects
        """
        forecasts = []
        now = datetime.now(timezone.utc)
        
        # Use current base temp or default
        base_temp = base.temperature_c if base else self._base_temp
        base_hour = now.hour
        base_weather = base.weather_desc if base else "Clear sky"
        
        # Generate 3-hour intervals
        for interval in range(0, hours_ahead, 3):
            future_hour = (base_hour + interval) % 24
            
            # Temperature variation from base (day/night cycle)
            temp_dev = self.TEMP_DEVIATIONS[future_hour % 24]
            temperature = base_temp + temp_dev + random.uniform(-1, 1)  # Add randomness
            
            # Weather pattern changes over time
            weather_roll = random.random()
            hour_phase = future_hour // 6  # 0=early AM, 1=mid AM, 2=midday, 3=evening
            
            if interval < 6:  # Near current time
                weather = base_weather  # Maintain base condition
            else:
                # Shift weather based on time of day
                if future_hour < 6:
                    if weather_roll < 0.5:
                        weather = "Clear sky"
                    elif weather_roll < 0.8:
                        weather = "Partly cloudy"
                    else:
                        weather = random.choice(["Overcast", "Light rain", "Fog"])
                elif future_hour < 12:
                    if weather_roll < 0.5:
                        weather = "Clear sky"
                    elif weather_roll < 0.8:
                        weather = "Partly cloudy"
                    else:
                        weather = "Overcast"
                elif future_hour < 18:
                    if weather_roll < 0.4:
                        weather = "Clear sky"
                    elif weather_roll < 0.7:
                        weather = "Partly cloudy"
                    elif weather_roll < 0.9:
                        weather = "Light rain"
                    else:
                        weather = random.choice(["Overcast", "Thunderstorm", "Snow"])
                else:
                    if weather_roll < 0.5:
                        weather = "Overcast"
                    elif weather_roll < 0.8:
                        weather = "Light rain"
                    else:
                        weather = random.choice(["Partly cloudy", "Thunderstorm", "Fog"])
            
            # Update base for next iteration
            if interval == 0:
                base_temp = temperature
                base_weather = weather
                
            forecast = ForecastReading(
                timestamp=int((now + timedelta(hours=interval)).timestamp()),
                temperature_c=round(temperature, 1),
                weather_desc=weather,
                observation_time=int((now + timedelta(hours=interval)).timestamp()),
            )
            
            # Add some derived properties
            forecast.wind_speed_kmh = base.wind_speed_kmh + random.uniform(-3, 3) if base else random.uniform(5, 12)
            forecast.humidity = base.humidity + random.randint(-5, 5) if base else random.randint(45, 75)
            
            forecasts.append(forecast)
            
        return forecasts

    def _generate_and_cache_weather(self) -> None:
        """
        Generate fresh mock weather data and cache it.
        """
        self._current = self._generate_mock_current()
        self._cache_weather(self._current)
    
    def _cache_weather(self, data: WeatherReading):
        """
        Cache weather data to file.
        
        Args:
            data: WeatherReading object to cache
        """
        os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
        
        cache_data = {
            "current": data.to_dict() if data else None,
            "timestamp": time.time(),
            "provider": self._provider,
            "city": self._default_city,
        }
        
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
            
        self.last_call = time.time()

    def _get_cached_weather(self) -> Optional[Dict]:
        """
        Retrieve cached weather data if it exists and hasn't expired.
        
        Returns:
            Cached data dict or None
        """
        if not os.path.exists(self._cache_file):
            return None
            
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                age = time.time() - data.get("timestamp", 0)
                
                if age < self._cache_duration:
                    return data
        except json.JSONDecodeError:
            self._log("WARN", "Corrupt cache file. Generating fresh data.")
        except FileNotFoundError:
            pass
            
        return None

    def fetch_and_display(self) -> None:
        """
        Fetch/generate weather data and display in terminal.
        
        Checks cache first, then generates fresh mock data if needed.
        """
        self._log("INFO", f"Fetching weather data for: {self._default_city}")
        
        # Check cache first
        cached = self._get_cached_weather()
        
        if cached and cached.get("current"):
            age = time.time() - cached.get("timestamp", 0)
            
            if age < self._cache_duration:
                # Restore from cache
                self._current = WeatherReading.from_cache(cached["current"])
                self._log("INFO", f"Cache hit: Loading weather data from cache (age: {age:.0f}s)")
            else:
                # Cache expired - generate fresh data
                self._log("INFO", f"Cache expired ({age:.0f}s). Generating fresh data.")
                self._generate_and_cache_weather()
            
            self._display_current_conditions()
            self._display_forecast()
        else:
            # No cache - generate fresh mock data
            self._log("INFO", "No cached data. Generating fresh mock weather data.")
            self._generate_and_cache_weather()
            self._forecast = self._generate_hourly_forecast(hours_ahead=24, base=self._current)
            self._display_current_conditions()
            self._display_forecast()

    def fetch_and_save(self) -> Optional[str]:
        """
        Fetch weather data and save to a markdown summary file.
        
        Returns:
            Path to the saved file if successful, None otherwise
        """
        os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
        
        # Generate current and forecast data
        self._generate_and_cache_weather()
        self._forecast = self._generate_hourly_forecast(hours_ahead=24, base=self._current)
        
        # Generate markdown content
        content = self._generate_summary_content()
        
        # Write to file
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self._log("INFO", f"Saved weather summary to: {self._cache_file}")
        return self._cache_file

    def _display_current_conditions(self) -> None:
        """
        Display current weather conditions in formatted terminal output.
        """
        if not self._current:
            print("\n⚠️  No weather data available. Please check your connection.")
            return
            
        print("\n" + "=" * 70)
        print("  🌡️  Current Weather Conditions")
        print("=" * 70)
        print(f"  📍 Location: {self._default_city}, NY (EST) | Timezone: UTC")
        print(f"  🕒 Observation: {self._format_observation_time()}")
        print("")
        print("  ─" * 70)
        
        print(f"  🌡️  Temperature: {self._current.temperature_c:.1f}°C ({self._current.temperature_f:.0f}°F)")
        print(f"  💨 Feels Like:   {self._current.feels_like_c:.1f}°C ({self._current.feels_like_f:.0f}°F)")
        print("")
        print(f"  ☁️  {self._current.weather_desc} {self._get_weather_emoji(self._current.weather_desc)}")
        print(f"      Cloud Cover: {self._current.cloud_cover:.0f}%")
        print("")
        print(f"  💨 Wind:        {self._current.wind_speed_kmh:.0f} km/h ({self._current.wind_speed_mph:.1f} mph) {self._current.wind_direction}")
        print(f"  💧 Humidity:    {self._current.humidity:.0f}%")
        print(f"  📊 Pressure:   {self._current.pressure_mb:.0f} hPa")
        print(f"  👁️  Visibility: {self._current.visibility_km:.0f} km")
        print(f"  🌗 Day/Night:  {'☀️ Day' if self._current.is_day else '🌙 Night'}")
        
        print("")
        print("  ─" * 70)
        
    def _display_forecast(self, forecasts: list = None) -> None:
        """
        Display forecast readings in a clear terminal format.
        
        Args:
            forecasts: List of ForecastReading objects (optional, defaults to self._forecast)
        """
        forecast_data = forecasts if forecasts is not None else self._forecast
        
        if not forecast_data:
            print("\n⚠️  No forecast data available.")
            return
            
        print("\n" + "=" * 70)
        print("  📅 24-Hour Weather Forecast")
        print("=" * 70)
        print(f"  📍 Location: {self._default_city}")
        print("  Forecast generated every 3 hours for the next 24 hours")
        print("")
        print("  ──" * 50)
        
        for idx, reading in enumerate(forecast_data, 1):
            time_str = datetime.fromtimestamp(reading.timestamp, tz=timezone.utc).strftime("%H:00")
            is_day_str = "☀️ " if reading.weather_desc in ["Clear sky", "Partly cloudy"] else "🌙 "
            print(f"  {idx}. ⏰ {time_str} | {is_day_str}{reading.weather_desc} {self._get_weather_emoji(reading.weather_desc)} | {reading.temperature_c:.0f}°C ({reading.temperature_f:.0f}°F)")
        
        print("  ──" * 50)

    def _get_weather_emoji(self, desc: str) -> str:
        """Get emoji for a weather description."""
        return self.WEATHER_EMOJI.get(desc, "🌡️")

    def _format_observation_time(self) -> str:
        """Format observation time for display."""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _generate_summary_content(self) -> str:
        """
        Generate markdown summary content for file output.
        
        Returns:
            Formatted markdown string
        """
        lines = [
            "# Weather Report",
            "",
            f"**Location:** {self._default_city}, New York",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Provider:** {self._provider}",
            "",
            "---",
            "",
            "## 🌡️ Current Conditions",
            "",
            f"- **Temperature:** {self._current.temperature_c:.1f}°C ({self._current.temperature_f:.0f}°F)",
            f"- **Feels Like:** {self._current.feels_like_c:.1f}°C ({self._current.feels_like_f:.0f}°F)",
            f"- **Conditions:** {self._current.weather_desc}",
            f"- **Wind Speed:** {self._current.wind_speed_kmh:.0f} km/h ({self._current.wind_speed_mph:.0f} mph)",
            f"- **Humidity:** {self._current.humidity:.0f}%",
            f"- **Pressure:** {self._current.pressure_mb:.0f} hPa",
            f"- **Cloud Cover:** {self._current.cloud_cover:.0f}%",
            f"- **Visibility:** {self._current.visibility_km:.0f} km",
            f"- **Day/Night:** {'Day ☀️' if self._current.is_day else 'Night 🌙'}",
            "",
            "---",
            "",
            "## 📅 24-Hour Forecast (3-Hour Intervals)",
            "",
            "| # | Time (UTC) | Conditions | Temperature (°C) | Temperature (°F) |",
            "|──│──────────│───────────│─────────────────│─────────────────│",
        ]
        
        for idx, reading in enumerate(self._forecast[:12], 1):  # Limit to 12 readings for display
            time_str = datetime.fromtimestamp(reading.timestamp, tz=timezone.utc).strftime("%H:00")
            emoji = self.WEATHER_EMOJI.get(reading.weather_desc, "🌡️")
            lines.append(f"| {idx} | {time_str} | {reading.weather_desc} {emoji} | {reading.temperature_c:.1f} | {reading.temperature_f:.0f} |")
            
        lines.extend([
            "",
            "---",
            "",
            "*Report generated by Weather and News Dashboard*",
            f"*Observation timestamp: {self._current.observation_time}",
        ])
        
        return "\n".join(line for line in lines if line and not line.startswith("---"))
