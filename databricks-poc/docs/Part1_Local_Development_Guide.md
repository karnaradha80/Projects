# Part 1: Local Development Guide
# Azure Databricks Data Sharing Platform – Complete Local Setup

| Field            | Value                                              |
|------------------|----------------------------------------------------|
| Version          | 1.0                                                |
| Date             | 2026-03-16                                         |
| Based On         | SoW – Azure Databricks SME Data Sharing Platform   |
| Purpose          | Build the entire data platform locally before cloud |
| Cost             | **$0 (Completely FREE)**                           |
| Machine          | Windows 11, 24 GB RAM, 1 TB SSD                   |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Why Local First?](#2-why-local-first)
3. [Machine Readiness Check](#3-machine-readiness-check)
4. [Software Installation – Step by Step](#4-software-installation--step-by-step)
5. [Project Structure Setup](#5-project-structure-setup)
6. [Configuration Management](#6-configuration-management)
7. [Data Generation – All 3 Categories](#7-data-generation--all-3-categories)
8. [Bronze Layer – Raw Ingestion Pipeline](#8-bronze-layer--raw-ingestion-pipeline)
9. [Silver Layer – Cleansing & Validation Pipeline](#9-silver-layer--cleansing--validation-pipeline)
10. [Gold Layer – Business Aggregation Pipeline](#10-gold-layer--business-aggregation-pipeline)
11. [Pipeline Orchestration (Run All)](#11-pipeline-orchestration-run-all)
12. [Pipeline Validation & Quality Checks](#12-pipeline-validation--quality-checks)
13. [Delta Sharing – Local Simulation](#13-delta-sharing--local-simulation)
14. [Databricks Community Edition (FREE Cloud)](#14-databricks-community-edition-free-cloud)
15. [Data Exploration & Visualisation](#15-data-exploration--visualisation)
16. [Performance Tuning on Local Machine](#16-performance-tuning-on-local-machine)
17. [Troubleshooting Guide](#17-troubleshooting-guide)
18. [What You Will Learn](#18-what-you-will-learn)
19. [Preparing for Part 2 (Azure)](#19-preparing-for-part-2-azure)

---

## 1. Executive Summary

This document provides a **complete, step-by-step guide** to build the entire Databricks Data Sharing Platform on your local Windows 11 machine at **zero cost**. You will install all necessary software, generate realistic synthetic data matching the SoW requirements, build the full Medallion architecture (Bronze → Silver → Gold), simulate Delta Sharing, and validate the entire pipeline — all before touching Azure.

### What You Will Build Locally

```
┌─────────────────────────────────────────────────────────────────┐
│              YOUR WINDOWS 11 MACHINE (24 GB RAM, 1 TB SSD)      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PySpark + Delta Lake Engine                              │   │
│  │                                                           │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐           │   │
│  │  │  BRONZE   │───▶│  SILVER  │───▶│   GOLD   │           │   │
│  │  │  (Raw)    │    │ (Clean)  │    │(Business)│           │   │
│  │  │ 266K rows │    │ 265K rows│    │  10K rows│           │   │
│  │  └──────────┘    └──────────┘    └──────────┘           │   │
│  │       ▲                                  │                │   │
│  │       │                                  ▼                │   │
│  │  ┌──────────┐                   ┌──────────────────┐     │   │
│  │  │Synthetic │                   │  Delta Sharing    │     │   │
│  │  │Data Gen  │                   │  (OSS Server)     │     │   │
│  │  │(3 types) │                   │  Local simulation │     │   │
│  │  └──────────┘                   └──────────────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Jupyter Notebook (Exploration & Visualisation)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Databricks Community Edition (FREE cloud practice)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Timeline

| Week | Activities | Hours/Week |
|------|-----------|------------|
| Week 1 | Install software, generate data, Bronze layer | 8-10 hrs |
| Week 2 | Silver layer, Gold layer, validation | 8-10 hrs |
| Week 3 | Delta Sharing simulation, Community Edition, exploration | 6-8 hrs |
| Week 4 | Performance tuning, documentation, prepare for Part 2 | 4-6 hrs |

---

## 2. Why Local First?

| Benefit | Explanation |
|---------|-------------|
| **$0 cost** | No cloud charges while learning fundamentals |
| **Fast iteration** | No cluster startup wait (3-5 min on cloud); instant on local |
| **No budget anxiety** | Experiment freely without watching costs |
| **Learn PySpark deeply** | Understand what happens under the hood |
| **Debug easily** | Full access to logs, Spark UI, file system |
| **Work offline** | Learn on train, plane, anywhere |
| **Your machine is powerful** | 24 GB RAM + 1 TB SSD handles 500 MB+ datasets easily |
| **Smooth cloud migration** | Same code runs on Azure with only path changes |

---

## 3. Machine Readiness Check

### 3.1 Your System Specifications

| Component | Your Machine | Minimum Required | Status |
|-----------|-------------|------------------|--------|
| OS | Windows 11 | Windows 10+ | Excellent |
| RAM | 24 GB | 8 GB | Excellent — can run Spark comfortably |
| Storage | 1 TB SSD | 50 GB free | Excellent — plenty for data + Delta tables |
| CPU | (check below) | 4+ cores | Check |

### 3.2 Check Your System

Open **PowerShell** (right-click Start → Terminal) and run:

```powershell
# Check CPU
Get-WmiObject -Class Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# Check RAM
[math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)

# Check free disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{N='FreeGB';E={[math]::Round($_.FreeSpace/1GB,2)}}

# Check if Python is installed
python --version

# Check if Java is installed
java -version
```

### 3.3 Disk Space Planning

| Data | Estimated Size |
|------|---------------|
| Raw synthetic data (Parquet) | ~80 MB |
| Bronze Delta tables | ~100 MB |
| Silver Delta tables | ~90 MB |
| Gold Delta tables | ~20 MB |
| Software (Java, Python, Spark) | ~1.5 GB |
| **Total** | **~2 GB** |

> Your 1 TB SSD has more than enough space. No concerns here.

---

## 4. Software Installation – Step by Step

### 4.1 Install Java 11 (Required for Spark)

PySpark runs on the JVM, so Java is mandatory.

**Step 1:** Download OpenJDK 11

1. Open browser → go to **adoptium.net** (Eclipse Temurin)
2. Select: **Operating System: Windows**, **Architecture: x64**, **Package Type: JDK**, **Version: 11**
3. Download the `.msi` installer
4. Run the installer with default options

**Step 2:** Set JAVA_HOME environment variable

```powershell
# Open PowerShell as Administrator

# Set JAVA_HOME (adjust path if your installation is different)
[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-11.0.21.9-hotspot", "Machine")

# Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
[System.Environment]::SetEnvironmentVariable("Path", "$currentPath;%JAVA_HOME%\bin", "Machine")
```

**Step 3:** Verify (open NEW PowerShell window)

```powershell
java -version
# Expected: openjdk version "11.x.x"

echo $env:JAVA_HOME
# Expected: C:\Program Files\Eclipse Adoptium\jdk-11.0.21.9-hotspot
```

### 4.2 Install Python 3.10+

**Step 1:** Download Python

1. Go to **python.org/downloads**
2. Download Python **3.10.x** or **3.11.x** (do NOT use 3.12+ as PySpark may have compatibility issues)
3. Run installer
4. **IMPORTANT:** Check the box **"Add Python to PATH"** before clicking Install

**Step 2:** Verify

```powershell
python --version
# Expected: Python 3.10.x or 3.11.x

pip --version
# Expected: pip 23.x+
```

### 4.3 Install Hadoop winutils (Required for Spark on Windows)

Spark on Windows needs Hadoop binaries. Without this, you'll get "Could not locate executable null\bin\winutils.exe" errors.

```powershell
# Create Hadoop directory
mkdir C:\hadoop\bin

# Download winutils.exe for Hadoop 3.3.x
# Go to GitHub: github.com/cdarlint/winutils
# Navigate to hadoop-3.3.1/bin/
# Download: winutils.exe and hadoop.dll
# Save both to C:\hadoop\bin\

# Set HADOOP_HOME
[System.Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "Machine")

# Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
[System.Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\hadoop\bin", "Machine")
```

**Verify** (open NEW PowerShell):

```powershell
echo $env:HADOOP_HOME
# Expected: C:\hadoop

winutils.exe chmod 777 C:\tmp
# Should run without error
```

### 4.4 Create Python Virtual Environment

```powershell
# Navigate to your projects directory
mkdir C:\Projects\databricks-poc
cd C:\Projects\databricks-poc

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get an execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
```

### 4.5 Install Python Packages

```powershell
# Make sure venv is activated (you should see (venv) in prompt)

# Core packages
pip install pyspark==3.5.1
pip install delta-spark==3.1.0

# Delta Sharing (for local simulation)
pip install delta-sharing

# Data exploration & visualization
pip install jupyter notebook
pip install pandas pyarrow matplotlib seaborn

# Utility
pip install tqdm python-dotenv

# Verify installations
pip list | findstr "pyspark delta"
# Expected:
# delta-sharing      x.x.x
# delta-spark        3.1.0
# pyspark            3.5.1
```

### 4.6 Verify Complete Setup

Create a test file `test_setup.py`:

```python
"""
Test script to verify all installations are working.
Run: python test_setup.py
"""

print("=" * 60)
print("  INSTALLATION VERIFICATION")
print("=" * 60)

# 1. Test Java
import subprocess
result = subprocess.run(["java", "-version"], capture_output=True, text=True)
java_version = result.stderr.split("\n")[0]
print(f"\n[1] Java: {java_version}")

# 2. Test PySpark
from pyspark.sql import SparkSession
spark = (SparkSession.builder
    .appName("SetupTest")
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .master("local[*]")
    .getOrCreate())

print(f"[2] PySpark: {spark.version}")
print(f"    Spark master: {spark.sparkContext.master}")
print(f"    Cores available: {spark.sparkContext.defaultParallelism}")

# 3. Test Delta Lake
df = spark.range(100).toDF("id")
df.write.format("delta").mode("overwrite").save("test_delta_table")
delta_df = spark.read.format("delta").load("test_delta_table")
print(f"[3] Delta Lake: Working (wrote & read {delta_df.count()} rows)")

# 4. Test Delta operations
from delta import DeltaTable
dt = DeltaTable.forPath(spark, "test_delta_table")
print(f"    Delta version: {dt.history().count() - 1}")

# 5. Cleanup
import shutil
shutil.rmtree("test_delta_table")
print("[4] Cleanup: test_delta_table removed")

# 6. Memory check
import psutil
ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
ram_available = round(psutil.virtual_memory().available / (1024**3), 1)
print(f"\n[5] System: {ram_gb} GB RAM ({ram_available} GB available)")

spark.stop()

print("\n" + "=" * 60)
print("  ALL CHECKS PASSED - Ready to build pipelines!")
print("=" * 60)
```

```powershell
# Install psutil for the test
pip install psutil

# Run the test
python test_setup.py
```

**Expected output:**

```
============================================================
  INSTALLATION VERIFICATION
============================================================

[1] Java: openjdk version "11.0.21" 2023-10-17
[2] PySpark: 3.5.1
    Spark master: local[*]
    Cores available: 8
[3] Delta Lake: Working (wrote & read 100 rows)
    Delta version: 0
[4] Cleanup: test_delta_table removed

[5] System: 24.0 GB RAM (18.5 GB available)

============================================================
  ALL CHECKS PASSED - Ready to build pipelines!
============================================================
```

---

## 5. Project Structure Setup

### 5.1 Create Directories

```powershell
cd C:\Projects\databricks-poc

# Create full project structure
mkdir config
mkdir notebooks
mkdir data\raw\timeseries
mkdir data\raw\snapshot
mkdir data\raw\files
mkdir data\bronze\timeseries
mkdir data\bronze\snapshot
mkdir data\bronze\files
mkdir data\silver\timeseries
mkdir data\silver\snapshot
mkdir data\silver\files
mkdir data\gold\daily_meter_summary
mkdir data\gold\regional_demand
mkdir data\gold\network_assets
mkdir data\gold\forecast_summary
mkdir delta_sharing
mkdir logs
mkdir tests
```

### 5.2 Final Structure

```
C:\Projects\databricks-poc\
├── venv\                          ← Python virtual environment
├── config\
│   ├── __init__.py
│   ├── pipeline_config.py         ← Paths & settings
│   └── spark_config.py            ← Spark session factory
├── notebooks\
│   ├── 01_generate_data.py        ← Synthetic data generator
│   ├── 02_ingest_bronze.py        ← Bronze layer ingestion
│   ├── 03_transform_silver.py     ← Silver layer transformation
│   ├── 04_aggregate_gold.py       ← Gold layer aggregation
│   ├── 05_validate.py             ← Pipeline validation
│   ├── 06_explore_data.ipynb      ← Jupyter exploration notebook
│   └── run_pipeline.py            ← Orchestrator (runs all steps)
├── delta_sharing\
│   ├── server_config.yaml         ← Delta Sharing OSS server config
│   ├── recipient_profile.json     ← Simulated vendor profile
│   └── consume_shared_data.py     ← Vendor data consumption script
├── data\
│   ├── raw\                       ← Generated synthetic data
│   │   ├── timeseries\
│   │   ├── snapshot\
│   │   └── files\
│   ├── bronze\                    ← Raw Delta tables
│   ├── silver\                    ← Cleaned Delta tables
│   └── gold\                      ← Aggregated Delta tables
├── logs\                          ← Pipeline execution logs
├── tests\
│   └── test_pipeline.py           ← Automated tests
├── test_setup.py                  ← Installation verifier
└── README.md
```

### 5.3 Create __init__.py for config module

```powershell
# Create empty __init__.py
New-Item -Path config\__init__.py -ItemType File
```

---

## 6. Configuration Management

### 6.1 Spark Session Factory

Create `config/spark_config.py`:

```python
"""
Spark Session Factory
Creates a configured SparkSession with Delta Lake support.
Used by all pipeline notebooks.
"""

from pyspark.sql import SparkSession


def get_spark_session(app_name="DataSharingPOC"):
    """
    Create and return a SparkSession configured for Delta Lake.

    Tuned for: Windows 11, 24 GB RAM, SSD storage
    Allocates 12 GB to Spark (leaving 12 GB for OS + other apps)
    """
    spark = (SparkSession.builder
        .appName(app_name)

        # Delta Lake configuration
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0")
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")

        # Memory configuration (tuned for 24 GB RAM)
        .config("spark.driver.memory", "12g")
        .config("spark.sql.shuffle.partitions", "8")

        # Performance tuning
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.parquet.compression.codec", "snappy")

        # Delta Lake optimisations
        .config("spark.databricks.delta.optimizeWrite.enabled", "true")
        .config("spark.databricks.delta.autoCompact.enabled", "true")

        # Windows-specific: avoid permission issues
        .config("spark.sql.warehouse.dir", "C:/Projects/databricks-poc/spark-warehouse")

        # Local mode using all CPU cores
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark
```

### 6.2 Pipeline Configuration

Create `config/pipeline_config.py`:

```python
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
```

---

## 7. Data Generation – All 3 Categories

### 7.1 Understanding the Data

From the SoW, three data categories need to be shared:

| Category | Production Volume | POC Volume | What It Represents |
|----------|------------------|------------|-------------------|
| **Time Series** | 163 GB/month | ~50 MB | Smart meter readings every 30 min |
| **Snapshot** | 5.2 GB/month | ~15 MB | Daily network asset status |
| **File Data** | 25 GB/month | ~25 MB | ERM demand forecasts (hourly, 7-day horizon) |

### 7.2 Data Generation Script

Create `notebooks/01_generate_data.py`:

```python
"""
01_generate_data.py
==================
Generate realistic synthetic data for all 3 SoW categories.

Data mirrors real-world patterns:
- Time Series: Smart meter readings with consumption patterns
  (higher during day, lower at night)
- Snapshot: Network asset status with realistic UK coordinates
- File Data: Demand forecasts with confidence intervals

Run: python notebooks/01_generate_data.py

Expected output:
  Time Series:  168,000 records (~50 MB)
  Snapshot:      14,000 records (~15 MB)
  File Data:     84,000 records (~25 MB)
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, DATA_CONFIG

from pyspark.sql.types import *

# ============================================================
# Initialise Spark
# ============================================================
spark = get_spark_session("DataGeneration")
start_time = time.time()

print("=" * 60)
print("  DATA GENERATION")
print("  SoW Categories: Time Series, Snapshot, File Data")
print("=" * 60)

# ============================================================
# Common reference data
# ============================================================
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
BASE_DATE = datetime(2026, 1, 1)

# ============================================================
# 1. TIME SERIES DATA
# ============================================================
# What: Smart meter readings recorded every 30 minutes
# Production: ~163 GB/month (~5.4 GB/day)
# POC: 500 meters × 7 days × 48 readings/day = 168,000 records
#
# Realistic patterns:
#   - Consumption higher during daytime (7am-7pm)
#   - Random variation within ±20%
#   - 85% VALID, 8% ESTIMATED, 5% SUSPECT, 2% MISSING quality
# ============================================================

print("\n[1/3] Generating Time Series data...")
print(f"      {DATA_CONFIG['timeseries']['num_meters']} meters × "
      f"{DATA_CONFIG['timeseries']['num_days']} days × "
      f"{DATA_CONFIG['timeseries']['readings_per_day']} readings/day")

schema_ts = StructType([
    StructField("meter_id", StringType(), False),
    StructField("reading_timestamp", TimestampType(), False),
    StructField("reading_value_kwh", DoubleType(), False),
    StructField("reading_quality", StringType(), True),
    StructField("meter_type", StringType(), False),
    StructField("region_code", StringType(), False),
    StructField("data_source", StringType(), False)
])

quality_codes = ["VALID", "ESTIMATED", "SUSPECT", "MISSING"]
quality_weights = [0.85, 0.08, 0.05, 0.02]
meter_types = ["SMART_ELEC", "SMART_GAS", "LEGACY_ELEC"]

ts_rows = []
num_meters = DATA_CONFIG["timeseries"]["num_meters"]
num_days = DATA_CONFIG["timeseries"]["num_days"]
readings_per_day = DATA_CONFIG["timeseries"]["readings_per_day"]

for meter_idx in range(num_meters):
    meter_id = f"MTR-{meter_idx:06d}"
    region = REGIONS[meter_idx % len(REGIONS)]
    m_type = meter_types[meter_idx % len(meter_types)]
    base_consumption = random.uniform(0.5, 3.0)

    for day in range(num_days):
        for reading in range(readings_per_day):
            ts = BASE_DATE + timedelta(days=day, minutes=reading * 30)

            # Realistic consumption: higher during daytime
            hour = ts.hour
            if 7 <= hour <= 9:       # Morning peak
                hour_factor = 1.5
            elif 17 <= hour <= 20:    # Evening peak
                hour_factor = 1.8
            elif 10 <= hour <= 16:    # Daytime
                hour_factor = 1.2
            elif 21 <= hour <= 23:    # Late evening
                hour_factor = 1.0
            else:                     # Night (midnight - 6am)
                hour_factor = 0.4

            value = round(base_consumption * hour_factor * random.uniform(0.8, 1.2), 4)
            quality = random.choices(quality_codes, quality_weights)[0]

            ts_rows.append((
                meter_id, ts, value, quality, m_type, region, "SPENW_METERING"
            ))

ts_df = spark.createDataFrame(ts_rows, schema_ts)
ts_df.write.mode("overwrite").parquet(get_path("raw_timeseries"))
ts_count = ts_df.count()
print(f"      Generated: {ts_count:,} records")

# ============================================================
# 2. SNAPSHOT DATA
# ============================================================
# What: Daily point-in-time capture of network asset status
# Production: ~5.2 GB/month
# POC: 2,000 assets × 7 days = 14,000 records
#
# Realistic patterns:
#   - 80% ACTIVE, 10% INACTIVE, 7% MAINTENANCE, 3% DECOMMISSIONED
#   - UK coordinates (lat: 50-58, lon: -6 to 2)
#   - Standard voltage levels (11kV, 33kV, 66kV, 132kV, 275kV, 400kV)
# ============================================================

print("\n[2/3] Generating Snapshot data...")
print(f"      {DATA_CONFIG['snapshot']['num_assets']} assets × "
      f"{DATA_CONFIG['snapshot']['num_snapshots']} daily snapshots")

schema_snap = StructType([
    StructField("asset_id", StringType(), False),
    StructField("snapshot_date", DateType(), False),
    StructField("asset_type", StringType(), False),
    StructField("status", StringType(), False),
    StructField("capacity_mw", DoubleType(), True),
    StructField("voltage_kv", DoubleType(), True),
    StructField("location_lat", DoubleType(), True),
    StructField("location_lon", DoubleType(), True),
    StructField("parent_asset_id", StringType(), True),
    StructField("last_maintenance_date", DateType(), True),
    StructField("firmware_version", StringType(), True)
])

asset_types = ["TRANSFORMER", "SWITCH", "CABLE", "METER_POINT", "SUBSTATION"]
statuses = ["ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED"]
status_weights = [0.80, 0.10, 0.07, 0.03]
voltage_levels = [11.0, 33.0, 66.0, 132.0, 275.0, 400.0]

snap_rows = []
num_assets = DATA_CONFIG["snapshot"]["num_assets"]
num_snapshots = DATA_CONFIG["snapshot"]["num_snapshots"]

for snap_day in range(num_snapshots):
    snap_date = BASE_DATE.date() + timedelta(days=snap_day)
    for asset_idx in range(num_assets):
        asset_id = f"AST-{asset_idx:07d}"
        a_type = asset_types[asset_idx % len(asset_types)]
        status = random.choices(statuses, status_weights)[0]

        snap_rows.append((
            asset_id,
            snap_date,
            a_type,
            status,
            round(random.uniform(10, 500), 2),
            random.choice(voltage_levels),
            round(random.uniform(50.0, 58.0), 6),   # UK latitude
            round(random.uniform(-6.0, 2.0), 6),     # UK longitude
            f"AST-{random.randint(0, 100):07d}" if random.random() > 0.3 else None,
            BASE_DATE.date() - timedelta(days=random.randint(1, 365)),
            f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}"
        ))

snap_df = spark.createDataFrame(snap_rows, schema_snap)
snap_df.write.mode("overwrite").parquet(get_path("raw_snapshot"))
snap_count = snap_df.count()
print(f"      Generated: {snap_count:,} records")

# ============================================================
# 3. FILE DATA (ERM Demand Forecasts)
# ============================================================
# What: Energy demand forecasts with 7-day hourly horizon
# Production: ~25 GB/month (spreadsheets + ERM data)
# POC: 500 forecasts × 168 hours = 84,000 records
#
# Realistic patterns:
#   - Demand varies by time of day (peaks at morning/evening)
#   - Confidence interval widens with forecast horizon
#   - 4 scenarios: BASE, HIGH, LOW, STRESS
# ============================================================

print("\n[3/3] Generating File/Forecast data...")
print(f"      {DATA_CONFIG['files']['num_forecasts']} forecasts × "
      f"{DATA_CONFIG['files']['forecast_hours']} hours each")

schema_file = StructType([
    StructField("forecast_id", StringType(), False),
    StructField("forecast_date", DateType(), False),
    StructField("horizon_hours", IntegerType(), False),
    StructField("predicted_demand_mw", DoubleType(), False),
    StructField("confidence_lower", DoubleType(), True),
    StructField("confidence_upper", DoubleType(), True),
    StructField("model_version", StringType(), False),
    StructField("region", StringType(), False),
    StructField("scenario", StringType(), False)
])

scenarios = ["BASE", "HIGH", "LOW", "STRESS"]
file_rows = []
num_forecasts = DATA_CONFIG["files"]["num_forecasts"]
forecast_hours = DATA_CONFIG["files"]["forecast_hours"]

for fc_idx in range(num_forecasts):
    fc_id = f"FC-{fc_idx:06d}"
    fc_date = BASE_DATE.date() + timedelta(days=fc_idx % 30)
    region = REGIONS[fc_idx % len(REGIONS)]
    scenario = scenarios[fc_idx % len(scenarios)]
    base_demand = random.uniform(500, 2000)

    for hour in range(forecast_hours):
        # Demand pattern: peaks at 8am and 6pm
        hour_of_day = hour % 24
        if 7 <= hour_of_day <= 9:
            time_factor = 1.4
        elif 17 <= hour_of_day <= 20:
            time_factor = 1.6
        elif 10 <= hour_of_day <= 16:
            time_factor = 1.1
        else:
            time_factor = 0.6

        demand = base_demand * time_factor * random.uniform(0.95, 1.05)

        # Confidence widens with horizon (uncertainty grows)
        horizon_factor = 1 + (hour / forecast_hours) * 0.5
        margin = demand * 0.05 * horizon_factor

        file_rows.append((
            fc_id, fc_date, hour,
            round(demand, 2),
            round(demand - margin, 2),
            round(demand + margin, 2),
            "ERM-v3.2.1",
            region,
            scenario
        ))

file_df = spark.createDataFrame(file_rows, schema_file)
file_df.write.mode("overwrite").parquet(get_path("raw_files"))
file_count = file_df.count()
print(f"      Generated: {file_count:,} records")

# ============================================================
# Summary
# ============================================================
elapsed = round(time.time() - start_time, 1)
total_records = ts_count + snap_count + file_count

print("\n" + "=" * 60)
print("  DATA GENERATION COMPLETE")
print("=" * 60)
print(f"  Time Series:   {ts_count:>10,} records")
print(f"  Snapshot:       {snap_count:>10,} records")
print(f"  File Data:      {file_count:>10,} records")
print(f"  {'─' * 35}")
print(f"  Total:          {total_records:>10,} records")
print(f"  Elapsed time:   {elapsed} seconds")
print(f"  Data location:  {os.path.dirname(get_path('raw_timeseries'))}")
print("=" * 60)

spark.stop()
```

### 7.3 Run Data Generation

```powershell
cd C:\Projects\databricks-poc
.\venv\Scripts\Activate.ps1
python notebooks/01_generate_data.py
```

---

## 8. Bronze Layer – Raw Ingestion Pipeline

### 8.1 Design Principles

```
Bronze Layer Rules:
  ✓ Append-only (never delete or update)
  ✓ Add ingestion metadata (_ingestion_timestamp, _source_file, _ingestion_date)
  ✓ NO transformations on source data
  ✓ Partition by _ingestion_date (for efficient incremental processing)
  ✓ Store as Delta format (enables time travel, ACID transactions)
```

### 8.2 Bronze Ingestion Script

Create `notebooks/02_ingest_bronze.py`:

```python
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
from config.pipeline_config import get_path

from pyspark.sql import functions as F
from delta import DeltaTable

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("BronzeIngestion")
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
    """Read raw data and write to Bronze Delta table."""
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


# ============================================================
# Ingest all 3 data sources
# ============================================================
results = {}

results["timeseries"] = ingest_to_bronze(
    "Time Series", get_path("raw_timeseries"), get_path("bronze_timeseries"))

results["snapshot"] = ingest_to_bronze(
    "Snapshot", get_path("raw_snapshot"), get_path("bronze_snapshot"))

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
print(f"  {'─' * 45}")
for name, (raw, bronze) in results.items():
    match = "YES" if raw == bronze else "NO"
    print(f"  {name:<15} {raw:>10,} {bronze:>10,} {match:>8}")
print(f"\n  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
```

---

## 9. Silver Layer – Cleansing & Validation Pipeline

### 9.1 Design Principles

```
Silver Layer Rules:
  ✓ Deduplicate records
  ✓ Enforce data types and schema
  ✓ Handle nulls (replace or filter)
  ✓ Apply validation rules (range checks, referential integrity)
  ✓ Standardise values (uppercase, trim whitespace)
  ✓ Add derived columns useful for downstream
  ✓ Partition by business date (not ingestion date)
  ✓ Track records filtered and why
```

### 9.2 Silver Transformation Script

Create `notebooks/03_transform_silver.py`:

```python
"""
03_transform_silver.py
======================
Clean, validate, and standardise Bronze data into Silver.

Transformations per table:
  Time Series: Dedup, range validation, quality codes, peak hours
  Snapshot:    Latest per asset/day, UK coordinates, null handling
  File Data:   Dedup, confidence interval validation, derived cols

Run: python notebooks/03_transform_silver.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, QUALITY

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("SilverTransformation")
start_time = time.time()

print("=" * 60)
print("  SILVER LAYER TRANSFORMATION")
print("=" * 60)

results = {}

# ============================================================
# 1. Silver: Time Series
# ============================================================
print("\n  [Time Series]")
ts_bronze = spark.read.format("delta").load(get_path("bronze_timeseries"))
bronze_count = ts_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

ts_silver = (ts_bronze
    # DEDUP: Same meter + timestamp should not appear twice
    .dropDuplicates(["meter_id", "reading_timestamp"])

    # VALIDATE: Reading must be in reasonable range (0 - 10,000 kWh)
    .filter(F.col("reading_value_kwh").between(0, 10000))

    # STANDARDISE: Clean quality codes
    .withColumn("reading_quality",
        F.when(F.col("reading_quality").isNull(), "UNKNOWN")
         .otherwise(F.upper(F.trim(F.col("reading_quality")))))

    # DERIVE: Add useful columns for downstream analysis
    .withColumn("reading_date", F.to_date("reading_timestamp"))
    .withColumn("reading_hour", F.hour("reading_timestamp"))
    .withColumn("is_peak_hour",
        F.when((F.hour("reading_timestamp") >= 7) &
               (F.hour("reading_timestamp") <= 19), True)
         .otherwise(False))
    .withColumn("day_of_week", F.dayofweek("reading_timestamp"))
    .withColumn("is_weekend",
        F.when(F.dayofweek("reading_timestamp").isin(1, 7), True)
         .otherwise(False))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(ts_silver.write.format("delta").mode("overwrite")
    .partitionBy("reading_date").save(get_path("silver_timeseries")))

silver_count = ts_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["timeseries"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# 2. Silver: Snapshot
# ============================================================
print("\n  [Snapshot]")
snap_bronze = spark.read.format("delta").load(get_path("bronze_snapshot"))
bronze_count = snap_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

# Keep only latest record per asset per day
w_latest = Window.partitionBy("asset_id", "snapshot_date") \
    .orderBy(F.col("_ingestion_timestamp").desc())

snap_silver = (snap_bronze
    # DEDUP: Keep latest ingestion per asset per snapshot day
    .withColumn("_rn", F.row_number().over(w_latest))
    .filter(F.col("_rn") == 1)
    .drop("_rn")

    # VALIDATE: UK geographic bounds
    .filter(F.col("location_lat").between(49.0, 61.0))
    .filter(F.col("location_lon").between(-8.0, 2.0))

    # STANDARDISE: Clean status values
    .withColumn("status", F.upper(F.trim(F.col("status"))))
    .withColumn("asset_type", F.upper(F.trim(F.col("asset_type"))))

    # NULL HANDLING: Default capacity to 0
    .withColumn("capacity_mw",
        F.when(F.col("capacity_mw").isNull(), 0.0)
         .otherwise(F.col("capacity_mw")))

    # DERIVE: Maintenance age
    .withColumn("days_since_maintenance",
        F.datediff(F.col("snapshot_date"), F.col("last_maintenance_date")))
    .withColumn("needs_maintenance",
        F.when(F.col("days_since_maintenance") > 180, True)
         .otherwise(False))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(snap_silver.write.format("delta").mode("overwrite")
    .partitionBy("snapshot_date").save(get_path("silver_snapshot")))

silver_count = snap_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["snapshot"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# 3. Silver: File Data (Forecasts)
# ============================================================
print("\n  [File Data / Forecasts]")
file_bronze = spark.read.format("delta").load(get_path("bronze_files"))
bronze_count = file_bronze.count()
print(f"    Input (Bronze): {bronze_count:,} records")

file_silver = (file_bronze
    # DEDUP: Same forecast + hour should not appear twice
    .dropDuplicates(["forecast_id", "horizon_hours"])

    # VALIDATE: Confidence interval must be valid
    .filter(F.col("confidence_lower") <= F.col("predicted_demand_mw"))
    .filter(F.col("predicted_demand_mw") <= F.col("confidence_upper"))

    # VALIDATE: Demand must be positive
    .filter(F.col("predicted_demand_mw") > 0)

    # DERIVE: Useful forecast analysis columns
    .withColumn("confidence_range_mw",
        F.col("confidence_upper") - F.col("confidence_lower"))
    .withColumn("confidence_pct",
        F.round((F.col("confidence_range_mw") / F.col("predicted_demand_mw")) * 100, 2))
    .withColumn("forecast_day",
        F.floor(F.col("horizon_hours") / 24).cast("int"))
    .withColumn("hour_of_day",
        (F.col("horizon_hours") % 24).cast("int"))

    # METADATA
    .withColumn("_silver_timestamp", F.current_timestamp())
)

(file_silver.write.format("delta").mode("overwrite")
    .partitionBy("forecast_date").save(get_path("silver_files")))

silver_count = file_silver.count()
drop_pct = round((1 - silver_count / bronze_count) * 100, 2)
print(f"    Output (Silver): {silver_count:,} records")
print(f"    Dropped: {bronze_count - silver_count:,} ({drop_pct}%)")
results["file_data"] = (bronze_count, silver_count, drop_pct)

# ============================================================
# Quality Report
# ============================================================
elapsed = round(time.time() - start_time, 1)

print("\n" + "=" * 60)
print("  SILVER TRANSFORMATION COMPLETE")
print("=" * 60)
print(f"  {'Table':<15} {'Bronze':>10} {'Silver':>10} {'Drop%':>8} {'Status':>8}")
print(f"  {'─' * 53}")
for name, (b, s, d) in results.items():
    threshold = QUALITY["max_drop_rate_pct"]
    status = "PASS" if d < threshold else "WARN" if d < threshold * 2 else "FAIL"
    print(f"  {name:<15} {b:>10,} {s:>10,} {d:>7}% {status:>8}")
print(f"\n  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
```

---

## 10. Gold Layer – Business Aggregation Pipeline

### 10.1 Design Principles

```
Gold Layer Rules:
  ✓ Aggregated, business-ready views
  ✓ These are the tables shared with the vendor via Delta Sharing
  ✓ Optimised for consumption (pre-computed metrics)
  ✓ Partitioned by business-relevant date columns
  ✓ Named clearly for business users
```

### 10.2 Gold Aggregation Script

Create `notebooks/04_aggregate_gold.py`:

```python
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
print(f"  {'─' * 37}")
for name, count in results.items():
    print(f"  {name:<25} {count:>10,}")
print(f"\n  Total Gold records: {sum(results.values()):,}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()
```

---

## 11. Pipeline Orchestration (Run All)

Create `notebooks/run_pipeline.py`:

```python
"""
run_pipeline.py
===============
Orchestrator: Runs the entire pipeline end-to-end.
Equivalent to a Databricks Workflow or Azure Data Factory pipeline.

Run: python notebooks/run_pipeline.py

Pipeline steps:
  1. Generate synthetic data
  2. Ingest to Bronze
  3. Transform to Silver
  4. Aggregate to Gold
  5. Validate everything
"""

import subprocess
import sys
import time
from datetime import datetime

SCRIPTS = [
    ("01_generate_data.py",    "Data Generation"),
    ("02_ingest_bronze.py",    "Bronze Ingestion"),
    ("03_transform_silver.py", "Silver Transformation"),
    ("04_aggregate_gold.py",   "Gold Aggregation"),
    ("05_validate.py",         "Pipeline Validation"),
]

print("=" * 60)
print("  PIPELINE ORCHESTRATOR")
print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

overall_start = time.time()
results = []

for i, (script, description) in enumerate(SCRIPTS, 1):
    print(f"\n{'─' * 60}")
    print(f"  Step {i}/{len(SCRIPTS)}: {description}")
    print(f"  Script: {script}")
    print(f"{'─' * 60}")

    step_start = time.time()
    result = subprocess.run(
        [sys.executable, f"notebooks/{script}"],
        capture_output=False,
        text=True
    )
    step_elapsed = round(time.time() - step_start, 1)

    status = "SUCCESS" if result.returncode == 0 else "FAILED"
    results.append((description, status, step_elapsed))

    if result.returncode != 0:
        print(f"\n  *** PIPELINE FAILED at step {i}: {description} ***")
        print(f"  Exit code: {result.returncode}")
        break

# ============================================================
# Pipeline Summary
# ============================================================
overall_elapsed = round(time.time() - overall_start, 1)

print("\n" + "=" * 60)
print("  PIPELINE EXECUTION SUMMARY")
print("=" * 60)
print(f"  {'Step':<25} {'Status':>10} {'Time':>10}")
print(f"  {'─' * 47}")
for desc, status, elapsed in results:
    print(f"  {desc:<25} {status:>10} {elapsed:>8}s")
print(f"  {'─' * 47}")
print(f"  {'TOTAL':<25} {'':>10} {overall_elapsed:>8}s")

all_passed = all(s == "SUCCESS" for _, s, _ in results)
print(f"\n  Overall: {'ALL STEPS PASSED' if all_passed else 'PIPELINE FAILED'}")
print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
```

### Run the full pipeline:

```powershell
cd C:\Projects\databricks-poc
.\venv\Scripts\Activate.ps1
python notebooks/run_pipeline.py
```

---

## 12. Pipeline Validation & Quality Checks

Create `notebooks/05_validate.py`:

```python
"""
05_validate.py
==============
Comprehensive pipeline validation.
Checks data quality, record counts, null rates, and business rules.

Run: python notebooks/05_validate.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path, QUALITY

from pyspark.sql import functions as F
from delta import DeltaTable

# ============================================================
# Initialise
# ============================================================
spark = get_spark_session("PipelineValidation")
start_time = time.time()

print("=" * 60)
print("  PIPELINE VALIDATION REPORT")
print("=" * 60)

all_checks = []

def check(name, passed):
    """Register a validation check."""
    status = "PASS" if passed else "FAIL"
    all_checks.append((name, passed))
    print(f"    [{status}] {name}")
    return passed

# ============================================================
# 1. RECORD COUNTS: Bronze → Silver
# ============================================================
print("\n[1] Record Counts (Bronze → Silver)")
print(f"    {'Table':<15} {'Bronze':>10} {'Silver':>10} {'Drop%':>8}")
print(f"    {'─' * 45}")

for name, b_path, s_path in [
    ("timeseries", get_path("bronze_timeseries"), get_path("silver_timeseries")),
    ("snapshot", get_path("bronze_snapshot"), get_path("silver_snapshot")),
    ("file_data", get_path("bronze_files"), get_path("silver_files"))
]:
    b_count = spark.read.format("delta").load(b_path).count()
    s_count = spark.read.format("delta").load(s_path).count()
    drop_pct = round((1 - s_count / b_count) * 100, 2) if b_count > 0 else 0
    status_str = "PASS" if drop_pct < QUALITY["max_drop_rate_pct"] else "FAIL"
    print(f"    {name:<15} {b_count:>10,} {s_count:>10,} {drop_pct:>7}%  {status_str}")
    check(f"{name}: drop rate < {QUALITY['max_drop_rate_pct']}%",
          drop_pct < QUALITY["max_drop_rate_pct"])

# ============================================================
# 2. GOLD LAYER COUNTS
# ============================================================
print(f"\n[2] Gold Layer Counts")
print(f"    {'Table':<25} {'Records':>10}")
print(f"    {'─' * 37}")

for name, path in [
    ("daily_meter_summary", get_path("gold_daily_meter")),
    ("regional_demand", get_path("gold_regional_demand")),
    ("network_assets", get_path("gold_network_assets")),
    ("forecast_summary", get_path("gold_forecast_summary"))
]:
    count = spark.read.format("delta").load(path).count()
    print(f"    {name:<25} {count:>10,}")
    check(f"gold.{name} has records", count > 0)

# ============================================================
# 3. DATA QUALITY CHECKS
# ============================================================
print(f"\n[3] Data Quality Checks")

# Daily meter summary
dm = spark.read.format("delta").load(get_path("gold_daily_meter"))
check("daily_meter: no null meter_ids",
      dm.filter(F.col("meter_id").isNull()).count() == 0)
check("daily_meter: total_kwh is positive",
      dm.filter(F.col("total_kwh") <= 0).count() == 0)
check("daily_meter: completeness 0-100%",
      dm.filter((F.col("data_completeness_pct") < 0) |
                (F.col("data_completeness_pct") > 100)).count() == 0)
check("daily_meter: peak + offpeak = total",
      dm.filter(F.abs(F.col("peak_hours_kwh") + F.col("offpeak_hours_kwh")
                      - F.col("total_kwh")) > 0.01).count() == 0)

# Network assets
na = spark.read.format("delta").load(get_path("gold_network_assets"))
check("network_assets: no null asset_ids",
      na.filter(F.col("asset_id").isNull()).count() == 0)
check("network_assets: valid statuses only",
      na.filter(~F.col("status").isin(
          "ACTIVE", "INACTIVE", "MAINTENANCE", "DECOMMISSIONED")).count() == 0)
check("network_assets: UK coordinates",
      na.filter(~((F.col("location_lat").between(49.0, 61.0)) &
                  (F.col("location_lon").between(-8.0, 2.0)))).count() == 0)

# Forecast summary
fc = spark.read.format("delta").load(get_path("gold_forecast_summary"))
check("forecast: positive avg demand",
      fc.filter(F.col("avg_predicted_mw") <= 0).count() == 0)
check("forecast: max >= avg",
      fc.filter(F.col("max_predicted_mw") < F.col("avg_predicted_mw")).count() == 0)

# ============================================================
# 4. DELTA TABLE HEALTH
# ============================================================
print(f"\n[4] Delta Table Health")
print(f"    {'Table':<25} {'Version':>8} {'Files':>8}")
print(f"    {'─' * 43}")

all_tables = [
    ("bronze.timeseries", get_path("bronze_timeseries")),
    ("bronze.snapshot", get_path("bronze_snapshot")),
    ("bronze.file_data", get_path("bronze_files")),
    ("silver.timeseries", get_path("silver_timeseries")),
    ("silver.snapshot", get_path("silver_snapshot")),
    ("silver.file_data", get_path("silver_files")),
    ("gold.daily_meter", get_path("gold_daily_meter")),
    ("gold.regional_demand", get_path("gold_regional_demand")),
    ("gold.network_assets", get_path("gold_network_assets")),
    ("gold.forecast_summary", get_path("gold_forecast_summary")),
]

for name, path in all_tables:
    try:
        dt = DeltaTable.forPath(spark, path)
        version = dt.history(1).collect()[0]["version"]
        detail = spark.sql(f"DESCRIBE DETAIL delta.`{path}`").collect()[0]
        files = detail["numFiles"]
        print(f"    {name:<25} {version:>8} {files:>8}")
    except Exception:
        print(f"    {name:<25} {'ERROR':>8} {'':>8}")

# ============================================================
# FINAL RESULT
# ============================================================
elapsed = round(time.time() - start_time, 1)
passed = sum(1 for _, p in all_checks if p)
total = len(all_checks)
all_passed = passed == total

print("\n" + "=" * 60)
print(f"  VALIDATION RESULT: {passed}/{total} checks passed")
print(f"  STATUS: {'ALL PASS' if all_passed else 'ISSUES FOUND'}")
print(f"  Elapsed: {elapsed} seconds")
print("=" * 60)

spark.stop()

# Exit with error code if any checks failed
if not all_passed:
    sys.exit(1)
```

---

## 13. Delta Sharing – Local Simulation

### 13.1 What is Delta Sharing?

Delta Sharing is an open protocol for secure data sharing. In production, Databricks manages this. Locally, we can simulate it using the open-source Delta Sharing server.

### 13.2 Option A: Python-Based Simulation (Simplest)

Create `delta_sharing/simulate_sharing.py`:

```python
"""
simulate_sharing.py
===================
Simulate Delta Sharing locally by reading Gold tables
as if you were the vendor (recipient).

This demonstrates the CONCEPT without needing the OSS server.

Run: python delta_sharing/simulate_sharing.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path

# ============================================================
# PROVIDER SIDE (Your organisation: SPENW)
# ============================================================
print("=" * 60)
print("  DELTA SHARING SIMULATION")
print("=" * 60)

print("\n--- PROVIDER SIDE (SPENW) ---")
print("  Sharing Gold tables with vendor...")

spark = get_spark_session("DeltaSharingSimulation")

# List what's being shared
gold_tables = {
    "daily_meter_summary": get_path("gold_daily_meter"),
    "regional_demand": get_path("gold_regional_demand"),
    "network_assets": get_path("gold_network_assets"),
    "forecast_summary": get_path("gold_forecast_summary"),
}

print(f"\n  Share: vendor_data_share")
print(f"  Tables shared:")
for name, path in gold_tables.items():
    count = spark.read.format("delta").load(path).count()
    print(f"    - gold.{name}: {count:,} records")

# ============================================================
# RECIPIENT SIDE (Simulated Vendor)
# ============================================================
print("\n--- RECIPIENT SIDE (Vendor) ---")
print("  Connecting to shared data...")

# In real Delta Sharing, the vendor would use:
#   delta_sharing.load_as_pandas("profile.json#share.schema.table")
# Locally, we simulate by reading the Gold Delta tables directly.

import pandas as pd

print("\n  [1] Reading: daily_meter_summary (as Pandas)")
dm_df = spark.read.format("delta").load(gold_tables["daily_meter_summary"])
dm_pandas = dm_df.limit(1000).toPandas()
print(f"      Rows received: {len(dm_pandas)}")
print(f"      Columns: {list(dm_pandas.columns)}")
print(f"      Sample:")
print(dm_pandas[["meter_id", "reading_date", "total_kwh", "data_completeness_pct"]].head())

print("\n  [2] Reading: regional_demand")
rd_df = spark.read.format("delta").load(gold_tables["regional_demand"])
rd_pandas = rd_df.limit(100).toPandas()
print(f"      Rows received: {len(rd_pandas)}")
print(f"      Regions: {sorted(rd_pandas['region_code'].unique())}")

print("\n  [3] Reading: network_assets")
na_df = spark.read.format("delta").load(gold_tables["network_assets"])
na_pandas = na_df.toPandas()
print(f"      Rows received: {len(na_pandas)}")
print(f"      Asset types: {dict(na_pandas['asset_type'].value_counts())}")
print(f"      Status breakdown: {dict(na_pandas['status'].value_counts())}")

print("\n  [4] Reading: forecast_summary")
fc_df = spark.read.format("delta").load(gold_tables["forecast_summary"])
fc_pandas = fc_df.limit(100).toPandas()
print(f"      Rows received: {len(fc_pandas)}")
print(f"      Scenarios: {sorted(fc_pandas['scenario'].unique())}")

# ============================================================
# VENDOR PROCESSING (What vendor would do with the data)
# ============================================================
print("\n--- VENDOR PROCESSING ---")
print("  Vendor analyses the received data...")

# Example: Vendor computes regional demand forecast accuracy
print("\n  Analysis 1: Regional demand peaks")
peak_demand = (rd_df
    .groupBy("region_code")
    .agg(
        {"total_demand_kwh": "max", "active_meters": "max"}
    )
    .toPandas())
print(peak_demand.to_string(index=False))

# Example: Vendor identifies assets needing attention
print("\n  Analysis 2: Assets needing maintenance")
maintenance_needed = na_df.filter("needs_maintenance = true").count()
total_assets = na_df.count()
print(f"      {maintenance_needed}/{total_assets} assets need maintenance "
      f"({round(maintenance_needed/total_assets*100,1)}%)")

# ============================================================
# BI-DIRECTIONAL: Vendor sends data back
# ============================================================
print("\n--- BI-DIRECTIONAL SHARING (Vendor → SPENW) ---")
print("  Vendor creates response data...")

vendor_response = spark.createDataFrame([
    ("FC-000001", "2026-01-15", 1250.5, 0.23, "INCREASE_CAPACITY", "VendorModel-v2"),
    ("FC-000002", "2026-01-15", 980.3,  0.15, "STABLE",            "VendorModel-v2"),
    ("FC-000003", "2026-01-15", 1560.8, 0.67, "HIGH_RISK",         "VendorModel-v2"),
    ("FC-000004", "2026-01-16", 1100.0, 0.31, "MONITOR",           "VendorModel-v2"),
    ("FC-000005", "2026-01-16", 890.2,  0.12, "STABLE",            "VendorModel-v2"),
], ["forecast_id", "output_date", "adjusted_demand_mw",
    "risk_score", "recommendation", "model_name"])

vendor_response.write.format("delta").mode("overwrite").save(
    "C:/Projects/databricks-poc/data/gold/vendor_forecast_output")

print(f"  Vendor shared: {vendor_response.count()} forecast responses")
vendor_response.show(truncate=False)

print("\n" + "=" * 60)
print("  DELTA SHARING SIMULATION COMPLETE")
print("=" * 60)
print("  In production (Part 2 - Azure):")
print("    - Replace local reads with delta_sharing.load_as_pandas()")
print("    - Use Databricks recipient tokens for authentication")
print("    - Vendor gets a profile.json with bearer token")
print("=" * 60)

spark.stop()
```

### 13.3 Option B: Delta Sharing OSS Server (Advanced)

For a more realistic simulation, you can run the open-source Delta Sharing server locally:

```powershell
# Download the Delta Sharing server
# Go to: github.com/delta-io/delta-sharing/releases
# Download: delta-sharing-server-x.x.x.zip

# Extract and create config
```

Create `delta_sharing/server_config.yaml`:

```yaml
# Delta Sharing Server Configuration (Local)
version: 1
shares:
  - name: "vendor_data_share"
    schemas:
      - name: "gold"
        tables:
          - name: "daily_meter_summary"
            location: "C:/Projects/databricks-poc/data/gold/daily_meter_summary"
          - name: "regional_demand"
            location: "C:/Projects/databricks-poc/data/gold/regional_demand"
          - name: "network_assets"
            location: "C:/Projects/databricks-poc/data/gold/network_assets"
          - name: "forecast_summary"
            location: "C:/Projects/databricks-poc/data/gold/forecast_summary"

# Server settings
host: "localhost"
port: 8080
endpoint: "/delta-sharing"

authorization:
  bearerToken: "poc-local-token-12345"
```

```powershell
# Start the server (requires Java)
java -jar delta-sharing-server-x.x.x.jar --config delta_sharing/server_config.yaml
```

Create `delta_sharing/recipient_profile.json`:

```json
{
    "shareCredentialsVersion": 1,
    "endpoint": "http://localhost:8080/delta-sharing",
    "bearerToken": "poc-local-token-12345"
}
```

Test with the delta-sharing Python client:

```python
import delta_sharing

profile = "delta_sharing/recipient_profile.json"

# List shares
client = delta_sharing.SharingClient(profile)
print("Shares:", client.list_shares())
print("Tables:", client.list_all_tables())

# Read a table
df = delta_sharing.load_as_pandas(
    f"{profile}#vendor_data_share.gold.daily_meter_summary")
print(df.head())
```

---

## 14. Databricks Community Edition (FREE Cloud)

### 14.1 Why Use Community Edition?

| Feature | Local PySpark | Community Edition |
|---------|--------------|-------------------|
| Cost | $0 | $0 |
| Databricks UI | No | Yes |
| Notebook collaboration | No | Yes |
| Built-in visualisations | No (need Jupyter) | Yes |
| Cluster management | N/A | Yes (learn the UI) |
| Delta Sharing | OSS only | No (needs Premium) |
| Unity Catalog | No | No (needs Premium) |

**Use Community Edition to:** Learn the Databricks UI, notebook workflows, and `display()` function — skills you'll need for Part 2 (Azure).

### 14.2 Getting Started

1. Go to **community.cloud.databricks.com**
2. Sign up with email (no credit card needed)
3. Create a cluster (auto-assigned, ~15 GB RAM)
4. Import your notebooks

### 14.3 Porting Your Code

The only changes needed:

```python
# LOCAL VERSION:
# from config.spark_config import get_spark_session
# spark = get_spark_session("MyApp")
# df.show()

# DATABRICKS VERSION:
# spark is already available (remove SparkSession creation)
# Use display(df) instead of df.show() for better formatting
# Use dbfs:/ paths instead of C:/ paths
```

### 14.4 Upload Your Data to DBFS

In a Databricks notebook:

```python
# Upload local data files to DBFS
# Option 1: Use the Databricks UI (Data → Upload File)
# Option 2: Use the Databricks CLI
# databricks fs cp -r data/raw/ dbfs:/poc/raw/
```

---

## 15. Data Exploration & Visualisation

### 15.1 Jupyter Notebook for Exploration

Create `notebooks/06_explore_data.ipynb` (or use `jupyter notebook`):

```powershell
cd C:\Projects\databricks-poc
.\venv\Scripts\Activate.ps1
jupyter notebook
```

Sample cells for exploration:

```python
# Cell 1: Setup
import sys
sys.path.insert(0, '..')
from config.spark_config import get_spark_session
from config.pipeline_config import get_path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

spark = get_spark_session("Exploration")
%matplotlib inline
plt.style.use('seaborn-v0_8')
```

```python
# Cell 2: Daily consumption pattern
dm = spark.read.format("delta").load(get_path("gold_daily_meter")).toPandas()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribution of daily consumption
axes[0].hist(dm['total_kwh'], bins=50, color='steelblue', edgecolor='black')
axes[0].set_title('Distribution of Daily Meter Consumption')
axes[0].set_xlabel('Total kWh')
axes[0].set_ylabel('Count')

# Peak vs off-peak by region
region_summary = dm.groupby('region_code').agg({
    'peak_hours_kwh': 'mean',
    'offpeak_hours_kwh': 'mean'
}).reset_index()

x = range(len(region_summary))
width = 0.35
axes[1].bar([i - width/2 for i in x], region_summary['peak_hours_kwh'],
            width, label='Peak', color='coral')
axes[1].bar([i + width/2 for i in x], region_summary['offpeak_hours_kwh'],
            width, label='Off-Peak', color='steelblue')
axes[1].set_xticks(x)
axes[1].set_xticklabels(region_summary['region_code'])
axes[1].set_title('Avg Peak vs Off-Peak Consumption by Region')
axes[1].set_ylabel('kWh')
axes[1].legend()

plt.tight_layout()
plt.savefig('data/consumption_analysis.png', dpi=150)
plt.show()
```

```python
# Cell 3: Hourly demand heatmap
rd = spark.read.format("delta").load(get_path("gold_regional_demand")).toPandas()

pivot = rd.pivot_table(
    values='total_demand_kwh',
    index='region_code',
    columns='reading_hour',
    aggfunc='mean'
)

plt.figure(figsize=(16, 4))
sns.heatmap(pivot, cmap='YlOrRd', annot=False, fmt='.0f')
plt.title('Average Hourly Demand by Region (kWh)')
plt.xlabel('Hour of Day')
plt.ylabel('Region')
plt.tight_layout()
plt.savefig('data/demand_heatmap.png', dpi=150)
plt.show()
```

```python
# Cell 4: Asset health overview
na = spark.read.format("delta").load(get_path("gold_network_assets")).toPandas()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Status breakdown
status_counts = na['status'].value_counts()
axes[0].pie(status_counts.values, labels=status_counts.index,
            autopct='%1.1f%%', startangle=90)
axes[0].set_title('Asset Status Distribution')

# Maintenance age distribution
axes[1].hist(na['days_since_maintenance'].dropna(), bins=30,
             color='steelblue', edgecolor='black')
axes[1].axvline(x=180, color='red', linestyle='--', label='180-day threshold')
axes[1].set_title('Days Since Last Maintenance')
axes[1].set_xlabel('Days')
axes[1].set_ylabel('Count')
axes[1].legend()

plt.tight_layout()
plt.savefig('data/asset_health.png', dpi=150)
plt.show()
```

---

## 16. Performance Tuning on Local Machine

### 16.1 Spark Memory Configuration (24 GB RAM)

```
Your 24 GB RAM allocation:
  ├── OS + Apps:        8 GB
  ├── Spark Driver:    12 GB  (set in spark_config.py)
  ├── Python/Pandas:    2 GB
  └── Buffer:           2 GB
```

### 16.2 Performance Tips

| Tip | What to Do | Why |
|-----|-----------|-----|
| **Partitioning** | Use 8 shuffle partitions (not default 200) | Fewer tasks for small data |
| **Adaptive Query** | Enabled in spark_config.py | Auto-optimises at runtime |
| **Caching** | `df.cache()` if reusing a DataFrame | Avoids re-reading from disk |
| **SSD advantage** | Your SSD handles Delta reads/writes fast | No tuning needed |
| **Snappy compression** | Enabled by default | Good speed/size balance |

### 16.3 Monitor Spark Performance

Access the **Spark UI** during execution:

1. While a Spark job is running, open browser to: `http://localhost:4040`
2. Explore tabs: **Jobs**, **Stages**, **Storage**, **SQL**
3. Look for skewed stages or excessive shuffles

---

## 17. Troubleshooting Guide

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Java not found** | `Error: Could not find or load main class` | Set `JAVA_HOME` correctly, restart PowerShell |
| **winutils error** | `Could not locate executable null\bin\winutils.exe` | Download winutils.exe to `C:\hadoop\bin\`, set `HADOOP_HOME` |
| **Spark won't start** | `Exception in thread "main" java.lang.NoClassDefFoundError` | Ensure `JAVA_HOME` points to JDK 11 (not JRE) |
| **Delta import error** | `ModuleNotFoundError: No module named 'delta'` | Run `pip install delta-spark==3.1.0` in venv |
| **Permission denied** | `Access is denied` on temp files | Run `winutils.exe chmod 777 C:\tmp` |
| **Out of memory** | `java.lang.OutOfMemoryError: Java heap space` | Reduce data volume in pipeline_config.py |
| **Slow execution** | Pipeline takes >10 minutes | Reduce num_meters/num_assets in DATA_CONFIG |
| **Port 4040 in use** | Spark UI won't open | Previous Spark session still running; restart Python |
| **venv activation fails** | `execution of scripts is disabled on this system` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| **Parquet read error** | `Unable to infer schema` | Data directory is empty; run 01_generate_data.py first |

---

## 18. What You Will Learn

After completing Part 1, you will have hands-on experience with:

| Skill | Where You Learned It | Industry Relevance |
|-------|---------------------|-------------------|
| PySpark DataFrame API | All notebooks | Core data engineering |
| Delta Lake (ACID, time travel) | Bronze/Silver/Gold layers | Modern lakehouse |
| Medallion Architecture | Pipeline design | Industry standard pattern |
| Data quality validation | 05_validate.py | Production pipeline essential |
| Pipeline orchestration | run_pipeline.py | Workflow management |
| Delta Sharing protocol | Simulation script | Secure data exchange |
| Spark performance tuning | spark_config.py | Interview topic |
| Data visualisation | Jupyter notebook | Stakeholder communication |

---

## 19. Preparing for Part 2 (Azure)

Before starting Part 2, make sure you have:

### Checklist

- [ ] All 5 pipeline scripts run successfully
- [ ] 05_validate.py shows all checks PASS
- [ ] Delta Sharing simulation works
- [ ] You understand the Medallion architecture
- [ ] You've explored data in Jupyter
- [ ] (Optional) You've used Databricks Community Edition
- [ ] Azure Pay-As-You-Go subscription is ready
- [ ] You've set a budget alert in Azure

### What Changes in Part 2

| Component | Part 1 (Local) | Part 2 (Azure) |
|-----------|----------------|-----------------|
| Spark engine | Local PySpark | Azure Databricks cluster |
| Storage | Local SSD (C:\) | ADLS Gen2 |
| Paths | `C:/Projects/...` | `/mnt/raw-data/...` |
| Catalog | N/A | Unity Catalog |
| Delta Sharing | Simulated locally | Databricks-managed (real) |
| Orchestration | run_pipeline.py | Databricks Workflows |
| Config change | `MODE = "local"` | `MODE = "azure"` |

> **Your code stays 95% the same** — only paths and Spark session creation change. This is the beauty of building locally first.
