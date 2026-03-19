# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 04 — Gold Layer Aggregation
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Builds 4 business-ready Gold tables from Silver:
# MAGIC - `daily_meter_summary` — per-meter per-day KWh aggregates
# MAGIC - `regional_demand`     — hourly demand by region
# MAGIC - `network_assets`      — latest snapshot per asset
# MAGIC - `forecast_summary`    — avg/min/max demand by region + scenario
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
print("  UTILITICS — GOLD LAYER AGGREGATION")
print("=" * 60)

# COMMAND ----------

# MAGIC %md ## 1. daily_meter_summary

# COMMAND ----------

print("\n[1/4] Building: daily_meter_summary")

ts = spark.read.format("delta").load(get_path("silver_timeseries"))

daily_meter = (ts
    .groupBy("meter_id", "reading_date", "meter_type", "region_code")
    .agg(
        F.sum("reading_value_kwh")                                          .alias("total_kwh"),
        F.avg("reading_value_kwh")                                          .alias("avg_kwh"),
        F.max("reading_value_kwh")                                          .alias("peak_kwh"),
        F.min("reading_value_kwh")                                          .alias("min_kwh"),
        F.stddev("reading_value_kwh")                                       .alias("stddev_kwh"),
        F.count("*")                                                        .alias("reading_count"),
        F.sum(F.when(F.col("reading_quality") == "VALID",     1).otherwise(0)).alias("valid_readings"),
        F.sum(F.when(F.col("reading_quality") == "ESTIMATED", 1).otherwise(0)).alias("estimated_readings"),
        F.sum(F.when(F.col("is_peak_hour"),  F.col("reading_value_kwh")).otherwise(0)).alias("peak_hours_kwh"),
        F.sum(F.when(~F.col("is_peak_hour"), F.col("reading_value_kwh")).otherwise(0)).alias("offpeak_hours_kwh"),
        F.sum(F.when(F.col("is_weekend"),    F.col("reading_value_kwh")).otherwise(0)).alias("weekend_kwh"),
        F.sum(F.when(~F.col("is_weekend"),   F.col("reading_value_kwh")).otherwise(0)).alias("weekday_kwh"),
    )
    .withColumn("data_completeness_pct",
        F.round(F.col("reading_count") / 48 * 100, 2))
    .withColumn("valid_reading_pct",
        F.round(F.col("valid_readings") / F.col("reading_count") * 100, 2))
    .withColumn("peak_to_offpeak_ratio",
        F.round(F.col("peak_hours_kwh") / F.col("offpeak_hours_kwh"), 4))
    .withColumn("_gold_timestamp", F.current_timestamp()))

(daily_meter.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("reading_date")
    .save(get_path("gold_daily_meter")))

count = spark.read.format("delta").load(get_path("gold_daily_meter")).count()
print(f"    Rows: {count:,}")

# COMMAND ----------

# MAGIC %md ## 2. regional_demand

# COMMAND ----------

print("\n[2/4] Building: regional_demand")

regional = (ts
    .groupBy("region_code", "reading_date", "reading_hour")
    .agg(
        F.sum("reading_value_kwh")  .alias("total_demand_kwh"),
        F.avg("reading_value_kwh")  .alias("avg_demand_kwh"),
        F.countDistinct("meter_id") .alias("active_meters"),
        F.sum(F.when(F.col("reading_quality") == "VALID", 1).otherwise(0)).alias("valid_count"),
        F.count("*")                .alias("total_readings"),
    )
    .withColumn("data_quality_pct",
        F.round(F.col("valid_count") / F.col("total_readings") * 100, 2))
    .withColumn("_gold_timestamp", F.current_timestamp()))

(regional.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("reading_date")
    .save(get_path("gold_regional_demand")))

count = spark.read.format("delta").load(get_path("gold_regional_demand")).count()
print(f"    Rows: {count:,}")

# COMMAND ----------

# MAGIC %md ## 3. network_assets

# COMMAND ----------

print("\n[3/4] Building: network_assets")

sn = spark.read.format("delta").load(get_path("silver_snapshot"))

# Latest snapshot per asset (SCD Type 1)
from pyspark.sql.window import Window

window_latest = Window.partitionBy("asset_id").orderBy(F.col("snapshot_date").desc())

network_assets = (sn
    .withColumn("_rank", F.row_number().over(window_latest))
    .filter(F.col("_rank") == 1)
    .drop("_rank")
    .withColumn("_gold_timestamp", F.current_timestamp()))

(network_assets.write
    .format("delta")
    .mode("overwrite")
    .save(get_path("gold_network_assets")))

count = spark.read.format("delta").load(get_path("gold_network_assets")).count()
print(f"    Rows: {count:,}")

# COMMAND ----------

# MAGIC %md ## 4. forecast_summary

# COMMAND ----------

print("\n[4/4] Building: forecast_summary")

fc = spark.read.format("delta").load(get_path("silver_files"))

forecast_summary = (fc
    .groupBy("forecast_date", "region", "scenario")
    .agg(
        F.avg("predicted_demand_mw")   .alias("avg_predicted_mw"),
        F.max("predicted_demand_mw")   .alias("max_predicted_mw"),
        F.min("predicted_demand_mw")   .alias("min_predicted_mw"),
        F.avg("confidence_width")      .alias("avg_confidence_width"),
        F.count("*")                   .alias("forecast_points"),
    )
    .withColumn("_gold_timestamp", F.current_timestamp()))

(forecast_summary.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("forecast_date")
    .save(get_path("gold_forecast_summary")))

count = spark.read.format("delta").load(get_path("gold_forecast_summary")).count()
print(f"    Rows: {count:,}")

# COMMAND ----------

# MAGIC %md ## Summary

# COMMAND ----------

elapsed = round(time.time() - start_time, 1)

totals = {
    "daily_meter_summary": spark.read.format("delta").load(get_path("gold_daily_meter")).count(),
    "regional_demand":     spark.read.format("delta").load(get_path("gold_regional_demand")).count(),
    "network_assets":      spark.read.format("delta").load(get_path("gold_network_assets")).count(),
    "forecast_summary":    spark.read.format("delta").load(get_path("gold_forecast_summary")).count(),
}

print("\n" + "=" * 60)
print("  UTILITICS — GOLD AGGREGATION COMPLETE")
print("=" * 60)
for name, cnt in totals.items():
    print(f"  {name:<25} {cnt:>8,}")
print(f"\n  Total Gold records: {sum(totals.values()):,}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

# CHANGE 3: display() for rich rendering in Databricks
display(daily_meter.limit(5))
