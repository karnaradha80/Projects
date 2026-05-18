"""
Tool 1 - Toad XML Sanitizer
============================
Reads raw Toad XML files from migration_toolset/input/
Replaces all sensitive values with consistent mock values.
Writes:
  - migration_toolset/reports/{report}/sanitized/{report}_sanitized.txt
  - migration_toolset/reports/{report}/sanitized/{report}_mapping.csv   (per-report subset)
  - migration_toolset/global/mapping_registry.csv                        (global, cumulative)

Usage:
  python tool1_sanitize.py                        # process all files in input/
  python tool1_sanitize.py MyReport.txt           # process specific file
  python tool1_sanitize.py MyReport.txt -v        # verbose output
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils.xml_parser import ToadXmlParser
from utils.mapping_registry import MappingRegistry

BASE_DIR         = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGISTRY_PATH    = os.path.join(BASE_DIR, 'global', 'mapping_registry.csv')
INPUT_DIR        = os.path.join(BASE_DIR, 'input')
REPORTS_DIR      = os.path.join(BASE_DIR, 'reports')
MAPPING_COLS     = ['original_value', 'mock_value', 'category']

ACTUAL_MAP_DIR   = os.path.join(BASE_DIR, 'global', 'actual_mapping_files')
POC_MAP_DIR      = os.path.join(BASE_DIR, 'global', 'poc_mapping_files')
POC_CONFIG_PATH  = os.path.join(BASE_DIR, 'global', 'poc_team_config.json')
FINAL_ACTUAL     = os.path.join(BASE_DIR, 'global', 'final_actual_mapping.csv')
FINAL_POC        = os.path.join(BASE_DIR, 'global', 'final_poc_mapping.csv')


# ─────────────────────────────────────────────────────────────────────────────
# Email mapping files
# ─────────────────────────────────────────────────────────────────────────────

def _load_poc_emails():
    """Return list of {email, group, type} dicts from poc_team_config.json."""
    if not os.path.exists(POC_CONFIG_PATH):
        return []
    with open(POC_CONFIG_PATH, encoding='utf-8') as f:
        return json.load(f).get('poc_team_emails', [])


def _write_email_mapping_files(report_name, touched):
    """
    Write per-report email mapping files and regenerate both final consolidated files.
    Called at the end of every sanitize_file() run.

    actual_mapping_files/{report}_actual_mapping.csv  -- real emails    (SENSITIVE)
    poc_mapping_files/{report}_poc_mapping.csv         -- mock emails    (safe)
    final_actual_mapping.csv  -- DISTINCT (report, real_email)           (SENSITIVE)
    final_poc_mapping.csv     -- every report x poc team emails          (safe)
    """
    # Deduplicate EMAIL rows from touched list
    seen, email_rows = set(), []
    for orig, mock, cat in touched:
        if cat == 'EMAIL' and orig not in seen:
            email_rows.append((orig, mock))
            seen.add(orig)

    # Per-report actual mapping (real emails)
    os.makedirs(ACTUAL_MAP_DIR, exist_ok=True)
    with open(os.path.join(ACTUAL_MAP_DIR, f'{report_name}_actual_mapping.csv'),
              'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['report_name', 'real_email_address'])
        for orig, _ in email_rows:
            w.writerow([report_name, orig])

    # Per-report poc mapping (mock emails)
    os.makedirs(POC_MAP_DIR, exist_ok=True)
    with open(os.path.join(POC_MAP_DIR, f'{report_name}_poc_mapping.csv'),
              'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['report_name', 'mock_email_address'])
        for _, mock in email_rows:
            w.writerow([report_name, mock])

    # Rebuild final_actual_mapping.csv -- DISTINCT (report, real_email) across all reports
    all_actual = set()
    for path in sorted(glob.glob(os.path.join(ACTUAL_MAP_DIR, '*_actual_mapping.csv'))):
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                all_actual.add((row['report_name'], row['real_email_address']))

    with open(FINAL_ACTUAL, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['report_name', 'real_email_address'])
        for rpt, email in sorted(all_actual):
            w.writerow([rpt, email])

    # Rebuild final_poc_mapping.csv -- all distinct reports x poc team emails from config
    poc_emails = _load_poc_emails()
    if poc_emails:
        all_reports = sorted({row[0] for row in all_actual})
        with open(FINAL_POC, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['report_name', 'poc_email_address', 'recipient_group', 'email_type'])
            for rpt in all_reports:
                for entry in poc_emails:
                    w.writerow([rpt, entry['email'], entry['group'], entry['type']])

    return len(email_rows)


def sanitize_file(xml_path, registry, verbose=False):
    report_file = os.path.basename(xml_path)
    print(f'\n  Processing : {report_file}')

    # -- Parse ---------------------------------------------------------
    parser = ToadXmlParser(xml_path)
    parser.parse()
    s = parser.summary()
    report_name = s['report_name'] or os.path.splitext(report_file)[0]

    if verbose:
        print(f'  Report name: {report_name}')
        print(f'  Emails     : {len(s["emails"])}')
        print(f'  Passwords  : {len(s["passwords"])}')
        print(f'  Servers    : {len(s["servers"])}')
        print(f'  Schemas    : {len(s["oracle_schemas"])}')
        print(f'  Accounts   : {len(s["usernames"])}')
        print(f'  DSNs       : {len(s["dsns"])}')
        print(f'  UNC paths  : {len(s["unc_paths"])}')
        print(f'  SMTP       : {len(s["smtp_servers"])}')
        print(f'  Pipeline   : {len(s["pipeline_steps"])} steps')

    # -- Build replacement map -----------------------------------------
    content = parser.raw
    touched = []   # (original, mock, category) -- in replacement order

    def sub(original, category):
        mock = registry.get_or_create(original, category, report_name)
        touched.append((original, mock, category))
        return mock

    # Order matters: longest/most specific first to avoid partial matches.

    def ireplace(text, original, replacement):
        """Case-insensitive string replacement."""
        return re.sub(re.escape(original), lambda _: replacement, text, flags=re.IGNORECASE)

    # 1. Passwords -- longest first to prevent partial matches (e.g. 123456 inside 123456789)
    for pwd in sorted(s['passwords'], key=len, reverse=True):
        mock = sub(pwd, 'PASSWORD')
        content = ireplace(content, pwd, mock)

    # 2. UNC paths (longest first -- paths share common prefixes)
    for path in s['unc_paths']:
        mock = sub(path, 'PATH')
        content = ireplace(content, path.replace('\\', '\\\\'), mock.replace('\\', '\\\\'))
        content = ireplace(content, path, mock)

    # 3. Emails -- case-insensitive (XML may have mixed case in UserName= attributes)
    for email in s['emails']:
        mock = sub(email, 'EMAIL')
        content = ireplace(content, email, mock)

    # 4. Oracle schemas (before server names -- schema names may appear in server strings)
    for schema in s['oracle_schemas']:
        mock = sub(schema, 'SCHEMA')
        content = ireplace(content, schema, mock)

    # 5. Servers
    for server in s['servers']:
        mock = sub(server, 'SERVER')
        content = ireplace(content, server, mock)

    # 6. Service accounts / usernames
    for account in s['usernames']:
        mock = sub(account, 'ACCOUNT')
        content = ireplace(content, account, mock)

    # 7. DSNs (replace space-form and URL-encoded form)
    for dsn in s['dsns']:
        mock = sub(dsn, 'DSN')
        dsn_encoded = dsn.replace(' ', '+')
        mock_encoded = mock.replace(' ', '+')
        content = ireplace(content, dsn_encoded, mock_encoded)
        content = ireplace(content, dsn, mock)

    # 8. SMTP servers
    for smtp in s['smtp_servers']:
        mock = sub(smtp, 'SMTP_SERVER')
        content = ireplace(content, smtp, mock)

    # -- Write sanitized XML -------------------------------------------
    out_dir = os.path.join(REPORTS_DIR, report_name, 'sanitized')
    os.makedirs(out_dir, exist_ok=True)

    sanitized_path = os.path.join(out_dir, f'{report_name}_sanitized.txt')
    with open(sanitized_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # -- Write per-report mapping CSV ----------------------------------
    mapping_path = os.path.join(out_dir, f'{report_name}_mapping.csv')
    seen = set()
    rows = []
    for original, mock, category in touched:
        if original not in seen:
            rows.append({'original_value': original, 'mock_value': mock, 'category': category})
            seen.add(original)

    with open(mapping_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=MAPPING_COLS)
        writer.writeheader()
        writer.writerows(rows)

    # Write per-report email mapping files + regenerate final consolidated files
    email_count = _write_email_mapping_files(report_name, touched)

    print(f'  Sanitized  : {sanitized_path}')
    print(f'  Mapping    : {mapping_path}')
    print(f'  Replaced   : {len(rows)} unique values  ({email_count} emails)')
    print(f'  Email maps : actual_mapping_files/ and poc_mapping_files/ updated')
    return report_name


def main():
    ap = argparse.ArgumentParser(description='Tool 1 -- Toad XML Sanitizer')
    ap.add_argument('files', nargs='*', help='XML files to sanitize (default: all in input/)')
    ap.add_argument('-v', '--verbose', action='store_true', help='Show per-file extraction details')
    args = ap.parse_args()

    registry = MappingRegistry(REGISTRY_PATH)

    # Resolve files
    files = []
    for f in args.files:
        if os.path.isabs(f):
            files.append(f)
        else:
            files.append(os.path.join(INPUT_DIR, f))

    if not files:
        files = sorted(
            glob.glob(os.path.join(INPUT_DIR, '*.txt')) +
            glob.glob(os.path.join(INPUT_DIR, '*.xml'))
        )

    if not files:
        print(f'No files found. Place Toad XML files in:\n  {INPUT_DIR}')
        sys.exit(1)

    print(f'Tool 1 -- Sanitizer')
    print(f'Input dir  : {INPUT_DIR}')
    print(f'Registry   : {REGISTRY_PATH}')
    print(f'Files      : {len(files)}')

    for f in files:
        if not os.path.exists(f):
            print(f'\n  SKIP (not found): {f}')
            continue
        sanitize_file(f, registry, verbose=args.verbose)

    print(f'\nGlobal registry  : {REGISTRY_PATH}')
    print(f'Final actual map : {FINAL_ACTUAL}')
    print(f'Final poc map    : {FINAL_POC}')
    print('Done.')


if __name__ == '__main__':
    main()
