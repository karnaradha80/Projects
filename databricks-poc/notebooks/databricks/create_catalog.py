# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Create Unity Catalog Structure
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Creates the catalog and schemas for the Medallion architecture.
# MAGIC
# MAGIC **Run this notebook ONCE** after Unity Catalog metastore is enabled.
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog metastore created and attached to this workspace (done via Admin Console)
# MAGIC - Cluster has Unity Catalog access mode enabled
# MAGIC
# MAGIC **What this creates:**
# MAGIC ```
# MAGIC data_sharing_poc          ← Catalog
# MAGIC ├── bronze                ← Schema: raw ingested Delta tables
# MAGIC ├── silver                ← Schema: cleansed Delta tables
# MAGIC └── gold                  ← Schema: business aggregates (shared via Delta Sharing)
# MAGIC ```

# COMMAND ----------

# Load config first — sets storage credentials so abfss:// paths work in SQL cells
%run ./00_config

# COMMAND ----------

# MAGIC %md ## Step 1 — Catalog already created via UI
# MAGIC Catalog `data_sharing_poc` was created manually via the Databricks UI.
# MAGIC Skipping CREATE CATALOG — running SHOW to confirm it exists.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW CATALOGS LIKE 'data_sharing_poc';

# COMMAND ----------

# MAGIC %md ## Step 2 — Create Schemas (Bronze / Silver / Gold)

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG data_sharing_poc;
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS bronze
# MAGIC   COMMENT 'Raw ingestion layer — no transformations, append-only';
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS silver
# MAGIC   COMMENT 'Cleaned and validated data — deduped, standardised, enriched';
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS gold
# MAGIC   COMMENT 'Business-ready aggregated data — shared externally via Delta Sharing';
# MAGIC
# MAGIC SHOW SCHEMAS IN data_sharing_poc;

# COMMAND ----------

# MAGIC %md ## Step 3 — Register Delta Tables (run AFTER pipeline completes)
# MAGIC
# MAGIC Run the pipeline first (`01_generate_data` → `02_ingest_bronze` → `03_transform_silver` → `04_aggregate_gold`),
# MAGIC then come back and run the cells below to register the Delta tables in Unity Catalog.

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG data_sharing_poc;
# MAGIC
# MAGIC -- Bronze tables
# MAGIC CREATE TABLE IF NOT EXISTS bronze.timeseries
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/bronze/timeseries'
# MAGIC   COMMENT 'Raw smart meter readings — 30 min intervals, 500 meters, 7 days';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS bronze.snapshot
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/bronze/snapshot'
# MAGIC   COMMENT 'Raw network asset snapshots — daily status per asset';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS bronze.file_data
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/bronze/files'
# MAGIC   COMMENT 'Raw ERM demand forecast files';
# MAGIC
# MAGIC SHOW TABLES IN bronze;

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG data_sharing_poc;
# MAGIC
# MAGIC -- Silver tables
# MAGIC CREATE TABLE IF NOT EXISTS silver.timeseries
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/silver/timeseries'
# MAGIC   COMMENT 'Cleaned meter readings — deduped, range-validated, peak-hour flag added';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS silver.snapshot
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/silver/snapshot'
# MAGIC   COMMENT 'Cleaned asset snapshots — UK coordinate bounds validated, maintenance flag added';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS silver.file_data
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/silver/files'
# MAGIC   COMMENT 'Validated forecasts — confidence intervals checked, forecast_date cast to DateType';
# MAGIC
# MAGIC SHOW TABLES IN silver;

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG data_sharing_poc;
# MAGIC
# MAGIC -- Gold tables (these will be shared via Delta Sharing)
# MAGIC CREATE TABLE IF NOT EXISTS gold.daily_meter_summary
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/gold/daily_meter_summary'
# MAGIC   COMMENT 'Daily consumption per meter — 3,500 records. Shared with vendor.';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.regional_demand
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/gold/regional_demand'
# MAGIC   COMMENT 'Hourly regional demand totals — 840 records. Shared with vendor.';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.network_assets
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/gold/network_assets'
# MAGIC   COMMENT 'Latest asset status and location — 2,000 records. Shared with vendor.';
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS gold.forecast_summary
# MAGIC   USING DELTA
# MAGIC   LOCATION 'abfss://processed-data@stpocadls4417.dfs.core.windows.net/gold/forecast_summary'
# MAGIC   COMMENT 'Aggregated demand forecasts — 420 records. Shared with vendor.';
# MAGIC
# MAGIC SHOW TABLES IN gold;

# COMMAND ----------

# MAGIC %md ## Step 4 — Verify Everything

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG data_sharing_poc;
# MAGIC
# MAGIC -- Show all tables across all schemas
# MAGIC SELECT table_catalog, table_schema, table_name, table_type, comment
# MAGIC FROM   information_schema.tables
# MAGIC WHERE  table_schema IN ('bronze', 'silver', 'gold')
# MAGIC ORDER BY table_schema, table_name;
