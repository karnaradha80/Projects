"""
Creates Toad-to-Azure POC presentation using NxZen branding.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy, os

# ── Paths ──────────────────────────────────────────────────────────────────────
PPT_DIR   = r"C:\Projects\Toad_poc\ppt"
LOGO      = os.path.join(PPT_DIR, "extracted", "Picture 3.png")   # NxZen logo
SIDE_IMG  = os.path.join(PPT_DIR, "extracted", "Picture 1.png")   # right panel
OUT_FILE  = os.path.join(PPT_DIR, "Toad_Azure_POC.pptx")

# ── Brand colours ──────────────────────────────────────────────────────────────
BG       = RGBColor(0x03, 0x03, 0x04)   # near-black background
GREEN    = RGBColor(0x8D, 0xE9, 0x71)   # primary green accent
CYAN     = RGBColor(0x74, 0xD1, 0xEA)   # cyan
PURPLE   = RGBColor(0xAD, 0x96, 0xDC)   # purple
YELLOW   = RGBColor(0xEC, 0xF1, 0x66)   # yellow
PINK     = RGBColor(0xFF, 0x71, 0x76)   # pink/red
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY    = RGBColor(0xE8, 0xE5, 0xE6)   # light gray text
DGRAY    = RGBColor(0x2A, 0x2A, 0x2C)   # dark gray for cards

SW = Inches(13.33)
SH = Inches(7.50)

prs = Presentation()
prs.slide_width  = SW
prs.slide_height = SH

blank_layout = prs.slide_layouts[6]  # completely blank


# ── Helper functions ────────────────────────────────────────────────────────────

def add_slide():
    slide = prs.slides.add_slide(blank_layout)
    # Dark background rectangle
    bg = slide.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    return slide


def add_logo(slide):
    slide.shapes.add_picture(LOGO, Inches(0.25), Inches(0.15), Inches(1.20), Inches(1.20))


def add_footer(slide, text="NxZen  |  Toad to Azure Migration POC  |  Confidential  |  2026"):
    tb = slide.shapes.add_textbox(Inches(0.25), Inches(7.15), Inches(12.80), Inches(0.30))
    tf = tb.text_frame
    p  = tf.paragraphs[0]
    r  = p.add_run(); r.text = text
    r.font.name = "Arial"; r.font.size = Pt(7); r.font.color.rgb = LGRAY
    p.alignment = PP_ALIGN.CENTER
    # thin line above footer
    line = slide.shapes.add_shape(1, Inches(0.25), Inches(7.10), Inches(12.80), Inches(0.02))
    line.fill.solid(); line.fill.fore_color.rgb = GREEN
    line.line.fill.background()


def add_header_bar(slide, height=Inches(1.30)):
    bar = slide.shapes.add_shape(1, 0, 0, SW, height)
    bar.fill.solid(); bar.fill.fore_color.rgb = DGRAY
    bar.line.fill.background()
    # green accent strip at top
    strip = slide.shapes.add_shape(1, 0, 0, SW, Inches(0.07))
    strip.fill.solid(); strip.fill.fore_color.rgb = GREEN
    strip.line.fill.background()
    return bar


def title_text(slide, title, subtitle=None, tx=Inches(1.60), ty=Inches(0.20),
               tw=Inches(10.0), title_size=22, title_color=WHITE):
    tb = slide.shapes.add_textbox(tx, ty, tw, Inches(0.80))
    tf = tb.text_frame; tf.word_wrap = False
    p  = tf.paragraphs[0]
    r  = p.add_run(); r.text = title
    r.font.name = "Arial"; r.font.size = Pt(title_size)
    r.font.bold = True; r.font.color.rgb = title_color
    if subtitle:
        tb2 = slide.shapes.add_textbox(tx, ty + Inches(0.65), tw, Inches(0.40))
        tf2 = tb2.text_frame
        p2  = tf2.paragraphs[0]
        r2  = p2.add_run(); r2.text = subtitle
        r2.font.name = "Arial"; r2.font.size = Pt(10)
        r2.font.color.rgb = GREEN


def add_textbox(slide, text, x, y, w, h, size=10, color=LGRAY, bold=False, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    p  = tf.paragraphs[0]; p.alignment = align
    r  = p.add_run(); r.text = text
    r.font.name = "Arial"; r.font.size = Pt(size)
    r.font.bold = bold; r.font.color.rgb = color
    return tb


def add_card(slide, x, y, w, h, title, body_lines, title_color=CYAN, fill=DGRAY):
    card = slide.shapes.add_shape(1, x, y, w, h)
    card.fill.solid(); card.fill.fore_color.rgb = fill
    card.line.color.rgb = title_color; card.line.width = Pt(0.75)

    # title
    tb = slide.shapes.add_textbox(x + Inches(0.12), y + Inches(0.10), w - Inches(0.24), Inches(0.35))
    tf = tb.text_frame
    p  = tf.paragraphs[0]
    r  = p.add_run(); r.text = title
    r.font.name = "Arial"; r.font.size = Pt(10.5)
    r.font.bold = True; r.font.color.rgb = title_color

    # body
    tb2 = slide.shapes.add_textbox(x + Inches(0.12), y + Inches(0.45), w - Inches(0.24), h - Inches(0.55))
    tf2 = tb2.text_frame; tf2.word_wrap = True
    first = True
    for line in body_lines:
        if first:
            p2 = tf2.paragraphs[0]; first = False
        else:
            p2 = tf2.add_paragraph()
        r2 = p2.add_run(); r2.text = line
        r2.font.name = "Arial"; r2.font.size = Pt(9)
        r2.font.color.rgb = LGRAY


def add_bullet_box(slide, x, y, w, h, lines, size=9.5, color=LGRAY, spacing=1.15):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for line in lines:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()
        r = p.add_run(); r.text = line
        r.font.name = "Arial"; r.font.size = Pt(size)
        r.font.color.rgb = color


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()

# Right side panel image
slide.shapes.add_picture(SIDE_IMG, Inches(7.80), 0, Inches(5.53), SH)

# Dark overlay on left
left_panel = slide.shapes.add_shape(1, 0, 0, Inches(8.20), SH)
left_panel.fill.solid(); left_panel.fill.fore_color.rgb = BG
left_panel.line.fill.background()

# Green top strip
strip = slide.shapes.add_shape(1, 0, 0, Inches(8.20), Inches(0.07))
strip.fill.solid(); strip.fill.fore_color.rgb = GREEN
strip.line.fill.background()

# Logo
slide.shapes.add_picture(LOGO, Inches(0.40), Inches(0.20), Inches(1.40), Inches(1.40))

# Title block
add_textbox(slide, "TOAD TO AZURE", Inches(0.40), Inches(2.00), Inches(7.50), Inches(0.90),
            size=36, color=WHITE, bold=True)
add_textbox(slide, "MIGRATION POC", Inches(0.40), Inches(2.80), Inches(7.50), Inches(0.90),
            size=36, color=GREEN, bold=True)
add_textbox(slide, "End-to-end proof of concept: replacing Toad automation\nwith Azure Data Factory, Azure Functions & Blob Storage",
            Inches(0.40), Inches(3.80), Inches(7.20), Inches(0.80), size=11, color=LGRAY)

# Divider
div = slide.shapes.add_shape(1, Inches(0.40), Inches(3.70), Inches(3.50), Inches(0.04))
div.fill.solid(); div.fill.fore_color.rgb = GREEN; div.line.fill.background()

add_textbox(slide, "May 2026  |  NxZen", Inches(0.40), Inches(6.80), Inches(4.0), Inches(0.30),
            size=8, color=LGRAY)

print("Slide 1 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Agenda", "What this presentation covers")
add_footer(slide)

items = [
    ("01", GREEN,  "Problem Statement",         "What Toad does today and why we are migrating"),
    ("02", CYAN,   "Solution Architecture",      "Azure components and how they connect"),
    ("03", PURPLE, "ADF Pipeline Flow",          "Step-by-step activity chain in Azure Data Factory"),
    ("04", YELLOW, "Azure Function Deep Dive",   "How CSV data is pushed into the Excel template"),
    ("05", PINK,   "Sample Data & Testing",      "1,000 records generated and loaded end-to-end"),
    ("06", GREEN,  "Pipeline Run Results",       "Confirmed output: CSV, XLSM, Archive"),
    ("07", CYAN,   "Next Steps",                 "Email integration and AWS equivalent"),
]

col_w = Inches(1.65)
gap   = Inches(0.12)
start_x = Inches(0.30)
y = Inches(1.50)

for i, (num, col, heading, detail) in enumerate(items):
    x = start_x + i * (col_w + gap)
    card = slide.shapes.add_shape(1, x, y, col_w, Inches(4.80))
    card.fill.solid(); card.fill.fore_color.rgb = DGRAY
    card.line.color.rgb = col; card.line.width = Pt(1)

    tb = slide.shapes.add_textbox(x + Inches(0.10), y + Inches(0.15), col_w - Inches(0.20), Inches(0.55))
    tf = tb.text_frame
    p  = tf.paragraphs[0]
    r  = p.add_run(); r.text = num
    r.font.name = "Arial"; r.font.size = Pt(28); r.font.bold = True; r.font.color.rgb = col

    add_textbox(slide, heading, x + Inches(0.10), y + Inches(0.75), col_w - Inches(0.20),
                Inches(0.55), size=10, color=WHITE, bold=True)
    add_textbox(slide, detail,  x + Inches(0.10), y + Inches(1.35), col_w - Inches(0.20),
                Inches(3.20), size=8.5, color=LGRAY)

print("Slide 2 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — PROBLEM STATEMENT
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Problem Statement", "Legacy Toad automation — limitations and migration drivers")
add_footer(slide)

# Left column — AS-IS
add_textbox(slide, "AS-IS  (Toad / On-Premise)", Inches(0.40), Inches(1.50), Inches(5.80),
            Inches(0.35), size=11, color=PINK, bold=True)
left_lines = [
    "  Quest Toad scripting runs on a local Windows server",
    "  Manual trigger required each morning",
    "  SQL query pulls gas escape data from Oracle ODS",
    "  Data exported to CSV, then manually pasted into Excel (.xlsm)",
    "  Report emailed to Operations team via Outlook automation",
    "  No monitoring, no retry, no audit trail",
    "  Single point of failure — if the server is down, report is missed",
    "  Licensing cost for Toad and supporting tools",
]
add_bullet_box(slide, Inches(0.40), Inches(1.90), Inches(5.80), Inches(4.50), left_lines, size=9.5)

# Divider
div = slide.shapes.add_shape(1, Inches(6.35), Inches(1.45), Inches(0.04), Inches(5.30))
div.fill.solid(); div.fill.fore_color.rgb = GREEN; div.line.fill.background()

# Right column — drivers
add_textbox(slide, "Migration Drivers", Inches(6.55), Inches(1.50), Inches(6.30),
            Inches(0.35), size=11, color=GREEN, bold=True)

drivers = [
    (GREEN,  "Cloud-native reliability",  "Managed pipeline with built-in retry, monitoring & alerts"),
    (CYAN,   "Zero infrastructure",       "No servers to maintain — ADF + Functions run serverless"),
    (PURPLE, "Cost efficiency",           "Consumption-based billing; no Toad licence fee"),
    (YELLOW, "Scalability",               "1,000+ records today; scales to millions with no changes"),
    (PINK,   "Auditability",              "Every run logged in ADF with full activity history"),
]

dy = Inches(1.90)
for col, heading, detail in drivers:
    dot = slide.shapes.add_shape(1, Inches(6.55), dy + Inches(0.08), Inches(0.12), Inches(0.12))
    dot.fill.solid(); dot.fill.fore_color.rgb = col; dot.line.fill.background()
    add_textbox(slide, heading, Inches(6.80), dy, Inches(5.80), Inches(0.28),
                size=10, color=WHITE, bold=True)
    add_textbox(slide, detail,  Inches(6.80), dy + Inches(0.28), Inches(5.80), Inches(0.38),
                size=9, color=LGRAY)
    dy += Inches(0.85)

print("Slide 3 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — SOLUTION ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Solution Architecture", "Azure-native replacement for Toad automation")
add_footer(slide)

components = [
    (GREEN,  "Azure Data Factory",  "PL_Toad_POC",          "Orchestrates the full pipeline — ODS check, data copy,\nfunction call, archive & email notification"),
    (CYAN,   "Azure SQL Database",  "sql-toad-poc / db-toad-poc", "Stores gas escape data (abcbimart schema)\n1,000 fact rows + dimension tables"),
    (PURPLE, "Azure Blob Storage",  "sttoadpoc",             "Holds CSV output, populated XLSM,\narchive reports and the XLSM template"),
    (YELLOW, "Azure Key Vault",     "kv-toad-poc",           "Stores storage key, SQL password\nand Function App key securely"),
    (PINK,   "Azure Functions",     "func-toad-poc",         "populate_template: reads CSV, fills\nRaw Data sheet in XLSM template"),
    (CYAN,   "Logic App (stub)",    "la-toad-poc-email",     "HTTP trigger ready for Office 365\nemail connection (deferred)"),
]

cw = Inches(1.98); ch = Inches(2.55); gap = Inches(0.10)
sx = Inches(0.28); sy = Inches(1.50)

for i, (col, name, resource, desc) in enumerate(components):
    col_pos = i % 3; row_pos = i // 3
    x = sx + col_pos * (cw + gap)
    y = sy + row_pos * (ch + gap)

    box = slide.shapes.add_shape(1, x, y, cw, ch)
    box.fill.solid(); box.fill.fore_color.rgb = DGRAY
    box.line.color.rgb = col; box.line.width = Pt(1)

    # colour top bar
    bar = slide.shapes.add_shape(1, x, y, cw, Inches(0.08))
    bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()

    add_textbox(slide, name,     x + Inches(0.12), y + Inches(0.15), cw - Inches(0.24),
                Inches(0.36), size=10.5, color=col, bold=True)
    add_textbox(slide, resource, x + Inches(0.12), y + Inches(0.52), cw - Inches(0.24),
                Inches(0.30), size=8.5,  color=WHITE, bold=False)
    add_textbox(slide, desc,     x + Inches(0.12), y + Inches(0.88), cw - Inches(0.24),
                Inches(1.55), size=8.5,  color=LGRAY)

print("Slide 4 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — ADF PIPELINE FLOW DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "ADF Pipeline Flow", "PL_Toad_POC — activity chain inside Azure Data Factory")
add_footer(slide)

# ── Arrow / line helpers ───────────────────────────────────────────────────────
def _rect(sl, x, y, w, h, col):
    s = sl.shapes.add_shape(1, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = col; s.line.fill.background()

def h_arrow(sl, x1, yc, x2, col=GREEN):
    """Horizontal line + right-arrow tip."""
    _rect(sl, x1, yc - Inches(0.025), x2 - x1 - Inches(0.15), Inches(0.05), col)
    tip = sl.shapes.add_shape(13, x2 - Inches(0.17), yc - Inches(0.12), Inches(0.17), Inches(0.24), )
    tip.fill.solid(); tip.fill.fore_color.rgb = col; tip.line.fill.background()

def v_arrow(sl, xc, y1, y2, col=GREEN):
    """Vertical line + down-arrow tip."""
    _rect(sl, xc - Inches(0.025), y1, Inches(0.05), y2 - y1 - Inches(0.13), col)
    tip = sl.shapes.add_shape(36, xc - Inches(0.12), y2 - Inches(0.15), Inches(0.24), Inches(0.15))
    tip.fill.solid(); tip.fill.fore_color.rgb = col; tip.line.fill.background()

def h_line(sl, x1, yc, x2, col=GREEN):
    _rect(sl, min(x1, x2), yc - Inches(0.025), abs(x2 - x1), Inches(0.05), col)

def v_line(sl, xc, y1, y2, col=GREEN):
    _rect(sl, xc - Inches(0.025), y1, Inches(0.05), y2 - y1, col)

def flow_box(sl, x, y, w, h, title5, detail5, col, decision=False):
    bg_col = RGBColor(0x1E, 0x1A, 0x00) if decision else DGRAY
    box = sl.shapes.add_shape(1, x, y, w, h)
    box.fill.solid(); box.fill.fore_color.rgb = bg_col
    box.line.color.rgb = col; box.line.width = Pt(2.0 if decision else 1.2)
    bar = sl.shapes.add_shape(1, x, y, w, Inches(0.07))
    bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()
    add_textbox(sl, title5, x + Inches(0.08), y + Inches(0.10),
                w - Inches(0.16), Inches(0.40), size=9, color=col, bold=True, align=PP_ALIGN.CENTER)
    if detail5:
        add_textbox(sl, detail5, x + Inches(0.08), y + Inches(0.52),
                    w - Inches(0.16), Inches(h / Inches(1) - 0.62) * Inches(1),
                    size=7.5, color=LGRAY, align=PP_ALIGN.CENTER)

# ── Layout constants ───────────────────────────────────────────────────────────
BW1 = Inches(2.60)   # top-row box width
BH1 = Inches(1.05)   # top-row box height
AW1 = Inches(0.45)   # top-row arrow gap
BW3 = Inches(2.80)   # If-box width
y1  = Inches(1.58)
yc1 = y1 + BH1 / 2

# x positions for top row
x_lkp = Inches(0.35)
x_set = x_lkp + BW1 + AW1
x_iff = x_set + BW1 + AW1      # = 0.35 + 2.60+0.45 + 2.60+0.45 = 6.45
xc_iff = x_iff + BW3 / 2       # center of If box = 7.85
x_iff_r = x_iff + BW3          # right edge = 9.25

# ── Top row: Lookup → SetVar → If ─────────────────────────────────────────────
flow_box(slide, x_lkp, y1, BW1, BH1,
         "Lookup ODS Check", "Queries T_ODS_LOG\nfor today's data refresh", GREEN)
h_arrow(slide, x_lkp + BW1, yc1, x_set, GREEN)

flow_box(slide, x_set, y1, BW1, BH1,
         "Set Report Date", "Sets dd.MM.yyyy\nvariable (yesterday)", CYAN)
h_arrow(slide, x_set + BW1, yc1, x_iff, CYAN)

flow_box(slide, x_iff, y1, BW3, BH1,
         "If ODS Refreshed?", "row_count > 0", YELLOW, decision=True)

# ── NO branch: right arrow → Email Not Refreshed ──────────────────────────────
no_x = x_iff_r + Inches(0.35)
flow_box(slide, no_x, y1, Inches(3.38), BH1,
         "Email: ODS Not Refreshed", "Logic App POST to Ops\n(no data today)", PINK)
h_arrow(slide, x_iff_r, yc1, no_x, PINK)
add_textbox(slide, "NO", x_iff_r + Inches(0.04), yc1 - Inches(0.30),
            Inches(0.30), Inches(0.22), size=7.5, color=PINK, bold=True)

# ── YES label ─────────────────────────────────────────────────────────────────
add_textbox(slide, "YES", xc_iff + Inches(0.07), y1 + BH1 + Inches(0.03),
            Inches(0.38), Inches(0.20), size=7.5, color=GREEN, bold=True)

# ── Row 2: true-branch 5 activities ───────────────────────────────────────────
BW2 = Inches(2.25)
BH2 = Inches(1.08)
AW2 = Inches(0.26)
y2  = Inches(3.20)
yc2 = y2 + BH2 / 2

total_w2 = 5 * BW2 + 4 * AW2        # 12.29 in
sx2 = (SW - total_w2) / 2            # 0.52 in
box1_cx = sx2 + BW2 / 2              # center of Box 4 = 1.645 in

row2 = [
    (GREEN,  "Copy Data\nto Blob",          "Runs SQL query\nCSV → Blob output/"),
    (CYAN,   "Populate Excel\nTemplate",    "Azure Function call\nCSV → XLSM"),
    (PURPLE, "Copy Archive\nFile",          "XLSM → archive/\nwith report name"),
    (YELLOW, "Email Report to\nOperations", "Logic App POST\n.xlsm attachment"),
    (PINK,   "Email BI Team\nConfirmation", "Pipeline complete\nconfirmation"),
]

for i, (col, title5, detail5) in enumerate(row2):
    bx2 = sx2 + i * (BW2 + AW2)
    flow_box(slide, bx2, y2, BW2, BH2, title5, detail5, col)
    if i < len(row2) - 1:
        h_arrow(slide, bx2 + BW2, yc2, bx2 + BW2 + AW2, col)

# ── Elbow connector: If box → Box 4 (L-shape) ─────────────────────────────────
elbow_y = Inches(2.83)
v_line(slide,  xc_iff,   y1 + BH1 + Inches(0.26), elbow_y, GREEN)
h_line(slide,  box1_cx,  elbow_y, xc_iff, GREEN)
v_arrow(slide, box1_cx,  elbow_y, y2, GREEN)

# ── Legend strip at bottom ─────────────────────────────────────────────────────
leg_y = Inches(4.45)
legend = [
    (GREEN,  "Sequential flow"),
    (YELLOW, "Decision / branch"),
    (PINK,   "False path (no data)"),
    (CYAN,   "Azure Function call"),
]
lx = Inches(0.50)
for col, lbl in legend:
    dot = slide.shapes.add_shape(1, lx, leg_y + Inches(0.06), Inches(0.18), Inches(0.18))
    dot.fill.solid(); dot.fill.fore_color.rgb = col; dot.line.fill.background()
    add_textbox(slide, lbl, lx + Inches(0.26), leg_y, Inches(2.20), Inches(0.30),
                size=8, color=LGRAY)
    lx += Inches(2.60)

print("Slide 5 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — AZURE FUNCTION DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Azure Function: populate_template",
           "Converts ADF CSV output into the Excel XLSM template")
add_footer(slide)

# Left: flow steps
add_textbox(slide, "Function Execution Flow", Inches(0.40), Inches(1.50),
            Inches(5.50), Inches(0.35), size=11, color=GREEN, bold=True)

flow_steps = [
    (GREEN,  "1. Receive POST",    "ADF WebActivity calls the function with\nreport_date, csv_blob path and out_blob path"),
    (CYAN,   "2. Download CSV",    "Reads BC_BIMIO_267_PRECOPY_<date>.csv\nfrom toad-poc-reports/output/ in Blob Storage"),
    (PURPLE, "3. Download Template","Fetches BC_BIMIO_267_TEMPLATE.xlsm\nfrom toad-poc-reports/templates/"),
    (YELLOW, "4. Populate Sheet",  "Clears Raw Data rows 2+, writes all\nCSV rows using openpyxl (keep_vba=True)"),
    (PINK,   "5. Upload XLSM",     "Uploads populated workbook back to\nBlob Storage as BC_BIMIO_267_PRECOPY_<date>.xlsm"),
    (GREEN,  "6. Return 200",      "Returns {status: success, output_blob: ...}\nADF marks activity Succeeded"),
]

fy = Inches(1.95)
for col, step, detail in flow_steps:
    dot = slide.shapes.add_shape(1, Inches(0.40), fy + Inches(0.08), Inches(0.14), Inches(0.14))
    dot.fill.solid(); dot.fill.fore_color.rgb = col; dot.line.fill.background()
    add_textbox(slide, step,   Inches(0.68), fy,                Inches(5.20), Inches(0.28), size=9.5, color=WHITE, bold=True)
    add_textbox(slide, detail, Inches(0.68), fy + Inches(0.28), Inches(5.20), Inches(0.40), size=8.5, color=LGRAY)
    fy += Inches(0.82)

# Divider
div = slide.shapes.add_shape(1, Inches(6.10), Inches(1.45), Inches(0.04), Inches(5.30))
div.fill.solid(); div.fill.fore_color.rgb = CYAN; div.line.fill.background()

# Right: tech details
add_textbox(slide, "Technical Details", Inches(6.30), Inches(1.50),
            Inches(6.60), Inches(0.35), size=11, color=CYAN, bold=True)

tech = [
    ("Runtime",        "Python 3.11, Linux Consumption Plan"),
    ("Auth",           "Function key (stored in Key Vault)"),
    ("Storage access", "STORAGE_CONNECTION_STRING app setting"),
    ("Template",       "keep_vba=True — macros preserved in .xlsm"),
    ("Deployed via",   "Azure Functions Core Tools v4 (remote build)"),
    ("Endpoint",       "func-toad-poc.azurewebsites.net\n/api/populate_template?code=<key>"),
    ("POST body", '{\n  "report_date": "13.05.2026",\n  "csv_blob": "output/...csv",\n  "out_blob": "output/...xlsm"\n}'),
]

ty2 = Inches(1.95)
for label, val in tech:
    add_textbox(slide, label, Inches(6.30), ty2, Inches(1.90), Inches(0.35),
                size=9, color=CYAN, bold=True)
    add_textbox(slide, val,   Inches(8.30), ty2, Inches(4.60), Inches(0.50),
                size=9, color=LGRAY)
    ty2 += Inches(0.65)

print("Slide 6 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — SAMPLE DATA & TESTING
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Sample Data & Testing", "1,000 gas escape records generated with full referential integrity")
add_footer(slide)

tables = [
    (GREEN,  "dim_organisation",    "20 rows",   "3 networks, 5 LDZs, 20 depots"),
    (CYAN,   "dim_addresses",       "50 rows",   "Generic display addresses across 26 towns"),
    (PURPLE, "dim_calendar",        "43 rows",   "2026-04-01 to 2026-05-13 (SQL date range)"),
    (YELLOW, "dim_time",            "24 rows",   "Hourly time slots 00:00 to 23:00"),
    (PINK,   "dim_work_orders",     "2,000 rows","IDs 1-1000 root WOs, 1001-2000 gas-prevented WOs"),
    (GREEN,  "fct_gas_escapes_v",   "1,000 rows","Links all dimensions; latest='Y' on all rows"),
]

tw2 = Inches(5.80); th = Inches(0.68); gap2 = Inches(0.10)
col2_x = Inches(6.80)
sy2 = Inches(1.50)

for i, (col, tname, count, desc) in enumerate(tables):
    row = i % 3; half = i // 3
    x2 = Inches(0.30) if half == 0 else col2_x
    y2 = sy2 + row * (th + gap2)

    box = slide.shapes.add_shape(1, x2, y2, tw2, th)
    box.fill.solid(); box.fill.fore_color.rgb = DGRAY
    box.line.color.rgb = col; box.line.width = Pt(0.75)

    bar = slide.shapes.add_shape(1, x2, y2, Inches(0.08), th)
    bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()

    add_textbox(slide, tname, x2 + Inches(0.20), y2 + Inches(0.05),
                Inches(2.40), Inches(0.30), size=10, color=col, bold=True)
    add_textbox(slide, count, x2 + Inches(0.20), y2 + Inches(0.35),
                Inches(1.20), Inches(0.28), size=9.5, color=WHITE, bold=True)
    add_textbox(slide, desc,  x2 + Inches(2.70), y2 + Inches(0.15),
                Inches(2.90), Inches(0.48), size=8.5, color=LGRAY)

# Bottom summary banner
banner = slide.shapes.add_shape(1, Inches(0.30), Inches(5.95), Inches(12.70), Inches(0.65))
banner.fill.solid(); banner.fill.fore_color.rgb = RGBColor(0x1A, 0x3A, 0x1A)
banner.line.color.rgb = GREEN; banner.line.width = Pt(0.75)

add_textbox(slide, "Tools:  generate_sample_data.py  (creates CSVs)    |    load_sample_data.py  (pushes to Azure SQL)    |    Pipeline run verified all 1,000 rows end-to-end",
            Inches(0.50), Inches(6.00), Inches(12.30), Inches(0.55),
            size=9, color=GREEN, align=PP_ALIGN.CENTER)

print("Slide 7 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — MIGRATION PROCESS FLOW
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Migration Process Flow",
           "From Toad XML reports to cloud-native automated delivery")
add_footer(slide)

def mbox(sl, x, y, w, h, step_num, title_m, bullets_m, col):
    box = sl.shapes.add_shape(1, x, y, w, h)
    box.fill.solid(); box.fill.fore_color.rgb = DGRAY
    box.line.color.rgb = col; box.line.width = Pt(1.2)
    topbar = sl.shapes.add_shape(1, x, y, w, Inches(0.07))
    topbar.fill.solid(); topbar.fill.fore_color.rgb = col; topbar.line.fill.background()
    badge = sl.shapes.add_shape(1, x + Inches(0.10), y + Inches(0.10), Inches(0.58), Inches(0.24))
    badge.fill.solid(); badge.fill.fore_color.rgb = col; badge.line.fill.background()
    add_textbox(sl, f"Step {step_num}", x + Inches(0.10), y + Inches(0.09),
                Inches(0.58), Inches(0.25), size=7, color=BG, bold=True, align=PP_ALIGN.CENTER)
    add_textbox(sl, title_m, x + Inches(0.10), y + Inches(0.38),
                w - Inches(0.20), Inches(0.30), size=9.5, color=WHITE, bold=True)
    tb = sl.shapes.add_textbox(x + Inches(0.10), y + Inches(0.72), w - Inches(0.20), h - Inches(0.80))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for line in bullets_m:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run(); r.text = line
        r.font.name = "Arial"; r.font.size = Pt(8); r.font.color.rgb = LGRAY

# ── Row 1: Steps 1-4 ──────────────────────────────────────────────────────────
BW1 = Inches(2.75); BH1 = Inches(1.35); GAP1 = Inches(0.38)
y1m  = Inches(1.58)
sx1m = (SW - (4 * BW1 + 3 * GAP1)) / 2

s1x = sx1m
s2x = sx1m + BW1 + GAP1
s3x = sx1m + 2 * (BW1 + GAP1)
s4x = sx1m + 3 * (BW1 + GAP1)
s4cx = s4x + BW1 / 2

mbox(slide, s1x, y1m, BW1, BH1, "1", "Receive Toad XML Reports",
     ["• 200+ report definitions in XML format",
      "• Each holds SQL query, schedule, user list & output format",
      "• UTF-16 encoded — sanitised before use"], GREEN)

mbox(slide, s2x, y1m, BW1, BH1, "2", "Sanitize & Extract to Flat File",
     ["• Microsoft Presidio NLP removes sensitive data",
      "• Actual + mockup data stored — one flat file per report",
      "• Output auto-feeds Step 5 config (no manual effort)"], CYAN)

mbox(slide, s3x, y1m, BW1, BH1, "3", "Analyse Sources & Access Rules",
     ["• Reports span multiple source databases",
      "• User access levels vary per report",
      "• Captured in config for Phase 2 — retained for future use"], PURPLE)

mbox(slide, s4x, y1m, BW1, BH1, "4", "Build Pipeline & Components",
     ["• ADF / AWS pipeline + datasets + linked services",
      "• Azure Function, Blob Storage, Key Vault, Logic App",
      "• Step 2 flat file used as configuration blueprint"], YELLOW)

y1mc = y1m + BH1 / 2
for bx in [s1x, s2x, s3x]:
    h_arrow(slide, bx + BW1, y1mc, bx + BW1 + GAP1, GREEN)

# ── Row 2: Steps 5-7 ──────────────────────────────────────────────────────────
BW2 = Inches(3.40); BH2 = Inches(1.35); GAP2 = Inches(0.42)
y2m  = Inches(3.55)
sx2m = (SW - (3 * BW2 + 2 * GAP2)) / 2

s5x  = sx2m
s6x  = sx2m + BW2 + GAP2
s7x  = sx2m + 2 * (BW2 + GAP2)
s5cx = sx2m + BW2 / 2
y2mc = y2m + BH2 / 2

mbox(slide, s5x, y2m, BW2, BH2, "5", "Configure Report-User Matrix",
     ["• Auto-generated directly from Step 2 flat file — zero manual effort",
      "• Centralised config: one record per report-user pair",
      "• Add / remove user = data change only — no code or flow change needed"], GREEN)

mbox(slide, s6x, y2m, BW2, BH2, "6", "Set Up Email Triggers",
     ["• Logic App triggered per report configuration",
      "• Report delivered to configured recipient list automatically",
      "• Pipeline failure alert routed to assigned engineer instantly"], CYAN)

mbox(slide, s7x, y2m, BW2, BH2, "7", "Daily Audit & Monitoring",
     ["• Flat file audit log created per pipeline run — full traceability",
      "• ADF Monitor / CloudWatch metrics available at all times",
      "• Failure detected → alert email sent to assigned person"], PINK)

h_arrow(slide, s5x + BW2, y2mc, s6x, CYAN)
h_arrow(slide, s6x + BW2, y2mc, s7x, PINK)

# ── Elbow connector: Step 4 → Step 5 (L-shape) ────────────────────────────────
y1m_bot  = y1m + BH1
elbow_ym = (y1m_bot + y2m) / 2

v_line(slide,  s4cx,  y1m_bot,  elbow_ym, GREEN)
h_line(slide,  s5cx,  elbow_ym, s4cx,     GREEN)
v_arrow(slide, s5cx,  elbow_ym, y2m,      GREEN)

# ── Step 2 → Step 5 dotted feed indicator ─────────────────────────────────────
s2cx   = s2x + BW1 / 2
dot_y  = elbow_ym - Inches(0.14)
n_dots = 9
for i in range(n_dots):
    dx = s5cx + (s2cx - s5cx) * i / (n_dots - 1)
    _rect(slide, dx, dot_y, Inches(0.10), Inches(0.04), CYAN)
add_textbox(slide, "Step 2 output", s5cx + Inches(0.32), dot_y - Inches(0.23),
            Inches(1.55), Inches(0.22), size=7, color=CYAN)

# ── ADF / AWS Advantages strip ────────────────────────────────────────────────
adv_y  = Inches(5.08)
adv_bg = slide.shapes.add_shape(1, Inches(0.30), adv_y - Inches(0.08), Inches(12.73), Inches(1.84))
adv_bg.fill.solid(); adv_bg.fill.fore_color.rgb = RGBColor(0x0A, 0x14, 0x0A)
adv_bg.line.color.rgb = GREEN; adv_bg.line.width = Pt(0.75)

add_textbox(slide, "vs Toad  —  Why ADF / AWS?",
            Inches(0.45), adv_y - Inches(0.04), Inches(12.0), Inches(0.26),
            size=8.5, color=GREEN, bold=True)

advantages = [
    (GREEN,  "Auto-Retry on Failure",
     "ADF retries automatically on transient errors.\nToad = manual restart every time"),
    (CYAN,   "Full Audit Trail",
     "Every run logged in ADF Monitor with timestamps.\nToad = zero visibility"),
    (YELLOW, "Instant Failure Alerts",
     "Alert email sent to assigned engineer on failure.\nToad = nobody knows until morning"),
    (PURPLE, "Central User Config",
     "Add or remove a user = one data row change.\nToad = edit script for every affected report"),
    (PINK,   "Scale to 200+ Reports",
     "Same pipeline pattern handles all reports.\nToad = one separate script per report"),
]

aw = Inches(2.34); ag = Inches(0.20); ax = Inches(0.45)
for col, adv_t, adv_d in advantages:
    abar = slide.shapes.add_shape(1, ax, adv_y + Inches(0.25), aw, Inches(0.05))
    abar.fill.solid(); abar.fill.fore_color.rgb = col; abar.line.fill.background()
    add_textbox(slide, adv_t, ax, adv_y + Inches(0.34), aw, Inches(0.26), size=8.5, color=col, bold=True)
    add_textbox(slide, adv_d, ax, adv_y + Inches(0.62), aw, Inches(1.00), size=7.5, color=LGRAY)
    ax += aw + ag

print("Slide 8 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — NEXT STEPS
# ═══════════════════════════════════════════════════════════════════════════════
slide = add_slide()
add_header_bar(slide)
add_logo(slide)
title_text(slide, "Next Steps", "Remaining work to complete the POC and expand to AWS")
add_footer(slide)

next_steps = [
    (GREEN,  "Email Integration",
     "Connect Logic App to Office 365",
     ["Wire la-toad-poc-email to Office 365 connector",
      "Map subject, to, body and attachment_path fields",
      "Test with real report attachment (.xlsm)",
      "Confirm delivery to operations-distribution@abc.co.uk"]),
    (CYAN,   "Pipeline Hardening",
     "Monitoring, alerts and scheduling",
     ["Add ADF trigger (daily 06:00 UTC)",
      "Set up Azure Monitor alert on pipeline failure",
      "Add spending alert on rg-toad-poc resource group",
      "Review Key Vault secret rotation policy"]),
    (PURPLE, "AWS Equivalent POC",
     "Replicate the same flow on AWS",
     ["AWS Glue job replaces ADF Copy activity",
      "AWS Lambda replaces Azure Function",
      "S3 replaces Blob Storage",
      "Amazon SES replaces Logic App email",
      "Compare cost, complexity and dev experience"]),
    (YELLOW, "Documentation & Handover",
     "Formalise the POC findings",
     ["Architecture decision record (ADR)",
      "Runbook for pipeline operations",
      "Cost comparison: Toad vs Azure vs AWS",
      "Present findings to stakeholders"]),
]

nw = Inches(2.90); nh = Inches(4.60); nsy = Inches(1.50)
nsx = Inches(0.28)

for i, (col, title3, subtitle3, bullets3) in enumerate(next_steps):
    x5 = nsx + i * (nw + Inches(0.12))
    box = slide.shapes.add_shape(1, x5, nsy, nw, nh)
    box.fill.solid(); box.fill.fore_color.rgb = DGRAY
    box.line.color.rgb = col; box.line.width = Pt(1)

    bar = slide.shapes.add_shape(1, x5, nsy, nw, Inches(0.08))
    bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()

    add_textbox(slide, title3,    x5 + Inches(0.12), nsy + Inches(0.12),
                nw - Inches(0.24), Inches(0.38), size=11, color=col, bold=True)
    add_textbox(slide, subtitle3, x5 + Inches(0.12), nsy + Inches(0.52),
                nw - Inches(0.24), Inches(0.32), size=8.5, color=WHITE)

    dl = slide.shapes.add_shape(1, x5 + Inches(0.12), nsy + Inches(0.88),
                                 nw - Inches(0.24), Inches(0.03))
    dl.fill.solid(); dl.fill.fore_color.rgb = col; dl.line.fill.background()

    add_bullet_box(slide, x5 + Inches(0.12), nsy + Inches(1.00),
                   nw - Inches(0.24), Inches(3.40),
                   ["• " + b for b in bullets3], size=9)

print("Slide 9 done")


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════════
prs.save(OUT_FILE)
print(f"\nSaved: {OUT_FILE}")
