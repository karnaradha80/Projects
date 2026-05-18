"""
Tool 1.01 - Mock Data Generator  (POC only)
============================================
Reads 10-row seed CSV files provided by the user.
Analyses column types and value patterns automatically.
Generates synthetic mock data at configurable scale -- default 1000 rows per table.

FK detection is data-driven: if all values in an integer column exist in another
table's `id` pool, that column is treated as a FK and constrained accordingly.

Usage:
  python tool1_01_mock_data.py <report_name> [--rows N] [-v]

  python tool1_01_mock_data.py BC_BIMIO_267_Daily
  python tool1_01_mock_data.py BC_BIMIO_267_Daily --rows 1500 -v

Seed input : migration_toolset/input/seed/{report_name}/*.csv  (10 rows per table)
Output     : migration_toolset/reports/{report_name}/mock_data/*.csv
"""

import argparse
import csv
import glob
import os
import random
import re
import sys
from datetime import datetime, timedelta
from collections import OrderedDict

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_DIR   = os.path.join(BASE_DIR, 'input', 'seed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

DATE_FMTS = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']
DT_FMTS   = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
TIME_FMTS = ['%H:%M:%S', '%H:%M']

PREFIXED_INT_RE = re.compile(r'^([A-Za-z\-_]+)(\d+)$')  # e.g. WO-00001

random.seed(42)


# ─────────────────────────────────────────────────────────────────────────────
# Type detection
# ─────────────────────────────────────────────────────────────────────────────

def _non_null(values):
    return [str(v).strip() for v in values if str(v).strip() not in ('', 'None', 'NULL', 'null')]


def detect_type(col_name, values):
    """
    Returns (kind, meta) where kind is one of:
      pk, fk_candidate, integer, decimal, datetime, date, time,
      prefixed_int, flag, enum, string
    meta is a dict of parameters used by the generator.
    """
    nn = _non_null(values)
    if not nn:
        return ('string', {'values': ['']})

    # ── Datetime (check before date) ─────────────────────────────────────────
    for fmt in DT_FMTS:
        try:
            parsed = [datetime.strptime(v, fmt) for v in nn]
            return ('datetime', {'fmt': fmt, 'min': min(parsed), 'max': max(parsed)})
        except ValueError:
            pass

    # ── Date ─────────────────────────────────────────────────────────────────
    for fmt in DATE_FMTS:
        try:
            parsed = [datetime.strptime(v, fmt) for v in nn]
            return ('date', {'fmt': fmt, 'min': min(parsed), 'max': max(parsed)})
        except ValueError:
            pass

    # ── Time ─────────────────────────────────────────────────────────────────
    for fmt in TIME_FMTS:
        try:
            [datetime.strptime(v, fmt) for v in nn]
            return ('time', {'fmt': fmt, 'values': nn})
        except ValueError:
            pass

    # ── Integer / PK / FK candidate ──────────────────────────────────────────
    try:
        int_vals = [int(float(v.replace(',', ''))) for v in nn]
        is_pk = col_name.lower() == 'id'
        if is_pk:
            return ('pk', {'max': max(int_vals), 'values': int_vals})
        return ('fk_candidate', {
            'min': min(int_vals), 'max': max(int_vals), 'values': int_vals
        })
    except (ValueError, AttributeError):
        pass

    # ── Decimal ──────────────────────────────────────────────────────────────
    try:
        nums = [float(v.replace(',', '')) for v in nn]
        dp = max(len(v.split('.')[1]) if '.' in v else 0 for v in nn)
        return ('decimal', {'min': min(nums), 'max': max(nums), 'dp': dp})
    except (ValueError, AttributeError):
        pass

    # ── Prefixed integer  (e.g. WO-00001) ───────────────────────────────────
    m = PREFIXED_INT_RE.match(nn[0])
    if m and all(PREFIXED_INT_RE.match(v) for v in nn):
        prefix   = m.group(1)
        width    = len(m.group(2))
        nums     = [int(PREFIXED_INT_RE.match(v).group(2)) for v in nn]
        return ('prefixed_int', {'prefix': prefix, 'width': width, 'max': max(nums)})

    # ── Flag / enum ──────────────────────────────────────────────────────────
    unique = list(OrderedDict.fromkeys(nn))
    if len(unique) <= 6:
        return ('enum', {'values': unique})

    # ── High-cardinality string ───────────────────────────────────────────────
    return ('string', {'values': nn})


# ─────────────────────────────────────────────────────────────────────────────
# FK resolution: name-based first, data-based fallback
# ─────────────────────────────────────────────────────────────────────────────

def _fk_name_score(fk_prefix, table_name):
    """
    Score how well a FK column prefix matches a table name.
    Strategy: strip leading type indicator (d=dim, f=fct) from prefix,
    strip dim_/fct_ from table name, check if remainder starts with same chars.
    e.g.  dwor -> wor  vs  dim_work_orders -> work_orders -> starts with 'wor' -> match
          dorg -> org  vs  dim_organisation -> organisation -> starts with 'org' -> match
    """
    fk_core    = re.sub(r'^[df]', '', fk_prefix.lower())          # dwor -> wor
    table_core = re.sub(r'^(dim|fct|fact|stg|src)_?', '', table_name.lower())  # work_orders
    table_flat = table_core.replace('_', '')                       # workorders

    if not fk_core:
        return 0

    # Direct starts-with match on the flattened table name (best signal)
    if table_flat.startswith(fk_core):
        return len(fk_core) + 10   # bonus for exact prefix match

    # Partial prefix match (at least 3 chars)
    match_len = 0
    for i, ch in enumerate(fk_core):
        if i < len(table_flat) and table_flat[i] == ch:
            match_len += 1
        else:
            break
    if match_len >= 2:
        return match_len

    return 0


def resolve_fk(col_name, col_values, id_pools):
    """
    1. Extract FK prefix from col name  (dwor_id_root -> dwor)
    2. Score each candidate table by name similarity  (dwor -> dim_work_orders wins)
    3. Among name-matched candidates confirm data is a subset of their id pool
    4. If no name match, fall back to first data-subset match
    """
    try:
        col_set = set(int(float(v)) for v in _non_null(col_values))
    except (ValueError, TypeError):
        return None

    if not col_set:
        return None

    # All tables whose id pool covers the FK values
    data_candidates = [t for t, pool in id_pools.items() if col_set.issubset(set(pool))]
    if not data_candidates:
        return None

    # Extract FK prefix: everything before first '_id'
    m = re.match(r'^([a-z]+)_id', col_name.lower())
    if m:
        prefix = m.group(1)
        scores = {t: _fk_name_score(prefix, t) for t in data_candidates}
        best_score = max(scores.values())
        if best_score > 0:
            return max(data_candidates, key=lambda t: scores[t])

    # Name scoring failed -- fall back to first data match
    return data_candidates[0]


# ─────────────────────────────────────────────────────────────────────────────
# Value generation
# ─────────────────────────────────────────────────────────────────────────────

def gen_value(kind, meta, row_idx, id_pools, fk_table=None):
    if kind == 'pk':
        return meta['max'] + row_idx + 1

    if kind == 'fk_candidate':
        if fk_table and fk_table in id_pools and id_pools[fk_table]:
            return random.choice(id_pools[fk_table])
        return random.randint(meta['min'], meta['max'])

    if kind == 'datetime':
        span = max(int((meta['max'] - meta['min']).total_seconds()), 1)
        return (meta['min'] + timedelta(seconds=random.randint(0, span))).strftime(meta['fmt'])

    if kind == 'date':
        span = max((meta['max'] - meta['min']).days, 1)
        return (meta['min'] + timedelta(days=random.randint(0, span))).strftime(meta['fmt'])

    if kind == 'time':
        return random.choice(meta['values'])

    if kind == 'integer':
        return random.randint(meta['min'], meta['max'])

    if kind == 'decimal':
        return round(random.uniform(meta['min'], meta['max']), meta['dp'])

    if kind == 'prefixed_int':
        n = meta['max'] + row_idx + 1
        return f"{meta['prefix']}{str(n).zfill(meta['width'])}"

    if kind in ('flag', 'enum'):
        return random.choice(meta['values'])

    # string -- sample from seed values
    return random.choice(meta['values'])


# ─────────────────────────────────────────────────────────────────────────────
# Per-table generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_table(seed_path, n_rows, id_pools, verbose=False):
    table = os.path.splitext(os.path.basename(seed_path))[0]

    with open(seed_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        seed_rows = list(reader)
        columns = list(reader.fieldnames or [])

    if not seed_rows:
        print(f'    SKIP (empty seed): {table}')
        return [], columns, table

    # ── Detect types ─────────────────────────────────────────────────────────
    col_types = {}
    for col in columns:
        vals = [row[col] for row in seed_rows]
        col_types[col] = detect_type(col, vals)

    # ── Resolve FK candidates ─────────────────────────────────────────────────
    fk_map = {}   # col_name -> referenced table_name (or None)
    for col in columns:
        kind, meta = col_types[col]
        if kind == 'fk_candidate':
            vals = [row[col] for row in seed_rows]
            fk_map[col] = resolve_fk(col, vals, id_pools)

    if verbose:
        print(f'\n    {table}  ({len(seed_rows)} seed -> {n_rows + len(seed_rows)} total)')
        for col in columns:
            kind, _ = col_types[col]
            fk_note = f'  -> {fk_map[col]}' if col in fk_map and fk_map[col] else ''
            print(f'      {col:<40} {kind}{fk_note}')

    # ── Generate new rows ─────────────────────────────────────────────────────
    generated = []
    for i in range(n_rows):
        row = {}
        for col in columns:
            kind, meta = col_types[col]
            row[col] = gen_value(kind, meta, i, id_pools, fk_table=fk_map.get(col))
        generated.append(row)

    all_rows = seed_rows + generated   # seed rows preserved at top

    # ── Register this table's PK pool for downstream FK resolution ────────────
    for col in columns:
        kind, meta = col_types[col]
        if kind == 'pk':
            id_pools[table] = [int(r[col]) for r in all_rows if str(r[col]).strip().lstrip('-').isdigit()]

    return all_rows, columns, table


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(report_name, n_rows, verbose=False):
    seed_dir = os.path.join(INPUT_DIR, report_name)
    out_dir  = os.path.join(REPORTS_DIR, report_name, 'mock_data')

    if not os.path.isdir(seed_dir):
        print(f'Seed folder not found:\n  {seed_dir}')
        print('Create it and place 10-row CSVs for each table.')
        sys.exit(1)

    seed_files = sorted(glob.glob(os.path.join(seed_dir, '*.csv')))
    if not seed_files:
        print(f'No CSV files found in: {seed_dir}')
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    print(f'\nTool 1.01 -- Mock Data Generator')
    print(f'Report    : {report_name}')
    print(f'Seed dir  : {seed_dir}')
    print(f'Output    : {out_dir}')
    print(f'Tables    : {len(seed_files)}')
    print(f'New rows  : {n_rows} per table  (seed rows also included)')

    # Dimension tables first (sorted alphabetically dim_ before fct_),
    # so FK pools are populated before fact tables are processed.
    dim_files = [f for f in seed_files if os.path.basename(f).startswith('dim_')]
    other_files = [f for f in seed_files if not os.path.basename(f).startswith('dim_')]
    ordered_files = dim_files + other_files

    id_pools = {}   # table -> [id values]  -- FK resolution registry

    for seed_path in ordered_files:
        rows, columns, table = generate_table(seed_path, n_rows, id_pools, verbose=verbose)
        if not rows:
            continue
        out_path = os.path.join(out_dir, f'{table}.csv')
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        seed_count = len(rows) - n_rows
        print(f'  {table:<42}  {seed_count} seed + {n_rows} generated = {len(rows)} rows')

    print(f'\nDone. Output: {out_dir}')


def main():
    ap = argparse.ArgumentParser(description='Tool 1.01 -- Mock Data Generator (POC only)')
    ap.add_argument('report', help='Report name (folder name under input/seed/)')
    ap.add_argument('--rows', type=int, default=1000,
                    help='Number of new rows to generate per table (default: 1000)')
    ap.add_argument('-v', '--verbose', action='store_true',
                    help='Show column type detection and FK mapping')
    args = ap.parse_args()

    generate_report(args.report, args.rows, verbose=args.verbose)


if __name__ == '__main__':
    main()
