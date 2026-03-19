# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Run Pipeline — Full Orchestrator
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Runs all 5 notebooks in sequence using `dbutils.notebook.run()`.
# MAGIC
# MAGIC ### Changes from local version
# MAGIC | # | Local | Databricks |
# MAGIC |---|-------|-----------|
# MAGIC | 1 | `subprocess.run([sys.executable, script])` | `dbutils.notebook.run(notebook, timeout)` |
# MAGIC | 2 | `sys.exit(1)` on failure | `raise Exception(...)` to fail the job |
# MAGIC | 3 | Print-based status | `dbutils.notebook.exit()` passes result to caller |

# COMMAND ----------

# MAGIC %md ## Widget — Timeout per notebook (seconds)

# COMMAND ----------

# CHANGE 2: dbutils.widgets instead of hardcoded values / input()
dbutils.widgets.text("timeout_seconds", "1800", "Timeout per notebook (s)")
TIMEOUT = int(dbutils.widgets.get("timeout_seconds"))

# COMMAND ----------

import time

steps = [
    ("01 — Data Generation",      "./01_generate_data"),
    ("02 — Bronze Ingestion",      "./02_ingest_bronze"),
    ("03 — Silver Transformation", "./03_transform_silver"),
    ("04 — Gold Aggregation",      "./04_aggregate_gold"),
    ("05 — Pipeline Validation",   "./05_validate"),
]

results  = []
pipeline_start = time.time()

print("=" * 60)
print("  UTILITICS — FULL PIPELINE RUN")
print("=" * 60)

# COMMAND ----------

for step_name, notebook_path in steps:
    print(f"\n  ▶  {step_name}...")
    step_start = time.time()
    status     = "SUCCESS"

    try:
        # CHANGE 1: dbutils.notebook.run() replaces subprocess.run()
        dbutils.notebook.run(notebook_path, timeout_seconds=TIMEOUT)
    except Exception as e:
        status = f"FAILED: {e}"

    elapsed = round(time.time() - step_start, 1)
    results.append((step_name, status, elapsed))
    print(f"     {status}  ({elapsed}s)")

# COMMAND ----------

# MAGIC %md ## Pipeline Summary

# COMMAND ----------

total_elapsed = round(time.time() - pipeline_start, 1)
all_passed    = all(r[1] == "SUCCESS" for r in results)

print("\n" + "=" * 60)
print("  UTILITICS — PIPELINE COMPLETE")
print("=" * 60)
print(f"  {'Step':<30} {'Status':<12} {'Time':>8}")
print(f"  {'─' * 52}")
for step_name, status, elapsed in results:
    icon = "✅" if status == "SUCCESS" else "❌"
    print(f"  {icon} {step_name:<28} {status:<12} {elapsed:>6}s")
print(f"\n  Total elapsed: {total_elapsed}s")
print(f"  Overall: {'✅ ALL STEPS PASSED' if all_passed else '❌ PIPELINE FAILED'}")
print("=" * 60)

# CHANGE 3: dbutils.notebook.exit() passes result to parent job / ADF
# In Part 2 Azure, ADF reads this exit value to determine pipeline success
if not all_passed:
    failed = [r[0] for r in results if r[1] != "SUCCESS"]
    dbutils.notebook.exit(f"FAILED: {failed}")
else:
    dbutils.notebook.exit("SUCCESS")
