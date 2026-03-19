"""
03_transform_silver.py
======================
Clean, validate, and standardise Bronze data into Silver.

Transformations per table:
  Time Series: Dedup, range validation, quality codes, peak hours
  Snapshot:    Latest per asset/day, UK coordinates, null handling
  File Data:   Dedup, confidence interval validation, derived cols

Run: python notebooks/03_transform_silver.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, QUALITY

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("SilverTransformation")
start_time = time.time()

print("=" * 60)
print("  SILVER LAYER TRANSFORMATION")
print("=" * 60)

results = {}

# ============================================================
# 1. Silver: Time Series
# ============================================================
print("\n  [Time Series]")
ts_bronze = spark.read.format("delta").load(get_path("bronze_timeseries"))
bronze_count = ts_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

ts_silver = (ts_bronze
    # DEDUP: Same meter + timestamp should not appear twice
    .dropDuplicates(["meter_id", "reading_timestamp"])

    # VALIDATE: Reading must be in reasonable range (0 - 10,000 kWh)
    .filter(F.col("reading_value_kwh").between(0, 10000))

    # STANDARDISE: Clean quality codes
    .withColumn("reading_quality",
        F.when(F.col("reading_quality").isNull(), "UNKNOWN")
         .otherwise(F.upper(F.trim(F.col("reading_quality")))))

    # DERIVE: Add useful columns for downstream analysis
    .withColumn("reading_date", F.to_date("reading_timestamp"))
    .withColumn("reading_hour", F.hour("reading_timestamp"))
    .withColumn("is_peak_hour",
        F.when((F.hour("reading_timestamp") >= 7) &
               (F.hour("reading_timestamp") <= 19), True)
         .otherwise(False))
    .withColumn("day_of_week", F.dayofweek("reading_timestamp"))
    .withColumn("is_weekend",
        F.when(F.dayofweek("reading_timestamp").isin(1, 7), True)
         .otherwise(False))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(ts_silver.write.format("delta").mode("overwrite")
    .partitionBy("reading_date").save(get_path("silver_timeseries")))

silver_count = ts_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["timeseries"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# 2. Silver: Snapshot
# ============================================================
print("\n  [Snapshot]")
snap_bronze = spark.read.format("delta").load(get_path("bronze_snapshot"))
bronze_count = snap_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

# Keep only latest record per asset per day
w_latest = Window.partitionBy("asset_id", "snapshot_date") \
    .orderBy(F.col("_ingestion_timestamp").desc())

snap_silver = (snap_bronze
    # DEDUP: Keep latest ingestion per asset per snapshot day
    .withColumn("_rn", F.row_number().over(w_latest))
    .filter(F.col("_rn") == 1)
    .drop("_rn")

    # VALIDATE: UK geographic bounds
    .filter(F.col("location_lat").between(49.0, 61.0))
    .filter(F.col("location_lon").between(-8.0, 2.0))

    # STANDARDISE: Clean status values
    .withColumn("status", F.upper(F.trim(F.col("status"))))
    .withColumn("asset_type", F.upper(F.trim(F.col("asset_type"))))

    # NULL HANDLING: Default capacity to 0
    .withColumn("capacity_mw",
        F.when(F.col("capacity_mw").isNull(), 0.0)
         .otherwise(F.col("capacity_mw")))

    # DERIVE: Maintenance age
    .withColumn("days_since_maintenance",
        F.datediff(F.col("snapshot_date"), F.col("last_maintenance_date")))
    .withColumn("needs_maintenance",
        F.when(F.col("days_since_maintenance") > 180, True)
         .otherwise(False))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(snap_silver.write.format("delta").mode("overwrite")
    .partitionBy("snapshot_date").save(get_path("silver_snapshot")))

silver_count = snap_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["snapshot"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# 3. Silver: File Data (Forecasts)
# ============================================================
print("\n  [File Data / Forecasts]")
file_bronze = spark.read.format("delta").load(get_path("bronze_files"))
bronze_count = file_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

file_silver = (file_bronze
    # DEDUP: Same forecast + hour should not appear twice
    .dropDuplicates(["forecast_id", "horizon_hours"])

    # VALIDATE: Confidence interval must be valid
    .filter(F.col("confidence_lower") <= F.col("predicted_demand_mw"))
    .filter(F.col("predicted_demand_mw") <= F.col("confidence_upper"))

    # VALIDATE: Demand must be positive
    .filter(F.col("predicted_demand_mw") > 0)

    # DERIVE: Useful forecast analysis columns
    .withColumn("confidence_range_mw",
        F.col("confidence_upper") - F.col("confidence_lower"))
    .withColumn("confidence_pct",
        F.round((F.col("confidence_range_mw") / F.col("predicted_demand_mw")) * 100, 2))
    .withColumn("forecast_day",
        F.floor(F.col("horizon_hours") / 24).cast("int"))
    .withColumn("hour_of_day",
        (F.col("horizon_hours") % 24).cast("int"))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(file_silver.write.format("delta").mode("overwrite")
    .partitionBy("forecast_date").save(get_path("silver_files")))

silver_count = file_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["file_data"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# Quality Report
# ============================================================
elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  SILVER TRANSFORMATION COMPLETE")
print("=" * 60)
print(f"  {'Table':<15} {'Bronze':>10} {'Silver':>10} {'Drop%':>8} {'Status':>8}")
print(f"  {chr(0x2500) * 53}")
for name, (b, s, d) in results.items():
    threshold = QUALITY["max_drop_rate_pct"]
    status = "PASS" if d < threshold else "WARN" if d < threshold * 2 else "FAIL"
    print(f"  {name:<15} {b:>10,} {s:>10,} {d:>7}% {status:>8}")
print(f"\n  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
