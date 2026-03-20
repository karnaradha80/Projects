"""
Creates the implementation document for the Utilitics POC.
Output: docs/Utilitics_Implementation_Guide.docx
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Inches(8.27)   # A4
section.page_height = Inches(11.69)
section.left_margin = section.right_margin = Inches(1)
section.top_margin  = section.bottom_margin = Inches(0.8)

# ── Styles helpers ────────────────────────────────────────────────────────────
def set_font(run, name="Calibri", size=11, bold=False, italic=False,
             color=None):
    run.font.name  = name
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def heading(text, level=1, color=(31, 73, 125)):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.font.color.rgb = RGBColor(*color)
        run.font.name = "Calibri"
    return p

def para(text, bold=False, italic=False, size=11, color=None, indent=0):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    run = p.add_run(text)
    set_font(run, size=size, bold=bold, italic=italic, color=color)
    return p

def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.3 + level * 0.3)
    run = p.add_run(text)
    set_font(run, size=10)
    return p

def table_header_row(table, headers, bg=(31, 73, 125)):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_font(run, bold=True, color=(255, 255, 255), size=10)
        # Background colour
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), f"{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}")
        tcPr.append(shd)

def shade_row(row, color="EBF3FB"):
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), color)
        tcPr.append(shd)

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    table_header_row(t, headers)
    for ri, row_data in enumerate(rows):
        row = t.rows[ri + 1]
        if ri % 2 == 0:
            shade_row(row, "EBF3FB")
        for ci, val in enumerate(row_data):
            cell = row.cells[ci]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            set_font(run, size=9.5)
    if col_widths:
        for ri in range(len(t.rows)):
            for ci, w in enumerate(col_widths):
                t.rows[ri].cells[ci].width = Inches(w)
    doc.add_paragraph()
    return t

def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    run = p.add_run(text)
    set_font(run, name="Courier New", size=9, color=(0, 0, 128))
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)


# ══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("\n\n\nUTILITICS")
set_font(run, size=32, bold=True, color=(31, 73, 125))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Azure Databricks Data Sharing Platform")
set_font(run, size=18, color=(31, 73, 125))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Part 1 — Local POC Implementation Guide")
set_font(run, size=14, italic=True, color=(89, 89, 89))

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Implementation completed: March 2026")
set_font(run, size=11, color=(89, 89, 89))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Platform: Windows 11  |  Python 3.11  |  PySpark 3.5.1  |  Delta Lake 3.1.0")
set_font(run, size=10, color=(89, 89, 89))

doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 1. PROJECT OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
heading("1. Project Overview")
para(
    "Utilitics is a local Proof of Concept (POC) for an Azure Databricks Data Sharing Platform "
    "built for a utility company. The project demonstrates a complete end-to-end data engineering "
    "pipeline — from raw data generation through to Gold-layer aggregations, Delta Sharing with "
    "external vendors, and ChatOps-based pipeline control via WhatsApp using Claude AI.",
    size=11
)
doc.add_paragraph()

add_table(
    ["Property", "Value"],
    [
        ["Project name",     "Utilitics — Azure Databricks Data Sharing Platform"],
        ["Stage",            "Part 1: Local POC (Windows 11, 24 GB RAM, 1 TB SSD)"],
        ["Architecture",     "Medallion (Bronze → Silver → Gold) + Delta Sharing"],
        ["Execution",        "Local PySpark or Databricks Community Edition (runtime flag)"],
        ["Automation",       "WhatsApp → Twilio → FastAPI → Claude AI → Pipeline"],
        ["Status",           "Part 1 COMPLETE — Part 2 (Azure Cloud) planned"],
        ["Completed date",   "March 2026"],
    ],
    col_widths=[2.0, 4.5]
)


# ══════════════════════════════════════════════════════════════════════════════
# 2. FULL FLOW DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
heading("2. End-to-End Flow Diagram")

para("The diagram below shows the complete data flow from source generation to consumption, "
     "including the ChatOps control layer and the planned Azure migration path.", size=11)
doc.add_paragraph()

# Draw flow diagram as a formatted table with arrows
flow_rows = [
    ("DATA SOURCES (Layer 0 — Raw Input)", "1F4981", "FFFFFF"),
    ("Time Series Parquet → lake/raw/timeseries/\n"
     "500 meters × 7 days × 48 readings = 168,000 records", "EBF3FB", "000000"),
    ("Network Asset Snapshot → SQLite DB (assets.db)\n"
     "2,000 assets × 7 snapshots = 14,000 records", "EBF3FB", "000000"),
    ("Vendor Forecasts Parquet → lake/raw/files/\n"
     "500 forecasts × 168 hourly points = 84,000 records", "EBF3FB", "000000"),
    ("▼  01_generate_data.py", "D6E4F0", "1F4981"),
    ("BRONZE LAYER (Layer 1 — Raw Ingestion into Delta Lake)", "1F4981", "FFFFFF"),
    ("lake/bronze/timeseries/  →  168,000 records  |  Delta version tracked", "EBF3FB", "000000"),
    ("lake/bronze/snapshot/   →   14,000 records  |  Read via pandas from SQLite", "EBF3FB", "000000"),
    ("lake/bronze/files/       →   84,000 records  |  Parquet → Delta", "EBF3FB", "000000"),
    ("▼  02_ingest_bronze.py", "D6E4F0", "1F4981"),
    ("SILVER LAYER (Layer 2 — Cleansed & Validated)", "1F4981", "FFFFFF"),
    ("lake/silver/timeseries/  →  168,000 records  |  Dedup + validation + derived cols", "EBF3FB", "000000"),
    ("lake/silver/snapshot/   →   14,000 records  |  Status/region filters", "EBF3FB", "000000"),
    ("lake/silver/files/       →   84,000 records  |  Schema normalisation", "EBF3FB", "000000"),
    ("▼  03_transform_silver.py", "D6E4F0", "1F4981"),
    ("GOLD LAYER (Layer 3 — Business Aggregations)", "1F4981", "FFFFFF"),
    ("daily_meter_summary   →  3,500 records  (500 meters × 7 days)", "EBF3FB", "000000"),
    ("regional_demand       →    840 records  (5 regions × 24 hrs × 7 days)", "EBF3FB", "000000"),
    ("network_assets        →  2,000 records  (1 row per asset, latest snapshot)", "EBF3FB", "000000"),
    ("forecast_summary      →    420 records  (by date/region/scenario/day)", "EBF3FB", "000000"),
    ("▼  04_aggregate_gold.py", "D6E4F0", "1F4981"),
    ("VALIDATION (Layer 4 — Quality Assurance)", "1F4981", "FFFFFF"),
    ("19/19 checks PASS: drop rates, Gold record counts, quality rules, Delta health, SQLite checks", "EBF3FB", "000000"),
    ("▼  05_validate.py", "D6E4F0", "1F4981"),
    ("DELTA SHARING (Distribution Layer)", "1F4981", "FFFFFF"),
    ("Option A: Python simulation — Provider shares 4 Gold tables with Vendor", "EBF3FB", "000000"),
    ("Option B: OSS Delta Sharing Server (JAR) + real protocol client", "EBF3FB", "000000"),
    ("Bi-directional: Vendor forecast responses written back to Utilitics", "EBF3FB", "000000"),
    ("▼  delta_sharing/simulate_sharing.py", "D6E4F0", "1F4981"),
    ("CHATOPS CONTROL LAYER", "1F4981", "FFFFFF"),
    ("WhatsApp message → Twilio webhook → ngrok tunnel → FastAPI server", "EBF3FB", "000000"),
    ("FastAPI → Claude AI (Anthropic API, tool use) → pipeline_runner.py", "EBF3FB", "000000"),
    ("Claude tools: run_pipeline / run_step / run_sharing / get_status / set_runtime", "EBF3FB", "000000"),
    ("Result → Claude formats → WhatsApp reply sent back to user", "EBF3FB", "000000"),
    ("▼  automation/webhook_server.py + claude_tools.py", "D6E4F0", "1F4981"),
    ("POWER BI (Consumption Layer)", "1F4981", "FFFFFF"),
    ("Power BI Desktop → Parquet connector → lake/gold/* tables", "EBF3FB", "000000"),
    ("Dashboards: daily demand, regional peaks, asset health, forecast scenarios", "EBF3FB", "000000"),
    ("PART 2 — AZURE CLOUD (Planned)", "6E40C9", "FFFFFF"),
    ("ADLS Gen2 replaces lake/ folder  |  Azure Databricks replaces local PySpark", "F3EEFF", "000000"),
    ("Azure Data Factory replaces run_pipeline.py orchestrator", "F3EEFF", "000000"),
    ("Azure SQL replaces SQLite (one JDBC line change)", "F3EEFF", "000000"),
    ("Azure Functions replaces FastAPI + ngrok  |  Same WhatsApp + Claude layer", "F3EEFF", "000000"),
]

t = doc.add_table(rows=len(flow_rows), cols=1)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.LEFT
for ri, (text, bg, fg) in enumerate(flow_rows):
    cell = t.rows[ri].cells[0]
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    is_header  = fg == "FFFFFF"
    is_arrow   = text.startswith("▼")
    set_font(run, size=9.5 if not is_header else 10,
             bold=is_header,
             color=tuple(int(fg[i:i+2], 16) for i in (0, 2, 4)))
    if is_arrow:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), bg)
    tcPr.append(shd)

doc.add_paragraph()
doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 3. WHAT WE IMPLEMENTED
# ══════════════════════════════════════════════════════════════════════════════
heading("3. What We Implemented")

sections_data = [
    ("Section 7 — Data Generation",
     "Created 01_generate_data.py to generate 266,000 synthetic utility records.\n"
     "• Time Series: 500 meters × 7 days × 48 readings = 168,000 Parquet records\n"
     "• Snapshot: 2,000 network assets × 7 daily snapshots = 14,000 rows in SQLite\n"
     "• Forecasts: 500 vendor forecasts × 168 hourly points = 84,000 Parquet records\n"
     "Windows fixes applied: PYSPARK_PYTHON, UTF-8 stdout, append mode + clear helper."),

    ("Section 8 — Bronze Ingestion",
     "Created 02_ingest_bronze.py to ingest all 3 sources into Delta Lake bronze layer.\n"
     "• Time Series + Forecasts: Parquet → Delta (168K + 84K records)\n"
     "• Snapshot: SQLite read via pandas (bypasses JDBC CHAR/VARCHAR type issue) → Delta\n"
     "• Added ingestion metadata: _ingestion_timestamp, _source_file, _ingestion_date\n"
     "• All 3 tables: Raw count = Bronze count (Match: YES)"),

    ("Section 9 — Silver Transformation",
     "Created 03_transform_silver.py to cleanse and validate bronze data.\n"
     "• Deduplication, null checks, range validation, derived columns added\n"
     "• Drop rate: 0.0% across all 3 tables (synthetic data was generated clean)\n"
     "• Added quality metadata columns per table"),

    ("Section 10 — Gold Aggregation",
     "Created 04_aggregate_gold.py to build 4 business-level Gold tables.\n"
     "• daily_meter_summary: 3,500 records (500 meters × 7 days)\n"
     "• regional_demand: 840 records (5 regions × 24 hrs × 7 days)\n"
     "• network_assets: 2,000 records (latest snapshot per asset)\n"
     "• forecast_summary: 420 records (aggregated by date/region/scenario)"),

    ("Sections 11 & 12 — Orchestration + Validation",
     "Created notebooks/run_pipeline.py to orchestrate all 5 steps via subprocess.\n"
     "Created notebooks/05_validate.py with 19 quality checks:\n"
     "• Bronze→Silver drop rates (3 checks)\n"
     "• Gold table record counts (4 checks)\n"
     "• Business quality rules (9 checks: nulls, ranges, UK coordinates, etc.)\n"
     "• SQLite source checks (3 checks: file exists, table exists, count matches)"),

    ("Section 13 — Delta Sharing",
     "Implemented both Option A (simulation) and Option B (OSS server).\n"
     "• Option A: Python simulation — Utilitics shares 4 Gold tables with external vendor\n"
     "  Vendor analyses regional demand peaks and asset maintenance status\n"
     "  Bi-directional: 5 vendor forecast responses written back to Utilitics\n"
     "• Option B: Real OSS Delta Sharing Server + Python client (JAR download required)\n"
     "  server_config.yaml and recipient_profile.json configured and ready"),

    ("Section 14 — Databricks Port + Runtime Flag",
     "Created run.py as unified launcher with RUNTIME flag switching.\n"
     "• RUNTIME = 'local' → runs local PySpark pipeline via subprocess\n"
     "• RUNTIME = 'databricks' → submits to Databricks Community Edition via REST API\n"
     "• run.py --local / --cloud / --config / --status\n"
     "• Created 7 Databricks-format notebooks in notebooks/databricks/:\n"
     "  No SparkSession (managed by cluster), DBFS paths, dbutils.notebook.run(),\n"
     "  dbutils.notebook.exit('SUCCESS'/'FAILED') for ADF integration\n"
     "• Snapshot uses CSV on DBFS (Community Edition has no SQLite)"),

    ("ChatOps — WhatsApp Pipeline Control",
     "Built complete ChatOps automation: WhatsApp → Twilio → ngrok → FastAPI → Claude AI.\n"
     "• automation/pipeline_runner.py: subprocess wrapper with state persistence\n"
     "• automation/claude_tools.py: 6 Claude tool schemas + dispatcher\n"
     "  run_pipeline, run_step, run_sharing, get_status, get_runtime, set_runtime\n"
     "• automation/webhook_server.py: FastAPI app with Twilio webhook\n"
     "  Background threading for long-running pipeline commands\n"
     "  Instant acknowledgement + async result reply\n"
     "• Live tested: 'status' and 'run pipeline' from WhatsApp confirmed working"),

    ("Power BI Integration",
     "Connected Power BI Desktop to Gold layer Delta tables.\n"
     "• Data connector: Parquet file connector → lake/gold/* folders\n"
     "• 4 Gold tables available for dashboards:\n"
     "  daily_meter_summary, regional_demand, network_assets, forecast_summary"),
]

for title, body in sections_data:
    heading(title, level=2, color=(31, 73, 125))
    for line in body.split("\n"):
        if line.startswith("•"):
            bullet(line[1:].strip())
        elif line:
            para(line, size=10.5)
    doc.add_paragraph()

doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 4. TECHNOLOGY STACK
# ══════════════════════════════════════════════════════════════════════════════
heading("4. Technology Stack — What It Is and Why We Used It")
doc.add_paragraph()

add_table(
    ["Technology", "Version", "Purpose", "Why Used"],
    [
        ["Python",         "3.11",         "Primary language for all pipeline scripts",
         "Ecosystem for data engineering; compatible with PySpark and all libraries"],
        ["PySpark",        "3.5.1",        "Distributed data processing engine",
         "Industry standard for large-scale data transformation; same API on Databricks"],
        ["Delta Lake",     "3.1.0",        "ACID-compliant storage format for Bronze/Silver/Gold",
         "Enables schema enforcement, time travel, versioning, and Databricks native format"],
        ["SQLite",         "3.x",          "Local relational database for asset snapshot data",
         "Zero-setup SQL database for local dev; same JDBC pattern as Azure SQL in Part 2"],
        ["SQLAlchemy",     "2.x",          "ORM for writing snapshot data to SQLite",
         "pandas.to_sql() integration; one connection string change migrates to Azure SQL"],
        ["sqlite-jdbc",    "3.44.1.0",     "JDBC driver for Spark to read SQLite",
         "Enables Spark JDBC reads from SQLite; replaced by SQL Server JDBC in Part 2"],
        ["pandas",         "2.x",          "Reading SQLite snapshot into Spark DataFrames",
         "Bypasses JDBC CHAR/VARCHAR type mapping issues from the sqlite-jdbc driver"],
        ["FastAPI",        "latest",       "Webhook server receiving Twilio HTTP POST",
         "Lightweight async Python web framework; production-ready, easy Azure Functions port"],
        ["Uvicorn",        "latest",       "ASGI server running the FastAPI app",
         "High-performance async server; replaces with Azure Functions in Part 2"],
        ["Twilio",         "SDK 9.x",      "WhatsApp messaging API",
         "Industry-standard CPaaS; sandbox available for development without approval"],
        ["Anthropic Claude API", "claude-sonnet-4-6", "AI brain for ChatOps — natural language → tool calls",
         "Tool use API allows Claude to call structured functions; no prompt engineering needed"],
        ["ngrok",          "latest",       "Expose local FastAPI server to the internet",
         "Tunnels Twilio webhooks to localhost; replaced by Azure Functions URL in Part 2"],
        ["python-dotenv",  "latest",       "Load credentials from .env file",
         "Keeps secrets out of code; standard pattern for local dev"],
        ["python-pptx",    "latest",       "Generate PowerPoint one-pager presentation",
         "Programmatic PPT creation without needing Office automation"],
        ["python-docx",    "latest",       "Generate this Word document",
         "Programmatic Word document creation"],
        ["Power BI Desktop", "latest",     "Data visualisation from Gold layer",
         "Microsoft standard BI tool; connects natively to Parquet/Delta files"],
        ["Databricks CE",  "Community Ed.", "Cloud notebook execution environment",
         "Free Databricks tier for testing cloud execution before Azure migration"],
        ["Java 11",        "11 LTS",       "JVM required by PySpark and Delta Lake",
         "PySpark runs on the JVM; Hadoop winutils also requires Java"],
        ["Hadoop winutils", "3.x",         "Windows compatibility layer for Hadoop filesystem",
         "Required on Windows to enable Spark filesystem operations"],
        ["Mermaid.js",     "10.x",         "Architecture diagrams in flowdiagram/architecture.html",
         "Code-defined diagrams; easy to update as architecture evolves"],
    ],
    col_widths=[1.5, 1.0, 2.2, 2.0]
)

doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 5. FILES CREATED
# ══════════════════════════════════════════════════════════════════════════════
heading("5. Files Created / Modified")
doc.add_paragraph()

add_table(
    ["File", "Action", "Description"],
    [
        ["config/pipeline_config.py",            "Modified", "All paths, DB_CONFIG (SQLite), RUNTIME flag, DATABRICKS_CONFIG, quality thresholds"],
        ["config/spark_config.py",               "Modified", "SparkSession factory with extra_packages param for JDBC JARs"],
        ["notebooks/01_generate_data.py",        "Modified", "Synthetic data generation; snapshot writes to SQLite via pandas"],
        ["notebooks/02_ingest_bronze.py",        "Created",  "Raw → Bronze Delta; snapshot read via pandas from SQLite"],
        ["notebooks/03_transform_silver.py",     "Created",  "Bronze → Silver; dedup, validation, derived columns"],
        ["notebooks/04_aggregate_gold.py",       "Created",  "Silver → Gold; 4 business aggregation tables"],
        ["notebooks/05_validate.py",             "Created",  "19 quality checks across all layers including SQLite source"],
        ["notebooks/run_pipeline.py",            "Created",  "Local orchestrator; runs all 5 scripts via subprocess"],
        ["notebooks/databricks/00_config.py",    "Created",  "Databricks shared config with DBFS paths"],
        ["notebooks/databricks/01-06 + run",     "Created",  "7 Databricks-formatted notebooks for Community Edition"],
        ["run.py",                               "Created",  "Unified launcher; --local / --cloud / --config / --status"],
        ["delta_sharing/simulate_sharing.py",    "Modified", "Option A Delta Sharing simulation (Utilitics branding)"],
        ["delta_sharing/server_config.yaml",     "Created",  "Option B OSS server configuration"],
        ["delta_sharing/recipient_profile.json", "Created",  "Option B vendor recipient profile"],
        ["delta_sharing/consume_shared_data.py", "Created",  "Option B Python client for real Delta Sharing protocol"],
        ["delta_sharing/run_sharing.py",         "Created",  "Interactive launcher — choose Option A or B"],
        ["automation/pipeline_runner.py",        "Created",  "Subprocess wrapper; run_full_pipeline, run_step, get_status, set_runtime"],
        ["automation/claude_tools.py",           "Created",  "Claude tool schemas (6 tools) + execute_tool dispatcher"],
        ["automation/webhook_server.py",         "Created",  "FastAPI Twilio webhook; ask_claude agentic loop; background threading"],
        ["automation/.env.example",             "Created",  "Credentials template (Twilio + Anthropic keys)"],
        ["flowdiagram/architecture.html",        "Created",  "Dark theme HTML with 6 Mermaid.js diagrams + progress bars"],
        ["conversation/conversation_log.txt",    "Created",  "Full conversation log with decisions, fixes, and results"],
        ["Utilitics_OnePager.pptx",              "Created",  "Single-slide PowerPoint covering all 6 sections"],
        ["docs/Utilitics_Implementation_Guide.docx", "Created", "This document"],
    ],
    col_widths=[2.3, 0.8, 3.6]
)

doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 6. ERRORS AND FIXES
# ══════════════════════════════════════════════════════════════════════════════
heading("6. Key Errors Encountered and Fixes Applied")
doc.add_paragraph()

add_table(
    ["Error", "Root Cause", "Fix Applied", "File"],
    [
        ["Windows ACL locked directories",
         "Pre-created data/ directories had locked Windows ACLs — Spark could not write or delete",
         "Changed LOCAL_BASE from data/ to lake/ (fresh directory Spark creates itself)",
         "pipeline_config.py"],
        ["Python worker not found",
         "Windows App Execution Aliases redirect 'python' to Microsoft Store instead of venv",
         "Set os.environ['PYSPARK_PYTHON'] = sys.executable before SparkSession",
         "spark_config.py"],
        ["UnicodeEncodeError on Windows console",
         "Box-drawing characters (chr(0x2500)) cannot print on Windows cp1252 console",
         "sys.stdout.reconfigure(encoding='utf-8') at startup",
         "spark_config.py, run_pipeline.py"],
        ["Parquet overwrite fails on locked dirs",
         "Spark's FileUtil.fullyDelete() via winutils fails on Windows locked directories",
         "Added clear_directory_contents() helper; changed mode('overwrite') → mode('append')",
         "01_generate_data.py"],
        ["AnalysisException: DateType vs StringType",
         "SQLite JDBC returns date columns as StringType; existing Delta table had DateType",
         ".withColumn('snapshot_date', F.to_date(F.col('snapshot_date')))",
         "02_ingest_bronze.py"],
        ["AnalysisException: DoubleType vs FloatType",
         "SQLite JDBC returns REAL columns as FloatType; Delta table schema had DoubleType",
         "Explicit .cast('double') for capacity_mw, voltage_kv, location_lat, location_lon",
         "02_ingest_bronze.py"],
        ["DeltaInvariantViolationException: CHAR(0)",
         "SQLite JDBC driver maps TEXT columns to CHAR(0); Delta enforces zero-length constraint",
         "Read SQLite via pandas + createDataFrame() instead of JDBC — bypasses type mapping",
         "02_ingest_bronze.py"],
        ["ModuleNotFoundError: sqlalchemy",
         "SQLAlchemy not installed in venv",
         "pip install sqlalchemy",
         "venv"],
        ["FastAPI: python-multipart missing",
         "FastAPI Form() parameters require python-multipart package",
         "pip install python-multipart",
         "venv"],
        ["Twilio/Anthropic clients not initialised",
         "load_dotenv() searches CWD, not the automation/ folder containing .env",
         "load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))",
         "webhook_server.py"],
        ["Anthropic API 401 Unauthorized",
         "Old deleted API key still set as ANTHROPIC_API_KEY shell env var, overriding .env",
         "export ANTHROPIC_API_KEY=<new-key> before starting server",
         "Shell environment"],
        ["Pipeline runner success=False in 0.2s",
         "run.py used capture_output=False so stdout was not captured; exit via sys.exit() not propagated",
         "pipeline_runner.py now calls notebooks/run_pipeline.py directly (skips run.py for local)",
         "automation/pipeline_runner.py"],
        ["get_current_runtime() returns cached value",
         "Python module caching — after set_runtime() edits pipeline_config.py, re-import returns old value",
         "get_current_runtime() now reads RUNTIME line directly from file via regex (no import)",
         "automation/pipeline_runner.py"],
        ["FastAPI blocks on long pipeline runs",
         "Uvicorn single-threaded; 5-minute pipeline blocks entire server, Twilio times out",
         "Long-running commands dispatched to background threading.Thread(daemon=True)",
         "automation/webhook_server.py"],
    ],
    col_widths=[1.8, 1.8, 2.3, 0.8]
)

doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
# 7. PIPELINE EXECUTION RESULTS
# ══════════════════════════════════════════════════════════════════════════════
heading("7. Pipeline Execution Results")
doc.add_paragraph()

add_table(
    ["Run", "Date", "Steps", "Result", "Records", "Elapsed"],
    [
        ["Run 1", "2026-03-18", "Data Generation only",        "SUCCESS", "266,000 total", "71.2s"],
        ["Run 2", "2026-03-18", "Bronze Ingestion only",       "SUCCESS", "266,000 matched", "46.5s"],
        ["Run 3", "2026-03-18", "Silver Transformation only",  "SUCCESS", "0% drop rate", "49.0s"],
        ["Run 4", "2026-03-18", "Gold Aggregation only",       "SUCCESS", "6,760 Gold records", "60.7s"],
        ["Run 5", "2026-03-18", "Full pipeline (all 5 steps)", "SUCCESS", "19/19 checks PASS", "298s (~5 min)"],
        ["Run 6", "2026-03-19", "Delta Sharing Option A",      "SUCCESS", "4 tables shared", "~30s"],
        ["Run 7", "2026-03-19", "Full pipeline + SQLite",      "SUCCESS", "19/19 checks PASS", "~5 min"],
        ["Run 8", "2026-03-19", "ChatOps live test (WhatsApp)","SUCCESS", "End-to-end confirmed", "~5 min"],
        ["Run 9", "2026-03-20", "Full fresh pipeline",         "SUCCESS", "19/19 checks PASS", "~5 min"],
    ],
    col_widths=[0.6, 1.0, 2.1, 1.0, 1.5, 0.9]
)


# ══════════════════════════════════════════════════════════════════════════════
# 8. KEY DECISIONS
# ══════════════════════════════════════════════════════════════════════════════
heading("8. Key Architecture Decisions")
doc.add_paragraph()

decisions = [
    ("lake/ instead of data/ for storage",
     "Pre-created data/ directories had locked Windows ACLs preventing Spark writes. "
     "Using lake/ (a fresh directory Spark creates itself) resolved all permission issues."),
    ("SQLite for snapshot data (local)",
     "Mixed-source architecture is more realistic. SQLite has no size limitations for 14K rows "
     "and uses the same JDBC pattern as Azure SQL in Part 2 — only the connection string changes."),
    ("pandas for SQLite reads (not JDBC)",
     "The sqlite-jdbc JDBC driver maps TEXT columns to CHAR(0) types which Delta Lake rejects. "
     "Reading via pandas.read_sql_table() and converting with createDataFrame() bypasses the issue entirely."),
    ("RUNTIME flag for local/cloud switching",
     "User wanted to switch between local PySpark and Databricks Community Edition on the fly "
     "without changing code. A single RUNTIME flag in pipeline_config.py routes run.py accordingly."),
    ("CSV on DBFS for snapshot in Databricks",
     "Databricks Community Edition cluster nodes do not have local SQLite. "
     "Snapshot is written to CSV on DBFS instead, with Azure SQL JDBC code ready to uncomment for Part 2."),
    ("Background threading for long pipeline runs",
     "FastAPI/Uvicorn is single-threaded by default. A 5-minute pipeline call blocks the server "
     "and causes Twilio to time out. Threading with daemon=True allows instant webhook response "
     "while the pipeline runs asynchronously, then sends the result via a second WhatsApp message."),
    ("Claude AI tool use for ChatOps",
     "Claude's tool use API allows natural language commands ('run pipeline', 'switch to databricks') "
     "to be mapped to structured function calls without any prompt engineering or regex parsing."),
    ("Both Delta Sharing options implemented",
     "Option A (Python simulation) works immediately with no extra setup. "
     "Option B (OSS server) is production-quality but requires a manual JAR download. "
     "An interactive launcher lets the user choose at runtime."),
]

for title, body in decisions:
    heading(title, level=2, color=(31, 73, 125))
    para(body, size=10.5)
    doc.add_paragraph()


# ══════════════════════════════════════════════════════════════════════════════
# 9. PART 2 — AZURE CLOUD PLAN
# ══════════════════════════════════════════════════════════════════════════════
heading("9. Part 2 — Azure Cloud Migration Plan")
doc.add_paragraph()

para("Part 2 migrates the entire local pipeline to Azure. The architecture is designed so that "
     "the migration requires minimal code changes — primarily connection strings and paths.", size=11)
doc.add_paragraph()

add_table(
    ["Local (Part 1)", "Azure Equivalent (Part 2)", "Migration Effort"],
    [
        ["lake/ folder (local filesystem)",    "Azure Data Lake Storage Gen2",           "Path change only"],
        ["SQLite (assets.db)",                 "Azure SQL Database",                     "1 JDBC connection string change"],
        ["notebooks/run_pipeline.py",          "Azure Data Factory pipeline",            "ADF pipeline definition"],
        ["Local PySpark",                      "Azure Databricks (paid, with Unity Catalog)", "Upload notebooks, set cluster"],
        ["FastAPI + ngrok (localhost)",        "Azure Functions (HTTP trigger)",          "Port webhook_server.py to Azure Function"],
        ["delta_sharing/simulate_sharing.py",  "Databricks-managed Delta Sharing",        "Enable Unity Catalog Delta Sharing"],
        ["DATABRICKS_TOKEN env var",           "Azure Key Vault + Managed Identity",     "Replace env vars with Key Vault refs"],
        ["Same Claude AI + WhatsApp layer",    "Unchanged — same Twilio + Anthropic",    "No change needed"],
    ],
    col_widths=[2.2, 2.4, 2.1]
)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Utilitics — Azure Databricks Data Sharing Platform  |  Part 1 Local POC  |  March 2026")
set_font(run, size=9, italic=True, color=(128, 128, 128))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Generated by Claude AI (claude-sonnet-4-6)  |  Anthropic")
set_font(run, size=9, italic=True, color=(128, 128, 128))

# ── Save ──────────────────────────────────────────────────────────────────────
out = "C:/Projects/databricks-poc/docs/Utilitics_Implementation_Guide.docx"
doc.save(out)
print(f"Saved: {out}")
