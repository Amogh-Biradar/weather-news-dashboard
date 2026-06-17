#!/usr/bin/env python3
"""
Weather data models for Weather and News Dashboard.
Defines WeatherReading, ForecastReading, and DailySummary classes.
"""


class WeatherReading:
    """
    Represents current weather conditions at a location.
    """
    def __init__(
        self,
        temperature_c: float = 0.0,
        temperature_f: float | None = None,
        feels_like_c: float | None = None,
        feels_like_f: float | None = None,
        weather_desc: str = "Clear sky",
        wind_speed_kmh: float | None = None,
        wind_speed_mph: float | None = None,
        wind_direction: str | None = None,
        humidity: float | None = None,
        pressure_mb: float | None = None,
        visibility_km: float | None = None,
        cloud_cover: float | None = None,
        is_day: bool = True,
        observation_time: int | None = None,
        timezone: str | None = "UTC",
    ):
        self.temperature_c = temperature_c
        self.temperature_f = temperature_f
        self.feels_like_c = feels_like_c
        self.feels_like_f = feels_like_f
        self.weather_desc = weather_desc
        self.wind_speed_kmh = wind_speed_kmh
        self.wind_speed_mph = wind_speed_mph
        self.wind_direction = wind_direction
        self.humidity = humidity
        self.pressure_mb = pressure_mb
        self.visibility_km = visibility_km
        self.cloud_cover = cloud_cover
        self.is_day = is_day
        self.timezone = "UTC"
        self.observation_time = None

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "temperature_c": self.temperature_c,
            "temperature_f": self.temperature_f,
            "feels_like_c": self.feels_like_c,
            "feels_like_f": self.feels_like_f,
            "weather_desc": self.weather_desc,
            "wind_speed_kmh": self.wind_speed_kmh,
            "wind_speed_mph": self.wind_speed_mph,
            "wind_direction": self.wind_direction,
            "humidity": self.humidity,
            "pressure_mb": self.pressure_mb,
            "visibility_km": self.visibility_km,
            "cloud_cover": self.cloud_cover,
            "is_day": self.is_day,
            "timezone": self.timezone,
            "observation_time": self.observation_time,
        }
        
    @classmethod
    def from_cache(cls, data: dict) -> 'WeatherReading':
        """
        Create a WeatherReading instance from cached data.
        
        Args:
            data: Cached weather data dictionary
            
        Returns:
            WeatherReading instance
        """
        return cls(
            temperature_c=data.get("temperature_c", 0.0),
            temperature_f=data.get("temperature_f"),
            feels_like_c=data.get("feels_like_c"),
            feels_like_f=data.get("feels_like_f"),
            weather_desc=data.get("weather_desc", "Clear sky"),
            wind_speed_kmh=data.get("wind_speed_kmh"),
            wind_speed_mph=data.get("wind_speed_mph"),
            wind_direction=data.get("wind_direction"),
            humidity=data.get("humidity"),
            pressure_mb=data.get("pressure_mb"),
            visibility_km=data.get("visibility_km"),
            cloud_cover=data.get("cloud_cover"),
            is_day=data.get("is_day", True),
            observation_time=data.get("observation_time"),
            timezone=data.get("timezone", "UTC"),
        )

    def __repr__(self):
        return f"WeatherReading(temp={self.temperature_c}°C, desc='{self.weather_desc}')"


class ForecastReading:
    """
    Represents a weather forecast reading at a specific time.
    """
    def __init__(
        self,
        timestamp: int,  # Unix timestamp
        temperature_c: float | None = None,
        temperature_f: float | None = None,
        weather_desc: str | None = None,
        wind_speed_kmh: float | None = None,
        humidity: float | None = None,
        observation_time: int | None = None,
        timezone: str | None = "UTC",
    ):
        self.timestamp = timestamp
        self.temperature_c = temperature_c
        self.temperature_f = temperature_f
        self.weather_desc = weather_desc
        self.wind_speed_kmh = wind_speed_kmh
        self.humidity = humidity
        self.observation_time = None

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "temperature_c": self.temperature_c,
            "temperature_f": self.temperature_f,
            "weather_desc": self.weather_desc,
            "wind_speed_kmh": self.wind_speed_kmh,
            "humidity": self.humidity,
            "observation_time": self.observation_time,
        }

    def __repr__(self):
        return f"ForecastReading(time={self.timestamp})"


class DailySummary:
    """
    Represents a daily weather summary with current and forecast data.
    """
    def __init__(
        self,
        date: str,  # YYYY-MM-DD string
        current: WeatherReading | None = None,
        forecasts: list[ForecastReading] | None = None,
        air_quality: dict | None = None,
        sunrise: int | None = None,
        sunset: int | None = None,
        moon_phase: str | None = None,
    ):
        self.date = date
        self.current = current
        self.forecasts = forecasts or []
        self.air_quality = air_quality
        self.sunrise = sunrise
        self.sunset = sunset
        self.moon_phase = moon_phase

    def add_forecast(self, forecast: ForecastReading):
        """Add a forecast reading to the summary."""
        self.forecasts.append(forecast)

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "date": self.date,
            "current": self.current.to_dict() if self.current else None,
            "forecasts": [f.to_dict() for f in self.forecasts],
            "air_quality": self.air_quality,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "moon_phase": self.moon_phase,
        }

    def __repr__(self):
        return f"DailySummary(date={self.date}, current={self.current})"
