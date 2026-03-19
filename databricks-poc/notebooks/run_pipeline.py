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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
    print(f"\n{chr(0x2500) * 60}")
    print(f"  Step {i}/{len(SCRIPTS)}: {description}")
    print(f"  Script: {script}")
    print(f"{chr(0x2500) * 60}")

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
print(f"  {chr(0x2500) * 47}")
for desc, status, elapsed in results:
    print(f"  {desc:<25} {status:>10} {elapsed:>8}s")
print(f"  {chr(0x2500) * 47}")
print(f"  {'TOTAL':<25} {'':>10} {overall_elapsed:>8}s")

all_passed = all(s == "SUCCESS" for _, s, _ in results)
print(f"\n  Overall: {'ALL STEPS PASSED' if all_passed else 'PIPELINE FAILED'}")
print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
