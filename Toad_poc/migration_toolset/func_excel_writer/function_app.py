"""
func_excel_writer — Generic Excel Template Writer
==================================================
Azure Function (HTTP trigger) called from the ADF generic pipeline.

Receives report_name + report_date, then:
  1. Reads template_blob_path and output_container from config.report
  2. Downloads the .xlsm template from Blob Storage (templates/ container)
  3. Downloads the CSV data written by Copy_ReportData_To_Blob
  4. Writes CSV data rows into the template's data sheet (keeps headers + VBA)
  5. Saves the populated .xlsm back to Blob as the report output file

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
import io
import json
import logging
import os

import openpyxl
import pyodbc
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Config DB helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_report_config(report_name: str) -> dict:
    """Read template_blob_path and output_container from config.report."""
    conn_str = os.environ['SQL_CONNECTION_STRING']
    with pyodbc.connect(conn_str, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT template_blob_path, output_container
            FROM   config.report
            WHERE  report_name = ?
            AND    is_active   = 'Y'
            """,
            (report_name,)
        )
        row = cursor.fetchone()

    if not row:
        raise ValueError(f"Report not found in config.report: {report_name}")

    template_blob_path, output_container = row
    if not template_blob_path:
        raise ValueError(f"No template_blob_path configured for: {report_name}")

    return {
        'template_blob_path': template_blob_path,   # e.g. 'templates/BC_BIMIO_267_Daily/BIMIO 267...xlsm'
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

    try:
        # ── 1. Read config ────────────────────────────────────────────────────
        cfg              = _get_report_config(report_name)
        output_container = cfg['output_container']
        template_path    = cfg['template_blob_path']   # 'templates/ReportName/file.xlsm'

        # Split template_blob_path into container + blob_name
        # Convention: first segment is the container name ('templates')
        path_parts        = template_path.split('/', 1)
        tmpl_container    = path_parts[0]
        tmpl_blob_name    = path_parts[1] if len(path_parts) > 1 else template_path

        # ── 2. Download inputs from Blob ──────────────────────────────────────
        blob_svc      = _blob_client()
        csv_blob_name = f"output/{report_name}_{report_date}.csv"

        csv_bytes      = _download_blob(blob_svc, output_container, csv_blob_name)
        template_bytes = _download_blob(blob_svc, tmpl_container,   tmpl_blob_name)

        # ── 3. Populate template ──────────────────────────────────────────────
        xlsm_bytes = _write_csv_into_template(template_bytes, csv_bytes)

        # ── 4. Upload populated xlsm ──────────────────────────────────────────
        output_blob_name = f"output/{report_name}_{report_date}.xlsm"
        _upload_blob(blob_svc, output_container, output_blob_name, xlsm_bytes)

        logger.info("excel_writer complete: %s / %s", output_container, output_blob_name)

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
        return func.HttpResponse(str(exc), status_code=404)

    except Exception as exc:
        logger.exception("excel_writer failed for %s: %s", report_name, exc)
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(exc)}),
            mimetype="application/json",
            status_code=500
        )
