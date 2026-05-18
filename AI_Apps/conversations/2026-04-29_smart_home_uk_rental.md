# Conversation: Smart Home AI App — UK Rental Constraint
**Date:** 2026-04-29  
**Project:** AI_Apps

---

## User Context
User is in the UK, renting a house. Cannot touch existing wiring or fixed installations.

## Key Adaptations Made

### What changes from the general guide
- No smart wall switches (require wiring)
- No boiler/thermostat wiring replacement
- No hardwired sensors or cameras
- No drilling into walls

### What works instead
- Smart bulbs (B22 bayonet/E27 screw) replace smart switches entirely
- tado° TRV heads clip onto existing radiator valves — no boiler wiring
- All Aqara sensors are battery-powered, Zigbee
- Shelly/Meross smart plugs are BS1363 UK format
- Battery/solar outdoor cameras, indoor plug-in cameras
- Broadlink IR blaster controls dumb devices (TV, fan, AC) with no wiring

### UK-Specific Opportunity: Free Smart Meter API
- Most UK homes (post-2019) have SMETS2 smart meters
- Hildebrand Glow dongle (£35–50) gives real-time 10-second energy data via MQTT
- n3rgy or Octopus Energy API gives half-hourly historical data free
- This is the energy monitoring layer — no smart plugs on every device needed
- Octopus Agile tariff users can optimize device scheduling to cheapest half-hours

### Starter Kit (~£220–255)
Raspberry Pi 4 + Sonoff Zigbee stick + 3 smart plugs + 3 IKEA bulbs + 2 Aqara door sensors + 1 motion sensor + Hildebrand Glow dongle

### Heating upgrade (~£190–260 extra)
tado° Starter Kit + 2 extra TRV heads = room-by-room heating control, fully reversible

## Document Created
`docs/08_SmartHome_UK_Rental.md` — UK rental specific guide: allowed devices, UK product recommendations, UK APIs, starter kit with costs, 6-week build plan
