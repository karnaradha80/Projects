# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 02 — Bronze Layer Ingestion
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Reads raw sources → adds metadata → writes Bronze Delta tables.
# MAGIC
# MAGIC ### Changes from local version
# MAGIC | # | Local | Databricks |
# MAGIC |---|-------|-----------|
# MAGIC | 1 | `get_spark_session(extra_packages=...)` | Removed — `spark` pre-exists, JDBC drivers built-in |
# MAGIC | 2 | `C:/Projects/.../lake/` | `dbfs:/utilitics/lake/` |
# MAGIC | 3 | `df.show()` | `display(df)` |
# MAGIC | 4 | Snapshot read via SQLite (pandas) | Snapshot read from Parquet on ADLS Gen2 |

# COMMAND ----------

%run ./00_config

# COMMAND ----------

import time
from datetime import datetime
from pyspark.sql import functions as F
from delta.tables import DeltaTable

# CHANGE 1: No SparkSession — spark already available
start_time   = time.time()
INGESTION_TS = datetime.now()

print("=" * 60)
print("  UTILITICS — BRONZE LAYER INGESTION")
print(f"  Ingestion timestamp: {INGESTION_TS}")
print("=" * 60)

# COMMAND ----------

# MAGIC %md ## Helper Functions

# COMMAND ----------

def add_bronze_metadata(df):
    """Add standard lineage columns to any DataFrame."""
    return (df
        .withColumn("_ingestion_timestamp", F.lit(INGESTION_TS))
        .withColumn("_source_file",         F.input_file_name())
        .withColumn("_ingestion_date",      F.to_date(F.lit(INGESTION_TS))))


def ingest_to_bronze(name, raw_path, bronze_path, fmt="parquet"):
    """Read raw Parquet/Delta and write to Bronze Delta table."""
    print(f"\n  [{name}]")
    print(f"    Source: {raw_path}")
    print(f"    Target: {bronze_path}")

    raw_df    = spark.read.format(fmt).load(raw_path)
    raw_count = raw_df.count()
    print(f"    Raw records: {raw_count:,}")

    bronze_df = add_bronze_metadata(raw_df)
    (bronze_df.write
        .format("delta")
        .mode("overwrite")
        .partitionBy("_ingestion_date")
        .save(bronze_path))

    written = spark.read.format("delta").load(bronze_path).count()
    dt      = DeltaTable.forPath(spark, bronze_path)
    version = dt.history(1).collect()[0]["version"]
    print(f"    Written: {written:,} records (Delta version: {version})")
    return raw_count, written


    # Note: snapshot uses the same ingest_to_bronze() as the other sources.
    # The snapshot Parquet already has correct native types (DateType, DoubleType)
    # because 01_generate_data.py writes it with an explicit schema.
    # Future: replace with JDBC read from Azure SQL:
    #   raw_df = (spark.read.format("jdbc")
    #       .option("url",      AZURE_SQL_CONFIG["jdbc_url"])
    #       .option("dbtable",  AZURE_SQL_CONFIG["table_name"])
    #       .option("driver",   AZURE_SQL_CONFIG["jdbc_driver"])
    #       .option("user",     AZURE_SQL_CONFIG["username"])
    #       .option("password", AZURE_SQL_CONFIG["password"])
    #       .load())

# COMMAND ----------

# MAGIC %md ## Ingest All 3 Sources

# COMMAND ----------

results = {}

results["timeseries"] = ingest_to_bronze(
    "Time Series",
    get_path("raw_timeseries"),
    get_path("bronze_timeseries"))

results["snapshot"] = ingest_to_bronze(
    "Snapshot",
    get_path("raw_snapshot"),
    get_path("bronze_snapshot"))

results["file_data"] = ingest_to_bronze(
    "File Data",
    get_path("raw_files"),
    get_path("bronze_files"))

# COMMAND ----------

# MAGIC %md ## Summary

# COMMAND ----------

elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  UTILITICS — BRONZE INGESTION COMPLETE")
print("=" * 60)
print(f"  {'Table':<15} {'Raw':>10} {'Bronze':>10} {'Match':>8}")
print(f"  {'─' * 45}")
for name, (raw, bronze) in results.items():
    match = "YES" if raw == bronze else "NO"
    print(f"  {name:<15} {raw:>10,} {bronze:>10,} {match:>8}")
print(f"\n  Elapsed: {elapsed} seconds")
print("=" * 60)

# CHANGE 3: display() for rich table rendering in Databricks
display(spark.read.format("delta").load(get_path("bronze_timeseries")).limit(5))
