#!/usr/bin/env python3
"""
Configuration blueprint for Weather and News Dashboard
All settings, API keys, and service configurations.
"""


class Config:
    """
    Central configuration class for the dashboard.
    Contains service settings, API credentials, and runtime configs.
    """

    # ===== App Settings =====
    APP_NAME = "Weather and News Dashboard"
    VERSION = "0.1.0"
    DEFAULT_REFRESH_RATE = 60  # seconds
    MAX_NEWS_ITEMS = 10
    MAX_WEATHER_READINGS = 5

    # ===== Hacker News API =====
    HNEWS_API_URL = "https://hacker-news.firebaseio.com/v0"
    TOP_STORY_PATH = "/topstories.json"
    NEWSTORY_PATH = "/item/"  # for individual stories
    DEFAULT_NEWS_COUNT = 5
    MAX_NEWS_COUNT = 10

    # ===== Weather Service =====
    # Default to open-meteo for no-API-key requirement
    WEATHER_PROVIDER = "open-meteo"  # or "openweathermap"
    WEATHER_API_KEY = None  # Optional: for OpenWeatherMap
    WEATHER_LAT = None     # Optional: latitude
    WEATHER_LON = None     # Optional: longitude
    DEFAULT_CITY = "New York"  # fallback for open-meteo uses geocoding

    # OpenWeatherMap specific (if using)
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    OPENWEATHER_DEGREE_UNITS = "metric"

    # ===== File I/O =====
    SUMMARY_FILE_PATH = "/Users/amoghb/.openclaw/workspace/today_summary.md"
    DATA_CACHE_FILE = "/Users/amoghb/.openclaw/workspace/news_cache.json"
    MAX_CACHE_AGE_SECONDS = 3600  # 1 hour

    # ===== Formatting =====
    TERMINAL_WIDTH = 80  # typical modern terminal width
    DATE_FORMAT = "%Y-%m-%d %H:%M"
    NEWS_ITEM_TEMPLATE = """
📰 [{index}] {title}
   Source: {domain} | Time: {time} | Popularity: {popularity}
   Link: {url}
"""
    WEATHER_ITEM_TEMPLATE = """
🌡️ Current Conditions
   Temperature: {temp_c}°C ({temp_f}°F)
   Feels Like: {feels_like_c}°C ({feels_like_f}°F)
   Description: {weather_desc}
   Wind: {wind_speed} km/h ({wind_speed_mph} mph)
   Humidity: {humidity}%
   {condition_desc}
"""

    # ===== Error Handling =====
    ERROR_PREFIX = "⚠️  "
    RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5

    # ===== Logging =====
    LOG_LEVEL = "INFO"
    LOG_FILE = "/Users/amoghb/.openclaw/workspace/dashboard.log"

    # ===== Dependencies =====
    REQUIRED_DEPS = [
        "requests",
        "python-dateutil",
        "pytz",
    ]
    OPTIONAL_DEPS = [
        "openmeteo",
        "beautifulsoup4",
        "rich",
    ]

    @staticmethod
    def validate():
        """Validate required config and return tuple of (is_valid, issues)."""
        issues = []
        return len(issues) == 0, issues
    
    def get(self, key, default=None):
        """Dict-style getter for compatibility."""
        return getattr(self, key, default)
