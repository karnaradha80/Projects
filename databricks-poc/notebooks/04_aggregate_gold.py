"""
04_aggregate_gold.py
====================
Create business-ready Gold layer tables from Silver data.
These Gold tables will be shared with the vendor via Delta Sharing.

Gold tables:
  1. daily_meter_summary    - Daily consumption per meter
  2. regional_demand        - Hourly demand aggregated by region
  3. network_assets         - Latest status per asset
  4. forecast_summary       - Aggregated demand forecasts

Run: python notebooks/04_aggregate_gold.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("GoldAggregation")
start_time = time.time()

print("=" * 60)
print("  GOLD LAYER AGGREGATION")
print("=" * 60)

results = {}

# ============================================================
# 1. DAILY METER SUMMARY
# Purpose: Daily consumption summary per meter for vendor analysis
# Source: Silver timeseries
# ============================================================
print("\n  [1/4] Building: daily_meter_summary")
ts_silver = spark.read.format("delta").load(get_path("silver_timeseries"))

daily_meter = (ts_silver
    .groupBy("meter_id", "reading_date", "meter_type", "region_code")
    .agg(
        # Consumption metrics
        F.sum("reading_value_kwh").alias("total_kwh"),
        F.avg("reading_value_kwh").alias("avg_kwh"),
        F.max("reading_value_kwh").alias("peak_kwh"),
        F.min("reading_value_kwh").alias("min_kwh"),
        F.stddev("reading_value_kwh").alias("stddev_kwh"),

        # Data quality metrics
        F.count("*").alias("reading_count"),
        F.sum(F.when(F.col("reading_quality") == "VALID", 1).otherwise(0))
            .alias("valid_readings"),
        F.sum(F.when(F.col("reading_quality") == "ESTIMATED", 1).otherwise(0))
            .alias("estimated_readings"),

        # Peak vs off-peak consumption
        F.sum(F.when(F.col("is_peak_hour"), F.col("reading_value_kwh")).otherwise(0))
            .alias("peak_hours_kwh"),
        F.sum(F.when(~F.col("is_peak_hour"), F.col("reading_value_kwh")).otherwise(0))
            .alias("offpeak_hours_kwh"),

        # Weekend vs weekday
        F.sum(F.when(F.col("is_weekend"), F.col("reading_value_kwh")).otherwise(0))
            .alias("weekend_kwh"),
        F.sum(F.when(~F.col("is_weekend"), F.col("reading_value_kwh")).otherwise(0))
            .alias("weekday_kwh")
    )
    .withColumn("data_completeness_pct",
        F.round(F.col("reading_count") / 48 * 100, 2))
    .withColumn("valid_reading_pct",
        F.round(F.col("valid_readings") / F.col("reading_count") * 100, 2))
    .withColumn("peak_to_offpeak_ratio",
        F.when(F.col("offpeak_hours_kwh") > 0,
               F.round(F.col("peak_hours_kwh") / F.col("offpeak_hours_kwh"), 3))
         .otherwise(F.lit(None)))
    .withColumn("_gold_timestamp", F.current_timestamp())
)

(daily_meter.write.format("delta").mode("overwrite")
    .partitionBy("reading_date").save(get_path("gold_daily_meter")))
count = daily_meter.count()
print(f"    Records: {count:,}")
results["daily_meter_summary"] = count

# ============================================================
# 2. REGIONAL DEMAND
# Purpose: Hourly demand by region for vendor's forecasting models
# Source: Silver timeseries
# ============================================================
print("\n  [2/4] Building: regional_demand")

regional = (ts_silver
    .groupBy("reading_date", "reading_hour", "region_code")
    .agg(
        F.sum("reading_value_kwh").alias("total_demand_kwh"),
        F.countDistinct("meter_id").alias("active_meters"),
        F.avg("reading_value_kwh").alias("avg_per_meter_kwh"),
        F.max("reading_value_kwh").alias("max_single_meter_kwh"),
        F.min("reading_value_kwh").alias("min_single_meter_kwh"),
        F.percentile_approx("reading_value_kwh", 0.5).alias("median_kwh"),
        F.percentile_approx("reading_value_kwh", 0.95).alias("p95_kwh"),
    )
    .withColumn("is_peak_hour",
        F.when(F.col("reading_hour").between(7, 19), True).otherwise(False))
    .orderBy("reading_date", "reading_hour", "region_code")
    .withColumn("_gold_timestamp", F.current_timestamp())
)

(regional.write.format("delta").mode("overwrite")
    .partitionBy("reading_date").save(get_path("gold_regional_demand")))
count = regional.count()
print(f"    Records: {count:,}")
results["regional_demand"] = count

# ============================================================
# 3. NETWORK ASSETS (Latest status)
# Purpose: Current asset inventory and status for vendor reference
# Source: Silver snapshot
# ============================================================
print("\n  [3/4] Building: network_assets")
snap_silver = spark.read.format("delta").load(get_path("silver_snapshot"))

w = Window.partitionBy("asset_id").orderBy(F.col("snapshot_date").desc())

assets = (snap_silver
    .withColumn("_rank", F.row_number().over(w))
    .filter(F.col("_rank") == 1)
    .drop("_rank")
    .select(
        "asset_id", "asset_type", "status", "capacity_mw", "voltage_kv",
        "location_lat", "location_lon", "snapshot_date",
        "last_maintenance_date", "firmware_version",
        "days_since_maintenance", "needs_maintenance"
    )
    .withColumn("_gold_timestamp", F.current_timestamp())
)

(assets.write.format("delta").mode("overwrite")
    .save(get_path("gold_network_assets")))
count = assets.count()
print(f"    Records: {count:,}")
results["network_assets"] = count

# ============================================================
# 4. FORECAST SUMMARY
# Purpose: Aggregated demand forecasts by region/scenario
# Source: Silver file data
# ============================================================
print("\n  [4/4] Building: forecast_summary")
file_silver = spark.read.format("delta").load(get_path("silver_files"))

forecast = (file_silver
    .groupBy("forecast_date", "region", "scenario", "forecast_day")
    .agg(
        F.avg("predicted_demand_mw").alias("avg_predicted_mw"),
        F.max("predicted_demand_mw").alias("max_predicted_mw"),
        F.min("predicted_demand_mw").alias("min_predicted_mw"),
        F.stddev("predicted_demand_mw").alias("stddev_predicted_mw"),
        F.avg("confidence_range_mw").alias("avg_confidence_range_mw"),
        F.avg("confidence_pct").alias("avg_confidence_pct"),
        F.count("*").alias("data_points"),
    )
    .withColumn("demand_range_mw",
        F.col("max_predicted_mw") - F.col("min_predicted_mw"))
    .withColumn("_gold_timestamp", F.current_timestamp())
)

(forecast.write.format("delta").mode("overwrite")
    .partitionBy("forecast_date").save(get_path("gold_forecast_summary")))
count = forecast.count()
print(f"    Records: {count:,}")
results["forecast_summary"] = count

# ============================================================
# Summary
# ============================================================
elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  GOLD AGGREGATION COMPLETE")
print("=" * 60)
print(f"  {'Table':<25} {'Records':>10}")
print(f"  {chr(0x2500) * 37}")
for name, count in results.items():
    print(f"  {name:<25} {count:>10,}")
print(f"\n  Total Gold records: {sum(results.values()):,}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
