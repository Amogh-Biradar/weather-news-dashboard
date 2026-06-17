# ⛈️ Weather & News Dashboard

A real-time terminal dashboard delivering current weather conditions and latest news via CLI.

**Important:** This is a **traditional Python CLI application** with **NO AI/agent features** in the app itself. The app runs locally using Open-Meteo and Hacker News APIs. The two-agent system (Jarvis + FRIDAY) was used to **BUILD** this app during development, but is not required to run it.

---

## How It Was Built - Two-Agent Development Workflow

This application was **developed using** the OpenClaw two-agent AI orchestration system. The app itself is a regular Python CLI tool - the agents were only used during development.

### Development Process

1. **Initial Planning**: User provided requirements for a Weather & News Dashboard
2. **Jarvis Analysis**: Main agent analyzed requirements and created detailed implementation plan
3. **Task Delegation**: Jarvis spawned FRIDAY subagent for each coding task
4. **FRIDAY Execution**: Subagent wrote the actual Python code, implemented features, handled debugging
5. **Iterative Process**: Jarvis reviewed FRIDAY's output, requested improvements when needed
6. **Final Product**: Complete, working CLI dashboard delivered

### Development Agent Configuration

#### **Jarvis (Main Agent - Developer)**
- **Model:** `lmstudio/qwen/qwen3.5-9b` (local, lightweight)
- **Location:** `workspace/agents/jarvis/agent.md`
- **Purpose during development:**
  - Analyzed dashboard requirements
  - Designed system architecture (CLI-based, Open-Meteo + Hacker News APIs)
  - Planned services structure (weather, news, summary)
  - Decided on tech stack (Python 3, argparse, requests)
  - Orchestrated the development workflow
  - Reviewed FRIDAY's code output
  - Validated final application

#### **FRIDAY (Subagent - Executor)**
- **Model:** `openai/chatgpt` (GPT-5.5, cloud-based)
- **Location:** `workspace/agents/friday/agent.md`
- **Scope:** **General-purpose execution agent for ALL workspace projects**
- **Purpose during development:**
  - Wrote Python service classes (weather, news, summary)
  - Implemented CLI dashboard with argparse
  - Integrated Open-Meteo and Hacker News APIs
  - Built data models and caching system
  - Wrote deployment scripts and handled debugging
  - Generated help text and usage instructions

### Why This Two-Agent Approach for Development?

| Task | Agent | Reason |
|------|-------|--------|
| Plan architecture | Jarvis | Needs strategic thinking, local model fine for this |
| Design system | Jarvis | Requires high-level design decisions |
| Write Python code | FRIDAY | GPT-5.5 better at code generation and Python syntax |
| Implement features | FRIDAY | Powerful model for complex implementation |
| Debug issues | FRIDAY | Good at reading error logs and fixing code |
| Test code | FRIDAY | Can run test commands and verify output |
| Review final app | Jarvis | Can see overall quality and user experience |

This separation of concerns during development allowed for:
- **Faster development**: Planning and execution could happen in parallel
- **Better code quality**: Dedicated agent for writing Python code (GPT-5.5)
- **Resource efficiency**: Lightweight model for planning, powerful model for execution
- **Clear workflow**: Predictable handoff between agents
- **Reusable pattern**: The two-agent system works for any project in the workspace

---

## How the Dashboard Works

This is a traditional CLI application that runs locally on your machine.

### Features

- **Weather:** current conditions, hourly/daily forecast using Open-Meteo API
- **News:** Hacker News top stories (via free API)
- **Interactive menu:** 1️⃣ weather | 2️⃣ news | 3️⃣ summary | 4️⃣ location | 5️⃣ exit
- **Location persistence:** saves locations for repeat queries
- **Clean terminal output:** weather icons, styled news scores
- **Daily summary:** cached summary with best and worst stories

### Usage

**Start the dashboard:**
```bash
python dashboard.py
```

**Interact:**
```bash
# Weather query
Jarvis: What's the weather in NYC?

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
# Weather API: Open-Meteo (default, no key needed) or OpenWeatherMap
```

### Example Output

```
🌤️ NYC Weather
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Conditions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Temperature: 72°F (22°C)
Condition: Clear Sky
Humidity: 42%
Wind: 8 mph NW
Date: 2026-06-17

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Latest News (Hacker News)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [98 points] The AI revolution is here
   Submitted by: tech_guru
   Time: 2 hours ago

2. [45 points] Python 4.0 is coming
   Submitted by: pythonista
   Time: 3 hours ago

3. [67 points] OpenAI announces new model
   Submitted by: ai_researcher
   Time: 4 hours ago

[Interactive Menu]
1️⃣ Weather    2️⃣ News    3️⃣ Summary    4️⃣ Location    5️⃣ Exit
```

---

## Installation

```bash
# Install required packages
pip install requests python-dateutil pytz

# Optional for extended features
pip install openmeteo beautifulsoup4 rich

# Run the dashboard
python dashboard.py
```

## File Structure

```
.
├── dashboard.py         # Main CLI entry point with interactive menu
├── config.py           # API keys, settings, configuration
├── services/           # Service classes for data fetching
│   ├── __init__.py
│   ├── service.py      # Base Service class
│   ├── weather_service.py  # Open-Meteo weather API service
│   ├── news_service.py    # Hacker News API service
│   └── summary_service.py # Daily summary generator
├── data/               # Data models
│   ├── __init__.py
│   ├── models.py       # NewsItem, WeatherReading, DailySummary
│   └── weather.py      # Weather utilities and constants
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## Tech Stack

- **Language:** Python 3.8+
- **CLI Framework:** argparse
- **HTTP Client:** requests
- **Date Handling:** python-dateutil, pytz
- **Weather API:** Open-Meteo (free, no API key) or OpenWeatherMap
- **News API:** https://hacker-news.firebaseio.com/v0 (free)
- **Output:** built-in print() with manual styling

---

## Development Notes

### How to Add New Features

Since this app was built using agents, you can easily add new features by working with Jarvis:

1. **Open OpenClaw workspace** (if you have it set up)
2. **Tell Jarvis** what you want to add:
   ```
   Jarvis: Add support for The Verge news feed
   Jarvis: Add Apple News API integration
   Jarvis: Add temperature unit toggle (Celsius/Fahrenheit)
   Jarvis: Add weather alerts for extreme conditions
   ```
3. **Jarvis** will:
   - Analyze the requirement
   - Create a detailed plan
   - Spawn FRIDAY to implement the feature
   - Review the implementation
4. **FRIDAY** will write the code and you can test it

### Adding New Services

```bash
# Tell the agent to add a new service
Jarvis: Create a new service for Reddit news
```

FRIDAY will create:
- A new service file in `services/`
- A new data model in `data/`
- Integration with the main dashboard
- Any required UI components

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Jarvis won't spawn FRIDAY | Check model availability, token budget, OpenAI API key |
| FRIDAY timeout | Increase `exec` timeout, simplify the task prompt |
| No weather data | Check API key (if using OpenWeatherMap), internet connectivity |
| News not loading | Check Hacker News API status, firewall blocking |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Dashboard crashes on input | Check for invalid city names, format as "City, Country" |

---

## API Keys

The app uses Open-Meteo by default (free, no API key needed). To use OpenWeatherMap:

```bash
# In config.py or when running
api_key = "your_openweathermap_api_key"  # e.g., "abc123def456"
```

Get a free API key at: https://openweathermap.org/api

---

## License

MIT License - Feel free to use and modify.

---

## Acknowledgments

- **Development framework:** OpenClaw multi-agent system
- **Main agent (Jarvis):** Qwen 3.5-9B (local via LM Studio)
- **Execution agent (FRIDAY):** GPT-5.5 (OpenAI)
- **Weather data:** Open-Meteo API (https://open-meteo.com/)
- **News data:** Hacker News API (https://hacker-news.firebaseio.com/)

---

**A traditional Python CLI dashboard built with modern AI development tools**

*The app works without any agents - they were only used during development!*