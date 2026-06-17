# ⛈️ Weather & News Dashboard

**Dual-agent terminal dashboard: weather + news via CLI**

**Agents:**
- **Jarvis** (`lmstudio/qwen/qwen3.5-9b`) — planning & intent
- **FRIDAY** (`openai/gpt-5.5`) — execution & API calls

---

## How It Works

**Architecture:** Two-agent handoff. Jarvis interprets your request, writes a plan + prompt, spawns FRIDAY. FRIDAY executes the plan (calls APIs, runs shell commands), returns results. Jarvis formats and delivers the output.

**Flow:**
1. You type: `Jarvis: What's the weather in NYC?`
2. Jarvis parses intent → creates prompt: "Call weather API for NYC"
3. Jarvis spawns FRIDAY subagent with prompt
4. FRIDAY executes: calls Open-Meteo, gets JSON
5. FRIDAY returns data to Jarvis
6. Jarvis formats and displays:
   ```
   🌤️ NYC Weather
   Temp: 75°F (24°C)
   Conditions: Clear
   Humidity: 45%
   Wind: 12 mph SE
   ```

---

## Usage

**Start the dashboard:**
```bash
python dashboard.py
```

**Interact:**
```bash
# Weather query
Jarvis: What's the weather in Boston?

# News query
Jarvis: Show me top Hacker News stories

# Forecast
Jarvis: Forecast for London tomorrow

# Summary
Jarvis: Daily summary for 2026-06-17
```

**Environment:**
```bash
export OPENAI_API_KEY=your_key_here
# Weather API: Open-Meteo (default, no key) or OpenWeatherMap
```

---

## Features

- **Weather:** current conditions, hourly/daily forecast
- **News:** Hacker News top stories (via API)
- **Interactive menu:** 1️⃣ weather | 2️⃣ news | 3️⃣ summary | 4️⃣ location | 5️⃣ exit
- **Location persistence:** saves locations for repeat queries
- **Clean terminal output:** weather icons, styled news scores

---

## Tech Stack

- **Language:** Python 3
- **JARVIS model:** lmstudio/qwen/qwen3.5-9b (planning, intent)
- **FRIDAY model:** openai/gpt-5.5 (execution, code gen)
- **Weather API:** Open-Meteo (no key) or OpenWeatherMap
- **News API:** https://hacker-news.firebaseio.com/v0

---

## Installation

```bash
pip install requests python-dateutil pytz
pip install openmeteo beautifulsoup4 rich  # optional
```

---

## File Structure

```
data/
  models.py      # NewsItem, WeatherReading
  weather.py     # weather utils
services/
  __init__.py
  service.py     # base Service class
  news_service.py# HN API service
  weather_service.py
  summary_service.py
dashboard.py      # CLI entry point
config.py         # API keys, settings
today_summary.md  # cached summary output
dashboard.log     # app logs
```

---

## Quick Examples

**Get current weather:**
```bash
Jarvis: Weather in Chicago
```

**Top news:**
```bash
Jarvis: News
```

**Specific forecast:**
```bash
Jarvis: Forecast for Seattle 24h
```

---

## Dependencies

- `lmstudio/qwen/qwen3.5-9b` — Jarvis (planning)
- `openai/gpt-5.5` — FRIDAY (execution)
- Open-Meteo / OpenWeatherMap
- Hacker News API

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Jarvis won't spawn FRIDAY | Check model availability, token budget |
| FRIDAY timeout | Increase `exec` timeout, simplify prompt |
| No weather data | Check API key, network, location format |
| News not loading | Check HN API status, firewall |

---

## Future

- More news sources (Reddit,rss feeds)
- Voice input (whisper + TTS)
- Multi-location tracking
- Alerts (threshold-based)
- Dark mode / custom themes

---

**Built for real-time weather & news in your terminal. Powered by Jarvis + FRIDAY.**
