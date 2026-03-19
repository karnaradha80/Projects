"""
consume_shared_data.py  (Option B)
====================================
Vendor-side client for the OSS Delta Sharing server.
Reads Gold tables via the real Delta Sharing protocol.

Prerequisites:
  1. Download the Delta Sharing server JAR from:
       https://github.com/delta-io/delta-sharing/releases
       File: delta-sharing-server-x.x.x.zip  →  extract JAR to delta_sharing/
  2. Start the server in a separate terminal:
       java -jar delta_sharing/delta-sharing-server.jar --config delta_sharing/server_config.yaml
  3. Run this script:
       python delta_sharing/consume_shared_data.py

Run via menu: python delta_sharing/run_sharing.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("=" * 60)
print("  DELTA SHARING CLIENT  —  Option B (OSS Server)")
print("=" * 60)

try:
    import delta_sharing
except ImportError:
    print("\n  [ERROR] delta-sharing package not installed.")
    print("  Run: pip install delta-sharing")
    sys.exit(1)

PROFILE = os.path.join(os.path.dirname(__file__), "recipient_profile.json")

if not os.path.exists(PROFILE):
    print(f"\n  [ERROR] Profile not found: {PROFILE}")
    sys.exit(1)

print(f"\n  Profile: {PROFILE}")
print("  Connecting to Delta Sharing server at localhost:8080...\n")

try:
    client = delta_sharing.SharingClient(PROFILE)

    # ============================================================
    # List available shares and tables
    # ============================================================
    print("--- DISCOVERY ---")
    shares = client.list_shares()
    print(f"  Shares available: {[s.name for s in shares]}")

    all_tables = client.list_all_tables()
    print(f"  Tables available:")
    for t in all_tables:
        print(f"    - {t.share}.{t.schema}.{t.name}")

    # ============================================================
    # Read tables as Pandas DataFrames
    # ============================================================
    print("\n--- READING TABLES ---")

    print("\n  [1] daily_meter_summary")
    dm = delta_sharing.load_as_pandas(
        f"{PROFILE}#vendor_data_share.gold.daily_meter_summary")
    print(f"      Rows: {len(dm):,}  |  Columns: {len(dm.columns)}")
    print(dm[["meter_id", "reading_date", "total_kwh", "data_completeness_pct"]].head())

    print("\n  [2] regional_demand")
    rd = delta_sharing.load_as_pandas(
        f"{PROFILE}#vendor_data_share.gold.regional_demand")
    print(f"      Rows: {len(rd):,}  |  Regions: {sorted(rd['region_code'].unique())}")

    print("\n  [3] network_assets")
    na = delta_sharing.load_as_pandas(
        f"{PROFILE}#vendor_data_share.gold.network_assets")
    print(f"      Rows: {len(na):,}")
    print(f"      Status breakdown: {dict(na['status'].value_counts())}")

    print("\n  [4] forecast_summary")
    fc = delta_sharing.load_as_pandas(
        f"{PROFILE}#vendor_data_share.gold.forecast_summary")
    print(f"      Rows: {len(fc):,}  |  Scenarios: {sorted(fc['scenario'].unique())}")

    # ============================================================
    # Vendor analysis
    # ============================================================
    print("\n--- VENDOR ANALYSIS ---")

    print("\n  Analysis 1: Regional demand peaks")
    peak = rd.groupby("region_code").agg(
        max_demand=("total_demand_kwh", "max"),
        max_meters=("active_meters", "max")
    ).reset_index()
    print(peak.to_string(index=False))

    print("\n  Analysis 2: Assets needing maintenance")
    needs_maint = na[na["needs_maintenance"] == True]
    print(f"      {len(needs_maint)}/{len(na)} assets need maintenance "
          f"({round(len(needs_maint)/len(na)*100, 1)}%)")

    print("\n" + "=" * 60)
    print("  DELTA SHARING CLIENT COMPLETE  (Option B)")
    print("=" * 60)
    print("  Data was read via real Delta Sharing protocol.")
    print("  In Azure (Part 2): same code, different profile endpoint.")
    print("=" * 60)

except Exception as e:
    print(f"\n  [ERROR] Could not connect to Delta Sharing server.")
    print(f"  Details: {e}")
    print("\n  Make sure the server is running:")
    print("    java -jar delta_sharing/delta-sharing-server.jar \\")
    print("         --config delta_sharing/server_config.yaml")
    sys.exit(1)
