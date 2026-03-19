"""
Creates a single-slide "one pager" PowerPoint for the Utilitics project.
Run: python create_ppt.py
Output: Utilitics_OnePager.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import pptx.oxml.ns as nsmap
from lxml import etree

# ── Slide size: Widescreen 16:9 ──────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

slide_layout = prs.slide_layouts[6]   # blank
slide = prs.slides.add_slide(slide_layout)

# ── Helper colours ────────────────────────────────────────────────────────────
DARK_BG    = RGBColor(0x0F, 0x11, 0x17)
PANEL_BG   = RGBColor(0x0D, 0x19, 0x29)
HEADER_BG  = RGBColor(0x1F, 0x6F, 0xEB)
GREEN      = RGBColor(0x23, 0x86, 0x36)
ORANGE     = RGBColor(0xF7, 0x8C, 0x00)
PURPLE     = RGBColor(0x6E, 0x40, 0xC9)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY = RGBColor(0xC9, 0xD1, 0xD9)
BLUE_TEXT  = RGBColor(0x58, 0xA6, 0xFF)
GREEN_TEXT = RGBColor(0x3F, 0xB9, 0x50)
YELLOW     = RGBColor(0xF7, 0xC9, 0x48)


def rgb(r, g, b):
    return RGBColor(r, g, b)


def add_rect(slide, left, top, width, height, fill_color, alpha=None):
    shape = slide.shapes.add_shape(
        pptx.enum.shapes.MSO_SHAPE_TYPE.AUTO_SHAPE if False else 1,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_text(slide, text, left, top, width, height,
             font_size=10, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_multiline(slide, lines, left, top, width, height,
                  font_size=9, color=LIGHT_GREY, spacing=1.0):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for line_data in lines:
        if isinstance(line_data, str):
            text, fc, bold, italic = line_data, color, False, False
        else:
            text = line_data.get("text", "")
            fc   = line_data.get("color", color)
            bold = line_data.get("bold", False)
            italic = line_data.get("italic", False)

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        run = p.add_run()
        run.text = text
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = fc
    return txBox


# ══════════════════════════════════════════════════════════════════════════════
# BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
add_rect(slide, 0, 0, 13.33, 7.5, DARK_BG)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER BAR
# ══════════════════════════════════════════════════════════════════════════════
add_rect(slide, 0, 0, 13.33, 0.65, HEADER_BG)
add_text(slide, "UTILITICS — Azure Databricks Data Sharing Platform  |  Local POC — End-to-End Architecture",
         0.15, 0.08, 10, 0.5, font_size=14, bold=True, color=WHITE)
add_text(slide, "Status: Part 1 COMPLETE  ✔",
         10.5, 0.08, 2.7, 0.5, font_size=11, bold=True, color=YELLOW, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1  — three panels: Data Sources | Medallion Pipeline | Delta Sharing
# ══════════════════════════════════════════════════════════════════════════════

# ── Panel 1: Data Sources ─────────────────────────────────────────────────────
add_rect(slide, 0.1, 0.75, 3.1, 2.15, PANEL_BG)
add_rect(slide, 0.1, 0.75, 3.1, 0.3, GREEN)
add_text(slide, "① DATA SOURCES", 0.15, 0.77, 3.0, 0.28,
         font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "Time Series (Parquet)", "color": BLUE_TEXT, "bold": True},
    {"text": "  500 meters × 7 days × 48 readings"},
    {"text": "  → 168,000 records  |  lake/raw/timeseries/"},
    {"text": ""},
    {"text": "Network Asset Snapshot (SQLite)", "color": BLUE_TEXT, "bold": True},
    {"text": "  2,000 assets × 7 snapshots"},
    {"text": "  → 14,000 records  |  lake/sources/assets.db"},
    {"text": "  JDBC read in bronze  (org.xerial:sqlite-jdbc)"},
    {"text": ""},
    {"text": "Vendor Forecasts (Parquet)", "color": BLUE_TEXT, "bold": True},
    {"text": "  500 forecasts × 168 hourly points"},
    {"text": "  → 84,000 records  |  lake/raw/files/"},
], 0.15, 1.08, 3.0, 1.75, font_size=8)

# ── Panel 2: Medallion Pipeline ───────────────────────────────────────────────
add_rect(slide, 3.3, 0.75, 5.1, 2.15, PANEL_BG)
add_rect(slide, 3.3, 0.75, 5.1, 0.3, GREEN)
add_text(slide, "② MEDALLION PIPELINE  (PySpark 3.5.1 + Delta Lake 3.1.0)",
         3.35, 0.77, 5.0, 0.28, font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "01  Generate Data", "color": YELLOW, "bold": True},
    {"text": "    Synthetic meter + asset + forecast data  →  266K total records"},
    {"text": "02  Bronze Ingestion", "color": YELLOW, "bold": True},
    {"text": "    Raw → Bronze Delta  |  168K + 14K + 84K  |  Match: 100%"},
    {"text": "03  Silver Transformation", "color": YELLOW, "bold": True},
    {"text": "    Dedup + validation + derived cols  |  Drop rate: 0.0%  PASS"},
    {"text": "04  Gold Aggregation", "color": YELLOW, "bold": True},
    {"text": "    4 Gold tables: daily_meter / regional_demand /"},
    {"text": "    network_assets / forecast_summary  →  6,760 records"},
    {"text": "05  Validation", "color": YELLOW, "bold": True},
    {"text": "    19/19 checks PASS  (Bronze→Silver drop, Gold counts,"},
    {"text": "    quality rules, Delta health, SQLite source checks)"},
    {"text": "    Full run elapsed: ~5 minutes"},
], 3.35, 1.08, 4.95, 1.75, font_size=8)

# ── Panel 3: Delta Sharing ────────────────────────────────────────────────────
add_rect(slide, 8.5, 0.75, 4.73, 2.15, PANEL_BG)
add_rect(slide, 8.5, 0.75, 4.73, 0.3, GREEN)
add_text(slide, "③ DELTA SHARING  (Section 13)",
         8.55, 0.77, 4.6, 0.28, font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "Option A — Python Simulation  ✔", "color": GREEN_TEXT, "bold": True},
    {"text": "  Provider shares 4 Gold tables with Vendor"},
    {"text": "  Vendor receives + analyses regional demand & assets"},
    {"text": "  Bi-directional: 5 forecast responses written back"},
    {"text": "  NORTH region highest peak: 670 kWh"},
    {"text": "  52.8% of assets flagged for maintenance"},
    {"text": ""},
    {"text": "Option B — OSS Delta Sharing Server  (code ready)", "color": BLUE_TEXT, "bold": True},
    {"text": "  Real delta-sharing-server.jar + Python client"},
    {"text": "  server_config.yaml + recipient_profile.json configured"},
    {"text": "  Requires: download JAR → place in delta_sharing/"},
], 8.55, 1.08, 4.6, 1.75, font_size=8)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — three panels: Section 14 Runtime Flag | ChatOps | Tech Stack
# ══════════════════════════════════════════════════════════════════════════════

# ── Panel 4: Section 14 Runtime Flag ─────────────────────────────────────────
add_rect(slide, 0.1, 3.05, 4.05, 2.2, PANEL_BG)
add_rect(slide, 0.1, 3.05, 4.05, 0.3, ORANGE)
add_text(slide, "④ DATABRICKS PORT + RUNTIME FLAG  (Section 14)",
         0.15, 3.07, 3.95, 0.28, font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "run.py  —  Unified Launcher", "color": YELLOW, "bold": True},
    {"text": "  --local   → runs local PySpark via subprocess"},
    {"text": "  --cloud   → submits to Databricks REST API"},
    {"text": "  --config  → shows RUNTIME, token, workspace URL"},
    {"text": "  --status  → checks last Databricks run"},
    {"text": ""},
    {"text": "RUNTIME flag in pipeline_config.py", "color": YELLOW, "bold": True},
    {"text": "  \"local\"      — Windows PySpark (default)"},
    {"text": "  \"databricks\" — Community Edition via REST API"},
    {"text": ""},
    {"text": "notebooks/databricks/  (7 notebooks)", "color": YELLOW, "bold": True},
    {"text": "  DBFS paths  |  dbutils.notebook.run()"},
    {"text": "  dbutils.notebook.exit(\"SUCCESS\"/\"FAILED\")"},
    {"text": "  Snapshot → CSV on DBFS (no SQLite on CE)"},
], 0.15, 3.38, 3.95, 1.8, font_size=8)

# ── Panel 5: ChatOps ──────────────────────────────────────────────────────────
add_rect(slide, 4.25, 3.05, 5.1, 2.2, PANEL_BG)
add_rect(slide, 4.25, 3.05, 5.1, 0.3, ORANGE)
add_text(slide, "⑤ CHATOPS — WhatsApp Pipeline Control  (LIVE ✔)",
         4.3, 3.07, 5.0, 0.28, font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "Flow:  WhatsApp → Twilio → ngrok → FastAPI → Claude AI → Pipeline",
     "color": BLUE_TEXT, "bold": True},
    {"text": ""},
    {"text": "automation/webhook_server.py  (FastAPI)", "color": YELLOW, "bold": True},
    {"text": "  POST /webhook  receives Twilio WhatsApp messages"},
    {"text": "  Agentic loop: Claude calls tools, executes, replies"},
    {"text": ""},
    {"text": "automation/claude_tools.py  (6 tools)", "color": YELLOW, "bold": True},
    {"text": "  run_pipeline   run_step   run_sharing"},
    {"text": "  get_status     get_runtime   set_runtime"},
    {"text": ""},
    {"text": "automation/pipeline_runner.py", "color": YELLOW, "bold": True},
    {"text": "  Subprocess wrapper  |  stdout capture  |  state file"},
    {"text": ""},
    {"text": "Tested live: 'status' + 'Run pipeline' from WhatsApp  ✔",
     "color": GREEN_TEXT, "bold": True},
], 4.3, 3.38, 4.95, 1.8, font_size=8)

# ── Panel 6: Part 2 Azure ─────────────────────────────────────────────────────
add_rect(slide, 9.45, 3.05, 3.78, 2.2, PANEL_BG)
add_rect(slide, 9.45, 3.05, 3.78, 0.3, PURPLE)
add_text(slide, "⑥ PART 2 — AZURE CLOUD  (planned)",
         9.5, 3.07, 3.68, 0.28, font_size=9, bold=True, color=WHITE)

add_multiline(slide, [
    {"text": "Azure Data Lake Storage Gen2", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Replaces lake/ local folder"},
    {"text": "Azure Databricks (paid)", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Full Unity Catalog + Workflows"},
    {"text": "Azure Data Factory", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Replaces run_pipeline.py orchestrator"},
    {"text": "Azure SQL Database", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Replaces SQLite (1 JDBC line change)"},
    {"text": "Azure Functions", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Replaces FastAPI + ngrok"},
    {"text": "Delta Sharing (managed)", "color": rgb(0xBC, 0x8C, 0xFF), "bold": True},
    {"text": "  Real protocol, no simulation needed"},
    {"text": "Same WhatsApp + Claude AI layer  →  no change"},
], 9.5, 3.38, 3.68, 1.8, font_size=8)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — Stats bar + Tech Stack + Key Fixes
# ══════════════════════════════════════════════════════════════════════════════

# Stats strip
add_rect(slide, 0.1, 5.38, 13.13, 0.52, rgb(0x0D, 0x1F, 0x0D))

stats = [
    ("266K",  "Raw Records"),
    ("19/19", "Checks Passed"),
    ("6,760", "Gold Records"),
    ("~5 min","Full Pipeline"),
    ("6",     "Claude Tools"),
    ("3",     "Automation Files"),
    ("14",    "Sections Done"),
    ("✔ LIVE","ChatOps"),
]
col_w = 13.13 / len(stats)
for i, (val, label) in enumerate(stats):
    x = 0.1 + i * col_w
    add_text(slide, val,   x, 5.4,  col_w, 0.25, font_size=12, bold=True,
             color=GREEN_TEXT, align=PP_ALIGN.CENTER)
    add_text(slide, label, x, 5.62, col_w, 0.2,  font_size=7,
             color=LIGHT_GREY, align=PP_ALIGN.CENTER)

# ── Tech stack + key fixes row ────────────────────────────────────────────────
add_rect(slide, 0.1, 6.0, 8.5, 1.38, PANEL_BG)
add_text(slide, "TECH STACK", 0.15, 6.02, 8.4, 0.22,
         font_size=8, bold=True, color=BLUE_TEXT)

tech = [
    "Python 3.11  |  PySpark 3.5.1  |  Delta Lake 3.1.0  |  SQLite + SQLAlchemy  |  sqlite-jdbc 3.44.1.0",
    "FastAPI + Uvicorn  |  Twilio WhatsApp API  |  Anthropic Claude API (tool use)  |  ngrok  |  python-dotenv",
    "Databricks Community Edition  |  DBFS  |  dbutils.notebook.run()  |  REST API 2.1",
    "Windows 11 (24 GB RAM, 1 TB SSD)  |  Java 11  |  Hadoop winutils  |  venv",
]
for i, line in enumerate(tech):
    add_text(slide, line, 0.15, 6.25 + i * 0.27, 8.4, 0.26,
             font_size=7.5, color=LIGHT_GREY)

# Key fixes panel
add_rect(slide, 8.7, 6.0, 4.53, 1.38, PANEL_BG)
add_text(slide, "KEY WINDOWS FIXES", 8.75, 6.02, 4.4, 0.22,
         font_size=8, bold=True, color=ORANGE)

fixes = [
    "PYSPARK_PYTHON = sys.executable  (App Execution Alias bypass)",
    "lake/ path  (ACL-locked data/ directories)",
    "mode(append) + clear_directory_contents()  (Parquet overwrite)",
    "sys.stdout.reconfigure(encoding='utf-8')  (Unicode on Windows)",
    "SQLite JDBC type casts  (DateType/DoubleType mismatch)",
    "load_dotenv(path)  (explicit .env path for FastAPI)",
]
for i, line in enumerate(fixes):
    add_text(slide, f"• {line}", 8.75, 6.22 + i * 0.185, 4.4, 0.2,
             font_size=7, color=LIGHT_GREY)

# ── Footer ────────────────────────────────────────────────────────────────────
add_rect(slide, 0, 7.35, 13.33, 0.15, HEADER_BG)
add_text(slide,
         "Utilitics Data Sharing POC  |  Part 1 Complete — Part 2: Azure Cloud Migration  |  2026-03-19",
         0.15, 7.35, 13.0, 0.15, font_size=7, color=WHITE, align=PP_ALIGN.CENTER)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "C:/Projects/databricks-poc/Utilitics_OnePager.pptx"
prs.save(out)
print(f"Saved: {out}")
