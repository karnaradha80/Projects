# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # 00 — Shared Configuration
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Run this notebook first in every session via `%run ./00_config`.
# MAGIC Configures ADLS Gen2 access and all paths. No SparkSession needed.
# MAGIC
# MAGIC ### Path strategy
# MAGIC | Environment | Approach |
# MAGIC |-------------|----------|
# MAGIC | Local | `C:/Projects/databricks-poc/lake/` |
# MAGIC | Azure Databricks + Unity Catalog | `abfss://` direct paths (mounts disabled) |

# COMMAND ----------

# ============================================================
# ADLS Gen2 — read credentials from secret scope and configure
# Spark to access storage directly via abfss:// protocol.
# No dbutils.fs.mount() needed (disabled with Unity Catalog).
# ============================================================

STORAGE_ACCOUNT = dbutils.secrets.get(scope="poc-secrets", key="storage-account-name")
STORAGE_KEY     = dbutils.secrets.get(scope="poc-secrets", key="storage-account-key")

# Set the account key so all abfss:// reads/writes are authenticated
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    STORAGE_KEY
)

RAW_BASE       = f"abfss://raw-data@{STORAGE_ACCOUNT}.dfs.core.windows.net"
PROCESSED_BASE = f"abfss://processed-data@{STORAGE_ACCOUNT}.dfs.core.windows.net"

# COMMAND ----------

PATHS = {
    # Raw data sources (ADLS Gen2 — raw-data container)
    "raw_timeseries":       f"{RAW_BASE}/timeseries",
    "raw_snapshot":         f"{RAW_BASE}/snapshot",
    "raw_files":            f"{RAW_BASE}/files",

    # Bronze Delta tables (ADLS Gen2 — processed-data container)
    "bronze_timeseries":    f"{PROCESSED_BASE}/bronze/timeseries",
    "bronze_snapshot":      f"{PROCESSED_BASE}/bronze/snapshot",
    "bronze_files":         f"{PROCESSED_BASE}/bronze/files",

    # Silver Delta tables
    "silver_timeseries":    f"{PROCESSED_BASE}/silver/timeseries",
    "silver_snapshot":      f"{PROCESSED_BASE}/silver/snapshot",
    "silver_files":         f"{PROCESSED_BASE}/silver/files",

    # Gold Delta tables
    "gold_daily_meter":     f"{PROCESSED_BASE}/gold/daily_meter_summary",
    "gold_regional_demand": f"{PROCESSED_BASE}/gold/regional_demand",
    "gold_network_assets":  f"{PROCESSED_BASE}/gold/network_assets",
    "gold_forecast_summary":f"{PROCESSED_BASE}/gold/forecast_summary",

    # Vendor output (bi-directional sharing)
    "vendor_forecast_output": f"{PROCESSED_BASE}/gold/vendor_forecast_output",
}

def get_path(key):
    return PATHS[key]

# COMMAND ----------

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
# Azure SQL config (future Phase — replaces snapshot Parquet)
# Uncomment when Azure SQL is provisioned and secrets are stored
# Secret scope: poc-secrets (already created)
# ============================================================
# AZURE_SQL_CONFIG = {
#     "jdbc_url":    "jdbc:sqlserver://<server>.database.windows.net:1433;database=<db>",
#     "jdbc_driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
#     "table_name":  "network_asset_snapshot",
#     "username":    dbutils.secrets.get("poc-secrets", "sql-username"),
#     "password":    dbutils.secrets.get("poc-secrets", "sql-password"),
# }

# COMMAND ----------

print("✅ Config loaded")
print(f"   Storage account: {STORAGE_ACCOUNT}")
print(f"   Raw base:        {RAW_BASE}")
print(f"   Processed base:  {PROCESSED_BASE}")
print(f"   Tables configured: {len(PATHS)}")
