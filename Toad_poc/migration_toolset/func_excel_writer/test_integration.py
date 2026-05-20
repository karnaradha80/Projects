"""
test_integration.py — Integration test for func-excel-writer.
Calls the full function end-to-end against the real POC Azure resources.

Requires local.settings.json to be populated with real connection strings.
Copy local.settings.json.template → local.settings.json and fill in values.

Usage:
    python test_integration.py
    python test_integration.py BC_BIMIO_267_Daily 19.05.2026
"""

import json
import os
import sys

# ── Load local.settings.json into env before importing the function ───────────
_settings_path = os.path.join(os.path.dirname(__file__), 'local.settings.json')
if not os.path.exists(_settings_path):
    print("ERROR: local.settings.json not found.")
    print("  Copy local.settings.json.template to local.settings.json")
    print("  and fill in SQL_CONNECTION_STRING and STORAGE_CONNECTION_STRING.")
    sys.exit(1)

with open(_settings_path) as _f:
    _settings = json.load(_f)
for _k, _v in _settings.get('Values', {}).items():
    os.environ.setdefault(_k, _v)

# ── Check required env vars are set ──────────────────────────────────────────
for _required in ('SQL_CONNECTION_STRING', 'STORAGE_CONNECTION_STRING'):
    val = os.environ.get(_required, '')
    if not val or val.startswith('<'):
        print(f"ERROR: {_required} is not set in local.settings.json.")
        sys.exit(1)

# ── Imports (after env vars loaded) ──────────────────────────────────────────
import azure.functions as func
from function_app import excel_writer


def _make_request(report_name: str, report_date: str) -> func.HttpRequest:
    body = json.dumps({
        'report_name': report_name,
        'report_date': report_date,
    }).encode('utf-8')
    return func.HttpRequest(
        method='POST',
        body=body,
        url='/api/excel_writer',
        headers={'Content-Type': 'application/json'},
        params={}
    )


def run_test(report_name: str, report_date: str):
    print(f"\n{'='*60}")
    print(f"  Integration test: func-excel-writer")
    print(f"  report_name : {report_name}")
    print(f"  report_date : {report_date}")
    print(f"{'='*60}")

    # ── Test 1: valid request ─────────────────────────────────────────────────
    print("\n[1] Valid request...")
    req = _make_request(report_name, report_date)
    resp = excel_writer(req)
    body = resp.get_body().decode()

    if resp.status_code == 200:
        result = json.loads(body)
        print(f"    Status  : {resp.status_code} OK")
        print(f"    Output  : {result.get('output_blob')}")
        print(f"    PASSED")
    else:
        print(f"    Status  : {resp.status_code}")
        print(f"    Body    : {body}")
        print(f"    FAILED -- check logs above for details")

    # ── Test 2: missing report_name ───────────────────────────────────────────
    print("\n[2] Missing report_name (expect 400)...")
    bad_body = json.dumps({'report_date': report_date}).encode()
    bad_req = func.HttpRequest(method='POST', body=bad_body,
                               url='/api/excel_writer',
                               headers={'Content-Type': 'application/json'},
                               params={})
    resp2 = excel_writer(bad_req)
    status = '  PASSED' if resp2.status_code == 400 else '  FAILED'
    print(f"    Status  : {resp2.status_code}  {status}")

    # ── Test 3: unknown report ────────────────────────────────────────────────
    print("\n[3] Unknown report name (expect 404)...")
    req3 = _make_request('UNKNOWN_REPORT_XYZ', report_date)
    resp3 = excel_writer(req3)
    status = '  PASSED' if resp3.status_code == 404 else '  FAILED'
    print(f"    Status  : {resp3.status_code}  {status}")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    report_name = sys.argv[1] if len(sys.argv) > 1 else 'BC_BIMIO_267_Daily'
    report_date = sys.argv[2] if len(sys.argv) > 2 else '19.05.2026'
    run_test(report_name, report_date)
