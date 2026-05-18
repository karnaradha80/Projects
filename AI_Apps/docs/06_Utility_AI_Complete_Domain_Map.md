# Utility Industry — Complete AI Domain Map (All Functions)

---

## Enterprise View: Where AI Applies Across a Utility

A utility company is not just a grid operator — it is a full enterprise with IT, HR, Finance, Supply Chain, Safety, and more. AI gaps exist in every function.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                         UTILITY ENTERPRISE                                    │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │  GRID & OPERATIONS LAYER                                             │    │
│  │  Generation │ Transmission │ Distribution │ Metering │ SCADA/EMS     │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌─────────────────────┐   ┌────────────────────┐   ┌─────────────────────┐ │
│  │  GIS & SPATIAL       │   │  ASSET MANAGEMENT  │   │  FIELD OPERATIONS   │ │
│  │  INTELLIGENCE        │   │  (EAM/SAP PM)      │   │  & WORKFORCE        │ │
│  └─────────────────────┘   └────────────────────┘   └─────────────────────┘ │
│                                                                               │
│  ┌─────────────────────┐   ┌────────────────────┐   ┌─────────────────────┐ │
│  │  CUSTOMER &          │   │  REVENUE &         │   │  SAFETY &           │ │
│  │  SERVICE DESK        │   │  BILLING           │   │  COMPLIANCE         │ │
│  └─────────────────────┘   └────────────────────┘   └─────────────────────┘ │
│                                                                               │
│  ┌─────────────────────┐   ┌────────────────────┐   ┌─────────────────────┐ │
│  │  IT / APPLICATION    │   │  SUPPLY CHAIN &    │   │  HR & WORKFORCE     │ │
│  │  MAINTENANCE (AIOps) │   │  PROCUREMENT       │   │  MANAGEMENT         │ │
│  └─────────────────────┘   └────────────────────┘   └─────────────────────┘ │
│                                                                               │
│  ┌─────────────────────┐   ┌────────────────────┐   ┌─────────────────────┐ │
│  │  RENEWABLE / DER     │   │  REGULATORY &      │   │  CYBERSECURITY      │ │
│  │  MANAGEMENT          │   │  COMPLIANCE        │   │  (OT/IT)            │ │
│  └─────────────────────┘   └────────────────────┘   └─────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete List: 20 AI Domains in Utilities

---

### DOMAIN 1: Predictive Asset Failure *(Grid & Operations)*
**Gap:** Time-based / reactive maintenance on 40-year-old infrastructure
**AI:** Predict transformer, cable, switchgear failures 30–90 days ahead using SCADA + AMI + weather + work order history
**ROI:** Avoid ₹5–65 Lakhs per failure; 60% reduction in unplanned outages
**Data:** SCADA readings, GIS asset data, work order history, weather

---

### DOMAIN 2: Energy Theft / Non-Technical Loss Detection *(Grid & Revenue)*
**Gap:** 15–25% AT&C losses in Indian DISCOMs; manual detection hits <5% of actual theft
**AI:** Anomaly detection on AMI data — load mismatches, tamper events, consumption pattern breaks
**ROI:** Direct revenue recovery; ₹100s of crores annually for a mid-sized DISCOM
**Data:** Smart meter interval data (15-min), feeder-level meter, billing records

---

### DOMAIN 3: Outage Prediction & Restoration Intelligence *(Grid & Operations)*
**Gap:** Reactive outage management; fault location takes 20–60 min manually
**AI:** Pre-storm risk scoring, ML-based fault location, optimal restoration sequencing
**ROI:** SAIDI/SAIFI improvement; regulatory penalty avoidance
**Data:** SCADA, weather forecast, grid topology, outage history

---

### DOMAIN 4: Demand Forecasting *(Grid & Planning)*
**Gap:** Old regression models can't handle EVs, rooftop solar, battery storage
**AI:** LSTM/Transformer models for feeder-level short-term and medium-term forecasting
**ROI:** Avoid over/under procurement penalties; better grid balancing
**Data:** Historical load, weather, EV adoption data, solar generation

---

### DOMAIN 5: Vegetation / ROW Management *(Field Operations)*
**Gap:** Manual inspection of 1000s of km of lines; 3–5 year inspection cycles
**AI:** Drone + satellite imagery + computer vision to detect encroachment and rank risk
**ROI:** 25–35% of outages are vegetation-related — AI reduces these dramatically
**Data:** Aerial/satellite imagery, line corridor GIS data, outage history by cause

---

### DOMAIN 6: Field Workforce Intelligence *(Field Operations)*
**Gap:** Aging workforce, knowledge loss, inefficient job scheduling, wrong-parts dispatching
**AI:** Optimal crew scheduling, AI job estimator, parts prediction, knowledge capture chatbot
**ROI:** Reduce second-trip rate (currently 30–40%), faster job completion
**Data:** Work orders, crew skills/location, inventory, historical job times

---

### DOMAIN 7: Customer Service & Billing Intelligence *(Customer)*
**Gap:** 70% of call center volume is predictable/automatable; bill disputes expensive
**AI:** Outage chatbot, bill explainer AI, payment default prediction, self-service automation
**ROI:** 30–50% call deflection; reduced cost-to-serve
**Data:** CIS/billing records, outage management data, payment history

---

### DOMAIN 8: Regulatory & Compliance Intelligence *(Enterprise)*
**Gap:** Massive manual reporting burden for CERC/SERC/FERC filings, environmental reports
**AI:** Auto-generate regulatory reports from operational data, compliance monitoring dashboards
**ROI:** Save 100s of man-hours per filing cycle; avoid penalties
**Data:** Operational databases, regulatory requirement documents

---

### DOMAIN 9: GIS Intelligence *(Spatial & Network)*

**The Problem**
- Utility GIS data is the **single most important dataset** — everything is location-dependent
- But most utility GIS is **incomplete, outdated, or incorrect**
  - Assets installed but never updated in GIS
  - Field changes (cable replaced, new pole) not reflected for months/years
  - Network connectivity errors → wrong fault isolation, wrong outage crew dispatch
  - Many utilities still have paper maps or partly digitized records

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Auto-GIS Update from Field** | Field crew takes photo of new asset → AI extracts asset type, location (GPS), attributes → auto-updates GIS |
| **Infrastructure Extraction from Imagery** | Satellite/drone imagery → Computer Vision → auto-map poles, lines, substations |
| **GIS Data Quality AI** | Scan GIS for topology errors, missing connectivity, duplicate assets, coordinate anomalies |
| **Network Topology Validation** | AI cross-checks GIS topology against SCADA connectivity — flags mismatches |
| **Spatial Risk Analysis** | Overlay asset locations with flood zones, seismic risk, crime (theft risk), soil corrosion — generate spatial risk map |
| **Optimal Network Planning** | AI suggests where to build new feeders, substations based on load growth + terrain + cost |
| **LLM on GIS** | "Show all 33kV lines in Zone 4 older than 25 years near flood zones" → AI queries and maps instantly |

**Data:** GIS database (ESRI/ArcGIS/QGIS), field photos, satellite imagery, SCADA topology, drone surveys

**ROI:** Accurate GIS reduces wrong crew dispatch, improves fault isolation time by 40–60%, enables all other AI use cases (bad GIS = bad AI)

---

### DOMAIN 10: Asset Management Intelligence *(EAM/SAP PM/Maximo)*

**The Problem**
- Utilities run SAP PM, IBM Maximo, Oracle EAM — but the **data inside is terrible**
  - Asset master records have missing attributes (age, rating, manufacturer unknown)
  - Work order notes are free text — no structured failure codes
  - Spare parts inventory is not linked to asset failure patterns
  - Repair vs replace decisions are made on gut feel
  - No consistent failure mode taxonomy across the organization

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Asset Master Data Enrichment** | AI reads free-text work orders, site photos, old inspection reports → fills missing attributes in EAM |
| **Work Order Intelligence** | NLP on work order descriptions → auto-classify failure mode, root cause, component failed |
| **Repair vs Replace Decision AI** | Score each aging asset: repair cost trend + failure probability + replacement cost → recommend repair/defer/replace |
| **Spare Parts Optimization** | Predict which spares will be needed in next 90 days based on asset health + season → right-size inventory |
| **Failure Mode Library** | Extract structured FMEA (Failure Mode & Effect Analysis) from 10 years of work order free text |
| **Maintenance Plan Optimization** | AI generates risk-based maintenance plans replacing calendar-based schedules |
| **Total Asset Lifecycle Costing** | AI models true total cost of ownership for each asset class |

**Data:** EAM work orders (10+ years), asset master data, procurement/parts records, field inspection reports, SCADA operational data

**ROI:** 15–25% reduction in maintenance costs; better capital planning (right asset replaced at right time)

---

### DOMAIN 11: IT Service Desk / Application Support *(IT)*

**The Problem**
- Utility IT teams manage 50–150 applications: SCADA, AMI HES, MDM, billing, GIS, ERP, CRM, OMS
- Many are 20–30 year old legacy systems — minimal documentation
- Service desk handles thousands of tickets: "SCADA not updating", "AMI meter offline", "Billing run failed"
- L1 resolution is repetitive and manual — tickets get stuck, escalation is slow
- Field staff constantly call IT for basic app issues

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Intelligent Ticket Routing** | AI reads ticket description → auto-categorize → route to right team in <1 min vs 30 min manual |
| **L1 Auto-Resolution** | AI resolves known issues automatically: password resets, stuck batch jobs, standard error codes |
| **Service Desk Chatbot** | Field engineer: "My mobile app won't sync work orders" → AI diagnoses and fixes or escalates |
| **Knowledge Base AI** | Search across all past tickets, resolutions, runbooks → AI surfaces the right fix instantly |
| **Proactive Incident Detection** | Monitor application logs → detect anomaly before users raise ticket |
| **Ticket Volume Prediction** | Forecast when spikes in tickets will happen (post-storm, post-billing run) → pre-staff the desk |
| **SLA Risk Alerting** | AI monitors open tickets → flags at-risk SLAs before they breach |

**Data:** ITSM ticket history (ServiceNow/Remedy/Jira), application logs, resolution notes, knowledge base articles

**ROI:** 40–60% reduction in L1 ticket handling time; 30% more first-call resolutions; faster MTTR

---

### DOMAIN 12: Application Maintenance & AIOps *(IT/DevOps)*

**The Problem**
- Utility applications are often deeply legacy — COBOL billing systems, 1990s SCADA, custom-built MDM
- Code is undocumented; original developers are retired
- Changes to one system break 3 others (tight coupling, no APIs)
- Application performance degrades silently → field operations impacted without warning
- Testing before releases is manual, slow, and incomplete

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Legacy Code Documentation AI** | AI reads COBOL/VB6/Java code → generates plain-English documentation and data flow diagrams |
| **Code Modernization** | AI translates legacy code to modern Python/Java — flags risks and differences |
| **Automated Test Generation** | AI generates test cases from code and historical incidents → reduces manual testing effort |
| **Log Intelligence (AIOps)** | AI ingests all application logs → correlates events → detects anomalies → predicts incidents |
| **Root Cause Analysis AI** | When an incident happens → AI traces logs across systems → identifies root cause in minutes vs hours |
| **Change Impact Analysis** | Before deploying a change, AI predicts which downstream systems/processes will be affected |
| **Performance Baseline & Drift Detection** | AI learns normal application behavior → alerts on degradation before it causes user impact |
| **Release Risk Scoring** | AI scores the risk of a proposed release based on code change volume, system criticality, historical incidents |

**Data:** Application logs, code repositories, incident history, change management records, performance metrics

**ROI:** 50–70% faster MTTR; fewer production incidents; dramatically faster legacy modernization

---

### DOMAIN 13: Renewable Energy & DER Management *(Grid & Strategy)*

**The Problem**
- Rooftop solar, wind, battery storage, EV charging are rapidly growing
- These are **bidirectional and unpredictable** — the grid was never designed for this
- Virtual Power Plants (VPPs) need millisecond-level orchestration
- Utilities struggle to forecast net load with high DER penetration

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Solar/Wind Generation Forecasting** | Predict output from distributed rooftop solar and wind farms for grid balancing |
| **VPP Orchestration AI** | Optimal dispatch of batteries, flexible loads, EVs to balance supply/demand in real time |
| **EV Charging Load Management** | Predict EV charging demand by location/time → manage grid impact, offer smart charging incentives |
| **DER Impact on Grid AI** | Model how adding 10,000 rooftop solar systems in a suburb changes feeder voltage profiles |
| **Battery Optimization** | Charge/discharge scheduling for grid-scale batteries based on price + grid need + degradation |

---

### DOMAIN 14: Safety & Incident Prevention *(HSE)*

**The Problem**
- Utilities have one of the highest fatality rates of any industry (electrocution, falls, arc flash)
- Safety incidents are recorded but patterns are not analyzed
- Near-misses are underreported and unanalyzed
- PPE compliance is spot-checked, not continuous

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Near-Miss Pattern Analysis** | NLP on safety observation reports → identify recurring unsafe conditions before fatality |
| **Arc Flash Risk Prediction** | Correlate SCADA protection settings + asset age + work type → flag high arc flash risk jobs |
| **PPE Compliance (Computer Vision)** | Camera at substation entry → AI detects missing helmet/gloves → blocks entry or alerts |
| **High-Risk Job Pre-screening** | Before issuing permit-to-work, AI checks: asset condition, weather, last inspection date, crew experience |
| **Safety Incident Root Cause AI** | Structured root cause classification from free-text incident reports |

---

### DOMAIN 15: Procurement & Supply Chain Intelligence *(Finance/SCM)*

**The Problem**
- Transformer lead times: 12–24 months. If you don't order in time, you wait.
- Utilities often have either too much or too little inventory of critical spares
- Vendor performance data exists but is not analyzed
- Contract terms (price escalation clauses, SLAs) are in PDFs — not queryable

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Demand Forecasting for Spares** | Predict which transformers, cables, meters will be needed 12–18 months ahead |
| **Vendor Risk Scoring** | AI scores each vendor: delivery performance, quality failures, financial stability |
| **Contract Intelligence** | AI extracts key terms, obligations, penalties from 100s of vendor contracts → searchable, alertable |
| **Inventory Optimization** | Right-size stock across warehouses using failure predictions + lead times |
| **Purchase Order Anomaly Detection** | Flag unusual procurement patterns (potential fraud or overpayment) |

---

### DOMAIN 16: HR & Workforce Development *(HR)*

**The Problem**
- 40–50% of skilled utility workers will retire in the next 10 years
- Institutional knowledge is walking out the door
- Training is generic, not role/skill-gap specific
- Succession planning is informal

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Skill Gap Analysis** | Compare current workforce skills vs future grid needs (EV, DER, smart grid) → targeted training |
| **Personalized Learning AI** | Employee-specific training path based on role, gaps, learning pace |
| **Knowledge Transfer AI** | Interview retiring experts → extract knowledge → store in searchable AI knowledge base |
| **Succession Planning AI** | Score candidates for leadership roles based on skills, performance, trajectory |
| **Attrition Prediction** | Identify flight-risk employees before they resign |

---

### DOMAIN 17: Cybersecurity for OT/IT Convergence *(IT/OT Security)*

**The Problem**
- SCADA, AMI, protection relays are now IP-connected → exposed to cyberattacks
- IT and OT networks are converging → IT threats now reach operational systems
- OT security monitoring is immature; most utilities lack 24x7 OT SOC

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **OT Anomaly Detection** | Baseline normal SCADA/DCS traffic → detect unusual commands or data flows |
| **IT/OT Threat Correlation** | Connect IT security events with OT network activity → detect lateral movement |
| **Vulnerability Prioritization** | AI ranks 1000s of CVEs by actual exploitability in utility OT context |
| **Phishing Detection** | Email security AI tuned to utility-specific social engineering attacks |

---

### DOMAIN 18: Meter Data Management (MDM) Intelligence *(Metering)*

**The Problem**
- Smart meters generate billions of reads — but 5–15% are missing, estimated, or incorrect
- Bad meter data → wrong bills → disputes → customer complaints
- AMI network health (which meters are offline) is poorly monitored

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Missing Read Imputation** | AI fills in missing meter reads using consumption patterns of similar meters |
| **Anomalous Read Detection** | Flag meter reads that are statistically impossible (spike, zero, constant flat-line) |
| **AMI Network Health AI** | Predict which meters are about to go offline based on communication quality trends |
| **Meter Fraud vs Fault Classification** | Distinguish between a broken meter and a bypassed meter |

---

### DOMAIN 19: Network Planning & Capital Investment *(Strategy/Planning)*

**The Problem**
- Grid expansion decisions involve ₹100s of crores in capital
- Load growth projections are based on simple extrapolation — EVs and solar make this inaccurate
- Underinvestment → congestion and outages; overinvestment → stranded assets

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Load Growth Modeling** | AI forecasts feeder/substation load 5–10 years ahead using EV adoption, urban growth, industry trends |
| **EV Infrastructure Planning** | Predict where EV charging demand will emerge → proactive grid reinforcement |
| **Substation Siting AI** | Optimal location for new substations based on demand, land cost, network topology |
| **Capital Prioritization** | Score all proposed capital projects by reliability impact, regulatory requirement, ROI |
| **Congestion Analysis** | Identify network bottlenecks limiting renewable integration |

---

### DOMAIN 20: Sustainability & ESG Reporting *(Corporate)*

**The Problem**
- ESG reporting requirements are growing rapidly (SEBI, GRI, CDP frameworks)
- Carbon footprint data is scattered across fuel, fleet, SF6, transmission losses
- SF6 (a powerful greenhouse gas in switchgear) leaks are hard to track
- Sustainability reports are manually compiled — slow and error-prone

**AI Opportunities**

| Use Case | Description |
|----------|-------------|
| **Carbon Footprint Aggregation AI** | Auto-collect and compute Scope 1/2/3 emissions from operations data |
| **SF6 Leak Detection** | Sensor + AI to detect SF6 leaks in switchgear — mandatory reporting + massive GHG impact |
| **ESG Report Generation** | AI drafts annual sustainability report from operational data + regulatory frameworks |
| **Renewable Certification Tracking** | Track and verify REC (Renewable Energy Certificates) compliance |

---

## Complete Priority Matrix — All 20 Domains

| # | Domain | Business Impact | Data Readiness | Speed to Value | Strategic Value | Priority |
|---|--------|----------------|----------------|----------------|-----------------|----------|
| 1 | Predictive Asset Failure | ★★★★★ | ★★★★ | ★★★★ | ★★★★★ | **P1** |
| 2 | Energy Theft / NTL | ★★★★★ | ★★★★ | ★★★★★ | ★★★★★ | **P1** |
| 9 | GIS Intelligence | ★★★★★ | ★★★ | ★★★ | ★★★★★ | **P1** |
| 10 | Asset Management (EAM) | ★★★★ | ★★★★ | ★★★ | ★★★★★ | **P1** |
| 3 | Outage Prediction | ★★★★ | ★★★★ | ★★★ | ★★★★ | **P2** |
| 11 | IT Service Desk AI | ★★★ | ★★★★★ | ★★★★★ | ★★★ | **P2** |
| 12 | Application Maintenance / AIOps | ★★★ | ★★★ | ★★★ | ★★★★ | **P2** |
| 7 | Customer Service AI | ★★★ | ★★★★★ | ★★★★★ | ★★★ | **P2** |
| 18 | MDM Intelligence | ★★★★ | ★★★★ | ★★★★ | ★★★ | **P2** |
| 15 | Procurement / SCM | ★★★ | ★★★ | ★★★ | ★★★ | **P3** |
| 4 | Demand Forecasting | ★★★★ | ★★★★ | ★★★ | ★★★★ | **P3** |
| 13 | Renewable / DER | ★★★★ | ★★★ | ★★ | ★★★★★ | **P3** |
| 14 | Safety & HSE AI | ★★★ | ★★★ | ★★★ | ★★★ | **P3** |
| 6 | Field Workforce | ★★★ | ★★★ | ★★★ | ★★★ | **P3** |
| 19 | Network Planning | ★★★★ | ★★★ | ★★ | ★★★★★ | **P3** |
| 5 | Vegetation Management | ★★★ | ★★ | ★★ | ★★★ | **P4** |
| 16 | HR & Workforce Dev | ★★ | ★★★ | ★★★ | ★★★ | **P4** |
| 8 | Regulatory / Compliance | ★★★ | ★★★ | ★★ | ★★★ | **P4** |
| 17 | Cybersecurity OT/IT | ★★★ | ★★ | ★★ | ★★★★ | **P4** |
| 20 | Sustainability / ESG | ★★ | ★★ | ★★ | ★★★ | **P4** |

---

## How These 20 Domains Group Into Platform Themes

```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│  GRID INTELLIGENCE PLATFORM     │   │  ENTERPRISE AI PLATFORM         │
│                                 │   │                                  │
│  1. Asset Failure Prediction    │   │  10. Asset Management (EAM)     │
│  2. NTL / Theft Detection       │   │  11. IT Service Desk AI         │
│  3. Outage Intelligence         │   │  12. AIOps / App Maintenance    │
│  4. Demand Forecasting          │   │  15. Procurement AI             │
│  9. GIS Intelligence            │   │  16. HR & Workforce AI          │
│  18. MDM Intelligence           │   │  20. ESG Reporting AI           │
└─────────────────────────────────┘   └─────────────────────────────────┘

┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│  CUSTOMER & REVENUE PLATFORM    │   │  FUTURE GRID PLATFORM           │
│                                 │   │                                  │
│  2. NTL Detection               │   │  13. Renewable / DER Mgmt       │
│  7. Customer Service AI         │   │  19. Network Planning AI        │
│  8. Compliance                  │   │  4. EV Load Forecasting         │
│  18. Meter Data Quality         │   │  17. OT Cybersecurity           │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

---

## The Recommended Starting Stack (Build in This Order)

```
FOUNDATION LAYER (Must have — everything else depends on this)
──────────────────────────────────────────────────────────────
  Domain 9:  GIS Intelligence — clean spatial data foundation
  Domain 10: Asset Management AI — clean asset master data

         ↓ (Build these once foundation is solid)

QUICK WIN LAYER (High ROI, Fast)
─────────────────────────────────
  Domain 2:  NTL Detection — immediate revenue recovery
  Domain 1:  Asset Failure Prediction — avoid capex surprises
  Domain 11: Service Desk AI — fast productivity wins

         ↓ (Build these to scale the platform)

INTELLIGENCE LAYER (Differentiation)
──────────────────────────────────────
  Domain 3:  Outage Intelligence
  Domain 18: MDM Intelligence
  Domain 12: AIOps

         ↓ (Build these for strategic positioning)

FUTURE LAYER (5-year horizon)
──────────────────────────────
  Domain 13: DER / Renewable Management
  Domain 19: Network Planning AI
  Domain 17: OT Cybersecurity
```

---

## Why GIS and Asset Management Are Actually Prerequisites

Most utilities want to jump straight to "predict failures" or "detect theft" — but the AI models underperform because the **underlying data is dirty**.

```
BAD GIS DATA
    │
    ├──► Transformer is in the wrong location in GIS
    │    → Model assigns it to wrong feeder
    │    → Predictions are for the wrong asset
    │
    ├──► Network topology is wrong
    │    → Fault isolation algorithm routes crew to wrong location
    │    → 2-hour delay

BAD EAM DATA
    │
    ├──► Transformer age is "unknown" in asset master
    │    → Age is the #1 feature in failure prediction
    │    → Model accuracy drops 30–40%
    │
    └──► Work order failure codes are blank/inconsistent
         → Can't train failure mode classifier
```

**Fix the data foundation first → all AI use cases perform dramatically better.**

---

*See `05_Utility_Industry_AI_Gaps.md` for deep-dive on the original 8 gaps.*
*See `02_Architecture.md` for the technical AI architecture to build these products.*
