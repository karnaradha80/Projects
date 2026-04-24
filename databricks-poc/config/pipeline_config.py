"""
Pipeline Configuration
All paths and settings used across the pipeline.
Switch MODE to "azure" when migrating to Part 2.
Switch RUNTIME to "databricks" to run on Databricks Community Edition.
"""

import os

# ============================================================
# MODE: "local" for Windows development, "azure" for cloud
# ============================================================
MODE = "local"

# ============================================================
# RUNTIME: where the pipeline actually executes
#   "local"       — runs on this machine via subprocess (default)
#   "databricks"  — triggers notebooks on Databricks Community Edition
#                   via REST API (requires DATABRICKS_TOKEN env var)
# ============================================================
RUNTIME = "local"

# ============================================================
# Databricks connection (only used when RUNTIME = "databricks")
# ============================================================
DATABRICKS_CONFIG = {
    # Your Community Edition workspace URL
    "workspace_url": "https://community.cloud.databricks.com",

    # Personal Access Token — set as env var, never hardcode
    # Generate in Databricks: User Settings → Access Tokens → Generate New Token
    # Then run: set DATABRICKS_TOKEN=your_token_here  (Windows cmd)
    #       or: $env:DATABRICKS_TOKEN="your_token_here"  (PowerShell)
    "token": os.environ.get("DATABRICKS_TOKEN", ""),

    # Full workspace path to your run_pipeline notebook
    # e.g. "/Users/you@email.com/databricks/run_pipeline"
    "notebook_path": "/Users/<your-email>/databricks/run_pipeline",

    # Cluster ID to attach to (leave blank to spin up a new one per run)
    # Find it in Databricks: Compute → your cluster → Configuration → Tags → ClusterId
    "cluster_id": "",

    # Spark version for new cluster (if cluster_id is blank)
    "spark_version": "13.3.x-scala2.12",
    "node_type":     "Standard_DS3_v2",
}

# ============================================================
# Base paths
# ============================================================
LOCAL_BASE = "C:/Projects/databricks-poc/data/lake"
AZURE_BASE_RAW = "/mnt/raw-data"
AZURE_BASE_PROCESSED = "/mnt/processed-data"

# ============================================================
# Path configuration by mode
# ============================================================
PATHS = {
    "local": {
        # Raw data (source) — three different source formats under sources/ (writable)
        "raw_timeseries": f"{LOCAL_BASE}/sources/timeseries_csv",   # CSV file drop
        "raw_files": f"{LOCAL_BASE}/sources/files_parquet",         # Parquet forecast files

        # Bronze layer
        "bronze_timeseries": f"{LOCAL_BASE}/bronze/timeseries",
        "bronze_snapshot": f"{LOCAL_BASE}/bronze/snapshot",
        "bronze_files": f"{LOCAL_BASE}/bronze/files",

        # Silver layer
        "silver_timeseries": f"{LOCAL_BASE}/silver/timeseries",
        "silver_snapshot": f"{LOCAL_BASE}/silver/snapshot",
        "silver_files": f"{LOCAL_BASE}/silver/files",

        # Gold layer
        "gold_daily_meter": f"{LOCAL_BASE}/gold/daily_meter_summary",
        "gold_regional_demand": f"{LOCAL_BASE}/gold/regional_demand",
        "gold_network_assets": f"{LOCAL_BASE}/gold/network_assets",
        "gold_forecast_summary": f"{LOCAL_BASE}/gold/forecast_summary",
    },
    "azure": {
        "raw_timeseries": f"{AZURE_BASE_RAW}/timeseries",
        "raw_files": f"{AZURE_BASE_RAW}/files",

        "bronze_timeseries": f"{AZURE_BASE_PROCESSED}/bronze/timeseries",
        "bronze_snapshot": f"{AZURE_BASE_PROCESSED}/bronze/snapshot",
        "bronze_files": f"{AZURE_BASE_PROCESSED}/bronze/files",

        "silver_timeseries": f"{AZURE_BASE_PROCESSED}/silver/timeseries",
        "silver_snapshot": f"{AZURE_BASE_PROCESSED}/silver/snapshot",
        "silver_files": f"{AZURE_BASE_PROCESSED}/silver/files",

        "gold_daily_meter": f"{AZURE_BASE_PROCESSED}/gold/daily_meter_summary",
        "gold_regional_demand": f"{AZURE_BASE_PROCESSED}/gold/regional_demand",
        "gold_network_assets": f"{AZURE_BASE_PROCESSED}/gold/network_assets",
        "gold_forecast_summary": f"{AZURE_BASE_PROCESSED}/gold/forecast_summary",
    }
}

# ============================================================
# Database configuration (snapshot source)
# Local:  SQLite   — zero-setup, maps to Azure SQL in Part 2
# Azure:  Azure SQL — same JDBC pattern, just a different URL
# ============================================================
DB_CONFIG = {
    "local": {
        "sqlite_path": f"{LOCAL_BASE}/sources/assets.db",
        "table_name": "network_asset_snapshot",
        "jdbc_url": f"jdbc:sqlite:{LOCAL_BASE}/sources/assets.db",
        "jdbc_driver": "org.sqlite.JDBC",
        "jdbc_package": "org.xerial:sqlite-jdbc:3.44.1.0",
    },
    "azure": {
        # Populated in Part 2 — same JDBC pattern, different driver
        "table_name": "network_asset_snapshot",
        "jdbc_url": "jdbc:sqlserver://<server>.database.windows.net:1433;database=<db>",
        "jdbc_driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        "jdbc_package": None,   # Driver pre-installed in Databricks runtime
    }
}

# ============================================================
# Data generation settings
# ============================================================
DATA_CONFIG = {
    "timeseries": {
        "num_meters": 500,          # Production: millions
        "num_days": 7,              # Production: 30+
        "readings_per_day": 48,     # Every 30 minutes
    },
    "snapshot": {
        "num_assets": 2000,         # Production: 100K+
        "num_snapshots": 7,         # Daily for 7 days
    },
    "files": {
        "num_forecasts": 500,       # Production: thousands
        "forecast_hours": 168,      # 7-day horizon (hourly)
    }
}

# ============================================================
# Quality thresholds
# ============================================================
QUALITY = {
    "max_drop_rate_pct": 20,        # Max acceptable % of records filtered
    "min_completeness_pct": 80,     # Minimum data completeness
    "max_null_pct": 5,              # Maximum null % in critical columns
}


def get_path(key):
    """Get path for current MODE."""
    return PATHS[MODE][key]


def get_all_paths():
    """Get all paths for current MODE."""
    return PATHS[MODE]


def get_db_config():
    """Get database config for current MODE."""
    return DB_CONFIG[MODE]


def get_runtime():
    """Get current RUNTIME setting."""
    return RUNTIME


def get_databricks_config():
    """Get Databricks connection config."""
    return DATABRICKS_CONFIG
