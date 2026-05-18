"""
Tool 5 - Blob Storage Upload Scripts
======================================
Extracts the expected .xlsm template filename from the sanitised Toad XML.
Checks whether the file has been placed in global/xlsm_templates/{report_name}/.
Generates ready-to-run upload scripts (PowerShell + bash) for az storage blob upload.

Does NOT connect to Azure or execute any az CLI commands.
The generated scripts are reviewed and run by the user when ready.

Blob Storage target layout:
  templates/
    {report_name}/
      {template_filename}.xlsm    <- report template

Input  : reports/{report}/sanitized/{report}_sanitized.txt
       : global/xlsm_templates/{report_name}/*.xlsm   (user-supplied)
       : reports/{report}/adf/arm_template_parameters.json  (for storage account name)
Output : reports/{report}/blob/
             upload_{report}.ps1
             upload_{report}.sh
             blob_checklist.txt

Usage:
  python tool5_blob_upload.py <report_name> [-v]
  python tool5_blob_upload.py BC_BIMIO_267_Daily
  python tool5_blob_upload.py BC_BIMIO_267_Daily -v
"""

import argparse
import glob
import json
import os
import re
import sys

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
GLOBAL_DIR  = os.path.join(BASE_DIR, 'global')

BLOB_CONTAINER = 'templates'


# ─────────────────────────────────────────────────────────────────────────────
# XML helpers
# ─────────────────────────────────────────────────────────────────────────────

def _decode(text):
    return (text
            .replace('&#xD;&#xA;', '\n').replace('&#xD;', '\r').replace('&#xA;', '\n')
            .replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"'))


# ─────────────────────────────────────────────────────────────────────────────
# Template file extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_template_files(decoded):
    """
    Return a list of dicts describing each xlsm template referenced in the XML:
      { 'filename': str, 'source': str (sanitised UNC path), 'via': str }

    Sources checked (in order):
    1. CopyFileActivity DestinationFileName  (most reliable -- explicit xlsm name)
    2. FileDescription Description            (email attachment label)
    3. BodyFileName attributes               (fallback UNC paths -- filename only)
    """
    found = {}   # filename -> dict  (deduplicate by filename)

    # 1. CopyFileActivity -- DestinationFileName usually has the xlsm name
    for m in re.finditer(
            r'CopyFileActivity[^>]*SourceFileName="([^"]*)"[^>]*DestinationFileName="([^"]*)"',
            decoded, re.IGNORECASE | re.DOTALL):
        src  = m.group(1)
        dest = m.group(2)
        if dest.lower().endswith('.xlsm'):
            fname = os.path.basename(dest)
            if fname not in found:
                found[fname] = {'filename': fname, 'source': src, 'via': 'CopyFileActivity'}

    # Also try reversed attribute order
    for m in re.finditer(
            r'CopyFileActivity[^>]*DestinationFileName="([^"]*)"[^>]*SourceFileName="([^"]*)"',
            decoded, re.IGNORECASE | re.DOTALL):
        dest = m.group(1)
        src  = m.group(2)
        if dest.lower().endswith('.xlsm'):
            fname = os.path.basename(dest)
            if fname not in found:
                found[fname] = {'filename': fname, 'source': src, 'via': 'CopyFileActivity'}

    # 2. FileDescription Description="Copy_N: filename.xlsm"
    for m in re.finditer(
            r'FileDescription[^>]*Description="(?:Copy_\d+:\s*)?([^"]*\.xlsm)"',
            decoded, re.IGNORECASE):
        fname = os.path.basename(m.group(1).strip())
        if fname and fname not in found:
            found[fname] = {'filename': fname, 'source': '', 'via': 'FileDescription'}

    # 3. BodyFileName -- UNC path, grab the filename portion
    for m in re.finditer(r'BodyFileName="([^"]+)"', decoded, re.IGNORECASE):
        path = m.group(1)
        fname = os.path.basename(path)
        if fname.lower().endswith('.xlsm') and fname not in found:
            found[fname] = {'filename': fname, 'source': path, 'via': 'BodyFileName'}

    return list(found.values())


def extract_log_files(decoded):
    """Return list of automation log filenames referenced in FileDescription."""
    logs = []
    for m in re.finditer(
            r'FileDescription[^>]*FileName="([^"]*\.log)"',
            decoded, re.IGNORECASE):
        fname = m.group(1).strip()
        if fname:
            logs.append(fname)
    return logs


def get_storage_account(report_name):
    """Read storage_account_name from the report's parameters file, if present."""
    params_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template_parameters.json')
    if not os.path.exists(params_path):
        return '<your-storage-account>'
    try:
        with open(params_path, encoding='utf-8') as f:
            data = json.load(f)
        return data['parameters'].get('storage_account_name', {}).get('value', '<your-storage-account>')
    except Exception:
        return '<your-storage-account>'


# ─────────────────────────────────────────────────────────────────────────────
# Script builders
# ─────────────────────────────────────────────────────────────────────────────

_PS1_TEMPLATE = """\
# =============================================================
# Blob Upload: {report_name} xlsm templates
# Generated by Tool 5 -- review before running.
# =============================================================
# Prerequisites:
#   az CLI installed   : https://learn.microsoft.com/cli/azure/install-azure-cli
#   az login           : run 'az login' or set AZURE_STORAGE_KEY env var
#   Templates present  : place .xlsm files in global\\xlsm_templates\\{report_name}\\
# =============================================================

$ErrorActionPreference = 'Stop'

# -- Configuration -------------------------------------------
$STORAGE_ACCOUNT = '{storage_account}'
$CONTAINER       = '{container}'
$LOCAL_DIR       = '{local_dir}'
$REPORT_NAME     = '{report_name}'

# -- Upload each template ------------------------------------
{upload_blocks}
Write-Host "All templates uploaded for $REPORT_NAME."
"""

_SH_TEMPLATE = """\
#!/usr/bin/env bash
# =============================================================
# Blob Upload: {report_name} xlsm templates
# Generated by Tool 5 -- review before running.
# =============================================================
# Prerequisites:
#   az CLI installed   : https://learn.microsoft.com/cli/azure/install-azure-cli
#   az login           : run 'az login' or set AZURE_STORAGE_KEY env var
#   Templates present  : place .xlsm files in global/xlsm_templates/{report_name}/
# =============================================================

set -euo pipefail

# -- Configuration -------------------------------------------
STORAGE_ACCOUNT="{storage_account}"
CONTAINER="{container}"
LOCAL_DIR="{local_dir_fwd}"
REPORT_NAME="{report_name}"

# -- Upload each template ------------------------------------
{upload_blocks}
echo "All templates uploaded for $REPORT_NAME."
"""

_PS1_BLOCK = """\
Write-Host "Uploading: {blob_name} ..."
az storage blob upload `
    --account-name $STORAGE_ACCOUNT `
    --container-name $CONTAINER `
    --name "{blob_name}" `
    --file "$LOCAL_DIR\\{filename}" `
    --auth-mode login `
    --overwrite
"""

_SH_BLOCK = """\
echo "Uploading: {blob_name} ..."
az storage blob upload \\
    --account-name "$STORAGE_ACCOUNT" \\
    --container-name "$CONTAINER" \\
    --name "{blob_name}" \\
    --file "$LOCAL_DIR/{filename}" \\
    --auth-mode login \\
    --overwrite
"""


def _norm(p):
    return p.replace('\\', '/')


def build_scripts(report_name, templates, storage_account, local_dir, out_dir):
    """Write PS1 + SH upload scripts. Returns (ps1_path, sh_path)."""
    safe = re.sub(r'[^A-Za-z0-9_]', '_', report_name)

    ps1_blocks, sh_blocks = [], []
    for t in templates:
        blob_name = f'{report_name}/{t["filename"]}'
        fname = t['filename']
        ps1_blocks.append(_PS1_BLOCK.format(blob_name=blob_name, filename=fname))
        sh_blocks.append(_SH_BLOCK.format(blob_name=blob_name, filename=fname))

    if not ps1_blocks:
        ps1_blocks = ['# No xlsm templates detected in sanitised XML.\n']
        sh_blocks  = ['# No xlsm templates detected in sanitised XML.\n']

    ps1 = _PS1_TEMPLATE.format(
        report_name=report_name,
        storage_account=storage_account,
        container=BLOB_CONTAINER,
        local_dir=local_dir,
        upload_blocks=''.join(ps1_blocks)
    )
    sh = _SH_TEMPLATE.format(
        report_name=report_name,
        storage_account=storage_account,
        container=BLOB_CONTAINER,
        local_dir=local_dir,
        local_dir_fwd=_norm(local_dir),
        upload_blocks=''.join(sh_blocks)
    )

    ps1_path = os.path.join(out_dir, f'upload_{safe}.ps1')
    sh_path  = os.path.join(out_dir, f'upload_{safe}.sh')

    with open(ps1_path, 'w', encoding='utf-8') as f:
        f.write(ps1)
    with open(sh_path, 'w', encoding='utf-8') as f:
        f.write(sh)

    return ps1_path, sh_path


# ─────────────────────────────────────────────────────────────────────────────
# Checklist
# ─────────────────────────────────────────────────────────────────────────────

def build_checklist(report_name, templates, local_dir, storage_account):
    safe = re.sub(r'[^A-Za-z0-9_]', '_', report_name)
    lines = []
    lines.append('=' * 60)
    lines.append(f'BLOB UPLOAD CHECKLIST  --  {report_name}')
    lines.append('=' * 60)
    lines.append('')

    lines.append('EXPECTED TEMPLATES')
    lines.append('-' * 40)
    if not templates:
        lines.append('  No xlsm templates found in sanitised XML.')
    else:
        for t in templates:
            local_path = os.path.join(local_dir, t['filename'])
            exists = os.path.isfile(local_path)
            status = '[OK] present' if exists else '[!!] MISSING'
            blob   = f'{BLOB_CONTAINER}/{report_name}/{t["filename"]}'
            lines.append(f'  {status}')
            lines.append(f'    Local  : {local_path}')
            lines.append(f'    Blob   : {blob}')
            lines.append(f'    Detect : via {t["via"]}')
            if t.get('source'):
                lines.append(f'    Origin : {t["source"]}  (sanitised UNC)')
            lines.append('')

    lines.append('STORAGE ACCOUNT')
    lines.append('-' * 40)
    if storage_account.startswith('<'):
        lines.append(f'  [!!] {storage_account}  <-- fill in arm_template_parameters.json')
    else:
        lines.append(f'  [OK] {storage_account}')
    lines.append('')

    missing_files = [t for t in templates
                     if not os.path.isfile(os.path.join(local_dir, t['filename']))]

    lines.append('ACTION REQUIRED')
    lines.append('-' * 40)
    if missing_files:
        lines.append(f'  Place the following file(s) in:')
        lines.append(f'  {local_dir}')
        for t in missing_files:
            lines.append(f'    {t["filename"]}')
        lines.append('')
    if storage_account.startswith('<'):
        lines.append('  Fill storage_account_name in arm_template_parameters.json')
        lines.append('')

    lines.append('UPLOAD SCRIPT')
    lines.append('-' * 40)
    lines.append(f'  reports/{report_name}/blob/upload_{safe}.ps1  (or .sh)')
    lines.append('')

    missing_count = len(missing_files) + (1 if storage_account.startswith('<') else 0)
    status = 'READY TO UPLOAD' if missing_count == 0 else f'NOT READY  ({missing_count} issue(s))'
    lines.append(f'STATUS: {status}')
    lines.append('=' * 60)
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def generate_upload(report_name, verbose=False):
    xml_path  = os.path.join(REPORTS_DIR, report_name, 'sanitized', f'{report_name}_sanitized.txt')
    local_dir = os.path.join(GLOBAL_DIR, 'xlsm_templates', report_name)
    out_dir   = os.path.join(REPORTS_DIR, report_name, 'blob')

    if not os.path.exists(xml_path):
        print(f'Sanitised XML not found: {xml_path}')
        print('Run Tool 1 first.')
        sys.exit(1)

    with open(xml_path, encoding='utf-8', errors='replace') as f:
        raw = f.read()
    decoded = _decode(raw)

    # ── Extract ───────────────────────────────────────────────────────────────
    templates       = extract_template_files(decoded)
    log_files       = extract_log_files(decoded)
    storage_account = get_storage_account(report_name)

    print(f'\nTool 5 -- Blob Upload Scripts')
    print(f'Report   : {report_name}')
    print(f'Storage  : {storage_account}')
    print(f'Container: {BLOB_CONTAINER}')
    print(f'Local dir: {local_dir}')
    print(f'Templates: {len(templates)} xlsm file(s) detected')

    if verbose:
        for t in templates:
            local_path = os.path.join(local_dir, t['filename'])
            present = 'present' if os.path.isfile(local_path) else 'MISSING'
            print(f'    [{present}]  {t["filename"]}  (via {t["via"]})')
            if t.get('source'):
                print(f'              origin: {t["source"]}')
        if log_files:
            print(f'  Log file(s) referenced (not uploaded): {log_files}')

    # ── Check local xlsm folder ───────────────────────────────────────────────
    os.makedirs(local_dir, exist_ok=True)
    present = glob.glob(os.path.join(local_dir, '*.xlsm'))
    if present:
        print(f'  Found {len(present)} xlsm file(s) already in local dir:')
        for p in present:
            print(f'    {os.path.basename(p)}')
    else:
        print(f'  No xlsm files in {local_dir} yet')
        print(f'  Place .xlsm files there before running the upload script')

    # ── Generate scripts ──────────────────────────────────────────────────────
    os.makedirs(out_dir, exist_ok=True)
    ps1_path, sh_path = build_scripts(
        report_name, templates, storage_account, local_dir, out_dir
    )
    safe = re.sub(r'[^A-Za-z0-9_]', '_', report_name)
    print(f'  Script : upload_{safe}.ps1  /  .sh')

    # ── Checklist ─────────────────────────────────────────────────────────────
    checklist = build_checklist(report_name, templates, local_dir, storage_account)
    checklist_path = os.path.join(out_dir, 'blob_checklist.txt')
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    print(f'  Check  : blob_checklist.txt')

    print(f'\n{checklist}')


def main():
    ap = argparse.ArgumentParser(description='Tool 5 -- Blob Upload Scripts')
    ap.add_argument('report', help='Report name (folder under reports/)')
    ap.add_argument('-v', '--verbose', action='store_true',
                    help='Show template file details')
    args = ap.parse_args()
    generate_upload(args.report, verbose=args.verbose)


if __name__ == '__main__':
    main()
