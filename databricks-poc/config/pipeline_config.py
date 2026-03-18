"""
Pipeline Configuration
All paths and settings used across the pipeline.
Switch MODE to "azure" when migrating to Part 2.
"""

import os

# ============================================================
# MODE: "local" for Windows development, "azure" for cloud
# ============================================================
MODE = "local"

# ============================================================
# Base paths
# ============================================================
LOCAL_BASE = "C:/Projects/databricks-poc/data"
AZURE_BASE_RAW = "/mnt/raw-data"
AZURE_BASE_PROCESSED = "/mnt/processed-data"

# ============================================================
# Path configuration by mode
# ============================================================
PATHS = {
    "local": {
        # Raw data (source)
        "raw_timeseries": f"{LOCAL_BASE}/raw/timeseries",
        "raw_snapshot": f"{LOCAL_BASE}/raw/snapshot",
        "raw_files": f"{LOCAL_BASE}/raw/files",

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
        "raw_snapshot": f"{AZURE_BASE_RAW}/snapshot",
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
