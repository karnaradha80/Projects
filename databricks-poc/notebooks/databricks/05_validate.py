# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 05 — Pipeline Validation
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Runs 17 checks across all layers. Exits with failure if any check fails.
# MAGIC
# MAGIC ### Changes from local version
# MAGIC | # | Local | Databricks |
# MAGIC |---|-------|-----------|
# MAGIC | 1 | `get_spark_session()` | Removed — `spark` pre-exists |
# MAGIC | 2 | `C:/Projects/.../lake/` | `dbfs:/utilitics/lake/` |
# MAGIC | 3 | `df.show()` | `display(df)` |
# MAGIC | 4 | SQLite checks (sqlite3 module) | Skipped — no local DB in Databricks (Azure SQL in Part 2) |

# COMMAND ----------

%run ./00_config

# COMMAND ----------

import time
from pyspark.sql import functions as F
from delta.tables import DeltaTable

# CHANGE 1: No SparkSession
start_time = time.time()
all_checks = []

print("=" * 60)
print("  UTILITICS — PIPELINE VALIDATION REPORT")
print("=" * 60)

# COMMAND ----------

def check(name, passed):
    status = "PASS" if passed else "FAIL"
    all_checks.append((name, passed))
    icon = "✅" if passed else "❌"
    print(f"    {icon} [{status}] {name}")
    return passed

# COMMAND ----------

# MAGIC %md ## 1. Record Counts — Bronze → Silver

# COMMAND ----------

print("\n[1] Record Counts (Bronze → Silver)")
print(f"    {'Table':<15} {'Bronze':>10} {'Silver':>10} {'Drop%':>8}")
print(f"    {'─' * 45}")

for name, b_path, s_path in [
    ("timeseries", get_path("bronze_timeseries"), get_path("silver_timeseries")),
    ("snapshot",   get_path("bronze_snapshot"),   get_path("silver_snapshot")),
    ("file_data",  get_path("bronze_files"),      get_path("silver_files")),
]:
    b_count  = spark.read.format("delta").load(b_path).count()
    s_count  = spark.read.format("delta").load(s_path).count()
    drop_pct = round((1 - s_count / b_count) * 100, 2) if b_count > 0 else 0
    status   = "PASS" if drop_pct < QUALITY["max_drop_rate_pct"] else "FAIL"
    print(f"    {name:<15} {b_count:>10,} {s_count:>10,} {drop_pct:>7}%  {status}")
    check(f"{name}: drop rate < {QUALITY['max_drop_rate_pct']}%",
          drop_pct < QUALITY["max_drop_rate_pct"])

# COMMAND ----------

# MAGIC %md ## 2. Gold Layer Counts

# COMMAND ----------

print(f"\n[2] Gold Layer Counts")
print(f"    {'Table':<25} {'Records':>10}")
print(f"    {'─' * 37}")

for name, path in [
    ("daily_meter_summary",  get_path("gold_daily_meter")),
    ("regional_demand",      get_path("gold_regional_demand")),
    ("network_assets",       get_path("gold_network_assets")),
    ("forecast_summary",     get_path("gold_forecast_summary")),
]:
    count = spark.read.format("delta").load(path).count()
    print(f"    {name:<25} {count:>10,}")
    check(f"gold.{name} has records", count > 0)

# COMMAND ----------

# MAGIC %md ## 3. Data Quality Checks

# COMMAND ----------

print(f"\n[3] Data Quality Checks")

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

na = spark.read.format("delta").load(get_path("gold_network_assets"))
check("network_assets: no null asset_ids",
      na.filter(F.col("asset_id").isNull()).count() == 0)
check("network_assets: valid statuses only",
      na.filter(~F.col("status").isin(
          "ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED")).count() == 0)
check("network_assets: UK coordinates",
      na.filter(~((F.col("location_lat").between(49.0, 61.0)) &
                  (F.col("location_lon").between(-8.0,  2.0)))).count() == 0)

fc = spark.read.format("delta").load(get_path("gold_forecast_summary"))
check("forecast: positive avg demand",
      fc.filter(F.col("avg_predicted_mw") <= 0).count() == 0)
check("forecast: max >= avg",
      fc.filter(F.col("max_predicted_mw") < F.col("avg_predicted_mw")).count() == 0)

# COMMAND ----------

# MAGIC %md ## 4. Delta Table Health

# COMMAND ----------

print(f"\n[4] Delta Table Health")
print(f"    {'Table':<25} {'Version':>8} {'Files':>8}")
print(f"    {'─' * 43}")

all_tables = [
    ("bronze.timeseries",     get_path("bronze_timeseries")),
    ("bronze.snapshot",       get_path("bronze_snapshot")),
    ("bronze.file_data",      get_path("bronze_files")),
    ("silver.timeseries",     get_path("silver_timeseries")),
    ("silver.snapshot",       get_path("silver_snapshot")),
    ("silver.file_data",      get_path("silver_files")),
    ("gold.daily_meter",      get_path("gold_daily_meter")),
    ("gold.regional_demand",  get_path("gold_regional_demand")),
    ("gold.network_assets",   get_path("gold_network_assets")),
    ("gold.forecast_summary", get_path("gold_forecast_summary")),
]

for name, path in all_tables:
    try:
        dt      = DeltaTable.forPath(spark, path)
        version = dt.history(1).collect()[0]["version"]
        detail  = spark.sql(f"DESCRIBE DETAIL delta.`{path}`").collect()[0]
        files   = detail["numFiles"]
        print(f"    {name:<25} {version:>8} {files:>8}")
    except Exception as e:
        print(f"    {name:<25} {'ERROR':>8}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Note: Snapshot Source Check
# MAGIC **Local version** checked SQLite DB existence and row count via `sqlite3`.
# MAGIC **Databricks** has no local SQLite — this check is replaced by verifying the
# MAGIC DBFS CSV source file exists and its row count matches `bronze_snapshot`.

# COMMAND ----------

print(f"\n[5] Snapshot Source Check (DBFS CSV)")

csv_dir = get_path("raw_snapshot_csv").replace("/network_asset_snapshot.csv", "")
try:
    csv_count    = spark.read.option("header","true").csv(csv_dir).count()
    bronze_count = spark.read.format("delta").load(get_path("bronze_snapshot")).count()
    print(f"      CSV rows: {csv_count:,}  |  Bronze rows: {bronze_count:,}")
    check("Snapshot CSV row count matches bronze_snapshot", csv_count == bronze_count)
except Exception as e:
    print(f"      [ERROR] {e}")
    all_checks.append(("Snapshot CSV check", False))

# COMMAND ----------

# MAGIC %md ## Final Result

# COMMAND ----------

elapsed    = round(time.time() - start_time, 1)
passed     = sum(1 for _, p in all_checks if p)
total      = len(all_checks)
all_passed = passed == total

print("\n" + "=" * 60)
print(f"  VALIDATION RESULT: {passed}/{total} checks passed")
print(f"  STATUS: {'✅ ALL PASS' if all_passed else '❌ ISSUES FOUND'}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

if not all_passed:
    failed = [name for name, p in all_checks if not p]
    print("\n  Failed checks:")
    for f in failed:
        print(f"    ❌ {f}")
    raise Exception(f"Validation failed: {len(failed)} check(s) did not pass")

# CHANGE 3: display() for rich summary table
results_df = spark.createDataFrame(
    [(name, "PASS" if p else "FAIL") for name, p in all_checks],
    ["check", "status"])
display(results_df)
