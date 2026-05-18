# 2026-04-27 — ZENOPS Client Presentation Creation

## Context
- Working root: `C:\Projects\UCase\ZenOps\`
- Template: `nxzen PPT template.potx` (nxzen branding, 21 layouts, pearl/green colour scheme)
- Source docs: `ZENOPS_Business_Documentation 1.docx` + `ZENOPS_Technical_Documentation 1.docx`

## What Was Done
1. Explored folder structure: 2 Word docs + 1 POTX template
2. Extracted text from both .docx files using Python zipfile (binary files, Read tool can't handle them)
3. Converted POTX → PPTX by patching content type in the zip
4. Inspected 21 slide layouts; identified useful ones (0=title-green, 14=text-pearl, 19=section heading)
5. Generated a 22-slide client presentation using python-pptx 1.0.2

## Output
**`ZENOPS_Client_Presentation.pptx`** — 22 slides, ~1.9 MB

## Slide Structure
| # | Title | Type |
|---|-------|------|
| 1 | ZENOPS (title) | Title green |
| 2 | Today's Agenda | Content |
| 3 | THE PROBLEM | Section |
| 4 | The Enterprise IT Automation Gap | 5-card pain points |
| 5 | Why Now — Three Forces Aligning | 3-column |
| 6 | THE SOLUTION | Section |
| 7 | What Is ZENOPS? | Reads→Decides→Acts |
| 8 | How ZENOPS Works — Request Flow | Full architecture flow diagram |
| 9 | Real-World: New-Hire Onboarding | Before/After comparison |
| 10 | Use Cases | 6-card grid |
| 11 | ARCHITECTURE | Section |
| 12 | Current Architecture (Demo Phase 0) | Layered diagram with all components |
| 13 | MCP Layer: Demo vs Enterprise | Side-by-side comparison table |
| 14 | Target Enterprise Architecture | Full target diagram with layers |
| 15 | BUSINESS CASE | Section |
| 16 | Competitive Landscape | 4-row comparison table |
| 17 | ROI — The Numbers | 6-row table + 4 callout badges |
| 18 | Pricing Model | 3 tiers + usage + PS fees |
| 19 | Go-to-Market Strategy | 3 pillars + requirements |
| 20 | 6–10 Week Roadmap | 7-phase timeline + milestones |
| 21 | Next Steps | 4 CTA boxes |
| 22 | Thank You | Title green |

## Key Facts About ZENOPS (from docs)
- AI agent that resolves enterprise IT tickets cross-system (ServiceNow, Salesforce, SAP, MuleSoft)
- Uses MCP (Model Context Protocol, Anthropic 2024) — 54 tools in demo
- Current state: working demo with local clones, no auth, SQLite, single tenant
- 6-10 weeks to first paid pilot
- Target customer: 5,000 emp, 20k tickets/month, 30 service-desk FTEs
- ROI: 50-70% auto-resolve, USD 600k-900k saved/year, <6 month payback
- Pricing: USD 36k-300k+/year + USD 0.10-0.30/resolved ticket

## Technical Notes
- PowerShell was rejected by user; used Bash + Python for all file operations
- POTX requires content-type patch to open with python-pptx
- Architecture diagrams built from python-pptx shapes (rbox, hline, arrow helpers)
- Script saved at: `C:\Projects\UCase\ZenOps\create_zenops_ppt.py`
