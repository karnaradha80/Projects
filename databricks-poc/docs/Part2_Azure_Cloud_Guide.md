# Part 2: Azure Cloud Guide
# Azure Databricks Data Sharing Platform – Complete Azure Deployment

| Field            | Value                                              |
|------------------|----------------------------------------------------|
| Version          | 1.0                                                |
| Date             | 2026-03-16                                         |
| Based On         | SoW – Azure Databricks SME Data Sharing Platform   |
| Prerequisite     | **Part 1 (Local Development) must be completed**   |
| Budget           | Azure Pay-As-You-Go, max ~$25/month                |
| Approach         | Premium Trial (14 days FREE) → Standard tier        |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites Checklist](#2-prerequisites-checklist)
3. [Azure Cost Strategy](#3-azure-cost-strategy)
4. [Phase 1 – Azure Foundation Setup](#4-phase-1--azure-foundation-setup)
5. [Phase 2 – Databricks Workspace Deployment](#5-phase-2--databricks-workspace-deployment)
6. [Phase 3 – Storage Configuration (ADLS Gen2)](#6-phase-3--storage-configuration-adls-gen2)
7. [Phase 4 – Cluster & Compute Setup](#7-phase-4--cluster--compute-setup)
8. [Phase 5 – Unity Catalog Setup](#8-phase-5--unity-catalog-setup)
9. [Phase 6 – Migrate Local Pipelines to Azure](#9-phase-6--migrate-local-pipelines-to-azure)
10. [Phase 7 – Data Pipeline Execution](#10-phase-7--data-pipeline-execution)
11. [Phase 8 – Delta Sharing (Real Implementation)](#11-phase-8--delta-sharing-real-implementation)
12. [Phase 9 – Databricks Workflows (Orchestration)](#12-phase-9--databricks-workflows-orchestration)
13. [Phase 10 – Monitoring, Alerts & Cost Control](#13-phase-10--monitoring-alerts--cost-control)
14. [Phase 11 – Performance Tuning on Azure](#14-phase-11--performance-tuning-on-azure)
15. [Phase 12 – Downgrade & Ongoing Operations](#15-phase-12--downgrade--ongoing-operations)
16. [Cleanup & Teardown](#16-cleanup--teardown)
17. [Architecture Diagrams (Final)](#17-architecture-diagrams-final)
18. [Troubleshooting Guide](#18-troubleshooting-guide)
19. [Production Readiness Checklist](#19-production-readiness-checklist)
20. [What You Have Learned](#20-what-you-have-learned)

---

## 1. Executive Summary

This document is **Part 2** of the Data Sharing Platform POC. It deploys everything you built locally (Part 1) onto Azure cloud, adds the features that require cloud infrastructure (Unity Catalog, Delta Sharing, ADLS Gen2), and teaches you cost management on a $25/month budget.

### The Strategy: Two-Stage Azure Deployment

```
STAGE A: Premium Trial (14 days FREE)          STAGE B: Standard Tier ($5-10/month)
┌──────────────────────────────────────┐       ┌──────────────────────────────────┐
│ Days 1-14: FREE Premium Features     │       │ Day 15+: Pay-per-use Standard    │
│                                      │       │                                  │
│ • Deploy workspace (Premium)         │  ──▶  │ • Downgrade to Standard tier     │
│ • Configure Unity Catalog            │       │ • Continue pipeline development   │
│ • Set up Delta Sharing               │       │ • Run 2-3 sessions/week          │
│ • Create shares & recipients         │       │ • Auto-terminate cluster (10 min)│
│ • Full end-to-end demo               │       │ • Budget: $5-10/month            │
│ • Cost: $0 (compute) + ~$1 (storage) │       │                                  │
└──────────────────────────────────────┘       └──────────────────────────────────┘
```

### Cost Projection

| Period | What | Cost |
|--------|------|------|
| Days 1-14 | Premium trial + ADLS storage | ~$1 |
| Days 15-30 | Standard tier, ~15 hrs compute | ~$5-8 |
| Month 2+ | Standard tier, 2-3 sessions/week | ~$5-8/month |
| **Monthly average** | | **$5-8/month** |

---

## 2. Prerequisites Checklist

Before starting Part 2, verify:

### From Part 1 (Local)

- [ ] All 5 pipeline scripts run and pass validation
- [ ] You understand Medallion architecture (Bronze → Silver → Gold)
- [ ] Delta Sharing simulation completed
- [ ] You're comfortable with PySpark DataFrame operations

### Azure Requirements

- [ ] Azure Pay-As-You-Go subscription (active, verified)
- [ ] Azure CLI installed on your Windows machine
- [ ] A valid email for budget alerts
- [ ] Browser access to Azure Portal

### Install Azure CLI (if not already installed)

```powershell
# Option 1: Via winget (Windows Package Manager)
winget install Microsoft.AzureCLI

# Option 2: Download MSI from Microsoft
# Search "Install Azure CLI on Windows" on Microsoft docs

# Verify
az --version
```

### Install Databricks CLI

```powershell
# Activate your virtual environment from Part 1
cd C:\Projects\databricks-poc
.\venv\Scripts\Activate.ps1

# Install Databricks CLI
pip install databricks-cli

# Verify
databricks --version
```

---

## 3. Azure Cost Strategy

### 3.1 Complete Cost Breakdown

| Resource | Tier/Config | Monthly Cost | Notes |
|----------|-------------|-------------|-------|
| **Resource Group** | N/A | $0 | Just a container |
| **Databricks Workspace** | Standard (after trial) | $0 | No charge for workspace itself |
| **Databricks Compute** | Standard_E2s_v3, single-node | $3-6 | ~15 hrs/month × ($0.15 VM + $0.07 DBU) |
| **ADLS Gen2 Storage** | Standard LRS, <5 GB | $0.50 | $0.0208/GB/month |
| **Networking** | Default (no VNET injection) | $0.50-1 | Egress charges |
| **Azure Functions** | Consumption plan, free tier | $0 | Optional: for triggering pipelines |
| **Key Vault** | Standard, <10 secrets | $0.03 | For storing access keys |
| **Azure Monitor** | Basic (free tier) | $0 | Budget alerts |
| **Total** | | **$4-8/month** |

### 3.2 Budget Rules (Non-Negotiable)

| Rule | Why | How |
|------|-----|-----|
| **Auto-terminate = 10 min** | Biggest cost saver | Cluster config |
| **Single-node only** | No worker cost | Cluster config |
| **Standard_E2s_v3 VM** | Cheapest with enough memory | Cluster config |
| **Terminate after every session** | Don't rely on auto-terminate alone | Manual habit |
| **Budget alert at $15** | Early warning with $10 buffer | Azure Cost Management |
| **Delete RG if idle >1 week** | $0 when nothing exists | Manual |
| **Use Community Edition for experiments** | Free | Use local or Community for learning |

### 3.3 Cost per Session

```
Cluster start-up:     ~2-3 minutes (no charge during startup)
Active session:        30-90 minutes typical
Auto-terminate:        10 minutes after last command

Cost per session:
  VM:  0.5-1.5 hrs × $0.15/hr = $0.08 - $0.23
  DBU: 0.5-1.5 hrs × $0.07/hr = $0.04 - $0.11
  Total per session:              $0.12 - $0.34

Sessions per month: 15-20
Monthly compute: $2 - $7
```

---

## 4. Phase 1 – Azure Foundation Setup

### 4.1 Login to Azure

```powershell
# Login (opens browser for authentication)
az login

# List subscriptions
az account list --output table

# Set the correct subscription
az account set --subscription "<your-subscription-id>"

# Verify
az account show --query "{Name:name, ID:id, State:state}" --output table
```

### 4.2 Register Required Resource Providers

```powershell
# These providers must be registered for Databricks to work
az provider register --namespace Microsoft.Databricks
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.ManagedIdentity

# Check registration status (should say "Registered")
az provider show --namespace Microsoft.Databricks --query "registrationState"
az provider show --namespace Microsoft.Storage --query "registrationState"
```

### 4.3 Choose a Region

Pick the cheapest region closest to you:

| Region | Location | VM Cost (E2s_v3) | Recommendation |
|--------|----------|-------------------|----------------|
| UK South | London | $0.146/hr | Best if you're in UK |
| West Europe | Netherlands | $0.146/hr | Good for EU |
| East US | Virginia | $0.134/hr | Cheapest overall |
| Central India | Pune | $0.121/hr | Cheapest if latency is OK |

> **Recommendation:** Use **UK South** for lowest latency (matching the SoW's Utilitics context), or **East US** for lowest price.

### 4.4 Create Resource Group

```powershell
# Choose your region (change uksouth if needed)
$REGION = "uksouth"
$RG_NAME = "rg-databricks-poc"

az group create `
  --name $RG_NAME `
  --location $REGION `
  --tags Environment=POC Project=DataSharing Budget=25USD Owner=Personal

# Verify
az group show --name $RG_NAME --query "{Name:name, Location:location}" --output table
```

### 4.5 Set Up Budget Alert (DO THIS FIRST!)

```powershell
# Create budget with email alerts
# Replace <your-email> with your actual email

az consumption budget create `
  --budget-name "POC-Monthly-25" `
  --amount 25 `
  --category Cost `
  --time-grain Monthly `
  --start-date "2026-03-01" `
  --end-date "2026-12-31" `
  --resource-group $RG_NAME

# You can also set this up in the Azure Portal:
# Azure Portal → Cost Management → Budgets → + Add
#   Amount: $25
#   Alerts at: 60% ($15), 80% ($20), 100% ($25)
#   Notification email: <your-email>
```

---

## 5. Phase 2 – Databricks Workspace Deployment

### 5.1 Deploy Workspace (Premium Tier – 14-Day Free Trial)

```powershell
$WORKSPACE_NAME = "dbw-poc-datasharing"

# Deploy with Premium SKU (14-day free trial for Delta Sharing & Unity Catalog)
az databricks workspace create `
  --resource-group $RG_NAME `
  --name $WORKSPACE_NAME `
  --location $REGION `
  --sku premium `
  --tags Environment=POC

# This takes 3-5 minutes...

# Get workspace URL
$WORKSPACE_URL = az databricks workspace show `
  --resource-group $RG_NAME `
  --name $WORKSPACE_NAME `
  --query "workspaceUrl" -o tsv

echo "Workspace URL: https://$WORKSPACE_URL"
```

> **Save this URL!** You'll use it to access the Databricks UI. It looks like: `adb-1234567890123456.7.azuredatabricks.net`

### 5.2 First Login to Databricks UI

1. Open browser → go to `https://<your-workspace-url>`
2. Sign in with your Azure AD credentials
3. You'll see the Databricks workspace home page

### 5.3 Generate Personal Access Token (PAT)

1. In Databricks UI → click your **username** (top-right) → **User Settings**
2. Go to **Developer** → **Access Tokens**
3. Click **Generate New Token**
   - Comment: `poc-cli-token`
   - Lifetime: `90 days`
4. **Copy the token immediately** (it won't be shown again!)

### 5.4 Configure Databricks CLI

```powershell
# Configure with the PAT
databricks configure --token

# Enter:
#   Databricks Host: https://<your-workspace-url>
#   Token: <paste-your-token>

# Verify connection
databricks workspace list /
```

---

## 6. Phase 3 – Storage Configuration (ADLS Gen2)

### 6.1 Create Storage Account

```powershell
# Create a unique storage account name (lowercase, 3-24 chars, no special chars)
$STORAGE_NAME = "stpocadls$(Get-Random -Minimum 1000 -Maximum 9999)"
echo "Storage account name: $STORAGE_NAME"

# Create ADLS Gen2 storage account
az storage account create `
  --name $STORAGE_NAME `
  --resource-group $RG_NAME `
  --location $REGION `
  --sku Standard_LRS `
  --kind StorageV2 `
  --hns true `
  --tags Environment=POC

# Get the storage account key
$STORAGE_KEY = az storage account keys list `
  --resource-group $RG_NAME `
  --account-name $STORAGE_NAME `
  --query "[0].value" -o tsv

echo "Storage key (save this): $STORAGE_KEY"
```

### 6.2 Create Containers and Directories

```powershell
# Create containers
az storage fs create --name raw-data --account-name $STORAGE_NAME --auth-mode key --account-key $STORAGE_KEY
az storage fs create --name processed-data --account-name $STORAGE_NAME --auth-mode key --account-key $STORAGE_KEY

# Create directory structure in raw-data container
foreach ($dir in "timeseries", "snapshot", "files") {
    az storage fs directory create `
      --name $dir `
      --file-system raw-data `
      --account-name $STORAGE_NAME `
      --auth-mode key `
      --account-key $STORAGE_KEY
}

# Create directory structure in processed-data container
foreach ($layer in "bronze", "silver", "gold") {
    az storage fs directory create `
      --name $layer `
      --file-system processed-data `
      --account-name $STORAGE_NAME `
      --auth-mode key `
      --account-key $STORAGE_KEY
}

# Verify
az storage fs directory list --file-system raw-data --account-name $STORAGE_NAME --auth-mode key --account-key $STORAGE_KEY --output table
az storage fs directory list --file-system processed-data --account-name $STORAGE_NAME --auth-mode key --account-key $STORAGE_KEY --output table
```

### 6.3 Upload Local Data to ADLS Gen2 (Optional)

If you generated data in Part 1 and want to upload it:

```powershell
# Upload raw data from Part 1 to ADLS
# Time Series
az storage fs directory upload `
  --file-system raw-data `
  --account-name $STORAGE_NAME `
  --source "C:\Projects\databricks-poc\data\raw\timeseries" `
  --destination-path timeseries `
  --recursive `
  --auth-mode key `
  --account-key $STORAGE_KEY

# Snapshot
az storage fs directory upload `
  --file-system raw-data `
  --account-name $STORAGE_NAME `
  --source "C:\Projects\databricks-poc\data\raw\snapshot" `
  --destination-path snapshot `
  --recursive `
  --auth-mode key `
  --account-key $STORAGE_KEY

# File Data
az storage fs directory upload `
  --file-system raw-data `
  --account-name $STORAGE_NAME `
  --source "C:\Projects\databricks-poc\data\raw\files" `
  --destination-path files `
  --recursive `
  --auth-mode key `
  --account-key $STORAGE_KEY
```

### 6.4 Create Secret Scope in Databricks

```powershell
# Create a Databricks-backed secret scope
databricks secrets create-scope --scope poc-secrets

# Store the storage account key
# This opens an editor — paste the storage key and save
databricks secrets put --scope poc-secrets --key storage-account-key

# Store the storage account name
databricks secrets put --scope poc-secrets --key storage-account-name

# Verify
databricks secrets list --scope poc-secrets
```

### 6.5 Mount ADLS Gen2 in Databricks

Create a notebook in Databricks: **`/POC/00_setup/mount_storage`**

```python
# ============================================================
# Notebook: mount_storage
# Purpose: Mount ADLS Gen2 containers to Databricks filesystem
# Run ONCE after workspace creation
# ============================================================

# Retrieve secrets
storage_account = dbutils.secrets.get(scope="poc-secrets", key="storage-account-name")
storage_key = dbutils.secrets.get(scope="poc-secrets", key="storage-account-key")

# Configuration
mount_config = {
    f"fs.azure.account.key.{storage_account}.blob.core.windows.net": storage_key
}

# Mount raw-data container
try:
    dbutils.fs.mount(
        source=f"wasbs://raw-data@{storage_account}.blob.core.windows.net",
        mount_point="/mnt/raw-data",
        extra_configs=mount_config
    )
    print("Mounted: /mnt/raw-data")
except Exception as e:
    if "already mounted" in str(e):
        print("/mnt/raw-data already mounted")
    else:
        raise e

# Mount processed-data container
try:
    dbutils.fs.mount(
        source=f"wasbs://processed-data@{storage_account}.blob.core.windows.net",
        mount_point="/mnt/processed-data",
        extra_configs=mount_config
    )
    print("Mounted: /mnt/processed-data")
except Exception as e:
    if "already mounted" in str(e):
        print("/mnt/processed-data already mounted")
    else:
        raise e

# Verify mounts
print("\nAll mounts:")
for mount in dbutils.fs.mounts():
    if "raw-data" in mount.mountPoint or "processed-data" in mount.mountPoint:
        print(f"  {mount.mountPoint} → {mount.source}")

# Test: List files in raw-data
print("\nFiles in /mnt/raw-data:")
for f in dbutils.fs.ls("/mnt/raw-data"):
    print(f"  {f.name}")
```

---

## 7. Phase 4 – Cluster & Compute Setup

### 7.1 Create Cost-Optimised Cluster

In Databricks UI → **Compute** → **Create Cluster**:

| Setting | Value | Why |
|---------|-------|-----|
| **Cluster Name** | `poc-single-node` | Descriptive name |
| **Cluster Mode** | Single Node | No worker cost |
| **Access Mode** | Single User | Your user only |
| **Databricks Runtime** | 14.3 LTS | Latest stable LTS |
| **Node Type** | Standard_E2s_v3 | 2 vCPU, 16 GB RAM — cheapest with enough memory |
| **Auto Termination** | 10 minutes | Critical for cost control |
| **Photon** | Disabled | Adds cost, not needed for POC |

### 7.2 Advanced Settings (Spark Config)

In the cluster creation form, expand **Advanced Options** → **Spark** tab:

```
spark.databricks.cluster.profile singleNode
spark.master local[*]
spark.sql.adaptive.enabled true
spark.sql.adaptive.coalescePartitions.enabled true
spark.sql.shuffle.partitions 8
spark.databricks.delta.optimizeWrite.enabled true
spark.databricks.delta.autoCompact.enabled true
```

### 7.3 Cluster via API (Alternative)

```powershell
# Create cluster via Databricks CLI
databricks clusters create --json '{
  "cluster_name": "poc-single-node",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "Standard_E2s_v3",
  "num_workers": 0,
  "autotermination_minutes": 10,
  "spark_conf": {
    "spark.databricks.cluster.profile": "singleNode",
    "spark.master": "local[*]",
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.shuffle.partitions": "8"
  },
  "custom_tags": {
    "ResourceClass": "SingleNode",
    "Project": "DataSharingPOC"
  }
}'
```

### 7.4 Cluster Management Best Practices

```
BEFORE each session:
  1. Databricks UI → Compute → Start cluster
  2. Wait 2-3 minutes for cluster to start
  3. Run your notebooks

AFTER each session:
  1. Databricks UI → Compute → Terminate cluster
  2. OR let auto-terminate after 10 min idle
  3. Verify cluster shows "Terminated" state

WEEKLY:
  - Check Azure Cost Management → filter by resource group
  - Verify spend is on track (<$2/week)
```

---

## 8. Phase 5 – Unity Catalog Setup

> **Note:** Unity Catalog requires **Premium tier**. Complete this during your 14-day trial.

### 8.1 Enable Unity Catalog

1. Databricks UI → **Admin Console** (gear icon, top-right)
2. Go to **Unity Catalog** tab
3. If no metastore exists, create one:
   - Name: `poc-metastore`
   - Region: `uksouth` (same as workspace)
   - ADLS Gen2 path: `abfss://processed-data@<storage-account>.dfs.core.windows.net/unity-catalog`
4. Assign metastore to workspace

### 8.2 Create Catalog and Schemas

Create notebook: **`/POC/00_setup/create_catalog`**

```sql
-- ============================================================
-- Notebook: create_catalog
-- Purpose: Set up Unity Catalog structure
-- Run ONCE after Unity Catalog is enabled
-- ============================================================

-- Create the main catalog for this POC
CREATE CATALOG IF NOT EXISTS data_sharing_poc
  COMMENT 'Data Sharing Platform POC - matches SoW deliverables';

USE CATALOG data_sharing_poc;

-- Create schemas matching the Medallion architecture
CREATE SCHEMA IF NOT EXISTS bronze
  COMMENT 'Raw ingestion layer - no transformations, append-only';

CREATE SCHEMA IF NOT EXISTS silver
  COMMENT 'Cleaned and validated data - deduped, standardised';

CREATE SCHEMA IF NOT EXISTS gold
  COMMENT 'Business-ready aggregated data - shared via Delta Sharing';

-- Verify
SHOW SCHEMAS IN data_sharing_poc;
```

### 8.3 Create Managed Tables (Register Pipeline Output)

After running the pipeline (Phase 7), register Delta tables in Unity Catalog:

```sql
-- ============================================================
-- Register Bronze tables
-- ============================================================
CREATE TABLE IF NOT EXISTS data_sharing_poc.bronze.timeseries
  USING DELTA
  LOCATION '/mnt/processed-data/bronze/timeseries'
  COMMENT 'Raw smart meter readings - 30 min intervals';

CREATE TABLE IF NOT EXISTS data_sharing_poc.bronze.snapshot
  USING DELTA
  LOCATION '/mnt/processed-data/bronze/snapshot'
  COMMENT 'Raw network asset snapshots - daily';

CREATE TABLE IF NOT EXISTS data_sharing_poc.bronze.file_data
  USING DELTA
  LOCATION '/mnt/processed-data/bronze/files'
  COMMENT 'Raw ERM demand forecast files';

-- ============================================================
-- Register Silver tables
-- ============================================================
CREATE TABLE IF NOT EXISTS data_sharing_poc.silver.timeseries
  USING DELTA
  LOCATION '/mnt/processed-data/silver/timeseries'
  COMMENT 'Cleaned meter readings - deduped, validated, enriched';

CREATE TABLE IF NOT EXISTS data_sharing_poc.silver.snapshot
  USING DELTA
  LOCATION '/mnt/processed-data/silver/snapshot'
  COMMENT 'Cleaned asset snapshots - latest per asset/day';

CREATE TABLE IF NOT EXISTS data_sharing_poc.silver.file_data
  USING DELTA
  LOCATION '/mnt/processed-data/silver/files'
  COMMENT 'Validated forecasts - confidence intervals checked';

-- ============================================================
-- Register Gold tables (these will be shared via Delta Sharing)
-- ============================================================
CREATE TABLE IF NOT EXISTS data_sharing_poc.gold.daily_meter_summary
  USING DELTA
  LOCATION '/mnt/processed-data/gold/daily_meter_summary'
  COMMENT 'Daily consumption per meter - shared with vendor';

CREATE TABLE IF NOT EXISTS data_sharing_poc.gold.regional_demand
  USING DELTA
  LOCATION '/mnt/processed-data/gold/regional_demand'
  COMMENT 'Hourly regional demand totals - shared with vendor';

CREATE TABLE IF NOT EXISTS data_sharing_poc.gold.network_assets
  USING DELTA
  LOCATION '/mnt/processed-data/gold/network_assets'
  COMMENT 'Latest asset status and location - shared with vendor';

CREATE TABLE IF NOT EXISTS data_sharing_poc.gold.forecast_summary
  USING DELTA
  LOCATION '/mnt/processed-data/gold/forecast_summary'
  COMMENT 'Aggregated demand forecasts - shared with vendor';

-- ============================================================
-- Verify all tables
-- ============================================================
SHOW TABLES IN data_sharing_poc.bronze;
SHOW TABLES IN data_sharing_poc.silver;
SHOW TABLES IN data_sharing_poc.gold;
```

---

## 9. Phase 6 – Migrate Local Pipelines to Azure

### 9.1 What Changes (Very Little!)

Your Part 1 code needs only 3 changes to run on Azure Databricks:

| Change | Part 1 (Local) | Part 2 (Azure) |
|--------|----------------|-----------------|
| **SparkSession** | Created manually | Already available as `spark` |
| **Paths** | `C:/Projects/databricks-poc/data/...` | `/mnt/raw-data/...` and `/mnt/processed-data/...` |
| **Config import** | `from config.spark_config import...` | Use `%run` magic command |

### 9.2 Create Azure Configuration Notebook

Create notebook: **`/POC/config/paths`**

```python
# ============================================================
# Notebook: /POC/config/paths
# Purpose: Centralised path configuration for Azure
# Usage: %run /POC/config/paths (at top of every notebook)
# ============================================================

# Raw data paths (ADLS Gen2 → mounted)
RAW_TIMESERIES = "/mnt/raw-data/timeseries"
RAW_SNAPSHOT = "/mnt/raw-data/snapshot"
RAW_FILES = "/mnt/raw-data/files"

# Bronze layer
BRONZE_TIMESERIES = "/mnt/processed-data/bronze/timeseries"
BRONZE_SNAPSHOT = "/mnt/processed-data/bronze/snapshot"
BRONZE_FILES = "/mnt/processed-data/bronze/files"

# Silver layer
SILVER_TIMESERIES = "/mnt/processed-data/silver/timeseries"
SILVER_SNAPSHOT = "/mnt/processed-data/silver/snapshot"
SILVER_FILES = "/mnt/processed-data/silver/files"

# Gold layer
GOLD_DAILY_METER = "/mnt/processed-data/gold/daily_meter_summary"
GOLD_REGIONAL_DEMAND = "/mnt/processed-data/gold/regional_demand"
GOLD_NETWORK_ASSETS = "/mnt/processed-data/gold/network_assets"
GOLD_FORECAST_SUMMARY = "/mnt/processed-data/gold/forecast_summary"

# Quality thresholds
MAX_DROP_RATE_PCT = 20
MIN_COMPLETENESS_PCT = 80

print("Configuration loaded. Paths available:")
print(f"  RAW_TIMESERIES:      {RAW_TIMESERIES}")
print(f"  BRONZE_TIMESERIES:   {BRONZE_TIMESERIES}")
print(f"  SILVER_TIMESERIES:   {SILVER_TIMESERIES}")
print(f"  GOLD_DAILY_METER:    {GOLD_DAILY_METER}")
```

### 9.3 Migration Example: Bronze Notebook

**Part 1 (Local) — `02_ingest_bronze.py`:**

```python
# These lines exist in Part 1:
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path
spark = get_spark_session("BronzeIngestion")
...
ts_raw = spark.read.parquet(get_path("raw_timeseries"))
```

**Part 2 (Azure) — `/POC/02_ingest_bronze`:**

```python
# Replace the imports with one line:
# %run /POC/config/paths

# spark is already available — no need to create it

# Use Azure path variables instead of get_path()
ts_raw = spark.read.parquet(RAW_TIMESERIES)
```

### 9.4 All Azure Notebooks

Create the following notebooks in Databricks. Each starts with `%run /POC/config/paths`:

#### Notebook: `/POC/01_generate_data`

```python
# %run /POC/config/paths

from pyspark.sql.types import *
import random
from datetime import datetime, timedelta

# ============================================================
# Data Generation (same logic as Part 1, Azure paths)
# ============================================================
print("Generating data for Azure POC...")

BASE_DATE = datetime(2026, 1, 1)
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

# --- TIME SERIES ---
print("[1/3] Time Series...")
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

for meter_idx in range(500):
    meter_id = f"MTR-{meter_idx:06d}"
    region = REGIONS[meter_idx % len(REGIONS)]
    m_type = meter_types[meter_idx % len(meter_types)]
    base_consumption = random.uniform(0.5, 3.0)
    for day in range(7):
        for reading in range(48):
            ts = BASE_DATE + timedelta(days=day, minutes=reading * 30)
            hour = ts.hour
            if 7 <= hour <= 9: hour_factor = 1.5
            elif 17 <= hour <= 20: hour_factor = 1.8
            elif 10 <= hour <= 16: hour_factor = 1.2
            else: hour_factor = 0.5
            value = round(base_consumption * hour_factor * random.uniform(0.8, 1.2), 4)
            quality = random.choices(quality_codes, quality_weights)[0]
            ts_rows.append((meter_id, ts, value, quality, m_type, region, "UTILITICS_METERING"))

ts_df = spark.createDataFrame(ts_rows, schema_ts)
ts_df.write.mode("overwrite").parquet(RAW_TIMESERIES)
print(f"  Time Series: {ts_df.count():,} records")

# --- SNAPSHOT ---
print("[2/3] Snapshot...")
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
snap_rows = []

for snap_day in range(7):
    snap_date = BASE_DATE.date() + timedelta(days=snap_day)
    for asset_idx in range(2000):
        snap_rows.append((
            f"AST-{asset_idx:07d}", snap_date,
            asset_types[asset_idx % len(asset_types)],
            random.choices(statuses, [0.8, 0.1, 0.07, 0.03])[0],
            round(random.uniform(10, 500), 2),
            random.choice([11.0, 33.0, 66.0, 132.0, 275.0, 400.0]),
            round(random.uniform(50.0, 58.0), 6),
            round(random.uniform(-6.0, 2.0), 6),
            f"AST-{random.randint(0, 100):07d}" if random.random() > 0.3 else None,
            BASE_DATE.date() - timedelta(days=random.randint(1, 365)),
            f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}"
        ))

snap_df = spark.createDataFrame(snap_rows, schema_snap)
snap_df.write.mode("overwrite").parquet(RAW_SNAPSHOT)
print(f"  Snapshot: {snap_df.count():,} records")

# --- FILE DATA ---
print("[3/3] File Data...")
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

for fc_idx in range(500):
    fc_id = f"FC-{fc_idx:06d}"
    fc_date = BASE_DATE.date() + timedelta(days=fc_idx % 30)
    region = REGIONS[fc_idx % len(REGIONS)]
    scenario = scenarios[fc_idx % len(scenarios)]
    base_demand = random.uniform(500, 2000)
    for hour in range(168):
        h = hour % 24
        tf = 1.4 if 7<=h<=9 else 1.6 if 17<=h<=20 else 1.1 if 10<=h<=16 else 0.6
        demand = base_demand * tf * random.uniform(0.95, 1.05)
        margin = demand * 0.05 * (1 + (hour / 168) * 0.5)
        file_rows.append((fc_id, fc_date, hour, round(demand, 2),
                         round(demand - margin, 2), round(demand + margin, 2),
                         "ERM-v3.2.1", region, scenario))

file_df = spark.createDataFrame(file_rows, schema_file)
file_df.write.mode("overwrite").parquet(RAW_FILES)
print(f"  File Data: {file_df.count():,} records")

print(f"\nTotal: {ts_df.count() + snap_df.count() + file_df.count():,} records generated")
```

#### Notebook: `/POC/02_ingest_bronze`

```python
# %run /POC/config/paths

from pyspark.sql import functions as F
from datetime import datetime

INGESTION_TS = datetime.now()

def add_metadata(df):
    return (df
        .withColumn("_ingestion_timestamp", F.lit(INGESTION_TS))
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_ingestion_date", F.to_date(F.lit(INGESTION_TS))))

# Time Series → Bronze
ts = add_metadata(spark.read.parquet(RAW_TIMESERIES))
ts.write.format("delta").mode("overwrite").partitionBy("_ingestion_date").save(BRONZE_TIMESERIES)
print(f"Bronze timeseries: {ts.count():,}")

# Snapshot → Bronze
snap = add_metadata(spark.read.parquet(RAW_SNAPSHOT))
snap.write.format("delta").mode("overwrite").partitionBy("_ingestion_date").save(BRONZE_SNAPSHOT)
print(f"Bronze snapshot: {snap.count():,}")

# File Data → Bronze
files = add_metadata(spark.read.parquet(RAW_FILES))
files.write.format("delta").mode("overwrite").partitionBy("_ingestion_date").save(BRONZE_FILES)
print(f"Bronze file_data: {files.count():,}")
```

#### Notebook: `/POC/03_transform_silver`

```python
# %run /POC/config/paths

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# --- Silver: Time Series ---
ts_b = spark.read.format("delta").load(BRONZE_TIMESERIES)
ts_s = (ts_b
    .dropDuplicates(["meter_id", "reading_timestamp"])
    .filter(F.col("reading_value_kwh").between(0, 10000))
    .withColumn("reading_quality",
        F.when(F.col("reading_quality").isNull(), "UNKNOWN")
         .otherwise(F.upper(F.trim(F.col("reading_quality")))))
    .withColumn("reading_date", F.to_date("reading_timestamp"))
    .withColumn("reading_hour", F.hour("reading_timestamp"))
    .withColumn("is_peak_hour",
        F.when(F.col("reading_hour").between(7, 19), True).otherwise(False))
    .withColumn("is_weekend",
        F.when(F.dayofweek("reading_timestamp").isin(1, 7), True).otherwise(False))
    .withColumn("_silver_timestamp", F.current_timestamp()))

ts_s.write.format("delta").mode("overwrite").partitionBy("reading_date").save(SILVER_TIMESERIES)
print(f"Silver timeseries: {ts_b.count():,} → {ts_s.count():,}")

# --- Silver: Snapshot ---
snap_b = spark.read.format("delta").load(BRONZE_SNAPSHOT)
w = Window.partitionBy("asset_id", "snapshot_date").orderBy(F.col("_ingestion_timestamp").desc())

snap_s = (snap_b
    .withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")
    .filter(F.col("location_lat").between(49.0, 61.0))
    .filter(F.col("location_lon").between(-8.0, 2.0))
    .withColumn("status", F.upper(F.trim(F.col("status"))))
    .withColumn("capacity_mw", F.when(F.col("capacity_mw").isNull(), 0.0).otherwise(F.col("capacity_mw")))
    .withColumn("days_since_maintenance", F.datediff(F.col("snapshot_date"), F.col("last_maintenance_date")))
    .withColumn("needs_maintenance", F.when(F.col("days_since_maintenance") > 180, True).otherwise(False))
    .withColumn("_silver_timestamp", F.current_timestamp()))

snap_s.write.format("delta").mode("overwrite").partitionBy("snapshot_date").save(SILVER_SNAPSHOT)
print(f"Silver snapshot: {snap_b.count():,} → {snap_s.count():,}")

# --- Silver: File Data ---
file_b = spark.read.format("delta").load(BRONZE_FILES)
file_s = (file_b
    .dropDuplicates(["forecast_id", "horizon_hours"])
    .filter(F.col("confidence_lower") <= F.col("predicted_demand_mw"))
    .filter(F.col("predicted_demand_mw") <= F.col("confidence_upper"))
    .filter(F.col("predicted_demand_mw") > 0)
    .withColumn("confidence_range_mw", F.col("confidence_upper") - F.col("confidence_lower"))
    .withColumn("confidence_pct", F.round((F.col("confidence_range_mw") / F.col("predicted_demand_mw")) * 100, 2))
    .withColumn("forecast_day", F.floor(F.col("horizon_hours") / 24).cast("int"))
    .withColumn("_silver_timestamp", F.current_timestamp()))

file_s.write.format("delta").mode("overwrite").partitionBy("forecast_date").save(SILVER_FILES)
print(f"Silver file_data: {file_b.count():,} → {file_s.count():,}")
```

#### Notebook: `/POC/04_aggregate_gold`

```python
# %run /POC/config/paths

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# --- Gold: Daily Meter Summary ---
ts = spark.read.format("delta").load(SILVER_TIMESERIES)
dm = (ts.groupBy("meter_id", "reading_date", "meter_type", "region_code")
    .agg(
        F.sum("reading_value_kwh").alias("total_kwh"),
        F.avg("reading_value_kwh").alias("avg_kwh"),
        F.max("reading_value_kwh").alias("peak_kwh"),
        F.min("reading_value_kwh").alias("min_kwh"),
        F.count("*").alias("reading_count"),
        F.sum(F.when(F.col("reading_quality") == "VALID", 1).otherwise(0)).alias("valid_readings"),
        F.sum(F.when(F.col("is_peak_hour"), F.col("reading_value_kwh")).otherwise(0)).alias("peak_hours_kwh"),
        F.sum(F.when(~F.col("is_peak_hour"), F.col("reading_value_kwh")).otherwise(0)).alias("offpeak_hours_kwh"))
    .withColumn("data_completeness_pct", F.round(F.col("reading_count") / 48 * 100, 2))
    .withColumn("_gold_timestamp", F.current_timestamp()))
dm.write.format("delta").mode("overwrite").partitionBy("reading_date").save(GOLD_DAILY_METER)
print(f"Gold daily_meter_summary: {dm.count():,}")

# --- Gold: Regional Demand ---
rd = (ts.groupBy("reading_date", "reading_hour", "region_code")
    .agg(
        F.sum("reading_value_kwh").alias("total_demand_kwh"),
        F.countDistinct("meter_id").alias("active_meters"),
        F.avg("reading_value_kwh").alias("avg_per_meter_kwh"))
    .withColumn("_gold_timestamp", F.current_timestamp()))
rd.write.format("delta").mode("overwrite").partitionBy("reading_date").save(GOLD_REGIONAL_DEMAND)
print(f"Gold regional_demand: {rd.count():,}")

# --- Gold: Network Assets ---
snap = spark.read.format("delta").load(SILVER_SNAPSHOT)
w = Window.partitionBy("asset_id").orderBy(F.col("snapshot_date").desc())
na = (snap.withColumn("_rank", F.row_number().over(w)).filter(F.col("_rank") == 1).drop("_rank")
    .select("asset_id", "asset_type", "status", "capacity_mw", "voltage_kv",
            "location_lat", "location_lon", "snapshot_date",
            "last_maintenance_date", "firmware_version", "days_since_maintenance", "needs_maintenance")
    .withColumn("_gold_timestamp", F.current_timestamp()))
na.write.format("delta").mode("overwrite").save(GOLD_NETWORK_ASSETS)
print(f"Gold network_assets: {na.count():,}")

# --- Gold: Forecast Summary ---
fc = spark.read.format("delta").load(SILVER_FILES)
fs = (fc.groupBy("forecast_date", "region", "scenario", "forecast_day")
    .agg(
        F.avg("predicted_demand_mw").alias("avg_predicted_mw"),
        F.max("predicted_demand_mw").alias("max_predicted_mw"),
        F.min("predicted_demand_mw").alias("min_predicted_mw"),
        F.avg("confidence_range_mw").alias("avg_confidence_range_mw"),
        F.count("*").alias("data_points"))
    .withColumn("_gold_timestamp", F.current_timestamp()))
fs.write.format("delta").mode("overwrite").partitionBy("forecast_date").save(GOLD_FORECAST_SUMMARY)
print(f"Gold forecast_summary: {fs.count():,}")
```

#### Notebook: `/POC/05_validate`

```python
# %run /POC/config/paths

from pyspark.sql import functions as F

checks = []

def check(name, passed):
    checks.append((name, passed))
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}")

# Record counts
print("=== Record Counts ===")
for name, b_path, s_path in [
    ("timeseries", BRONZE_TIMESERIES, SILVER_TIMESERIES),
    ("snapshot", BRONZE_SNAPSHOT, SILVER_SNAPSHOT),
    ("file_data", BRONZE_FILES, SILVER_FILES)]:
    b = spark.read.format("delta").load(b_path).count()
    s = spark.read.format("delta").load(s_path).count()
    d = round((1 - s/b) * 100, 1) if b > 0 else 0
    print(f"  {name}: {b:,} → {s:,} (dropped {d}%)")
    check(f"{name} drop rate < {MAX_DROP_RATE_PCT}%", d < MAX_DROP_RATE_PCT)

# Gold counts
print("\n=== Gold Layer ===")
for name, path in [("daily_meter", GOLD_DAILY_METER), ("regional_demand", GOLD_REGIONAL_DEMAND),
                    ("network_assets", GOLD_NETWORK_ASSETS), ("forecast_summary", GOLD_FORECAST_SUMMARY)]:
    c = spark.read.format("delta").load(path).count()
    print(f"  {name}: {c:,}")
    check(f"gold.{name} has records", c > 0)

# Quality checks
print("\n=== Quality Checks ===")
dm = spark.read.format("delta").load(GOLD_DAILY_METER)
check("No null meter_ids", dm.filter(F.col("meter_id").isNull()).count() == 0)
check("total_kwh positive", dm.filter(F.col("total_kwh") <= 0).count() == 0)
check("peak + offpeak = total",
      dm.filter(F.abs(F.col("peak_hours_kwh") + F.col("offpeak_hours_kwh") - F.col("total_kwh")) > 0.01).count() == 0)

na = spark.read.format("delta").load(GOLD_NETWORK_ASSETS)
check("Valid statuses", na.filter(~F.col("status").isin("ACTIVE","INACTIVE","MAINTENANCE","DECOMMISSIONED")).count() == 0)

fc = spark.read.format("delta").load(GOLD_FORECAST_SUMMARY)
check("Positive forecasts", fc.filter(F.col("avg_predicted_mw") <= 0).count() == 0)

# Result
passed = sum(1 for _, p in checks if p)
print(f"\n{'='*50}")
print(f"RESULT: {passed}/{len(checks)} checks passed")
print(f"STATUS: {'ALL PASS' if passed == len(checks) else 'ISSUES FOUND'}")
print(f"{'='*50}")
```

---

## 10. Phase 7 – Data Pipeline Execution

### 10.1 Run Order in Databricks

Execute notebooks in this sequence:

```
1. /POC/00_setup/mount_storage      (ONCE only)
2. /POC/00_setup/create_catalog     (ONCE only)
3. /POC/01_generate_data            (OR upload from Part 1)
4. /POC/02_ingest_bronze
5. /POC/03_transform_silver
6. /POC/04_aggregate_gold
7. /POC/05_validate
8. /POC/00_setup/create_catalog     (run SQL to register tables — after Gold is populated)
```

### 10.2 Verify Tables in Unity Catalog

```sql
-- After pipeline runs, verify all tables have data
SELECT 'bronze.timeseries' as tbl, count(*) as cnt FROM data_sharing_poc.bronze.timeseries
UNION ALL
SELECT 'bronze.snapshot', count(*) FROM data_sharing_poc.bronze.snapshot
UNION ALL
SELECT 'bronze.file_data', count(*) FROM data_sharing_poc.bronze.file_data
UNION ALL
SELECT 'silver.timeseries', count(*) FROM data_sharing_poc.silver.timeseries
UNION ALL
SELECT 'silver.snapshot', count(*) FROM data_sharing_poc.silver.snapshot
UNION ALL
SELECT 'silver.file_data', count(*) FROM data_sharing_poc.silver.file_data
UNION ALL
SELECT 'gold.daily_meter', count(*) FROM data_sharing_poc.gold.daily_meter_summary
UNION ALL
SELECT 'gold.regional_demand', count(*) FROM data_sharing_poc.gold.regional_demand
UNION ALL
SELECT 'gold.network_assets', count(*) FROM data_sharing_poc.gold.network_assets
UNION ALL
SELECT 'gold.forecast_summary', count(*) FROM data_sharing_poc.gold.forecast_summary;
```

---

## 11. Phase 8 – Delta Sharing (Real Implementation)

> **CRITICAL:** This requires Premium tier. Do this within your 14-day trial period!

### 11.1 Enable Delta Sharing

1. Databricks UI → **Admin Console** → **Workspace Settings**
2. Find **Delta Sharing** → **Enable**

### 11.2 Create a Share

```sql
-- Create a share containing Gold tables for the vendor
CREATE SHARE IF NOT EXISTS vendor_data_share
  COMMENT 'Utilitics data share for 3rd party vendor - POC';

-- Add Gold tables to the share
ALTER SHARE vendor_data_share ADD TABLE data_sharing_poc.gold.daily_meter_summary;
ALTER SHARE vendor_data_share ADD TABLE data_sharing_poc.gold.regional_demand;
ALTER SHARE vendor_data_share ADD TABLE data_sharing_poc.gold.network_assets;
ALTER SHARE vendor_data_share ADD TABLE data_sharing_poc.gold.forecast_summary;

-- Verify share contents
SHOW ALL IN SHARE vendor_data_share;
```

### 11.3 Create a Recipient (Simulated Vendor)

```sql
-- Create recipient (simulates the 3rd party vendor)
CREATE RECIPIENT IF NOT EXISTS vendor_recipient
  COMMENT 'Simulated 3rd party vendor for POC testing';

-- Grant access
GRANT SELECT ON SHARE vendor_data_share TO RECIPIENT vendor_recipient;

-- IMPORTANT: Get the activation link
-- This contains the authentication token the vendor will use
DESCRIBE RECIPIENT vendor_recipient;
```

> **Copy the activation_link from the output!** It contains a one-time-use URL with the auth token.

### 11.4 Activate and Get Credentials

1. Open the activation link in a browser
2. Download the credentials file (or copy the token)
3. Save as `vendor_profile.json`:

```json
{
    "shareCredentialsVersion": 1,
    "endpoint": "https://<your-workspace-url>/api/2.0/delta-sharing/",
    "bearerToken": "<token-from-activation>"
}
```

### 11.5 Consume Shared Data (Run on Your Local Machine)

Back on your **Windows machine** (not in Databricks), run this Python script:

```python
"""
consume_shared_data.py
Run this on your LOCAL MACHINE to simulate the vendor accessing shared data.
This proves Delta Sharing works end-to-end.
"""

import delta_sharing
import pandas as pd

# Path to the profile downloaded from activation link
PROFILE = "C:/Projects/databricks-poc/delta_sharing/vendor_profile.json"

# ============================================================
# 1. List available shares
# ============================================================
print("=== Available Shares ===")
client = delta_sharing.SharingClient(PROFILE)

shares = client.list_shares()
for share in shares:
    print(f"  Share: {share.name}")

# ============================================================
# 2. List available tables
# ============================================================
print("\n=== Available Tables ===")
tables = client.list_all_tables()
for table in tables:
    print(f"  {table.share}.{table.schema}.{table.name}")

# ============================================================
# 3. Read shared tables as Pandas DataFrames
# ============================================================
print("\n=== Reading Shared Data ===")

# Daily Meter Summary
table_url = f"{PROFILE}#vendor_data_share.gold.daily_meter_summary"
dm_df = delta_sharing.load_as_pandas(table_url)
print(f"\n[1] daily_meter_summary: {len(dm_df)} rows, {len(dm_df.columns)} columns")
print(f"    Columns: {list(dm_df.columns)}")
print(dm_df.head())

# Regional Demand
table_url = f"{PROFILE}#vendor_data_share.gold.regional_demand"
rd_df = delta_sharing.load_as_pandas(table_url)
print(f"\n[2] regional_demand: {len(rd_df)} rows")
print(f"    Regions: {sorted(rd_df['region_code'].unique())}")

# Network Assets
table_url = f"{PROFILE}#vendor_data_share.gold.network_assets"
na_df = delta_sharing.load_as_pandas(table_url)
print(f"\n[3] network_assets: {len(na_df)} rows")
print(f"    Status breakdown: {dict(na_df['status'].value_counts())}")

# Forecast Summary
table_url = f"{PROFILE}#vendor_data_share.gold.forecast_summary"
fc_df = delta_sharing.load_as_pandas(table_url)
print(f"\n[4] forecast_summary: {len(fc_df)} rows")
print(f"    Scenarios: {sorted(fc_df['scenario'].unique())}")

print("\n=== Delta Sharing: SUCCESS ===")
print("Vendor can access all 4 Gold tables via open protocol!")
```

### 11.6 Bi-Directional Sharing (Vendor → Utilitics)

```sql
-- Create vendor output table
CREATE TABLE IF NOT EXISTS data_sharing_poc.gold.vendor_forecast_output (
    forecast_id STRING,
    output_date DATE,
    adjusted_demand_mw DOUBLE,
    risk_score DOUBLE,
    recommendation STRING,
    model_name STRING
) USING DELTA
COMMENT 'Vendor forecast adjustments - simulated bi-directional share';

-- Insert sample vendor responses
INSERT INTO data_sharing_poc.gold.vendor_forecast_output VALUES
    ('FC-000001', '2026-01-15', 1250.5, 0.23, 'INCREASE_CAPACITY', 'VendorModel-v2'),
    ('FC-000002', '2026-01-15', 980.3,  0.15, 'STABLE',            'VendorModel-v2'),
    ('FC-000003', '2026-01-15', 1560.8, 0.67, 'HIGH_RISK',         'VendorModel-v2'),
    ('FC-000004', '2026-01-16', 1100.0, 0.31, 'MONITOR',           'VendorModel-v2'),
    ('FC-000005', '2026-01-16', 890.2,  0.12, 'STABLE',            'VendorModel-v2');

-- Create a reverse share
CREATE SHARE IF NOT EXISTS vendor_response_share
  COMMENT 'Vendor response data - bi-directional sharing POC';

ALTER SHARE vendor_response_share
  ADD TABLE data_sharing_poc.gold.vendor_forecast_output;

-- Verify
SHOW ALL IN SHARE vendor_response_share;
SELECT * FROM data_sharing_poc.gold.vendor_forecast_output;
```

---

## 12. Phase 9 – Databricks Workflows (Orchestration)

### 12.1 Create a Workflow Job

Replace Azure Data Factory with free Databricks Workflows:

1. Databricks UI → **Workflows** → **Create Job**
2. Job name: `data_sharing_etl`

### 12.2 Add Tasks

| Task Key | Notebook | Depends On |
|----------|----------|------------|
| generate_data | /POC/01_generate_data | (none) |
| ingest_bronze | /POC/02_ingest_bronze | generate_data |
| transform_silver | /POC/03_transform_silver | ingest_bronze |
| aggregate_gold | /POC/04_aggregate_gold | transform_silver |
| validate | /POC/05_validate | aggregate_gold |

For each task:
- **Type:** Notebook task
- **Cluster:** Use existing `poc-single-node`
- **Timeout:** 30 minutes
- **Retries:** 1

### 12.3 Workflow via API

```powershell
databricks jobs create --json '{
  "name": "data_sharing_etl",
  "tasks": [
    {
      "task_key": "generate_data",
      "notebook_task": {"notebook_path": "/POC/01_generate_data"},
      "existing_cluster_id": "<your-cluster-id>"
    },
    {
      "task_key": "ingest_bronze",
      "depends_on": [{"task_key": "generate_data"}],
      "notebook_task": {"notebook_path": "/POC/02_ingest_bronze"},
      "existing_cluster_id": "<your-cluster-id>"
    },
    {
      "task_key": "transform_silver",
      "depends_on": [{"task_key": "ingest_bronze"}],
      "notebook_task": {"notebook_path": "/POC/03_transform_silver"},
      "existing_cluster_id": "<your-cluster-id>"
    },
    {
      "task_key": "aggregate_gold",
      "depends_on": [{"task_key": "transform_silver"}],
      "notebook_task": {"notebook_path": "/POC/04_aggregate_gold"},
      "existing_cluster_id": "<your-cluster-id>"
    },
    {
      "task_key": "validate",
      "depends_on": [{"task_key": "aggregate_gold"}],
      "notebook_task": {"notebook_path": "/POC/05_validate"},
      "existing_cluster_id": "<your-cluster-id>"
    }
  ],
  "max_concurrent_runs": 1
}'
```

### 12.4 Schedule (Optional – Budget Conscious)

For the POC, run manually. In production, you'd add a schedule:

```json
{
  "schedule": {
    "quartz_cron_expression": "0 0 6 * * ?",
    "timezone_id": "Europe/London"
  }
}
```

> **Budget warning:** A scheduled daily job means the cluster starts every day. For POC, run manually only.

---

## 13. Phase 10 – Monitoring, Alerts & Cost Control

### 13.1 Cost Monitoring Dashboard (Azure Portal)

```
Azure Portal → Cost Management + Billing → Cost analysis
  Scope: rg-databricks-poc
  View: Daily costs
  Group by: Service name

Key metrics to watch:
  - Azure Databricks (compute DBUs)
  - Virtual Machines (cluster VM)
  - Storage Accounts (ADLS)
```

### 13.2 Storage Usage Monitor (Databricks Notebook)

Create notebook: **`/POC/06_monitoring/storage_usage`**

```python
# ============================================================
# Storage Usage Monitor
# Run periodically to track data growth
# ============================================================

print("=== Storage Usage Report ===\n")

layers = {
    "Bronze": ["/mnt/processed-data/bronze/timeseries",
               "/mnt/processed-data/bronze/snapshot",
               "/mnt/processed-data/bronze/files"],
    "Silver": ["/mnt/processed-data/silver/timeseries",
               "/mnt/processed-data/silver/snapshot",
               "/mnt/processed-data/silver/files"],
    "Gold":   ["/mnt/processed-data/gold/daily_meter_summary",
               "/mnt/processed-data/gold/regional_demand",
               "/mnt/processed-data/gold/network_assets",
               "/mnt/processed-data/gold/forecast_summary"]
}

total_bytes = 0
for layer, paths in layers.items():
    layer_bytes = 0
    for path in paths:
        try:
            for f in dbutils.fs.ls(path):
                if not f.name.startswith("_"):
                    layer_bytes += f.size
        except:
            pass
    total_bytes += layer_bytes
    print(f"  {layer}: {round(layer_bytes/1024/1024, 2)} MB")

total_gb = total_bytes / (1024**3)
storage_cost = total_gb * 0.0208  # ADLS Gen2 LRS price per GB/month
print(f"\n  TOTAL: {round(total_bytes/1024/1024, 2)} MB ({round(total_gb, 4)} GB)")
print(f"  Estimated storage cost: ${round(storage_cost, 4)}/month")
```

### 13.3 Azure CLI Cost Check

```powershell
# Quick cost check from PowerShell
az cost management query `
  --type ActualCost `
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-databricks-poc" `
  --timeframe MonthToDate `
  --output table
```

### 13.4 Cluster Monitoring

```python
# In a Databricks notebook:
# Check cluster events (starts, stops, etc.)
cluster_id = spark.conf.get("spark.databricks.clusterUsageTags.clusterId")
print(f"Current cluster: {cluster_id}")
print(f"Cores: {spark.sparkContext.defaultParallelism}")
print(f"Memory: {spark.sparkContext._jsc.sc().getExecutorMemoryStatus().size()} executors")
```

---

## 14. Phase 11 – Performance Tuning on Azure

### 14.1 Delta Lake Optimisation

```sql
-- Run OPTIMIZE on frequently queried Gold tables
OPTIMIZE data_sharing_poc.gold.daily_meter_summary;
OPTIMIZE data_sharing_poc.gold.regional_demand;

-- Z-ORDER for faster queries on common filter columns
OPTIMIZE data_sharing_poc.gold.daily_meter_summary ZORDER BY (region_code, meter_type);
OPTIMIZE data_sharing_poc.gold.regional_demand ZORDER BY (region_code);

-- VACUUM old versions (saves storage)
-- Keeps 7 days of history by default
VACUUM data_sharing_poc.gold.daily_meter_summary RETAIN 168 HOURS;
VACUUM data_sharing_poc.gold.regional_demand RETAIN 168 HOURS;
```

### 14.2 Query Performance

```sql
-- Check table statistics
DESCRIBE DETAIL data_sharing_poc.gold.daily_meter_summary;

-- Analyze for query optimiser
ANALYZE TABLE data_sharing_poc.gold.daily_meter_summary COMPUTE STATISTICS;
ANALYZE TABLE data_sharing_poc.gold.regional_demand COMPUTE STATISTICS;
```

### 14.3 Caching Strategy

```python
# Cache frequently accessed tables during a session
spark.table("data_sharing_poc.gold.daily_meter_summary").cache()
spark.table("data_sharing_poc.gold.regional_demand").cache()

# Uncache when done (frees memory)
spark.catalog.uncacheTable("data_sharing_poc.gold.daily_meter_summary")
```

---

## 15. Phase 12 – Downgrade & Ongoing Operations

### 15.1 Downgrade from Premium to Standard (After Trial)

```powershell
# After 14 days, downgrade to save costs
az databricks workspace update `
  --resource-group rg-databricks-poc `
  --name dbw-poc-datasharing `
  --sku standard
```

### 15.2 What You Lose After Downgrade

| Feature | Premium (Trial) | Standard (Ongoing) |
|---------|----------------|-------------------|
| Unity Catalog | Yes | No (tables still exist but can't manage via catalog) |
| Delta Sharing | Yes | No (existing shares stop working) |
| Workflows | Yes | Yes |
| Delta Lake | Yes | Yes |
| Notebooks | Yes | Yes |
| Cluster management | Yes | Yes |

> **Important:** Screenshot/export all Delta Sharing configs before downgrading. Delta tables and data remain intact.

### 15.3 Ongoing Session Routine

```
Weekly routine (2-3 sessions):
  1. Open Databricks workspace
  2. Start cluster (2-3 min)
  3. Run notebook experiments (30-60 min)
  4. Terminate cluster
  5. Check Azure Cost Management

Monthly:
  - Review total spend
  - Run VACUUM on Delta tables
  - Clean up old data if storage grows
  - Consider deleting RG if taking a break
```

---

## 16. Cleanup & Teardown

### 16.1 Pause (Keep Workspace, Stop Costs)

```powershell
# Terminate cluster (Databricks UI or CLI)
databricks clusters delete --cluster-id <cluster-id>

# Cost when paused:
#   Storage only: ~$0.50/month
#   Compute: $0
```

### 16.2 Full Teardown (Delete Everything)

```powershell
# STEP 1: Export notebooks
databricks workspace export_dir /POC C:\Projects\databricks-poc\azure_backup -o

# STEP 2: Download important data
az storage fs directory download `
  --file-system processed-data `
  --account-name $STORAGE_NAME `
  --source-path gold `
  --destination-path "C:\Projects\databricks-poc\azure_gold_backup" `
  --recursive

# STEP 3: Delete resource group (removes ALL Azure resources)
az group delete --name rg-databricks-poc --yes

# STEP 4: Verify
az group show --name rg-databricks-poc 2>$null
# Should return error: "Resource group not found"
```

### 16.3 Recreate Later

If you want to start again:

```powershell
# Re-run Phase 1 commands to create everything fresh
# Your local code (Part 1) and notebooks backup are still on your machine
# Upload notebooks back to new workspace
```

---

## 17. Architecture Diagrams (Final)

### 17.1 Complete Azure Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AZURE SUBSCRIPTION (Pay-As-You-Go)                    │
│                    Budget: $25/month | Actual: ~$5-8/month               │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Resource Group: rg-databricks-poc                               │    │
│  │                                                                   │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  Azure Databricks Workspace (Standard tier)               │   │    │
│  │  │                                                            │   │    │
│  │  │  ┌─────────────┐                                          │   │    │
│  │  │  │ Cluster:     │  Standard_E2s_v3 (2 vCPU, 16 GB)       │   │    │
│  │  │  │ Single Node  │  Auto-terminate: 10 min                 │   │    │
│  │  │  └──────┬──────┘                                          │   │    │
│  │  │         │                                                   │   │    │
│  │  │         ▼                                                   │   │    │
│  │  │  ┌─────────────────────────────────────────────────┐      │   │    │
│  │  │  │  Notebooks (Pipeline)                            │      │   │    │
│  │  │  │                                                  │      │   │    │
│  │  │  │  01_generate → 02_bronze → 03_silver → 04_gold  │      │   │    │
│  │  │  │                                          │       │      │   │    │
│  │  │  │                                          ▼       │      │   │    │
│  │  │  │                                   05_validate    │      │   │    │
│  │  │  └─────────────────────────────────────────────────┘      │   │    │
│  │  │                                                            │   │    │
│  │  │  ┌────────────────────┐   ┌─────────────────────────┐    │   │    │
│  │  │  │ Unity Catalog      │   │ Delta Sharing            │    │   │    │
│  │  │  │ (Premium trial)    │   │ (Premium trial)          │    │   │    │
│  │  │  │ • bronze schema    │   │ • vendor_data_share      │    │   │    │
│  │  │  │ • silver schema    │   │ • vendor_recipient       │    │   │    │
│  │  │  │ • gold schema      │   │ • 4 Gold tables shared   │    │   │    │
│  │  │  └────────────────────┘   └──────────┬──────────────┘    │   │    │
│  │  └───────────────────────────────────────┼────────────────────┘   │    │
│  │                                           │                        │    │
│  │  ┌──────────────────────────────────┐    │                        │    │
│  │  │  ADLS Gen2 Storage (~$0.50/mo)   │    │                        │    │
│  │  │  • raw-data (timeseries,         │    │                        │    │
│  │  │    snapshot, files)              │    │                        │    │
│  │  │  • processed-data (bronze,       │    │                        │    │
│  │  │    silver, gold Delta tables)    │    │                        │    │
│  │  └──────────────────────────────────┘    │                        │    │
│  │                                           │                        │    │
│  │  ┌──────────────────────────────────┐    │                        │    │
│  │  │  Secret Scope                     │    │                        │    │
│  │  │  • storage-account-key            │    │                        │    │
│  │  │  • storage-account-name           │    │                        │    │
│  │  └──────────────────────────────────┘    │                        │    │
│  └──────────────────────────────────────────┼────────────────────────┘    │
└─────────────────────────────────────────────┼────────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────┐
                              │  VENDOR (Simulated)          │
                              │  Local PySpark +             │
                              │  delta-sharing library       │
                              │  vendor_profile.json         │
                              │                              │
                              │  Reads Gold tables via       │
                              │  Delta Sharing protocol      │
                              └─────────────────────────────┘
```

### 17.2 Data Flow Summary

```
 LOCAL (Part 1)                           AZURE (Part 2)
 ──────────────                           ──────────────
 Generate data ──── Upload ─────────────▶ ADLS Gen2 raw-data/
       │                                        │
       ▼                                        ▼
 Bronze (local) ── Same code ──────────▶ Bronze (ADLS Delta)
       │                                        │
       ▼                                        ▼
 Silver (local) ── Same code ──────────▶ Silver (ADLS Delta)
       │                                        │
       ▼                                        ▼
 Gold (local)   ── Same code ──────────▶ Gold (ADLS Delta)
       │                                        │
       ▼                                        ▼
 Simulated      ── Real ──────────────▶ Delta Sharing
 Delta Sharing     implementation        (vendor_data_share)
```

---

## 18. Troubleshooting Guide

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Workspace won't create** | "Quota exceeded" | Request vCPU quota increase in Azure Portal or try a different region |
| **Cluster won't start** | "Unable to allocate" | Try a different VM size or region |
| **Mount fails** | "Invalid credentials" | Verify storage key in secret scope matches storage account |
| **Mount already exists** | "Mount point already in use" | `dbutils.fs.unmount("/mnt/raw-data")` then remount |
| **Delta Sharing not available** | "Feature not supported" | Requires Premium tier — check trial hasn't expired |
| **Unity Catalog errors** | "Metastore not found" | Ensure metastore is created and assigned to workspace |
| **High unexpected cost** | >$15 in first week | Check cluster is terminated; verify auto-terminate is set |
| **Notebook runs slow** | >5 min for small data | Check cluster is running (not starting); check shuffle partitions = 8 |
| **Storage key expired** | "Authentication failed" | Regenerate key in Azure Portal, update secret scope |
| **Databricks CLI auth fails** | "Unauthorized" | Generate new PAT token, reconfigure CLI |
| **Budget alert not firing** | No email received | Check email in Azure budget config; alerts may take 24 hrs |

---

## 19. Production Readiness Checklist

What would change if this were a real production deployment:

| POC Setting | Production Recommendation |
|-------------|--------------------------|
| Single-node cluster | Multi-node with auto-scaling (2-8 workers) |
| Standard_E2s_v3 | Standard_D4s_v3 or larger |
| 10 min auto-terminate | Scheduled start/stop via Workflows |
| Manual runs | Scheduled Workflows (daily/hourly) |
| Secret scope (Databricks-backed) | Azure Key Vault-backed secret scope |
| No networking | VNET injection + Private Link |
| Standard tier (after trial) | Premium tier (Unity Catalog + Delta Sharing) |
| No monitoring | Azure Monitor + Log Analytics |
| No disaster recovery | Geo-redundant storage (GRS) + workspace backup |
| Pay-as-you-go | Reserved instances for compute savings |

---

## 20. What You Have Learned

After completing Parts 1 and 2, you now have hands-on experience with:

| Skill Area | Part 1 (Local) | Part 2 (Azure) |
|-----------|----------------|-----------------|
| **PySpark** | DataFrame API, transformations, aggregations | Same + Databricks optimisations |
| **Delta Lake** | ACID tables, time travel, schema enforcement | + OPTIMIZE, Z-ORDER, VACUUM |
| **Medallion Architecture** | Bronze/Silver/Gold design | + Unity Catalog registration |
| **Data Quality** | Validation framework, quality reports | Same in cloud context |
| **Delta Sharing** | Simulated protocol | Real implementation with recipients |
| **Azure** | N/A | Resource groups, ADLS Gen2, Databricks workspace |
| **Cost Management** | N/A | Budget alerts, cluster management, tier selection |
| **Orchestration** | Python subprocess | Databricks Workflows |
| **Security** | N/A | Secret scopes, PAT tokens, mount configs |
| **DevOps** | Local → cloud migration | CLI deployments, API-driven setup |

### Interview Talking Points

From this POC, you can confidently discuss:

1. **"How would you design a data sharing platform?"** → Medallion architecture, Delta Sharing, Unity Catalog
2. **"How do you manage cloud costs?"** → Auto-terminate, single-node, budget alerts, tier selection
3. **"What's the difference between Bronze, Silver, and Gold?"** → You built all three with real transformations
4. **"How does Delta Sharing work?"** → You implemented it end-to-end, including recipient management
5. **"How do you test data pipelines?"** → Validation notebook with quality checks, drop rate monitoring
6. **"How do you orchestrate pipelines?"** → Databricks Workflows vs ADF trade-offs (cost and capability)
