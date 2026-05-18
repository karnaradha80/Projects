"""
ZENOPS Client Presentation — v2
Applies the exact SDLC_WM.pptx visual style:
  • Pearl (#F4F2F3) background on content slides
  • Dark (#030304) header bar (1.1") + footer bar (0.3")
  • Left accent line (0.07" wide) + right accent line + top-right badge
  • White title text (20pt bold) + green subtitle (9.5pt)
  • Card pattern: dark label bar (0.3") + pearl/white content area
  • Calibri font throughout
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import copy

# ── Paths ─────────────────────────────────────────────────────────────────────
SDLC_TEMPLATE = r'C:\Projects\SDLC\SDLC_WM.pptx'
OUT_PATH       = r'C:\Projects\UCase\ZenOps\ZENOPS_Client_Presentation_v2.pptx'

# ── Palette (matches SDLC_WM theme exactly) ───────────────────────────────────
DARK    = RGBColor(0x03, 0x03, 0x04)   # near-black
PEARL   = RGBColor(0xF4, 0xF2, 0xF3)  # slide background
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GREEN   = RGBColor(0x8D, 0xE9, 0x71)  # accent / subtitle colour
CYAN    = RGBColor(0x74, 0xD1, 0xEA)
PURPLE  = RGBColor(0xAD, 0x96, 0xDC)
YELLOW  = RGBColor(0xEC, 0xF1, 0x66)
RED     = RGBColor(0xFF, 0x71, 0x76)
LGRAY   = RGBColor(0xD8, 0xD4, 0xD5)
MIDGRAY = RGBColor(0x66, 0x66, 0x66)
DGREEN  = RGBColor(0x1B, 0x5E, 0x20)
DRED    = RGBColor(0xB7, 0x1C, 0x1C)

# ── Load template (SDLC) and clear existing slides ────────────────────────────
prs = Presentation(SDLC_TEMPLATE)
W = prs.slide_width    # 12192000 EMU = 13.33"
H = prs.slide_height   # 6858000  EMU = 7.50"

# Remove the 10 SDLC slides cleanly
from pptx.oxml.ns import qn
xml_slides = prs.slides._sldIdLst
for el in list(xml_slides):
    xml_slides.remove(el)

# ── Layout refs ───────────────────────────────────────────────────────────────
BLANK = prs.slide_layouts[6]   # "Blank" layout from SDLC master


# ══════════════════════════════════════════════════════════════════════════════
# SHAPE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
FONT = 'Calibri'

def _set_run(run, text, size_pt, bold=False, color=DARK, italic=False, font=FONT):
    run.text = text
    run.font.name  = font
    run.font.size  = Pt(size_pt)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color


def tb(slide, l, t, w, h, text, size=14, bold=False, color=DARK,
       align=PP_ALIGN.LEFT, wrap=True, italic=False):
    """Text box (measurements in inches)."""
    bx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = bx.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    _set_run(p.add_run(), text, size, bold, color, italic)
    return bx


def tb_ml(slide, l, t, w, h, lines, size=9, bold=False, color=DARK,
          align=PP_ALIGN.LEFT, wrap=True, line_spacing_pt=None):
    """Multi-line text box (list of strings → paragraphs)."""
    bx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = bx.text_frame
    tf.word_wrap = wrap
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        _set_run(p.add_run(), line, size, bold, color)
    return bx


def box(slide, l, t, w, h, fill, text='', size=9, text_color=WHITE,
        bold=False, line_color=None, align=PP_ALIGN.CENTER):
    """Filled rectangle (measurements in inches)."""
    shp = slide.shapes.add_shape(
        9,  # MSO rectangle
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line_color:
        shp.line.color.rgb = line_color
        shp.line.width     = Pt(0.5)
    else:
        shp.line.fill.background()
    if text:
        tf = shp.text_frame
        tf.word_wrap = True
        p  = tf.paragraphs[0]
        p.alignment = align
        _set_run(p.add_run(), text, size, bold, text_color)
    return shp


# ══════════════════════════════════════════════════════════════════════════════
# SDLC LAYOUT HELPERS — matching exact SDLC_WM measurements
# ══════════════════════════════════════════════════════════════════════════════

def add_slide():
    """Add a blank slide."""
    return prs.slides.add_slide(BLANK)


def set_bg(slide, color):
    """Set slide background fill."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def header(slide, accent, title, subtitle, badge='ZENOPS'):
    """SDLC-style dark header bar with left accent line."""
    box(slide, 0, 0, 13.33, 1.1, DARK)                           # dark bar
    box(slide, 0, 0, 0.07, 1.1, accent)                          # left accent line
    tb(slide, 0.18, 0.10, 9.8,  0.55, title,    20, True,  WHITE)  # title
    tb(slide, 0.18, 0.65, 10.2, 0.38, subtitle, 9.5, False, GREEN)  # subtitle
    box(slide, 13.26, 0,    0.07, 7.2,  accent)                   # right accent line
    box(slide, 11.88, 0.12, 1.3,  0.22, accent, badge, 8, DARK, True)  # badge


def footer(slide, left_text='ZENOPS  |  AI Co-Worker for Enterprise Operations  |  Confidential  |  April 2026'):
    """SDLC-style dark footer bar."""
    box(slide, 0,    7.2,  13.33, 0.3, DARK)
    tb(slide,  0.2,  7.22, 9.0,   0.25, left_text, 7, False, PEARL)
    tb(slide,  12.5, 7.22, 0.75,  0.25, '2026',    7, False, PEARL)


def label_bar(slide, x, y, w, text, bg=DARK, text_color=WHITE, size=9):
    """Dark label bar (h=0.3") above a content panel."""
    box(slide, x, y, w, 0.3, bg, text, size, text_color, True)


def content_area(slide, x, y, w, h, bg=PEARL, line_color=None):
    """Pearl content panel background."""
    box(slide, x, y, w, h, bg, line_color=line_color)


def card(slide, x, y, w, h, label, lines,
         label_bg=DARK, label_text_color=WHITE, content_size=9, accent=None):
    """
    SDLC-style card:
      dark label bar (h=0.3) → pearl content (h) → multi-line text box on top.
    """
    lh = 0.3
    label_bar(slide, x, y, w, label, label_bg, label_text_color)
    bg = PEARL if accent is None else WHITE
    content_area(slide, x, y + lh, w, h)
    tb_ml(slide, x + 0.1, y + lh + 0.06, w - 0.2, h - 0.1, lines, content_size)


def accent_row(slide, x, y, total_w, label, label_w, text, row_h=0.37,
               accent=GREEN, alt=False):
    """
    One row:  [accent label box | white/pearl text box]
    Matches SDLC slide-9/10 pattern exactly.
    """
    box(slide, x, y, label_w, row_h, accent, label, 9, DARK, True)
    bg = WHITE if not alt else PEARL
    box(slide, x + label_w, y, total_w - label_w, row_h, bg, line_color=LGRAY)
    tb(slide, x + label_w + 0.1, y + 0.04, total_w - label_w - 0.2, row_h - 0.08,
       text, 9, False, DARK)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)

box(s, 0, 0, 0.5, 7.5, GREEN)                             # left green bar
box(s, 0.5, 1.75, 7.8, 0.07, GREEN)                       # top line
box(s, 0.5, 3.9,  7.8, 0.07, GREEN)                       # bottom line

tb(s, 0.75, 1.95, 9.5, 0.65, 'ZENOPS',
   34, True, WHITE)
tb(s, 0.75, 2.65, 9.5, 0.55, 'AI Co-Worker for Enterprise Operations',
   18, False, GREEN)
tb(s, 0.75, 3.25, 9.5, 0.55, 'Reads incoming requests — Decides the actions — Acts across your enterprise systems',
   11, False, LGRAY, italic=True)
tb(s, 0.75, 4.1,  7.5, 0.4,  'Autonomous  ·  Auditable  ·  Always-On  ·  24/7',
   13, True, WHITE)

# Bottom strip — 6 coloured boxes (systems instead of phases)
strips = [
    (CYAN,   'ServiceNow'),
    (PURPLE, 'Salesforce'),
    (GREEN,  'SAP'),
    (YELLOW, 'MuleSoft'),
    (RED,    'Custom MCP'),
    (LGRAY,  'Enterprise'),
]
for i, (col, lbl) in enumerate(strips):
    x = i * (13.33 / 6)
    box(s, x, 6.65, 13.33 / 6, 0.55, col, lbl, 10, DARK, True)

tb(s, 0.75, 7.22, 10, 0.25, 'Confidential  |  2026  |  Internal Use Only', 7.5, False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Agenda (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'Agenda', 'Seven sections — from problem through to commercial & next steps')
footer(s)

agenda = [
    (RED,    '01', 'The Problem',            'The enterprise IT automation gap that costs billions every year'),
    (RED,    '02', 'Why Now',                'Three market forces aligning in 2024–2026 that make this possible'),
    (GREEN,  '03', 'The ZENOPS Solution',    'What it does, how it works, and a real-world before/after'),
    (CYAN,   '04', 'Architecture',           'Current demo state → target enterprise-grade architecture'),
    (PURPLE, '05', 'Business Case',          'ROI, competitive landscape, and pricing model'),
    (YELLOW, '06', 'Go-to-Market & Roadmap', '6–10 week path to first paid pilot'),
    (GREEN,  '07', 'Next Steps',             'Concrete actions to move from today to a scoped pilot'),
]
for i, (col, num, section, desc) in enumerate(agenda):
    y = 1.25 + i * 0.82
    box(s, 0.15, y, 0.52, 0.62, col, num, 16, DARK, True)
    tb(s, 0.8,  y + 0.03, 3.5,  0.28, section, 12, True,  DARK)
    tb(s, 0.8,  y + 0.33, 12.2, 0.28, desc,    9.5, False, MIDGRAY)
    box(s, 0.15, y + 0.65, 13.0, 0.02, LGRAY)              # thin divider

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Section: The Problem (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)
box(s, 0, 0,   0.5,  7.5,  RED)
box(s, 0.5, 2.1, 7.8, 0.07, RED)
box(s, 0.5, 4.2, 7.8, 0.07, RED)
tb(s, 0.75, 2.25, 11, 0.72, '01  —  THE PROBLEM', 32, True, WHITE)
tb(s, 0.75, 3.05, 10, 0.55, 'The Enterprise IT Automation Gap', 18, False, RED)
tb(s, 0.75, 3.65, 10, 0.45, 'Every large company runs the same tired pattern — and it costs them millions every year.',
   11, False, LGRAY, italic=True)
strips2 = [('Repetitive Work', RED), ('Slow Resolution', YELLOW), ('System Sprawl', CYAN),
           ('Off-Hours Gaps', PURPLE), ('Audit Risk', RED), ('High Cost', LGRAY)]
for i, (lbl, col) in enumerate(strips2):
    box(s, i * (13.33/6), 6.65, 13.33/6, 0.55, col, lbl, 9, DARK, True)
tb(s, 0.75, 7.22, 10, 0.25, 'ZENOPS  |  AI Co-Worker for Enterprise Operations  |  Confidential  |  April 2026',
   7, False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Enterprise Pain Points (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, RED, 'Enterprise IT Pain Points Today',
       'Five compounding problems that ZENOPS eliminates in one platform', '01 Problem')
footer(s)

# Left column — pain point rows
label_bar(s, 0.13, 1.22, 13.07, 'THE FIVE PAIN POINTS  —  with illustrative cost impact')
pain = [
    (RED,    'Repetitive Ticket Work',
             '70%+ of L1 agents\' day is password resets, account creations, and cross-system copy-paste. '
             'Teams of 50–500 people doing the same rote work every day. At USD 35–60k/yr per FTE, this is '
             'a significant and quantifiable cost.'),
    (YELLOW, 'Slow Resolution Times',
             'Employees wait 2+ hours for routine requests. Gartner: average employee loses ~30 min per IT ticket '
             'waiting. At 20,000 tickets/month across a 5,000-person company, that\'s 10,000 person-hours lost monthly.'),
    (CYAN,   'System Sprawl',
             'The same data exists in 3–5 platforms and someone copies it by hand — ServiceNow to Salesforce to SAP. '
             'Every copy is an error risk. "Swivel-chair integration" tax is real and invisible on the P&L.'),
    (PURPLE, 'Off-Hours Coverage Gaps',
             'A user in Singapore raises a critical ticket at 3 AM US time. Nothing moves until the US team wakes up. '
             'Global operations suffer and SLA metrics degrade despite the team doing their best.'),
    (RED,    'Inconsistent Quality & Audit Risk',
             'Different agents resolve the same issue differently. Access-change logs are incomplete. '
             'Auditors find gaps. Compliance posture is weaker than it should be — with no easy fix under the current model.'),
]
for i, (col, title, desc) in enumerate(pain):
    y = 1.55 + i * 1.1
    box(s, 0.13, y, 2.5, 1.0, col, title, 10, DARK, True)
    box(s, 2.63, y, 10.57, 1.0, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb(s, 2.73, y + 0.06, 10.37, 0.9, desc, 9, False, DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Why Now (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, RED, 'Why Now — Three Forces Aligning',
       'LLMs · MCP standard · Buyer mandate — all arrived together in 2024–2026', '01 Problem')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'THREE MARKET FORCES THAT MAKE ZENOPS POSSIBLE TODAY AT THE RIGHT PRICE')

forces = [
    (GREEN, '1',
     'LLMs Crossed the\nReliability Threshold',
     [
         'Large language models now reliably drive real business actions — not just answer questions.',
         'They can call APIs, select tools, complete multi-step tasks, and handle ambiguity with high accuracy.',
         'This crossed a threshold in 2024: the models are good enough to trust with consequential enterprise tasks.',
         '',
         'Before 2024: LLMs could draft an email.',
         'After 2024: LLMs can create a Salesforce account, open an SAP work order, and close the ServiceNow ticket.',
     ]),
    (PURPLE, '2',
     'Model Context Protocol\n(MCP) — Open Standard',
     [
         'Introduced by Anthropic in late 2024, MCP gives agents a common language to talk to enterprise systems.',
         'Salesforce, GitHub, Atlassian, ServiceNow are publishing official MCP connectors right now.',
         '',
         'We ride that wave instead of building 200 one-off integrations.',
         'Every new vendor MCP connector = a new capability for ZENOPS at near-zero incremental cost.',
         '',
         'MCP is to AI agents what REST was to web services — it is the plumbing that makes the ecosystem work.',
     ]),
    (CYAN, '3',
     'Buyer Demand at\nAll-Time High',
     [
         'Every major CIO survey in 2025–2026 lists "agentic AI for IT operations" as a top-three priority.',
         'Boards are mandating AI ROI. "Do more with less" is the dominant IT leadership brief worldwide.',
         '',
         'The question is no longer IF — it is WHO and WHEN.',
         'ZENOPS is positioned to be the WHO for cross-platform IT operations.',
         '',
         'Buying cycles are faster than ever: pilots can be approved in weeks, not quarters.',
     ]),
]
col_w = (13.33 - 0.26) / 3
for i, (col, num, title, lines) in enumerate(forces):
    x = 0.13 + i * col_w
    box(s, x, 1.55, col_w - 0.08, 0.75, col, f'{num}  {title}', 11, DARK, True)
    card(s, x, 2.3, col_w - 0.08, 4.7, 'DETAIL', lines, DARK, WHITE, 9)

# Bottom principle
label_bar(s, 0.13, 7.05, 13.07,
    '→  These three forces together — for the first time — let an agent replace the human swivel-chair work across ALL enterprise systems.',
    DARK, GREEN, 8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Section: Solution (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)
box(s, 0, 0, 0.5, 7.5, GREEN)
box(s, 0.5, 2.1, 7.8, 0.07, GREEN)
box(s, 0.5, 4.2, 7.8, 0.07, GREEN)
tb(s, 0.75, 2.25, 11, 0.72, '02 + 03  —  THE ZENOPS SOLUTION', 30, True, WHITE)
tb(s, 0.75, 3.05, 10, 0.55, 'What It Is, How It Works, and the Real-World Impact', 18, False, GREEN)
tb(s, 0.75, 3.65, 10, 0.45,
   'An AI co-worker that reads requests in plain language, decides what to do, and acts across all your enterprise systems.',
   11, False, LGRAY, italic=True)
strips3 = [('READS', GREEN), ('DECIDES', PURPLE), ('ACTS', CYAN),
           ('24/7', YELLOW), ('Auditable', RED), ('Secure', LGRAY)]
for i, (lbl, col) in enumerate(strips3):
    box(s, i * (13.33/6), 6.65, 13.33/6, 0.55, col, lbl, 10, DARK, True)
tb(s, 0.75, 7.22, 10, 0.25, 'ZENOPS  |  AI Co-Worker for Enterprise Operations  |  Confidential  |  April 2026',
   7, False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — What Is ZENOPS (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'What Is ZENOPS?',
       'A new kind of employee: same system access, same permissions — never sleeps, never makes a typo', '02 Solution')
footer(s)

# Three-step visual matching SDLC phase-overview style
steps = [
    (CYAN,   'READS',
     ['Incoming employee and customer requests in plain language:',
      '',
      '  "Reset my password"',
      '  "Onboard Priya Shah, joining 1 May, Sales, Mumbai"',
      '  "Create a new vendor — Acme Corp"',
      '  "Show me everything we know about this customer"',
      '',
      'No special syntax. No ticketing forms. Just a plain-language request.']),
    (PURPLE, 'DECIDES',
     ['Classifies the request and selects the right actions:',
      '',
      '  Fast-path handler  →  deterministic, no LLM cost',
      '  (common patterns: password reset, account create)',
      '',
      '  AI path  →  LLM selects tools from the 54-tool catalog',
      '  (complex or novel requests)',
      '',
      'Same logic a senior service-desk agent would apply — in milliseconds.']),
    (GREEN,  'ACTS',
     ['Executes actions directly inside your enterprise systems:',
      '',
      '  sf_create_user        →  Salesforce CRM',
      '  sap_create_user        →  SAP HR record',
      '  sap_create_work_order  →  laptop provisioning',
      '  send_email             →  welcome email',
      '  sn_close_ticket        →  ticket closed & logged',
      '',
      '24/7 · in seconds · full audit trail · reversible.']),
]
col_w = (13.33 - 0.26) / 3
for i, (col, label, lines) in enumerate(steps):
    x = 0.13 + i * col_w
    # Arrow between steps
    if i > 0:
        tb(s, x - 0.22, 2.55, 0.22, 0.5, '→', 18, True, DARK, PP_ALIGN.CENTER)
    box(s, x, 1.25, col_w - 0.08, 0.7, col, label, 16, DARK, True)
    card(s, x, 1.95, col_w - 0.08, 4.95, 'HOW', lines, DARK, WHITE, 9)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Request Flow Diagram (Pearl) — SDLC row style
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'How ZENOPS Works — Request Flow',
       'Step-by-step: from ticket submission to resolved action across enterprise systems', '02 Solution')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'END-TO-END REQUEST LIFECYCLE')

flow = [
    (CYAN,   'Step 1  —  INBOUND',
             'User submits a request via ServiceNow, Client Portal, Email, or API webhook. '
             'ServiceNow auto-forwarder posts ticket to the Ticket Orchestrator (FastAPI, port 2486).'),
    (CYAN,   'Step 2  —  CLASSIFY',
             'Ticket Orchestrator classifies the action type: PASSWORD_RESET · USER_CREATION · WORK_ORDER · '
             'CASE · CROSS_PLATFORM_LOOKUP · APPROVAL. Sets priority, stores in DB, marks status PENDING.'),
    (PURPLE, 'Step 3  —  ROUTE',
             'NetworkOpsAgent continuous processor (polls every 10 s) picks up PENDING tickets. '
             'Evaluates: does a fast-path deterministic handler match? If YES → fast path. If NO → AI path.'),
    (GREEN,  'Step 4a  —  FAST PATH (60–80% of volume)',
             'Hand-coded handler executes the tool call sequence directly via MCP Hub. Zero LLM cost. '
             'Sub-second resolution. Common ticket types: password reset, account create, status lookup.'),
    (YELLOW, 'Step 4b  —  AI PATH (complex/novel requests)',
             'Mistral / Claude receives the ticket text plus the full 54-tool catalog. '
             'LLM selects tools and arguments. Agent executes each tool call via MCP Hub. '
             'Result is returned and the LLM posts a closure note.'),
    (RED,    'Step 5  —  MCP EXECUTION',
             'MCP Unified Hub (54 tools, stdio transport today / HTTP+SSE in enterprise) receives tool calls. '
             'Each tool is a thin wrapper over the target system\'s REST API — Salesforce · ServiceNow · SAP · MuleSoft.'),
    (LGRAY,  'Step 6  —  CLOSE & AUDIT',
             'Agent posts result back to Orchestrator → status set RESOLVED. '
             'Source system (ServiceNow) receives the closure note via API. '
             'Full audit row written: ticket_id · tool · arguments · response · timestamp · agent_version.'),
]
for i, (col, label, desc) in enumerate(flow):
    y = 1.55 + i * 0.81
    box(s, 0.13, y, 3.0, 0.72, col, label, 8.5, DARK, True)
    box(s, 3.13, y, 10.07, 0.72, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb(s, 3.23, y + 0.06, 9.87, 0.62, desc, 9, False, DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Before vs After (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'Real-World Example: New-Hire Onboarding',
       'The same ticket — 2–6 hours of human effort vs 30 seconds of autonomous execution', '02 Solution')
footer(s)

# Two columns
box(s, 0.13, 1.22, 6.45, 0.3, RED, 'BEFORE ZENOPS  —  Manual Process', 9, WHITE, True)
before = [
    '1.  Manager files ticket in ServiceNow',
    '2.  Queue wait:  30 minutes – 2 hours',
    '3.  Agent logs into Salesforce →  creates user record',
    '4.  Agent logs into SAP HR  →  creates employee record',
    '5.  Agent opens SAP work order for laptop provisioning',
    '6.  Agent posts KB link to new hire and sends welcome email',
    '7.  Agent emails manager with completion confirmation',
    '8.  Agent closes ticket manually in ServiceNow',
    '',
    '⏱  Total elapsed time:   2 – 6 hours',
    '👥  People involved:       2 – 3 agents',
    '💸  Cost:                  ~1 FTE-hour of L1 agent time',
    '❌  Audit trail:           incomplete / manual notes',
]
box(s, 0.13, 1.52, 6.45, 5.55, WHITE, line_color=LGRAY)
tb_ml(s, 0.23, 1.58, 6.25, 5.4, before, 10, False, DARK)

box(s, 6.75, 1.22, 6.45, 0.3, GREEN, 'WITH ZENOPS  —  Autonomous Execution', 9, DARK, True)
after = [
    '1.  Manager files the same ticket in ServiceNow',
    '2.  Orchestrator classifies:  USER_ONBOARDING  (instant)',
    '3.  Agent reads ticket — plain language, no parsing rules',
    '',
    '4.  MCP tool calls executed in sequence:',
    '       sf_create_user         →  Salesforce record created',
    '       sap_create_user        →  SAP HR record created',
    '       sap_create_work_order  →  laptop work order raised',
    '       send_email             →  welcome email dispatched',
    '       sn_close_ticket        →  ticket closed & logged',
    '',
    '⏱  Total elapsed time:   ~30 seconds',
    '👥  People involved:       0  (exceptions only)',
    '✅  Audit trail:           complete — every tool call logged',
]
box(s, 6.75, 1.52, 6.45, 5.55, WHITE, line_color=LGRAY)
tb_ml(s, 6.85, 1.58, 6.25, 5.4, after, 10, False, DARK)

# Divider line between columns
box(s, 6.63, 1.22, 0.04, 5.85, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Use Cases (Pearl) — SDLC row style
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'Use Cases ZENOPS Handles Today',
       '54 tools across 4 enterprise systems — growing as the MCP ecosystem expands', '02 Solution')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'USE CASE CATEGORIES  —  current scope in the demo build')

use_cases = [
    (CYAN,   'Identity & Access Management',
             'Password resets  ·  Account creation  ·  Access request provisioning  ·  Role assignment  ·  User deactivation / offboarding'),
    (PURPLE, 'Employee Lifecycle',
             'New-hire onboarding (full cross-system stack)  ·  Role & location transfers  ·  Equipment provisioning via SAP work orders'),
    (GREEN,  'Customer & Vendor Records',
             'New contact / account creation across CRM + ERP  ·  Vendor onboarding  ·  Service case creation and intelligent routing'),
    (YELLOW, 'Approvals & Change Management',
             'Work order creation and approval  ·  Expense line routing  ·  Low-risk change management requests  ·  CAB-ready summaries'),
    (RED,    'Cross-System Insight & Reporting',
             '360° customer view across Salesforce + ServiceNow  ·  Enterprise health dashboard  ·  Ticket triage and escalation routing'),
    (LGRAY,  'Integration & Operations',
             'MuleSoft route status checks  ·  Cross-platform data sync validation  ·  Scheduled batch operation triggers  ·  Health checks'),
]
for i, (col, title, desc) in enumerate(use_cases):
    y = 1.55 + i * 0.91
    box(s, 0.13, y, 2.8,  0.82, col, title, 10, DARK, True)
    box(s, 2.93, y, 10.27, 0.82, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb(s, 3.03, y + 0.1, 10.07, 0.7, desc, 9.5, False, DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Section: Architecture (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)
box(s, 0, 0, 0.5, 7.5, CYAN)
box(s, 0.5, 2.1, 7.8, 0.07, CYAN)
box(s, 0.5, 4.2, 7.8, 0.07, CYAN)
tb(s, 0.75, 2.25, 11, 0.72, '04  —  ARCHITECTURE', 32, True, WHITE)
tb(s, 0.75, 3.05, 10, 0.55, 'Current Demo State  →  Target Enterprise Architecture', 18, False, CYAN)
tb(s, 0.75, 3.65, 10, 0.45,
   'MCP-native from day one. The gap to enterprise is multi-tenancy, remote transport, auth, and Kubernetes.',
   11, False, LGRAY, italic=True)
strips4 = [('Demo: Phase 0', MIDGRAY), ('Phase 1: Security', RED), ('Phase 2: Foundation', YELLOW),
           ('Phase 3: MCP Routing', PURPLE), ('Phase 4: Real APIs', GREEN), ('Phase 5: Production', CYAN)]
for i, (lbl, col) in enumerate(strips4):
    box(s, i * (13.33/6), 6.65, 13.33/6, 0.55, col, lbl, 8, DARK, True)
tb(s, 0.75, 7.22, 10, 0.25, 'ZENOPS  |  AI Co-Worker for Enterprise Operations  |  Confidential  |  April 2026',
   7, False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Current Architecture (Pearl) — SDLC layered card style
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, CYAN, 'Current Architecture — Demo (Phase 0)',
       'Single-tenant · Local Docker Compose · No auth · SQLite · stdio MCP transport', '04 Architecture')
footer(s)

# Left margin layer labels + right content rows
# Using SDLC row pattern: accent label | white content
layers = [
    (CYAN,   'FRONTEND\nCHANNELS',
             'Client Portal (React 18 + nginx, port 2005)  ·  ServiceNow Frontend (React, port 4780)  '
             '·  Auto-forwarder pushes new tickets to the Orchestrator via REST'),
    (DARK,   'TICKET\nORCHESTRATOR',
             'FastAPI service (port 2486) · SQLite store · Classifies tickets by action_type '
             '(PASSWORD_RESET, USER_CREATION, WORK_ORDER, CASE, ...) · Routes to agent · Stores state'),
    (PURPLE, 'NETWORK OPS\nAGENT',
             'FastAPI service (port 7532) · Mistral Agents API (cloud) · '
             'Continuous Processor polls Orchestrator every 10 s · '
             'Fast-path handlers (lines 768–1118) for common types · MCPHub client (stdio)'),
    (YELLOW, 'MCP UNIFIED\nHUB',
             'mcp_unified.py · Single monolithic MCP server · 54 tools: '
             'Salesforce (8) · ServiceNow (10) · SAP (12) · MuleSoft (6) · Cross-platform (18) '
             '· stdio transport (agent + MCP must share the same host) · No auth between agent and MCP'),
    (MIDGRAY,'ENTERPRISE\nBACKENDS',
             'ServiceNow clone (port 4780 / db 4793)  ·  Salesforce clone (port 4799 / db 4791)  '
             '·  SAP clone (port 4798 / db 4794)  ·  MuleSoft clone (port 4797 / db 4792)  '
             '·  ⚠  ALL ARE LOCAL CLONES — no real Salesforce / SAP / ServiceNow traffic today'),
]
lbl_w = 1.6
content_w = 11.47
for i, (col, lbl, desc) in enumerate(layers):
    y = 1.22 + i * 1.17
    box(s, 0.13, y, lbl_w, 1.08, col, lbl, 9, DARK if col in (YELLOW, CYAN, LGRAY) else WHITE, True)
    box(s, 1.73, y, content_w, 1.08, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb(s, 1.83, y + 0.1, content_w - 0.2, 0.9, desc, 9, False, DARK, wrap=True)
    if i < 4:
        tb(s, 0.13 + lbl_w/2 - 0.1, y + 1.08, 0.2, 0.09, '▼', 8, True, MIDGRAY, PP_ALIGN.CENTER)

# Known issues note
label_bar(s, 0.13, 7.05, 13.07,
    '⚠  Known gaps: hardcoded credentials (admin123/changeme)  ·  CORS wildcard ["*"]  '
    '·  no retries / circuit breaker  ·  no tests  ·  no observability',
    RED, WHITE, 7.5)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — MCP Demo vs Enterprise (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, CYAN, 'MCP Layer: Demo vs Enterprise',
       'The protocol is the same — the gap is transport, auth, tenancy, and scale', '04 Architecture')
footer(s)

label_bar(s, 0.13, 1.22, 13.07,
    'MODEL CONTEXT PROTOCOL (MCP)  —  Anthropic open standard 2024  ·  already in production in our demo')

dims = [
    ('Transport',        'stdio subprocess (local only)',          'HTTP + SSE / Streamable HTTP · mTLS optional'),
    ('Auth',             'None — stdio = trusted child process',   'OAuth 2.1 (client-credentials) · API key · per-tenant tokens'),
    ('Multi-tenancy',    'Single tenant — one customer only',      'tenant_id on every record · row-level Postgres security'),
    ('MCP Routing',      'Hardcoded path to mcp_unified.py',       'MCP Gateway: N servers · tool→server registry · conflict resolution'),
    ('Tool Surface',     '54 tools · static list in source code',  '100s of tools · paginated list_tools · versioned manifests'),
    ('Audit Log',        'Basic Python logging only',              'Append-only immutable log · tenant · request_id · tool call · response'),
    ('Reliability',      'No retries · no circuit breaker · no DLQ', 'Tenacity retries · circuit breaker per MCP · DLQ for poison tickets'),
    ('Scale',            'Local Docker Compose · single host',     'Kubernetes · HPA · blue-green · multi-AZ · health probes'),
]
# Header row
box(s, 0.13, 1.55, 3.3,  0.38, DARK,   'DIMENSION',        10, WHITE, True)
box(s, 3.43, 1.55, 4.35, 0.38, RED,    'OUR DEMO STATE',   10, WHITE, True)
box(s, 7.78, 1.55, 5.42, 0.38, GREEN,  'ENTERPRISE TARGET', 10, DARK,  True)

for i, (dim, cur, tgt) in enumerate(dims):
    y = 1.93 + i * 0.64
    bg = PEARL if i % 2 == 0 else WHITE
    box(s, 0.13, y, 3.3,  0.6, bg, dim, 9, DARK, True, LGRAY)
    box(s, 3.43, y, 4.35, 0.6, RGBColor(0xFF,0xEE,0xEE), line_color=LGRAY)
    tb(s, 3.53, y + 0.08, 4.15, 0.5, cur, 8.5, False, DRED, wrap=True)
    box(s, 7.78, y, 5.42, 0.6, RGBColor(0xEE,0xFF,0xEE), line_color=LGRAY)
    tb(s, 7.88, y + 0.08, 5.22, 0.5, tgt, 8.5, False, DGREEN, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Target Enterprise Architecture (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, CYAN, 'Target Enterprise Architecture',
       'Multi-tenant · Kubernetes · OAuth 2.1 · MCP Gateway · OpenTelemetry · SOC 2', '04 Architecture')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'TARGET TOPOLOGY  —  SaaS default · Hybrid (agent in customer VPC) · Self-hosted (Helm chart)')

target_layers = [
    (CYAN,   'API\nGATEWAY',
             'Kong  ·  TLS termination  ·  WAF  ·  JWT verification  ·  Rate limiting per tenant  ·  OpenTelemetry traces on every request'),
    (DARK,   'CONTROL\nPLANE',
             'Ticket Orchestrator (PostgreSQL + Redis)  ·  Tenant Admin UI (React)  ·  Webhook Ingress (ServiceNow forwarder)  '
             '·  Event bus (Redis Streams / NATS): ticket.created · classified · completed · failed'),
    (PURPLE, 'AGENT\nWORKERS',
             'k8s Deployment · HPA (auto-scale by ticket queue depth) · '
             'Fast-path handlers · LLM path (Claude / Mistral / OpenAI — configurable per tenant) · '
             'MCPManager (multi-server) loads tenant MCP set at session start from Secrets Manager'),
    (YELLOW, 'MCP\nGATEWAY',
             'New service — extends current mcp_manager.py · Routes by tenant_id + tool_name · '
             'Injects per-tenant OAuth 2.1 tokens from Vault / AWS SM · '
             'Circuit breaker per MCP · Retries with back-off · DLQ for poison messages · Full audit log'),
    (MIDGRAY,'ENTERPRISE\nMCPs',
             'ServiceNow MCP (official)  ·  Salesforce MCP (official)  ·  SAP S/4 MCP (custom thin wrapper over SAP REST APIs)  '
             '·  GitHub · Atlassian · Microsoft Graph MCP connectors as needed per customer'),
]
lbl_w = 1.6
cw = 11.47
for i, (col, lbl, desc) in enumerate(target_layers):
    y = 1.55 + i * 1.1
    box(s, 0.13, y, lbl_w, 1.0, col, lbl, 9, DARK if col in (YELLOW, CYAN, LGRAY) else WHITE, True)
    box(s, 1.73, y, cw, 1.0, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb(s, 1.83, y + 0.08, cw - 0.2, 0.85, desc, 9, False, DARK, wrap=True)
    if i < 4:
        tb(s, 0.13 + lbl_w/2 - 0.1, y + 1.0, 0.2, 0.1, '▼', 8, True, MIDGRAY, PP_ALIGN.CENTER)

label_bar(s, 0.13, 7.05, 13.07,
    'Cross-cutting: Secrets Manager (Vault/AWS SM)  ·  OpenTelemetry → Tempo + Prometheus + Loki  ·  Postgres audit log  ·  S3 object store',
    DARK, GREEN, 7.5)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — Section: Business Case (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)
box(s, 0, 0, 0.5, 7.5, PURPLE)
box(s, 0.5, 2.1, 7.8, 0.07, PURPLE)
box(s, 0.5, 4.2, 7.8, 0.07, PURPLE)
tb(s, 0.75, 2.25, 11, 0.72, '05  —  BUSINESS CASE', 32, True, WHITE)
tb(s, 0.75, 3.05, 10, 0.55, 'ROI · Competition · Pricing', 18, False, PURPLE)
tb(s, 0.75, 3.65, 10, 0.45,
   'Numbers a CFO will sign off on in under 10 minutes. Payback period under 6 months.',
   11, False, LGRAY, italic=True)
strips5 = [('50–70%\nauto-resolve', GREEN), ('USD 600k–900k\nsaved/yr', PURPLE), ('<30 sec\nresolution', CYAN),
           ('<6 months\npayback', YELLOW), ('70–80%\ngross margin', RED), ('SOC 2\nType I', LGRAY)]
for i, (lbl, col) in enumerate(strips5):
    box(s, i * (13.33/6), 6.45, 13.33/6, 0.75, col, lbl, 9, DARK, True)
tb(s, 0.75, 7.22, 10, 0.25, 'ZENOPS  |  AI Co-Worker for Enterprise Operations  |  Confidential  |  April 2026',
   7, False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Competitive Landscape (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, PURPLE, 'Competitive Landscape',
       'Every category leaves a gap — cross-system IT orchestration — that ZENOPS fills', '05 Business Case')
footer(s)

label_bar(s, 0.13, 1.22, 13.07,
    'COMPETITIVE POSITIONING  —  why each alternative falls short for cross-system enterprise IT ops')

comp = [
    (CYAN,   'Big Platform AI\n(Now Assist, Copilot, Einstein)',
             'Microsoft, Salesforce,\nServiceNow themselves',
             '✗ Works only inside their own platform\n✗ No cross-system orchestration\n✗ Each vendor incentivised to keep you in their walled garden',
             '✓ Works ACROSS all platforms simultaneously\n✓ Vendor-agnostic — additive, not rip-and-replace\n✓ Bridges the gaps no single vendor will ever fix'),
    (PURPLE, 'RPA\n(UiPath, AA, Blue Prism)',
             'Long-established\nenterprise RPA',
             '✗ Brittle UI scripts — break on any screen change\n✗ No natural language understanding\n✗ High maintenance burden at scale',
             '✓ API-native + AI reasoning — adapts to change\n✓ Handles requests it has never seen before\n✓ MCP standard vs fragile screen-scrapers'),
    (GREEN,  'AI Agent Startups\n(Sierra, Decagon, Kore.ai)',
             'Customer-support\nfocused agents',
             '✗ Customer-facing chatbots, not IT ops\n✗ Limited internal system integration depth\n✗ Different buyer (customer success vs CIO)',
             '✓ Internal IT/ops buyer: CIO and Head of IT Ops\n✓ Multi-system orchestration (ServiceNow + SAP + Salesforce)\n✓ Enterprise audit trail and compliance posture'),
    (YELLOW, 'Custom In-House Build',
             'Large enterprises\ntrying to self-build',
             '✗ 12–18 months build time\n✗ 10-person engineering team required\n✗ Ongoing maintenance and on-call burden',
             '✓ Pilot in 2–4 weeks — production in 6–10 weeks\n✓ MCP standard: plug in vendor connectors as they publish\n✓ Shared SaaS platform costs across all customers'),
]
# Header row
hs = [0.13, 2.13, 4.63, 7.13]
hw = [2.0,  2.5,  2.5,  6.07]
hlabels = ['CATEGORY', 'VENDOR', 'THEIR GAP', 'ZENOPS ADVANTAGE']
hcolors = [DARK, DARK, RED, GREEN]
htc     = [WHITE, WHITE, WHITE, DARK]
for j, (x, w, lbl, hc, htcc) in enumerate(zip(hs, hw, hlabels, hcolors, htc)):
    box(s, x, 1.55, w, 0.38, hc, lbl, 9, htcc, True)

for i, (col, cat, who, gap, adv) in enumerate(comp):
    y = 1.93 + i * 1.3
    bg = WHITE if i % 2 == 0 else PEARL
    box(s, 0.13, y, 2.0,  1.22, col, cat, 9, DARK, True, LGRAY)
    box(s, 2.13, y, 2.5,  1.22, bg, line_color=LGRAY)
    tb(s, 2.23, y + 0.08, 2.3, 1.1, who, 9, False, DARK, wrap=True)
    box(s, 4.63, y, 2.5,  1.22, RGBColor(0xFF,0xEE,0xEE), line_color=LGRAY)
    tb(s, 4.73, y + 0.05, 2.3, 1.1, gap, 8.5, False, DRED, wrap=True)
    box(s, 7.13, y, 6.07, 1.22, RGBColor(0xEE,0xFF,0xEE), line_color=LGRAY)
    tb(s, 7.23, y + 0.05, 5.87, 1.1, adv, 8.5, False, DGREEN, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — ROI (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, PURPLE, 'ROI — The Numbers a CFO Will Recognise',
       'Representative profile: 5,000 employees · 20,000 tickets/month · 30 service-desk FTEs', '05 Business Case')
footer(s)

label_bar(s, 0.13, 1.22, 13.07,
    'QUANTIFIED ANNUAL IMPACT  —  5,000-employee enterprise, 20k tickets/month, 30 service-desk FTEs')

roi = [
    ('Tickets auto-resolved',             '0%',                   '50 – 70%',        'Material productivity uplift across the whole workforce'),
    ('Avg. resolution time — routine',    '2 hours',              '< 1 minute',       'Faster employees and customers — SLA dramatically improved'),
    ('Service-desk headcount required',   '30 FTE',               '12 – 18 FTE',      'USD 600,000 – 900,000 saved per year in salary alone'),
    ('After-hours ticket coverage',       'Manual on-call gaps',  '24/7 automated',   'Better SLA, lower agent attrition, happier global employees'),
    ('Audit posture on access changes',   'Frequent gaps',        'Full audit log',   'Compliance risk reduced — every action logged with who/what/when'),
    ('Payback period at list pricing',    '—',                    '< 6 months',       'CFO-friendly ROI with quantifiable cost avoidance from month one'),
]
# Header row
for j, (lbl, x, w, hc, htc) in enumerate(zip(
    ['METRIC', 'TODAY', 'WITH ZENOPS', 'ANNUAL IMPACT'],
    [0.13, 3.83, 6.23, 8.93],
    [3.7, 2.4, 2.7, 4.27],
    [DARK, RED, GREEN, PURPLE],
    [WHITE, WHITE, DARK, WHITE]
)):
    box(s, x, 1.55, w, 0.4, hc, lbl, 10, htc, True)

for i, (metric, today, after, impact) in enumerate(roi):
    y = 1.95 + i * 0.84
    bg = WHITE if i % 2 == 0 else PEARL
    box(s, 0.13, y, 3.7,  0.75, bg, metric, 9.5, DARK, True, LGRAY)
    box(s, 3.83, y, 2.4,  0.75, RGBColor(0xFF,0xEE,0xEE), line_color=LGRAY)
    tb(s, 3.93, y + 0.1, 2.2, 0.6, today, 9, False, DRED)
    box(s, 6.23, y, 2.7,  0.75, RGBColor(0xEE,0xFF,0xEE), line_color=LGRAY)
    tb(s, 6.33, y + 0.1, 2.5, 0.6, after, 9, True,  DGREEN)
    box(s, 8.93, y, 4.27, 0.75, bg, line_color=LGRAY)
    tb(s, 9.03, y + 0.1, 4.07, 0.6, impact, 9, False, DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Pricing Model (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, PURPLE, 'Pricing Model',
       'Two-part: fixed platform fee + usage fee that scales with value delivered', '05 Business Case')
footer(s)

label_bar(s, 0.13, 1.22, 13.07,
    'PLATFORM FEE (annual)  —  covers agent runtime · admin UI · audit · standard connectors · tiered by company size')

tiers = [
    (CYAN,   'STARTER',
     'Up to 1,000 employees',
     'USD 36,000 / year\n(USD 3,000 / month)',
     ['• Standard connectors (ServiceNow + one CRM/ERP)',
      '• Core ticket types included',
      '• Email support',
      '• Up to 5,000 auto-resolved tickets/month included']),
    (PURPLE, 'GROWTH',
     '1,000 – 10,000 employees',
     'USD 120,000 / year\n(USD 10,000 / month)',
     ['• All standard connectors',
      '• Custom fast-path rule configuration',
      '• Dedicated Customer Success Manager',
      '• Up to 25,000 auto-resolved tickets/month included']),
    (GREEN,  'ENTERPRISE',
     '10,000+ employees',
     'USD 300,000+ / year\n(custom)',
     ['• Custom MCP integrations built to spec',
      '• Hybrid VPC deployment option',
      '• SLA guarantee (99.9%) + on-call',
      '• Unlimited tickets · SOC 2 Type I']),
]
col_w = (13.33 - 0.26) / 3
for i, (col, name, size_lbl, price, features) in enumerate(tiers):
    x = 0.13 + i * col_w
    w = col_w - 0.08
    box(s, x, 1.55, w, 0.48, col,  name,     13, DARK, True)
    box(s, x, 2.03, w, 0.3,  DARK, size_lbl, 8.5, col,  False)
    box(s, x, 2.33, w, 0.65, DARK, price,    12, WHITE, True)
    box(s, x, 2.98, w, 2.85, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb_ml(s, x + 0.1, 3.04, w - 0.2, 2.7, features, 10, False, DARK)

label_bar(s, 0.13, 5.88, 13.07,
    'USAGE FEE  —  USD 0.10 – 0.30 per auto-resolved ticket above tier quota  '
    '(you pay more only when we resolve more tickets for you)',
    DARK, GREEN, 9)
box(s, 0.13, 6.21, 13.07, 0.6, PEARL, line_color=LGRAY)
tb(s, 0.23, 6.27, 12.87, 0.5,
   'Professional Services (one-time):  USD 25,000 – 100,000 per engagement  '
   '—  integration setup · custom connector build · fast-path automation tuning',
   9.5, False, DARK, wrap=True)
label_bar(s, 0.13, 6.84, 13.07,
    'Target gross margin: 70 – 80%  ·  LLM cost mitigated by fast-path covering 60–80% of volume at zero LLM cost',
    DARK, LGRAY, 7.5)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — Go-to-Market (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, YELLOW, 'Go-to-Market Strategy',
       'Pilot-first · Partner-led · Land and expand — starting in India and the Middle East', '06 GTM')
footer(s)

# Phase banner
box(s, 0.13, 1.22, 6.85, 0.3, CYAN,   'PHASE 1 (NOW):  India & Middle East  —  fastest buying cycles, strongest network', 8.5, DARK, True)
box(s, 7.0,  1.22, 6.2,  0.3, PURPLE, 'PHASE 2 (Month 6+):  North America & Europe', 8.5, WHITE, True)

# Three pillars
pillars = [
    (GREEN,  'Design Partners\n(First 6 Months)',
     ['2 design partners — 1 financial services, 1 manufacturing',
      '',
      'Heavy discount in exchange for:',
      '  • Case studies with named ROI figures',
      '  • Reference calls for new prospects',
      '  • Roadmap input (shapes our backlog)',
      '',
      'Goal: one public ROI number we can sell against for Series A.',
      'Target payback story: "saved USD 750k in Year 1, paid back in 4 months"']),
    (PURPLE, 'Partner-Led\nSales Channel',
     ['ServiceNow Store · Salesforce AppExchange · SAP Marketplace',
      '',
      'Partner marketplace listing provides:',
      '  • Procurement-friendly path (no new vendor approval)',
      '  • CIO air cover ("endorsed by ServiceNow")',
      '  • Inbound lead flow from marketplace search',
      '',
      'Presence at: Dreamforce · ServiceNow World Forum · SAP Sapphire']),
    (CYAN,   'Pilot-First\nConversion Model',
     ['6-week paid pilot scoped to ONE use case',
      '(e.g., password resets + onboarding only)',
      '',
      'Process:',
      '  1.  Agree ROI target upfront (e.g., 50% auto-resolve)',
      '  2.  Run pilot against real ServiceNow instance',
      '  3.  Hit the target → convert to annual contract',
      '',
      'Land & expand: each new use case = config, not code']),
]
col_w = (13.33 - 0.26) / 3
for i, (col, title, lines) in enumerate(pillars):
    x = 0.13 + i * col_w
    w = col_w - 0.08
    box(s, x, 1.55, w, 0.62, col, title, 11, DARK, True)
    card(s, x, 2.17, w, 4.72, 'DETAIL', lines, DARK, WHITE, 9)

label_bar(s, 0.13, 6.92, 13.07,
    'Sales Motion:  CIO / Head of IT Ops (top-down buyer)  ←  Service-desk manager (daily champion)',
    DARK, GREEN, 8.5)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — Roadmap (Pearl) — SDLC phase-overview style
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, YELLOW, '6–10 Week Engineering Roadmap to First Paid Pilot',
       'Additive build — nothing thrown away; each phase is independently deployable', '06 GTM')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'PHASED ROADMAP  —  Phase 0 decisions first; client-ready at end of Phase 6')

phases = [
    (MIDGRAY,'Ph 0\nWk 0',
     'Lock Decisions',
     ['LLM choice', 'Deployment model', 'First 2 real integrations']),
    (RED,    'Ph 1\nWk 1',
     'Security',
     ['Remove hardcoded creds', 'JWT auth all endpoints', 'Secrets Manager', 'Argon2 passwords', 'Fix CORS']),
    (YELLOW, 'Ph 2\nWk 2–3',
     'Foundation',
     ['SQLite → PostgreSQL', 'Alembic migrations', 'Multi-tenancy primitives', 'OTel tracing']),
    (PURPLE, 'Ph 3\nWk 3–5',
     'MCP Routing',
     ['MCPHub → MCPManager', 'HTTP+SSE transport', 'Tool registry (DB)', 'Per-tenant vault', 'Circuit breaker + DLQ']),
    (CYAN,   'Ph 4\nWk 5–7',
     'Real APIs',
     ['Replace ServiceNow clone', 'Replace Salesforce / SAP', 'Validate on customer sandbox']),
    (GREEN,  'Ph 5\nWk 7–9',
     'Production',
     ['Kubernetes + Helm', 'HPA + blue-green', 'SLOs + alerting', 'Admin UI']),
    (LGRAY,  'Ph 6\nWk 9–10',
     'GTM',
     ['SOC 2 Type I evidence', 'DPA + security pack', 'Pricing tiers live', 'Design partner pilot live']),
]
ph_w = (13.33 - 0.26) / 7
for i, (col, label, title, items) in enumerate(phases):
    x = 0.13 + i * ph_w
    w = ph_w - 0.06
    box(s, x, 1.55, w, 0.72, col, f'{label}\n{title}', 8, DARK, True)
    box(s, x, 2.27, w, 3.85, WHITE if i % 2 == 0 else PEARL, line_color=LGRAY)
    tb_ml(s, x + 0.07, 2.33, w - 0.14, 3.72,
          ['• ' + it for it in items], 8.5, False, DARK)

# Milestone row
label_bar(s, 0.13, 6.15, 13.07, 'KEY MILESTONES  —  what customers see at each stage')
milestones = [
    (0.13, 'M1: Prod-ready core',     MIDGRAY),
    (2.0,  'M2: First real integration', CYAN),
    (3.87, 'M3: Paid pilot live',      YELLOW),
    (5.74, 'M4: Public case study',    PURPLE),
    (7.61, 'M5: SOC 2 Type I',        RED),
    (9.48, 'M6: Marketplace listed',   GREEN),
    (11.35,'M7: 10 paying customers',  LGRAY),
]
for x, lbl, col in milestones:
    box(s, x, 6.48, 1.78, 0.6, col, lbl, 7.5, DARK, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 21 — Next Steps (Pearl)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, PEARL)
header(s, GREEN, 'Next Steps',
       'Four concrete actions to move from this conversation to a scoped paid pilot', '07 Next Steps')
footer(s)

label_bar(s, 0.13, 1.22, 13.07, 'RECOMMENDED ACTIONS  —  in sequence, targeting a pilot start within 4 weeks')

actions = [
    (GREEN,  '01  Schedule Live Demo',
     ['30-minute live demonstration of the end-to-end flow against our realistic cloned systems.',
      '',
      'What you will see:',
      '  • Password reset ticket → resolved in ServiceNow + SAP in seconds',
      '  • New-hire onboarding across Salesforce + SAP + ServiceNow in ~30 seconds',
      '  • Cross-system lookup ("show me everything about this customer")',
      '  • Audit log review — every tool call timestamped and reviewable',
      '',
      'Typically 30 minutes including Q&A.']),
    (PURPLE, '02  Define Pilot Scope',
     ['Technical discovery call with your service-desk manager and IT architect.',
      '',
      'Outcomes:',
      '  • Identify top 3 ticket types to automate (e.g., password reset + onboarding)',
      '  • Map your ServiceNow instance and target CRM/ERP',
      '  • Confirm deployment model (SaaS vs hybrid VPC)',
      '  • Agree pilot success metrics and ROI target',
      '',
      'Feeds directly into a scoped 6-week pilot proposal.']),
    (CYAN,   '03  Commercial Alignment',
     ['Share pilot pricing and contract template (standard DPA + MSA).',
      '',
      'We provide:',
      '  • Pre-filled security questionnaire (SOC 2 in progress)',
      '  • Data processing agreement (standard template)',
      '  • Pilot commercial proposal with agreed ROI target',
      '  • Reference to design partner if you want a peer reference call',
      '',
      'Target: commercial agreement signed within 2 weeks of scoping call.']),
    (YELLOW, '04  Pilot Kick-off',
     ['6-week paid pilot — scoped to the agreed use cases.',
      '',
      'Week 1–2:  Integration setup (real ServiceNow + target system)',
      'Week 3–4:  Agent configured, fast-path rules tuned, UAT',
      'Week 5–6:  Production traffic on agreed ticket types',
      '',
      'At the end of Week 6:',
      '  → Measured ROI vs agreed target',
      '  → Go/no-go decision on annual contract',
      '  → If go: expand to additional use cases']),
]
col_w2 = (13.33 - 0.26) / 2
for i, (col, title, lines) in enumerate(actions):
    row = i // 2
    ci  = i %  2
    x = 0.13 + ci * col_w2
    y = 1.55 + row * 2.8
    w = col_w2 - 0.08
    box(s, x, y, w, 0.52, col, title, 11, DARK, True)
    card(s, x, y + 0.52, w, 2.2, 'DETAIL', lines, DARK, WHITE, 9)

box(s, 0.13, 7.0, 13.07, 0.17, DARK,
    'Contact:  karnaradha80@gmail.com  ·  zenops.ai  ·  India & Middle East — Phase 1 focus',
    8, GREEN, False)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 22 — Thank You (Dark)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide()
set_bg(s, DARK)
box(s, 0, 0, 0.5, 7.5, GREEN)
box(s, 0.5, 2.5, 7.8, 0.07, GREEN)
box(s, 0.5, 4.5, 7.8, 0.07, GREEN)
tb(s, 0.75, 2.65, 10, 0.7, 'Thank You', 36, True, WHITE)
tb(s, 0.75, 3.45, 10, 0.55, 'ZENOPS — AI Co-Worker for Enterprise Operations', 18, False, GREEN)
tb(s, 0.75, 4.1,  10, 0.45, 'Autonomous  ·  Auditable  ·  Always-On  ·  24/7', 13, True, WHITE)
tb(s, 0.75, 4.65, 10, 0.35, 'Confidential — Internal Use Only — April 2026', 10, False, LGRAY, italic=True)
# Contact strip
box(s, 0, 6.65, 13.33, 0.55, GREEN,
    'karnaradha80@gmail.com  ·  zenops.ai  ·  India & Middle East — Phase 1 focus',
    11, DARK, True)
tb(s, 0.75, 7.22, 10, 0.25, 'ZENOPS  |  Confidential  |  2026', 7, False, LGRAY)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save(OUT_PATH)
print(f'Saved: {OUT_PATH}')
print(f'Total slides: {len(prs.slides)}')
for i, sl in enumerate(prs.slides, 1):
    print(f'  Slide {i:2d}: {len(sl.shapes)} shapes')
