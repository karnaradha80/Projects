"""
02_ingest_bronze.py
===================
Ingest raw data into Bronze Delta Lake tables.

Bronze layer principles:
  - Append-only (no updates, no deletes)
  - Add metadata columns for lineage tracking
  - No business transformations
  - Partition by ingestion date

Run: python notebooks/02_ingest_bronze.py
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, get_db_config

from pyspark.sql import functions as F
from delta import DeltaTable

# ============================================================
# Initialise — load SQLite JDBC driver alongside Delta Lake
# ============================================================
db_cfg = get_db_config()
spark = get_spark_session("BronzeIngestion", extra_packages=db_cfg.get("jdbc_package"))
start_time = time.time()
INGESTION_TS = datetime.now()

print("=" * 60)
print("  BRONZE LAYER INGESTION")
print(f"  Ingestion timestamp: {INGESTION_TS}")
print("=" * 60)


def add_bronze_metadata(df):
    """Add standard metadata columns to a DataFrame."""
    return (df
        .withColumn("_ingestion_timestamp", F.lit(INGESTION_TS))
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_ingestion_date", F.to_date(F.lit(INGESTION_TS)))
    )


def ingest_to_bronze(name, raw_path, bronze_path):
    """Read raw Parquet data and write to Bronze Delta table."""
    print(f"\n  [{name}]")
    print(f"    Source: {raw_path}")
    print(f"    Target: {bronze_path}")

    # Read raw data
    raw_df = spark.read.parquet(raw_path)
    raw_count = raw_df.count()
    print(f"    Raw records: {raw_count:,}")

    # Add metadata
    bronze_df = add_bronze_metadata(raw_df)

    # Write as Delta (append mode for idempotent re-runs)
    (bronze_df.write
        .format("delta")
        .mode("overwrite")  # Use "append" in production for incremental loads
        .partitionBy("_ingestion_date")
        .save(bronze_path))

    # Verify
    written = spark.read.format("delta").load(bronze_path).count()
    dt = DeltaTable.forPath(spark, bronze_path)
    version = dt.history(1).collect()[0]["version"]

    print(f"    Written: {written:,} records (Delta version: {version})")
    return raw_count, written


def ingest_snapshot_to_bronze(bronze_path):
    """
    Read snapshot data from SQLite via JDBC and write to Bronze Delta table.
    In Part 2 this function is unchanged — only the JDBC URL and driver
    in DB_CONFIG switch from SQLite to Azure SQL.
    """
    cfg = get_db_config()
    print(f"\n  [Snapshot — SQLite]")
    print(f"    Source: {cfg['jdbc_url']}  table={cfg['table_name']}")
    print(f"    Target: {bronze_path}")

    # Read via pandas to avoid SQLite JDBC CHAR(0) type mapping issues
    # (SQLite JDBC maps TEXT → CHAR(0) which Delta rejects with invariant violation)
    import pandas as pd
    from sqlalchemy import create_engine
    engine = create_engine(f"sqlite:///{cfg['sqlite_path']}")
    pdf = pd.read_sql_table(cfg["table_name"], engine)
    pdf["snapshot_date"]        = pd.to_datetime(pdf["snapshot_date"]).dt.date
    pdf["last_maintenance_date"] = pd.to_datetime(pdf["last_maintenance_date"]).dt.date
    pdf["capacity_mw"]  = pdf["capacity_mw"].astype(float)
    pdf["voltage_kv"]   = pdf["voltage_kv"].astype(float)
    pdf["location_lat"] = pdf["location_lat"].astype(float)
    pdf["location_lon"] = pdf["location_lon"].astype(float)

    raw_df = spark.createDataFrame(pdf)
    raw_count = raw_df.count()
    print(f"    Raw records: {raw_count:,}")

    # _source_file is not meaningful for DB sources — use JDBC URL instead
    bronze_df = (raw_df
        .withColumn("_ingestion_timestamp", F.lit(INGESTION_TS))
        .withColumn("_source_file", F.lit(cfg["jdbc_url"]))
        .withColumn("_ingestion_date", F.to_date(F.lit(INGESTION_TS))))

    (bronze_df.write
        .format("delta")
        .mode("overwrite")
        .partitionBy("_ingestion_date")
        .save(bronze_path))

    written = spark.read.format("delta").load(bronze_path).count()
    dt = DeltaTable.forPath(spark, bronze_path)
    version = dt.history(1).collect()[0]["version"]

    print(f"    Written: {written:,} records (Delta version: {version})")
    return raw_count, written


# ============================================================
# Ingest all 3 data sources
# ============================================================
results = {}

results["timeseries"] = ingest_to_bronze(
    "Time Series", get_path("raw_timeseries"), get_path("bronze_timeseries"))

results["snapshot"] = ingest_snapshot_to_bronze(get_path("bronze_snapshot"))

results["file_data"] = ingest_to_bronze(
    "File Data", get_path("raw_files"), get_path("bronze_files"))

# ============================================================
# Summary
# ============================================================
elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  BRONZE INGESTION COMPLETE")
print("=" * 60)
print(f"  {'Table':<15} {'Raw':>10} {'Bronze':>10} {'Match':>8}")
print(f"  {chr(0x2500) * 45}")
for name, (raw, bronze) in results.items():
    match = "YES" if raw == bronze else "NO"
    print(f"  {name:<15} {raw:>10,} {bronze:>10,} {match:>8}")
print(f"\n  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
