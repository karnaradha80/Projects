# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 03 — Silver Layer Transformation
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Cleanses and validates Bronze data → writes Silver Delta tables.
# MAGIC Applies: deduplication, range validation, derived columns.
# MAGIC
# MAGIC ### Changes from local version
# MAGIC | # | Local | Databricks |
# MAGIC |---|-------|-----------|
# MAGIC | 1 | `get_spark_session()` | Removed — `spark` pre-exists |
# MAGIC | 2 | `C:/Projects/.../lake/` | `dbfs:/utilitics/lake/` |
# MAGIC | 3 | `df.show()` | `display(df)` |

# COMMAND ----------

%run ./00_config

# COMMAND ----------

import time
from pyspark.sql import functions as F
from delta.tables import DeltaTable

# CHANGE 1: No SparkSession
start_time = time.time()

print("=" * 60)
print("  UTILITICS — SILVER LAYER TRANSFORMATION")
print("=" * 60)

# COMMAND ----------

# MAGIC %md ## 1. Time Series — Dedup + Range Validation

# COMMAND ----------

print("\n[1/3] Transforming: timeseries")

ts_bronze = spark.read.format("delta").load(get_path("bronze_timeseries"))
input_count = ts_bronze.count()

ts_silver = (ts_bronze
    # Dedup: keep latest per meter + timestamp
    .dropDuplicates(["meter_id", "reading_timestamp"])
    # Range validation: remove physically impossible readings
    .filter(F.col("reading_value_kwh").between(0, 100))
    .filter(F.col("reading_quality").isin("VALID", "ESTIMATED", "SUSPECT", "MISSING"))
    # Derived columns
    .withColumn("reading_date", F.to_date("reading_timestamp"))
    .withColumn("reading_hour", F.hour("reading_timestamp"))
    .withColumn("is_peak_hour",
        F.when(F.col("reading_hour").between(7, 9),  True)
         .when(F.col("reading_hour").between(17, 20), True)
         .otherwise(False))
    .withColumn("is_weekend",
        F.dayofweek("reading_date").isin(1, 7))
    # Drop ingestion partition column — repartition by business date
    .drop("_ingestion_date"))

(ts_silver.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("reading_date")
    .save(get_path("silver_timeseries")))

output_count = spark.read.format("delta").load(get_path("silver_timeseries")).count()
drop_pct = round((1 - output_count / input_count) * 100, 2) if input_count > 0 else 0
print(f"    Bronze: {input_count:,}  →  Silver: {output_count:,}  (drop: {drop_pct}%)")

# COMMAND ----------

# MAGIC %md ## 2. Snapshot — Dedup + Coordinate Validation

# COMMAND ----------

print("\n[2/3] Transforming: snapshot")

sn_bronze    = spark.read.format("delta").load(get_path("bronze_snapshot"))
input_count  = sn_bronze.count()

sn_silver = (sn_bronze
    .dropDuplicates(["asset_id", "snapshot_date"])
    # UK coordinate bounds
    .filter(F.col("location_lat").between(49.0, 61.0))
    .filter(F.col("location_lon").between(-8.0,  2.0))
    # Valid status only
    .filter(F.col("status").isin("ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED"))
    # Derived columns
    .withColumn("needs_maintenance",
        F.col("status").isin("MAINTENANCE", "INACTIVE"))
    .withColumn("days_since_maintenance",
        F.datediff(F.col("snapshot_date"), F.col("last_maintenance_date")))
    .drop("_ingestion_date"))

(sn_silver.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("snapshot_date")
    .save(get_path("silver_snapshot")))

output_count = spark.read.format("delta").load(get_path("silver_snapshot")).count()
drop_pct = round((1 - output_count / input_count) * 100, 2) if input_count > 0 else 0
print(f"    Bronze: {input_count:,}  →  Silver: {output_count:,}  (drop: {drop_pct}%)")

# COMMAND ----------

# MAGIC %md ## 3. File Data — Dedup + Confidence Bound Validation

# COMMAND ----------

print("\n[3/3] Transforming: file_data")

fc_bronze   = spark.read.format("delta").load(get_path("bronze_files"))
input_count = fc_bronze.count()

fc_silver = (fc_bronze
    .dropDuplicates(["forecast_id", "horizon_hours"])
    .filter(F.col("predicted_demand_mw") > 0)
    .filter(F.col("confidence_lower") <= F.col("predicted_demand_mw"))
    .filter(F.col("confidence_upper") >= F.col("predicted_demand_mw"))
    .withColumn("confidence_width",
        F.col("confidence_upper") - F.col("confidence_lower"))
    .withColumn("forecast_date", F.to_date(F.col("forecast_date")))
    .drop("_ingestion_date"))

(fc_silver.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("forecast_date")
    .save(get_path("silver_files")))

output_count = spark.read.format("delta").load(get_path("silver_files")).count()
drop_pct = round((1 - output_count / input_count) * 100, 2) if input_count > 0 else 0
print(f"    Bronze: {input_count:,}  →  Silver: {output_count:,}  (drop: {drop_pct}%)")

# COMMAND ----------

# MAGIC %md ## Summary

# COMMAND ----------

elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  UTILITICS — SILVER TRANSFORMATION COMPLETE")
print("=" * 60)
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

# CHANGE 3: display() for rich rendering
display(ts_silver.limit(5))
