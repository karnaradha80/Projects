"""
BC_BIMIO_267_Daily — Local POC Pipeline
Replicates the Toad Automation Script pipeline logic using CSV sample data.
Outputs: Excel report (.xlsx) + archived copy with date suffix.
"""

import os
import shutil
import logging
import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR      = os.path.join(BASE_DIR, "sample_data")
OUTPUT_DIR    = os.path.join(BASE_DIR, "output")
ARCHIVE_DIR   = os.path.join(OUTPUT_DIR, "archive")
TEMPLATE_FILE = os.path.join(BASE_DIR, "toad_generated_reports", "BC_BIMIO_267_TEMPLATE.xlsm")
PRECOPY_FILE  = os.path.join(OUTPUT_DIR, "BC_BIMIO_267_PRECOPY.xlsm")

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Step 1: ODS Refresh Check ──────────────────────────────────────────────────
def check_ods_refresh():
    """Replicates: SELECT * FROM MAXRPD.T_ODS_LOG WHERE trunc(ems) = trunc(sysdate)"""
    log.info("Step 1 — Checking ODS refresh status...")
    ods_log = pd.read_csv(os.path.join(DATA_DIR, "t_ods_log.csv"), parse_dates=["ems"])
    today = date.today()
    refreshed_rows = ods_log[ods_log["ems"].dt.date == today]
    row_count = len(refreshed_rows)
    log.info(f"  ODS log rows for today ({today}): {row_count}")
    return row_count


# ── Step 2: Set Date Variable ──────────────────────────────────────────────────
def get_report_date():
    """Replicates: SELECT to_char((sysdate)-1, 'dd.mm.yyyy')"""
    yesterday = date.today() - timedelta(days=1)
    report_date = yesterday.strftime("%d.%m.%Y")
    log.info(f"Step 2 — Report date set to: {report_date}")
    return report_date


# ── Config: Load Email Distribution ───────────────────────────────────────────
def load_email_config(report_name="BC_BIMIO_267_Daily"):
    """Load email distribution list from config CSVs for the given report."""
    log.info("  Loading email config...")
    reports = pd.read_csv(os.path.join(DATA_DIR, "config_report.csv"))
    emails  = pd.read_csv(os.path.join(DATA_DIR, "config_report_email.csv"))

    report_row = reports[
        (reports["report_name"] == report_name) & (reports["is_active"] == "Y")
    ]
    if report_row.empty:
        raise ValueError(f"No active report config found for: {report_name}")

    report_id = int(report_row.iloc[0]["report_id"])
    active_emails = emails[
        (emails["report_id"] == report_id) & (emails["is_active"] == "Y")
    ]

    def get_list(group, email_type):
        rows = active_emails[
            (active_emails["recipient_group"] == group) &
            (active_emails["email_type"] == email_type)
        ]
        return "; ".join(rows["email_address"].tolist())

    config = {
        "ops_to"   : get_list("OPERATIONS",  "TO"),
        "bi_bcc"   : get_list("BI_TEAM",     "BCC"),
        "alert_cc" : get_list("ALERT_ONLY",  "CC"),
    }
    log.info(f"    Operations TO  : {config['ops_to']}")
    log.info(f"    BI Team BCC    : {config['bi_bcc']}")
    log.info(f"    Alert CC       : {config['alert_cc']}")
    return config


# ── Step 3a: ODS Not Ready — Alert ────────────────────────────────────────────
def send_ods_alert(report_date, email_config):
    """Replicates: Email_2 — ODS not refreshed alert to operations teams."""
    log.warning("Step 3a — ODS data NOT refreshed. Alert email would be sent.")
    log.warning(f"  Subject : BIMIO 267 - 12 Hour Prevented Daily (MTD, YTD) For_{report_date}")
    log.warning(f"  To      : {email_config['ops_to']}")
    log.warning(f"  CC      : {email_config['alert_cc']}")
    log.warning("  Body    : ODS Refresh Error — report cannot be generated today.")


# ── Step 3b: Run Report ────────────────────────────────────────────────────────
def load_data():
    """Load all CSV sample data files into DataFrames."""
    log.info("  Loading source data tables...")
    tables = {
        "fct"       : pd.read_csv(os.path.join(DATA_DIR, "fct_gas_escapes_v.csv")),
        "dwor"      : pd.read_csv(os.path.join(DATA_DIR, "dim_work_orders.csv"),    parse_dates=["reported_date_time"]),
        "dorg"      : pd.read_csv(os.path.join(DATA_DIR, "dim_organisation.csv")),
        "dadr"      : pd.read_csv(os.path.join(DATA_DIR, "dim_addresses.csv")),
        "dcal"      : pd.read_csv(os.path.join(DATA_DIR, "dim_calendar.csv"),       parse_dates=["date_oracle"]),
        "dtim"      : pd.read_csv(os.path.join(DATA_DIR, "dim_time.csv")),
    }

    # Ensure all ID/FK columns are consistently typed as int
    int_cols = {
        "fct" : ["id", "dwor_id_root", "dwor_id_gas_prevented", "dorg_id_root", "dadr_id_root", "dcal_id_gas_prevented_date", "dtim_id_gas_prevented_time"],
        "dwor": ["id"],
        "dorg": ["id"],
        "dadr": ["id"],
        "dcal": ["id"],
        "dtim": ["id"],
    }
    for name, cols in int_cols.items():
        for col in cols:
            tables[name][col] = tables[name][col].astype(int)
    for name, df in tables.items():
        log.info(f"    {name}: {len(df)} rows loaded")
    return tables


def get_financial_year_start():
    """
    Replicates Redshift expression:
      date_add('month', 3,
        date_trunc('year',
          date_add('month', -3,
            date_add('day', -1, SYSDATE-3))))
    Gives April 1st of the current UK financial year.
    """
    base        = date.today() - timedelta(days=4)        # SYSDATE - 3 days - 1 day
    shifted     = base - relativedelta(months=3)           # subtract 3 months
    year_start  = date(shifted.year, 1, 1)                 # truncate to Jan 1
    fy_start    = year_start + relativedelta(months=3)     # add 3 months → April 1
    return fy_start


def build_report(tables):
    """
    Replicates the main SQL query: joins fact + dimensions,
    calculates prevented timestamp, time difference, and report flags.
    """
    log.info("  Building report dataset...")

    fct   = tables["fct"]
    dwor  = tables["dwor"]
    dorg  = tables["dorg"]
    dadr  = tables["dadr"]
    dcal  = tables["dcal"]
    dtim  = tables["dtim"]

    # Filter latest records only (WHERE ge.latest = 'Y')
    fct = fct[fct["latest"] == "Y"]

    # Join: fct → dim_work_orders (root work order) — includes job_type
    df = fct.merge(dwor, left_on="dwor_id_root", right_on="id", suffixes=("", "_root_dwor"))

    # Join: fct → dim_work_orders (gas prevented work order)
    df = df.merge(dwor, left_on="dwor_id_gas_prevented", right_on="id", suffixes=("", "_prev_dwor"))

    # Join: fct → dim_organisation
    df = df.merge(dorg, left_on="dorg_id_root", right_on="id", suffixes=("", "_org"))

    # Join: fct → dim_addresses
    df = df.merge(dadr, left_on="dadr_id_root", right_on="id", suffixes=("", "_adr"))

    # Join: fct → dim_calendar (gas prevented date)
    df = df.merge(dcal, left_on="dcal_id_gas_prevented_date", right_on="id", suffixes=("", "_cal"))

    # Join: fct → dim_time (gas prevented time)
    df = df.merge(dtim, left_on="dtim_id_gas_prevented_time", right_on="id", suffixes=("", "_tim"))

    # DECODE: DEPOT_K → DEPOT_L (Toad: DECODE(depot_work_group,'DEPOT_K','DEPOT_L',depot_work_group))
    df["depot"] = df["depot_work_group"].replace("DEPOT_K", "DEPOT_L")

    # Build prevented timestamp: date_disp_1 + hour_24_minute (last 8 chars)
    df["prevented"] = pd.to_datetime(
        df["date_disp_1"] + " " + df["hour_24_minute"].str[-8:],
        format="%d/%m/%Y %H:%M:%S"
    )

    # Calculate time difference in hours (DATEDIFF minutes / 60)
    df["difference"] = (
        (df["prevented"] - df["reported_date_time"]).dt.total_seconds() / 3600
    ).round(2)

    # Apply financial year date filter
    fy_start  = get_financial_year_start()
    today     = date.today()
    log.info(f"  Date filter: {fy_start} to {today - timedelta(days=1)}")

    df = df[
        (df["date_oracle"].dt.date >= fy_start) &
        (df["date_oracle"].dt.date <  today)
    ]

    # MTD flag: prevented date is within current month
    month_start = date.today().replace(day=1) - timedelta(days=1)
    df["MTD"] = (df["prevented"].dt.date > month_start).astype(int)

    # 12-hour flags
    df["Less 12"]  = (df["difference"] <= 12).astype(int)
    df["Great 12"] = (df["difference"] >  12).astype(int)
    df["Count"]    = 1

    # Select and rename final columns to match report
    report = df[[
        "network",
        "ldz",
        "depot",
        "work_order_number_prev_dwor",
        "job_type",
        "work_order_number",
        "reported_date_time",
        "prevented",
        "difference",
        "display_address",
        "MTD",
        "Less 12",
        "Great 12",
        "Count",
    ]].rename(columns={
        "network"                    : "Network",
        "ldz"                        : "LDZ",
        "depot"                      : "Depot",
        "work_order_number_prev_dwor": "Work Order",
        "job_type"                   : "Job Type",
        "work_order_number"          : "Root Work Order",
        "reported_date_time"         : "Emergency Date",
        "prevented"                  : "Gas Prevented",
        "difference"                 : "Time Difference",
        "display_address"            : "Address",
    })

    log.info(f"  Report rows after filter: {len(report)}")
    return report


def export_to_excel(report):
    """
    Loads the .xlsm template, populates Raw Data sheet starting from row 2,
    preserves all template formatting and the Summary sheet.
    """
    log.info(f"  Loading template: {TEMPLATE_FILE}")
    wb = load_workbook(TEMPLATE_FILE, keep_vba=True)
    ws = wb["Raw Data"]

    # Clear any existing data rows (keep header in row 1)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.value = None

    # Write data rows
    for row_idx, row_data in enumerate(report.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(PRECOPY_FILE)
    log.info(f"  Template populated and saved: {PRECOPY_FILE}")


def archive_file(report_date):
    """
    Replicates: CopyFileActivity
    Copies precopy file to archive folder with date suffix in filename.
    """
    archive_name = f"BIMIO_267_12Hour_Prevented_Daily_For_{report_date}.xlsm"
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    shutil.copy2(PRECOPY_FILE, archive_path)
    log.info(f"  Archived to: {archive_path}")
    return archive_path


def send_report_email(report_date, archive_path, email_config):
    """Replicates: Email_1 — send report with Excel attachment to operations teams."""
    log.info("  Report email would be sent:")
    log.info(f"    Subject    : BIMIO 267 - 12 Hour Prevented Daily (MTD, YTD) For_{report_date}")
    log.info(f"    To         : {email_config['ops_to']}")
    log.info(f"    CC         : {email_config['alert_cc']}")
    log.info(f"    BCC        : {email_config['bi_bcc']}")
    log.info(f"    Attachment : {os.path.basename(archive_path)}")


def send_confirmation_email(report_date, email_config):
    """Replicates: Email_3 — internal confirmation email to BI team."""
    log.info("  Confirmation email would be sent:")
    log.info(f"    Subject : BIMIO 267 For_{report_date} - Has Run and Been Emailed")
    log.info(f"    To      : {email_config['bi_bcc']}")


def handle_exception(error):
    """Replicates: FaultHandlersActivity — error email with log attachment."""
    log.error("PIPELINE FAILED — Error email would be sent to BI team.")
    log.error(f"  Error: {error}")


# ── Main Pipeline ──────────────────────────────────────────────────────────────
def run_pipeline():
    log.info("=" * 60)
    log.info("BC_BIMIO_267_Daily Pipeline — Starting")
    log.info("=" * 60)

    try:
        # Step 1: ODS refresh check
        ods_row_count = check_ods_refresh()

        # Step 2: Set date variable
        report_date = get_report_date()

        # Load email config from config tables
        email_config = load_email_config("BC_BIMIO_267_Daily")

        # Step 3: IF/ELSE branch
        if ods_row_count == 0:
            # Branch 1: Data not ready
            send_ods_alert(report_date, email_config)

        elif ods_row_count >= 1:
            # Branch 2: Data ready — run report
            log.info("Step 3b — ODS refreshed. Running report...")
            tables       = load_data()
            report       = build_report(tables)
            export_to_excel(report)
            archive_path = archive_file(report_date)
            send_report_email(report_date, archive_path, email_config)
            send_confirmation_email(report_date, email_config)

        log.info("=" * 60)
        log.info("Pipeline completed successfully.")
        log.info("=" * 60)

    except Exception as e:
        handle_exception(e)
        raise


if __name__ == "__main__":
    run_pipeline()
