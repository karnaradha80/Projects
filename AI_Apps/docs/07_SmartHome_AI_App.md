# AI-Based Smart Home Application — Complete Guide

---

## What Is an AI Smart Home App?

A traditional smart home lets you control devices manually via an app.
An **AI smart home** goes further:

| Traditional Smart Home | AI Smart Home |
|------------------------|--------------|
| "Turn on lights" button | "I'm watching a movie" → AI dims lights, lowers AC, closes blinds |
| Fixed schedules | AI learns your routine, automates without you setting rules |
| Manual energy tracking | AI explains your bill and optimizes usage automatically |
| Rule-based alerts | AI detects anomalies: "Fridge door open 30 min — is that normal?" |
| App control only | Natural language: "What's happening at home right now?" |

---

## The 7 AI Use Cases in a Smart Home

| # | Use Case | AI Type | Value |
|---|----------|---------|-------|
| 1 | **Natural Language Control** | LLM (Claude/GPT) | "Turn everything off except bedroom AC" — understands complex commands |
| 2 | **Behavioral Learning & Automation** | ML (Time-series) | AI learns your patterns → creates automations automatically |
| 3 | **Energy Optimization** | ML + LLM | Schedule high-power devices in off-peak hours; explain bill |
| 4 | **Anomaly Detection** | Unsupervised ML | Unusual activity = security alert; appliance anomaly = maintenance alert |
| 5 | **Predictive Comfort** | ML + location | Pre-cool room 30 min before you arrive based on GPS + weather |
| 6 | **Conversational Automation Builder** | LLM | "Every morning at 7, if it's a weekday, turn on kitchen lights and start coffee" → AI creates the rule |
| 7 | **Security Intelligence** | Computer Vision + LLM | Camera detects person/package/intruder → AI describes what it sees |

---

## Full Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  DEVICE LAYER (Physical Hardware)                                        │
│                                                                          │
│  Smart Lights  Smart Plugs  Thermostat  Door Locks  Sensors  Cameras    │
│  (Philips Hue) (Tasmota)   (Nest/Ecobee)(Schlage)  (Temp/Motion)(RTSP) │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │ MQTT / Matter / Zigbee / Z-Wave / WiFi
┌──────────────────────────────▼───────────────────────────────────────────┐
│  IOT GATEWAY / HUB (Local — Raspberry Pi 4 or small PC)                 │
│                                                                          │
│  MQTT Broker (Mosquitto)  ──  Home Assistant (optional)                 │
│  Device Discovery         ──  Protocol Bridge (Zigbee → MQTT)           │
│  Local AI (Ollama, optional for privacy)                                 │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │ REST API / WebSocket / gRPC
┌──────────────────────────────▼───────────────────────────────────────────┐
│  BACKEND (FastAPI / Python)                                              │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────┐ │
│  │  Device Manager │  │ Automation      │  │  AI / LLM Layer          │ │
│  │  - Register     │  │ Engine          │  │  - Intent Parser         │ │
│  │  - State Store  │  │ - Rule Engine   │  │  - Command Executor      │ │
│  │  - Command Send │  │ - Trigger/Action│  │  - Behavior Learner      │ │
│  └─────────────────┘  └─────────────────┘  │  - Anomaly Detector      │ │
│                                             │  - Energy Advisor        │ │
│  ┌─────────────────┐  ┌─────────────────┐  └──────────────────────────┘ │
│  │  Event Stream   │  │  User/Auth      │                               │
│  │  (WebSocket)    │  │  Manager        │                               │
│  └─────────────────┘  └─────────────────┘                               │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
         ┌─────────────────────┼──────────────────────┐
         │                     │                      │
┌────────▼────────┐  ┌─────────▼──────────┐  ┌───────▼──────────────┐
│  TIME-SERIES DB │  │  RELATIONAL DB     │  │  CACHE               │
│  InfluxDB /     │  │  PostgreSQL        │  │  Redis               │
│  TimescaleDB    │  │  - Users           │  │  - Device states     │
│  - Sensor reads │  │  - Devices         │  │  - Active sessions   │
│  - Power usage  │  │  - Automations     │  │  - Recent events     │
│  - Temp history │  │  - Notifications   │  └──────────────────────┘
└─────────────────┘  └────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────┐
│  EXTERNAL AI SERVICES                                                    │
│  Claude API (Anthropic) — NL control, automation builder, energy advisor │
│  OpenAI Whisper (optional) — Voice-to-text                              │
└──────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────┐
│  FRONTEND LAYER                                                          │
│                                                                          │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐ │
│  │  Mobile App        │  │  Web Dashboard     │  │  Voice Interface   │ │
│  │  React Native/Expo │  │  React / Next.js   │  │  Wake word +       │ │
│  │  - Dashboard       │  │  - Floor plan view │  │  Whisper STT +     │ │
│  │  - Device control  │  │  - Analytics       │  │  Claude LLM +      │ │
│  │  - AI Chat         │  │  - Automations     │  │  TTS response      │ │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack — Complete List

### Hardware You Need (for Development & Testing)

| Device | Purpose | Cost (approx.) |
|--------|---------|----------------|
| **Raspberry Pi 4 (4GB)** | Local hub/gateway | ₹5,000–8,000 |
| Smart WiFi plugs (x3–5) | Controllable outlets (use Tasmota firmware) | ₹500–1,500 each |
| DHT22 / SHT31 sensor | Temperature + humidity | ₹200–500 |
| PIR Motion sensor | Motion detection | ₹200–500 |
| Smart LED bulbs | Controllable lighting | ₹500–2,000 each |
| IP Camera (RTSP) | Video feed for CV | ₹2,000–5,000 |
| ESP32 microcontroller | Custom sensor nodes | ₹300–600 |

**Minimum to start:** Just a Raspberry Pi + 2–3 smart WiFi plugs running Tasmota. No Zigbee hardware required.

---

### Software Stack

#### IoT / Device Communication
| Component | Tool | Notes |
|-----------|------|-------|
| **MQTT Broker** | Mosquitto | Free, runs on Pi, industry standard |
| **Device Firmware** | Tasmota / ESPHome | Flash onto ESP8266/ESP32 smart devices |
| **Protocol Bridge** | Zigbee2MQTT | Converts Zigbee devices → MQTT |
| **Home Automation Base** | Home Assistant (optional) | Open source, huge device support |
| **IoT Standard** | Matter over WiFi | New universal standard (Apple/Google/Amazon) |

#### Backend
| Component | Tool | Notes |
|-----------|------|-------|
| **API Framework** | FastAPI (Python) | Async, fast, auto-docs |
| **WebSocket** | FastAPI WebSocket | Real-time device state push to frontend |
| **MQTT Client** | paho-mqtt | Python library to subscribe to device topics |
| **Task Queue** | Celery + Redis | Async automation execution |
| **Auth** | JWT tokens | User authentication |

#### Databases
| Database | Purpose | Tool |
|----------|---------|------|
| **Time-series** | Sensor readings, power usage, temperature history | InfluxDB or TimescaleDB |
| **Relational** | Users, devices, automations, rooms, scenes | PostgreSQL |
| **Cache / State** | Current device states, active sessions | Redis |
| **Vector Store** | Semantic search on automations (for AI) | Chroma (local) |

#### AI / ML Layer
| Component | Tool | Use Case |
|-----------|------|---------|
| **LLM (primary)** | Claude API (Sonnet) | NL commands, automation builder, energy Q&A |
| **LLM (local, optional)** | Ollama + Llama 3 | Privacy-first, no cloud needed |
| **Behavior Learning** | scikit-learn / Prophet | Learn user routines from time-series data |
| **Anomaly Detection** | Isolation Forest / LSTM | Detect unusual device behavior |
| **Speech-to-Text** | OpenAI Whisper | Convert voice to text for LLM |
| **Text-to-Speech** | Coqui TTS / ElevenLabs | Speak back AI responses |
| **Computer Vision** | YOLOv8 | Person/object detection on camera feeds |
| **Embeddings** | sentence-transformers | Semantic search on device descriptions |

#### Frontend
| Layer | Tool | Notes |
|-------|------|-------|
| **Mobile App** | React Native + Expo | iOS + Android from one codebase |
| **Web Dashboard** | React + Vite or Next.js | Browser-based control panel |
| **UI Components** | shadcn/ui or Ant Design | Ready-made components |
| **Real-time Updates** | Socket.io or native WebSocket | Live device state updates |
| **Charts** | Recharts or Chart.js | Energy usage graphs |
| **Floor Plan** | react-floorplan or SVG | Interactive home map |

#### Infrastructure
| Component | Tool |
|-----------|------|
| **Local Deployment** | Docker Compose (all services on Pi or home server) |
| **Cloud (optional)** | Railway / Render / AWS for remote access |
| **Reverse Proxy** | Nginx or Caddy (HTTPS) |
| **DNS / Remote Access** | Cloudflare Tunnel (free, no port forwarding) |
| **Monitoring** | Grafana + InfluxDB (already in stack) |

---

## How the AI Layer Works

### Feature 1 — Natural Language Device Control

```
User says: "It's movie time"
            │
            ▼
     Speech-to-Text (Whisper)
            │
            ▼
┌──────────────────────────────────────────┐
│  Claude API with Tool Calling            │
│                                          │
│  System Prompt:                          │
│  "You control a smart home. Available    │
│  devices: {device_list}. Current states: │
│  {current_states}. User is in: {room}"   │
│                                          │
│  User: "It's movie time"                 │
│                                          │
│  Claude decides to call:                 │
│  - set_light(room="living", brightness=10│
│  - set_ac(temp=22, mode="cool")          │
│  - close_blinds(room="living")           │
│  - set_scene("movie")                    │
└──────────────────────────────────────────┘
            │ Tool calls executed
            ▼
     Devices update → User gets confirmation
     "Done! Lights dimmed, AC set to 22°C, blinds closed."
```

### Feature 2 — Conversational Automation Builder

```
User: "Every weekday morning at 6:30, turn on the kitchen lights at 30%,
       start the coffee maker, and set the thermostat to 24°C.
       But only if I'm home."

Claude parses this into structured rule:
{
  "trigger": {"type": "time", "cron": "30 6 * * 1-5"},
  "conditions": [{"type": "presence", "user": "owner", "state": "home"}],
  "actions": [
    {"device": "kitchen_light", "command": "set_brightness", "value": 30},
    {"device": "coffee_maker", "command": "turn_on"},
    {"device": "thermostat", "command": "set_temp", "value": 24}
  ]
}

Saved to automation engine → runs every weekday
```

### Feature 3 — Behavioral Learning

```
Collect 30 days of: device events + timestamps + user location

Pattern Mining (ML):
  Monday–Friday:
    06:25 → Bedroom light ON (91% of days)
    06:28 → Bathroom light ON
    06:45 → Kitchen light ON, Coffee maker ON
    07:55 → All lights OFF, Door locked, AC set to 30°C

AI proposes automation:
  "I noticed you follow the same morning routine on weekdays.
   Want me to automate it?"
  → User approves → Automation created
```

### Feature 4 — Energy Advisor

```
User: "Why was my electricity bill so high last month?"

RAG Pipeline:
  1. Query InfluxDB: get last 30 days of per-device power consumption
  2. Calculate: which devices used most, compare to previous month
  3. Inject data into Claude prompt
  4. Claude responds:

"Your bill was 23% higher than last month. The main cause:
 - AC in the living room ran 8 hours/day vs 5 hours last month (+₹620)
 - The water heater was left on overnight 6 times (+₹280)
 
 Quick fixes:
 1. I can set the AC to auto-off at midnight — save ~₹500/month
 2. I'll add a water heater schedule — save ~₹300/month
 Want me to apply these?"
```

---

## Data Models (Key Entities)

```python
# Device
{
  "id": "light_living_001",
  "name": "Living Room Main Light",
  "type": "light",          # light | switch | thermostat | lock | sensor | camera
  "room": "living_room",
  "protocol": "mqtt",       # mqtt | matter | zigbee | wifi
  "topic": "home/living/light1",
  "capabilities": ["on_off", "brightness", "color_temp"],
  "current_state": {"on": true, "brightness": 80, "color_temp": 3000},
  "last_seen": "2026-04-29T08:32:00Z"
}

# Automation
{
  "id": "auto_001",
  "name": "Morning Routine",
  "created_by": "ai",       # ai | user
  "trigger": {"type": "time", "cron": "30 6 * * 1-5"},
  "conditions": [{"type": "presence", "state": "home"}],
  "actions": [
    {"device_id": "light_kitchen_001", "command": "set_brightness", "value": 80},
    {"device_id": "coffee_maker_001", "command": "turn_on"}
  ],
  "enabled": true
}

# Sensor Reading (Time-series in InfluxDB)
measurement: "sensor_data"
tags: {device_id: "temp_bedroom_001", room: "bedroom", type: "temperature"}
fields: {value: 24.5}
timestamp: 2026-04-29T08:32:00Z
```

---

## Step-by-Step Build Plan

### Phase 1 — Core (4–6 weeks)
- [ ] Set up Raspberry Pi + Mosquitto MQTT broker
- [ ] Connect 2–3 smart plugs via MQTT (Tasmota)
- [ ] Build FastAPI backend: device registry, MQTT subscriber, device command API
- [ ] Set up PostgreSQL (devices, users) + Redis (device states)
- [ ] Build basic React Native dashboard: see devices, toggle on/off
- [ ] User auth with JWT

**Milestone:** Can control real smart devices from mobile app

### Phase 2 — AI Control (3–4 weeks)
- [ ] Integrate Claude API with tool calling for device control
- [ ] Define tools: `set_device_state`, `get_device_states`, `get_room_devices`
- [ ] Build chat UI in mobile app — user types or speaks commands
- [ ] Add Whisper for voice input → text → Claude → device action
- [ ] Add TTS for Claude's spoken confirmation

**Milestone:** "Hey, turn off everything in the living room" works end-to-end

### Phase 3 — Intelligence (4–6 weeks)
- [ ] Add InfluxDB for time-series sensor + power data
- [ ] Build automation engine (trigger/condition/action runner)
- [ ] Build conversational automation builder (Claude parses natural language → rule JSON)
- [ ] Add energy tracking dashboard (per-device power usage charts)
- [ ] Build Energy Advisor AI (RAG on InfluxDB data → Claude explains usage)

**Milestone:** AI can create automations from natural language + explain energy bill

### Phase 4 — Learning & Security (4–6 weeks)
- [ ] Behavioral pattern mining (scikit-learn on event logs)
- [ ] AI-proposed automations ("I noticed your pattern — want to automate it?")
- [ ] Anomaly detection on sensor data (Isolation Forest)
- [ ] Camera integration + YOLOv8 person detection
- [ ] Security alerts: unusual motion, unknown person, door open at night

**Milestone:** App learns your habits and proactively suggests automations

### Phase 5 — Polish & Deploy (2–3 weeks)
- [ ] Floor plan view (drag-and-drop room map with device icons)
- [ ] Scenes builder ("Movie mode", "Dinner mode", "Away mode")
- [ ] Cloudflare Tunnel for remote access (no port forwarding needed)
- [ ] Docker Compose: package all services for easy deployment
- [ ] Push notifications for alerts

---

## Complete Tech Stack Summary

```
Layer              Technology
────────────────── ──────────────────────────────────────────
Device/IoT         MQTT (Mosquitto), Tasmota, Zigbee2MQTT, Matter
Hub OS             Raspberry Pi OS (64-bit) or Home Assistant
Backend API        FastAPI (Python 3.11+)
Task Queue         Celery + Redis
MQTT Client        paho-mqtt (Python)
Time-series DB     InfluxDB v2
Relational DB      PostgreSQL 15
Cache              Redis 7
Vector Store       Chroma (for automation semantic search)
LLM                Claude API (claude-sonnet-4-6)
Local LLM (opt)    Ollama + Llama 3.1 8B
STT                OpenAI Whisper (local)
TTS                Coqui TTS or ElevenLabs
Computer Vision    YOLOv8 (ultralytics)
ML/Behavior        scikit-learn, Prophet
Mobile App         React Native + Expo
Web Dashboard      React + Vite + Tailwind CSS
Charts             Recharts
Real-time          WebSocket (FastAPI native)
Auth               JWT (python-jose)
Deployment         Docker Compose
Remote Access      Cloudflare Tunnel (free)
Monitoring         Grafana + InfluxDB
```

---

## Skills You Need

### Must Have
| Skill | Used For |
|-------|---------|
| **Python** | Backend, AI layer, MQTT client, ML |
| **REST API basics** | Calling Claude API, building FastAPI endpoints |
| **Basic Linux / Raspberry Pi** | Running services on the hub |
| **SQL basics** | PostgreSQL queries |
| **Git** | Version control |

### Good to Have
| Skill | Used For |
|-------|---------|
| React Native | Mobile app |
| Docker | Packaging and deploying |
| MQTT basics | Understanding device communication |
| LangChain or direct Anthropic SDK | Building the AI layer |

### Learn Along the Way
- InfluxDB query language (Flux)
- MQTT topic design patterns
- WebSocket programming
- Whisper model usage
- YOLOv8 inference

---

## Cost to Build (Monthly Running Cost)

| Service | Cost |
|---------|------|
| Claude API (Sonnet) — ~100 queries/day | ~$2–5/month |
| Hosting (if cloud) — Railway/Render | ~$5–10/month |
| Cloudflare Tunnel | Free |
| Everything else runs locally on Pi | Free |
| **Total** | **~$7–15/month** |

Local-only (no cloud LLM): run Ollama on home server → $0/month

---

## Minimum Viable Product (MVP) in 6 Weeks

Focus on just these 3 things:

1. **Control** — Mobile app + voice → Claude → MQTT → device responds
2. **Automate** — "Create an automation for me" → Claude → saved rule → runs
3. **Inform** — "What's on at home right now?" → Claude reads all device states → describes home status

Everything else (learning, CV, energy AI) comes after the MVP works.

---

*Related: See `01_Terminology.md` for AI concepts, `02_Architecture.md` for general AI app architecture, `03_LearningPath.md` for learning sequence.*
