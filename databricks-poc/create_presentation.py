"""
create_presentation.py
Creates a professional PowerPoint presentation for the Utilitics Azure Databricks
Data Sharing Platform project — suitable for mixed audience (executives + technical team).
9-slide concise version.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import datetime

# ─── Colour Palette ───────────────────────────────────────────────────────────
NAVY        = RGBColor(0x0D, 0x1B, 0x2A)
BLUE        = RGBColor(0x1B, 0x4F, 0x72)
ACCENT      = RGBColor(0x00, 0xAE, 0xEF)
GREEN       = RGBColor(0x1A, 0xBC, 0x9C)
ORANGE      = RGBColor(0xE6, 0x7E, 0x22)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY  = RGBColor(0xF4, 0xF6, 0xF7)
DARK_GRAY   = RGBColor(0x2C, 0x3E, 0x50)
MID_GRAY    = RGBColor(0x7F, 0x8C, 0x8D)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)
TOTAL   = 9

# ─── Helpers ──────────────────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    layout = prs.slide_layouts[6]
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
    run.font.size   = Pt(font_size)
    run.font.bold   = bold
    run.font.color.rgb = color
    run.font.italic = italic
    run.font.name   = "Calibri"
    return txb


def txt_box(slide, lines, left, top, width, height,
            font_size=16, color=DARK_GRAY):
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
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = text
        run.font.size  = Pt(font_size)
        run.font.bold  = bold
        run.font.color.rgb = col
        run.font.name  = "Calibri"
    return txb


def header_bar(slide, title, subtitle=None):
    rect(slide, 0, 0, SLIDE_W, Inches(1.35), fill_color=NAVY)
    rect(slide, 0, Inches(1.35), SLIDE_W, Pt(4), fill_color=ACCENT)
    txt(slide, title, Inches(0.4), Inches(0.18), Inches(12), Inches(0.7),
        font_size=28, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, Inches(0.4), Inches(0.82), Inches(10), Inches(0.45),
            font_size=16, color=ACCENT)


def footer(slide, slide_num):
    rect(slide, 0, Inches(7.1), SLIDE_W, Inches(0.4), fill_color=NAVY)
    txt(slide, "UTILITICS | Azure Databricks Data Sharing Platform | Confidential",
        Inches(0.3), Inches(7.12), Inches(10), Inches(0.3),
        font_size=9, color=MID_GRAY)
    txt(slide, f"{slide_num} / {TOTAL}",
        Inches(12.5), Inches(7.12), Inches(0.7), Inches(0.3),
        font_size=9, color=MID_GRAY, align=PP_ALIGN.RIGHT)


def stat_box(slide, left, top, width, height, number, label, color=ACCENT):
    rect(slide, left, top, width, height, fill_color=NAVY)
    rect(slide, left, top, width, Pt(4), fill_color=color)
    txt(slide, number, left, top + Inches(0.15), width, Inches(0.7),
        font_size=32, bold=True, color=color, align=PP_ALIGN.CENTER)
    txt(slide, label, left, top + Inches(0.75), width, Inches(0.5),
        font_size=11, color=WHITE, align=PP_ALIGN.CENTER)


def _check(s, x, y, label, done=True, detail=""):
    color  = GREEN if done else ORANGE
    symbol = "+" if done else "o"
    rect(s, x, y, Inches(0.28), Inches(0.26), fill_color=color)
    txt(s, symbol, x, y, Inches(0.28), Inches(0.26),
        font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, label, x + Inches(0.33), y, Inches(2.7), Inches(0.26),
        font_size=11, bold=done, color=DARK_GRAY if done else ORANGE)
    if detail:
        txt(s, detail, x + Inches(3.1), y, Inches(2.8), Inches(0.26),
            font_size=9, color=MID_GRAY)


# ─── Slide 1: Title ───────────────────────────────────────────────────────────

def slide_01_title(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    rect(s, 0, 0, Inches(0.18), SLIDE_H, fill_color=ACCENT)
    rect(s, 0, Inches(6.8), SLIDE_W, Pt(4), fill_color=ACCENT)

    txt(s, "UTILITICS", Inches(0.4), Inches(0.4), Inches(5), Inches(0.5),
        font_size=13, bold=True, color=ACCENT)
    txt(s, "Azure Databricks\nData Sharing Platform",
        Inches(0.4), Inches(1.2), Inches(9), Inches(2.2),
        font_size=44, bold=True, color=WHITE)
    txt(s, "Proof of Concept — Progress & Roadmap Presentation",
        Inches(0.4), Inches(3.3), Inches(9), Inches(0.6),
        font_size=20, color=ACCENT, italic=True)
    rect(s, Inches(0.4), Inches(4.0), Inches(4), Pt(2), fill_color=ACCENT)
    txt(s, "Presented by:  Radhakrishnan Karnakumar",
        Inches(0.4), Inches(4.2), Inches(8), Inches(0.4),
        font_size=14, color=WHITE)
    txt(s, "Date:  April 2026",
        Inches(0.4), Inches(4.65), Inches(8), Inches(0.4),
        font_size=14, color=MID_GRAY)
    txt(s, "Audience:  Executive Leadership + Technical Team",
        Inches(0.4), Inches(5.1), Inches(8), Inches(0.4),
        font_size=14, color=MID_GRAY)

    rect(s, Inches(10.5), Inches(1.5), Inches(2.5), Inches(4.5), fill_color=BLUE)
    txt(s, "POC\nSTATUS", Inches(10.5), Inches(2.2), Inches(2.5), Inches(1.2),
        font_size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    rect(s, Inches(10.7), Inches(3.5), Inches(2.1), Pt(2), fill_color=ACCENT)
    txt(s, "Part 1\nComplete", Inches(10.5), Inches(3.6), Inches(2.5), Inches(0.8),
        font_size=14, color=GREEN, bold=True, align=PP_ALIGN.CENTER)
    txt(s, "Part 2\nIn Progress", Inches(10.5), Inches(4.4), Inches(2.5), Inches(0.8),
        font_size=14, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)


# ─── Slide 2: Business Requirement & Approach ─────────────────────────────────

def slide_02_requirement_approach(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Business Requirement & Approach",
               "What was asked — and how we tackled it")
    footer(s, 2)

    # LEFT panel
    rect(s, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.65), fill_color=WHITE)
    rect(s, Inches(0.3), Inches(1.5), Inches(6.0), Pt(4), fill_color=BLUE)
    txt(s, "What Was Asked", Inches(0.5), Inches(1.58),
        Inches(5.6), Inches(0.38), font_size=14, bold=True, color=BLUE)

    asks = [
        ("Build a Data Sharing Platform on Azure Databricks",       True),
        ("Handle 3 types of real energy data from Utilitics:",      True),
        ("  Time Series  — 168K meter readings  (CSV file drops)",  False),
        ("  Snapshot     — 14K network assets   (SQLite database)", False),
        ("  File Data    — 84K demand forecasts (Parquet files)",   False),
        ("Medallion architecture: Bronze -> Silver -> Gold",        True),
        ("Secure Delta Sharing with external vendors (read-only)",  True),
        ("Pipeline automation & monitoring (ChatOps via WhatsApp)", True),
        ("Budget: under $25 / month on Azure",                      True),
    ]
    ty = Inches(2.05)
    for text, bold in asks:
        txt(s, text, Inches(0.5), ty, Inches(5.6), Inches(0.32),
            font_size=11, bold=bold, color=DARK_GRAY if bold else BLUE)
        ty += Inches(0.33)

    rect(s, Inches(0.3), Inches(5.25), Inches(6.0), Pt(2), fill_color=BLUE)
    txt(s, "Success Criteria", Inches(0.5), Inches(5.3),
        Inches(5.5), Inches(0.3), font_size=12, bold=True, color=BLUE)
    criteria = [
        ("Full pipeline end-to-end",           True),
        ("19/19 quality checks pass",          True),
        ("Delta Sharing: Utilitics -> Vendor", True),
        ("Pipeline via WhatsApp (live tested)", True),
        ("Azure cloud run",                    False),
        ("Workflows scheduling",               False),
    ]
    cx, cy = Inches(0.5), Inches(5.68)
    for i, (label, done) in enumerate(criteria):
        col = GREEN if done else ORANGE
        sym = "+" if done else "o"
        x = cx + (i % 2) * Inches(3.0)
        y = cy + (i // 2) * Inches(0.3)
        txt(s, f"{sym} {label}", x, y, Inches(2.8), Inches(0.28),
            font_size=10, color=col, bold=done)

    # RIGHT panel
    rect(s, Inches(6.6), Inches(1.5), Inches(6.4), Inches(5.65), fill_color=NAVY)
    rect(s, Inches(6.6), Inches(1.5), Inches(6.4), Pt(4), fill_color=ACCENT)
    txt(s, "Our Approach  —  Local First, Then Azure",
        Inches(6.8), Inches(1.58), Inches(6.0), Inches(0.38),
        font_size=14, bold=True, color=ACCENT)

    rect(s, Inches(6.8), Inches(2.05), Inches(5.9), Inches(1.55), fill_color=DARK_GRAY)
    rect(s, Inches(6.8), Inches(2.05), Inches(5.9), Pt(3), fill_color=GREEN)
    txt(s, "PHASE 1 - Local Development  [DONE]  ($0 cost)",
        Inches(6.95), Inches(2.08), Inches(5.6), Inches(0.3),
        font_size=11, bold=True, color=GREEN)
    for i, pt in enumerate([
        "  Full pipeline on Windows 11 laptop - PySpark + Delta Lake",
        "  Same code as cloud - validated before any Azure spend",
        "  ChatOps live: WhatsApp -> Claude AI -> pipeline control",
        "  CI/CD: GitHub Actions + nightly build + WhatsApp alerts",
    ]):
        txt(s, pt, Inches(6.95), Inches(2.43) + i * Inches(0.27),
            Inches(5.6), Inches(0.26), font_size=10, color=LIGHT_GRAY)

    txt(s, "   Same code - only 3 config path changes",
        Inches(6.8), Inches(3.68), Inches(5.9), Inches(0.32),
        font_size=11, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)

    rect(s, Inches(6.8), Inches(4.05), Inches(5.9), Inches(2.85), fill_color=DARK_GRAY)
    rect(s, Inches(6.8), Inches(4.05), Inches(5.9), Pt(3), fill_color=ORANGE)
    txt(s, "PHASE 2 - Azure Migration  [IN PROGRESS]  (~$5-8/month)",
        Inches(6.95), Inches(4.08), Inches(5.6), Inches(0.3),
        font_size=11, bold=True, color=ORANGE)
    phase2 = [
        ("+ Resource group, ADLS Gen2, Databricks Premium", True),
        ("+ Unity Catalog, secret scope, cluster running",  True),
        ("+ 9 notebooks deployed (abfss:// paths)",         True),
        ("+ CI/CD auto-deploys on every push",              True),
        ("o Run Azure pipeline (01-05) - NEXT STEP",        False),
        ("o Real Delta Sharing via Unity Catalog (Phase 8)",False),
        ("o Databricks Workflows scheduling (Phase 9)",     False),
        ("o Azure Functions ChatOps (Phase 10)",            False),
    ]
    for i, (pt, done) in enumerate(phase2):
        col = GREEN if done else ORANGE
        txt(s, pt, Inches(6.95), Inches(4.45) + i * Inches(0.29),
            Inches(5.6), Inches(0.28), font_size=10, color=col)


# ─── Slide 3: What is Azure Databricks? ──────────────────────────────────────

def slide_03_databricks_overview(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "What is Azure Databricks?",
               "Unified analytics platform — built for big data at cloud scale")
    footer(s, 3)

    # Three concept cards
    cards = [
        (ACCENT,  "Unified Analytics",
         "One platform for data engineering, ML, and BI analytics.",
         ["Apache Spark compute engine", "Delta Lake storage layer",
          "SQL, Python, Scala, R support", "Notebooks + Jobs + Dashboards"]),
        (GREEN,   "Cloud-Native on Azure",
         "Deep Azure integration — secure, scalable, pay-per-use.",
         ["ADLS Gen2 (abfss://) storage", "Azure AD + Unity Catalog security",
          "Auto-scaling clusters", "DevOps & GitHub integration"]),
        (ORANGE,  "Why We Chose It",
         "Best fit for energy data: volume, variety, and sharing.",
         ["Handles TB-scale time-series data", "Delta Sharing: vendor read access",
          "Medallion (Bronze/Silver/Gold)", "Same code local + cloud"]),
    ]
    for i, (color, title, subtitle, bullets) in enumerate(cards):
        x = Inches(0.3) + i * Inches(4.35)
        w = Inches(4.1)
        rect(s, x, Inches(1.55), w, Inches(5.15), fill_color=WHITE)
        rect(s, x, Inches(1.55), w, Pt(5), fill_color=color)
        txt(s, title, x + Inches(0.15), Inches(1.65),
            w - Inches(0.3), Inches(0.4),
            font_size=16, bold=True, color=color)
        txt(s, subtitle, x + Inches(0.15), Inches(2.1),
            w - Inches(0.3), Inches(0.5),
            font_size=11, color=MID_GRAY, italic=True)
        rect(s, x + Inches(0.15), Inches(2.6), w - Inches(0.3), Pt(1),
             fill_color=RGBColor(0xDD, 0xDD, 0xDD))
        for j, bullet in enumerate(bullets):
            txt(s, f"  {bullet}",
                x + Inches(0.15), Inches(2.72) + j * Inches(0.42),
                w - Inches(0.3), Inches(0.38),
                font_size=12, color=DARK_GRAY)

    # Bottom bar: key numbers
    rect(s, 0, Inches(6.8), SLIDE_W, Inches(0.3), fill_color=NAVY)
    facts = [
        ("10,000+", "customers worldwide"),
        ("$43B",    "Databricks valuation"),
        ("Apache Spark", "open-source engine"),
        ("Delta Lake", "ACID transactions on data lake"),
        ("Unity Catalog", "single governance layer"),
    ]
    for i, (num, label) in enumerate(facts):
        x = Inches(0.3) + i * Inches(2.6)
        txt(s, num, x, Inches(6.82), Inches(2.4), Inches(0.25),
            font_size=9, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
        txt(s, label, x, Inches(7.07), Inches(2.4), Inches(0.25),
            font_size=8, color=MID_GRAY, align=PP_ALIGN.CENTER)


# ─── Slide 4: Solution Architecture ──────────────────────────────────────────

def slide_04_architecture(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "Solution Architecture",
               "End-to-end data flow: Sources -> Bronze -> Silver -> Gold -> Sharing")
    footer(s, 4)

    # Layer boxes
    layers = [
        (DARK_GRAY, "DATA SOURCES",
         ["CSV (meter readings)", "SQLite (network assets)", "Parquet (ERM forecasts)"]),
        (RGBColor(0x6E, 0x28, 0x0A), "BRONZE LAYER",
         ["Raw ingestion", "Metadata columns", "Partition by date", "Delta format"]),
        (RGBColor(0x1A, 0x5C, 0x6E), "SILVER LAYER",
         ["Quality checks", "Deduplication", "Type casting", "19 DQ rules"]),
        (RGBColor(0x1A, 0x6E, 0x3C), "GOLD LAYER",
         ["Business aggregates", "Daily meter summary", "Regional demand", "Forecast KPIs"]),
        (BLUE,                        "DELTA SHARING",
         ["Unity Catalog", "Read-only tokens", "Vendor access", "Audit logs"]),
    ]
    for i, (color, title, items) in enumerate(layers):
        x = Inches(0.25) + i * Inches(2.6)
        w = Inches(2.45)
        rect(s, x, Inches(1.55), w, Inches(4.8), fill_color=color)
        rect(s, x, Inches(1.55), w, Pt(4), fill_color=ACCENT)
        txt(s, title, x, Inches(1.6), w, Inches(0.35),
            font_size=11, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
        for j, item in enumerate(items):
            txt(s, f"• {item}", x + Inches(0.1), Inches(2.05) + j * Inches(0.36),
                w - Inches(0.2), Inches(0.32), font_size=10, color=WHITE)
        if i < 4:
            txt(s, "->", x + w, Inches(3.55), Inches(0.15), Inches(0.35),
                font_size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # Automation bar
    rect(s, Inches(0.25), Inches(6.5), Inches(12.8), Inches(0.6), fill_color=DARK_GRAY)
    rect(s, Inches(0.25), Inches(6.5), Inches(12.8), Pt(3), fill_color=ACCENT)
    txt(s, "AUTOMATION  |  ChatOps: WhatsApp -> Twilio -> Claude AI (7 tools) -> Pipeline   "
        "|   CI/CD: GitHub Actions -> Databricks   |   Nightly Build: Task Scheduler 2AM",
        Inches(0.45), Inches(6.52), Inches(12.4), Inches(0.5),
        font_size=10, color=LIGHT_GRAY)

    # Runtime flag note
    txt(s, "MODE flag: local (Windows) -> azure (cloud) — same notebooks, 3 path changes",
        Inches(0.25), Inches(7.1), Inches(12), Inches(0.3),
        font_size=9, color=MID_GRAY, italic=True)


# ─── Slide 5: Data Sources & Medallion Layers ─────────────────────────────────

def slide_05_data_sources(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Data Sources & Medallion Layers",
               "Three source formats ingested, quality-checked, and aggregated")
    footer(s, 5)

    # Source cards (top row)
    sources = [
        (ACCENT, "Time Series",
         "Smart meter half-hourly readings",
         "Format: CSV file drops", "168,000 records", "500 meters x 7 days x 48 readings"),
        (GREEN,  "Snapshot",
         "Daily network asset status capture",
         "Format: SQLite database",  "14,000 records", "2,000 assets x 7 daily snapshots"),
        (ORANGE, "File / Forecast",
         "ERM demand forecast with confidence bands",
         "Format: Parquet columnar", "84,000 records", "500 forecasts x 168 horizon hours"),
    ]
    for i, (color, title, desc, fmt, count, detail) in enumerate(sources):
        x = Inches(0.3) + i * Inches(4.35)
        w = Inches(4.1)
        rect(s, x, Inches(1.5), w, Inches(2.1), fill_color=WHITE)
        rect(s, x, Inches(1.5), w, Pt(5), fill_color=color)
        txt(s, title, x + Inches(0.12), Inches(1.6), w - Inches(0.24), Inches(0.35),
            font_size=14, bold=True, color=color)
        txt(s, desc, x + Inches(0.12), Inches(1.97), w - Inches(0.24), Inches(0.3),
            font_size=10, color=DARK_GRAY)
        txt(s, fmt, x + Inches(0.12), Inches(2.3), w - Inches(0.24), Inches(0.26),
            font_size=10, color=MID_GRAY, italic=True)
        txt(s, count, x + Inches(0.12), Inches(2.6), w - Inches(0.24), Inches(0.3),
            font_size=12, bold=True, color=color)
        txt(s, detail, x + Inches(0.12), Inches(2.92), w - Inches(0.24), Inches(0.26),
            font_size=9, color=MID_GRAY)

    # Medallion section
    txt(s, "Medallion Architecture", Inches(0.3), Inches(3.8), Inches(12), Inches(0.35),
        font_size=14, bold=True, color=DARK_GRAY)
    rect(s, Inches(0.3), Inches(4.15), Inches(12.7), Pt(1),
         fill_color=RGBColor(0xCC, 0xCC, 0xCC))

    medals = [
        (RGBColor(0xCD, 0x7F, 0x32), "BRONZE",
         "Raw ingestion — no transforms",
         ["Append-only Delta tables", "Metadata: source, date, file",
          "Partition by ingestion date", "Preserves raw data forever"]),
        (RGBColor(0xC0, 0xC0, 0xC0), "SILVER",
         "Cleaned & validated",
         ["19 data quality checks", "Dedup, null filter, range checks",
          "Quality flags retained", "Rejects < 20% drop rate"]),
        (RGBColor(0xFF, 0xD7, 0x00), "GOLD",
         "Business-ready aggregates",
         ["Daily meter summary", "Regional demand totals",
          "Network asset health", "Forecast confidence KPIs"]),
    ]
    for i, (color, title, subtitle, items) in enumerate(medals):
        x = Inches(0.3) + i * Inches(4.25)
        w = Inches(4.0)
        rect(s, x, Inches(4.3), w, Inches(2.35), fill_color=DARK_GRAY)
        rect(s, x, Inches(4.3), w, Pt(5), fill_color=color)
        txt(s, title, x + Inches(0.12), Inches(4.35), w - Inches(0.24), Inches(0.32),
            font_size=13, bold=True, color=color)
        txt(s, subtitle, x + Inches(0.12), Inches(4.68), w - Inches(0.24), Inches(0.26),
            font_size=10, color=MID_GRAY, italic=True)
        for j, item in enumerate(items):
            txt(s, f"  {item}", x + Inches(0.12), Inches(4.98) + j * Inches(0.35),
                w - Inches(0.24), Inches(0.31), font_size=10, color=WHITE)


# ─── Slide 6: POC Status & Achievements ──────────────────────────────────────

def slide_06_poc_status(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "POC Status & Key Achievements",
               "Part 1 complete — Part 2 Azure migration in progress")
    footer(s, 6)

    # Stat boxes
    stats = [
        ("266K",  "Total Records\nGenerated",   ACCENT),
        ("19/19", "Quality Checks\nPassed",      GREEN),
        ("9",     "Notebooks\nDeployed",         BLUE),
        ("7",     "ChatOps AI\nTools",           ORANGE),
        ("$0",    "Cloud Cost\nPart 1 (Local)",  GREEN),
    ]
    for i, (num, label, col) in enumerate(stats):
        x = Inches(0.3) + i * Inches(2.55)
        stat_box(s, x, Inches(1.55), Inches(2.35), Inches(1.15), num, label, col)

    # Part 1 achievements
    rect(s, Inches(0.3), Inches(2.9), Inches(6.1), Inches(3.9), fill_color=WHITE)
    rect(s, Inches(0.3), Inches(2.9), Inches(6.1), Pt(4), fill_color=GREEN)
    txt(s, "Part 1 — Local POC  [COMPLETE]", Inches(0.5), Inches(2.94),
        Inches(5.7), Inches(0.36), font_size=13, bold=True, color=GREEN)

    done_items = [
        ("Data generation",         "168K + 14K + 84K records, 3 formats"),
        ("Bronze ingestion",        "CSV, SQLite, Parquet -> Delta Lake"),
        ("Silver quality checks",   "19 DQ rules, dedup, null filter"),
        ("Gold aggregations",       "4 gold tables: meter, demand, assets, forecast"),
        ("Delta Sharing",           "Vendor token, profile JSON, read-only"),
        ("ChatOps (WhatsApp)",      "7 tools: run, status, quality, logs, CI..."),
        ("CI/CD pipeline",          "GitHub Actions -> Databricks auto-deploy"),
        ("Nightly build",           "Windows Task Scheduler 2AM + WhatsApp alert"),
        ("Full pipeline run",       "234.5 sec, ALL STEPS PASSED on laptop"),
    ]
    for i, (label, detail) in enumerate(done_items):
        y = Inches(3.4) + i * Inches(0.36)
        txt(s, "+", Inches(0.45), y, Inches(0.25), Inches(0.28),
            font_size=10, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER)
        rect(s, Inches(0.45), y + Inches(0.02), Inches(0.22), Inches(0.24),
             fill_color=GREEN)
        txt(s, "+", Inches(0.45), y + Inches(0.02), Inches(0.22), Inches(0.24),
            font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s, label, Inches(0.75), y, Inches(2.3), Inches(0.28),
            font_size=11, bold=True, color=DARK_GRAY)
        txt(s, detail, Inches(3.1), y, Inches(3.1), Inches(0.28),
            font_size=9, color=MID_GRAY)

    # Part 2 status
    rect(s, Inches(6.6), Inches(2.9), Inches(6.4), Inches(3.9), fill_color=NAVY)
    rect(s, Inches(6.6), Inches(2.9), Inches(6.4), Pt(4), fill_color=ORANGE)
    txt(s, "Part 2 — Azure Migration  [IN PROGRESS]", Inches(6.8), Inches(2.94),
        Inches(6.0), Inches(0.36), font_size=13, bold=True, color=ORANGE)

    progress = [
        (True,  "Resource group + ADLS Gen2 provisioned"),
        (True,  "Databricks Premium + Unity Catalog enabled"),
        (True,  "Cluster running (Standard_DS3_v2)"),
        (True,  "9 notebooks uploaded via CI/CD"),
        (True,  "abfss:// paths configured in config"),
        (True,  "Secret scope for credentials"),
        (False, "Run full pipeline 01->05 on Databricks"),
        (False, "Register Delta tables in Unity Catalog"),
        (False, "Real Delta Sharing (Phase 8)"),
        (False, "Databricks Workflows scheduling (Phase 9)"),
        (False, "Azure Functions for permanent ChatOps (Phase 10)"),
    ]
    for i, (done, label) in enumerate(progress):
        color = GREEN if done else ORANGE
        sym = "+" if done else "o"
        y = Inches(3.4) + i * Inches(0.33)
        rect(s, Inches(6.75), y + Inches(0.02), Inches(0.22), Inches(0.24),
             fill_color=color)
        txt(s, sym, Inches(6.75), y + Inches(0.02), Inches(0.22), Inches(0.24),
            font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s, label, Inches(7.05), y, Inches(5.7), Inches(0.28),
            font_size=10, color=WHITE if done else ORANGE, bold=done)


# ─── Slide 7: ChatOps & CI/CD ─────────────────────────────────────────────────

def slide_07_chatops_cicd(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    header_bar(s, "ChatOps & CI/CD — Pipeline Automation",
               "Control the entire pipeline from WhatsApp — and deploy code via GitHub")
    footer(s, 7)

    # ChatOps flow (left)
    rect(s, Inches(0.3), Inches(1.55), Inches(6.2), Inches(5.1), fill_color=DARK_GRAY)
    rect(s, Inches(0.3), Inches(1.55), Inches(6.2), Pt(4), fill_color=ACCENT)
    txt(s, "ChatOps — WhatsApp Pipeline Control",
        Inches(0.5), Inches(1.6), Inches(5.8), Inches(0.36),
        font_size=13, bold=True, color=ACCENT)

    flow = [
        (ACCENT, "WhatsApp Message",     "User sends: 'run pipeline'"),
        (BLUE,   "Twilio Webhook",       "Routes message to FastAPI server"),
        (BLUE,   "ngrok Tunnel",         "Exposes localhost:8000 to internet"),
        (ORANGE, "FastAPI Server",       "automation/chatops_server.py"),
        (GREEN,  "Claude AI (7 tools)",  "Interprets intent, calls tools"),
        (GREEN,  "Pipeline / CI / Logs", "Executes action, returns result"),
    ]
    for i, (color, step, detail) in enumerate(flow):
        y = Inches(2.1) + i * Inches(0.62)
        rect(s, Inches(0.5), y, Inches(5.8), Inches(0.5), fill_color=color)
        txt(s, step, Inches(0.6), y + Inches(0.04), Inches(2.2), Inches(0.38),
            font_size=11, bold=True, color=WHITE)
        txt(s, detail, Inches(2.9), y + Inches(0.04), Inches(3.3), Inches(0.38),
            font_size=10, color=WHITE)
        if i < 5:
            txt(s, "  |", Inches(1.3), y + Inches(0.5), Inches(0.4), Inches(0.18),
                font_size=10, color=ACCENT)

    # 7 tools
    tools = [
        "run_pipeline", "get_status", "get_quality_report",
        "get_logs", "get_pipeline_config", "run_ci", "share_data",
    ]
    txt(s, "7 Available Tools:", Inches(0.5), Inches(5.95), Inches(5.8), Inches(0.28),
        font_size=11, bold=True, color=ACCENT)
    tool_str = "  |  ".join(tools)
    txt(s, tool_str, Inches(0.5), Inches(6.25), Inches(5.8), Inches(0.3),
        font_size=9, color=LIGHT_GRAY)

    # CI/CD flow (right)
    rect(s, Inches(6.8), Inches(1.55), Inches(6.2), Inches(5.1), fill_color=DARK_GRAY)
    rect(s, Inches(6.8), Inches(1.55), Inches(6.2), Pt(4), fill_color=GREEN)
    txt(s, "CI/CD — Automated Code Quality & Deploy",
        Inches(7.0), Inches(1.6), Inches(5.8), Inches(0.36),
        font_size=13, bold=True, color=GREEN)

    ci_steps = [
        (GREEN,  "git push -> main",          "Developer pushes code"),
        (ACCENT, "GitHub Actions (CI)",        ".github/workflows/ci.yml triggers"),
        (ACCENT, "check_syntax.py",            "25 files: syntax + 6 secret patterns"),
        (GREEN,  "CI passes",                  "0 errors, 0 secret leaks"),
        (GREEN,  "GitHub Actions (CD)",        ".github/workflows/cd.yml triggers"),
        (GREEN,  "upload_notebooks.py",        "9 notebooks auto-deployed to Databricks"),
    ]
    for i, (color, step, detail) in enumerate(ci_steps):
        y = Inches(2.1) + i * Inches(0.62)
        rect(s, Inches(7.0), y, Inches(5.8), Inches(0.5), fill_color=color)
        txt(s, step, Inches(7.1), y + Inches(0.04), Inches(2.2), Inches(0.38),
            font_size=11, bold=True, color=WHITE)
        txt(s, detail, Inches(9.4), y + Inches(0.04), Inches(3.3), Inches(0.38),
            font_size=10, color=WHITE)
        if i < 5:
            txt(s, "  |", Inches(7.9), y + Inches(0.5), Inches(0.4), Inches(0.18),
                font_size=10, color=GREEN)

    rect(s, Inches(7.0), Inches(5.95), Inches(5.8), Inches(0.55), fill_color=BLUE)
    txt(s, "Nightly Build: Windows Task Scheduler @ 2AM  ->  full pipeline  ->  WhatsApp alert",
        Inches(7.1), Inches(6.02), Inches(5.6), Inches(0.4),
        font_size=10, color=WHITE)


# ─── Slide 8: Business Value & Roadmap ────────────────────────────────────────

def slide_08_value_roadmap(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=LIGHT_GRAY)
    header_bar(s, "Business Value & Roadmap",
               "What this delivers — and what comes next")
    footer(s, 8)

    # Value cards (left)
    rect(s, Inches(0.3), Inches(1.55), Inches(6.2), Inches(5.1), fill_color=WHITE)
    rect(s, Inches(0.3), Inches(1.55), Inches(6.2), Pt(4), fill_color=BLUE)
    txt(s, "Business Value Delivered",
        Inches(0.5), Inches(1.6), Inches(5.8), Inches(0.36),
        font_size=14, bold=True, color=BLUE)

    values = [
        (ACCENT, "Zero-Copy Data Sharing",
         "Vendors read Gold data without copy/export. No PII exposure, full audit trail."),
        (GREEN,  "Cost Efficiency",
         "POC at $0 (local). Azure run <$25/month. Scales to TB without RDBMS licensing."),
        (ORANGE, "Pipeline Reliability",
         "19 DQ checks catch bad data before it reaches Gold. Nightly alerts via WhatsApp."),
        (BLUE,   "Developer Velocity",
         "CI/CD auto-deploys on push. Same code local and cloud — no manual notebook uploads."),
        (GREEN,  "Real-Time Control",
         "Operations team controls pipeline from WhatsApp — no VPN, no dashboard login needed."),
    ]
    for i, (color, title, desc) in enumerate(values):
        y = Inches(2.1) + i * Inches(0.85)
        rect(s, Inches(0.5), y, Inches(5.8), Inches(0.75), fill_color=LIGHT_GRAY)
        rect(s, Inches(0.5), y, Pt(5), Inches(0.75), fill_color=color)
        txt(s, title, Inches(0.65), y + Inches(0.04), Inches(5.5), Inches(0.3),
            font_size=12, bold=True, color=color)
        txt(s, desc, Inches(0.65), y + Inches(0.34), Inches(5.5), Inches(0.35),
            font_size=10, color=DARK_GRAY)

    # Roadmap (right)
    rect(s, Inches(6.8), Inches(1.55), Inches(6.2), Inches(5.1), fill_color=NAVY)
    rect(s, Inches(6.8), Inches(1.55), Inches(6.2), Pt(4), fill_color=ACCENT)
    txt(s, "Remaining Roadmap",
        Inches(7.0), Inches(1.6), Inches(5.8), Inches(0.36),
        font_size=14, bold=True, color=ACCENT)

    roadmap = [
        (False, "Phase 7", "Run full pipeline on Azure Databricks",
         "NEXT: Execute 01->05 on cluster — validates cloud config"),
        (False, "Phase 8", "Real Delta Sharing via Unity Catalog",
         "Register Gold tables, issue vendor share tokens"),
        (False, "Phase 9", "Databricks Workflows scheduling",
         "Replace manual runs with cron-scheduled jobs"),
        (False, "Phase 10", "Azure Functions for ChatOps",
         "Permanent webhook (replaces ngrok) — production-ready"),
        (False, "Phase 11", "Power BI / Databricks SQL",
         "Dashboard on Gold layer for business users"),
    ]
    for i, (done, phase, title, detail) in enumerate(roadmap):
        color = GREEN if done else ORANGE
        y = Inches(2.1) + i * Inches(0.88)
        rect(s, Inches(7.0), y, Inches(5.8), Inches(0.78), fill_color=DARK_GRAY)
        rect(s, Inches(7.0), y, Pt(5), Inches(0.78), fill_color=color)
        txt(s, phase, Inches(7.12), y + Inches(0.04), Inches(1.0), Inches(0.28),
            font_size=10, bold=True, color=color)
        txt(s, title, Inches(8.2), y + Inches(0.04), Inches(4.5), Inches(0.3),
            font_size=11, bold=True, color=WHITE)
        txt(s, detail, Inches(7.12), y + Inches(0.38), Inches(5.6), Inches(0.3),
            font_size=10, color=MID_GRAY, italic=True)

    # Budget line
    rect(s, Inches(0.3), Inches(6.7), Inches(12.7), Inches(0.4), fill_color=DARK_GRAY)
    txt(s, "Budget:  Part 1 = $0 (laptop)  |  Part 2 = ~$5-8/month (Azure Premium)  "
        "|  Production estimate = $80-120/month (auto-scale clusters)",
        Inches(0.5), Inches(6.72), Inches(12.3), Inches(0.35),
        font_size=10, color=LIGHT_GRAY)


# ─── Slide 9: Thank You ───────────────────────────────────────────────────────

def slide_09_thankyou(prs):
    s = blank_slide(prs)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, fill_color=NAVY)
    rect(s, 0, 0, Inches(0.18), SLIDE_H, fill_color=ACCENT)
    rect(s, 0, Inches(6.8), SLIDE_W, Pt(4), fill_color=ACCENT)

    txt(s, "Thank You", Inches(0.4), Inches(1.0), Inches(12), Inches(1.5),
        font_size=54, bold=True, color=WHITE)
    txt(s, "Questions & Open Discussion",
        Inches(0.4), Inches(2.4), Inches(12), Inches(0.6),
        font_size=22, color=ACCENT, italic=True)
    rect(s, Inches(0.4), Inches(3.1), Inches(5), Pt(2), fill_color=ACCENT)

    contacts = [
        ("Presenter",     "Radhakrishnan Karnakumar"),
        ("GitHub",        "github.com/RadhaK / databricks-poc"),
        ("ChatOps",       "WhatsApp -> Twilio -> Claude AI"),
        ("Azure Tenant",  "Databricks Premium + Unity Catalog"),
    ]
    for i, (label, value) in enumerate(contacts):
        y = Inches(3.3) + i * Inches(0.5)
        txt(s, label + ":", Inches(0.4), y, Inches(1.8), Inches(0.4),
            font_size=13, color=MID_GRAY)
        txt(s, value, Inches(2.3), y, Inches(6), Inches(0.4),
            font_size=13, color=WHITE, bold=True)

    # Key takeaways box
    rect(s, Inches(8.5), Inches(1.5), Inches(4.5), Inches(5.3), fill_color=DARK_GRAY)
    rect(s, Inches(8.5), Inches(1.5), Inches(4.5), Pt(4), fill_color=GREEN)
    txt(s, "Key Takeaways", Inches(8.65), Inches(1.56),
        Inches(4.2), Inches(0.36), font_size=13, bold=True, color=GREEN)
    takeaways = [
        "Full end-to-end pipeline working",
        "266K records across 3 data formats",
        "19/19 quality checks passing",
        "Live ChatOps via WhatsApp + Claude AI",
        "CI/CD auto-deploys to Databricks",
        "Azure infrastructure provisioned",
        "Ready to run on cloud - next session",
    ]
    for i, t in enumerate(takeaways):
        rect(s, Inches(8.65), Inches(2.08) + i * Inches(0.55),
             Inches(0.22), Inches(0.22), fill_color=GREEN)
        txt(s, "+", Inches(8.65), Inches(2.08) + i * Inches(0.55),
            Inches(0.22), Inches(0.22),
            font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(s, t, Inches(8.95), Inches(2.06) + i * Inches(0.55),
            Inches(3.9), Inches(0.3), font_size=11, color=LIGHT_GRAY)

    txt(s, "UTILITICS | Confidential | April 2026",
        Inches(0.4), Inches(6.85), Inches(10), Inches(0.3),
        font_size=9, color=MID_GRAY)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    prs = new_prs()

    print("Building 9-slide presentation...")
    slide_01_title(prs)
    print("  [1/9] Title slide")
    slide_02_requirement_approach(prs)
    print("  [2/9] Business Requirement & Approach")
    slide_03_databricks_overview(prs)
    print("  [3/9] What is Azure Databricks?")
    slide_04_architecture(prs)
    print("  [4/9] Solution Architecture")
    slide_05_data_sources(prs)
    print("  [5/9] Data Sources & Medallion Layers")
    slide_06_poc_status(prs)
    print("  [6/9] POC Status & Achievements")
    slide_07_chatops_cicd(prs)
    print("  [7/9] ChatOps & CI/CD")
    slide_08_value_roadmap(prs)
    print("  [8/9] Business Value & Roadmap")
    slide_09_thankyou(prs)
    print("  [9/9] Thank You")

    out = "Utilitics_Databricks_POC.pptx"
    prs.save(out)
    print(f"\nSaved: {out}")
    print("Done.")


if __name__ == "__main__":
    main()
