# ⛈️ Weather & News Dashboard

A simple terminal dashboard that shows weather and Hacker News stories.

## About

I built this app to check weather and read news right from the terminal without opening a browser. It uses Open-Meteo for weather (free, no API key) and Hacker News API for news.

## Quick Start

```bash
python dashboard.py
```

Type commands when prompted, like:
```
Jarvis: Weather in NYC
Jarvis: News
```

## Features

- 🌤️ Current weather with icons and temperature
- 📰 Latest Hacker News stories with points
- Interactive menu to switch between weather and news
- Saves your locations so you don't have to type them repeatedly

## Installation

```bash
pip install requests python-dateutil pytz
python dashboard.py
```

## How It Was Built

I used the OpenClaw two-agent system to build this:

- **Jarvis** (Qwen 3.5-9B local): planned everything, decided on the architecture, orchestrated the work
- **FRIDAY** (GPT-5.5 via OpenAI): wrote all the actual code, handled implementation, debugging

The app itself doesn't have any AI features - it's just a regular Python CLI. The agents were only used to build it.

## API Keys

No key needed - I use Open-Meteo for weather and Hacker News API for news (both free).

If you want to use OpenWeatherMap instead, add your API key to `config.py`:
```python
API_KEY = "your_key_here"
```

## License

MIT - feel free to use and modify.
