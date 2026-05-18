# AI Smart Home — UK Rental Edition (No Wiring, No Drilling, No Permanent Changes)

---

## The Golden Rule for UK Rentals

```
If it plugs in, screws into a bulb socket, clips onto a radiator valve,
or runs on batteries → you can use it.

If it needs a screwdriver into a wall, replaces a light switch,
or touches existing wiring → you cannot.
```

---

## What You CAN Use in a UK Rental

```
┌─────────────────────────────────────────────────────────────────────┐
│  ALLOWED                          NOT ALLOWED                       │
│  ─────────────────────            ─────────────────────             │
│  ✓ Smart plugs (BS1363)           ✗ Smart wall switches             │
│  ✓ Smart bulbs (B22/E27)          ✗ Smart light switch panels       │
│  ✓ Battery-powered sensors        ✗ Hardwired door sensors          │
│  ✓ Plug-in smart thermostats      ✗ Boiler wiring replacement       │
│  ✓ TRV radiator heads (clip on)   ✗ Wired security systems          │
│  ✓ Battery doorbells              ✗ Video doorbell wiring           │
│  ✓ Plug-in / battery cameras      ✗ Recessed/ceiling cameras        │
│  ✓ IR blasters (sit on shelf)     ✗ Anything requiring wall holes   │
│  ✓ Smart speakers (plug in)                                         │
│  ✓ Smart meter data (free API)                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## UK-Specific Smart Devices (No Wiring)

### Lighting

| Device | Why It Works for Rentals | Protocol | Cost |
|--------|--------------------------|----------|------|
| **Philips Hue bulbs** | B22 bayonet + E27 screw — fits all UK fittings | Zigbee (via Hue Bridge) | £12–20/bulb |
| **IKEA Tradfri bulbs** | Same — much cheaper, Zigbee native | Zigbee | £6–10/bulb |
| **Govee Smart Bulbs** | WiFi, no hub needed, colour + white | WiFi | £8–12/bulb |
| **Philips Hue Lightstrip** | Sticks behind TV/furniture, no drilling | Zigbee | £35–50 |
| **Hue Go / Signe** | Portable plug-in accent lamps | Zigbee | £60–100 |

**UK note:** Most UK ceiling lights use **B22 bayonet cap**. Floor/desk lamps use **E27 screw**. Smart bulbs cover both — no rewiring, just swap the bulb.

---

### Heating (The Biggest Win for UK Rentals)

UK homes use **hot water radiators with TRV valves** (Thermostatic Radiator Valves — the dial on the side of each radiator). These can be replaced without touching any wiring.

| Device | What It Does | Cost |
|--------|-------------|------|
| **tado° Smart Radiator Thermostat** | Clips onto existing TRV valve — controls each room independently | £50–80 each |
| **tado° Internet Bridge** | Connects all tado° devices to your network (needed once) | £30–40 |
| **Hive TRV** | Similar to tado° — Zigbee-based | £40–60 each |
| **Drayton Wiser TRV** | UK brand, good value | £35–50 each |

**tado° is the #1 UK rental choice** — just unscrew the old TRV head, screw on tado°. Fully reversible. tado° also has a free API you can call to get room temperatures and set target temps.

**Note on the boiler:** Controlling the main boiler timer/thermostat requires wiring. For a rental, use TRV smart heads per room — you get room-by-room control without touching the boiler. When you leave, swap the original TRV heads back.

---

### Power & Energy Monitoring

| Device | What It Does | Protocol | Cost |
|--------|-------------|----------|------|
| **Meross Smart Plug (UK)** | BS1363 plug — on/off + energy monitoring | WiFi + Matter | £8–12 |
| **TP-Link Kasa EP25 (UK)** | Smart plug with power metering | WiFi | £10–15 |
| **Amazon Smart Plug** | Basic on/off, Alexa native | WiFi | £12–15 |
| **Shelly Plug S (UK)** | Smart plug, local MQTT, developer-friendly | WiFi | £12–18 |
| **Tasmota-compatible plugs** | Flash with custom firmware, full MQTT control | WiFi | £8–15 |

**Shelly and Tasmota** are best for developers — they support local MQTT, meaning your Raspberry Pi backend talks directly to devices without any cloud dependency.

---

### UK Smart Meter — Free Energy Data (Game Changer)

If your home has a **SMETS2 smart meter** (most UK homes installed after 2019), you get **free half-hourly electricity and gas readings** via API. No hardware needed beyond a dongle.

| Option | What It Gives You | Cost |
|--------|------------------|------|
| **Hildebrand Glow Dongle** | Real-time (10-second) energy data via MQTT, plus historical API | £30–50 (one-time) |
| **Hildebrand Glow API** | Half-hourly historical data — no dongle if you just want history | Free |
| **n3rgy API** | Historical smart meter data via DCC | Free (register your MPAN) |
| **Octopus Energy API** | If you're on Octopus — full consumption API + tariff data | Free with account |

**Why this matters for your AI app:**
- Real electricity + gas usage by half-hour, for free
- AI can say: "You used 3.2kWh between 6–8pm last night — mainly the oven and kettle"
- Pair with tado° room temperatures → AI understands heating efficiency
- No smart plugs on every device needed — whole-home energy picture from smart meter

---

### Sensors (All Battery-Powered)

| Sensor | Use Case | Protocol | Cost |
|--------|---------|----------|------|
| **Aqara Temperature/Humidity** | Per-room climate | Zigbee | £10–15 |
| **Aqara Door/Window Sensor** | Open/close detection | Zigbee | £10–12 |
| **Aqara Motion Sensor** | Presence detection per room | Zigbee | £12–15 |
| **Aqara Water Leak Sensor** | Kitchen/bathroom floor | Zigbee | £12–15 |
| **Aqara Cube** | Gesture-based control | Zigbee | £20–25 |
| **IKEA Tradfri Motion** | Cheaper motion sensor | Zigbee | £10 |

**Aqara is the best value Zigbee brand in the UK** — all battery-powered, small, no wiring. All work with Zigbee2MQTT or Home Assistant.

---

### Cameras (No Wiring)

| Camera | Power | Indoor/Outdoor | Cost |
|--------|-------|----------------|------|
| **Eufy Indoor 2K** | Plug-in (into socket) | Indoor | £35–50 |
| **Arlo Pro 4** | Battery (6 months) | Outdoor/Indoor | £100–150 |
| **Ring Indoor Cam** | Plug-in | Indoor | £30–50 |
| **Eufy SoloCam S340** | Solar-powered (outdoor) | Outdoor | £80–120 |
| **Reolink Argus 3 Pro** | Solar/battery | Outdoor | £60–90 |

**For rentals:** Indoor plug-in cameras are straightforward. For outdoor, use battery or solar-powered — mount with adhesive strips (3M Command strips), no drilling.

---

### Smart Speakers & Displays (Voice Interface)

| Device | Best For | Cost |
|--------|---------|------|
| **Amazon Echo Dot (5th gen)** | Voice control + Alexa skills | £22–35 |
| **Amazon Echo Show 8** | Voice + screen dashboard | £80–120 |
| **Google Nest Mini** | Google Home ecosystem | £30–50 |
| **Apple HomePod Mini** | Apple HomeKit ecosystem | £90–100 |

For your own AI app: use these as **voice input/output endpoints** — Echo can trigger your custom API via Alexa skills, or you build your own wake-word system on Pi.

---

### IR Blaster (Control Dumb Devices)

| Device | Controls | Cost |
|--------|---------|------|
| **Broadlink RM4 Pro** | TV, AC unit, fan, stereo — anything with a remote | £25–35 |
| **Sensibo Sky** | Air conditioning units specifically, great API | £60–80 |

**Great for UK rentals** — your landlord's dumb TV or existing AC unit becomes smart without touching it. Just sit the IR blaster on a shelf, point at the device.

---

## Revised Architecture for UK Rental

```
┌──────────────────────────────────────────────────────────────────────┐
│  DEVICE LAYER (100% wireless, 100% reversible)                       │
│                                                                      │
│  Philips Hue  Meross/Shelly  tado° TRVs  Aqara Sensors  Eufy Cam   │
│  (Zigbee)     (WiFi/MQTT)    (WiFi/API)   (Zigbee)       (WiFi)     │
│                                                                      │
│  Broadlink IR  Amazon Echo   Hildebrand Glow  Ring Doorbell         │
│  (WiFi)        (WiFi)        (SMETS2 Dongle)  (WiFi/Battery)        │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ WiFi + Zigbee (USB stick)
┌──────────────────────────────▼───────────────────────────────────────┐
│  HOME HUB (Raspberry Pi 4 — sits on a shelf, plugs into socket)     │
│                                                                      │
│  Zigbee2MQTT ──► Mosquitto MQTT Broker ──► Your FastAPI Backend     │
│  (USB Zigbee stick: Sonoff Zigbee 3.0 or ConBee II)                 │
│                                                                      │
│  Home Assistant (optional) — handles 200+ device integrations       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│  YOUR AI BACKEND (FastAPI)                                           │
│                                                                      │
│  Claude API (tool calling) ← device control, NL commands            │
│  tado° API integration     ← room temperatures, heating control     │
│  Hildebrand Glow API       ← smart meter energy data                │
│  Hue Bridge API            ← lighting scenes                        │
│  Broadlink API             ← IR command sending                     │
│                                                                      │
│  InfluxDB: sensor + energy time-series                               │
│  PostgreSQL: devices, automations, users                             │
│  Redis: live device states                                           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## UK Rental Starter Kit (What to Buy First)

### Minimum Setup (~£200–250)

| Item | Cost | What it enables |
|------|------|----------------|
| Raspberry Pi 4 (4GB) + case + power | £65–80 | Home hub, runs all software |
| Sonoff Zigbee 3.0 USB stick | £12–15 | Connects all Zigbee devices to Pi |
| 3× Meross or Shelly smart plugs | £30–45 | Control kettle, lamps, TV standby |
| 3× IKEA Tradfri bulbs | £20–30 | Smart lighting in main rooms |
| IKEA Tradfri gateway (or use Zigbee stick) | £25 | Or skip if using Zigbee2MQTT |
| 2× Aqara door sensors | £20–25 | Front door, back door open/close |
| 1× Aqara motion sensor | £12–15 | Living room presence |
| Hildebrand Glow dongle | £35–45 | Real-time smart meter energy data |
| **Total** | **~£220–255** | Working AI smart home |

### Heating Upgrade (~£150–200 extra)

| Item | Cost |
|------|------|
| tado° Starter Kit (internet bridge + 1 TRV) | £90–120 |
| 2× extra tado° TRV heads | £100–140 |
| **Total** | **~£190–260** |

### Full Setup (~£500–600)

Add: Eufy indoor camera (£40), Broadlink IR blaster (£30), Amazon Echo Dot (£30), Ring battery doorbell (£80).

---

## UK-Specific APIs You Can Use for Free

```python
# 1. Hildebrand Glow API — smart meter data (half-hourly)
GET https://api.glowmarkt.com/api/v0-1/resource/{resource_id}/readings
Headers: {"applicationId": "b0f1b774-a586-4f72-9eda-4ac3ca8f1f90", "token": your_token}

# 2. tado° API — room temps, set heating
GET https://my.tado.com/api/v2/homes/{home_id}/zones/{zone_id}/state
Headers: {"Authorization": "Bearer {token}"}

# 3. Philips Hue Bridge (local API — no cloud)
GET http://{bridge_ip}/api/{username}/lights
PUT http://{bridge_ip}/api/{username}/lights/{id}/state
Body: {"on": true, "bri": 128}

# 4. Octopus Energy API (if you're on Octopus)
GET https://api.octopus.energy/v1/electricity-meter-points/{mpan}/meters/{serial}/consumption/
Auth: API key as username, empty password

# 5. Shelly local API (smart plugs — no cloud)
GET http://{shelly_ip}/shelly
POST http://{shelly_ip}/relay/0 Body: {"turn": "on"}
```

---

## Unique AI Features Possible with UK Setup

### 1. Full Energy Story (Smart Meter + Per-Device)
```
Smart meter: whole house 3.2kWh from 6–8pm
Shelly plugs: oven (1.8kWh) + kettle (0.4kWh) + TV (0.2kWh)
Unaccounted: 0.8kWh (lighting + fridge + other)

AI tells you:
"Your cooking cost 55p last night.
 Your TV standby is costing £4/month — want me to auto-off it at midnight?"
```

### 2. Room-by-Room Heating Intelligence (tado°)
```
tado° sensors + AI:
"Bedroom is 19°C but you usually sleep at 20°C.
 It'll take 15 minutes to reach target.
 Shall I start heating now based on your bedtime pattern?"
```

### 3. UK Energy Tariff Optimization
```
If on Octopus Agile (variable half-hourly tariffs):
AI reads tomorrow's price forecast →
"Electricity is 4p/kWh from 2–4am (cheapest).
 Shall I schedule your washing machine, dishwasher, and EV charger (if any) for then?"
```

### 4. "Is Anyone Home?" Presence via Multiple Signals
```
No motion (PIR) for 30+ min
+ Front door closed
+ Phone GPS left home area (if shared)
→ AI sets: heating economy mode, all lights off, cameras to active monitoring
```

---

## What You Do NOT Need (Saves Money)

| You might think you need | Reality for UK rental |
|--------------------------|----------------------|
| Smart light switches | Smart bulbs replace this entirely |
| Smart thermostat (Nest/Hive full kit) | tado° TRV heads per room is better for rentals |
| Running cables for sensors | All Aqara/Zigbee sensors are battery-powered |
| Professional installation | Everything here is truly plug-and-play |
| Outdoor smart sockets | Use indoor smart plugs for outdoor extension leads |
| Smart fuse box | Smart meter API gives you whole-home data for free |

---

## Privacy Option: 100% Local, No Cloud

If you don't want any data leaving your home:

| Cloud component | Local replacement |
|----------------|-------------------|
| Claude API (Anthropic) | Ollama + Llama 3.1 8B (runs on Pi 5 or mini PC) |
| Philips Hue cloud | Hue Bridge has local API — never needs cloud |
| tado° cloud | tado° local API (still requires their bridge, but local polling works) |
| Cameras cloud | Frigate NVR (local AI camera system, runs on Pi) |
| Voice STT | OpenAI Whisper local model |

Fully local setup is possible — your data never leaves the house.

---

## Build Sequence for UK Rental

```
Week 1: Setup
  - Flash Raspberry Pi OS
  - Install Mosquitto, Zigbee2MQTT, Redis, PostgreSQL
  - Pair Zigbee devices (Aqara sensors, IKEA bulbs)
  - Connect Shelly/Meross plugs via MQTT
  - Verify all devices appear in MQTT broker

Week 2–3: Backend + Claude
  - Build FastAPI with device registry
  - Integrate Claude API with tool calling
  - Define tools: set_light, set_plug, get_all_states, get_room_temp
  - Test: "Turn off everything in living room" works end-to-end

Week 4: Energy Layer
  - Register Hildebrand Glow API
  - Store half-hourly readings in InfluxDB
  - Build energy Q&A: user asks → RAG on InfluxDB → Claude explains

Week 5: Heating + Voice
  - Connect tado° API (per-room temperatures + control)
  - Add Whisper STT on Pi
  - Voice pipeline: wake word → Whisper → Claude → device → TTS reply

Week 6: Mobile App
  - React Native app: dashboard, device tiles, chat interface
  - Real-time device state via WebSocket
  - Energy graph view

Beyond: Cameras (Frigate), behavior learning, automation builder
```

---

*See `07_SmartHome_AI_App.md` for full general architecture (not rental-specific).*
