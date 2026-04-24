import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# Page margins
section = doc.sections[0]
section.top_margin    = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin   = Cm(2)
section.right_margin  = Cm(2)

# Colour palette
DARK_BLUE  = RGBColor(0x1F, 0x35, 0x64)
MID_BLUE   = RGBColor(0x2E, 0x75, 0xB6)
ALT_ROW    = RGBColor(0xF2, 0xF7, 0xFD)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x00, 0x00, 0x00)
GREY       = RGBColor(0x80, 0x80, 0x80)

def set_cell_bg(cell, rgb):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    hex_color = '{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def bold_para(cell, text, font_size=9, color=WHITE, align=WD_ALIGN_PARAGRAPH.CENTER):
    para = cell.paragraphs[0]
    para.alignment = align
    run  = para.add_run(text)
    run.bold = True
    run.font.size = Pt(font_size)
    run.font.color.rgb = color

def normal_para(cell, text, font_size=8.5, color=BLACK, align=WD_ALIGN_PARAGRAPH.LEFT):
    para = cell.paragraphs[0]
    para.alignment = align
    run  = para.add_run(text)
    run.font.size = Pt(font_size)
    run.font.color.rgb = color

# ── RTM table helper ─────────────────────────────────────────────────────────
HEADERS = [
    'RTM ID', 'BRD Req ID', 'Requirement Description',
    'TDD Design Component', 'DB / Package Reference',
    'Test Case ID', 'Status', 'Notes'
]
COL_WIDTHS = [Cm(1.4), Cm(2.1), Cm(5.0), Cm(3.6), Cm(3.6), Cm(1.9), Cm(1.8), Cm(2.4)]

def add_rtm_table(rows_data):
    tbl = doc.add_table(rows=1 + len(rows_data), cols=len(HEADERS))
    tbl.style = 'Table Grid'
    for j, (hdr, w) in enumerate(zip(HEADERS, COL_WIDTHS)):
        cell = tbl.cell(0, j)
        cell.width = w
        set_cell_bg(cell, DARK_BLUE)
        bold_para(cell, hdr, font_size=8, color=WHITE)
    for i, row_data in enumerate(rows_data):
        bg = ALT_ROW if i % 2 == 1 else WHITE
        for j, val in enumerate(row_data):
            cell = tbl.cell(i + 1, j)
            cell.width = COL_WIDTHS[j]
            set_cell_bg(cell, bg)
            normal_para(cell, val, font_size=8)
    doc.add_paragraph()

def add_h1(text):
    h = doc.add_heading(text, level=1)
    h.runs[0].font.color.rgb = DARK_BLUE

def add_h2(text):
    h = doc.add_heading(text, level=2)
    h.runs[0].font.color.rgb = MID_BLUE

def add_body(text):
    p = doc.add_paragraph(text)
    p.runs[0].font.size = Pt(9)

# ════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ════════════════════════════════════════════════════════════════════════════
doc.add_paragraph('\n\n')

tbl = doc.add_table(rows=1, cols=1)
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = tbl.cell(0, 0)
set_cell_bg(cell, DARK_BLUE)
p = cell.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('\nMAVIS Faster Staging\nRequirements Traceability Matrix (RTM)\nD0010 & D0150 Flows\n')
r.bold = True
r.font.size = Pt(20)
r.font.color.rgb = WHITE

doc.add_paragraph()

meta = doc.add_table(rows=5, cols=2)
meta.alignment = WD_TABLE_ALIGNMENT.CENTER
meta.style = 'Table Grid'
labels = ['Project', 'Document Type', 'Author', 'Date', 'Version']
values = ['MAVIS Faster Staging', 'Requirements Traceability Matrix (RTM)', 'Danie Selvaraju', '14-01-2026', '1.0']
for i, (lbl, val) in enumerate(zip(labels, values)):
    lc = meta.cell(i, 0)
    vc = meta.cell(i, 1)
    set_cell_bg(lc, MID_BLUE)
    bold_para(lc, lbl, font_size=9)
    normal_para(vc, val, font_size=9, color=BLACK)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 1. DOCUMENT CONTROL
# ════════════════════════════════════════════════════════════════════════════
add_h1('1. Document Control')
add_h2('1.1 Version History')
vh = doc.add_table(rows=2, cols=4)
vh.style = 'Table Grid'
for j, hdr in enumerate(['Version', 'Date', 'Author', 'Description of Change']):
    set_cell_bg(vh.cell(0, j), MID_BLUE)
    bold_para(vh.cell(0, j), hdr, font_size=9)
for j, v in enumerate(['1.0', '14-01-2026', 'Danie Selvaraju', 'Initial RTM created from BRD v0.1 and TDD v0.2']):
    normal_para(vh.cell(1, j), v, font_size=8.5)

doc.add_paragraph()
add_h2('1.2 Reference Documents')
rd = doc.add_table(rows=3, cols=3)
rd.style = 'Table Grid'
for j, hdr in enumerate(['Doc ID', 'Document Title', 'Version']):
    set_cell_bg(rd.cell(0, j), MID_BLUE)
    bold_para(rd.cell(0, j), hdr, font_size=9)
refs = [
    ['BRD-001', 'MHHS Faster Staging - Business Requirements Document', 'v0.1'],
    ['TDD-001', 'MHHS Faster Staging - Technical Design Document', 'v0.2'],
]
for i, row_data in enumerate(refs):
    for j, v in enumerate(row_data):
        normal_para(rd.cell(i + 1, j), v, font_size=8.5)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 2. INTRODUCTION
# ════════════════════════════════════════════════════════════════════════════
add_h1('2. Introduction')

add_h2('2.1 Purpose')
add_body(
    'This Requirements Traceability Matrix (RTM) provides end-to-end traceability from business '
    'requirements captured in the BRD through to functional requirements, technical design '
    'components, and test cases for the MAVIS Faster Staging project. The RTM is a living '
    'document updated throughout the Software Development Lifecycle (SDLC).'
)

add_h2('2.2 Scope')
add_body(
    'This RTM covers all requirements for D0010 (Meter Readings) and D0150 (Non Half Hourly '
    'Meter Technical Details) flow processing as described in BRD v0.1. Out-of-scope items '
    '(post-staging transformations, business rule validations beyond structural checks, '
    'UI for configuration management) are excluded.'
)

add_h2('2.3 How to Read the RTM')
for item in [
    'RTM ID: unique identifier for each traceability row.',
    'BRD Req ID: source requirement ID from the Business Requirements Document.',
    'Requirement Description: brief description of the requirement.',
    'TDD Design Component: the design component or function in the Technical Design Document.',
    'DB / Package Reference: the Oracle package, procedure, or table implementing the requirement.',
    'Test Case ID: linked test case(s) from the Test Plan.',
    'Status: Not Started | In Progress | Completed | Verified.',
    'Notes: open issues, assumptions, or dependencies.',
]:
    ip = doc.add_paragraph(style='List Bullet')
    ip.add_run(item).font.size = Pt(9)

add_h2('2.4 SDLC Context (Waterfall)')
add_body(
    'In the Waterfall SDLC Phase Overview, the RTM is first produced during Phase 1 - Planning & '
    'Requirements, immediately after the BRD is baselined and Requirements are frozen. The matrix '
    'is progressively enriched: TDD references are added in Phase 2 (System Design), Test Case IDs '
    'are linked in Phase 3 (Testing), and the Status column is updated to Verified once each '
    'requirement passes QA/UAT sign-off. A complete, fully-Verified RTM is a mandatory exit '
    'criterion before Phase 5 (Deployment).'
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 3. BUSINESS REQUIREMENTS
# ════════════════════════════════════════════════════════════════════════════
add_h1('3. Business Requirements Traceability')
add_body(
    'The following table traces each business requirement from the BRD to its implementing '
    'technical design component, Oracle package/procedure, and linked test case.'
)

biz_rows = [
    ['RTM-B-001', 'REQ-001',
     'Accept & process pipe-delimited files for D0010 & D0150',
     'PKG_DTC_D0010 / PKG_DTC_D0150 - PRC_PROCESS_FILE_V2',
     'PRC_PROCESS_FILE_V2 (both packages)',
     'TC-B-001', 'Completed', 'Core entry-point procedure'],
    ['RTM-B-002', 'REQ-002',
     'Two-stage validation: Stage 1 (file-level critical), Stage 2 (group-level partial acceptance)',
     'PKG_DTC_VALIDATION - FN_VALIDATE_STAGE1, FN_VALIDATE_STAGE2',
     'FN_VALIDATE_STAGE1, FN_VALIDATE_STAGE2',
     'TC-B-002', 'Completed', 'Generic reusable functions'],
    ['RTM-B-003', 'REQ-003',
     'Reject entire file if Stage 1 validation fails',
     'FN_VALIDATE_STAGE1 - returns REJECTED status',
     'FN_VALIDATE_STAGE1 -> status = REJECTED',
     'TC-B-003', 'Completed', 'No data staged on Stage 1 failure'],
    ['RTM-B-004', 'REQ-004',
     'Partial acceptance on Stage 2 failure - only valid parent groups staged',
     'FN_VALIDATE_STAGE2 - hierarchical validity flags',
     'Boolean flags v_XXX_valid per parent group',
     'TC-B-004', 'Completed', 'Groups individually accepted/rejected'],
    ['RTM-B-005', 'REQ-005',
     'Data integrity - child records linked only to valid parent records',
     'Hierarchical Validation Logic (Boolean flags)',
     'v_026_valid, v_028_valid, v_030_valid (D0010)',
     'TC-B-005', 'Completed', 'Cascading rejection on parent failure'],
    ['RTM-B-006', 'REQ-006',
     'Validate file-level components (header, footer, record counts, file ID consistency)',
     'FN_VALIDATE_STAGE1 - header/footer parse & count checks',
     'FN_PARSE_HEADER, FN_PARSE_FOOTER',
     'TC-B-006', 'Completed', '6 discrete checks in Stage 1'],
    ['RTM-B-007', 'REQ-007',
     'Field-level validation: mandatory, length, datatype, pattern matching, precision/scale',
     'FN_VALIDATE_FIELD - 5-step validation engine',
     'FN_VALIDATE_FIELD',
     'TC-B-007', 'Completed', 'Covers NUMBER, DATE, DATETIME, VARCHAR2'],
    ['RTM-B-008', 'REQ-008',
     'Validate hierarchical relationships: parent group existence and nested integrity',
     'FN_VALIDATE_STAGE2 - hierarchical propagation logic',
     'Boolean validity flags per group level',
     'TC-B-008', 'Completed', 'Strict parent-child enforcement'],
    ['RTM-B-009', 'REQ-009',
     'Capture & report all errors with: error code, message, line no., field name, group ID',
     'ADD_ERROR / WRITE_ERROR procedures',
     'MDQ_ETL_ERROR table',
     'TC-B-009', 'Completed', 'Full error detail per validation failure'],
    ['RTM-B-010', 'REQ-010',
     'Differentiate Stage 1 (file rejection) vs Stage 2 (group rejection) errors',
     'Error code ranges: ERR-1xx (Stage 1) / ERR-2xx (Stage 2)',
     'MDQ_ETL_ERROR.ERROR_CODE',
     'TC-B-010', 'Completed', 'Error code prefix identifies stage'],
    ['RTM-B-011', 'REQ-011',
     'Provide statistics: total, staged, rejected record and flow counts (6 metrics)',
     'WRITE_AUDIT - statistics capture',
     'MDQ_ETL_AUDIT table',
     'TC-B-011', 'Completed', '6 count metrics written per run'],
]
add_rtm_table(biz_rows)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 4. D0010 FUNCTIONAL REQUIREMENTS
# ════════════════════════════════════════════════════════════════════════════
add_h1('4. D0010 Functional Requirements Traceability')
add_body(
    'Traceability for D0010 (Meter Readings) flow processing requirements, covering file '
    'structure, data elements, and hierarchical validation rules.'
)

d0010_rows = [
    ['RTM-D10-001', 'REQ-D0010-001',
     'Process D0010 v002 files: ZHV header, groups 026-033, ZPT footer',
     'PKG_DTC_D0010 - PRC_PROCESS_FILE_V2', 'PRC_PROCESS_FILE_V2',
     'TC-D10-001', 'Completed', ''],
    ['RTM-D10-002', 'REQ-D0010-002',
     'Recognise group 026 as parent group (MPAN level)',
     'FN_INSERT_GROUP_026 - parent flag logic', 'FN_INSERT_GROUP_026',
     'TC-D10-002', 'Completed', 'v_026_valid flag initialised here'],
    ['RTM-D10-003', 'REQ-D0010-003',
     'Support D0010 hierarchy: 026 -> 027/028 -> 029/030 -> 032/033',
     'Hierarchical Validation Logic - D0010 Boolean flags',
     'v_026_valid, v_028_valid, v_030_valid',
     'TC-D10-003', 'Completed', 'Hierarchy strictly enforced'],
    ['RTM-D10-004', 'REQ-D0010-004',
     'Group 026: MPAN (13 digits, mandatory), BSC Validation Status (1 char, mandatory)',
     'Config: D0010/group-026 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 026',
     'TC-D10-004', 'Completed', 'JSON config drives field validation'],
    ['RTM-D10-005', 'REQ-D0010-005',
     'Group 027: Site Visit Check (2 chars, mandatory), Additional Info (0-200, optional)',
     'Config: D0010/group-027 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 027',
     'TC-D10-005', 'Completed', ''],
    ['RTM-D10-006', 'REQ-D0010-006',
     'Group 028: Meter ID (1-10 chars, mandatory), Reading Type (1 char, mandatory)',
     'Config: D0010/group-028 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 028',
     'TC-D10-006', 'Completed', ''],
    ['RTM-D10-007', 'REQ-D0010-007',
     'Group 029: Site Visit Check (2 chars, mandatory), Additional Info (optional)',
     'Config: D0010/group-029 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 029',
     'TC-D10-007', 'Completed', ''],
    ['RTM-D10-008', 'REQ-D0010-008',
     'Group 030: Meter Register ID, Read DateTime, Read Value (NUMBER 9,1), Reading Method - mandatory; optional fields as defined',
     'Config: D0010/group-030 + FN_VALIDATE_FIELD precision/scale check',
     'MDQ_ETL_VALIDATION_CONFIG -> group 030',
     'TC-D10-008', 'Completed', 'Precision/scale via FN_VALIDATE_FIELD'],
    ['RTM-D10-009', 'REQ-D0010-009',
     'Group 032: Read Reason Code (2 chars, mandatory), Read Status (1 char, mandatory)',
     'Config: D0010/group-032 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 032',
     'TC-D10-009', 'Completed', ''],
    ['RTM-D10-010', 'REQ-D0010-010',
     'Group 033: Site Visit Check (2 chars, mandatory), Additional Info (optional)',
     'Config: D0010/group-033 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 033',
     'TC-D10-010', 'Completed', ''],
    ['RTM-D10-011', 'REQ-D0010-011',
     'Each D0010 file must contain at least one group 026 (parent group)',
     'FN_VALIDATE_STAGE1 - minimum parent group check',
     'FN_VALIDATE_STAGE1 -> ERR-106',
     'TC-D10-011', 'Completed', 'Stage 1 - no parent = file rejected'],
    ['RTM-D10-012', 'REQ-D0010-012',
     'Group 026 failure: reject all descendants (027, 028, 029, 030, 032, 033)',
     'Hierarchical Logic - v_026_valid = FALSE cascades',
     'Boolean flag cascade: v_026_valid',
     'TC-D10-012', 'Completed', ''],
    ['RTM-D10-013', 'REQ-D0010-013',
     'Group 028 failure: reject 028 descendants; 026 and 027 remain staged',
     'Hierarchical Logic - v_028_valid = FALSE; 026 unaffected',
     'Boolean flag: v_028_valid',
     'TC-D10-013', 'Completed', 'Partial acceptance demonstrated'],
    ['RTM-D10-014', 'REQ-D0010-014',
     'Group 030 failure: reject 032 and 033; all ancestors remain staged',
     'Hierarchical Logic - v_030_valid = FALSE; 028 and 026 unaffected',
     'Boolean flag: v_030_valid',
     'TC-D10-014', 'Completed', ''],
]
add_rtm_table(d0010_rows)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 5. D0150 FUNCTIONAL REQUIREMENTS
# ════════════════════════════════════════════════════════════════════════════
add_h1('5. D0150 Functional Requirements Traceability')
add_body(
    'Traceability for D0150 (Non Half Hourly Meter Technical Details) flow processing requirements, '
    'covering file structure, data elements (9 group types), and hierarchical validation rules.'
)

d0150_rows = [
    ['RTM-D150-001', 'REQ-D0150-001',
     'Process D0150 v002 files: ZHV header, groups 288/289/290/291/293/295/296/762/08A, ZPT footer',
     'PKG_DTC_D0150 - PRC_PROCESS_FILE_V2', 'PRC_PROCESS_FILE_V2',
     'TC-D150-001', 'Completed', ''],
    ['RTM-D150-002', 'REQ-D0150-002',
     'Recognise group 288 as parent group (MPAN level)',
     'FN_INSERT_GROUP_288 - parent flag logic', 'FN_INSERT_GROUP_288',
     'TC-D150-002', 'Completed', 'v_288_valid flag initialised here'],
    ['RTM-D150-003', 'REQ-D0150-003',
     'Support D0150 hierarchy: 288 -> 289/762/290/08A -> 291/293/295/296',
     'Hierarchical Validation Logic - D0150 Boolean flags',
     'v_288_valid, v_290_valid',
     'TC-D150-003', 'Completed', ''],
    ['RTM-D150-004', 'REQ-D0150-004',
     'Group 288: MPAN (13 digits), Effective Date (YYYYMMDD), Energisation Status - mandatory',
     'Config: D0150/group-288 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 288',
     'TC-D150-004', 'Completed', ''],
    ['RTM-D150-005', 'REQ-D0150-005',
     'Group 289: SSC ID (4 chars, mandatory), SSC Effective Date (YYYYMMDD, mandatory)',
     'Config: D0150/group-289 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 289',
     'TC-D150-005', 'Completed', 'PRC_INSERT_GROUP_289'],
    ['RTM-D150-006', 'REQ-D0150-006',
     'Group 290: Meter ID, Current Rating, Location, Make/Type, Asset Provider ID, Retrieval Method (mandatory); 19 optional fields',
     'Config: D0150/group-290 field rules (25 total fields)',
     'MDQ_ETL_VALIDATION_CONFIG -> group 290',
     'TC-D150-006', 'Completed', 'FN_INSERT_GROUP_290'],
    ['RTM-D150-007', 'REQ-D0150-007',
     'Group 291: CT Ratio (1-6 chars, mandatory)',
     'Config: D0150/group-291 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 291',
     'TC-D150-007', 'Completed', 'PRC_INSERT_GROUP_291 (not staged per TDD)'],
    ['RTM-D150-008', 'REQ-D0150-008',
     'Group 293: Meter Register ID, Type, MQ ID, Multiplier (NUMBER 9,2), Digit Count - mandatory',
     'Config: D0150/group-293 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 293',
     'TC-D150-008', 'Completed', 'PRC_INSERT_GROUP_293'],
    ['RTM-D150-009', 'REQ-D0150-009',
     'Group 295: Channel Number, MQ ID, Pulse Multiplier (NUMBER 9,6) - all optional',
     'Config: D0150/group-295 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 295',
     'TC-D150-009', 'Completed', 'PRC_INSERT_GROUP_295 (not staged per TDD)'],
    ['RTM-D150-010', 'REQ-D0150-010',
     'Group 296: Maintenance Date (YYYYMMDD, mandatory), Maintenance Description (1-200 chars, mandatory)',
     'Config: D0150/group-296 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 296',
     'TC-D150-010', 'Completed', 'PRC_INSERT_GROUP_296 (not staged per TDD)'],
    ['RTM-D150-011', 'REQ-D0150-011',
     'Group 762: Maintenance Date (YYYYMMDD, mandatory), Maintenance Description (1-200 chars, mandatory)',
     'Config: D0150/group-762 field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 762',
     'TC-D150-011', 'Completed', 'PRC_INSERT_GROUP_762'],
    ['RTM-D150-012', 'REQ-D0150-012',
     'Group 08A: Meter ID (1-10 chars), Removal Date (YYYYMMDD), Asset Provider ID (1-4 chars) - all mandatory',
     'Config: D0150/group-08A field rules',
     'MDQ_ETL_VALIDATION_CONFIG -> group 08A',
     'TC-D150-012', 'Completed', 'PRC_INSERT_GROUP_08A'],
    ['RTM-D150-013', 'REQ-D0150-013',
     'Each D0150 file must contain at least one group 288',
     'FN_VALIDATE_STAGE1 - minimum parent group check',
     'FN_VALIDATE_STAGE1 -> ERR-106',
     'TC-D150-013', 'Completed', 'Stage 1 - no 288 = file rejected'],
    ['RTM-D150-014', 'REQ-D0150-014',
     'Group 288 failure: reject all descendants (289, 290, 762, 08A and their children)',
     'Hierarchical Logic - v_288_valid = FALSE cascades',
     'Boolean flag cascade: v_288_valid',
     'TC-D150-014', 'Completed', ''],
    ['RTM-D150-015', 'REQ-D0150-015',
     'Group 290 failure: reject 291/293/295/296; group 288 and valid siblings remain staged',
     'Hierarchical Logic - v_290_valid = FALSE; 288 unaffected',
     'Boolean flag: v_290_valid',
     'TC-D150-015', 'Completed', 'Partial acceptance for D0150'],
]
add_rtm_table(d0150_rows)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 6. TECHNICAL REQUIREMENTS
# ════════════════════════════════════════════════════════════════════════════
add_h1('6. Technical Requirements Traceability')

tech_rows = [
    ['RTM-T-001', 'REQ-TECH-001',
     'JSON-based validation configuration stored in the database',
     'MDQ_ETL_VALIDATION_CONFIG table - JSON CLOB column',
     'MDQ_ETL_VALIDATION_CONFIG',
     'TC-T-001', 'Completed', 'Retrieved via FN_GET_ACTIVE_CONFIG'],
    ['RTM-T-002', 'REQ-TECH-002',
     'Retrieve active configuration from MDQ_ETL_VALIDATION_CONFIG table',
     'FN_GET_ACTIVE_CONFIG - queries active version by flow type',
     'FN_GET_ACTIVE_CONFIG',
     'TC-T-002', 'Completed', ''],
    ['RTM-T-003', 'REQ-TECH-003',
     'Config must include: flow type, version, header/footer fields, group definitions with parent-child relationships and field validation rules',
     'JSON structure: flowType, version, headerFields, footerFields, groups[]',
     'MDQ_ETL_VALIDATION_CONFIG',
     'TC-T-003', 'Completed', 'Config-driven; no code change for rule updates'],
    ['RTM-T-004', 'REQ-TECH-004',
     'Insert validated data into staging tables: 7 D0010 tables + 9 D0150 tables',
     'FN/PRC_INSERT_GROUP_XXX procedures',
     'STAGE_D0010_026..033 / STAGE_D0150_288..08A',
     'TC-T-004', 'Completed', '16 staging tables total'],
    ['RTM-T-005', 'REQ-TECH-005',
     'No schema changes to staging tables; staging logic identical to existing Datastage process',
     'Same INSERT column lists as existing Datastage jobs',
     'Existing STAGE_DXXxx table DDLs',
     'TC-T-005', 'Completed', 'Verified against Datastage column mapping'],
    ['RTM-T-006', 'REQ-TECH-006',
     'Full ROLLBACK if unexpected error occurs during processing',
     'Exception block in PRC_PROCESS_FILE_V2 - ROLLBACK on unhandled exception',
     'EXCEPTION block -> ROLLBACK',
     'TC-T-006', 'Completed', 'COMMIT only after successful staging'],
    ['RTM-T-007', 'REQ-TECH-007',
     'Structured validation result: status (REJECTED/STAGING), count statistics, error collection, parent group ranges',
     'T_VALIDATION_RESULT composite type in PKG_DTC_VALIDATION',
     'T_VALIDATION_RESULT type',
     'TC-T-007', 'Completed', 'Returned from FN_VALIDATE_STAGE1/2'],
    ['RTM-T-008', 'REQ-TECH-008',
     'Seamless Datastage-GoAnywhere handoff with failure recovery and simplified support tasks',
     'EWAY Changes section - GoAnywhere trigger configuration',
     'GoAnywhere job + EWAY interface',
     'TC-T-008', 'In Progress', 'Handoff mechanism design in progress'],
]
add_rtm_table(tech_rows)

# ════════════════════════════════════════════════════════════════════════════
# 7. NON-FUNCTIONAL REQUIREMENTS
# ════════════════════════════════════════════════════════════════════════════
add_h1('7. Non-Functional Requirements Traceability')

nfr_rows = [
    ['RTM-NFR-001', 'REQ-NFR-001',
     'Generic validation package (PKG_DTC_VALIDATION) reusable across multiple flow types without code changes',
     'PKG_DTC_VALIDATION - generic design; flow type passed as parameter',
     'PKG_DTC_VALIDATION',
     'TC-NFR-001', 'Completed', 'New flows added via config only'],
    ['RTM-NFR-002', 'REQ-NFR-002',
     'Externalise validation rules in JSON configuration - changes allowed without code modifications',
     'MDQ_ETL_VALIDATION_CONFIG - JSON config pattern',
     'MDQ_ETL_VALIDATION_CONFIG',
     'TC-NFR-002', 'Completed', 'Maintainability design principle confirmed'],
    ['RTM-NFR-003', 'REQ-NFR-003',
     'Audit and error tables consistent with existing Datastage ETL framework (ETL_FILE, AUDIT, ERROR)',
     'WRITE_AUDIT / WRITE_ERROR / WRITE_FILE_TABLE procedures',
     'MDQ_ETL_AUDIT / MDQ_ETL_ERROR / MDQ_ETL_FILE',
     'TC-NFR-003', 'Completed', 'Same structure as Datastage framework'],
    ['RTM-NFR-004', 'REQ-NFR-004',
     'Processing performance significantly improved vs existing Datastage staging',
     'Layered Oracle PL/SQL architecture eliminates Datastage overhead',
     'PRC_PROCESS_FILE_V2 (native Oracle)',
     'TC-NFR-004', 'In Progress', 'Benchmark target TBD; baseline from Datastage run logs'],
]
add_rtm_table(nfr_rows)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 8. COVERAGE SUMMARY
# ════════════════════════════════════════════════════════════════════════════
add_h1('8. Traceability Coverage Summary')
add_body(
    'Consolidated view of traceability coverage across all requirement categories, giving '
    'stakeholders a quick health-check of SDLC status.'
)

sum_tbl = doc.add_table(rows=7, cols=5)
sum_tbl.style = 'Table Grid'
for j, hdr in enumerate(['Requirement Category', 'Total', 'Completed', 'In Progress', 'Not Started']):
    set_cell_bg(sum_tbl.cell(0, j), DARK_BLUE)
    bold_para(sum_tbl.cell(0, j), hdr, font_size=9, color=WHITE)

summary_data = [
    ['Business Requirements (REQ-001 to REQ-011)', '11', '11', '0', '0'],
    ['D0010 Functional Requirements (REQ-D0010-001 to 014)', '14', '14', '0', '0'],
    ['D0150 Functional Requirements (REQ-D0150-001 to 015)', '15', '15', '0', '0'],
    ['Technical Requirements (REQ-TECH-001 to 008)', '8', '7', '1', '0'],
    ['Non-Functional Requirements (REQ-NFR-001 to 004)', '4', '3', '1', '0'],
    ['TOTAL', '52', '50', '2', '0'],
]
for i, row_data in enumerate(summary_data):
    is_total = (i == 5)
    bg = DARK_BLUE if is_total else (ALT_ROW if i % 2 == 1 else WHITE)
    fc = WHITE if is_total else BLACK
    for j, val in enumerate(row_data):
        cell = sum_tbl.cell(i + 1, j)
        set_cell_bg(cell, bg)
        align = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
        p = cell.paragraphs[0]
        p.alignment = align
        run = p.add_run(val)
        run.font.size = Pt(9)
        run.font.color.rgb = fc
        if is_total:
            run.bold = True

doc.add_paragraph()
note = doc.add_paragraph()
r1 = note.add_run('Coverage: ')
r1.bold = True
r1.font.size = Pt(9)
r2 = note.add_run(
    '50 of 52 requirements (96%) have a confirmed technical design component and are Completed. '
    '2 requirements are In Progress: REQ-TECH-008 (GoAnywhere handoff design) and '
    'REQ-NFR-004 (performance benchmark). These will be updated once design is finalised.'
)
r2.font.size = Pt(9)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# 9. GUIDE FOR JUNIOR DEVELOPERS
# ════════════════════════════════════════════════════════════════════════════
add_h1('9. Guide for Junior Developers - Reading the RTM')

sections = [
    ('What is an RTM?',
     'An RTM is a document that links every requirement to the part of the system that implements '
     'it and the test case that proves it works. Think of it as a chain: Business Need (BRD) -> '
     'Design Decision (TDD) -> Code Component (Package/Table) -> Proof (Test Case). If any link '
     'in the chain is missing, the requirement has a gap.'),
    ('Why is the RTM produced in Phase 1 of Waterfall SDLC?',
     'In a Waterfall SDLC, Phase 1 (Planning & Requirements) ends with a Requirements Freeze. '
     'At that point you create the RTM shell with all BRD requirement IDs filled in. The TDD '
     'columns get filled in Phase 2 (System Design). Test Case IDs are added in Phase 3 '
     '(Testing). Statuses move from Not Started to Verified as each phase completes. '
     'A fully Verified RTM is the gatekeeper before Phase 5 (Deployment).'),
    ('How to use this RTM when picking up a task',
     'Find the RTM ID for your assigned BRD requirement. The row tells you: WHAT to build '
     '(Requirement Description), WHERE to build it (TDD Design Component + DB/Package Reference), '
     'and HOW to prove it works (Test Case ID). Update Status to In Progress when you start, '
     'Completed when your unit tests pass, and Verified once QA signs it off.'),
    ('What does each Status value mean?',
     'Not Started: requirement acknowledged but design and build have not begun. '
     'In Progress: design or build is underway. '
     'Completed: build is done and developer unit tests pass. '
     'Verified: the linked test case passed formal QA/UAT sign-off.'),
    ('A concrete example - tracing REQ-001 end-to-end',
     'BRD says (REQ-001): the system SHALL accept pipe-delimited D0010/D0150 files. '
     'TDD responds: PRC_PROCESS_FILE_V2 is the main entry-point procedure in PKG_DTC_D0010 '
     'and PKG_DTC_D0150. RTM row RTM-B-001 is the single source of truth joining them. '
     'Test case TC-B-001 then proves the procedure correctly parses a valid sample file. '
     'When TC-B-001 passes in QA, RTM-B-001 Status moves to Verified - requirement is done.'),
    ('What happens if a requirement has no TDD or Test Case reference?',
     'A blank TDD Design Component column means the requirement has not been designed yet - '
     'flag it to the Tech Lead. A blank Test Case ID means it cannot be formally signed off '
     'even if the code exists. Both are blockers to Deployment in a Waterfall SDLC. The RTM '
     'is the tool that makes these gaps visible early, before they become production defects.'),
]
for title, body in sections:
    add_h2(title)
    add_body(body)

# Footer
doc.add_paragraph()
fp = doc.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = fp.add_run('MAVIS Faster Staging  |  Requirements Traceability Matrix v1.0  |  MHHS Programme  |  Confidential  |  14-01-2026')
fr.font.size = Pt(7.5)
fr.font.color.rgb = GREY
fr.italic = True

doc.save('MHHS Faster Staging RTM v1.0.docx')
print('RTM document saved successfully: MHHS Faster Staging RTM v1.0.docx')
