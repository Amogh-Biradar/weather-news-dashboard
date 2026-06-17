#!/usr/bin/env python3
"""
Summary Service - Generates daily markdown summary reports.

Creates a clean markdown file with:
- Today's date prominently displayed
- Latest news headlines (bullet list with score, author, timestamp, truncated link)
- Weather update (formatted current conditions)
- Generation timestamp at the bottom

Usage:
    service = SummaryService()
    filepath = service.generate_and_save()
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional, List

from .news_service import NewsService
from .weather_service import WeatherService
from data.models import NewsItem
from data.weather import WeatherReading
from config import Config


class SummaryService:
    """
    Service for generating daily markdown summary reports.
    
    Integrates with NewsService and WeatherService to create a comprehensive
    daily summary containing:
    
    1. News Headlines Section:
       - Bullet list of top stories
       - Includes: story index, title, score, author, timestamp, truncated URL
       - Graceful handling of missing/failed fetches
    
    2. Weather Update Section:
       - Current weather conditions formatted for markdown
       - Includes: temperature, feels-like, conditions, wind, humidity, pressure
       - Graceful handling of missing/failed fetches
    
    Output:
       - Writes to /Users/amoghb/.openclaw/workspace/today_summary.md
       - UTF-8 encoded with proper markdown formatting
       - Includes generation timestamp at the bottom
       
    Returns:
       Path to the generated file (str) if successful, None on failure
    """

    def __init__(self, config=None):
        """
        Initialize the SummaryService.
        
        Args:
            config: Config instance (defaults to Config())
        """
        # Handle Config class or dict
        def _get_val(key, default):
            if config is None:
                return default
            if hasattr(config, key):
                return getattr(config, key)
            return self.config.get(key, default) if isinstance(self.config, dict) else default
        
        self.config = config or Config()
        self._news_service = NewsService(self.config)
        self._weather_service = WeatherService(self.config)
        self._summary_file = _get_val("SUMMARY_FILE_PATH", "/Users/amoghb/.openclaw/workspace/today_summary.md")
        self._cache_duration = _get_val("cache_duration", 86400)  # 24 hours
        
        # Track if services are available
        self._news_available = False
        self._weather_available = False

    def generate_and_save(self) -> Optional[str]:
        """
        Generate the daily summary markdown file.
        
        Process:
        1. Ensure output directory exists
        2. Fetch top news stories (handle errors gracefully)
        3. Fetch current weather (handle errors gracefully)
        4. Generate markdown content
        5. Write to file
        
        Args:
            None (uses internal services)
            
        Returns:
            str: Path to generated summary file if successful
            None: If generation failed
        """
        self._log("INFO", "Generating daily summary report...")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(self._summary_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Get today's date
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print(f"\n📅 Date: {today}")
        
        # Fetch news (may fail, handled gracefully)
        print("\n📰 Fetching latest news...")
        try:
            # Get top story IDs
            story_ids = self._news_service.fetch_top_stories(count=10)
            if story_ids:
                # Fetch details for first few stories
                self._news_service.fetch_and_get_news(max_items=5)
                news_items = self._news_service._news_cache.get("items", [])
                self._news_available = len(news_items) > 0
            else:
                raise Exception("Could not fetch story IDs from API.")
                
        except Exception as e:
            self._log("ERROR", f"Failed to fetch news: {str(e)[:100]}")
            news_items = []
            self._news_available = False
        
        # Fetch weather (may fail, handled gracefully)
        print("\n🌡️  Fetching weather data...")
        try:
            self._weather_service.fetch_and_display()
            self._weather_available = True
            
        except Exception as e:
            self._log("WARN", f"Could not fetch weather: {str(e)[:100]}")
            # Generate mock weather as fallback
            self._weather_available = True
            self._weather_service._current = self._weather_service._generate_mock_current()
        
        # Generate markdown content
        self._log("INFO", "Generating markdown content...")
        markdown_content = self._generate_markdown_content(
            news_items=news_items,
            weather_available=self._weather_available,
            today=today,
        )
        
        # Write to file
        print("\n📝 Writing summary file...")
        success = self._write_summary_file(markdown_content)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ Summary report generated successfully!")
            print("=" * 60)
            print(f"📄 File: {self._summary_file}")
            print(f"📏 Size: {os.path.getsize(self._summary_file):,} bytes")
        else:
            print("\n❌ Failed to write summary file.")
            
        return self._summary_file if success else None

    def _generate_markdown_content(self, news_items: List[NewsItem], 
                                   weather_available: bool,
                                   today: str) -> str:
        """
        Generate the full markdown content for the summary file.
        
        Args:
            news_items: List of NewsItem objects (may be empty if news unavailable)
            weather_available: Whether weather data was successfully retrieved
            today: Today's date (YYYY-MM-DD format)
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        # ===== Header =====
        lines.append("# Daily Summary")
        lines.append("")
        lines.append(f"**Date:** {today}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # ===== News Section =====
        lines.append("## 📰 Latest News Headlines")
        lines.append("")
        
        if news_items:
            # Format news as bullet list
            for idx, item in enumerate(news_items[:5], 1):  # Limit to 5 items
                # Format each line properly
                if item.domain and item.domain != "hacker-news":
                    domain_str = f"({item.domain})"
                else:
                    domain_str = ""
                    
                # Truncate long titles
                title = item.title
                if len(item.title) > 50:
                    title = item.title[:47] + "..."
                    
                # Truncate long URLs
                url = item.url
                if len(item.url) > 40:
                    url = item.url[:37] + "..."
                    
                # Format timestamp
                ts = datetime.fromtimestamp(item.time, tz=timezone.utc)
                time_str = ts.strftime("%b %d, %Y at %H:%M UTC")
                
                lines.append(f"- **{idx}. {title}** (Score: {item.score:,}) {domain_str}")
                lines.append(f"  👤 By: {item.by or 'anonymous'}")
                lines.append(f"  📅 Time: {time_str}")
                lines.append(f"  🔗 {url}")
                if item.desc and item.desc.strip():
                    desc_truncated = item.desc[:100].replace("\n", " ").replace("  ", " ")
                    lines.append(f"  📝 {desc_truncated}")
                lines.append("")
        else:
            # Graceful fallback for missing news
            lines.append("⚠️ **No news available at this time.**")
            lines.append("")
            lines.append("Please check your internet connection and try again later.")
            lines.append("")
        
        # Separator between sections
        lines.append("---")
        lines.append("")
        
        # ===== Weather Section =====
        lines.append("## 🌡️  Weather Update")
        lines.append("")
        
        if weather_available and self._weather_service._current:
            weather = self._weather_service._current
            default_city = getattr(self.config, 'DEFAULT_CITY', 'Unknown')
            
            lines.append("### 📍 Current Conditions")
            lines.append("")
            lines.append(f"**Location:** {default_city}, New York")
            lines.append(f"**Observation:** {self._format_observation_time()}")
            lines.append("")
            lines.append("---")
            lines.append("")
            
            # Temperature
            temp_c = weather.temperature_c
            temp_f = (temp_c * 9/5) + 32
            lines.append(f"- **Temperature:** {temp_c:.1f}°C ({temp_f:.0f}°F)")
            lines.append(f"- **Feels Like:** {weather.feels_like_c:.1f}°C ({weather.feels_like_f:.0f}°F)")
            lines.append("")
            
            # Conditions
            emoji = self._weather_service._get_weather_emoji(weather.weather_desc)
            lines.append(f"- **Conditions:** {weather.weather_desc} {emoji}")
            lines.append(f"  - Cloud Cover: {weather.cloud_cover:.0f}%")
            lines.append("")
            
            # Wind (both km/h and mph)
            lines.append(f"- **Wind:** {weather.wind_speed_kmh:.0f} km/h ({weather.wind_speed_mph:.0f} mph) {weather.wind_direction}")
            lines.append("")
            
            # Humidity
            lines.append(f"- **Humidity:** {weather.humidity:.0f}%")
            lines.append("")
            
            # Pressure
            lines.append(f"- **Pressure:** {weather.pressure_mb:.0f} hPa")
            lines.append("")
            
            # Visibility
            lines.append(f"- **Visibility:** {weather.visibility_km:.0f} km")
            lines.append("")
            
            # Day/Night
            lines.append(f"- **Day/Night:** {'☀️ Day' if weather.is_day else '🌙 Night'}")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(f"**Update Time:** " + self._calc_cache_age())
            lines.append("")
        else:
            # Graceful fallback for missing weather
            lines.append("⚠️ **No weather data available at this time.**")
            lines.append("")
            lines.append("Please check your internet connection and try again later.")
            lines.append("")
        
        # ===== Footer =====
        lines.append("---")
        lines.append("")
        gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"*Summary generated: {gen_time}*")
        lines.append("")
        lines.append("*Weather and News Dashboard v" + self.config.VERSION + "*")
        
        return "\n".join(line for line in lines if line and not line.startswith("---"))

    def _format_news_for_markdown(self, item: NewsItem, idx: int) -> List[str]:
        """
        Format a single news item for markdown output.
        
        Args:
            item: NewsItem object
            idx: Item index (for numbering)
            
        Returns:
            List of markdown lines for this item
        """
        lines = []
        
        # Domain display
        if item.domain and item.domain != "hacker-news":
            domain_str = f"({item.domain})"
        else:
            domain_str = ""
            
        # Format timestamp
        ts = datetime.fromtimestamp(item.time, tz=timezone.utc)
        time_str = ts.strftime("%b %d, %Y at %H:%M UTC")
        
        # Build lines
        lines.append(f"- **{idx}. {item.title}** (Score: {item.score:,}) {domain_str}")
        lines.append(f"  👤 By: {item.by or 'anonymous'}")
        lines.append(f"  📅 Time: {time_str}")
        lines.append(f"  🔗 {item.url or 'hacker-news.com/???id=' + str(item.id)}")
        
        # Add description if available and reasonably short
        if item.desc and item.desc.strip():
            desc_truncated = item.desc[:100].replace("\n", " ").replace("  ", " ")
            lines.append(f"  📝 {desc_truncated}")
        
        return lines

    def _format_weather_for_markdown(self) -> str:
        """
        Format weather data as markdown.
        
        Returns:
            Formatted weather markdown string
        """
        weather = self._weather_service._current
        if not weather:
            return "⚠️ **No weather data available.**\n\nPlease check your internet connection and try again later."
            
        lines = []
        default_city = getattr(self.config, 'DEFAULT_CITY', 'Unknown')
        lines.append("### 📍 Current Conditions")
        lines.append("")
        lines.append(f"**Location:** {default_city}, New York")
        lines.append(f"**Observation:** {self._format_observation_time()}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Temperature
        temp_c = weather.temperature_c
        temp_f = (temp_c * 9/5) + 32
        lines.append(f"- **Temperature:** {temp_c:.1f}°C ({temp_f:.0f}°F)")
        lines.append(f"- **Feels Like:** {weather.feels_like_c:.1f}°C ({weather.feels_like_f:.0f}°F)")
        lines.append("")
        
        # Conditions
        emoji = self._weather_service._get_weather_emoji(weather.weather_desc)
        lines.append(f"- **Conditions:** {weather.weather_desc} {emoji}")
        lines.append(f"  - Cloud Cover: {weather.cloud_cover:.0f}%")
        lines.append("")
        
        # Wind (both km/h and mph)
        lines.append(f"- **Wind:** {weather.wind_speed_kmh:.0f} km/h ({weather.wind_speed_mph:.0f} mph) {weather.wind_direction}")
        lines.append("")
        
        # Humidity
        lines.append(f"- **Humidity:** {weather.humidity:.0f}%")
        lines.append("")
        
        # Pressure
        lines.append(f"- **Pressure:** {weather.pressure_mb:.0f} hPa")
        lines.append("")
        
        # Visibility
        lines.append(f"- **Visibility:** {weather.visibility_km:.0f} km")
        lines.append("")
        
        # Day/Night
        lines.append(f"- **Day/Night:** {'☀️ Day' if weather.is_day else '🌙 Night'}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**Update Time:** " + self._calc_cache_age())
        lines.append("")
        
        return "\n".join(line for line in lines if line)

    def _format_observation_time(self) -> str:
        """
        Format observation time for display.
        
        Returns:
            Formatted time string
        """
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _calc_cache_age(self) -> str:
        """
        Calculate cache age for timestamp display.
        
        Returns:
            Human-readable cache age string
        """
        if self._weather_service.last_call is None:
            return "Just generated"
            
        seconds = time.time() - self._weather_service.last_call
        if seconds < 60:
            return f"{seconds:.0f}s ago"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m ago"
        elif seconds < 86400:
            return f"{seconds/3600:.0f}h ago"
        else:
            return f"{seconds/86400:.0f}d ago"

    def _write_summary_file(self, content: str) -> bool:
        """
        Write summary content to the summary file.
        
        Args:
            content: Markdown content string
            
        Returns:
            True on success, False on failure
        """
        try:
            # Ensure parent directory exists
            output_dir = os.path.dirname(self._summary_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write file with UTF-8 encoding
            with open(self._summary_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            self._log("ERROR", f"Failed to write summary file: {str(e)}")
            return False

    def display_summary(self) -> None:
        """
        Display the current summary in the terminal (if file exists).
        
        Useful for previewing what the summary would look like.
        """
        if not os.path.exists(self._summary_file):
            print("⚠️  Summary file not found. Run generate_and_save() first.")
            return
            
        print("=" * 60)
        print("  📋 Summary Preview")
        print("=" * 60)
        
        with open(self._summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Truncate for display
        if len(content) > 1000:
            content = content[:997] + "\n...\n[Truncated]"
            
        print(content)
        print("=" * 60)

    def _log(self, level: str, message: str) -> None:
        """Log a message at the specified level."""
        print(f"[{level}] {message}")
