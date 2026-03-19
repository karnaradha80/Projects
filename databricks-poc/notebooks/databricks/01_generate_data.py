# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 01 — Data Generation
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Generates synthetic data for all 3 SoW categories:
# MAGIC - Time Series: Smart meter readings (168,000 records)
# MAGIC - Snapshot: Network asset status → CSV on DBFS (14,000 records)
# MAGIC - File Data: ERM demand forecasts (84,000 records)
# MAGIC
# MAGIC ### Changes from local version
# MAGIC | # | Local | Databricks |
# MAGIC |---|-------|-----------|
# MAGIC | 1 | `get_spark_session()` | Removed — `spark` pre-exists |
# MAGIC | 2 | `C:/Projects/.../lake/` | `dbfs:/utilitics/lake/` |
# MAGIC | 3 | `df.show()` | `display(df)` |
# MAGIC | 4 | Snapshot → SQLite via SQLAlchemy | Snapshot → CSV on DBFS |

# COMMAND ----------

# CHANGE 2: Run shared config instead of importing local config files
# Local: from config.spark_config import get_spark_session
#         from config.pipeline_config import get_path, DATA_CONFIG
%run ./00_config

# COMMAND ----------

import time
import random
import shutil
from datetime import datetime, timedelta
from pyspark.sql.types import *
from pyspark.sql import functions as F

# CHANGE 1: No SparkSession creation — spark is already available in Databricks
# Local: spark = get_spark_session("DataGeneration")

start_time = time.time()

# COMMAND ----------

# MAGIC %md ## Common Reference Data

# COMMAND ----------

REGIONS  = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
BASE_DATE = datetime(2026, 1, 1)

print("=" * 60)
print("  UTILITICS — DATA GENERATION")
print("  Categories: Time Series, Snapshot, File Data")
print("=" * 60)

# COMMAND ----------

# MAGIC %md ## 1. Time Series — Smart Meter Readings

# COMMAND ----------

print(f"\n[1/3] Generating Time Series data...")
print(f"      {DATA_CONFIG['timeseries']['num_meters']} meters × "
      f"{DATA_CONFIG['timeseries']['num_days']} days × "
      f"{DATA_CONFIG['timeseries']['readings_per_day']} readings/day")

schema_ts = StructType([
    StructField("meter_id",            StringType(),    False),
    StructField("reading_timestamp",   TimestampType(), False),
    StructField("reading_value_kwh",   DoubleType(),    False),
    StructField("reading_quality",     StringType(),    True),
    StructField("meter_type",          StringType(),    False),
    StructField("region_code",         StringType(),    False),
    StructField("data_source",         StringType(),    False),
])

quality_codes   = ["VALID", "ESTIMATED", "SUSPECT", "MISSING"]
quality_weights = [0.85, 0.08, 0.05, 0.02]
meter_types     = ["SMART_ELEC", "SMART_GAS", "LEGACY_ELEC"]

ts_rows = []
num_meters       = DATA_CONFIG["timeseries"]["num_meters"]
num_days         = DATA_CONFIG["timeseries"]["num_days"]
readings_per_day = DATA_CONFIG["timeseries"]["readings_per_day"]

for meter_idx in range(num_meters):
    meter_id = f"MTR-{meter_idx:06d}"
    region   = REGIONS[meter_idx % len(REGIONS)]
    m_type   = meter_types[meter_idx % len(meter_types)]
    base_consumption = random.uniform(0.5, 3.0)

    for day in range(num_days):
        for reading in range(readings_per_day):
            ts   = BASE_DATE + timedelta(days=day, minutes=reading * 30)
            hour = ts.hour

            if   7 <= hour <=  9: hour_factor = 1.5
            elif 17 <= hour <= 20: hour_factor = 1.8
            elif 10 <= hour <= 16: hour_factor = 1.2
            elif 21 <= hour <= 23: hour_factor = 1.0
            else:                  hour_factor = 0.4

            value   = round(base_consumption * hour_factor * random.uniform(0.8, 1.2), 4)
            quality = random.choices(quality_codes, quality_weights)[0]
            ts_rows.append((meter_id, ts, value, quality, m_type, region, "UTILITICS_METERING"))

ts_df    = spark.createDataFrame(ts_rows, schema_ts)
ts_count = ts_df.count()
ts_df.write.mode("overwrite").parquet(get_path("raw_timeseries"))
print(f"      Generated: {ts_count:,} records → {get_path('raw_timeseries')}")

# COMMAND ----------

# MAGIC %md ## 2. Snapshot — Network Assets (CSV on DBFS)
# MAGIC
# MAGIC **Local version** wrote to SQLite via SQLAlchemy.
# MAGIC **Community Edition** writes to CSV on DBFS (no external DB needed).
# MAGIC **Part 2 Azure** will write to Azure SQL via JDBC.

# COMMAND ----------

print(f"\n[2/3] Generating Snapshot data...")
print(f"      {DATA_CONFIG['snapshot']['num_assets']} assets × "
      f"{DATA_CONFIG['snapshot']['num_snapshots']} daily snapshots")

schema_snap = StructType([
    StructField("asset_id",              StringType(),  False),
    StructField("snapshot_date",         StringType(),  False),   # stored as string in CSV
    StructField("asset_type",            StringType(),  False),
    StructField("status",                StringType(),  False),
    StructField("capacity_mw",           DoubleType(),  True),
    StructField("voltage_kv",            DoubleType(),  True),
    StructField("location_lat",          DoubleType(),  True),
    StructField("location_lon",          DoubleType(),  True),
    StructField("parent_asset_id",       StringType(),  True),
    StructField("last_maintenance_date", StringType(),  True),
    StructField("firmware_version",      StringType(),  True),
])

asset_types    = ["TRANSFORMER", "SWITCH", "CABLE", "METER_POINT", "SUBSTATION"]
statuses       = ["ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED"]
status_weights = [0.80, 0.10, 0.07, 0.03]
voltage_levels = [11.0, 33.0, 66.0, 132.0, 275.0, 400.0]

snap_rows    = []
num_assets   = DATA_CONFIG["snapshot"]["num_assets"]
num_snapshots= DATA_CONFIG["snapshot"]["num_snapshots"]

for snap_day in range(num_snapshots):
    snap_date = str(BASE_DATE.date() + timedelta(days=snap_day))
    for asset_idx in range(num_assets):
        asset_id = f"AST-{asset_idx:07d}"
        a_type   = asset_types[asset_idx % len(asset_types)]
        status   = random.choices(statuses, status_weights)[0]
        maint_date = str(BASE_DATE.date() - timedelta(days=random.randint(1, 365)))
        parent = f"AST-{random.randint(0, 100):07d}" if random.random() > 0.3 else None

        snap_rows.append((
            asset_id, snap_date, a_type, status,
            round(random.uniform(10, 500), 2),
            random.choice(voltage_levels),
            round(random.uniform(50.0, 58.0), 6),
            round(random.uniform(-6.0,  2.0), 6),
            parent, maint_date,
            f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}"
        ))

snap_df    = spark.createDataFrame(snap_rows, schema_snap)
snap_count = snap_df.count()

# Write as CSV to DBFS (single file for easy reading in bronze step)
snap_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(
    get_path("raw_snapshot_csv").replace("/network_asset_snapshot.csv", ""))
print(f"      Generated: {snap_count:,} records → {get_path('raw_snapshot_csv')}")

# COMMAND ----------

# MAGIC %md ## 3. File Data — ERM Demand Forecasts

# COMMAND ----------

print(f"\n[3/3] Generating File/Forecast data...")
print(f"      {DATA_CONFIG['files']['num_forecasts']} forecasts × "
      f"{DATA_CONFIG['files']['forecast_hours']} hours each")

schema_file = StructType([
    StructField("forecast_id",          StringType(),  False),
    StructField("forecast_date",        StringType(),  False),
    StructField("horizon_hours",        IntegerType(), False),
    StructField("predicted_demand_mw",  DoubleType(),  False),
    StructField("confidence_lower",     DoubleType(),  True),
    StructField("confidence_upper",     DoubleType(),  True),
    StructField("model_version",        StringType(),  False),
    StructField("region",               StringType(),  False),
    StructField("scenario",             StringType(),  False),
])

scenarios      = ["BASE", "HIGH", "LOW", "STRESS"]
file_rows      = []
num_forecasts  = DATA_CONFIG["files"]["num_forecasts"]
forecast_hours = DATA_CONFIG["files"]["forecast_hours"]

for fc_idx in range(num_forecasts):
    fc_id      = f"FC-{fc_idx:06d}"
    fc_date    = str(BASE_DATE.date() + timedelta(days=fc_idx % 30))
    region     = REGIONS[fc_idx % len(REGIONS)]
    scenario   = scenarios[fc_idx % len(scenarios)]
    base_demand= random.uniform(500, 2000)

    for hour in range(forecast_hours):
        hour_of_day = hour % 24
        if   7 <= hour_of_day <=  9: time_factor = 1.4
        elif 17 <= hour_of_day <= 20: time_factor = 1.6
        elif 10 <= hour_of_day <= 16: time_factor = 1.1
        else:                         time_factor = 0.6

        demand          = base_demand * time_factor * random.uniform(0.95, 1.05)
        horizon_factor  = 1 + (hour / forecast_hours) * 0.5
        margin          = demand * 0.05 * horizon_factor

        file_rows.append((
            fc_id, fc_date, hour,
            round(demand, 2),
            round(demand - margin, 2),
            round(demand + margin, 2),
            "ERM-v3.2.1", region, scenario
        ))

file_df    = spark.createDataFrame(file_rows, schema_file)
file_count = file_df.count()
file_df.write.mode("overwrite").parquet(get_path("raw_files"))
print(f"      Generated: {file_count:,} records → {get_path('raw_files')}")

# COMMAND ----------

# MAGIC %md ## Summary

# COMMAND ----------

elapsed       = round(time.time() - start_time, 1)
total_records = ts_count + snap_count + file_count

print("\n" + "=" * 60)
print("  UTILITICS — DATA GENERATION COMPLETE")
print("=" * 60)
print(f"  Time Series:  {ts_count:>10,} records")
print(f"  Snapshot:     {snap_count:>10,} records")
print(f"  File Data:    {file_count:>10,} records")
print(f"  {'─' * 35}")
print(f"  Total:        {total_records:>10,} records")
print(f"  Elapsed:      {elapsed} seconds")
print("=" * 60)

# CHANGE 3: display() instead of df.show() for Databricks rich rendering
display(ts_df.limit(5))
