"""
create_presentation.py
Creates a professional PowerPoint presentation for the Utilitics Azure Databricks
Data Sharing Platform project — suitable for mixed audience (executives + technical team).
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import datetime

# ─── Colour Palette ───────────────────────────────────────────────────────────
NAVY        = RGBColor(0x0D, 0x1B, 0x2A)   # dark navy — backgrounds
BLUE        = RGBColor(0x1B, 0x4F, 0x72)   # mid blue — headers
ACCENT      = RGBColor(0x00, 0xAE, 0xEF)   # bright cyan — highlights
GREEN       = RGBColor(0x1A, 0xBC, 0x9C)   # green — done/success
ORANGE      = RGBColor(0xE6, 0x7E, 0x22)   # orange — in progress
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY  = RGBColor(0xF4, 0xF6, 0xF7)
DARK_GRAY   = RGBColor(0x2C, 0x3E, 0x50)
MID_GRAY    = RGBColor(0x7F, 0x8C, 0x8D)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)


def rect(slide, left, top, width, height, fill_color=None, line_color=None, line_width=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width or Pt(1)
    else:
        shape.line.fill.background()
    return shape


def txt(slide, text, left, top, width, height,
        font_size=18, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(left, top, width, height)
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    run.font.name  = "Calibri"
    return txb


def txt_box(slide, lines, left, top, width, height,
            font_size=16, color=DARK_GRAY, line_spacing=1.2):
    """Multi-line text box — lines is list of (text, bold, color_override)."""
    from pptx.util import Pt
    from pptx.oxml.ns import qn
    from lxml import etree
    txb = slide.shapes.add_textbox(left, top, width, height)
    txb.word_wrap = True
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in lines:
        if isinstance(item, str):
            text, bold, col = item, False, color
        else:
            text = item[0]
            bold = item[1] if len(item) > 1 else False
            col  = item[2] if len(item) > 2 else color

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = text
        run.font.size  = Pt(font_size)
        run.font.bold  = bold
        run.font.color.rgb = col
        run.font.name  = "Calibri"
    return txb


def header_bar(slide, title, subtitle=None):
    """Dark navy top bar with title."""
    rect(slide, 0, 0, SLIDE_W, Inches(1.35), fill_color=NAVY)
    rect(slide, 0, Inches(1.35), SLIDE_W, Pt(4), fill_color=ACCENT)
    txt(slide, title, Inches(0.4), Inches(0.18), Inches(12), Inches(0.7),
        font_size=28, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, Inches(0.4), Inches(0.82), Inches(10), Inches(0.45),
            font_size=16, color=ACCENT, bold=False)


def footer(slide, slide_num, total=15):
    rect(slide, 0, Inches(7.1), SLIDE_W, Inches(0.4), fill_color=NAVY)
    txt(slide, "UTILITICS | Azure Databricks Data Sharing Platform | Confidential",
        Inches(0.3), Inches(7.12), Inches(10), Inches(0.3),
        font_size=9, color=MID_GRAY)
    txt(slide, f"{slide_num} / {total}",
        Inches(12.5), Inches(7.12), Inches(0.7), Inches(0.3),
        font_size=9, color=MID_GRAY, align=PP_ALIGN.RIGHT)


def stat_box(slide, left, top, width, height, number, label, color=ACCENT):
    rect(slide, left, top, width, height, fill_color=NAVY)
    rect(slide, left, top, width, Pt(4), fill_color=color)
    txt(slide, number, left, top + Inches(0.15), width, Inches(0.7),
        font_size=32, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(slide, label, left, top + Inches(0.75), width, Inches(0.5),
        font_size=11, color=WHITE, align=PP_ALIGN.CENTER)


def status_pill(slide, left, top, label, done=True):
    color = GREEN if done else ORANGE
    status = "DONE" if done else "IN PROGRESS"
    rect(slide, left, top, Inches(1.1), Inches(0.32), fill_color=color)
    txt(slide, status, left, top, Inches(1.1), Inches(0.32),
        font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


# ─── Slide Builders ──────────────────────────────────────────────────────────

def slide_01_title(prs):
    s = blank_slide(prs)

    # Full background
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)

    # Left accent strip
    rect(s, 0, 0, Inches(0.18), SLIDE_H, fill_color=ACCENT)

    # Bottom accent line
    rect(s, 0, Inches(6.8), SLIDE_W, Pt(4), fill_color=ACCENT)

    # Company tag
    txt(s, "UTILITICS", Inches(0.4), Inches(0.4), Inches(5), Inches(0.5),
        font_size=13, bold=True, color=ACCENT)

    # Main title
    txt(s, "Azure Databricks\nData Sharing Platform",
        Inches(0.4), Inches(1.2), Inches(9), Inches(2.2),
        font_size=44, bold=True, color=WHITE)

    # Subtitle
    txt(s, "Proof of Concept — Progress & Roadmap Presentation",
        Inches(0.4), Inches(3.3), Inches(9), Inches(0.6),
        font_size=20, color=ACCENT, italic=True)

    # Divider
    rect(s, Inches(0.4), Inches(4.0), Inches(4), Pt(2), fill_color=ACCENT)

    # Meta info
    txt(s, f"Presented by:  Radhakrishnan Karnakumar",
        Inches(0.4), Inches(4.2), Inches(8), Inches(0.4),
        font_size=14, color=WHITE)
    txt(s, f"Date:  April 2026",
        Inches(0.4), Inches(4.65), Inches(8), Inches(0.4),
        font_size=14, color=MID_GRAY)
    txt(s, "Audience:  Executive Leadership + Technical Team",
        Inches(0.4), Inches(5.1), Inches(8), Inches(0.4),
        font_size=14, color=MID_GRAY)

    # Right side graphic element
    rect(s, Inches(10.5), Inches(1.5), Inches(2.5), Inches(4.5), fill_color=BLUE)
    txt(s, "POC\nSTATUS", Inches(10.5), Inches(2.2), Inches(2.5), Inches(1.2),
        font_size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    rect(s, Inches(10.7), Inches(3.5), Inches(2.1), Pt(2), fill_color=ACCENT)
    txt(s, "Part 1\nComplete", Inches(10.5), Inches(3.6), Inches(2.5), Inches(0.8),
        font_size=14, color=GREEN, bold=True, align=PP_ALIGN.CENTER)
    txt(s, "Part 2\nIn Progress", Inches(10.5), Inches(4.4), Inches(2.5), Inches(0.8),
        font_size=14, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)


def slide_02_agenda(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Agenda", "What we will cover today")
    footer(s, 2)

    items = [
        ("01", "Business Requirement",        "What was asked of us"),
        ("02", "Our Approach",                "Why local first, then Azure"),
        ("03", "What is Databricks?",         "Origin, platform overview, simple explanation"),
        ("04", "Databricks Key Features",     "Delta Lake, Unity Catalog, Medallion, Sharing"),
        ("05", "Why Azure Databricks?",       "Azure integration, cost, vs alternatives"),
        ("06", "Solution Architecture",       "End-to-end platform design"),
        ("07", "Technology Stack",            "Tools used and why"),
        ("08", "Part 1 — Local POC",          "What we built, fully working"),
        ("09", "Part 2 — Azure Migration",    "Current progress on cloud"),
        ("10", "Key Achievements",            "Highlights and live features"),
        ("11", "What's Next",                 "Remaining phases and plan"),
        ("12", "Business Value",              "What this delivers when complete"),
        ("13", "Q&A",                         "Open discussion"),
    ]

    col1_x = Inches(0.4)
    col2_x = Inches(7.0)
    top    = Inches(1.6)
    gap    = Inches(0.52)

    for i, (num, title, desc) in enumerate(items):
        col = col1_x if i < 5 else col2_x
        row = (i % 5) * gap + top

        rect(s, col, row, Inches(0.42), Inches(0.38), fill_color=ACCENT)
        txt(s, num, col, row, Inches(0.42), Inches(0.38),
            font_size=12, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s, title, col + Inches(0.5), row, Inches(2.8), Inches(0.38),
            font_size=14, bold=True, color=DARK_GRAY)
        txt(s, desc,  col + Inches(0.5), row + Inches(0.22), Inches(2.8), Inches(0.28),
            font_size=10, color=MID_GRAY)


def slide_03_requirement(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Business Requirement", "What was asked — Statement of Work")
    footer(s, 3)

    # Left box
    rect(s, Inches(0.3), Inches(1.6), Inches(5.9), Inches(5.1), fill_color=WHITE)
    rect(s, Inches(0.3), Inches(1.6), Inches(5.9), Pt(4), fill_color=BLUE)
    txt(s, "The Brief", Inches(0.5), Inches(1.7), Inches(5), Inches(0.45),
        font_size=16, bold=True, color=BLUE)

    reqs = [
        "Build a modern Data Sharing Platform on Azure Databricks",
        "Handle 3 types of energy data from Utilitics:",
        "    Time Series — 168,000 smart meter readings",
        "    Snapshot   — 14,000 network asset records (SQL)",
        "    File Data  — 84,000 demand forecast records",
        "Implement Medallion architecture (Bronze → Silver → Gold)",
        "Enable secure Delta Sharing with external vendors",
        "Automate pipeline execution and monitoring",
        "Keep costs under $25/month",
    ]
    txt_box(s, [(r, "Utilitics" in r or "3 types" in r or "Medallion" in r
                    or "Delta Sharing" in r, DARK_GRAY) for r in reqs],
            Inches(0.5), Inches(2.25), Inches(5.5), Inches(4.0),
            font_size=13, color=DARK_GRAY)

    # Right box
    rect(s, Inches(6.5), Inches(1.6), Inches(6.5), Inches(5.1), fill_color=NAVY)
    rect(s, Inches(6.5), Inches(1.6), Inches(6.5), Pt(4), fill_color=ACCENT)
    txt(s, "Success Criteria", Inches(6.7), Inches(1.7), Inches(6), Inches(0.45),
        font_size=16, bold=True, color=ACCENT)

    criteria = [
        ("Full pipeline runs end-to-end", True),
        ("19/19 data quality checks pass", True),
        ("Data shared with vendor (Utilitics→Vendor, read-only)", True),
        ("Pipeline controllable via WhatsApp", True),
        ("Gold data visible in Power BI", True),
        ("Runs on Azure cloud (not just local)", False),
        ("Scheduled automation (Workflows)", False),
    ]
    top_c = Inches(2.25)
    for label, done in criteria:
        color  = GREEN if done else ORANGE
        symbol = "✔" if done else "◉"
        txt(s, symbol, Inches(6.7), top_c, Inches(0.4), Inches(0.38),
            font_size=14, bold=True, color=color)
        txt(s, label, Inches(7.2), top_c, Inches(5.5), Inches(0.38),
            font_size=13, color=WHITE)
        top_c += Inches(0.45)


def slide_04_approach(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Our Approach", "Local first — then Azure. Zero risk, zero wasted spend.")
    footer(s, 4)

    # Two phase boxes
    for i, (phase, color, title, points) in enumerate([
        ("PHASE 1", GREEN, "Local Development (Zero Cost)",
         ["Build entire platform on Windows 11 laptop",
          "PySpark + Delta Lake — same code as cloud",
          "Validate all logic before spending on cloud",
          "Fast iteration — no cluster startup wait",
          "Cost: $0   Duration: 2 weeks"]),
        ("PHASE 2", ACCENT, "Azure Cloud Migration (~$5-8/month)",
         ["Lift-and-shift: 3 path changes, code unchanged",
          "ADLS Gen2 storage + Databricks Premium workspace",
          "Unity Catalog for governance & Delta Sharing",
          "Databricks Workflows for scheduling",
          "Azure Functions for permanent ChatOps webhook"]),
    ]):
        x = Inches(0.3 + i * 6.5)
        rect(s, x, Inches(1.6), Inches(6.1), Inches(5.1), fill_color=NAVY)
        rect(s, x, Inches(1.6), Inches(6.1), Pt(5), fill_color=color)
        rect(s, x, Inches(1.6), Inches(1.2), Inches(0.55), fill_color=color)
        txt(s, phase, x, Inches(1.6), Inches(1.2), Inches(0.55),
            font_size=11, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s, title, x + Inches(0.2), Inches(2.25), Inches(5.7), Inches(0.5),
            font_size=16, bold=True, color=WHITE)
        top_p = Inches(2.85)
        for pt in points:
            txt(s, f"  {pt}", x + Inches(0.1), top_p, Inches(5.8), Inches(0.42),
                font_size=13, color=LIGHT_GRAY)
            top_p += Inches(0.43)

    # Arrow between boxes
    txt(s, "→", Inches(6.25), Inches(3.8), Inches(0.5), Inches(0.6),
        font_size=36, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # Key benefit bar
    rect(s, Inches(0.3), Inches(6.85), Inches(12.7), Inches(0.4), fill_color=BLUE)
    txt(s, "Key Insight:  Same Python code runs locally and on Azure — only file paths change. No rewrite needed.",
        Inches(0.5), Inches(6.87), Inches(12.3), Inches(0.35),
        font_size=12, color=WHITE, bold=True)


def slide_08_architecture(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "Solution Architecture", "End-to-end data platform — Medallion + Delta Sharing + ChatOps")
    footer(s, 8)

    layers = [
        (ACCENT,  "DATA SOURCES",   ["Smart Meters\n(Parquet)", "Network Assets\n(SQL/SQLite)", "Demand Forecasts\n(Parquet)"]),
        (BLUE,    "BRONZE LAYER",   ["Raw ingestion", "Delta Lake tables", "Lineage metadata"]),
        (RGBColor(0x15,0x6A,0x9A), "SILVER LAYER", ["Deduplication", "Validation", "Derived columns"]),
        (RGBColor(0x1A,0x5C,0x4A), "GOLD LAYER",   ["daily_meter_summary", "regional_demand", "network_assets", "forecast_summary"]),
    ]

    box_w = Inches(2.6)
    gap   = Inches(0.2)
    top_l = Inches(1.6)
    ht    = Inches(3.2)

    for i, (color, label, items) in enumerate(layers):
        x = Inches(0.3) + i * (box_w + gap)
        rect(s, x, top_l, box_w, ht, fill_color=color)
        txt(s, label, x, top_l + Inches(0.08), box_w, Inches(0.4),
            font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        rect(s, x + Inches(0.1), top_l + Inches(0.45), box_w - Inches(0.2), Pt(1), fill_color=WHITE)
        top_i = top_l + Inches(0.6)
        for item in items:
            txt(s, f"• {item}", x + Inches(0.15), top_i, box_w - Inches(0.2), Inches(0.6),
                font_size=11, color=WHITE)
            top_i += Inches(0.55)
        if i < 3:
            txt(s, "▶", x + box_w + Inches(0.02), top_l + Inches(1.3), Inches(0.22), Inches(0.5),
                font_size=18, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # Bottom row — outputs
    outputs = [
        (GREEN,  "DELTA SHARING",    "Provider → Vendor\n(read-only protocol)\nVendor write-back = separate share / API"),
        (ACCENT, "CHATOPS",          "WhatsApp → Claude AI\n→ Pipeline control\n(Live & tested)"),
        (ORANGE, "POWER BI",         "Gold tables →\nDashboards &\nvisualisation"),
        (BLUE,   "WORKFLOWS",        "Scheduled pipeline\nAutomation\n(Azure — next)"),
    ]
    box_w2 = Inches(2.8)
    top_o  = Inches(5.1)
    ht2    = Inches(1.6)
    for i, (color, label, desc) in enumerate(outputs):
        x = Inches(0.3) + i * (box_w2 + Inches(0.35))
        rect(s, x, top_o, box_w2, ht2, fill_color=DARK_GRAY)
        rect(s, x, top_o, box_w2, Pt(4), fill_color=color)
        txt(s, label, x, top_o + Inches(0.05), box_w2, Inches(0.35),
            font_size=11, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s, desc, x, top_o + Inches(0.38), box_w2, Inches(1.1),
            font_size=10, color=WHITE, align=PP_ALIGN.CENTER)


def slide_09_techstack(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Technology Stack", "Industry-standard tools — all production-grade")
    footer(s, 9)

    categories = [
        ("Data Processing", BLUE, [
            ("Apache Spark / PySpark 3.5", "Distributed data processing engine"),
            ("Delta Lake 3.1",             "ACID transactions, time travel, schema enforcement"),
            ("Delta Sharing",              "Open protocol for secure cross-org data sharing"),
        ]),
        ("Azure Cloud", ACCENT, [
            ("Azure Databricks Premium",   "Managed Spark + Unity Catalog + Delta Sharing"),
            ("ADLS Gen2",                  "Enterprise data lake storage (hierarchical namespace)"),
            ("Azure Key Vault / Secrets",  "Secure credential management"),
        ]),
        ("Automation & ChatOps", GREEN, [
            ("Claude AI (Anthropic)",      "AI reasoning + tool use to control pipeline"),
            ("Twilio WhatsApp API",        "WhatsApp channel for pipeline control messages"),
            ("FastAPI + ngrok",            "Webhook server (local) → Azure Functions (cloud)"),
        ]),
        ("Local & Tooling", ORANGE, [
            ("SQLite → Azure SQL",         "Snapshot data source — same JDBC pattern both envs"),
            ("Power BI Desktop",           "Gold table visualisation, connects to Parquet/Delta"),
            ("Python-pptx / python-docx",  "Auto-generated documentation and presentations"),
        ]),
    ]

    col_w = Inches(6.0)
    row_h = Inches(2.4)
    pad   = Inches(0.25)

    for i, (cat, color, items) in enumerate(categories):
        col = i % 2
        row = i // 2
        x   = Inches(0.3) + col * (col_w + Inches(0.7))
        y   = Inches(1.6) + row * (row_h + Inches(0.15))

        rect(s, x, y, col_w, row_h, fill_color=WHITE)
        rect(s, x, y, col_w, Pt(4), fill_color=color)
        rect(s, x, y, Inches(0.08), row_h, fill_color=color)

        txt(s, cat, x + Inches(0.18), y + Inches(0.08), col_w, Inches(0.35),
            font_size=13, bold=True, color=color)

        top_i = y + Inches(0.5)
        for tech, desc in items:
            txt(s, tech, x + Inches(0.18), top_i, col_w - Inches(0.3), Inches(0.3),
                font_size=12, bold=True, color=DARK_GRAY)
            txt(s, desc, x + Inches(0.18), top_i + Inches(0.27), col_w - Inches(0.3), Inches(0.28),
                font_size=10, color=MID_GRAY)
            top_i += Inches(0.62)


def slide_10_part1(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Part 1 — Local POC", "Fully complete. All 15 sections done.")
    footer(s, 10)

    # Stat boxes
    stats = [
        ("266,000", "Records\nGenerated"),
        ("19 / 19",  "Quality Checks\nPassed"),
        ("~5 min",   "End-to-End\nPipeline"),
        ("$0",       "Development\nCost"),
    ]
    bw = Inches(2.8)
    for i, (num, lbl) in enumerate(stats):
        stat_box(s, Inches(0.3) + i * (bw + Inches(0.27)),
                 Inches(1.6), bw, Inches(1.3), num, lbl, ACCENT)

    # Two columns
    col_top = Inches(3.1)
    col_h   = Inches(3.6)

    # Left — What we built
    rect(s, Inches(0.3), col_top, Inches(5.9), col_h, fill_color=WHITE)
    rect(s, Inches(0.3), col_top, Inches(5.9), Pt(4), fill_color=BLUE)
    txt(s, "What We Built", Inches(0.5), col_top + Inches(0.1),
        Inches(5.5), Inches(0.4), font_size=15, bold=True, color=BLUE)

    built = [
        "Medallion pipeline: Bronze → Silver → Gold",
        "3 data sources: Time Series, SQL Snapshot, Forecasts",
        "Delta Sharing: simulated Utilitics → vendor (read-only protocol)",
        "ChatOps: WhatsApp → Claude AI → pipeline control",
        "Power BI: 4 Gold tables connected as dashboards",
        "SQLite as real DB source (Azure SQL in Part 2)",
        "Full docs: Word guide, PPT, flow diagram (HTML)",
    ]
    top_b = col_top + Inches(0.6)
    for item in built:
        txt(s, f"✔  {item}", Inches(0.5), top_b, Inches(5.5), Inches(0.4),
            font_size=12, color=DARK_GRAY)
        top_b += Inches(0.41)

    # Right — Live highlight
    rect(s, Inches(6.5), col_top, Inches(6.5), col_h, fill_color=NAVY)
    rect(s, Inches(6.5), col_top, Inches(6.5), Pt(4), fill_color=GREEN)
    txt(s, "Live Highlight — ChatOps", Inches(6.7), col_top + Inches(0.1),
        Inches(6.2), Inches(0.4), font_size=15, bold=True, color=GREEN)

    steps = [
        ("WhatsApp message: 'Run pipeline'", ACCENT),
        ("Twilio receives → sends to webhook", WHITE),
        ("FastAPI webhook → Claude AI (tool use)", WHITE),
        ("Claude calls run_pipeline tool", ACCENT),
        ("Pipeline runs in background (~3.5 min)", WHITE),
        ("Result sent back to WhatsApp", GREEN),
    ]

    top_s = col_top + Inches(0.65)
    for i, (step, color) in enumerate(steps):
        txt(s, f"{i+1}", Inches(6.7), top_s, Inches(0.35), Inches(0.38),
            font_size=12, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
        txt(s, step, Inches(7.15), top_s, Inches(5.6), Inches(0.38),
            font_size=12, color=color)
        top_s += Inches(0.42)


def slide_11_part2(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Part 2 — Azure Cloud Migration", "Infrastructure complete. Pipeline ready to run.")
    footer(s, 11)

    items = [
        (True,  "Azure Subscription",       "Pay-As-You-Go | Sub ID: d926b212-..."),
        (True,  "Resource Group",            "rg-databricks-poc (UK South)"),
        (True,  "Databricks Workspace",      "dbw-poc-datasharing — Premium SKU"),
        (True,  "ADLS Gen2 Storage",         "stpocadls4417 — raw-data + processed-data containers"),
        (True,  "Data Uploaded",             "69 files (Parquet) uploaded to ADLS"),
        (True,  "Secret Scope",              "poc-secrets — storage key secured"),
        (True,  "Cluster",                   "poc-single-node — Standard_E2s_v3, 10 min auto-terminate"),
        (True,  "Unity Catalog",             "Auto-enabled — data_sharing_poc catalog created"),
        (True,  "Schemas",                   "bronze / silver / gold schemas created"),
        (True,  "Notebooks Deployed",        "9 notebooks uploaded to /POC/ workspace folder"),
        (False, "Pipeline Run on Azure",     "01_generate_data → 05_validate — NEXT STEP"),
        (False, "Tables in Unity Catalog",   "Register Delta tables after pipeline run"),
        (False, "Real Delta Sharing",        "Phase 8 — Unity Catalog sharing setup"),
        (False, "Databricks Workflows",      "Phase 9 — scheduled pipeline"),
        (False, "Azure Functions ChatOps",   "Phase 10 — permanent webhook (no ngrok)"),
    ]

    col_w = Inches(5.8)
    top   = Inches(1.65)
    gap   = Inches(0.355)

    for i, (done, label, detail) in enumerate(items):
        col = i // 8
        row = i  % 8
        x   = Inches(0.3) + col * (col_w + Inches(0.9))
        y   = top + row * gap

        color  = GREEN if done else ORANGE
        symbol = "✔" if done else "○"
        rect(s, x, y, Inches(0.32), Inches(0.3), fill_color=color)
        txt(s, symbol, x, y, Inches(0.32), Inches(0.3),
            font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s, label, x + Inches(0.38), y, Inches(2.1), Inches(0.3),
            font_size=12, bold=True, color=DARK_GRAY if done else ORANGE)
        txt(s, detail, x + Inches(2.55), y, Inches(3.2), Inches(0.3),
            font_size=10, color=MID_GRAY)


def slide_12_achievements(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "Key Achievements", "What makes this POC stand out")
    footer(s, 12)

    achievements = [
        (ACCENT, "Zero-Cost Development",
         "$0 spent during entire Part 1. Full platform validated before any Azure spend."),
        (GREEN,  "Live End-to-End Automation",
         "WhatsApp message triggers Claude AI which controls the pipeline. Tested live on 2026-03-20."),
        (BLUE,   "Production-Grade Architecture",
         "Medallion pattern, Delta Lake ACID, Unity Catalog governance — same as enterprise deployments."),
        (ORANGE, "Mixed Data Sources",
         "Time series (Parquet) + SQL database (SQLite→Azure SQL) + files — realistic real-world setup."),
        (ACCENT, "Same Code — Two Environments",
         "Only 3 lines change between local and Azure. No rewrite. No rework. Proven migration path."),
        (GREEN,  "Full Documentation",
         "Word guide, PowerPoint, interactive HTML flow diagram, conversation log — all auto-generated."),
    ]

    bw = Inches(3.8)
    bh = Inches(1.9)

    for i, (color, title, desc) in enumerate(achievements):
        col = i % 3
        row = i // 3
        x   = Inches(0.3) + col * (bw + Inches(0.43))
        y   = Inches(1.65) + row * (bh + Inches(0.2))

        rect(s, x, y, bw, bh, fill_color=DARK_GRAY)
        rect(s, x, y, bw, Pt(5), fill_color=color)
        rect(s, x, y, Pt(5), bh, fill_color=color)

        txt(s, title, x + Inches(0.15), y + Inches(0.12), bw - Inches(0.2), Inches(0.45),
            font_size=15, bold=True, color=color)
        txt(s, desc,  x + Inches(0.15), y + Inches(0.62), bw - Inches(0.2), Inches(1.1),
            font_size=12, color=LIGHT_GRAY)


def slide_13_next(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "What's Next", "Remaining phases — Azure pipeline to production-ready")
    footer(s, 13)

    phases = [
        ("THIS WEEK",  ACCENT,  [
            ("Run Azure pipeline",       "01_generate_data → 05_validate on cloud cluster"),
            ("Register Unity Catalog",   "Register all Delta tables in data_sharing_poc catalog"),
        ]),
        ("PHASE 8",    BLUE,    [
            ("Real Delta Sharing",       "Unity Catalog shares — Utilitics → Vendor (read-only protocol)"),
            ("Vendor write-back",        "Separate share or REST API for vendor → Utilitics responses"),
        ]),
        ("PHASE 9",    GREEN,   [
            ("Databricks Workflows",     "Scheduled DAG replacing manual notebook runs"),
            ("Alerting",                 "Email/WhatsApp on failure, Azure Monitor integration"),
        ]),
        ("PHASE 10",   ORANGE,  [
            ("Azure Functions webhook",  "Permanent ChatOps endpoint — no more ngrok"),
            ("Azure SQL migration",      "Replace SQLite with Azure SQL (one connection string change)"),
        ]),
    ]

    bw = Inches(2.9)
    bh = Inches(4.8)

    for i, (phase, color, tasks) in enumerate(phases):
        x = Inches(0.3) + i * (bw + Inches(0.35))
        y = Inches(1.65)

        rect(s, x, y, bw, bh, fill_color=WHITE)
        rect(s, x, y, bw, Pt(5), fill_color=color)

        # Phase badge
        rect(s, x, y, bw, Inches(0.45), fill_color=color)
        txt(s, phase, x, y, bw, Inches(0.45),
            font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

        top_t = y + Inches(0.55)
        for task, detail in tasks:
            rect(s, x + Inches(0.15), top_t, Inches(0.06), Inches(0.3), fill_color=color)
            txt(s, task, x + Inches(0.3), top_t, bw - Inches(0.4), Inches(0.32),
                font_size=13, bold=True, color=DARK_GRAY)
            txt(s, detail, x + Inches(0.3), top_t + Inches(0.33), bw - Inches(0.4), Inches(0.8),
                font_size=11, color=MID_GRAY)
            top_t += Inches(1.3)


def slide_14_value(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "Business Value", "What this platform delivers when complete")
    footer(s, 14)

    values = [
        ("Cost Efficiency",    ACCENT,
         "~$5-8/month on Azure vs enterprise alternatives at $500+/month.\nFull Premium Databricks features at minimal cost."),
        ("Data Governance",    GREEN,
         "Unity Catalog provides centralised access control, lineage tracking,\nand auditable data sharing — meets compliance requirements."),
        ("Vendor Data Sharing", BLUE,
         "Delta Sharing protocol allows external vendors to access\nGold data securely without copying or exposing raw data."),
        ("Operational Control", ORANGE,
         "Pipeline controllable via WhatsApp from anywhere.\nClaude AI interprets natural language commands — no CLI needed."),
        ("Scalability",        ACCENT,
         "From 266K records (POC) to millions — same architecture.\nAdd more data sources by adding one notebook."),
        ("Team Enablement",    GREEN,
         "Full documentation, conversation log, and guides created.\nAny team member can pick up, understand, and extend the work."),
    ]

    bw = Inches(3.8)
    bh = Inches(1.85)

    for i, (title, color, desc) in enumerate(values):
        col = i % 3
        row = i // 3
        x   = Inches(0.3) + col * (bw + Inches(0.43))
        y   = Inches(1.65) + row * (bh + Inches(0.2))

        rect(s, x, y, bw, bh, fill_color=DARK_GRAY)
        rect(s, x, y, bw, Pt(5), fill_color=color)

        txt(s, title, x + Inches(0.15), y + Inches(0.1), bw - Inches(0.2), Inches(0.4),
            font_size=15, bold=True, color=color)
        txt(s, desc, x + Inches(0.15), y + Inches(0.58), bw - Inches(0.2), Inches(1.1),
            font_size=11, color=LIGHT_GRAY)


def slide_15_thankyou(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    rect(s, 0, 0, Inches(0.18), SLIDE_H, fill_color=ACCENT)
    rect(s, 0, Inches(6.8), SLIDE_W, Pt(4), fill_color=ACCENT)

    txt(s, "Thank You", Inches(0.5), Inches(1.0), Inches(8), Inches(1.5),
        font_size=52, bold=True, color=WHITE)

    rect(s, Inches(0.5), Inches(2.5), Inches(4), Pt(3), fill_color=ACCENT)

    txt(s, "Questions & Discussion", Inches(0.5), Inches(2.7), Inches(8), Inches(0.6),
        font_size=22, color=ACCENT, italic=True)

    contact = [
        ("Presenter",  "Radhakrishnan Karnakumar"),
        ("Workspace",  "https://adb-7405604806384457.17.azuredatabricks.net"),
        ("Repo",       "C:/Projects/databricks-poc"),
        ("Docs",       "docs/Utilitics_Implementation_Guide.docx"),
    ]
    top_c = Inches(3.5)
    for label, value in contact:
        txt(s, f"{label}:", Inches(0.5), top_c, Inches(1.8), Inches(0.38),
            font_size=13, color=MID_GRAY, bold=True)
        txt(s, value, Inches(2.3), top_c, Inches(8), Inches(0.38),
            font_size=13, color=WHITE)
        top_c += Inches(0.45)

    # Right side summary stats
    rect(s, Inches(9.8), Inches(1.5), Inches(3.2), Inches(5.0), fill_color=DARK_GRAY)
    rect(s, Inches(9.8), Inches(1.5), Inches(3.2), Pt(4), fill_color=ACCENT)
    txt(s, "POC IN NUMBERS", Inches(9.8), Inches(1.58), Inches(3.2), Inches(0.4),
        font_size=12, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    footer(s, 15)

    numbers = [
        ("266,000", "records generated"),
        ("19 / 19",  "quality checks pass"),
        ("10",       "Azure components"),
        ("9",        "notebooks deployed"),
        ("6",        "Claude AI tools"),
        ("$0",       "local dev cost"),
        ("~$5-8",    "per month on Azure"),
    ]
    top_n = Inches(2.1)
    for num, lbl in numbers:
        txt(s, num, Inches(9.9), top_n, Inches(1.1), Inches(0.38),
            font_size=14, bold=True, color=ACCENT, align=PP_ALIGN.RIGHT)
        txt(s, lbl, Inches(11.1), top_n, Inches(1.8), Inches(0.38),
            font_size=12, color=WHITE)
        top_n += Inches(0.42)


# ─── New Databricks Slides ────────────────────────────────────────────────────

def slide_05_what_is_databricks(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "What is Databricks?", "Founded 2013 by creators of Apache Spark (UC Berkeley)")
    footer(s, 5)

    # Left — simple explanation
    rect(s, Inches(0.3), Inches(1.6), Inches(5.8), Inches(5.1), fill_color=WHITE)
    rect(s, Inches(0.3), Inches(1.6), Inches(5.8), Pt(4), fill_color=BLUE)
    txt(s, "In Simple Terms", Inches(0.5), Inches(1.72), Inches(5.4), Inches(0.4),
        font_size=15, bold=True, color=BLUE)

    simple = [
        ("Think of it as...", True, DARK_GRAY),
        ("Excel for millions of rows — running in the cloud,", False, DARK_GRAY),
        ("processing data 100x faster than traditional tools,", False, DARK_GRAY),
        ("with AI, governance, and sharing built in.", False, DARK_GRAY),
        ("", False, WHITE),
        ("What it replaces...", True, DARK_GRAY),
        ("Multiple tools: ETL tools + data warehouses +", False, DARK_GRAY),
        ("ML platforms + data catalogues + file storage =", False, DARK_GRAY),
        ("all unified in one platform.", False, DARK_GRAY),
        ("", False, WHITE),
        ("Who uses it...", True, DARK_GRAY),
        ("NHS, Shell, National Grid, HSBC, BT,", False, DARK_GRAY),
        ("Netflix, Uber, Airbnb — and now Utilitics.", False, DARK_GRAY),
    ]
    txt_box(s, simple, Inches(0.5), Inches(2.2), Inches(5.4), Inches(4.2),
            font_size=12, color=DARK_GRAY)

    # Right — platform stack visual
    rect(s, Inches(6.4), Inches(1.6), Inches(6.6), Inches(5.1), fill_color=NAVY)
    rect(s, Inches(6.4), Inches(1.6), Inches(6.6), Pt(4), fill_color=ACCENT)
    txt(s, "The Platform Stack", Inches(6.6), Inches(1.72), Inches(6.2), Inches(0.4),
        font_size=15, bold=True, color=ACCENT)

    layers = [
        (RGBColor(0x6E,0x40,0xC9), "DATABRICKS WORKFLOWS",    "Schedule & automate pipelines"),
        (RGBColor(0x00,0x70,0xC0), "UNITY CATALOG",           "Governance · Lineage · Delta Sharing"),
        (RGBColor(0x1A,0xBC,0x9C), "DELTA LAKE",              "ACID storage · Time Travel · Schema"),
        (RGBColor(0x00,0xAE,0xEF), "APACHE SPARK",            "Distributed compute — Python/SQL/Scala"),
        (RGBColor(0x1B,0x4F,0x72), "CLOUD STORAGE",           "ADLS Gen2 / S3 / GCS underneath"),
    ]
    top_l = Inches(2.2)
    for color, label, desc in layers:
        rect(s, Inches(6.6), top_l, Inches(6.0), Inches(0.72), fill_color=color)
        txt(s, label, Inches(6.75), top_l + Inches(0.04), Inches(3.5), Inches(0.35),
            font_size=12, bold=True, color=WHITE)
        txt(s, desc,  Inches(6.75), top_l + Inches(0.38), Inches(5.6), Inches(0.3),
            font_size=10, color=LIGHT_GRAY)
        top_l += Inches(0.8)

    txt(s, "Each layer builds on the one below it",
        Inches(6.6), Inches(6.28), Inches(6.0), Inches(0.3),
        font_size=10, color=MID_GRAY, italic=True)


def slide_06_databricks_features(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Databricks Key Features", "Why it's the industry standard for data engineering")
    footer(s, 6)

    features = [
        (ACCENT, "Apache Spark Engine",
         "Processes data across many machines in parallel.\n100x faster than traditional tools.\nSame Python code — 1 machine or 1,000 machines."),
        (GREEN, "Delta Lake Storage",
         "ACID transactions — no corrupt data ever.\nTime Travel — query data as it was yesterday.\nSchema enforcement — bad data rejected at entry."),
        (BLUE, "Medallion Architecture",
         "Bronze (raw) → Silver (clean) → Gold (business).\nIndustry standard pattern — what we built.\nEach layer adds quality and business value."),
        (RGBColor(0x6E,0x40,0xC9), "Unity Catalog",
         "One place to control who sees what data.\nTracks every read/write — full audit trail.\nRequired for compliance and governance."),
        (ORANGE, "Delta Sharing",
         "Share Gold tables with vendors securely.\nOpen protocol — vendor needs no Databricks licence.\nRead-only — no raw data ever exposed."),
        (RGBColor(0xC0,0x39,0x2B), "Databricks Workflows",
         "Schedule pipelines: daily, hourly, on-trigger.\nRetry logic + alerting built in.\nReplaces manual notebook runs — our Phase 9."),
    ]

    bw = Inches(3.8)
    bh = Inches(2.1)
    for i, (color, title, desc) in enumerate(features):
        col = i % 3
        row = i // 3
        x   = Inches(0.3) + col * (bw + Inches(0.43))
        y   = Inches(1.65) + row * (bh + Inches(0.15))

        rect(s, x, y, bw, bh, fill_color=WHITE)
        rect(s, x, y, bw, Pt(5), fill_color=color)
        rect(s, x, y, Pt(5), bh, fill_color=color)

        txt(s, title, x + Inches(0.15), y + Inches(0.1), bw - Inches(0.25), Inches(0.38),
            font_size=14, bold=True, color=color)
        txt(s, desc,  x + Inches(0.15), y + Inches(0.55), bw - Inches(0.25), Inches(1.4),
            font_size=11, color=DARK_GRAY)


def slide_07_why_azure_databricks(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "Why Azure Databricks?", "Joint product — Microsoft + Databricks. Best of both worlds.")
    footer(s, 7)

    # Left — vs alternatives table
    rect(s, Inches(0.3), Inches(1.6), Inches(6.1), Inches(5.1), fill_color=DARK_GRAY)
    rect(s, Inches(0.3), Inches(1.6), Inches(6.1), Pt(4), fill_color=ACCENT)
    txt(s, "Azure Databricks vs Alternatives", Inches(0.5), Inches(1.72),
        Inches(5.7), Inches(0.4), font_size=14, bold=True, color=ACCENT)

    headers = ["", "Azure\nDatabricks", "SQL\nServer", "Self-managed\nSpark", "Azure\nSynapse"]
    col_x   = [Inches(0.35), Inches(2.05), Inches(3.15), Inches(4.2), Inches(5.25)]
    col_w   = [Inches(1.65), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0)]

    for i, (h, x, w) in enumerate(zip(headers, col_x, col_w)):
        txt(s, h, x, Inches(2.12), w, Inches(0.45),
            font_size=9, bold=True,
            color=ACCENT if i == 0 else (GREEN if i == 1 else MID_GRAY),
            align=PP_ALIGN.CENTER)

    rows = [
        ("Setup time",         "5 min",  "1 day",  "1 week", "1 day"),
        ("Scale to billions",  "Yes",    "No",     "Yes",    "Yes"),
        ("Delta Lake native",  "Yes",    "No",     "Manual", "Partial"),
        ("Unity Catalog",      "Yes",    "No",     "No",     "No"),
        ("Delta Sharing",      "Yes",    "No",     "No",     "No"),
        ("AI/ML built-in",     "Yes",    "No",     "No",     "Partial"),
        ("Cost (our POC)",     "£5-8/m", "£50+/m", "£100+", "£20+/m"),
        ("Azure AD integration","Native","No",     "Manual", "Native"),
    ]

    top_r = Inches(2.65)
    for ri, (label, *vals) in enumerate(rows):
        bg = RGBColor(0x2C,0x3E,0x50) if ri % 2 == 0 else DARK_GRAY
        rect(s, Inches(0.35), top_r, Inches(5.95), Inches(0.34), fill_color=bg)
        txt(s, label, Inches(0.4), top_r, Inches(1.6), Inches(0.34),
            font_size=10, color=LIGHT_GRAY)
        for i, val in enumerate(vals):
            col = GREEN if val in ("Yes", "Native", "£5-8/m", "5 min") else (
                  RGBColor(0xC0,0x39,0x2B) if val in ("No", "Manual") else MID_GRAY)
            txt(s, val, col_x[i+1], top_r, col_w[i+1], Inches(0.34),
                font_size=9, bold=(i == 0), color=col, align=PP_ALIGN.CENTER)
        top_r += Inches(0.36)

    # Right — Azure integrations
    rect(s, Inches(6.7), Inches(1.6), Inches(6.3), Inches(5.1), fill_color=DARK_GRAY)
    rect(s, Inches(6.7), Inches(1.6), Inches(6.3), Pt(4), fill_color=GREEN)
    txt(s, "Azure Integrations We Use", Inches(6.9), Inches(1.72),
        Inches(5.9), Inches(0.4), font_size=14, bold=True, color=GREEN)

    integrations = [
        (GREEN,  "ADLS Gen2",           "Our data lake — raw-data + processed-data containers"),
        (ACCENT, "Secret Scope",        "poc-secrets — storage keys never hardcoded"),
        (BLUE,   "Azure Active Directory","Workspace login — your Azure account"),
        (ORANGE, "Azure Monitor",       "Budget alerts — ceiling set at $25/month"),
        (GREEN,  "Unity Catalog",       "data_sharing_poc + bronze/silver/gold schemas"),
        (RGBColor(0x6E,0x40,0xC9), "Azure Functions","Phase 10 — permanent ChatOps webhook"),
        (ACCENT, "Azure SQL",           "Phase 10 — replaces SQLite for snapshot data"),
    ]
    top_i = Inches(2.2)
    for color, label, detail in integrations:
        rect(s, Inches(6.9), top_i, Inches(0.06), Inches(0.28), fill_color=color)
        txt(s, label,  Inches(7.05), top_i,               Inches(1.8), Inches(0.28),
            font_size=11, bold=True, color=color)
        txt(s, detail, Inches(8.9),  top_i,               Inches(3.9), Inches(0.28),
            font_size=10, color=LIGHT_GRAY)
        top_i += Inches(0.42)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    prs = new_prs()

    print("Building presentation...")
    slide_01_title(prs)                 ; print("  Slide  1 — Title")
    slide_02_agenda(prs)                ; print("  Slide  2 — Agenda")
    slide_03_requirement(prs)           ; print("  Slide  3 — Business Requirement")
    slide_04_approach(prs)              ; print("  Slide  4 — Our Approach")
    slide_05_what_is_databricks(prs)    ; print("  Slide  5 — What is Databricks?")
    slide_06_databricks_features(prs)   ; print("  Slide  6 — Databricks Key Features")
    slide_07_why_azure_databricks(prs)  ; print("  Slide  7 — Why Azure Databricks?")
    slide_08_architecture(prs)          ; print("  Slide  8 — Solution Architecture")
    slide_09_techstack(prs)             ; print("  Slide  9 — Tech Stack")
    slide_10_part1(prs)                 ; print("  Slide 10 — Part 1 Complete")
    slide_11_part2(prs)                 ; print("  Slide 11 — Part 2 Progress")
    slide_12_achievements(prs)          ; print("  Slide 12 — Achievements")
    slide_13_next(prs)                  ; print("  Slide 13 — What's Next")
    slide_14_value(prs)                 ; print("  Slide 14 — Business Value")
    slide_15_thankyou(prs)              ; print("  Slide 15 — Thank You")

    out = r"C:\Projects\databricks-poc\Utilitics_Platform_Presentation.pptx"
    prs.save(out)
    print(f"\nSaved: {out}")
    print("15 slides — ready for presentation")


if __name__ == "__main__":
    main()
