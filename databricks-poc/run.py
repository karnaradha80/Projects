"""
run.py
======
Utilitics — Unified Pipeline Launcher

Single entry point for the entire pipeline.
Reads RUNTIME from config/pipeline_config.py and routes accordingly.

Usage:
  python run.py                  # uses RUNTIME flag from pipeline_config.py
  python run.py --local          # force local regardless of flag
  python run.py --cloud          # force Databricks regardless of flag
  python run.py --status         # check last Databricks run status
  python run.py --config         # show current config (runtime, mode, token set?)

To switch permanently:
  Edit config/pipeline_config.py  →  RUNTIME = "local" or "databricks"
"""

import sys
import os
import argparse
import time
import subprocess
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))
from config.pipeline_config import RUNTIME, get_databricks_config


# ============================================================
# Argument parsing — flag overrides config
# ============================================================
parser = argparse.ArgumentParser(description="Utilitics Pipeline Launcher")
group  = parser.add_mutually_exclusive_group()
group.add_argument("--local",  action="store_true", help="Force local execution")
group.add_argument("--cloud",  action="store_true", help="Force Databricks execution")
group.add_argument("--status", action="store_true", help="Check last Databricks run status")
group.add_argument("--config", action="store_true", help="Show current configuration")
args = parser.parse_args()

# Resolve effective runtime
if args.local:
    effective_runtime = "local"
elif args.cloud:
    effective_runtime = "databricks"
else:
    effective_runtime = RUNTIME   # read from pipeline_config.py


# ============================================================
# --config: show current settings
# ============================================================
def show_config():
    dbx = get_databricks_config()
    token_set = "SET ✅" if dbx["token"] else "NOT SET ❌  (run: set DATABRICKS_TOKEN=...)"
    cluster   = dbx["cluster_id"] if dbx["cluster_id"] else "blank (new cluster per run)"

    print("=" * 60)
    print("  UTILITICS — CURRENT CONFIGURATION")
    print("=" * 60)
    print(f"  RUNTIME (config):    {RUNTIME}")
    print(f"  RUNTIME (effective): {effective_runtime}")
    print()
    print("  Databricks settings:")
    print(f"    Workspace URL:  {dbx['workspace_url']}")
    print(f"    Token:          {token_set}")
    print(f"    Notebook path:  {dbx['notebook_path']}")
    print(f"    Cluster ID:     {cluster}")
    print()
    print("  To change runtime permanently:")
    print("    Edit config/pipeline_config.py  →  RUNTIME = \"local\" or \"databricks\"")
    print("=" * 60)


# ============================================================
# LOCAL execution — existing run_pipeline.py
# ============================================================
def run_local():
    print("=" * 60)
    print("  UTILITICS — LOCAL PIPELINE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "notebooks", "run_pipeline.py")],
        capture_output=False
    )
    sys.exit(result.returncode)


# ============================================================
# DATABRICKS execution — REST API trigger
# ============================================================
def run_databricks():
    try:
        import requests
    except ImportError:
        print("\n  [ERROR] 'requests' package not installed.")
        print("  Run: pip install requests")
        sys.exit(1)

    dbx   = get_databricks_config()
    token = dbx["token"]
    url   = dbx["workspace_url"].rstrip("/")

    if not token:
        print("\n  [ERROR] DATABRICKS_TOKEN environment variable is not set.")
        print("  Steps:")
        print("  1. In Databricks: User Settings → Access Tokens → Generate New Token")
        print("  2. Then in your terminal:")
        print("       set DATABRICKS_TOKEN=your_token_here          (cmd)")
        print("       $env:DATABRICKS_TOKEN=\"your_token_here\"      (PowerShell)")
        print("  3. Re-run: python run.py --cloud")
        sys.exit(1)

    if "<your-email>" in dbx["notebook_path"]:
        print("\n  [ERROR] Notebook path not configured.")
        print("  Edit config/pipeline_config.py:")
        print("    DATABRICKS_CONFIG[\"notebook_path\"] = \"/Users/you@email.com/databricks/run_pipeline\"")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }

    # Build the run submission payload
    payload = {
        "run_name": f"utilitics-pipeline-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "notebook_task": {
            "notebook_path": dbx["notebook_path"],
            "base_parameters": {
                "timeout_seconds": "1800"
            }
        }
    }

    # Attach to existing cluster or spin up a new one
    if dbx["cluster_id"]:
        payload["existing_cluster_id"] = dbx["cluster_id"]
    else:
        payload["new_cluster"] = {
            "num_workers":    0,
            "spark_version":  dbx["spark_version"],
            "node_type_id":   dbx["node_type"],
            "spark_conf": {
                "spark.master":                 "local[*]",
                "spark.databricks.cluster.profile": "singleNode",
            },
            "custom_tags": {"ResourceClass": "SingleNode"},
        }

    print("=" * 60)
    print("  UTILITICS — DATABRICKS PIPELINE")
    print(f"  Workspace: {url}")
    print(f"  Notebook:  {dbx['notebook_path']}")
    print(f"  Started:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Submit the run
    print("\n  Submitting run to Databricks...")
    resp = requests.post(f"{url}/api/2.1/jobs/runs/submit", headers=headers, json=payload)

    if resp.status_code != 200:
        print(f"\n  [ERROR] Submission failed: {resp.status_code}")
        print(f"  Response: {resp.text}")
        sys.exit(1)

    run_id = resp.json()["run_id"]
    run_url = f"{url}/#job/runs/{run_id}"
    print(f"  Run submitted  ·  Run ID: {run_id}")
    print(f"  Monitor at:    {run_url}")

    # Save run_id for --status
    state_file = os.path.join(os.path.dirname(__file__), ".last_dbx_run_id")
    with open(state_file, "w") as f:
        f.write(str(run_id))

    # Poll for completion
    print("\n  Polling status every 15 seconds...\n")
    poll_start = time.time()

    while True:
        time.sleep(15)
        status_resp = requests.get(
            f"{url}/api/2.1/jobs/runs/get?run_id={run_id}",
            headers=headers
        )

        if status_resp.status_code != 200:
            print(f"  [WARNING] Status poll failed: {status_resp.status_code}")
            continue

        run_data   = status_resp.json()
        life_cycle = run_data["state"]["life_cycle_state"]
        result_state = run_data["state"].get("result_state", "")
        elapsed    = round(time.time() - poll_start)

        print(f"  [{elapsed:>4}s]  {life_cycle}  {result_state}")

        if life_cycle in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"):
            break

    # Final result
    print()
    if result_state == "SUCCESS":
        exit_output = run_data.get("notebook_output", {}).get("result", "")
        print("=" * 60)
        print("  DATABRICKS PIPELINE COMPLETE")
        print(f"  Result:  {exit_output}")
        print(f"  Run URL: {run_url}")
        print("=" * 60)
    else:
        error = run_data["state"].get("state_message", "")
        print("=" * 60)
        print(f"  DATABRICKS PIPELINE FAILED")
        print(f"  State:   {result_state}")
        print(f"  Message: {error}")
        print(f"  Run URL: {run_url}")
        print("=" * 60)
        sys.exit(1)


# ============================================================
# --status: check last submitted Databricks run
# ============================================================
def check_status():
    try:
        import requests
    except ImportError:
        print("  Run: pip install requests")
        sys.exit(1)

    state_file = os.path.join(os.path.dirname(__file__), ".last_dbx_run_id")
    if not os.path.exists(state_file):
        print("  No previous Databricks run found.")
        print("  Run: python run.py --cloud  to start one.")
        sys.exit(0)

    with open(state_file) as f:
        run_id = f.read().strip()

    dbx     = get_databricks_config()
    url     = dbx["workspace_url"].rstrip("/")
    token   = dbx["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(f"{url}/api/2.1/jobs/runs/get?run_id={run_id}", headers=headers)
    if resp.status_code != 200:
        print(f"  [ERROR] {resp.status_code}: {resp.text}")
        sys.exit(1)

    data        = resp.json()
    life_cycle  = data["state"]["life_cycle_state"]
    result      = data["state"].get("result_state", "IN PROGRESS")
    start_time  = data.get("start_time", 0)
    run_url     = f"{url}/#job/runs/{run_id}"

    print("=" * 60)
    print(f"  LAST DATABRICKS RUN STATUS")
    print("=" * 60)
    print(f"  Run ID:     {run_id}")
    print(f"  State:      {life_cycle}")
    print(f"  Result:     {result}")
    print(f"  Run URL:    {run_url}")
    print("=" * 60)


# ============================================================
# Entry point
# ============================================================
if args.config or args.status:
    if args.config:
        show_config()
    if args.status:
        check_status()
elif effective_runtime == "local":
    run_local()
elif effective_runtime == "databricks":
    run_databricks()
else:
    print(f"  [ERROR] Unknown RUNTIME: '{effective_runtime}'. Use 'local' or 'databricks'.")
    sys.exit(1)
