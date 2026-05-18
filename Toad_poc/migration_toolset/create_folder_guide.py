"""
Generates migration_toolset_guide.xlsx — folder structure + step-by-step process guide.
Run once: python create_folder_guide.py
"""

import openpyxl
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter

# ─────────────────────────────────────────────────────────────────────────────
# Content
# ─────────────────────────────────────────────────────────────────────────────

# (step, category, path, description)
# step = '' for folder/output rows (not a numbered tool step)
ROWS = [
    # ── PRE-REQUISITES ────────────────────────────────────────────────────────
    ('',   'ROOT',       'migration_toolset\\',
     'Root folder for the entire Toad → Azure migration toolset'),

    ('',   'INPUT',      'migration_toolset\\input\\',
     'Place raw Toad XML automation files here before running Tool 1'),

    ('',   'GLOBAL',     'migration_toolset\\global\\',
     'Shared resources used across all 200+ reports'),

    ('',   'GLOBAL',     'migration_toolset\\global\\mapping_registry.csv',
     'Global registry: maps every real value (email/server/password) to its mock replacement. GITIGNORED.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\poc_team_config.json',
     'Dev team email addresses for --poc testing mode. Fill before running Tool 3 --poc.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\actual_mapping_files\\{report}_actual_mapping.csv',
     'Per-report actual email list (real client emails). GITIGNORED — never commit.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\poc_mapping_files\\{report}_poc_mapping.csv',
     'Per-report POC email list (dev team emails mapped to each report). Safe to commit.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\final_actual_mapping.csv',
     'Consolidated: DISTINCT (report, real_email) across all processed reports. GITIGNORED.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\final_poc_mapping.csv',
     'Consolidated: every report x dev team emails. Used for bulk Tool 3 --poc runs.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\xlsm_templates\\{report_name}\\',
     'Place the report Excel template (.xlsm) here before running Tool 5 blob upload.'),

    ('',   'GLOBAL',     'migration_toolset\\global\\config\\config_schema_ddl.sql',
     'Tool 3 output: CREATE TABLE DDL for config schema (config.report, config.report_email, config.report_sql). Run once per environment.'),

    # ── STEP 1 ────────────────────────────────────────────────────────────────
    ('STEP 1', 'TOOL',   'migration_toolset\\tools\\tool1_sanitize.py',
     'Sanitize Toad XML: replace all sensitive values (emails, passwords, servers, UNC paths) with safe mock values'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\sanitized\\{report}_sanitized.txt',
     'Sanitized XML file — safe to share, use in all downstream tools'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\sanitized\\{report}_mapping.csv',
     'Per-report mapping: real value → mock value for this report only'),

    # ── STEP 2 (POC only) ─────────────────────────────────────────────────────
    ('STEP 2\n(POC only)', 'TOOL', 'migration_toolset\\tools\\tool1_01_mock_data.py',
     'Mock Data Generator: reads 10 seed rows per table from input\\seed\\ → generates 1000+ synthetic rows'),

    ('',   'INPUT',      'migration_toolset\\input\\seed\\{report}\\{table}.csv',
     'User-supplied: 10 real rows per table (anonymised). Used as seed for mock data generation.'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\mock_data\\{table}.csv',
     'Generated mock data: 10 seed rows + 1000 synthetic rows per table'),

    # ── STEP 3 (POC only) ─────────────────────────────────────────────────────
    ('STEP 3\n(POC only)', 'TOOL', 'migration_toolset\\tools\\tool1_02_ddl_generator.py',
     'DDL Generator: infers SQL column types from mock CSVs + schema from sanitized XML → generates CREATE TABLE scripts'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\ddl\\{report}_ddl.sql',
     'T-SQL CREATE TABLE DDL for all tables in the report. Idempotent (IF OBJECT_ID guard).'),

    # ── STEP 4 ────────────────────────────────────────────────────────────────
    ('STEP 4', 'TOOL',   'migration_toolset\\tools\\tool2_adf_generator.py',
     'ADF ARM Template Generator: reads sanitized XML → generates Linked Services, Datasets, Pipeline JSON + combined ARM template'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\linkedServices\\',
     'ADF Linked Service JSONs: LS_AzureKeyVault, LS_AzureSQL_Source, LS_AzureBlobStorage'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\datasets\\',
     'ADF Dataset JSONs: one per SQL table + ODS log + report source + blob output/archive + config'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\pipelines\\PL_{report}.json',
     'ADF Pipeline JSON: full activity chain (ODS check → set vars → copy data → email notifications)'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\arm_template.json',
     'Combined deployable ARM template: all 16 resources (factory + LS + datasets + pipeline)'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\arm_template_parameters.json',
     'Parameter template: fill server names, Key Vault name, storage account before deploying. GITIGNORED.'),

    # ── STEP 5 ────────────────────────────────────────────────────────────────
    ('STEP 5', 'TOOL',   'migration_toolset\\tools\\tool3_config_setup.py',
     'Config Setup: reads sanitized XML → generates config schema DDL + per-report INSERT SQL (emails, SQL queries, template info)'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\config\\{report}_config_data.sql',
     'Idempotent INSERT SQL for config.report (+ template), config.report_sql (ODS_CHECK + REPORT_MAIN), config.report_email'),

    # ── STEP 6 ────────────────────────────────────────────────────────────────
    ('STEP 6', 'TOOL',   'migration_toolset\\tools\\tool4_adf_deploy.py',
     'ADF Deploy Script Generator: splits ARM template into bootstrap (once) + per-report; generates PS1 + bash deploy scripts'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\deploy\\deploy_bootstrap.ps1 / .sh',
     'Run once per environment: deploys ADF factory + 3 shared Linked Services'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\deploy\\deploy_{report}.ps1 / .sh',
     'Run per report: deploys 11 datasets + 1 pipeline (Incremental mode)'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\adf\\deploy\\deployment_checklist.txt',
     'Parameter status checklist: shows [OK]/[!!] per parameter + full resource list + run order'),

    # ── STEP 7 ────────────────────────────────────────────────────────────────
    ('STEP 7', 'TOOL',   'migration_toolset\\tools\\tool5_blob_upload.py',
     'Blob Upload Script Generator: extracts xlsm template filename from sanitized XML → generates PS1 + bash az storage upload scripts'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\blob\\upload_{report}.ps1 / .sh',
     'Upload script: az storage blob upload for xlsm template → templates/{report}/{file}.xlsm in Blob Storage'),

    ('',   'OUTPUT',     'migration_toolset\\reports\\{report}\\blob\\blob_checklist.txt',
     'Template presence check: [OK] if xlsm found in global\\xlsm_templates\\{report}\\, [!!] if missing'),

    # ── UTILITIES ─────────────────────────────────────────────────────────────
    ('',   'UTILITY',    'migration_toolset\\tools\\utils\\xml_parser.py',
     'ToadXmlParser: extracts all sensitive values from Toad XML (emails, passwords, servers, UNC paths, SQL tables)'),

    ('',   'UTILITY',    'migration_toolset\\tools\\utils\\mapping_registry.py',
     'MappingRegistry: loads/saves global CSV, generates consistent mock replacements across all reports'),
]

# ─────────────────────────────────────────────────────────────────────────────
# Colour palette
# ─────────────────────────────────────────────────────────────────────────────

COL_HEADER   = '1F4E79'   # dark blue
COL_STEP     = '2E75B6'   # medium blue
COL_TOOL     = 'D6E4F0'   # light blue
COL_OUTPUT   = 'EBF3E8'   # light green
COL_INPUT    = 'FFF2CC'   # light yellow
COL_GLOBAL   = 'F2F2F2'   # light grey
COL_ROOT     = 'D9D9D9'   # grey
COL_UTILITY  = 'EDE7F6'   # light purple

CATEGORY_FILL = {
    'TOOL':    COL_TOOL,
    'OUTPUT':  COL_OUTPUT,
    'INPUT':   COL_INPUT,
    'GLOBAL':  COL_GLOBAL,
    'ROOT':    COL_ROOT,
    'UTILITY': COL_UTILITY,
}

def _fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def _border():
    thin = Side(style='thin', color='BFBFBF')
    return Border(left=thin, right=thin, top=thin, bottom=thin)


# ─────────────────────────────────────────────────────────────────────────────
# Build workbook
# ─────────────────────────────────────────────────────────────────────────────

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Migration Toolset Guide'

# ── Column widths ─────────────────────────────────────────────────────────────
ws.column_dimensions['A'].width = 14   # Step
ws.column_dimensions['B'].width = 72   # Path
ws.column_dimensions['C'].width = 70   # Description

# ── Header row ────────────────────────────────────────────────────────────────
headers = ['Step', 'Folder / File Path', 'Description']
for col, h in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font      = Font(bold=True, color='FFFFFF', size=12)
    cell.fill      = _fill(COL_HEADER)
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border    = _border()

ws.row_dimensions[1].height = 24

# ── Data rows ─────────────────────────────────────────────────────────────────
for i, (step, category, path, desc) in enumerate(ROWS, start=2):
    bg = CATEGORY_FILL.get(category, 'FFFFFF')
    is_step = bool(step)

    # Step column
    c_step = ws.cell(row=i, column=1, value=step)
    c_step.font      = Font(bold=is_step, color=('FFFFFF' if is_step else '595959'), size=10)
    c_step.fill      = _fill(COL_STEP if is_step else bg)
    c_step.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c_step.border    = _border()

    # Path column
    c_path = ws.cell(row=i, column=2, value=path)
    c_path.font      = Font(bold=is_step, name='Courier New', size=9,
                            color=('1F4E79' if is_step else '2C2C2C'))
    c_path.fill      = _fill(bg)
    c_path.alignment = Alignment(vertical='center', wrap_text=True)
    c_path.border    = _border()

    # Description column
    c_desc = ws.cell(row=i, column=3, value=desc)
    c_desc.font      = Font(size=10, color='2C2C2C')
    c_desc.fill      = _fill(bg)
    c_desc.alignment = Alignment(vertical='center', wrap_text=True)
    c_desc.border    = _border()

    ws.row_dimensions[i].height = 36 if '\n' in step else 28

# ── Freeze top row ────────────────────────────────────────────────────────────
ws.freeze_panes = 'A2'

# ── Legend sheet ──────────────────────────────────────────────────────────────
wl = wb.create_sheet('Legend')
wl.column_dimensions['A'].width = 18
wl.column_dimensions['B'].width = 55

legend_header = wl.cell(row=1, column=1, value='Colour Legend')
legend_header.font  = Font(bold=True, color='FFFFFF', size=12)
legend_header.fill  = _fill(COL_HEADER)
wl.merge_cells('A1:B1')
wl.cell(row=1, column=1).alignment = Alignment(horizontal='center')

legend_rows = [
    (COL_STEP,    'STEP N',   'Numbered tool step — run in this order'),
    (COL_TOOL,    'TOOL',     'Python tool script to run'),
    (COL_INPUT,   'INPUT',    'Files you must provide before running the step'),
    (COL_OUTPUT,  'OUTPUT',   'Files generated automatically by the tool'),
    (COL_GLOBAL,  'GLOBAL',   'Shared files used across all reports'),
    (COL_ROOT,    'ROOT',     'Root folder'),
    (COL_UTILITY, 'UTILITY',  'Shared utility modules (used by tools internally)'),
]

for r, (color, label, meaning) in enumerate(legend_rows, start=2):
    ca = wl.cell(row=r, column=1, value=label)
    ca.fill      = _fill(color)
    ca.font      = Font(bold=True, size=10)
    ca.alignment = Alignment(horizontal='center', vertical='center')
    ca.border    = _border()
    cb = wl.cell(row=r, column=2, value=meaning)
    cb.fill      = _fill(color)
    cb.font      = Font(size=10)
    cb.alignment = Alignment(vertical='center')
    cb.border    = _border()
    wl.row_dimensions[r].height = 22

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────

import os
out = os.path.join(os.path.dirname(__file__), 'migration_toolset_guide.xlsx')
wb.save(out)
print(f'Created: {out}')
