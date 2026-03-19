"""
simulate_sharing.py  (Option A)
================================
Simulate Delta Sharing locally by reading Gold tables
as if you were the vendor (recipient).

This demonstrates the CONCEPT without needing the OSS server.

Run directly: python delta_sharing/simulate_sharing.py
Or via menu:  python delta_sharing/run_sharing.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.spark_config import get_spark_session
from config.pipeline_config import get_path

import pandas as pd

# ============================================================
# PROVIDER SIDE (Your organisation: Utilitics)
# ============================================================
print("=" * 60)
print("  DELTA SHARING SIMULATION  —  Option A (Python)")
print("=" * 60)

print("\n--- PROVIDER SIDE (Utilitics) ---")
print("  Sharing Gold tables with vendor...")

spark = get_spark_session("DeltaSharingSimulation")

gold_tables = {
    "daily_meter_summary": get_path("gold_daily_meter"),
    "regional_demand":     get_path("gold_regional_demand"),
    "network_assets":      get_path("gold_network_assets"),
    "forecast_summary":    get_path("gold_forecast_summary"),
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
# VENDOR PROCESSING
# ============================================================
print("\n--- VENDOR PROCESSING ---")
print("  Vendor analyses the received data...")

print("\n  Analysis 1: Regional demand peaks")
peak_demand = (rd_df
    .groupBy("region_code")
    .agg(
        {"total_demand_kwh": "max", "active_meters": "max"}
    )
    .toPandas())
print(peak_demand.to_string(index=False))

print("\n  Analysis 2: Assets needing maintenance")
maintenance_needed = na_df.filter("needs_maintenance = true").count()
total_assets = na_df.count()
print(f"      {maintenance_needed}/{total_assets} assets need maintenance "
      f"({round(maintenance_needed / total_assets * 100, 1)}%)")

# ============================================================
# BI-DIRECTIONAL: Vendor sends data back
# ============================================================
print("\n--- BI-DIRECTIONAL SHARING (Vendor → Utilitics) ---")
print("  Vendor creates response data...")

vendor_response = spark.createDataFrame([
    ("FC-000001", "2026-01-15", 1250.5, 0.23, "INCREASE_CAPACITY", "VendorModel-v2"),
    ("FC-000002", "2026-01-15",  980.3, 0.15, "STABLE",            "VendorModel-v2"),
    ("FC-000003", "2026-01-15", 1560.8, 0.67, "HIGH_RISK",         "VendorModel-v2"),
    ("FC-000004", "2026-01-16", 1100.0, 0.31, "MONITOR",           "VendorModel-v2"),
    ("FC-000005", "2026-01-16",  890.2, 0.12, "STABLE",            "VendorModel-v2"),
], ["forecast_id", "output_date", "adjusted_demand_mw",
    "risk_score", "recommendation", "model_name"])

vendor_output_path = get_path("gold_daily_meter").replace(
    "gold/daily_meter_summary", "gold/vendor_forecast_output")
vendor_response.write.format("delta").mode("overwrite").save(vendor_output_path)

print(f"  Vendor shared: {vendor_response.count()} forecast responses")
vendor_response.show(truncate=False)

print("\n" + "=" * 60)
print("  DELTA SHARING SIMULATION COMPLETE  (Option A)")
print("=" * 60)
print("  In production (Part 2 - Azure):")
print("    - Replace local reads with delta_sharing.load_as_pandas()")
print("    - Use Databricks recipient tokens for authentication")
print("    - Vendor gets a profile.json with bearer token")
print("=" * 60)

spark.stop()
