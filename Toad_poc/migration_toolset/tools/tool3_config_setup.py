"""
Tool 3 - Config Schema + Data Setup
=====================================
Creates the config schema DDL (shared, run once) and per-report INSERT scripts.
Reads the sanitised Toad XML to extract:
  - Email distribution lists (To/Cc/Bcc per SendEmailActivity)
  - SQL queries (ODS check + main report) translated to T-SQL
  - Excel template filename and blob storage path

config.report       : one row per report (name, pipeline, schedule, template info)
config.report_email : email distribution list per report
config.report_sql   : SQL queries per report (ods_check, report_main)

Two modes:
  default  : uses mock emails extracted from sanitised XML (emailid@company.com)
  --poc    : uses dev team emails from global/poc_team_config.json
             allows real end-to-end pipeline testing without client email addresses

Input  : reports/{report}/sanitized/{report}_sanitized.txt
       : global/poc_team_config.json  (only in --poc mode)
Output : global/config/config_schema_ddl.sql   (idempotent DDL, created once)
       : reports/{report}/config/{report}_config_data.sql  (idempotent INSERTs)

Usage:
  python tool3_config_setup.py <report_name> [-v]
  python tool3_config_setup.py BC_BIMIO_267_Daily
  python tool3_config_setup.py BC_BIMIO_267_Daily -v
"""

import argparse
import json
import os
import re
import sys

BASE_DIR        = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORTS_DIR     = os.path.join(BASE_DIR, 'reports')
GLOBAL_DIR      = os.path.join(BASE_DIR, 'global')
POC_CONFIG_PATH = os.path.join(GLOBAL_DIR, 'poc_team_config.json')


# ─────────────────────────────────────────────────────────────────────────────
# XML helpers
# ─────────────────────────────────────────────────────────────────────────────

def _decode(text):
    return (text
            .replace('&#xD;&#xA;', '\n').replace('&#xD;', '\r').replace('&#xA;', '\n')
            .replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"'))


def _attr(attrs_str, name):
    """Extract an attribute value from a raw attributes string."""
    m = re.search(rf'\b{re.escape(name)}="([^"]*)"', attrs_str, re.IGNORECASE)
    return m.group(1).strip() if m else ''


def _split_emails(s):
    return [e.strip() for e in re.split(r'[;,]', s) if e.strip() and '@' in e]


# ─────────────────────────────────────────────────────────────────────────────
# Oracle / Redshift → T-SQL translator  (mirrors tool2_adf_generator.py)
# ─────────────────────────────────────────────────────────────────────────────

def translate_sql(sql):
    """Basic Oracle/Redshift → T-SQL translation for common Toad patterns."""
    if not sql:
        return sql
    sql = re.sub(r'\bSYSDATE\b', 'GETDATE()', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\btrunc\s*\(((?:[^()]+|\([^()]*\))+)\)',
                 lambda m: f'CAST({m.group(1).strip()} AS DATE)',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"date_add\s*\(\s*'day'\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEADD(DAY, {m.group(1).strip()}, {m.group(2).strip()})',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"date_add\s*\(\s*'month'\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEADD(MONTH, {m.group(1).strip()}, {m.group(2).strip()})',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"date_trunc\s*\(\s*'month'\s*,\s*([^)]+?)\s*\)",
                 lambda m: (f'DATEFROMPARTS(YEAR({m.group(1).strip()}), '
                            f'MONTH({m.group(1).strip()}), 1)'),
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"date_trunc\s*\(\s*'year'\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEFROMPARTS(YEAR({m.group(1).strip()}), 1, 1)',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"date_trunc\s*\(\s*'day'\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'CAST({m.group(1).strip()} AS DATE)',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bDATEDIFF\s*\(\s*minutes\s*,', 'DATEDIFF(MINUTE,', sql, flags=re.IGNORECASE)
    sql = re.sub(r'::\s*TIMESTAMP\b', ' AS DATETIME2', sql, flags=re.IGNORECASE)
    sql = re.sub(r'::\s*DATE\b', ' AS DATE', sql, flags=re.IGNORECASE)
    sql = re.sub(r"to_date\s*\(\s*([^,]+?)\s*,\s*'dd/mm/yyyy'\s*\)",
                 lambda m: f'CONVERT(DATE, {m.group(1).strip()}, 103)',
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r"DECODE\s*\(\s*([^,]+?)\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([^)]+?)\s*\)",
                 lambda m: (f"CASE WHEN {m.group(1).strip()} = '{m.group(2)}' "
                            f"THEN '{m.group(3)}' ELSE {m.group(4).strip()} END"),
                 sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bdate\s*\(\s*(CONVERT\([^)]+\))\s*\)',
                 lambda m: f'CAST({m.group(1)} AS DATE)',
                 sql, flags=re.IGNORECASE)
    return sql


# ─────────────────────────────────────────────────────────────────────────────
# SQL query extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_sql_queries(raw, decoded):
    """
    Extract and translate ODS check + main report SQL from the XML.
    raw     : original file content (pre-decode, for attribute scanning)
    decoded : entity-decoded content
    Returns dict: { 'ODS_CHECK': str, 'REPORT_MAIN': str }
    """
    queries = {}

    # ODS check -- first SelectDataActivity
    ods_m = re.search(r'<ta1:SelectDataActivity[^>]+SqlScriptEmbed="([^"]+)"', raw)
    if ods_m:
        ods_raw = _decode(ods_m.group(1)).strip()
        ods_sql = translate_sql(ods_raw)
        # Ensure scalar result for ADF Lookup
        ods_sql = re.sub(r'^\s*SELECT\s+\*', 'SELECT COUNT(*) AS row_count',
                         ods_sql, flags=re.IGNORECASE)
        queries['ODS_CHECK'] = ods_sql
    else:
        queries['ODS_CHECK'] = 'SELECT 1 AS row_count'

    # Main report SQL -- SelectToExcelActivity
    rpt_m = re.search(r'<ta1:SelectToExcelActivity[^>]+SqlScriptEmbed="([^"]+)"', raw, re.DOTALL)
    if rpt_m:
        rpt_raw = _decode(rpt_m.group(1)).strip()
        lines = [l for l in rpt_raw.splitlines() if not l.strip().startswith('--')]
        rpt_sql = translate_sql('\n'.join(lines).strip())
        queries['REPORT_MAIN'] = rpt_sql

    return queries


# ─────────────────────────────────────────────────────────────────────────────
# Template file extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_template_info(decoded, report_name):
    """
    Extract the xlsm template filename from CopyFileActivity or FileDescription.
    Returns (template_name, template_blob_path) or ('', '') if not found.
    Blob path convention: templates/{report_name}/{filename}
    """
    fname = ''

    # 1. CopyFileActivity DestinationFileName (most reliable)
    for m in re.finditer(
            r'CopyFileActivity[^>]*DestinationFileName="([^"]*\.xlsm)"',
            decoded, re.IGNORECASE | re.DOTALL):
        fname = os.path.basename(m.group(1))
        break

    if not fname:
        for m in re.finditer(
                r'CopyFileActivity[^>]*SourceFileName="[^"]*"[^>]*DestinationFileName="([^"]*\.xlsm)"',
                decoded, re.IGNORECASE | re.DOTALL):
            fname = os.path.basename(m.group(1))
            break

    # 2. FileDescription
    if not fname:
        for m in re.finditer(
                r'FileDescription[^>]*Description="(?:Copy_\d+:\s*)?([^"]*\.xlsm)"',
                decoded, re.IGNORECASE):
            fname = os.path.basename(m.group(1).strip())
            if fname:
                break

    if not fname:
        return '', ''

    blob_path = f'templates/{report_name}/{fname}'
    return fname, blob_path


# ─────────────────────────────────────────────────────────────────────────────
# Email activity extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_email_activities(decoded):
    """
    Return list of dicts, one per SendEmailActivity:
      name, subject, to, cc, bcc  (to/cc/bcc are lists of email strings)
    """
    # Match the opening tag -- may span several lines due to many attributes
    pattern = re.compile(
        r'<(?:ta[01]:)?SendEmailActivity\s(.*?)(?:/>|>)',
        re.DOTALL | re.IGNORECASE
    )
    results = []
    for m in pattern.finditer(decoded):
        attrs = m.group(1)
        results.append({
            'name':    _attr(attrs, 'x:Name'),
            'subject': _attr(attrs, 'Subject'),
            'to':      _split_emails(_attr(attrs, 'To')),
            'cc':      _split_emails(_attr(attrs, 'Cc')),
            'bcc':     _split_emails(_attr(attrs, 'Bcc')),
        })
    return results


def classify_email_groups(activities):
    """
    Map SendEmailActivity recipients to config recipient groups.

    Groups needed by ADF pipeline:
      OPERATIONS / TO   -- main report recipients
      ALERT_ONLY / CC   -- CC on main email; also receive ODS-not-refreshed alert
      BI_TEAM    / BCC  -- BCC on main email; receive confirmation

    Heuristic:
      - Activity with most To recipients = main report email
      - Its To  -> OPERATIONS / TO
      - Its Cc  -> ALERT_ONLY / CC
      - Its Bcc -> BI_TEAM    / BCC
      - Any remaining activities with To/Cc/Bcc that are not already captured
        are added to OPERATIONS as a fallback.
    """
    if not activities:
        return {}

    # Find the main report email (most To recipients; skip pure error/exception emails)
    non_error = [a for a in activities
                 if 'Error' not in a['subject'] and 'Exception' not in a['name']]
    candidates = non_error if non_error else activities

    main = max(candidates, key=lambda a: len(a['to']), default=candidates[0])

    groups = {}  # email -> (recipient_group, email_type)

    def _add(emails, group, etype):
        for e in emails:
            if e and e not in groups:
                groups[e] = (group, etype)

    _add(main['to'],  'OPERATIONS', 'TO')
    _add(main['cc'],  'ALERT_ONLY', 'CC')
    _add(main['bcc'], 'BI_TEAM',    'BCC')

    # Remaining activities -- add any new addresses not already classified
    for act in activities:
        if act is main:
            continue
        is_error = 'Error' in act['subject'] or 'Exception' in act['name']
        fallback_group = 'ALERT_ONLY' if is_error else 'OPERATIONS'
        _add(act['to'],  fallback_group, 'TO')
        _add(act['cc'],  'ALERT_ONLY',   'CC')
        _add(act['bcc'], 'BI_TEAM',      'BCC')

    return groups


# ─────────────────────────────────────────────────────────────────────────────
# Report metadata extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_report_metadata(decoded, report_name):
    """Return dict of report-level metadata for config.report INSERT."""
    safe = re.sub(r'[^A-Za-z0-9_]', '_', report_name)

    desc_m = re.search(r'\bDescription="([^"]{5,})"', decoded)
    description = desc_m.group(1)[:200] if desc_m else report_name

    container = safe.lower().replace('_', '-')
    template_name, template_blob_path = extract_template_info(decoded, report_name)

    return {
        'report_name':        report_name,
        'pipeline_name':      f'PL_{safe}',
        'description':        description,
        'schedule_time':      '06:00',
        'output_container':   container,
        'template_name':      template_name,
        'template_blob_path': template_blob_path,
        'is_active':          'Y',
    }


# ─────────────────────────────────────────────────────────────────────────────
# SQL generators
# ─────────────────────────────────────────────────────────────────────────────

def _sq(s):
    """Escape single quotes for SQL string literals."""
    return s.replace("'", "''")


CONFIG_SCHEMA_DDL = """\
-- ============================================================
-- config schema DDL  (Tool 3 output -- run once per environment)
-- Idempotent: safe to re-run.
-- ============================================================

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'config')
    EXEC('CREATE SCHEMA [config]');
GO

-- ── config.report ─────────────────────────────────────────────
IF OBJECT_ID('config.report', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report]
    (
        [report_id]          INT          IDENTITY(1,1) NOT NULL,
        [report_name]        VARCHAR(200) NOT NULL,
        [pipeline_name]      VARCHAR(200) NOT NULL,
        [description]        VARCHAR(500) NULL,
        [schedule_time]      VARCHAR(10)  NOT NULL CONSTRAINT [DF_report_schedule] DEFAULT '06:00',
        [output_container]   VARCHAR(100) NOT NULL,
        [template_name]      VARCHAR(500) NULL,
        [template_blob_path] VARCHAR(500) NULL,
        [is_active]          CHAR(1)      NOT NULL CONSTRAINT [DF_report_active]   DEFAULT 'Y',
        CONSTRAINT [PK_report]      PRIMARY KEY ([report_id]),
        CONSTRAINT [UQ_report_name] UNIQUE      ([report_name])
    );
END
ELSE
BEGIN
    -- Add template columns if upgrading from older schema version
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'template_name')
        ALTER TABLE [config].[report] ADD [template_name] VARCHAR(500) NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'template_blob_path')
        ALTER TABLE [config].[report] ADD [template_blob_path] VARCHAR(500) NULL;
END
GO

-- ── config.report_email ───────────────────────────────────────
IF OBJECT_ID('config.report_email', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report_email]
    (
        [email_id]        INT          IDENTITY(1,1) NOT NULL,
        [report_id]       INT          NOT NULL,
        [email_address]   VARCHAR(200) NOT NULL,
        [recipient_group] VARCHAR(50)  NOT NULL,
        [email_type]      VARCHAR(10)  NOT NULL,
        [is_active]       CHAR(1)      NOT NULL CONSTRAINT [DF_report_email_active] DEFAULT 'Y',
        CONSTRAINT [PK_report_email] PRIMARY KEY ([email_id]),
        CONSTRAINT [FK_report_email_report]
            FOREIGN KEY ([report_id]) REFERENCES [config].[report] ([report_id])
    );
END
GO

-- ── config.report_sql ────────────────────────────────────────
IF OBJECT_ID('config.report_sql', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report_sql]
    (
        [sql_id]       INT           IDENTITY(1,1) NOT NULL,
        [report_id]    INT           NOT NULL,
        [query_type]   VARCHAR(50)   NOT NULL,   -- ODS_CHECK | REPORT_MAIN
        [query_text]   NVARCHAR(MAX) NOT NULL,
        [is_active]    CHAR(1)       NOT NULL CONSTRAINT [DF_report_sql_active] DEFAULT 'Y',
        CONSTRAINT [PK_report_sql] PRIMARY KEY ([sql_id]),
        CONSTRAINT [UQ_report_sql_type]
            UNIQUE ([report_id], [query_type]),
        CONSTRAINT [FK_report_sql_report]
            FOREIGN KEY ([report_id]) REFERENCES [config].[report] ([report_id])
    );
END
GO
"""


def build_data_sql(meta, email_groups, sql_queries, verbose=False):
    """
    Return per-report INSERT SQL (idempotent).
    meta        : dict from extract_report_metadata()
    email_groups: dict from classify_email_groups()  { email -> (group, type) }
    sql_queries : dict from extract_sql_queries()    { 'ODS_CHECK': str, 'REPORT_MAIN': str }
    """
    lines = []
    rn = meta['report_name']

    lines.append(f"-- ============================================================")
    lines.append(f"-- config data for report: {rn}")
    lines.append(f"-- Tool 3 output -- idempotent, safe to re-run.")
    lines.append(f"-- ============================================================")
    lines.append("")
    lines.append("DECLARE @report_id INT;")
    lines.append("")

    # config.report INSERT
    lines.append(f"-- ── config.report ──────────────────────────────────────────")
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM config.report WHERE report_name = '{_sq(rn)}')")
    lines.append(f"BEGIN")
    lines.append(f"    INSERT INTO config.report")
    lines.append(f"        (report_name, pipeline_name, description, schedule_time,")
    lines.append(f"         output_container, template_name, template_blob_path, is_active)")
    lines.append(f"    VALUES (")
    lines.append(f"        '{_sq(rn)}',")
    lines.append(f"        '{_sq(meta['pipeline_name'])}',")
    lines.append(f"        '{_sq(meta['description'])}',")
    lines.append(f"        '{meta['schedule_time']}',")
    lines.append(f"        '{meta['output_container']}',")
    tname = 'NULL' if not meta['template_name'] else f"'{_sq(meta['template_name'])}'"
    tblob = 'NULL' if not meta['template_blob_path'] else f"'{_sq(meta['template_blob_path'])}'"
    lines.append(f"        {tname},")
    lines.append(f"        {tblob},")
    lines.append(f"        '{meta['is_active']}'")
    lines.append(f"    );")
    lines.append(f"END")
    lines.append(f"ELSE")
    lines.append(f"BEGIN")
    lines.append(f"    -- Update template info if it was added later")
    if meta['template_name']:
        lines.append(f"    UPDATE config.report")
        lines.append(f"    SET    template_name      = '{_sq(meta['template_name'])}',")
        lines.append(f"           template_blob_path = '{_sq(meta['template_blob_path'])}'")
        lines.append(f"    WHERE  report_name = '{_sq(rn)}';")
    else:
        lines.append(f"    -- No template detected in sanitised XML; skipping update.")
    lines.append(f"END")
    lines.append(f"SET @report_id = (SELECT report_id FROM config.report WHERE report_name = '{_sq(rn)}');")
    lines.append("")

    # config.report_sql INSERTs
    lines.append(f"-- ── config.report_sql ──────────────────────────────────────")
    if not sql_queries:
        lines.append("-- No SQL queries found in sanitised XML.")
    else:
        for qtype, qtext in sql_queries.items():
            safe_sql = qtext.replace("'", "''")
            lines.append(f"IF NOT EXISTS (SELECT 1 FROM config.report_sql")
            lines.append(f"              WHERE report_id = @report_id AND query_type = '{qtype}')")
            lines.append(f"    INSERT INTO config.report_sql (report_id, query_type, query_text, is_active)")
            lines.append(f"    VALUES (@report_id, '{qtype}', N'{safe_sql}', 'Y');")
            lines.append(f"ELSE")
            lines.append(f"    UPDATE config.report_sql")
            lines.append(f"    SET    query_text = N'{safe_sql}', is_active = 'Y'")
            lines.append(f"    WHERE  report_id = @report_id AND query_type = '{qtype}';")
            lines.append("")
            if verbose:
                preview = qtext[:80].replace('\n', ' ')
                print(f'      {qtype:<15}  {preview}...')

    # config.report_email INSERTs
    lines.append(f"-- ── config.report_email ────────────────────────────────────")
    if not email_groups:
        lines.append("-- No email addresses found in sanitised XML.")
    else:
        for email, (group, etype) in sorted(email_groups.items(), key=lambda x: (x[1][0], x[1][1])):
            lines.append(
                f"IF NOT EXISTS (SELECT 1 FROM config.report_email "
                f"WHERE report_id = @report_id "
                f"AND email_address = '{_sq(email)}' "
                f"AND recipient_group = '{group}')"
            )
            lines.append(f"    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)")
            lines.append(f"    VALUES (@report_id, '{_sq(email)}', '{group}', '{etype}', 'Y');")
            if verbose:
                print(f'      {group:<15} {etype:<5} {email}')

    lines.append("")
    lines.append(f"-- ── verify ─────────────────────────────────────────────────")
    lines.append(f"SELECT r.report_name, r.template_name, r.template_blob_path")
    lines.append(f"FROM   config.report r")
    lines.append(f"WHERE  r.report_name = '{_sq(rn)}';")
    lines.append("")
    lines.append(f"SELECT rs.query_type, LEFT(rs.query_text, 100) AS query_preview")
    lines.append(f"FROM   config.report_sql rs")
    lines.append(f"JOIN   config.report r ON r.report_id = rs.report_id")
    lines.append(f"WHERE  r.report_name = '{_sq(rn)}';")
    lines.append("")
    lines.append(f"SELECT r.report_name, re.recipient_group, re.email_type, re.email_address")
    lines.append(f"FROM   config.report r")
    lines.append(f"JOIN   config.report_email re ON re.report_id = r.report_id")
    lines.append(f"WHERE  r.report_name = '{_sq(rn)}'")
    lines.append(f"ORDER  BY re.recipient_group, re.email_type, re.email_address;")
    lines.append("")

    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# POC team email loader
# ─────────────────────────────────────────────────────────────────────────────

def load_poc_email_groups():
    """
    Read poc_team_config.json and return email_groups dict
    in the same format as classify_email_groups():
      { email_address -> (recipient_group, email_type) }
    """
    if not os.path.exists(POC_CONFIG_PATH):
        print(f'ERROR: poc_team_config.json not found at {POC_CONFIG_PATH}')
        print('Create it with your dev team email addresses before using --poc mode.')
        sys.exit(1)

    with open(POC_CONFIG_PATH, encoding='utf-8') as f:
        config = json.load(f)

    entries = config.get('poc_team_emails', [])
    if not entries:
        print('ERROR: poc_team_emails list is empty in poc_team_config.json')
        sys.exit(1)

    return {e['email']: (e['group'], e['type']) for e in entries}


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def generate_config(report_name, verbose=False, poc=False):
    xml_path   = os.path.join(REPORTS_DIR, report_name, 'sanitized', f'{report_name}_sanitized.txt')
    config_dir = os.path.join(REPORTS_DIR, report_name, 'config')
    global_cfg = os.path.join(GLOBAL_DIR, 'config')
    schema_ddl = os.path.join(global_cfg, 'config_schema_ddl.sql')
    data_sql   = os.path.join(config_dir, f'{report_name}_config_data.sql')

    if not os.path.exists(xml_path):
        print(f'Sanitised XML not found: {xml_path}')
        print('Run Tool 1 first.')
        sys.exit(1)

    with open(xml_path, encoding='utf-8', errors='replace') as f:
        raw = f.read()
    decoded = _decode(raw)

    # ── Extract ───────────────────────────────────────────────────────────────
    activities  = extract_email_activities(decoded)
    meta        = extract_report_metadata(decoded, report_name)
    sql_queries = extract_sql_queries(raw, decoded)

    if poc:
        email_groups = load_poc_email_groups()
        mode_label   = 'POC (dev team emails from poc_team_config.json)'
    else:
        email_groups = classify_email_groups(activities)
        mode_label   = 'default (mock emails from sanitised XML)'

    print(f'\nTool 3 -- Config Schema + Data Setup')
    print(f'Report    : {report_name}')
    print(f'Mode      : {mode_label}')
    print(f'Pipeline  : {meta["pipeline_name"]}')
    print(f'Container : {meta["output_container"]}')
    print(f'Schedule  : {meta["schedule_time"]}')
    print(f'Template  : {meta["template_name"] or "(not detected)"}')
    if meta['template_blob_path']:
        print(f'Blob path : {meta["template_blob_path"]}')
    print(f'SQL       : {len(sql_queries)} query type(s) extracted ({", ".join(sql_queries.keys())})')
    print(f'Emails    : {len(email_groups)} addresses across '
          f'{len(set(g for g, _ in email_groups.values()))} groups')

    if verbose:
        print('\n  SQL queries:')
        for qtype, qtext in sql_queries.items():
            preview = qtext[:120].replace('\n', ' ')
            print(f'    {qtype:<15}  {preview}')
        print('\n  Email groups:')
        for email, (group, etype) in sorted(email_groups.items(), key=lambda x: (x[1][0], x[1][1])):
            print(f'    {group:<15} {etype:<5}  {email}')

    # ── Write global schema DDL (always regenerate to pick up schema changes) ──
    os.makedirs(global_cfg, exist_ok=True)
    with open(schema_ddl, 'w', encoding='utf-8') as f:
        f.write(CONFIG_SCHEMA_DDL)
    print(f'\n  DDL  {schema_ddl}  (written)')

    # ── Write per-report data SQL ─────────────────────────────────────────────
    os.makedirs(config_dir, exist_ok=True)
    sql = build_data_sql(meta, email_groups, sql_queries, verbose=verbose)
    with open(data_sql, 'w', encoding='utf-8') as f:
        f.write(sql)
    print(f'  SQL  {data_sql}  (written)')

    print(f'\nDone.')
    print(f'Run order:')
    print(f'  1. global/config/config_schema_ddl.sql        (once per environment -- idempotent)')
    print(f'  2. reports/{report_name}/config/{report_name}_config_data.sql  (per report -- idempotent)')


def main():
    ap = argparse.ArgumentParser(description='Tool 3 -- Config Schema + Data Setup')
    ap.add_argument('report', help='Report name (folder under reports/)')
    ap.add_argument('--poc', action='store_true',
                    help='Use dev team emails from poc_team_config.json instead of mock emails')
    ap.add_argument('-v', '--verbose', action='store_true', help='Show email group assignments')
    args = ap.parse_args()
    generate_config(args.report, verbose=args.verbose, poc=args.poc)


if __name__ == '__main__':
    main()
