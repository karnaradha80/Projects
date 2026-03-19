"""
05_validate.py
==============
Comprehensive pipeline validation.
Checks data quality, record counts, null rates, and business rules.

Run: python notebooks/05_validate.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, get_db_config, QUALITY

from pyspark.sql import functions as F
from delta import DeltaTable

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("PipelineValidation")
start_time = time.time()

print("=" * 60)
print("  PIPELINE VALIDATION REPORT")
print("=" * 60)

all_checks = []

def check(name, passed):
    """Register a validation check."""
    status = "PASS" if passed else "FAIL"
    all_checks.append((name, passed))
    print(f"    [{status}] {name}")
    return passed

# ============================================================
# 1. RECORD COUNTS: Bronze → Silver
# ============================================================
print("\n[1] Record Counts (Bronze → Silver)")
print(f"    {'Table':<15} {'Bronze':>10} {'Silver':>10} {'Drop%':>8}")
print(f"    {chr(0x2500) * 45}")

for name, b_path, s_path in [
    ("timeseries", get_path("bronze_timeseries"), get_path("silver_timeseries")),
    ("snapshot",   get_path("bronze_snapshot"),   get_path("silver_snapshot")),
    ("file_data",  get_path("bronze_files"),      get_path("silver_files"))
]:
    b_count = spark.read.format("delta").load(b_path).count()
    s_count = spark.read.format("delta").load(s_path).count()
    drop_pct = round((1 - s_count / b_count) * 100, 2) if b_count > 0 else 0
    status_str = "PASS" if drop_pct < QUALITY["max_drop_rate_pct"] else "FAIL"
    print(f"    {name:<15} {b_count:>10,} {s_count:>10,} {drop_pct:>7}%  {status_str}")
    check(f"{name}: drop rate < {QUALITY['max_drop_rate_pct']}%",
          drop_pct < QUALITY["max_drop_rate_pct"])

# ============================================================
# 2. GOLD LAYER COUNTS
# ============================================================
print(f"\n[2] Gold Layer Counts")
print(f"    {'Table':<25} {'Records':>10}")
print(f"    {chr(0x2500) * 37}")

for name, path in [
    ("daily_meter_summary",  get_path("gold_daily_meter")),
    ("regional_demand",      get_path("gold_regional_demand")),
    ("network_assets",       get_path("gold_network_assets")),
    ("forecast_summary",     get_path("gold_forecast_summary"))
]:
    count = spark.read.format("delta").load(path).count()
    print(f"    {name:<25} {count:>10,}")
    check(f"gold.{name} has records", count > 0)

# ============================================================
# 3. DATA QUALITY CHECKS
# ============================================================
print(f"\n[3] Data Quality Checks")

# Daily meter summary
dm = spark.read.format("delta").load(get_path("gold_daily_meter"))
check("daily_meter: no null meter_ids",
      dm.filter(F.col("meter_id").isNull()).count() == 0)
check("daily_meter: total_kwh is positive",
      dm.filter(F.col("total_kwh") <= 0).count() == 0)
check("daily_meter: completeness 0-100%",
      dm.filter((F.col("data_completeness_pct") < 0) |
                (F.col("data_completeness_pct") > 100)).count() == 0)
check("daily_meter: peak + offpeak = total",
      dm.filter(F.abs(F.col("peak_hours_kwh") + F.col("offpeak_hours_kwh")
                      - F.col("total_kwh")) > 0.01).count() == 0)

# Network assets
na = spark.read.format("delta").load(get_path("gold_network_assets"))
check("network_assets: no null asset_ids",
      na.filter(F.col("asset_id").isNull()).count() == 0)
check("network_assets: valid statuses only",
      na.filter(~F.col("status").isin(
          "ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED")).count() == 0)
check("network_assets: UK coordinates",
      na.filter(~((F.col("location_lat").between(49.0, 61.0)) &
                  (F.col("location_lon").between(-8.0, 2.0)))).count() == 0)

# Forecast summary
fc = spark.read.format("delta").load(get_path("gold_forecast_summary"))
check("forecast: positive avg demand",
      fc.filter(F.col("avg_predicted_mw") <= 0).count() == 0)
check("forecast: max >= avg",
      fc.filter(F.col("max_predicted_mw") < F.col("avg_predicted_mw")).count() == 0)

# ============================================================
# 4. SQLITE SOURCE CHECKS
# ============================================================
print(f"\n[4] SQLite Source Checks")

import sqlite3

db_cfg = get_db_config()
sqlite_path = db_cfg.get("sqlite_path", "")
table_name  = db_cfg["table_name"]

sqlite_exists = os.path.exists(sqlite_path)
check(f"SQLite DB file exists ({sqlite_path})", sqlite_exists)

if sqlite_exists:
    try:
        conn = sqlite3.connect(sqlite_path)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        table_present = table_name in tables
        check(f"SQLite table '{table_name}' exists", table_present)

        if table_present:
            sqlite_count = conn.execute(
                f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            bronze_count = spark.read.format("delta").load(
                get_path("bronze_snapshot")).count()
            counts_match = sqlite_count == bronze_count
            print(f"      SQLite rows: {sqlite_count:,}  |  Bronze rows: {bronze_count:,}")
            check("SQLite row count matches bronze_snapshot", counts_match)
        conn.close()
    except Exception as e:
        print(f"      [ERROR] SQLite check failed: {e}")
        all_checks.append(("SQLite checks", False))
else:
    all_checks.append(("SQLite table exists (skipped — DB missing)", False))
    all_checks.append(("SQLite row count matches bronze (skipped)", False))

# ============================================================
# 5. DELTA TABLE HEALTH
# ============================================================
print(f"\n[5] Delta Table Health")
print(f"    {'Table':<25} {'Version':>8} {'Files':>8}")
print(f"    {chr(0x2500) * 43}")

all_tables = [
    ("bronze.timeseries",    get_path("bronze_timeseries")),
    ("bronze.snapshot",      get_path("bronze_snapshot")),
    ("bronze.file_data",     get_path("bronze_files")),
    ("silver.timeseries",    get_path("silver_timeseries")),
    ("silver.snapshot",      get_path("silver_snapshot")),
    ("silver.file_data",     get_path("silver_files")),
    ("gold.daily_meter",     get_path("gold_daily_meter")),
    ("gold.regional_demand", get_path("gold_regional_demand")),
    ("gold.network_assets",  get_path("gold_network_assets")),
    ("gold.forecast_summary",get_path("gold_forecast_summary")),
]

for name, path in all_tables:
    try:
        dt = DeltaTable.forPath(spark, path)
        version = dt.history(1).collect()[0]["version"]
        detail = spark.sql(f"DESCRIBE DETAIL delta.`{path}`").collect()[0]
        files = detail["numFiles"]
        print(f"    {name:<25} {version:>8} {files:>8}")
    except Exception:
        print(f"    {name:<25} {'ERROR':>8} {'':>8}")

# ============================================================
# FINAL RESULT
# ============================================================
elapsed = round(time.time() - start_time, 1)
passed = sum(1 for _, p in all_checks if p)
total = len(all_checks)
all_passed = passed == total

print("\n" + "=" * 60)
print(f"  VALIDATION RESULT: {passed}/{total} checks passed")
print(f"  STATUS: {'ALL PASS' if all_passed else 'ISSUES FOUND'}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()

# Exit with error code if any checks failed
if not all_passed:
    sys.exit(1)
