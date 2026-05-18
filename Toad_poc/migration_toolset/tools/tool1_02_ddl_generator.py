"""
Tool 1.02 - DDL Generator  (POC only)
=======================================
Reads mock data CSVs produced by Tool 1.01.
Infers T-SQL data types from the actual data values.
Reads the sanitized XML (Tool 1 output) to assign the correct schema to each table.
Generates T-SQL DDL: CREATE SCHEMA + CREATE TABLE statements.

Usage:
  python tool1_02_ddl_generator.py <report_name> [-v]

  python tool1_02_ddl_generator.py BC_BIMIO_267_Daily
  python tool1_02_ddl_generator.py BC_BIMIO_267_Daily -v

Input  : migration_toolset/reports/{report}/mock_data/*.csv
       : migration_toolset/reports/{report}/sanitized/{report}_sanitized.txt
Output : migration_toolset/reports/{report}/ddl/{report}_ddl.sql
"""

import argparse
import csv
import glob
import os
import re
import sys
from datetime import datetime

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

DATE_FMTS = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']
DT_FMTS   = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
TIME_FMTS  = ['%H:%M:%S', '%H:%M']

# Standard VARCHAR bucket sizes
VARCHAR_SIZES = [10, 20, 50, 100, 200, 500, 1000]


# ─────────────────────────────────────────────────────────────────────────────
# Schema extraction from sanitized XML
# ─────────────────────────────────────────────────────────────────────────────

def _decode_entities(text):
    return (text
            .replace('&#xD;&#xA;', '\n').replace('&#xD;', '\r').replace('&#xA;', '\n')
            .replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"'))


def extract_schema_map(sanitized_xml_path):
    """
    Parse the sanitized XML to find every  schema.table  reference in SQL.
    Returns dict: lower(table_name) -> schema_name
    """
    if not os.path.exists(sanitized_xml_path):
        return {}

    with open(sanitized_xml_path, encoding='utf-8', errors='replace') as f:
        content = _decode_entities(f.read())

    schema_map = {}
    pattern = re.compile(
        r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)',
        re.IGNORECASE
    )
    for schema, table in pattern.findall(content):
        schema_map[table.lower()] = schema

    return schema_map


# ─────────────────────────────────────────────────────────────────────────────
# T-SQL type inference
# ─────────────────────────────────────────────────────────────────────────────

def _non_null(values):
    return [str(v).strip() for v in values if str(v).strip() not in ('', 'None', 'NULL', 'null')]


def _varchar_size(max_len):
    for size in VARCHAR_SIZES:
        if max_len <= size:
            return size
    return None   # caller should use NVARCHAR(MAX)


def infer_sql_type(col_name, values):
    """
    Infer the best T-SQL type for a column given its sample values.
    Returns a string like  'INT NOT NULL'  or  'VARCHAR(50) NULL'.
    """
    nn       = _non_null(values)
    nullable = len(nn) < len(values)
    null     = 'NULL' if nullable else 'NOT NULL'

    if not nn:
        return f'NVARCHAR(MAX) NULL'

    # ── Primary key ───────────────────────────────────────────────────────────
    if col_name.lower() == 'id':
        return 'INT NOT NULL'

    # ── Datetime (must check before date) ────────────────────────────────────
    for fmt in DT_FMTS:
        try:
            [datetime.strptime(v, fmt) for v in nn]
            return f'DATETIME2 {null}'
        except ValueError:
            pass

    # ── Date ─────────────────────────────────────────────────────────────────
    for fmt in DATE_FMTS:
        try:
            [datetime.strptime(v, fmt) for v in nn]
            return f'DATE {null}'
        except ValueError:
            pass

    # ── Time ─────────────────────────────────────────────────────────────────
    for fmt in TIME_FMTS:
        try:
            [datetime.strptime(v, fmt) for v in nn]
            return f'TIME {null}'
        except ValueError:
            pass

    # ── Integer ───────────────────────────────────────────────────────────────
    try:
        int_vals = [int(float(v.replace(',', ''))) for v in nn]
        max_abs  = max(abs(v) for v in int_vals)
        sql_type = 'BIGINT' if max_abs > 2_147_483_647 else 'INT'
        return f'{sql_type} {null}'
    except (ValueError, AttributeError):
        pass

    # ── Decimal ───────────────────────────────────────────────────────────────
    try:
        nums     = [float(v.replace(',', '')) for v in nn]
        max_dp   = max(len(v.split('.')[1]) if '.' in v else 0 for v in nn)
        max_digs = max(len(v.replace('.', '').replace('-', '').replace(',', '')) for v in nn)
        precision = min(max_digs + 4, 38)
        return f'DECIMAL({precision}, {max_dp}) {null}'
    except (ValueError, AttributeError):
        pass

    # ── Single-char flag  Y/N ─────────────────────────────────────────────────
    unique = {v.upper() for v in nn}
    if unique <= {'Y', 'N'}:
        return f'CHAR(1) {null}'

    # ── Sized VARCHAR ─────────────────────────────────────────────────────────
    max_len = max(len(v) for v in nn)
    size    = _varchar_size(max_len)
    if size:
        return f'VARCHAR({size}) {null}'
    return f'NVARCHAR(MAX) {null}'


# ─────────────────────────────────────────────────────────────────────────────
# DDL builder
# ─────────────────────────────────────────────────────────────────────────────

def _is_view(table_name):
    """Heuristic: table name ending in _v is likely a view."""
    return table_name.lower().endswith('_v')


def build_table_ddl(schema, table, columns, col_types, verbose=False):
    """Return a CREATE TABLE DDL string."""
    lines = []

    # Header comment
    obj_type = 'VIEW (stored as TABLE for POC)' if _is_view(table) else 'TABLE'
    lines.append(f'-- {obj_type}: [{schema}].[{table}]')
    lines.append(f"IF OBJECT_ID('{schema}.{table}', 'U') IS NULL")
    lines.append('BEGIN')
    lines.append(f'    CREATE TABLE [{schema}].[{table}]')
    lines.append('    (')

    col_defs = []
    for col in columns:
        sql_type = col_types[col]
        col_defs.append(f'        [{col}] {sql_type}')
        if verbose:
            print(f'      {col:<42} {sql_type}')

    # PK constraint on id column
    if 'id' in columns:
        col_defs.append(f'        CONSTRAINT [PK_{table}] PRIMARY KEY ([id])')

    lines.append(',\n'.join(col_defs))
    lines.append('    );')
    lines.append('END')
    lines.append('GO')
    lines.append('')

    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def generate_ddl(report_name, verbose=False):
    mock_dir  = os.path.join(REPORTS_DIR, report_name, 'mock_data')
    ddl_dir   = os.path.join(REPORTS_DIR, report_name, 'ddl')
    xml_path  = os.path.join(REPORTS_DIR, report_name, 'sanitized', f'{report_name}_sanitized.txt')
    out_path  = os.path.join(ddl_dir, f'{report_name}_ddl.sql')

    if not os.path.isdir(mock_dir):
        print(f'Mock data folder not found: {mock_dir}')
        print('Run Tool 1.01 first.')
        sys.exit(1)

    csv_files = sorted(glob.glob(os.path.join(mock_dir, '*.csv')))
    if not csv_files:
        print(f'No CSV files found in: {mock_dir}')
        sys.exit(1)

    # Schema map from sanitized XML
    schema_map = extract_schema_map(xml_path)
    if schema_map:
        print(f'Schema map from XML: {schema_map}')
    else:
        print('No sanitized XML found -- using schema [dbo] for all tables.')

    os.makedirs(ddl_dir, exist_ok=True)

    print(f'\nTool 1.02 -- DDL Generator')
    print(f'Report    : {report_name}')
    print(f'Mock data : {mock_dir}')
    print(f'Output    : {out_path}')
    print(f'Tables    : {len(csv_files)}')

    ddl_sections = []
    ddl_sections.append(f'-- DDL generated by Tool 1.02 for report: {report_name}')
    ddl_sections.append(f'-- Source: mock data in reports/{report_name}/mock_data/')
    ddl_sections.append(f'-- NOTE: Types inferred from data. Review before production use.')
    ddl_sections.append('')

    schemas_written = set()

    # Dims before fact tables (same order as Tool 1.01)
    dim_files   = [f for f in csv_files if os.path.basename(f).startswith('dim_')]
    other_files = [f for f in csv_files if not os.path.basename(f).startswith('dim_')]

    for csv_path in dim_files + other_files:
        table      = os.path.splitext(os.path.basename(csv_path))[0]
        schema     = schema_map.get(table.lower(), 'dbo')

        # CREATE SCHEMA block (once per schema)
        if schema not in schemas_written:
            ddl_sections.append(f"-- ── Schema: {schema} ──────────────────────────────────────")
            ddl_sections.append(f"IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{schema}')")
            ddl_sections.append(f"    EXEC('CREATE SCHEMA [{schema}]');")
            ddl_sections.append('GO')
            ddl_sections.append('')
            schemas_written.add(schema)

        # Read CSV -- infer types
        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader  = csv.DictReader(f)
            rows    = list(reader)
            columns = list(reader.fieldnames or [])

        col_types = {col: infer_sql_type(col, [r[col] for r in rows]) for col in columns}

        if verbose:
            print(f'\n  [{schema}].[{table}]')

        ddl = build_table_ddl(schema, table, columns, col_types, verbose=verbose)
        ddl_sections.append(ddl)

        print(f'  {schema}.{table:<42}  {len(columns)} columns')

    # Write file
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ddl_sections))

    print(f'\nDDL written: {out_path}')


def main():
    ap = argparse.ArgumentParser(description='Tool 1.02 -- DDL Generator (POC only)')
    ap.add_argument('report', help='Report name (folder under reports/)')
    ap.add_argument('-v', '--verbose', action='store_true',
                    help='Show column-level type inference')
    args = ap.parse_args()

    generate_ddl(args.report, verbose=args.verbose)


if __name__ == '__main__':
    main()
