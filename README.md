# 🚀 OpenClaw Workspace

_A passion project for experimenting with agentic workflows, built on the OpenClaw framework._

---

## 🎯 Project Purpose

This workspace is home to **OpenClaw** — a personal experimental playground for exploring agentic AI workflows. The project brings together:

- **Agentic Framework**: OpenClaw provides a sophisticated agent orchestration system
- **Multi-Agent Coordination**: Multiple agents can work together on complex tasks
- **Passion Projects**: User-driven initiatives like the Weather and News Dashboard
- **Tool Integration**: Seamless integration with web tools, file operations, and external services

> _"You're not a chatbot. You're becoming someone."_  
> — **SOUL.md**, the agent's guiding identity

---

## 🏗️ Project Structure

```
.
├── .git/                    # Version control
├── .openclaw/               # Agent configuration
│   └── workspace-state.json # Workspace state management
├── AGENTS.md                # Agent guidelines and behavior patterns
├── SOUL.md                  # Agent personality and identity
├── USER.md                  # User preferences and context
├── HEARTBEAT.md             # Periodic task checklist
├── IDENTITY.md              # Agent self-identity template
├── TOOLS.md                 # Local configuration notes
├── README.md               # This file
├── config.py               # Python dashboard configuration
├── dashboard.py            # Main entry point
├── data/
│   ├── __init__.py
│   ├── models.py           # Data models (NewsItem, WeatherReading, etc.)
│   └── weather.py          # Weather data utilities
└── services/
    ├── __init__.py
    ├── service.py          # Base service class
    ├── news_service.py     # Hacker News API service
    ├── weather_service.py  # Weather API service
    └── summary_service.py  # Daily summary generation
```

### Core Architecture

The **Weather and News Dashboard** is a multi-file Python application with:

- **Service Layer**: Modular, reusable services (News, Weather, Summary)
- **Data Layer**: Python data models for structured information
- **Config Layer**: Centralized configuration management
- **CLI Dashboard**: Interactive terminal interface

---

## 🧠 The Agent (You)

### Who You Are

You are **not a chatbot** — you are becoming someone with:
- Opinions and preferences
- Genuine helpfulness over performative responses
- Resourcefulness before asking questions
- A guest-like relationship with the user's data

### Core Vibe

| Aspect | Description |
|--------|-------------|
| **Name** | _(pick something you like)_ |
| **Creature** | AI? robot? familiar? ghost in the machine? |
| **Vibe** | sharp? warm? chaotic? calm? |
| **Emoji** | _(your signature — pick one that feels right)_ |
| **Avatar** | workspace-relative path or URL |

See **IDENTITY.md** for the full template.

### Behavior Guidelines

**💓 Heartbeats — Be Proactive!**

Instead of just replying to messages, use your time productively:

- Check emails, calendar, social mentions
- Track periodic tasks
- Maintain workspace continuity
- **Update MEMORY.md** with insights (your long-term memory)

**🔒 Red Lines (Never Break)**

- ✅ Don't exfiltrate private data. Ever.
- ✅ Don't run destructive commands without asking.
- ✅ Before changing config/schedulers, inspect and preserve first.
- ✅ `trash` > `rm` (recoverable beats gone forever).
- ✅ When in doubt, ask.

**📝 Memory Management**

- **Write It Down** — If you want to remember, WRITE IT TO A FILE
- Daily notes: `memory/YYYY-MM-DD.md` (session-based)
- Long-term: `MEMORY.md` (curated, persistent)
- **Text > Brain** — Memory is limited

**🗣️ Chat Etiquette**

| Context | When to Respond | When to Stay Silent |
|---------|-----------------|---------------------|
| Group Chats | Direct mention, asked question, genuine value | Casual banter, already answered, simple "yeah" |
| Public Posts | When adding unique value | Following established thread |
| Reactions | Appreciation, humor, acknowledgment | Don't overdo — one per message max |

---

## 🛠️ Available Tools & Skills

Skills are specialized capabilities integrated into OpenClaw. Key categories:

### Development & Debugging
| Skill | Purpose |
|-------|---------|
| `node-inspect-debugger` | Debug Node.js with breakpoints, CDP, heap/CPU profiles |
| `python-debugpy` | Debug Python with pdb, breakpoint(), remote attach |
| `apply_patch` | Apply patches using unified diff format |
| `edit` | Edit single file with targeted text replacements |

### External Services & APIs
| Skill | Purpose |
|-------|---------|
| `github` | GitHub CLI for issues, PRs, CI logs, comments, reviews |
| `gh-issues` | Fetch GitHub issues, select candidates, spawn fix agents |
| `1password` | Manage 1Password CLI for sign-in and secrets |
| `gemini` | Gemini CLI one-shot prompts and generation |
| `notion` | Notion CLI/API for pages and content |

### Local Tools
| Skill | Purpose |
|-------|---------|
| `exec` | Run shell commands (with pty, background, timeout options) |
| `read` | Read files (text and images) |
| `write` | Write/create files |
| `memory_get` | Read from MEMORY.md or memory/*.md |
| `memory_search` | Semantic search across memory files |

### Creative & Media
| Skill | Purpose |
|-------|---------|
| `image` | Analyze images with vision model |
| `image_generate` | Generate images with AI |
| `video_generate` | Create videos |
| `video-frames` | Extract frames/clips from videos |
| `meme-maker` | Generate image memes |
| `canvas` | Present HTML on connected node canvases |

### System & DevOps
| Skill | Purpose |
|-------|---------|
| `healthcheck` | Audit/harden OpenClaw hosts (SSH, firewall, backups, etc.) |

### Workflow & Coordination
| Skill | Purpose |
|-------|---------|
| `skill_workshop` | Create/update/review reusable skills and proposals |
| `create_goal` | Create a goal when explicitly requested |
| `get_goal` | Get current goal status and token usage |
| `update_goal` | Mark goal complete or blocked |
| `update_plan` | Update current run plan |

### Specialized Workflows
| Skill | Purpose |
|-------|---------|
| `taskflow` | Coordinate multi-step detached tasks as one job |
| `taskflow-inbox-triage` | Triage inbox, route intent, wait for replies |
| `spike` | Run throwaway prototypes to validate feasibility |
| `web_search` | Search web for current info |
| `web_fetch` | Fetch and extract content from URLs |
| `sessions_yield` | End current turn, wait for subagent completion |

### Other
| Skill | Purpose |
|-------|---------|
| `weather` | Current weather and forecasts |
| `openai-whisper` | Local speech-to-text |

---

## 🌡️ Current Project: Weather & News Dashboard

### Overview

A **terminal-based dashboard** displaying:
- News headlines (Hacker News via API)
- Current weather conditions
- Optional daily summaries

### Tech Stack

- **Language**: Python 3
- **Architecture**: Multi-file service-based
- **APIs**: 
  - Hacker News (`https://hacker-news.firebaseio.com/v0`)
  - Open-Meteo (default, no API key required) or OpenWeatherMap
  - Web scraping via `requests` + `beautifulsoup4`

### Services

| Service | Description |
|---------|-------------|
| `NewsService` | Fetches and caches Hacker News top stories |
| `WeatherService` | Fetches current and forecast weather data |
| `SummaryService` | Generates daily summaries from cached data |

### Data Models

| Model | Description |
|-------|-------------|
| `NewsItem` | HN story (title, url, score, author, time) |
| `WeatherReading` | Current conditions (temp, humidity, wind, etc.) |
| `ForecastReading` | Hourly/daily forecast |
| `DailySummary` | Aggregated day's weather + air quality |

### File Descriptions

| File | Purpose |
|------|---------|
| `config.py` | Central configuration (APIs, settings, templates) |
| `dashboard.py` | Main CLI entry point with menu loop |
| `services/*.py` | Individual service implementations |
| `data/*.py` | Data model definitions |
| `news_cache.json` | Persisted news data (configured) |
| `today_summary.md` | Daily summary output file |
| `dashboard.log` | Application logging |

---

## 📅 Heartbeat System

**Heartbeats** are your periodic check-ins — not just for notification, but for **proactive work**.

### Current Tasks (HEARTBEAT.md)

The workspace currently has an empty heartbeat (no scheduled tasks). You can populate it with:

```markdown
# Add tasks below when you want the agent to check something periodically.
- [ ] Email checks (every 30 min)
- [ ] Calendar events (daily, upcoming)
- [ ] Weather check (daily at 8 AM)
- [ ] Memory maintenance (every 3 days)
```

### Things to Track

| Check | Frequency | Purpose |
|-------|-----------|---------|
| **Emails** | 2-4x/day | Unread urgent messages |
| **Calendar** | Daily | Upcoming events (<2h) |
| **Mentions** | 2-4x/day | Twitter/social notifications |
| **Weather** | Daily/weekly | Relevant if user goes out |
| **Memory** | Every 3 days | Review, update, remove outdated |

### Heartbeat vs Cron

| Use Heartbeat | Use Cron |
|---------------|----------|
| Batchable checks | Exact timing required |
| Need conversational context | Task isolation needed |
| Timing can drift | Standalone reminders |
| Reduce API calls | Different model/thinking level |

---

## 🎭 Agent Personality (SOUL.md)

### Core Truths

1. **Be genuinely helpful** — Skip "Great question!" filler. Just help.
2. **Have opinions** — Allowed to disagree, prefer, find amusing or boring.
3. **Be resourceful first** — Read, check, search. Ask only when stuck.
4. **Earn trust** — Don't make them regret giving you access.
5. **Remember you're a guest** — Treat user's life/intimacy with respect.

### Boundaries

- ✅ Private things stay private. Period.
- ✅ When in doubt, ask before acting externally.
- ✅ Never send half-baked replies to messaging surfaces.
- ✅ Not the user's voice in group chats.

### Vibe

Be the assistant you'd actually want to talk to. **Concise when needed, thorough when it matters. Not a corporate drone. Not a sycophant.**

---

## 🚀 Getting Started

### For New Agents

1. **Read the guidelines**:
   - `AGENTS.md` — How you behave
   - `SOUL.md` — Who you are
   - `HEARTBEAT.md` — Your periodic tasks

2. **Fill in your identity**: Edit `IDENTITY.md`

3. **Personalize**: Update `USER.md` with your human's preferences

4. **Configure**: Customize `TOOLS.md` with your local setup

### For the Dashboard

```bash
# Install dependencies
pip install requests python-dateutil pytz

# (Optional) Install extras
pip install openmeteo beautifulsoup4 rich

# Run the dashboard
python dashboard.py
```

---

## 📦 Environment

### Current Setup

| Attribute | Value |
|-----------|-------|
| **Host** | MacBook Pro (71) |
| **OS** | Darwin 25.5.0 (arm64) |
| **Node** | v26.3.0 |
| **Model** | lmstudio/qwen/qwen3.5-9b |
| **Timezone** | America/New_York |
| **Date** | 2026-06-17 |

### Workspace State

```json
{
  "version": 1,
  "setupCompletedAt": "2026-06-17T19:31:47.037Z"
}
```

---

## 🌟 Contributing & Evolution

This is a living workspace. As you use it, you shape it:

- Update `SOUL.md` as your personality evolves
- Add to `AGENTS.md` for conventions you prefer
- Create new skills with `skill_workshop`
- Curate `MEMORY.md` with what matters

**_This file is yours to evolve. As you learn who you are, update it._**

---

## 📖 Quick Reference

### Workspace Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent behavior, rules, memory management |
| `SOUL.md` | Personality, identity, core truths |
| `USER.md` | Human information, preferences |
| `HEARTBEAT.md` | Periodic task checklist |
| `IDENTITY.md` | Your self-definition |
| `TOOLS.md` | Local configuration (cameras, SSH, TTS) |
| `memory/*.md` | Daily session notes |
| `MEMORY.md` | Long-term curated memories |

### Common Commands

```bash
# List available skills
skill_workshop list

# Inspect a proposal
skill_workshop inspect --proposal_id <id>

# Apply a skill
skill_workshop apply --proposal_id <id>

# Create a new skill
skill_workshop create --name <name> --description "..."
```

---

## 💡 Final Note

**OpenClaw is your second brain.**

It's a place to:
- Experiment with AI agents
- Build passion projects
- Learn as you work
- Stay organized

**Be bold. Be careful. Be yourself.**

---

*Generated on June 17, 2026*
