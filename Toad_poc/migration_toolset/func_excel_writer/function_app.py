"""
func_excel_writer — Generic Excel Template Writer
==================================================
Azure Function (HTTP trigger) called from the ADF generic pipeline.

Receives report_name + report_date, then:
  1. Reads template_blob_path, template_container, output_container from config.report
  2. Downloads the .xlsm template from toad-poc-reports/templates/ (shared container)
  3. Downloads the CSV data written by Copy_ReportData_To_Blob (per-report container)
  4. Writes CSV data rows into the template's data sheet (keeps headers + VBA)
  5. Saves the populated .xlsm to {output_container}/output_Reports/ (per-report container)

Fully generic — zero report-specific logic.
All report configuration comes from config.report at runtime.

Environment variables (set in Azure Function App settings / Key Vault refs):
  SQL_CONNECTION_STRING     : ODBC connection string for config DB
  STORAGE_CONNECTION_STRING : Azure Storage account connection string

Request body (JSON):
  {
    "report_name": "BC_BIMIO_267_Daily",
    "report_date": "19.05.2026"
  }

Response (JSON):
  { "status": "ok", "output_blob": "output/BC_BIMIO_267_Daily_19.05.2026.xlsm" }
"""

import azure.functions as func
import csv
import datetime
import io
import json
import logging
import os
from typing import Optional

import openpyxl
import pymssql
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Config DB helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pymssql_connect():
    """Parse ODBC-format SQL_CONNECTION_STRING and return a pymssql connection."""
    raw = os.environ['SQL_CONNECTION_STRING']
    parts = {k.strip(): v.strip()
             for k, v in (p.split('=', 1) for p in raw.split(';') if '=' in p)}
    server = parts.get('Server', parts.get('SERVER', ''))
    server = server.replace('tcp:', '').split(',')[0]
    return pymssql.connect(
        server=server,
        user=parts.get('Uid', parts.get('UID', '')),
        password=parts.get('Pwd', parts.get('PWD', '')),
        database=parts.get('Database', parts.get('DATABASE', '')),
        port=1433,
        login_timeout=30,
    )


def _history_start(report_name: str) -> Optional[int]:
    """
    Insert an InProgress row into config.Report_Process_History.
    Returns the new History_id, or None if the insert fails (non-fatal).
    """
    try:
        with _pymssql_connect() as conn:
            cursor = conn.cursor()
            # Resolve report_id FK
            cursor.execute(
                "SELECT report_id FROM config.report WHERE report_name = %s",
                (report_name,)
            )
            row = cursor.fetchone()
            if not row:
                logger.warning("history_start: report not in config.report: %s", report_name)
                return None
            report_id = row[0]
            run_dt = datetime.datetime.utcnow()
            cursor.execute(
                """INSERT INTO [config].[Report_Process_History]
                       ([Report_id], [Report_Run_Datetime],
                        [Report_Process_Status], [Created_Datetime])
                   VALUES (%d, %s, 'InProgress', %s)""",
                (report_id, run_dt, run_dt)
            )
            cursor.execute("SELECT SCOPE_IDENTITY()")
            history_id = int(cursor.fetchone()[0])
            conn.commit()
            logger.info("history_start: report=%s  history_id=%d  status=InProgress",
                        report_name, history_id)
            return history_id
    except Exception as exc:
        logger.warning("history_start failed (non-fatal): %s", exc)
        return None


def _history_end(history_id: Optional[int], status: str):
    """
    Update Report_Process_Status to 'Success' or 'Failed'.
    Non-fatal — a logging failure must never mask a real report error.
    """
    if history_id is None:
        return
    try:
        with _pymssql_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE [config].[Report_Process_History]
                   SET    [Report_Process_Status] = %s
                   WHERE  [History_id] = %d""",
                (status, history_id)
            )
            conn.commit()
            logger.info("history_end: history_id=%d  status=%s", history_id, status)
    except Exception as exc:
        logger.warning("history_end failed (non-fatal): %s", exc)


def _get_report_config(report_name: str) -> dict:
    """Read template_blob_path, template_container and output_container from config.report."""
    with _pymssql_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT template_blob_path, template_container, output_container
            FROM   config.report
            WHERE  report_name = %s
            AND    is_active   = 'Y'
            """,
            (report_name,)
        )
        row = cursor.fetchone()

    if not row:
        raise ValueError(f"Report not found in config.report: {report_name}")

    template_blob_path, template_container, output_container = row
    if not template_blob_path:
        raise ValueError(f"No template_blob_path configured for: {report_name}")

    # Fall back to 'toad-poc-reports' if the column is NULL (older rows)
    if not template_container:
        template_container = 'toad-poc-reports'

    return {
        'template_blob_path': template_blob_path,    # e.g. 'templates/BIMIO 267...xlsm'
        'template_container': template_container,    # e.g. 'toad-poc-reports'
        'output_container':   output_container,      # e.g. 'bc-bimio-267-daily'
    }


# ─────────────────────────────────────────────────────────────────────────────
# Blob helpers
# ─────────────────────────────────────────────────────────────────────────────

def _blob_client():
    return BlobServiceClient.from_connection_string(os.environ['STORAGE_CONNECTION_STRING'])


def _download_blob(blob_svc: BlobServiceClient, container: str, blob_name: str) -> bytes:
    logger.info("Downloading blob: %s / %s", container, blob_name)
    return (blob_svc
            .get_blob_client(container=container, blob=blob_name)
            .download_blob()
            .readall())


def _upload_blob(blob_svc: BlobServiceClient, container: str, blob_name: str, data: bytes):
    logger.info("Uploading blob: %s / %s  (%d bytes)", container, blob_name, len(data))
    blob_svc.get_blob_client(container=container, blob=blob_name).upload_blob(data, overwrite=True)


# ─────────────────────────────────────────────────────────────────────────────
# Excel writer
# ─────────────────────────────────────────────────────────────────────────────

def _find_data_sheet(wb: openpyxl.Workbook) -> openpyxl.worksheet.worksheet.Worksheet:
    """
    Return the worksheet to write data into.
    Convention: prefer a sheet named 'Data' or 'Sheet1'; fall back to the active sheet.
    """
    for candidate in ('Data', 'Sheet1', 'Sheet'):
        if candidate in wb.sheetnames:
            return wb[candidate]
    return wb.active


def _write_csv_into_template(template_bytes: bytes, csv_bytes: bytes) -> bytes:
    """
    Open the xlsm template, clear data rows (keep row 1 as header),
    write CSV rows starting at row 2, return the populated workbook as bytes.
    """
    wb = openpyxl.load_workbook(io.BytesIO(template_bytes), keep_vba=True)
    ws = _find_data_sheet(wb)

    # Remove all data rows below the header
    max_row = ws.max_row
    if max_row > 1:
        ws.delete_rows(2, max_row - 1)

    # Parse CSV — skip its own header row (template already has headers)
    text = csv_bytes.decode('utf-8-sig')
    reader = csv.reader(io.StringIO(text))
    next(reader, None)  # skip CSV header line

    for row_data in reader:
        ws.append(row_data)

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# HTTP trigger
# ─────────────────────────────────────────────────────────────────────────────

@app.route(route="excel_writer", methods=["POST"])
def excel_writer(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generic Excel template writer — called by ADF PL_Generic_* pipelines.

    Reads config at runtime so the same function handles every report.
    """
    # ── Parse request ─────────────────────────────────────────────────────────
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Request body must be JSON", status_code=400)

    report_name = (body.get('report_name') or '').strip()
    report_date = (body.get('report_date') or '').strip()

    if not report_name:
        return func.HttpResponse("Missing required field: report_name", status_code=400)
    if not report_date:
        return func.HttpResponse("Missing required field: report_date", status_code=400)

    logger.info("excel_writer called: report_name=%s  report_date=%s", report_name, report_date)

    # ── Log process start (InProgress) ────────────────────────────────────────
    history_id = _history_start(report_name)

    try:
        # ── 1. Read config ────────────────────────────────────────────────────
        cfg                = _get_report_config(report_name)
        output_container   = cfg['output_container']
        tmpl_container     = cfg['template_container']   # shared 'toad-poc-reports'
        tmpl_blob_name     = cfg['template_blob_path']   # 'templates/file.xlsm'

        # ── 2. Download inputs from Blob ──────────────────────────────────────
        blob_svc      = _blob_client()
        csv_blob_name = f"output_csv/{report_name}_{report_date}.csv"

        csv_bytes      = _download_blob(blob_svc, output_container, csv_blob_name)
        template_bytes = _download_blob(blob_svc, tmpl_container,   tmpl_blob_name)

        # ── 3. Populate template ──────────────────────────────────────────────
        xlsm_bytes = _write_csv_into_template(template_bytes, csv_bytes)

        # ── 4. Upload populated xlsm ──────────────────────────────────────────
        output_blob_name = f"output_Reports/{report_name}_{report_date}.xlsm"
        _upload_blob(blob_svc, output_container, output_blob_name, xlsm_bytes)

        logger.info("excel_writer complete: %s / %s", output_container, output_blob_name)

        # ── Log success ───────────────────────────────────────────────────────
        _history_end(history_id, 'Success')

        return func.HttpResponse(
            json.dumps({
                "status":      "ok",
                "report_name": report_name,
                "report_date": report_date,
                "output_blob": f"{output_container}/{output_blob_name}",
            }),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as exc:
        logger.warning("excel_writer config error: %s", exc)
        _history_end(history_id, 'Failed')
        return func.HttpResponse(str(exc), status_code=404)

    except Exception as exc:
        logger.exception("excel_writer failed for %s: %s", report_name, exc)
        _history_end(history_id, 'Failed')
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(exc)}),
            mimetype="application/json",
            status_code=500
        )
