# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 00 — Shared Configuration
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Run this notebook first in every session via `%run ./00_config`.
# MAGIC It sets all DBFS paths, quality thresholds, and data generation settings.
# MAGIC No SparkSession creation needed — Databricks provides `spark` automatically.

# COMMAND ----------

# ============================================================
# CHANGE 1 vs Local: Paths use DBFS instead of C:/
# Local:      C:/Projects/databricks-poc/lake/
# Databricks: dbfs:/utilitics/lake/
# ============================================================

DBFS_BASE = "dbfs:/utilitics/lake"

PATHS = {
    # Raw data sources
    "raw_timeseries":       f"{DBFS_BASE}/raw/timeseries",
    "raw_files":            f"{DBFS_BASE}/raw/files",

    # Snapshot source — CSV on DBFS (Community Edition)
    # Part 2 Azure: replace with JDBC connection to Azure SQL
    "raw_snapshot_csv":     f"{DBFS_BASE}/raw/snapshot/network_asset_snapshot.csv",

    # Bronze Delta tables
    "bronze_timeseries":    f"{DBFS_BASE}/bronze/timeseries",
    "bronze_snapshot":      f"{DBFS_BASE}/bronze/snapshot",
    "bronze_files":         f"{DBFS_BASE}/bronze/files",

    # Silver Delta tables
    "silver_timeseries":    f"{DBFS_BASE}/silver/timeseries",
    "silver_snapshot":      f"{DBFS_BASE}/silver/snapshot",
    "silver_files":         f"{DBFS_BASE}/silver/files",

    # Gold Delta tables
    "gold_daily_meter":     f"{DBFS_BASE}/gold/daily_meter_summary",
    "gold_regional_demand": f"{DBFS_BASE}/gold/regional_demand",
    "gold_network_assets":  f"{DBFS_BASE}/gold/network_assets",
    "gold_forecast_summary":f"{DBFS_BASE}/gold/forecast_summary",

    # Vendor output (bi-directional sharing)
    "vendor_forecast_output": f"{DBFS_BASE}/gold/vendor_forecast_output",
}

def get_path(key):
    return PATHS[key]

# ============================================================
# Data generation settings (same as local)
# ============================================================
DATA_CONFIG = {
    "timeseries": {
        "num_meters":        500,
        "num_days":          7,
        "readings_per_day":  48,
    },
    "snapshot": {
        "num_assets":    2000,
        "num_snapshots": 7,
    },
    "files": {
        "num_forecasts":   500,
        "forecast_hours":  168,
    }
}

# ============================================================
# Quality thresholds
# ============================================================
QUALITY = {
    "max_drop_rate_pct":   20,
    "min_completeness_pct": 80,
    "max_null_pct":         5,
}

# ============================================================
# Azure SQL config (Part 2 — replaces SQLite)
# Uncomment and fill in when migrating to Azure
# ============================================================
# AZURE_SQL_CONFIG = {
#     "jdbc_url":    "jdbc:sqlserver://<server>.database.windows.net:1433;database=<db>",
#     "jdbc_driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
#     "table_name":  "network_asset_snapshot",
#     "username":    dbutils.secrets.get("utilitics-kv", "sql-username"),
#     "password":    dbutils.secrets.get("utilitics-kv", "sql-password"),
# }

print("✅ Config loaded")
print(f"   DBFS base: {DBFS_BASE}")
print(f"   Tables configured: {len(PATHS)}")
