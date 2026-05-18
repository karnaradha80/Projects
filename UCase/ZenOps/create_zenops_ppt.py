"""
Creates a professional ZENOPS client presentation using the nxzen PPT template.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import copy

# ── Template ──────────────────────────────────────────────────────────────────
TEMPLATE  = r'C:\Projects\UCase\ZenOps\nxzen_template_converted.pptx'
OUT_PATH  = r'C:\Projects\UCase\ZenOps\ZENOPS_Client_Presentation.pptx'

prs = Presentation(TEMPLATE)
W = prs.slide_width    # 12192000 EMU = 13.33"
H = prs.slide_height   # 6858000  EMU = 7.50"

# ── Colour palette ─────────────────────────────────────────────────────────────
GREEN   = RGBColor(0x8D, 0xE9, 0x71)
PURPLE  = RGBColor(0xAD, 0x96, 0xDC)
YELLOW  = RGBColor(0xEC, 0xF1, 0x66)
CYAN    = RGBColor(0x74, 0xD1, 0xEA)
RED     = RGBColor(0xFF, 0x71, 0x76)
DARK    = RGBColor(0x03, 0x03, 0x04)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
PEARL   = RGBColor(0xF6, 0xF2, 0xF3)
MIDGRAY = RGBColor(0x44, 0x44, 0x44)
LGRAY   = RGBColor(0xCC, 0xCC, 0xCC)
DGREEN  = RGBColor(0x2E, 0x7D, 0x32)
DBLUE   = RGBColor(0x1A, 0x23, 0x7E)

IN = Inches(1)


# ── Helpers ────────────────────────────────────────────────────────────────────
def add_slide(layout_idx):
    return prs.slides.add_slide(prs.slide_layouts[layout_idx])


def tb(slide, l, t, w, h, text, size=16, bold=False,
       color=DARK, align=PP_ALIGN.LEFT, wrap=True, italic=False):
    """Add a text box. Measurements in inches."""
    bx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = bx.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    r  = p.add_run()
    r.text = text
    r.font.size   = Pt(size)
    r.font.bold   = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return bx


def tb_lines(slide, l, t, w, h, lines, size=14, bold=False,
             color=DARK, align=PP_ALIGN.LEFT, wrap=True,
             line_spacing=None):
    """Add a text box with multiple paragraphs (list of strings)."""
    bx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = bx.text_frame
    tf.word_wrap = wrap
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size  = Pt(size)
        r.font.bold  = bold
        r.font.color.rgb = color
        if line_spacing:
            from pptx.oxml.ns import qn
            from lxml import etree
            pPr = p._p.get_or_add_pPr()
            lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
            spcPts = etree.SubElement(lnSpc, qn('a:spcPts'))
            spcPts.set('val', str(int(line_spacing * 100)))
    return bx


def box(slide, l, t, w, h, fill, text='', size=13, text_color=WHITE,
        bold=False, line_color=None, align=PP_ALIGN.CENTER, shape_type=9):
    """Add a filled rectangle with optional label. shape_type 9=rect, 5=rounded."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    shp = slide.shapes.add_shape(shape_type, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line_color:
        shp.line.color.rgb = line_color
        shp.line.width     = Pt(1.0)
    else:
        shp.line.fill.background()
    if text:
        tf = shp.text_frame
        tf.word_wrap = True
        p  = tf.paragraphs[0]
        p.alignment = align
        r  = p.add_run()
        r.text = text
        r.font.size  = Pt(size)
        r.font.bold  = bold
        r.font.color.rgb = text_color
    return shp


def rbox(slide, l, t, w, h, fill, text='', size=13, text_color=WHITE,
         bold=False, line_color=None, align=PP_ALIGN.CENTER):
    """Rounded rectangle (shape_type 5)."""
    return box(slide, l, t, w, h, fill, text, size, text_color, bold, line_color, align, 5)


def hline(slide, l, t, w, color=LGRAY, thickness=1.5):
    """Horizontal rule."""
    shp = slide.shapes.add_shape(9, Inches(l), Inches(t), Inches(w), Inches(0.02))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def arrow_right(slide, l, t, w, color=MIDGRAY):
    """Simple right arrow connector."""
    shp = slide.shapes.add_shape(13, Inches(l), Inches(t), Inches(w), Inches(0.02))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def arrow_down(slide, l, t, h, color=MIDGRAY):
    """Simple down arrow (thin vertical bar)."""
    shp = slide.shapes.add_shape(9, Inches(l), Inches(t), Inches(0.02), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    return shp


def badge(slide, l, t, label, fill=GREEN, text_color=DARK, size=11, bold=True):
    """Small pill-shaped badge label."""
    rbox(slide, l, t, 1.4, 0.3, fill, label, size, text_color, bold)


# ── Remove the 5 template example slides ──────────────────────────────────────
# python-pptx can't delete slides via the public API easily; we work around it
xml_slides = prs.slides._sldIdLst
while len(xml_slides):
    xml_slides.remove(xml_slides[0])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(0)  # title - green
# Try to fill placeholders; if not, use text boxes
for ph in s.placeholders:
    idx = ph.placeholder_format.idx
    if idx == 0:
        ph.text = 'ZENOPS'
    elif idx == 1:
        ph.text = 'AI Co-Worker for Enterprise Operations'

# Supplementary labels
tb(s, 0.6, 5.8, 8, 0.4,
   'Transforming Enterprise IT — 24/7 Autonomous Resolution',
   size=15, color=WHITE, italic=True)
tb(s, 0.6, 6.3, 5, 0.4,
   'Confidential — April 2026', size=11, color=LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Agenda
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)  # text - pearl
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Today\'s Agenda'

items = [
    ('01', 'The Problem — enterprise IT automation gap',   CYAN),
    ('02', 'Why Now — three forces aligning in 2024-26',   GREEN),
    ('03', 'The ZENOPS Solution — what it does & how',     PURPLE),
    ('04', 'Architecture — current demo → enterprise',     YELLOW),
    ('05', 'Business Case — ROI, competition, pricing',    RED),
    ('06', 'Go-to-Market & Roadmap — 6-10 weeks to pilot',CYAN),
    ('07', 'Next Steps',                                    GREEN),
]
for i, (num, text, color) in enumerate(items):
    y = 1.7 + i * 0.72
    rbox(s, 0.6, y, 0.55, 0.5, color, num, 14, DARK, True)
    tb(s,  1.3, y + 0.05, 10, 0.45, text, size=14, color=DARK)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Section: The Problem
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(19)  # section heading
box(s, 0, 0, 13.33, 7.5, DARK)
tb(s, 1.5, 2.6, 10, 1.0,
   'THE PROBLEM', size=42, bold=True, color=GREEN, align=PP_ALIGN.LEFT)
tb(s, 1.5, 3.7, 9, 0.7,
   'The enterprise IT automation gap that costs billions every year',
   size=20, color=WHITE, align=PP_ALIGN.LEFT)
hline(s, 1.5, 3.65, 5.5, GREEN)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Enterprise Pain Points
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'The Enterprise IT Automation Gap'

pain_points = [
    (RED,    'Repetitive Ticket Work',
             'L1 agents spend 70%+ of their day on password resets, account\ncreations & cross-system copy-paste. Teams of 50–500 doing rote work.'),
    (YELLOW, 'Slow Resolution Times',
             'Employees wait 2+ hours for routine requests. Gartner: avg. 30 min\nlost productivity per IT ticket across the workforce.'),
    (CYAN,   'System Sprawl',
             'Same data needed in 3–5 platforms. Someone copies it by hand —\nerrors, rework, and "swivel-chair integration tax" every day.'),
    (PURPLE, 'Off-Hours Coverage Gaps',
             'A user in Singapore raises a ticket at 3 AM US time.\nNothing happens until morning. Global ops suffer.'),
    (GREEN,  'Inconsistent Quality & Audit Risk',
             'Different agents resolve the same issue differently. Access changes\nlogged inconsistently — compliance exposure for auditors.'),
]
for i, (color, title, desc) in enumerate(pain_points):
    col = i % 3
    row = i // 3
    lft = 0.5 + col * 4.25
    top = 1.6 + row * 2.4
    rbox(s, lft, top, 4.0, 2.15, color, '', line_color=color)
    tb(s, lft + 0.15, top + 0.12, 3.7, 0.45, title, size=12, bold=True, color=DARK)
    hline(s, lft + 0.15, top + 0.55, 3.5, DARK)
    tb(s, lft + 0.15, top + 0.65, 3.7, 1.35, desc, size=11, color=DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Why Now
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Why Now — Three Forces Aligning'

forces = [
    (GREEN, '1', 'LLMs Crossed the\nReliability Threshold',
     'Large language models now reliably drive real business actions —\nnot just generate text. They call APIs, complete tasks, handle\nambiguity, and maintain high accuracy at enterprise scale.'),
    (PURPLE, '2', 'Model Context Protocol\n(MCP) — Open Standard',
     'Introduced by Anthropic in late 2024, MCP gives agents a common\nlanguage for talking to enterprise systems. Salesforce, GitHub,\nAtlassian, ServiceNow are publishing official MCP connectors now.'),
    (CYAN, '3', 'Buyer Demand at\nAll-Time High',
     'Every major CIO survey in 2025–2026 lists "agentic AI for IT\noperations" as a top-three priority. Boards are mandating AI ROI.\nThe budget question is no longer IF — it\'s WHO and WHEN.'),
]
for i, (color, num, title, desc) in enumerate(forces):
    x = 0.5 + i * 4.2
    rbox(s, x, 1.5, 3.9, 1.0, color, '', line_color=color)
    tb(s, x + 0.15, 1.55, 0.8, 0.9, num, size=36, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    tb(s, x + 1.0, 1.6, 2.7, 0.8, title, size=13, bold=True, color=DARK, wrap=True)
    tb(s, x + 0.1, 2.65, 3.65, 3.5, desc, size=12, color=MIDGRAY, wrap=True)

tb(s, 0.5, 6.5, 12, 0.4,
   '→  These three forces together make ZENOPS possible today at the right price and with the right buyer appetite.',
   size=12, bold=True, color=GREEN)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Section: The Solution
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(19)
box(s, 0, 0, 13.33, 7.5, DARK)
tb(s, 1.5, 2.5, 10, 1.0,
   'THE SOLUTION', size=42, bold=True, color=PURPLE, align=PP_ALIGN.LEFT)
tb(s, 1.5, 3.6, 9, 0.7,
   'ZENOPS: an AI co-worker that reads, decides, and acts — across all your systems',
   size=20, color=WHITE, align=PP_ALIGN.LEFT)
hline(s, 1.5, 3.55, 5.5, PURPLE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — What Is ZENOPS
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'What Is ZENOPS?'

# Three-column "reads → decides → acts"
steps = [
    (CYAN,   'READS',   'Incoming employee\nand customer requests\nin plain language\n\n"Reset my password"\n"Onboard Priya Shah"\n"Create a new vendor"'),
    (PURPLE, 'DECIDES', 'Which systems to use\nWhich tools to call\nFast-path or LLM-path\n\nSame logic a senior\nagent would apply —\nin milliseconds'),
    (GREEN,  'ACTS',    'Creates records\nUpdates systems\nSends notifications\nCloses the ticket\n\n24/7 · in seconds ·\nwith full audit trail'),
]
arrow_labels = ['→', '→']
for i, (color, label, desc) in enumerate(steps):
    x = 0.4 + i * 4.15
    rbox(s, x, 1.4, 3.8, 0.65, color, label, 22, DARK, True)
    tb(s, x + 0.15, 2.1, 3.5, 4.2, desc, size=13, color=DARK, wrap=True)

for i, arr in enumerate(arrow_labels):
    tb(s, 4.35 + i * 4.15, 1.55, 0.5, 0.4, arr, size=26, bold=True,
       color=MIDGRAY, align=PP_ALIGN.CENTER)

# Bottom banner
rbox(s, 0.4, 6.3, 12.3, 0.8,
     DARK, '→  Think of ZENOPS as a new kind of employee: same systems access, same permissions — never sleeps, never makes a typo, logs everything.',
     12, WHITE, False)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — How ZENOPS Works (Request Flow)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'How ZENOPS Works — Request Flow'

# ── flow diagram ──────────────────────────────────────────────────────────────
# Row 1: User input sources
tb(s, 0.3, 1.3, 12.5, 0.3, 'INBOUND CHANNELS', 10, True, MIDGRAY)
rbox(s, 0.4, 1.6, 2.6, 0.7, CYAN,   'Employee Portal',   12, DARK, True)
rbox(s, 3.2, 1.6, 2.6, 0.7, CYAN,   'ServiceNow Ticket', 12, DARK, True)
rbox(s, 6.0, 1.6, 2.6, 0.7, CYAN,   'Email / Webhook',   12, DARK, True)
rbox(s, 8.8, 1.6, 2.6, 0.7, CYAN,   'API Ingestion',     12, DARK, True)

# Arrow down to Orchestrator
for x in [1.7, 4.5, 7.3, 10.1]:
    arrow_down(s, x, 2.32, 0.38)

# Row 2: Ticket Orchestrator
rbox(s, 0.4, 2.7, 12.3, 0.8, DARK,
     'Ticket Orchestrator  —  classifies request · assigns action type · routes to agent',
     13, WHITE, True)

arrow_down(s, 6.5, 3.52, 0.33)

# Row 3: Agent (two paths)
rbox(s, 0.4, 3.85, 5.7, 1.05, PURPLE,
     'FAST PATH\n(deterministic handler)\nCommon patterns: password reset,\nonboarding, lookup — zero LLM cost',
     11, WHITE, False)
rbox(s, 7.1, 3.85, 5.7, 1.05, GREEN,
     'AI PATH\n(Mistral / Claude LLM)\nComplex or novel requests:\nLLM selects tools, agent executes',
     11, DARK, False)
tb(s, 6.0, 4.05, 1.1, 0.65, 'or', 18, True, MIDGRAY, PP_ALIGN.CENTER)

# Arrow down to MCP
for x in [3.25, 10.0]:
    arrow_down(s, x, 4.92, 0.33)

# Row 4: MCP Unified Hub
rbox(s, 0.4, 5.25, 12.3, 0.7, YELLOW,
     'MCP Unified Hub  —  54 tools across 4 enterprise systems  (Model Context Protocol)',
     13, DARK, True)

# Arrow down to systems
for x in [1.7, 4.3, 6.9, 9.5, 11.7]:
    arrow_down(s, x, 5.97, 0.3)

# Row 5: Enterprise systems
systems = [
    (0.3,  'ServiceNow',  MIDGRAY),
    (2.9,  'Salesforce',  RGBColor(0x00, 0xA1, 0xE0)),
    (5.5,  'SAP',         RGBColor(0x00, 0x7A, 0xCC)),
    (8.1,  'MuleSoft',    RGBColor(0x00, 0x86, 0x72)),
    (10.7, 'Custom MCP',  PURPLE),
]
for x, name, color in systems:
    rbox(s, x, 6.3, 2.3, 0.7, color, name, 11, WHITE, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Before vs After
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Real-World Example: New-Hire Onboarding'

# Before column
rbox(s, 0.4, 1.35, 5.8, 0.55, RED, 'BEFORE  ZENOPS', 14, WHITE, True)
before = [
    '1.  Manager files ticket in ServiceNow',
    '2.  Service-desk agent picks up (queue wait: 30 min – 2 hrs)',
    '3.  Agent logs into Salesforce → creates user record',
    '4.  Agent logs into SAP HR → creates employee record',
    '5.  Agent opens SAP work order for laptop provisioning',
    '6.  Agent sends welcome email & posts KB link to new hire',
    '7.  Agent emails manager with confirmation',
    '',
    '⏱   Total time:  2–6 hours   |   People involved:  2–3',
    '💸  Cost:  1 FTE-hour of L1 agent time + management overhead',
]
tb_lines(s, 0.5, 2.0, 5.6, 4.7, before, size=12, color=DARK)

# Divider
hline(s, 6.35, 1.35, 0.02, MIDGRAY)
box(s, 6.35, 1.35, 0.04, 5.8, LGRAY)

# After column
rbox(s, 6.55, 1.35, 6.2, 0.55, GREEN, 'WITH  ZENOPS', 14, DARK, True)
after = [
    '1.  Manager files ticket in ServiceNow',
    '2.  Ticket Orchestrator classifies: USER_ONBOARDING',
    '3.  Agent reads ticket in plain language',
    '4.  MCP calls:',
    '       • sf_create_user  →  Salesforce record created',
    '       • sap_create_user →  SAP HR record created',
    '       • sap_create_work_order → laptop provisioning',
    '       • send_email  →  welcome email dispatched',
    '       • sn_close_ticket  →  ticket resolved & logged',
    '',
    '⏱   Total time:  ~30 seconds   |   People involved:  0',
    '✅  Full audit log. Consistent. Always-on.',
]
tb_lines(s, 6.65, 2.0, 6.0, 4.7, after, size=12, color=DARK)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Use Cases
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Use Cases ZENOPS Handles Today'

use_cases = [
    (GREEN,  'Identity & Access',
             'Password resets · Account creation\nAccess requests · Role provisioning\nUser deactivation / offboarding'),
    (PURPLE, 'Employee Lifecycle',
             'New-hire onboarding (full stack)\nRole changes · Location transfers\nEquipment provisioning via SAP'),
    (CYAN,   'Customer & Vendor',
             'New contact/account creation\nVendor onboarding across CRM + ERP\nService case creation & routing'),
    (YELLOW, 'Approvals & Orders',
             'Work order creation & approval\nExpense line routing\nLow-risk change management'),
    (RED,    'Insight & Reporting',
             'Cross-system 360° customer view\nEnterprise health dashboard\nTicket triage & escalation'),
    (PURPLE, 'Integration & Ops',
             'MuleSoft route status checks\nCross-platform data sync\nScheduled batch operations'),
]
for i, (color, title, desc) in enumerate(use_cases):
    col = i % 3
    row = i // 2
    x = 0.4 + col * 4.25
    y = 1.5 + row * 2.35
    rbox(s, x, y, 3.9, 0.55, color, title, 12, DARK, True)
    tb(s, x + 0.1, y + 0.6, 3.7, 1.65, desc, size=12, color=DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Section: Architecture
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(19)
box(s, 0, 0, 13.33, 7.5, DARK)
tb(s, 1.5, 2.4, 10, 1.0,
   'ARCHITECTURE', size=42, bold=True, color=CYAN, align=PP_ALIGN.LEFT)
tb(s, 1.5, 3.55, 9, 0.7,
   'Demo state today  →  Enterprise-grade target architecture',
   size=20, color=WHITE, align=PP_ALIGN.LEFT)
hline(s, 1.5, 3.5, 5.5, CYAN)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Current Architecture (Demo)
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Current Architecture — Demo (Phase 0)'

badge(s, 0.4, 1.3, 'DEMO STATE', RED, WHITE)
badge(s, 2.0, 1.3, 'LOCAL DOCKER', MIDGRAY, WHITE)

# Layer labels (left margin)
tb(s, 0.35, 1.75, 1.0, 0.55, 'FRONTEND', 8, True, MIDGRAY)
tb(s, 0.35, 2.5,  1.0, 0.55, 'ROUTER',   8, True, MIDGRAY)
tb(s, 0.35, 3.25, 1.0, 0.55, 'AGENT',    8, True, MIDGRAY)
tb(s, 0.35, 4.05, 1.0, 0.55, 'MCP HUB',  8, True, MIDGRAY)
tb(s, 0.35, 4.85, 1.0, 0.55, 'SYSTEMS',  8, True, MIDGRAY)

hline(s, 1.45, 1.72, 11.5, LGRAY)
hline(s, 1.45, 2.48, 11.5, LGRAY)
hline(s, 1.45, 3.22, 11.5, LGRAY)
hline(s, 1.45, 4.02, 11.5, LGRAY)
hline(s, 1.45, 4.82, 11.5, LGRAY)

# Frontend row
rbox(s, 1.5, 1.75, 2.8, 0.55, CYAN,   'Client Portal\n(nginx :2005)', 10, DARK)
rbox(s, 4.5, 1.75, 2.8, 0.55, CYAN,   'ServiceNow Frontend\n(:4780)', 10, DARK)

# Arrows down
for x in [2.9, 5.9]:
    arrow_down(s, x, 2.32, 0.2)

# Router row
rbox(s, 1.5, 2.5, 10.5, 0.6, DARK,
     'Ticket Orchestrator  (FastAPI · SQLite · :2486)  —  classifies · routes · stores tickets',
     11, WHITE, False)

arrow_down(s, 6.7, 3.12, 0.2)

# Agent row
rbox(s, 1.5, 3.27, 4.8, 0.62, PURPLE,
     'NetworkOpsAgent  (FastAPI · :7532)\nMistral AI  ←→  fast-path handlers', 10, WHITE)
rbox(s, 7.0, 3.27, 5.0, 0.62, MIDGRAY,
     'Continuous Processor\n(polls Orchestrator every 10 s)', 10, WHITE)

for x in [3.9, 9.5]:
    arrow_down(s, x, 3.91, 0.2)

# MCP Hub row
rbox(s, 1.5, 4.1, 10.5, 0.58, YELLOW,
     'MCP Unified Hub  (mcp_unified.py · stdio · 54 tools)  —  single monolithic MCP server',
     11, DARK, True)

for x in [2.8, 4.9, 7.0, 9.1, 11.2]:
    arrow_down(s, x, 4.7, 0.22)

# Systems row
clones = [
    (1.5, 'ServiceNow\nclone :4780', MIDGRAY),
    (3.8, 'Salesforce\nclone :4799', MIDGRAY),
    (6.1, 'SAP\nclone :4798', MIDGRAY),
    (8.4, 'MuleSoft\nclone :4797', MIDGRAY),
    (10.5,'SQLite\nOrchestrator', RGBColor(0x66, 0x66, 0x66)),
]
for x, name, col in clones:
    rbox(s, x, 4.95, 2.0, 0.7, col, name, 10, WHITE)

# Note
tb(s, 1.5, 5.8, 11, 0.35,
   '⚠  All enterprise backends are LOCAL CLONES (no real Salesforce/SAP/ServiceNow traffic). '
   'Single tenant. No auth. SQLite.',
   size=10, color=RED, italic=True)

# Tech stack footer
tb(s, 1.5, 6.2, 11, 0.4,
   'Stack: Python 3.11 · FastAPI · Uvicorn · Mistral Agents API · MCP SDK ≥1.0 · React 18 + TypeScript · Docker Compose',
   size=9, color=MIDGRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — MCP: Our Demo vs Enterprise
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'MCP Layer: Demo vs Enterprise'

tb(s, 0.4, 1.25, 12.5, 0.35,
   'Model Context Protocol (MCP) is the open standard (Anthropic, 2024) that lets AI agents talk to enterprise tools.'
   '  We already use it — the gap is in transport, auth, and multi-tenancy.',
   size=11, color=MIDGRAY, italic=True)

dims = [
    ('Transport',       'stdio subprocess (local)',         'HTTP+SSE / Streamable HTTP',     RED,   GREEN),
    ('Auth',            'None (stdio = trusted child)',     'OAuth 2.1 / mTLS / API key per tenant', RED, GREEN),
    ('Multi-tenancy',   'Single tenant',                   'tenant_id on every call; row-level security', RED, GREEN),
    ('Routing',         'Hardcoded to mcp_unified.py',     'MCP Gateway: N servers, tool→server registry', RED, GREEN),
    ('Tool surface',    '54 tools, static list',           '100s of tools, paginated, versioned', YELLOW, GREEN),
    ('Audit log',       'Basic Python logs',               'Immutable append-only log per tool call', RED, GREEN),
    ('Reliability',     'No retries, no circuit breaker',  'Tenacity retries · circuit breaker · DLQ', RED, GREEN),
    ('Scale',           'Local docker-compose, 1 host',    'Kubernetes · HPA · multi-AZ · blue-green', RED, GREEN),
]

# Header row
rbox(s, 1.55, 1.65, 3.5, 0.45, DARK, 'DIMENSION', 11, WHITE, True)
rbox(s, 5.2,  1.65, 3.5, 0.45, RED,  'OUR DEMO',  11, WHITE, True)
rbox(s, 8.8,  1.65, 4.2, 0.45, GREEN,'ENTERPRISE TARGET', 11, DARK, True)

for i, (dim, cur, tgt, c_cur, c_tgt) in enumerate(dims):
    y = 2.15 + i * 0.54
    bg = PEARL if i % 2 == 0 else WHITE
    rbox(s, 1.55, y, 3.5, 0.5, RGBColor(0xEE,0xEE,0xEE), dim,  10, DARK,    False)
    rbox(s, 5.2,  y, 3.5, 0.5, RGBColor(0xFF,0xEE,0xEE), cur,  9,  MIDGRAY, False)
    rbox(s, 8.8,  y, 4.2, 0.5, RGBColor(0xEE,0xFF,0xEE), tgt,  9,  DARK,    False)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Target Enterprise Architecture
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Target Enterprise Architecture'

badge(s, 0.4, 1.3, 'PRODUCTION TARGET', GREEN, DARK)
badge(s, 2.2, 1.3, 'KUBERNETES',         CYAN,  DARK)
badge(s, 3.8, 1.3, 'MULTI-TENANT',       PURPLE, WHITE)

# Layers
layers = [
    (1.75, 'INGRESS',   CYAN),
    (2.45, 'CONTROL',   DARK),
    (3.2,  'AGENT',     PURPLE),
    (4.0,  'MCP GW',    YELLOW),
    (4.75, 'ENTERPRISE',MIDGRAY),
]
for y, lbl, col in layers:
    tb(s, 0.3, y, 1.1, 0.55, lbl, 7, True, col)
    hline(s, 1.45, y, 11.5, LGRAY)

# API Gateway
rbox(s, 1.5, 1.75, 11, 0.55, CYAN,
     'API Gateway (Kong)  —  TLS · WAF · rate limiting · JWT verify · OpenTelemetry',
     11, DARK, True)

arrow_down(s, 7.0, 2.32, 0.18)

# Control plane row
rbox(s, 1.5,  2.5, 3.5, 0.58, DARK,   'Tenant Admin UI\n(React — onboard, config, audit)', 10, WHITE)
rbox(s, 5.2,  2.5, 4.0, 0.58, DARK,   'Ticket Orchestrator  (PostgreSQL + Redis)\nroute · classify · DLQ · event emit', 10, WHITE)
rbox(s, 9.4,  2.5, 3.1, 0.58, DARK,   'Webhook Ingress\n(ServiceNow forwarder)', 10, WHITE)

arrow_down(s, 7.2, 3.1, 0.18)

# Agent worker pool
rbox(s, 1.5, 3.28, 11.0, 0.62, PURPLE,
     'Agent Worker Pool  (k8s HPA)  —  fast-path handlers · LLM-path (Claude / Mistral) · MCP Manager (multi-server)',
     11, WHITE, True)

arrow_down(s, 7.0, 3.92, 0.18)

# MCP Gateway
rbox(s, 1.5, 4.1, 11.0, 0.55, YELLOW,
     'MCP Gateway / Router  —  tenant→MCP registry · OAuth 2.1 / mTLS · circuit breaker · retry · audit log',
     11, DARK, True)

for x in [2.5, 5.0, 7.5, 10.0]:
    arrow_down(s, x, 4.67, 0.2)

# Enterprise MCPs
ent_mcps = [
    (1.5,  'ServiceNow\nMCP (official)',  MIDGRAY),
    (4.0,  'Salesforce\nMCP (official)',  RGBColor(0x00, 0xA1, 0xE0)),
    (6.5,  'SAP S/4\nMCP (custom)',      RGBColor(0x00, 0x7A, 0xCC)),
    (9.0,  'Custom\nEnterprise MCP',     PURPLE),
]
for x, name, col in ent_mcps:
    rbox(s, x, 4.9, 2.3, 0.65, col, name, 10, WHITE)

# Cross-cutting
tb(s, 1.5, 5.7, 11.0, 0.3,
   'Cross-cutting:  Secrets Manager (Vault/AWS SM) · OpenTelemetry → Tempo + Prometheus + Loki · Postgres audit log · S3 attachments',
   size=9, color=MIDGRAY, wrap=True)

# Deployment options
rbox(s, 1.5, 6.1, 3.5, 0.55, DARK,
     'SaaS\n(default — our cloud)', 10, WHITE)
rbox(s, 5.2, 6.1, 3.5, 0.55, DARK,
     'Hybrid\n(agent in customer VPC)', 10, WHITE)
rbox(s, 9.0, 6.1, 3.5, 0.55, DARK,
     'Self-hosted\n(full Helm chart)', 10, WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — Section: Business Case
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(19)
box(s, 0, 0, 13.33, 7.5, DARK)
tb(s, 1.5, 2.4, 10, 1.0,
   'BUSINESS CASE', size=42, bold=True, color=YELLOW, align=PP_ALIGN.LEFT)
tb(s, 1.5, 3.55, 9, 0.7,
   'ROI that a CFO will sign off on in under 10 minutes',
   size=20, color=WHITE, align=PP_ALIGN.LEFT)
hline(s, 1.5, 3.5, 5.5, YELLOW)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Competitive Landscape
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Competitive Landscape'

tb(s, 0.4, 1.25, 12.5, 0.35,
   'Every category has a gap ZENOPS fills: cross-system intelligence that no single vendor will ever build.',
   size=11, color=MIDGRAY, italic=True)

comp = [
    ('Big Platform AI\n(Now Assist, Einstein,\nM365 Copilot)',
     'Microsoft, Salesforce,\nServiceNow',
     '✗ Works inside their own\nplatform only',
     '✓ Works ACROSS all platforms\nVendor-agnostic orchestration'),
    ('RPA\n(UiPath, AA,\nBlue Prism)',
     'Long-established\nenterprise RPA',
     '✗ Brittle UI scripts\n✗ No language understanding\n✗ Breaks on UI changes',
     '✓ API-native + AI reasoning\n✓ Adapts to unseen requests\n✓ MCP standard vs. fragile bots'),
    ('AI Agent Startups\n(Sierra, Decagon,\nKore.ai)',
     'Customer-support\nfocused agents',
     '✗ Customer-facing chatbots\n✗ Limited IT/ops depth\n✗ Single system integration',
     '✓ Internal IT/ops buyer (CIO)\n✓ Multi-system orchestration\n✓ Enterprise audit & compliance'),
    ('Custom In-House\nBuild',
     'Large enterprises\nbuilding their own',
     '✗ 12–18 months build time\n✗ 10-person engineering team\n✗ Ongoing maintenance burden',
     '✓ Pilot in 2–4 weeks\n✓ MCP standard — plug in vendors\n✓ Shared SaaS platform costs'),
]

headers = ['Competitor Category', 'Who',  'Their Gap',  'ZENOPS Advantage']
widths  = [2.8, 2.2, 3.5, 3.8]
x_pos   = [0.4, 3.25, 5.5, 9.05]
colors  = [DARK, DARK, RED, GREEN]
t_cols  = [WHITE, WHITE, WHITE, DARK]

for j, (hdr, w, x, col, tc) in enumerate(zip(headers, widths, x_pos, colors, t_cols)):
    rbox(s, x, 1.65, w, 0.5, col, hdr, 10, tc, True)

for i, (cat, who, gap, adv) in enumerate(comp):
    y = 2.2 + i * 1.18
    bg = PEARL if i % 2 == 0 else WHITE
    data = [cat, who, gap, adv]
    t_clrs = [DARK, DARK, RGBColor(0xCC, 0x00, 0x00), DGREEN]
    for j, (val, w, x) in enumerate(zip(data, widths, x_pos)):
        rbox(s, x, y, w, 1.1, bg, val, 9, t_clrs[j], False, LGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — ROI & Business Value
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'ROI — The Numbers a CFO Will Recognise'

tb(s, 0.4, 1.25, 12.5, 0.35,
   'Representative profile: 5,000-employee enterprise · 20,000 tickets/month · 30 service-desk FTEs',
   size=11, color=MIDGRAY, italic=True, bold=True)

roi_rows = [
    ('Tickets auto-resolved',         '0%',                   '50–70%',         'Material productivity uplift'),
    ('Avg. resolution time (routine)', '2 hours',              'Under 1 minute', 'Faster employees & customers'),
    ('Service-desk headcount',         '30 FTE',               '12–18 FTE',      'USD 600k–900k saved per year'),
    ('After-hours coverage',           'Manual on-call gaps',  '24/7 automated', 'Better SLA, lower attrition'),
    ('Audit posture (access changes)', 'Frequent gaps',        'Full audit log',  'Compliance risk reduced'),
    ('Payback period',                 '—',                   '< 6 months',      'At planned pricing'),
]

hdrs = ['METRIC', 'TODAY', 'WITH ZENOPS', 'ANNUAL IMPACT']
xs   = [0.4, 3.3, 6.2, 9.1]
ws   = [2.7, 2.7, 2.7, 4.0]
hcolors = [DARK, RED, GREEN, PURPLE]

for j, (hdr, x, w, hc) in enumerate(zip(hdrs, xs, ws, hcolors)):
    rbox(s, x, 1.65, w, 0.48, hc, hdr, 11, WHITE, True)

for i, (metric, today, after, impact) in enumerate(roi_rows):
    y = 2.18 + i * 0.75
    bg = PEARL if i % 2 == 0 else WHITE
    for j, (val, x, w) in enumerate(zip([metric, today, after, impact], xs, ws)):
        tc = [DARK, RED, DGREEN, PURPLE][j]
        rbox(s, x, y, w, 0.7, bg, val, 10, tc, j == 2, LGRAY)

# Big number callouts at bottom
callouts = [
    (GREEN,  '50–70%',         'Tickets auto-resolved'),
    (PURPLE, 'USD 600k–900k',  'Saved per year'),
    (CYAN,   '< 30 sec',       'Avg resolution time'),
    (YELLOW, '< 6 months',     'Payback period'),
]
for i, (c, big, label) in enumerate(callouts):
    x = 0.4 + i * 3.2
    rbox(s, x, 6.55, 2.95, 0.7, c, f'{big}\n{label}', 11, DARK, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Pricing Model
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Pricing Model'

tb(s, 0.4, 1.25, 12.5, 0.35,
   'Two-part model aligned to customer value: fixed platform fee + usage fee that scales with what we do for them.',
   size=11, color=MIDGRAY, italic=True)

tiers = [
    (CYAN,   'STARTER',    'Up to 1,000 employees',
     'USD 36,000 / year\n(USD 3,000 / month)',
     '• Standard connectors\n• Core ticket types\n• Email support'),
    (PURPLE, 'GROWTH',     '1,000 – 10,000 employees',
     'USD 120,000 / year\n(USD 10,000 / month)',
     '• All standard connectors\n• Custom fast-path rules\n• Dedicated CSM'),
    (GREEN,  'ENTERPRISE', '10,000+ employees',
     'USD 300,000+ / year\n(custom)',
     '• Custom MCP integrations\n• Hybrid VPC deployment\n• SLA guarantee · SOC 2'),
]
for i, (col, name, size_lbl, price, features) in enumerate(tiers):
    x = 0.4 + i * 4.25
    rbox(s, x, 1.65, 3.9, 0.5, col, name, 14, DARK, True)
    tb(s, x + 0.1, 2.2, 3.7, 0.35, size_lbl, 10, False, MIDGRAY)
    rbox(s, x, 2.6, 3.9, 0.75, DARK, price, 13, WHITE, True)
    tb(s, x + 0.1, 3.4, 3.7, 1.8, features, 12, False, DARK, wrap=True)

# Usage fee row
rbox(s, 0.4, 5.3, 12.5, 0.65, DARK,
     'Usage Fee  —  USD 0.10–0.30 per auto-resolved ticket above tier quota'
     '   (pay more only when we do more work for you)',
     12, GREEN, True)

# PS row
rbox(s, 0.4, 6.05, 12.5, 0.62, RGBColor(0xEE,0xEE,0xEE),
     'Professional Services  —  USD 25k–100k one-time per engagement'
     '   (integration setup · custom connector build · fast-path automation tuning)',
     11, DARK, False)

# Margin note
tb(s, 0.4, 6.75, 12.5, 0.35,
   'Target gross margin: 70–80%  ·  LLM cost mitigated by fast-path (zero LLM cost) covering 60–80% of volume',
   size=10, color=MIDGRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — Go-to-Market
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Go-to-Market Strategy'

# Geography phase boxes
rbox(s, 0.4, 1.4, 5.8, 0.55, CYAN,
     'Phase 1 (Now):  India & Middle East  —  fastest buying cycles, strongest network', 11, DARK, True)
rbox(s, 6.5, 1.4, 6.4, 0.55, PURPLE,
     'Phase 2 (Month 6+):  North America & Europe', 11, WHITE, True)

# GTM pillars
pillars = [
    (GREEN,  'Design Partners\n(First 6 Months)',
             '2 design partners — 1 financial services, 1 manufacturing\n'
             'Heavy discount in exchange for case studies + ROI numbers\n'
             'Goal: public reference customer for Series A story'),
    (PURPLE, 'Partner-Led Sales\nMotion',
             'ServiceNow Store · Salesforce AppExchange · SAP Marketplace\n'
             'Partner channel = procurement-friendly path + CIO air cover\n'
             'Presence at Dreamforce, ServiceNow World Forum, SAP Sapphire'),
    (CYAN,   'Pilot-First\nConversion',
             '6-week paid pilot scoped to ONE use case (e.g., password resets)\n'
             'Agree ROI target upfront. Hit it → convert to annual contract\n'
             'Land & expand: each new use case is config, not code'),
]
for i, (col, title, desc) in enumerate(pillars):
    x = 0.4 + i * 4.25
    rbox(s, x, 2.1, 3.9, 0.6, col, title, 12, DARK, True)
    tb(s, x + 0.1, 2.75, 3.7, 2.1, desc, 11, False, DARK, wrap=True)

# Sales motion
rbox(s, 0.4, 5.0, 12.5, 0.5, DARK,
     'Sales Motion:  CIO / Head of IT Ops (top-down buyer)  ←  Service-desk manager (daily champion)',
     12, WHITE, True)

# What we need to close first deal
tb(s, 0.4, 5.6, 12.5, 0.3, 'To close the first deal we need:', 11, True, DARK)
needs = [
    'Working multi-tenant product (Phases 1–3)',
    'Two real integrations live (ServiceNow + Salesforce or SAP)',
    'Security pack: SOC 2 Type I in progress · DPA template · security questionnaire pre-filled',
    'Simple admin UI so customer can self-onboard without our engineers',
]
for i, n in enumerate(needs):
    x = 0.6 + (i % 2) * 6.2
    y = 5.95 + (i // 2) * 0.38
    tb(s, x, y, 5.8, 0.35, f'✓  {n}', 10, False, DARK, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — 6–10 Week Roadmap
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = '6–10 Week Engineering Roadmap to First Paid Pilot'

phases = [
    (0,   GREEN,  'Phase 0\nWk 0',
     'Lock Decisions\n• LLM choice (Mistral vs Claude)\n• Deployment model (SaaS/Hybrid)\n• First 2 real integrations'),
    (1,   RED,    'Phase 1\nWk 1',
     'Security Hardening\n• Remove hardcoded creds\n• JWT auth on all endpoints\n• Secrets Manager (Vault/AWS SM)\n• Argon2 password hashing\n• Tighten CORS'),
    (2,   YELLOW, 'Phase 2\nWk 2–3',
     'Foundation\n• SQLite → PostgreSQL\n• Alembic migrations\n• Multi-tenancy primitives\n• Structured logging + OTel'),
    (3,   PURPLE, 'Phase 3\nWk 3–5',
     'MCP Routing\n• MCPHub → MCPManager\n• HTTP+SSE transport\n• Tool registry (DB)\n• Per-tenant credential vault\n• Circuit breaker + DLQ'),
    (4,   CYAN,   'Phase 4\nWk 5–7',
     'Real Integrations\n• Replace ServiceNow clone\n• Replace Salesforce or SAP\n• Validate on customer sandbox'),
    (5,   GREEN,  'Phase 5\nWk 7–9',
     'Production-Ready\n• Kubernetes + Helm chart\n• HPA + blue-green\n• SLOs + alerting\n• Admin UI (tenant onboard)'),
    (6,   PURPLE, 'Phase 6\nWk 9–10',
     'Compliance & GTM\n• SOC 2 Type I evidence\n• DPA + security pack\n• Pricing tiers live\n• Design partner pilot'),
]

ph_w = 1.75
ph_gap = 0.05
x_start = 0.35

for i, (_, col, label, items) in enumerate(phases):
    x = x_start + i * (ph_w + ph_gap)
    rbox(s, x, 1.4, ph_w, 0.65, col, label, 9, DARK, True)
    arrow_right(s, x + ph_w, 1.7, ph_gap + 0.03)
    tb(s, x + 0.08, 2.1, ph_w - 0.15, 4.8, items, 8, False, DARK, wrap=True)

# Milestone bar
milestones = [
    (1.5,  GREEN,  'M1\nProd-ready\ncore'),
    (3.7,  CYAN,   'M2\nFirst real\nintegration'),
    (5.5,  YELLOW, 'M3\nPaid pilot\nlive'),
    (7.3,  PURPLE, 'M4\nPublic\ncase study'),
    (9.0,  RED,    'M5\nSOC 2\nType I'),
    (10.8, GREEN,  'M6\nMarket-\nplace listed'),
]
tb(s, 0.35, 6.3, 12.5, 0.25, '  KEY MILESTONES', 8, True, MIDGRAY)
for x, col, label in milestones:
    rbox(s, x, 6.55, 1.6, 0.65, col, label, 7, DARK, True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 21 — Next Steps
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(14)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = 'Next Steps'

actions = [
    (GREEN,  'Schedule Live Demo',
             'We will run the end-to-end demo against our realistic cloned systems:\n'
             'password reset → onboarding → cross-system lookup.\n'
             'Typically 30 minutes including Q&A.'),
    (PURPLE, 'Define Design Partner Scope',
             'Identify the top 3 ticket types your service desk wants to automate.\n'
             'We scope a 6-week paid pilot with an agreed ROI target upfront.'),
    (CYAN,   'Technical Discovery Call',
             'Architecture review with your engineering/IT team.\n'
             'Map your current systems (ServiceNow instance, Salesforce/SAP version).\n'
             'Confirm VPC / deployment model preference.'),
    (YELLOW, 'Commercial Alignment',
             'Share pilot pricing + contract template.\n'
             'Review security questionnaire and DPA.\n'
             'Agree success metrics for pilot → annual conversion.'),
]
for i, (col, title, desc) in enumerate(actions):
    col_i = i % 2
    row_i = i // 2
    x = 0.4 + col_i * 6.4
    y = 1.5 + row_i * 2.7
    rbox(s, x, y, 6.0, 0.55, col, f'0{i+1}  {title}', 13, DARK, True)
    tb(s, x + 0.15, y + 0.6, 5.7, 1.95, desc, 12, False, DARK, wrap=True)

rbox(s, 0.4, 7.0, 12.5, 0.25, DARK,
     'Contact:  karnaradha80@gmail.com  ·  zenops.ai',
     10, WHITE, False)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 22 — Thank You / End
# ══════════════════════════════════════════════════════════════════════════════
s = add_slide(0)  # title - green layout
for ph in s.placeholders:
    idx = ph.placeholder_format.idx
    if idx == 0:
        ph.text = 'Thank You'
    elif idx == 1:
        ph.text = 'ZENOPS — AI Co-Worker for Enterprise Operations'

tb(s, 0.6, 5.5, 10, 0.4,
   'Autonomous · Auditable · Always-On', size=18, bold=True, color=WHITE, italic=True)
tb(s, 0.6, 6.0, 8, 0.4,
   'Internal Confidential — April 2026', size=11, color=LGRAY)

# ── Save ───────────────────────────────────────────────────────────────────────
prs.save(OUT_PATH)
print(f'Saved: {OUT_PATH}')
print(f'Total slides: {len(prs.slides)}')
