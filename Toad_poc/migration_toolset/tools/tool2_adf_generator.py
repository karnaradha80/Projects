"""
Tool 2 - ADF ARM Template Generator (Generic Pipeline)
=======================================================
Reads the sanitized Toad XML (Tool 1 output).
Derives the report category (Daily/Weekly/Monthly/Custom) from the report name.
Generates a GENERIC ADF pipeline per category (PL_Generic_Daily etc.) that:
  - Accepts report_name as a runtime parameter
  - Reads SQL queries from config.report_sql at runtime (Lookup activities)
  - Reads email distribution from config.report_email at runtime
  - Produces one pipeline that serves ALL reports in the same category

Also generates a per-report schedule trigger that passes report_name as a
parameter to the generic pipeline.

ARM template split (used by Tool 4):
  arm_template_bootstrap.json  -- factory + linked services + datasets + generic pipeline
  arm_template_report.json     -- per-report trigger only

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
# Category derivation
# ─────────────────────────────────────────────────────────────────────────────

def _derive_category(report_name):
    """Return pipeline category from report name suffix, e.g. _Daily -> Daily."""
    up = report_name.upper()
    for suffix in ('_DAILY', '_WEEKLY', '_MONTHLY', '_HOURLY', '_QUARTERLY'):
        if up.endswith(suffix):
            return suffix.lstrip('_').capitalize()
    return 'Custom'


# ─────────────────────────────────────────────────────────────────────────────
# Sanitised XML extractor  (used for report_name / description only now)
# ─────────────────────────────────────────────────────────────────────────────

class ToadXmlExtractor:
    """Pulls identity metadata out of a sanitised Toad XML file."""

    def __init__(self, xml_path):
        with open(xml_path, encoding='utf-8', errors='replace') as f:
            self.raw = f.read()
        self.decoded = _decode(self.raw)

    @property
    def report_name(self):
        m = re.search(r'x:Name="([^"]+)"', self.raw)
        return m.group(1) if m else 'UnknownReport'

    @property
    def description(self):
        m = re.search(r'Description="([^"]{5,})"', self.raw)
        return m.group(1)[:200] if m else ''

    @property
    def safe_name(self):
        return re.sub(r'[^A-Za-z0-9_]', '_', self.report_name)


# ─────────────────────────────────────────────────────────────────────────────
# Oracle / Redshift → T-SQL translator  (preserved for Tool 3 and reports)
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
# Linked Services
# ─────────────────────────────────────────────────────────────────────────────

def _ls(name, description, ls_type, type_props):
    return {
        'name': name,
        'type': 'Microsoft.DataFactory/factories/linkedservices',
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
# Datasets  (generic — no per-report SQL tables)
# ─────────────────────────────────────────────────────────────────────────────

def ds_sql_config():
    """Shared Azure SQL dataset — all Lookup/Copy sources use sqlReaderQuery override."""
    return {
        'name': 'DS_AzureSQL_Config',
        'type': 'Microsoft.DataFactory/factories/datasets',
        'properties': {
            'description': 'Azure SQL -- all dynamic queries use sqlReaderQuery override at runtime',
            'linkedServiceName': {'referenceName': 'LS_AzureSQL_Source', 'type': 'LinkedServiceReference'},
            'type': 'AzureSqlTable',
            'typeProperties': {'schema': 'config', 'table': 'report'},
            'schema': [],
            'annotations': []
        }
    }


def ds_blob_generic(ds_name, description, folder_role, file_param_name):
    """Generic blob dataset parameterised by container + file_name (or archive_file_name)."""
    return {
        'name': ds_name,
        'type': 'Microsoft.DataFactory/factories/datasets',
        'properties': {
            'description': description,
            'linkedServiceName': {'referenceName': 'LS_AzureBlobStorage', 'type': 'LinkedServiceReference'},
            'parameters': {
                'container': {'type': 'string'},
                file_param_name: {'type': 'string'}
            },
            'type': 'DelimitedText',
            'typeProperties': {
                'location': {
                    'type': 'AzureBlobStorageLocation',
                    'container': {'value': '@dataset().container', 'type': 'Expression'},
                    'folderPath': folder_role,
                    'fileName': {'value': f'@dataset().{file_param_name}', 'type': 'Expression'}
                },
                'columnDelimiter': ',', 'rowDelimiter': '\n',
                'firstRowAsHeader': True, 'quoteChar': '"', 'escapeChar': '\\'
            },
            'schema': [],
            'annotations': []
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# ADF expression helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dep(activity, condition='Succeeded'):
    return {'activity': activity, 'dependencyConditions': [condition]}


def _expr(value):
    return {'value': value, 'type': 'Expression'}


def _sql_lookup_expr(query_type):
    """ADF @concat expression to fetch query_text from config.report_sql."""
    return (
        f"@concat('SELECT query_text FROM config.report_sql rs "
        f"JOIN config.report r ON rs.report_id = r.report_id "
        f"WHERE r.report_name = ''', pipeline().parameters.report_name, ''' "
        f"AND rs.query_type = ''{query_type}'' AND rs.is_active = ''Y''')"
    )


def _email_list_expr(group, email_type):
    """ADF @concat expression to fetch semicolon-separated email list."""
    return (
        f"@concat('SELECT STRING_AGG(re.email_address, '';'') AS email_list "
        f"FROM config.report_email re "
        f"JOIN config.report r ON re.report_id = r.report_id "
        f"WHERE r.report_name = ''', pipeline().parameters.report_name, ''' "
        f"AND re.recipient_group = ''{group}'' "
        f"AND re.email_type = ''{email_type}'' "
        f"AND re.is_active = ''Y'' AND r.is_active = ''Y''')"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Generic Pipeline builder
# ─────────────────────────────────────────────────────────────────────────────

def build_generic_pipeline(category):
    """
    Build PL_Generic_{category} -- parameterised by report_name.
    Reads ALL SQL queries and email lists from config tables at runtime.
    One pipeline handles every report in the same category.
    """
    pl_name  = f'PL_Generic_{category}'
    rn_param = "pipeline().parameters.report_name"
    date_var = "variables('report_date')"

    def _lookup(name, description, depends_on, sql_expr_value, timeout='00:05:00'):
        act = {
            'name': name,
            'description': description,
            'type': 'Lookup',
            'policy': {'timeout': '0.00:05:00', 'retry': 1, 'retryIntervalInSeconds': 30},
            'typeProperties': {
                'source': {
                    'type': 'AzureSqlSource',
                    'sqlReaderQuery': _expr(sql_expr_value),
                    'queryTimeout': timeout
                },
                'dataset': {'referenceName': 'DS_AzureSQL_Config', 'type': 'DatasetReference'},
                'firstRowOnly': True
            }
        }
        if depends_on:
            act['dependsOn'] = [_dep(d) for d in depends_on]
        return act

    # ── Step 1: read report metadata from config ──────────────────────────────
    lookup_config = _lookup(
        'Lookup_Report_Config',
        'Read report metadata (container, template) from config.report.',
        [],
        f"@concat('SELECT output_container, template_name "
        f"FROM config.report "
        f"WHERE report_name = ''', {rn_param}, ''' AND is_active = ''Y''')",
        timeout='00:02:00'
    )

    # ── Step 2: fetch ODS check SQL text ──────────────────────────────────────
    lookup_ods_sql = _lookup(
        'Lookup_ODS_SQL',
        'Fetch ODS check query text from config.report_sql.',
        ['Lookup_Report_Config'],
        _sql_lookup_expr('ODS_CHECK'),
        timeout='00:02:00'
    )

    # ── Step 3: execute ODS check (SQL from config, row_count result) ─────────
    lookup_ods_check = _lookup(
        'Lookup_ODS_Refresh_Check',
        'Run ODS refresh check SQL loaded from config. Replicates: SelectDataActivity.',
        ['Lookup_ODS_SQL'],
        "@activity('Lookup_ODS_SQL').output.firstRow.query_text",
        timeout='00:05:00'
    )

    # ── Step 4: set report_date variable ─────────────────────────────────────
    set_date = {
        'name': 'SetVar_ReportDate',
        'description': "Set yesterday's date as report_date.",
        'type': 'SetVariable',
        'dependsOn': [_dep('Lookup_ODS_Refresh_Check')],
        'typeProperties': {
            'variableName': 'report_date',
            'value': _expr("@formatDateTime(addDays(utcNow(), -1), 'dd.MM.yyyy')")
        }
    }

    # ── Step 5 (parallel): fetch email lists + main SQL ───────────────────────
    lkp_ops = _lookup(
        'Lookup_Ops_Email',
        'Load OPERATIONS TO email list from config.',
        ['SetVar_ReportDate'],
        _email_list_expr('OPERATIONS', 'TO'),
        timeout='00:01:00'
    )

    lkp_bi = _lookup(
        'Lookup_BI_Email',
        'Load BI_TEAM BCC email list from config.',
        ['SetVar_ReportDate'],
        _email_list_expr('BI_TEAM', 'BCC'),
        timeout='00:01:00'
    )

    lkp_alert = _lookup(
        'Lookup_Alert_Email',
        'Load ALERT_ONLY CC email list from config.',
        ['SetVar_ReportDate'],
        _email_list_expr('ALERT_ONLY', 'CC'),
        timeout='00:01:00'
    )

    lkp_main_sql = _lookup(
        'Lookup_Main_SQL',
        'Fetch report main query text from config.report_sql.',
        ['SetVar_ReportDate'],
        _sql_lookup_expr('REPORT_MAIN'),
        timeout='00:02:00'
    )

    # ── IF true: copy data → archive → email ops → email BI ──────────────────

    copy_to_blob = {
        'name': 'Copy_ReportData_To_Blob',
        'description': 'Execute main report SQL from config, export to Blob CSV. Replicates: SelectToExcelActivity.',
        'type': 'Copy',
        'policy': {'timeout': '0.01:00:00', 'retry': 1, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'source': {
                'type': 'AzureSqlSource',
                'sqlReaderQuery': _expr("@activity('Lookup_Main_SQL').output.firstRow.query_text"),
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
        'inputs': [{'referenceName': 'DS_AzureSQL_Config', 'type': 'DatasetReference'}],
        'outputs': [{
            'referenceName': 'DS_Blob_Generic_Output',
            'type': 'DatasetReference',
            'parameters': {
                'container': _expr("@activity('Lookup_Report_Config').output.firstRow.output_container"),
                'file_name': _expr(f"@concat({rn_param}, '_', {date_var}, '.csv')")
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
            'referenceName': 'DS_Blob_Generic_Output',
            'type': 'DatasetReference',
            'parameters': {
                'container': _expr("@activity('Lookup_Report_Config').output.firstRow.output_container"),
                'file_name': _expr(f"@concat({rn_param}, '_', {date_var}, '.csv')")
            }
        }],
        'outputs': [{
            'referenceName': 'DS_Blob_Generic_Archive',
            'type': 'DatasetReference',
            'parameters': {
                'container': _expr("@activity('Lookup_Report_Config').output.firstRow.output_container"),
                'archive_file_name': _expr(f"@concat({rn_param}, '_For_', {date_var}, '.csv')")
            }
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
                f"@concat('{{\"subject\":\"', {rn_param}, ' - Report: ', {date_var}, '\"',"
                f" ',\"to\":\"', activity('Lookup_Ops_Email').output.firstRow.email_list, '\"',"
                f" ',\"cc\":\"', activity('Lookup_Alert_Email').output.firstRow.email_list, '\"',"
                f" ',\"bcc\":\"', activity('Lookup_BI_Email').output.firstRow.email_list, '\"',"
                f" ',\"body\":\"Report attached.\"}}')"
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
                f"@concat('{{\"subject\":\"', {rn_param}, ' - Pipeline Complete: ', {date_var}, '\"',"
                f" ',\"to\":\"', activity('Lookup_BI_Email').output.firstRow.email_list, '\"',"
                f" ',\"body\":\"Pipeline completed successfully.\"}}')"
            )
        }
    }

    # ── IF false: ODS not refreshed alert ─────────────────────────────────────
    email_no_data = {
        'name': 'Email_ODS_Not_Refreshed',
        'description': 'Alert email when ODS not ready. Replicates: Email_2 SendEmailActivity.',
        'type': 'WebActivity',
        'typeProperties': {
            'url': _expr('@pipeline().parameters.logic_app_email_url'),
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': _expr(
                f"@concat('{{\"subject\":\"', {rn_param}, ' - ODS Not Refreshed: ', {date_var}, '\"',"
                f" ',\"to\":\"', activity('Lookup_Ops_Email').output.firstRow.email_list, '\"',"
                f" ',\"cc\":\"', activity('Lookup_Alert_Email').output.firstRow.email_list, '\"',"
                f" ',\"body\":\"ODS data has not been refreshed. Report not generated.\"}}')"
            )
        }
    }

    if_condition = {
        'name': 'If_ODS_Refreshed',
        'description': 'Branch on ODS refresh check result. Replicates: VariableIfElseActivity.',
        'type': 'IfCondition',
        'dependsOn': [
            _dep('Lookup_Ops_Email'),
            _dep('Lookup_BI_Email'),
            _dep('Lookup_Alert_Email'),
            _dep('Lookup_Main_SQL')
        ],
        'typeProperties': {
            'expression': _expr(
                "@greater(activity('Lookup_ODS_Refresh_Check').output.firstRow.row_count, 0)"
            ),
            'ifFalseActivities': [email_no_data],
            'ifTrueActivities':  [copy_to_blob, copy_archive, email_ops, email_bi]
        }
    }

    return {
        'name': pl_name,
        'type': 'Microsoft.DataFactory/factories/pipelines',
        'properties': {
            'description': (
                f'Generic {category} pipeline -- parameterised by report_name. '
                f'Reads SQL queries and email lists from config tables at runtime. '
                f'One pipeline serves all {category} reports.'
            ),
            'activities': [
                lookup_config,
                lookup_ods_sql,
                lookup_ods_check,
                set_date,
                lkp_main_sql, lkp_ops, lkp_bi, lkp_alert,
                if_condition
            ],
            'parameters': {
                'report_name': {
                    'type': 'string',
                    'defaultValue': ''
                },
                'logic_app_email_url': {
                    'type': 'string',
                    'defaultValue': 'https://prod-xx.region.logic.azure.com/workflows/YOUR_URL'
                }
            },
            'variables': {
                'report_date': {'type': 'String'}
            },
            'annotations': [
                f'Generated: {__import__("datetime").date.today()}',
                f'Category: {category}',
                'Generic pipeline: reads SQL + email config from DB at runtime',
                'No report-specific SQL embedded -- all queries stored in config.report_sql'
            ]
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# ARM template assembler
# ─────────────────────────────────────────────────────────────────────────────

def build_arm_template(report_name, category, linked_services, datasets, pipeline):
    safe      = re.sub(r'[^A-Za-z0-9_]', '_', report_name)
    pl_name   = f'PL_Generic_{category}'
    trig_name = f'TR_{safe}_0600'

    def ls_resource(ls):
        ls_name = ls['name']
        return {
            'type': 'Microsoft.DataFactory/factories/linkedservices',
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
            [f"[concat(variables('factoryId'), '/datasets/{ds['name']}')]" for ds in datasets]
        ),
        'properties': pipeline['properties']
    }

    # Per-report trigger passes report_name as parameter to the generic pipeline
    trigger_resource = {
        'type': 'Microsoft.DataFactory/factories/triggers',
        'apiVersion': API_VER,
        'name': f"[concat(parameters('factoryName'), '/{trig_name}')]",
        'dependsOn': [
            "[variables('factoryId')]",
            f"[concat(variables('factoryId'), '/pipelines/{pl_name}')]"
        ],
        'properties': {
            'description': f'Schedule trigger for {report_name} -- runs {pl_name} with report_name parameter.',
            'runtimeState': 'Stopped',
            'type': 'ScheduleTrigger',
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
                    'referenceName': pl_name,
                    'type': 'PipelineReference'
                },
                'parameters': {
                    'report_name': report_name
                }
            }]
        }
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
      + [pl_resource, trigger_resource]

    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {
            'factoryName':          {'type': 'string', 'metadata': {'description': 'ADF instance name'}},
            'location':             {'type': 'string', 'defaultValue': 'uksouth'},
            'azure_sql_server':     {'type': 'string', 'metadata': {'description': 'Azure SQL Server name'}},
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

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)

    category = _derive_category(report_name)
    pl_name  = f'PL_Generic_{category}'

    print(f'\nTool 2 -- ADF ARM Template Generator  [Generic Pipeline]')
    print(f'Report   : {report_name}')
    print(f'Category : {category}')
    print(f'Pipeline : {pl_name}  (shared across all {category} reports)')
    print(f'Output   : {out_dir}')

    ex = ToadXmlExtractor(xml_path)

    if verbose:
        print(f'\n  Report name  : {ex.report_name}')
        print(f'  Description  : {ex.description[:80]}')
        print(f'  Category     : {category}')
        print(f'  Pipeline     : {pl_name}')
        print(f'  Trigger      : TR_{re.sub(chr(91) + "^A-Za-z0-9_" + chr(93), "_", report_name)}_0600')

    # ── Linked Services ───────────────────────────────────────────────────────
    linked_services = [ls_key_vault(), ls_azure_sql(), ls_blob_storage()]
    for ls in linked_services:
        path = os.path.join(out_dir, 'linkedServices', f"{ls['name']}.json")
        _write_json(path, ls)
        print(f'  LS  {ls["name"]}')

    # ── Datasets (generic — 3 total) ──────────────────────────────────────────
    datasets = [
        ds_sql_config(),
        ds_blob_generic('DS_Blob_Generic_Output',  'Report CSV output',  'output',  'file_name'),
        ds_blob_generic('DS_Blob_Generic_Archive', 'Report CSV archive', 'archive', 'archive_file_name'),
    ]
    for ds in datasets:
        path = os.path.join(out_dir, 'datasets', f"{ds['name']}.json")
        _write_json(path, ds)
        print(f'  DS  {ds["name"]}')

    # ── Generic Pipeline ──────────────────────────────────────────────────────
    pipeline = build_generic_pipeline(category)
    pl_path  = os.path.join(out_dir, 'pipelines', f'{pl_name}.json')
    _write_json(pl_path, pipeline)
    act_count = len(pipeline['properties']['activities'])
    print(f'  PL  {pl_name}  ({act_count} top-level activities)')
    print(f'      ^ shared pipeline — SQL and emails loaded from DB at runtime')

    # ── ARM template ──────────────────────────────────────────────────────────
    arm = build_arm_template(report_name, category, linked_services, datasets, pipeline)
    _write_json(os.path.join(out_dir, 'arm_template.json'), arm)
    print(f'  ARM arm_template.json  ({len(arm["resources"])} resources)')

    params = build_parameters()
    _write_json(os.path.join(out_dir, 'arm_template_parameters.json'), params)
    print(f'  ARM arm_template_parameters.json')

    print(f'\nDone. Output: {out_dir}')
    print(f'  Bootstrap deploy: factory + LS + datasets + {pl_name}  (once per category)')
    print(f'  Report deploy   : TR_{re.sub("[^A-Za-z0-9_]", "_", report_name)}_0600 trigger only  (per report)')


def main():
    ap = argparse.ArgumentParser(description='Tool 2 -- ADF Generic Pipeline Generator')
    ap.add_argument('report', help='Report name (folder under reports/)')
    ap.add_argument('-v', '--verbose', action='store_true', help='Show extraction details')
    args = ap.parse_args()
    generate_adf(args.report, verbose=args.verbose)


if __name__ == '__main__':
    main()
