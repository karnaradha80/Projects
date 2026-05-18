"""
Tool 2 - ADF ARM Template Generator
=====================================
Reads the sanitized Toad XML (Tool 1 output).
Extracts pipeline structure, SQL queries, connections, and email steps.
Translates Oracle/Redshift SQL to T-SQL (basic patterns).
Generates:
  - Linked Service JSONs (Key Vault, Azure SQL, Blob Storage)
  - Dataset JSONs (per SQL table + Blob output/archive + Config)
  - Pipeline JSON  (full activity chain mapped from Toad activities)
  - arm_template.json  (combined deployable ARM template)
  - arm_template_parameters.json  (template -- fill before deploying)

Usage:
  python tool2_adf_generator.py <report_name> [-v]

Input  : reports/{report}/sanitized/{report}_sanitized.txt
Output : reports/{report}/adf/
         linkedServices/  datasets/  pipelines/
         arm_template.json  arm_template_parameters.json
"""

import argparse
import json
import os
import re
import shutil
import sys

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

API_VER = '2018-06-01'


# ─────────────────────────────────────────────────────────────────────────────
# XML entity decoding
# ─────────────────────────────────────────────────────────────────────────────

def _decode(text):
    return (text
            .replace('&#xD;&#xA;', '\n').replace('&#xD;', '\r').replace('&#xA;', '\n')
            .replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"'))


# ─────────────────────────────────────────────────────────────────────────────
# Sanitised XML extractor
# ─────────────────────────────────────────────────────────────────────────────

class ToadXmlExtractor:
    """Pulls structured data out of a sanitised Toad XML file."""

    def __init__(self, xml_path):
        with open(xml_path, encoding='utf-8', errors='replace') as f:
            self.raw = f.read()
        self.decoded = _decode(self.raw)

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def report_name(self):
        m = re.search(r'x:Name="([^"]+)"', self.raw)
        return m.group(1) if m else 'UnknownReport'

    @property
    def description(self):
        m = re.search(r'Description="([^"]+)"', self.raw)
        return m.group(1) if m else ''

    # ── ODS refresh check ─────────────────────────────────────────────────────

    @property
    def ods_check_sql(self):
        """Raw SQL from the first SelectDataActivity (ODS refresh check)."""
        m = re.search(r'<ta1:SelectDataActivity[^>]+SqlScriptEmbed="([^"]+)"', self.raw)
        if not m:
            return 'SELECT 1 AS row_count'
        return _decode(m.group(1)).strip()

    @property
    def ods_table(self):
        """schema.table used in the ODS check query."""
        m = re.search(r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)',
                      self.ods_check_sql, re.IGNORECASE)
        if m:
            return f'{m.group(1)}.{m.group(2)}'
        return 'dbo.ODS_LOG'

    # ── Main report SQL ───────────────────────────────────────────────────────

    @property
    def report_sql_raw(self):
        """SQL from SelectToExcelActivity, decoded but not translated."""
        m = re.search(r'<ta1:SelectToExcelActivity[^>]+SqlScriptEmbed="([^"]+)"',
                      self.raw, re.DOTALL)
        if not m:
            return ''
        sql = _decode(m.group(1)).strip()
        # Drop commented-out aggregation line at the top (common in Toad scripts)
        lines = [l for l in sql.splitlines() if not l.strip().startswith('--')]
        return '\n'.join(lines).strip()

    # ── Output file info ──────────────────────────────────────────────────────

    @property
    def output_file_base(self):
        """Base name for the output CSV/Excel file."""
        # Try BaseFileName inside ExportOptionsXml (double-encoded)
        m = re.search(r'BaseFileName=&quot;([^&]+)&quot;', self.raw)
        if m:
            return m.group(1)
        # Fall back: report name without spaces
        return re.sub(r'\W+', '_', self.report_name)

    @property
    def archive_file_name(self):
        """Destination file name pattern from CopyFileActivity."""
        m = re.search(r'DestinationFileName="([^"]+)"', self.raw)
        return m.group(1) if m else f'{self.report_name}_For_.csv'

    # ── Email subjects ────────────────────────────────────────────────────────

    @property
    def email_subjects(self):
        """All SendEmailActivity subjects in order of appearance."""
        return re.findall(r'Subject="([^"]+)"', self.raw)

    @property
    def email_subject_report(self):
        subjects = [s for s in self.email_subjects if 'Error' not in s]
        return subjects[0] if subjects else f'{self.report_name} - Report'

    @property
    def email_subject_no_data(self):
        subjects = self.email_subjects
        return subjects[0] if subjects else f'{self.report_name} - ODS Not Refreshed'

    @property
    def email_subject_confirm(self):
        subjects = [s for s in self.email_subjects if 'Run' in s or 'Confirm' in s or 'Has Run' in s]
        if subjects:
            return subjects[0]
        all_s = self.email_subjects
        return all_s[-1] if len(all_s) >= 2 else f'{self.report_name} - Pipeline Complete'

    # ── Tables ────────────────────────────────────────────────────────────────

    @property
    def tables(self):
        """Dict of table_name (lower) -> schema extracted from all SQL."""
        result = {}
        pattern = re.compile(
            r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)',
            re.IGNORECASE)
        for schema, table in pattern.findall(self.decoded):
            result[table.lower()] = schema
        return result

    # ── Misc ─────────────────────────────────────────────────────────────────

    @property
    def has_email(self):
        return 'SendEmailActivity' in self.raw

    @property
    def has_copy_file(self):
        return 'CopyFileActivity' in self.raw

    @property
    def safe_name(self):
        """Report name safe for use in ADF resource names."""
        return re.sub(r'[^A-Za-z0-9_]', '_', self.report_name)


# ─────────────────────────────────────────────────────────────────────────────
# Oracle / Redshift → T-SQL translator
# ─────────────────────────────────────────────────────────────────────────────

def translate_sql(sql):
    """Basic Oracle/Redshift → T-SQL translation for common Toad patterns."""
    if not sql:
        return sql

    # SYSDATE → GETDATE()
    sql = re.sub(r'\bSYSDATE\b', 'GETDATE()', sql, flags=re.IGNORECASE)

    # trunc(expr) → CAST(expr AS DATE)  -- supports one level of nested parens e.g. trunc(GETDATE())
    sql = re.sub(r'\btrunc\s*\(((?:[^()]+|\([^()]*\))+)\)',
                 lambda m: f'CAST({m.group(1).strip()} AS DATE)',
                 sql, flags=re.IGNORECASE)

    # date_add('day', n, expr) → DATEADD(DAY, n, expr)
    sql = re.sub(r"date_add\s*\(\s*'day'\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEADD(DAY, {m.group(1).strip()}, {m.group(2).strip()})',
                 sql, flags=re.IGNORECASE)

    # date_add('month', n, expr) → DATEADD(MONTH, n, expr)
    sql = re.sub(r"date_add\s*\(\s*'month'\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEADD(MONTH, {m.group(1).strip()}, {m.group(2).strip()})',
                 sql, flags=re.IGNORECASE)

    # date_trunc('month', expr) → DATEFROMPARTS(YEAR(expr), MONTH(expr), 1)
    sql = re.sub(r"date_trunc\s*\(\s*'month'\s*,\s*([^)]+?)\s*\)",
                 lambda m: (f'DATEFROMPARTS(YEAR({m.group(1).strip()}), '
                            f'MONTH({m.group(1).strip()}), 1)'),
                 sql, flags=re.IGNORECASE)

    # date_trunc('year', expr) → DATEFROMPARTS(YEAR(expr), 1, 1)
    sql = re.sub(r"date_trunc\s*\(\s*'year'\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'DATEFROMPARTS(YEAR({m.group(1).strip()}), 1, 1)',
                 sql, flags=re.IGNORECASE)

    # date_trunc('day', expr) → CAST(expr AS DATE)
    sql = re.sub(r"date_trunc\s*\(\s*'day'\s*,\s*([^)]+?)\s*\)",
                 lambda m: f'CAST({m.group(1).strip()} AS DATE)',
                 sql, flags=re.IGNORECASE)

    # DATEDIFF(minutes, ...) → DATEDIFF(MINUTE, ...)
    sql = re.sub(r'\bDATEDIFF\s*\(\s*minutes\s*,', 'DATEDIFF(MINUTE,', sql, flags=re.IGNORECASE)

    # ::TIMESTAMP → AS DATETIME2
    sql = re.sub(r'::\s*TIMESTAMP\b', ' AS DATETIME2', sql, flags=re.IGNORECASE)

    # ::DATE → AS DATE
    sql = re.sub(r'::\s*DATE\b', ' AS DATE', sql, flags=re.IGNORECASE)

    # to_date(col, 'dd/mm/yyyy') → CONVERT(DATE, col, 103)
    sql = re.sub(r"to_date\s*\(\s*([^,]+?)\s*,\s*'dd/mm/yyyy'\s*\)",
                 lambda m: f'CONVERT(DATE, {m.group(1).strip()}, 103)',
                 sql, flags=re.IGNORECASE)

    # DECODE(col, 'A', 'B', col) → CASE WHEN col='A' THEN 'B' ELSE col END
    sql = re.sub(r"DECODE\s*\(\s*([^,]+?)\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([^)]+?)\s*\)",
                 lambda m: (f"CASE WHEN {m.group(1).strip()} = '{m.group(2)}' "
                            f"THEN '{m.group(3)}' ELSE {m.group(4).strip()} END"),
                 sql, flags=re.IGNORECASE)

    # date(to_date(...)) -- Redshift date() wrapper → CAST(... AS DATE)
    sql = re.sub(r'\bdate\s*\(\s*(CONVERT\([^)]+\))\s*\)',
                 lambda m: f'CAST({m.group(1)} AS DATE)',
                 sql, flags=re.IGNORECASE)

    return sql


def build_ods_sql(raw_sql):
    """
    Convert ODS check SELECT * → COUNT(*) AS row_count and translate to T-SQL.
    ADF Lookup uses firstRow, so we need a scalar result.
    """
    sql = translate_sql(raw_sql)
    # Replace leading SELECT * or SELECT col with SELECT COUNT(*) AS row_count
    sql = re.sub(r'^\s*SELECT\s+\*', 'SELECT COUNT(*) AS row_count', sql,
                 flags=re.IGNORECASE)
    return sql


# ─────────────────────────────────────────────────────────────────────────────
# Linked Services
# ─────────────────────────────────────────────────────────────────────────────

def _ls(name, description, ls_type, type_props):
    return {
        'name': name,
        'type': f'Microsoft.DataFactory/factories/linkedservices',
        'properties': {
            'description': description,
            'type': ls_type,
            'typeProperties': type_props,
            'annotations': []
        }
    }


def ls_key_vault():
    return _ls(
        'LS_AzureKeyVault',
        'Azure Key Vault -- stores all connection secrets',
        'AzureKeyVault',
        {'baseUrl': 'https://$(key_vault_name).vault.azure.net/'}
    )


def ls_azure_sql():
    return _ls(
        'LS_AzureSQL_Source',
        'Azure SQL Server -- POC source (simulates Oracle/Redshift)',
        'AzureSqlDatabase',
        {
            'connectionString': (
                'Server=tcp:$(azure_sql_server).database.windows.net,1433;'
                'Database=$(azure_sql_db);User ID=sqladmin;'
                'Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
            ),
            'password': {
                'type': 'AzureKeyVaultSecret',
                'store': {'referenceName': 'LS_AzureKeyVault', 'type': 'LinkedServiceReference'},
                'secretName': 'azuresql-db-password'
            }
        }
    )


def ls_blob_storage():
    return _ls(
        'LS_AzureBlobStorage',
        'Azure Blob Storage -- report output and archive',
        'AzureBlobStorage',
        {
            'connectionString': {
                'type': 'AzureKeyVaultSecret',
                'store': {'referenceName': 'LS_AzureKeyVault', 'type': 'LinkedServiceReference'},
                'secretName': 'storage-account-key'
            }
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Datasets
# ─────────────────────────────────────────────────────────────────────────────

def ds_sql_table(ds_name, description, schema, table):
    return {
        'name': ds_name,
        'type': 'Microsoft.DataFactory/factories/datasets',
        'properties': {
            'description': description,
            'linkedServiceName': {'referenceName': 'LS_AzureSQL_Source', 'type': 'LinkedServiceReference'},
            'type': 'AzureSqlTable',
            'typeProperties': {'schema': schema, 'table': table},
            'schema': [],
            'annotations': []
        }
    }


def ds_sql_config():
    return {
        'name': 'DS_AzureSQL_Config',
        'type': 'Microsoft.DataFactory/factories/datasets',
        'properties': {
            'description': 'Azure SQL config schema -- report metadata and email distribution',
            'linkedServiceName': {'referenceName': 'LS_AzureSQL_Source', 'type': 'LinkedServiceReference'},
            'type': 'AzureSqlTable',
            'typeProperties': {'schema': 'config', 'table': 'report_email'},
            'schema': [],
            'annotations': []
        }
    }


def ds_blob(ds_name, description, container_param, folder_path, param_name):
    return {
        'name': ds_name,
        'type': 'Microsoft.DataFactory/factories/datasets',
        'properties': {
            'description': description,
            'linkedServiceName': {'referenceName': 'LS_AzureBlobStorage', 'type': 'LinkedServiceReference'},
            'parameters': {param_name: {'type': 'string'}},
            'type': 'DelimitedText',
            'typeProperties': {
                'location': {
                    'type': 'AzureBlobStorageLocation',
                    'container': {'value': f"@pipeline().parameters.blob_container", 'type': 'Expression'},
                    'folderPath': folder_path,
                    'fileName': {'value': f"@dataset().{param_name}", 'type': 'Expression'}
                },
                'columnDelimiter': ',', 'rowDelimiter': '\n',
                'firstRowAsHeader': True, 'quoteChar': '"', 'escapeChar': '\\'
            },
            'schema': [],
            'annotations': []
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline builder
# ─────────────────────────────────────────────────────────────────────────────

def _dep(activity, condition='Succeeded'):
    return {'activity': activity, 'dependencyConditions': [condition]}


def _expr(value):
    return {'value': value, 'type': 'Expression'}


def _web_email(name, description, depends_on, subject_expr, to_expr, body_expr,
               cc_expr=None, bcc_expr=None):
    parts = [f'"subject":', f'"{subject_expr}"',
             f',"to":"{to_expr}"']
    if cc_expr:
        parts.append(f',"cc":"{cc_expr}"')
    if bcc_expr:
        parts.append(f',"bcc":"{bcc_expr}"')
    parts.append(f',"body":"{body_expr}"')

    body_val = (
        "@concat('{"
        + f'"subject":"', subject_expr, '"'
        + f',"to":"', f"@{{to_expr}}", '"'
        + "}')"
    )

    # Build a clean concat expression for the JSON body
    body_parts = [f"{{", f'"subject":"' + subject_expr + '"']
    if to_expr:
        body_parts.append(f',"to":"' + to_expr + '"')
    if cc_expr:
        body_parts.append(f',"cc":"' + cc_expr + '"')
    if bcc_expr:
        body_parts.append(f',"bcc":"' + bcc_expr + '"')
    body_parts.append(f',"body":"' + body_expr + '"' + '}')

    return {
        'name': name,
        'description': description,
        'type': 'WebActivity',
        'dependsOn': [_dep(d) for d in depends_on],
        'typeProperties': {
            'url': _expr("@pipeline().parameters.logic_app_email_url"),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': _expr(
                "@concat('{"
                + f'"subject":"', subject_expr, '",',
                '"to":"', "@{activity('Lookup_Ops_Email_List').output.firstRow.email_list}", '"',
                "})"
            )
        }
    }


def build_email_body(subject_expr, to_var, cc_var=None, bcc_var=None, body_text=''):
    """Build the ADF expression for a Logic App email POST body."""
    parts = [f"'{{\"subject\":\"'", f", {subject_expr}", f", '\"'"]
    parts += [f", ',\"to\":\"'", f", {to_var}", f", '\"'"]
    if cc_var:
        parts += [f", ',\"cc\":\"'", f", {cc_var}", f", '\"'"]
    if bcc_var:
        parts += [f", ',\"bcc\":\"'", f", {bcc_var}", f", '\"'"]
    parts += [f", ',\"body\":\"{body_text}\"'", f", '}}'" ]
    return '@concat(' + ', '.join(parts) + ')'


def build_pipeline(extractor, report_name=None):
    """Build the full ADF pipeline dict from extracted Toad metadata."""
    # Use folder name (report_name) as canonical ADF name; fall back to Toad workflow name
    rn         = report_name or extractor.report_name
    safe       = re.sub(r'[^A-Za-z0-9_]', '_', rn)
    ods_sql    = build_ods_sql(extractor.ods_check_sql)
    report_sql = translate_sql(extractor.report_sql_raw)
    out_base   = extractor.output_file_base
    archive_fn = extractor.archive_file_name

    # Email variables
    ops_list   = "activity('Lookup_Ops_Email_List').output.firstRow.email_list"
    bi_list    = "activity('Lookup_BI_Email_List').output.firstRow.email_list"
    alert_list = "activity('Lookup_Alert_Email_List').output.firstRow.email_list"
    date_var   = "variables('report_date')"

    subj_report  = extractor.email_subject_report.replace('#date#', "', variables('report_date'), '")
    subj_no_data = extractor.email_subject_no_data.replace('#date#', "', variables('report_date'), '")
    subj_confirm = extractor.email_subject_confirm.replace('#date#', "', variables('report_date'), '")

    def email_body_expr(subject, to, cc=None, bcc=None, body_text=''):
        s = f"@concat('{{\"subject\":\"', '{subject}', '\"',"
        s += f" ',\"to\":\"', {to}, '\"'"
        if cc:
            s += f", ',\"cc\":\"', {cc}, '\"'"
        if bcc:
            s += f", ',\"bcc\":\"', {bcc}, '\"'"
        s += f", ',\"body\":\"{body_text}\"}}' )"
        return s

    # ── Activities ────────────────────────────────────────────────────────────

    lookup_ods = {
        'name': 'Lookup_ODS_Refresh_Check',
        'description': f'Check ODS data refresh. Replicates: SelectDataActivity in Toad.',
        'type': 'Lookup',
        'policy': {'timeout': '0.00:05:00', 'retry': 1, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'source': {
                'type': 'AzureSqlSource',
                'sqlReaderQuery': ods_sql,
                'queryTimeout': '00:05:00'
            },
            'dataset': {'referenceName': f'DS_AzureSQL_ODS_Log', 'type': 'DatasetReference'},
            'firstRowOnly': True
        }
    }

    set_date = {
        'name': 'SetVar_ReportDate',
        'description': "Set yesterday's date. Replicates: VariableActivity in Toad.",
        'type': 'SetVariable',
        'dependsOn': [_dep('Lookup_ODS_Refresh_Check')],
        'typeProperties': {
            'variableName': 'report_date',
            'value': _expr("@formatDateTime(addDays(utcNow(), -1), 'dd.MM.yyyy')")
        }
    }

    def email_lookup(name, group, email_type):
        return {
            'name': name,
            'description': f'Load {group} email list from config table.',
            'type': 'Lookup',
            'dependsOn': [_dep('SetVar_ReportDate')],
            'typeProperties': {
                'source': {
                    'type': 'AzureSqlSource',
                    'sqlReaderQuery': (
                        f"SELECT STRING_AGG(re.email_address, ';') AS email_list "
                        f"FROM config.report_email re "
                        f"JOIN config.report r ON re.report_id = r.report_id "
                        f"WHERE r.report_name = '{rn}' "
                        f"AND re.recipient_group = '{group}' "
                        f"AND re.email_type = '{email_type}' "
                        f"AND re.is_active = 'Y' AND r.is_active = 'Y'"
                    ),
                    'queryTimeout': '00:01:00'
                },
                'dataset': {'referenceName': 'DS_AzureSQL_Config', 'type': 'DatasetReference'},
                'firstRowOnly': True
            }
        }

    lkp_ops   = email_lookup('Lookup_Ops_Email_List',   'OPERATIONS', 'TO')
    lkp_bi    = email_lookup('Lookup_BI_Email_List',     'BI_TEAM',    'BCC')
    lkp_alert = email_lookup('Lookup_Alert_Email_List',  'ALERT_ONLY', 'CC')

    copy_to_blob = {
        'name': 'Copy_ReportData_To_Blob',
        'description': 'Run report SQL, export to Blob as CSV. Replicates: SelectToExcelActivity.',
        'type': 'Copy',
        'policy': {'timeout': '0.01:00:00', 'retry': 1, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'source': {
                'type': 'AzureSqlSource',
                'sqlReaderQuery': _expr(
                    '@concat(\'' + report_sql.replace("'", "\\'").replace('\n', '\\n') + '\')'
                    if False else report_sql   # embed SQL directly
                ),
                'queryTimeout': '00:30:00'
            },
            'sink': {
                'type': 'DelimitedTextSink',
                'storeSettings': {'type': 'AzureBlobStorageWriteSettings'},
                'formatSettings': {
                    'type': 'DelimitedTextWriteSettings',
                    'quoteAllText': True,
                    'fileExtension': '.csv'
                }
            },
            'enableStaging': False
        },
        'inputs':  [{'referenceName': 'DS_AzureSQL_ReportSource', 'type': 'DatasetReference'}],
        'outputs': [{
            'referenceName': 'DS_Blob_Output',
            'type': 'DatasetReference',
            'parameters': {
                'file_name': _expr(f"@concat('{out_base}_', {date_var}, '.csv')")
            }
        }]
    }

    copy_archive = {
        'name': 'Copy_Archive_File',
        'description': 'Copy output to archive folder. Replicates: CopyFileActivity.',
        'type': 'Copy',
        'dependsOn': [_dep('Copy_ReportData_To_Blob')],
        'typeProperties': {
            'source': {
                'type': 'DelimitedTextSource',
                'storeSettings': {'type': 'AzureBlobStorageReadSettings'},
                'formatSettings': {'type': 'DelimitedTextReadSettings'}
            },
            'sink': {
                'type': 'DelimitedTextSink',
                'storeSettings': {'type': 'AzureBlobStorageWriteSettings'},
                'formatSettings': {
                    'type': 'DelimitedTextWriteSettings',
                    'quoteAllText': True,
                    'fileExtension': '.csv'
                }
            },
            'enableStaging': False
        },
        'inputs': [{
            'referenceName': 'DS_Blob_Output', 'type': 'DatasetReference',
            'parameters': {'file_name': _expr(f"@concat('{out_base}_', {date_var}, '.csv')")}
        }],
        'outputs': [{
            'referenceName': 'DS_Blob_Archive', 'type': 'DatasetReference',
            'parameters': {'archive_file_name': _expr(f"@concat('{archive_fn}', {date_var}, '.csv')")}
        }]
    }

    email_ops = {
        'name': 'Email_Report_To_Operations',
        'description': 'Send report email to Operations. Replicates: Email_1 SendEmailActivity.',
        'type': 'WebActivity',
        'dependsOn': [_dep('Copy_Archive_File')],
        'typeProperties': {
            'url': _expr('@pipeline().parameters.logic_app_email_url'),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': _expr(
                f"@concat('{{\"subject\":\"', '{subj_report}', '\"', "
                f"',\"to\":\"', {ops_list}, '\"', "
                f"',\"cc\":\"', {alert_list}, '\"', "
                f"',\"bcc\":\"', {bi_list}, '\"', "
                f"',\"body\":\"Report attached.\"}}')"
            )
        }
    }

    email_bi = {
        'name': 'Email_Confirmation_To_BI_Team',
        'description': 'Send confirmation to BI team. Replicates: Email_3 SendEmailActivity.',
        'type': 'WebActivity',
        'dependsOn': [_dep('Email_Report_To_Operations')],
        'typeProperties': {
            'url': _expr('@pipeline().parameters.logic_app_email_url'),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': _expr(
                f"@concat('{{\"subject\":\"', '{subj_confirm}', '\"', "
                f"',\"to\":\"', {bi_list}, '\"', "
                f"',\"body\":\"Pipeline completed successfully.\"}}')"
            )
        }
    }

    email_no_data = {
        'name': 'Email_ODS_Not_Refreshed',
        'description': 'Alert email when ODS not ready. Replicates: Email_2 SendEmailActivity.',
        'type': 'WebActivity',
        'typeProperties': {
            'url': _expr('@pipeline().parameters.logic_app_email_url'),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': _expr(
                f"@concat('{{\"subject\":\"', '{subj_no_data}', '\"', "
                f"',\"to\":\"', {ops_list}, '\"', "
                f"',\"cc\":\"', {alert_list}, '\"', "
                f"',\"body\":\"ODS data has not been refreshed. Report not generated.\"}}')"
            )
        }
    }

    if_condition = {
        'name': 'If_ODS_Refreshed',
        'description': 'Branch on ODS refresh. Replicates: VariableIfElseActivity.',
        'type': 'IfCondition',
        'dependsOn': [
            _dep('Lookup_Ops_Email_List'),
            _dep('Lookup_BI_Email_List'),
            _dep('Lookup_Alert_Email_List')
        ],
        'typeProperties': {
            'expression': _expr(
                "@greater(activity('Lookup_ODS_Refresh_Check').output.firstRow.row_count, 0)"
            ),
            'ifFalseActivities': [email_no_data],
            'ifTrueActivities':  [copy_to_blob, copy_archive, email_ops, email_bi]
        }
    }

    # ── Pipeline object ───────────────────────────────────────────────────────

    return {
        'name': f'PL_{safe}',
        'type': 'Microsoft.DataFactory/factories/pipelines',
        'properties': {
            'description': (
                f'Migrated from Toad Automation Script: {extractor.report_name}. '
                f'Generated by Tool 2 -- review SQL translation before production use.'
            ),
            'activities': [
                lookup_ods, set_date,
                lkp_ops, lkp_bi, lkp_alert,
                if_condition
            ],
            'parameters': {
                'logic_app_email_url': {
                    'type': 'string',
                    'defaultValue': 'https://prod-xx.region.logic.azure.com/workflows/YOUR_URL'
                },
                'blob_container': {
                    'type': 'string',
                    'defaultValue': safe.lower().replace('_', '-')
                }
            },
            'variables': {
                'report_date': {'type': 'String'}
            },
            'annotations': [
                f'Generated: {__import__("datetime").date.today()}',
                f'Source: Toad XML {rn}',
                'SQL translation: auto -- review before production deployment'
            ],
            'triggers': [{
                'name': 'TR_Daily_0600',
                'type': 'ScheduleTrigger',
                'runtimeState': 'Stopped',
                'typeProperties': {
                    'recurrence': {
                        'frequency': 'Day', 'interval': 1,
                        'startTime': '2026-01-01T06:00:00Z',
                        'timeZone': 'GMT Standard Time',
                        'schedule': {'hours': [6], 'minutes': [0]}
                    }
                },
                'pipelines': [{
                    'pipelineReference': {
                        'referenceName': f'PL_{safe}',
                        'type': 'PipelineReference'
                    }
                }]
            }]
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# ARM template assembler
# ─────────────────────────────────────────────────────────────────────────────

def build_arm_template(report_name, linked_services, datasets, pipeline):
    safe = re.sub(r'[^A-Za-z0-9_]', '_', report_name)
    pl_name = f'PL_{safe}'

    def ls_resource(ls):
        name = ls['properties']['type']
        ls_name = ls['name']
        return {
            'type': f'Microsoft.DataFactory/factories/linkedservices',
            'apiVersion': API_VER,
            'name': f"[concat(parameters('factoryName'), '/{ls_name}')]",
            'dependsOn': ["[variables('factoryId')]"],
            'properties': ls['properties']
        }

    def ds_resource(ds):
        ds_name = ds['name']
        ls_dep  = ds['properties']['linkedServiceName']['referenceName']
        return {
            'type': 'Microsoft.DataFactory/factories/datasets',
            'apiVersion': API_VER,
            'name': f"[concat(parameters('factoryName'), '/{ds_name}')]",
            'dependsOn': [
                "[variables('factoryId')]",
                f"[concat(variables('factoryId'), '/linkedservices/{ls_dep}')]"
            ],
            'properties': ds['properties']
        }

    pl_resource = {
        'type': 'Microsoft.DataFactory/factories/pipelines',
        'apiVersion': API_VER,
        'name': f"[concat(parameters('factoryName'), '/{pl_name}')]",
        'dependsOn': (
            ["[variables('factoryId')]"] +
            ["[concat(variables('factoryId'), '/datasets/" + ds['name'] + "')]"
             for ds in datasets]
        ),
        'properties': pipeline['properties']
    }

    resources = [
        {
            'type': 'Microsoft.DataFactory/factories',
            'apiVersion': API_VER,
            'name': "[parameters('factoryName')]",
            'location': "[parameters('location')]",
            'identity': {'type': 'SystemAssigned'},
            'properties': {}
        }
    ] + [ls_resource(ls) for ls in linked_services] \
      + [ds_resource(ds) for ds in datasets] \
      + [pl_resource]

    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {
            'factoryName':          {'type': 'string', 'metadata': {'description': 'ADF instance name'}},
            'location':             {'type': 'string', 'defaultValue': 'uksouth'},
            'azure_sql_server':     {'type': 'string', 'metadata': {'description': 'Azure SQL Server name (without .database.windows.net)'}},
            'azure_sql_db':         {'type': 'string', 'metadata': {'description': 'Azure SQL Database name'}},
            'key_vault_name':       {'type': 'string', 'metadata': {'description': 'Key Vault name'}},
            'storage_account_name': {'type': 'string', 'metadata': {'description': 'Blob Storage account name'}},
            'logic_app_email_url':  {'type': 'string', 'metadata': {'description': 'Logic App HTTP trigger URL'}}
        },
        'variables': {
            'factoryId': "[concat('Microsoft.DataFactory/factories/', parameters('factoryName'))]"
        },
        'resources': resources
    }


def build_parameters():
    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {
            'factoryName':          {'value': 'adf-toad-poc'},
            'location':             {'value': 'uksouth'},
            'azure_sql_server':     {'value': '<your-sql-server>'},
            'azure_sql_db':         {'value': '<your-sql-db>'},
            'key_vault_name':       {'value': '<your-keyvault>'},
            'storage_account_name': {'value': '<your-storage-account>'},
            'logic_app_email_url':  {'value': '<your-logic-app-url>'}
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generate_adf(report_name, verbose=False):
    xml_path = os.path.join(REPORTS_DIR, report_name, 'sanitized', f'{report_name}_sanitized.txt')
    out_dir  = os.path.join(REPORTS_DIR, report_name, 'adf')

    if not os.path.exists(xml_path):
        print(f'Sanitized XML not found: {xml_path}')
        print('Run Tool 1 first.')
        sys.exit(1)

    # Clean previous output so re-runs don't leave stale files
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)

    print(f'\nTool 2 -- ADF ARM Template Generator')
    print(f'Report : {report_name}')
    print(f'Input  : {xml_path}')
    print(f'Output : {out_dir}')

    ex = ToadXmlExtractor(xml_path)

    if verbose:
        print(f'\n  Report name  : {ex.report_name}')
        print(f'  ODS table    : {ex.ods_table}')
        print(f'  Output base  : {ex.output_file_base}')
        print(f'  Archive file : {ex.archive_file_name}')
        print(f'  Tables found : {list(ex.tables.keys())}')
        print(f'  Has email    : {ex.has_email}')
        print(f'  Subjects     : {ex.email_subjects[:3]}')

    # ── Linked Services ───────────────────────────────────────────────────────
    linked_services = [ls_key_vault(), ls_azure_sql(), ls_blob_storage()]
    for ls in linked_services:
        path = os.path.join(out_dir, 'linkedServices', f"{ls['name']}.json")
        _write_json(path, ls)
        print(f'  LS  {ls["name"]}')

    # ── Datasets ──────────────────────────────────────────────────────────────
    datasets = []

    # One dataset per SQL table (skip ODS table -- gets its own dedicated dataset below)
    tables = ex.tables
    ods_schema, ods_table_name = ex.ods_table.split('.') if '.' in ex.ods_table else ('dbo', ex.ods_table)
    for table, schema in tables.items():
        if table.lower() == ods_table_name.lower():
            continue  # handled as DS_AzureSQL_ODS_Log below
        ds_name = f'DS_AzureSQL_{table}'
        ds = ds_sql_table(ds_name, f'{schema}.{table}', schema, table)
        datasets.append(ds)
        path = os.path.join(out_dir, 'datasets', f'{ds_name}.json')
        _write_json(path, ds)
        print(f'  DS  {ds_name}')

    # Config dataset (always)
    cfg_ds = ds_sql_config()
    datasets.append(cfg_ds)
    _write_json(os.path.join(out_dir, 'datasets', 'DS_AzureSQL_Config.json'), cfg_ds)
    print(f'  DS  DS_AzureSQL_Config')

    # Blob output + archive
    safe = ex.safe_name
    blob_out = ds_blob('DS_Blob_Output', 'Report CSV output',
                       safe.lower(), f'{safe}/output', 'file_name')
    blob_arc = ds_blob('DS_Blob_Archive', 'Report archive',
                       safe.lower(), f'{safe}/archive', 'archive_file_name')
    datasets += [blob_out, blob_arc]
    _write_json(os.path.join(out_dir, 'datasets', 'DS_Blob_Output.json'), blob_out)
    _write_json(os.path.join(out_dir, 'datasets', 'DS_Blob_Archive.json'), blob_arc)
    print(f'  DS  DS_Blob_Output  /  DS_Blob_Archive')

    # Ensure ODS dataset and Report source dataset exist
    ods_ds_name = 'DS_AzureSQL_ODS_Log'
    if ods_ds_name not in [d['name'] for d in datasets]:
        ods_ds = ds_sql_table(ods_ds_name, f'ODS log table: {ex.ods_table}', ods_schema, ods_table_name)
        datasets.append(ods_ds)
        _write_json(os.path.join(out_dir, 'datasets', f'{ods_ds_name}.json'), ods_ds)
        print(f'  DS  {ods_ds_name}')

    # Generic report source dataset (for Copy activity)
    rpt_tables = [t for t in tables if t != ods_table_name.lower()]
    if rpt_tables:
        main_table  = rpt_tables[0]
        main_schema = tables[main_table]
        rpt_ds = ds_sql_table('DS_AzureSQL_ReportSource',
                              f'Main report source: {main_schema}.{main_table}',
                              main_schema, main_table)
        datasets.append(rpt_ds)
        _write_json(os.path.join(out_dir, 'datasets', 'DS_AzureSQL_ReportSource.json'), rpt_ds)
        print(f'  DS  DS_AzureSQL_ReportSource  ({main_schema}.{main_table})')

    # ── Pipeline ──────────────────────────────────────────────────────────────
    pipeline = build_pipeline(ex, report_name=report_name)
    safe_report = re.sub(r'[^A-Za-z0-9_]', '_', report_name)
    pl_path  = os.path.join(out_dir, 'pipelines', f"PL_{safe_report}.json")
    _write_json(pl_path, pipeline)
    print(f'  PL  PL_{safe_report}  ({len(pipeline["properties"]["activities"])} top-level activities)')

    # ── ARM template ──────────────────────────────────────────────────────────
    arm = build_arm_template(report_name, linked_services, datasets, pipeline)
    _write_json(os.path.join(out_dir, 'arm_template.json'), arm)
    print(f'  ARM arm_template.json  ({len(arm["resources"])} resources)')

    params = build_parameters()
    _write_json(os.path.join(out_dir, 'arm_template_parameters.json'), params)
    print(f'  ARM arm_template_parameters.json')

    print(f'\nDone. Output: {out_dir}')


def main():
    ap = argparse.ArgumentParser(description='Tool 2 -- ADF ARM Template Generator')
    ap.add_argument('report', help='Report name (folder under reports/)')
    ap.add_argument('-v', '--verbose', action='store_true', help='Show extraction details')
    args = ap.parse_args()
    generate_adf(args.report, verbose=args.verbose)


if __name__ == '__main__':
    main()
