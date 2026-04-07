"""
upload_notebooks.py
Upload all Databricks notebooks to the workspace via REST API.

Usage:
    python upload_notebooks.py

Requires DATABRICKS_HOST and DATABRICKS_TOKEN environment variables
(or fill in the values below directly for one-off use).

Notebooks uploaded to: /POC/
"""

import os
import base64
import requests
import sys

# ─── Config ───────────────────────────────────────────────────────────────────

DBX_HOST  = os.environ.get("DATABRICKS_HOST",  "https://adb-7405604806384457.17.azuredatabricks.net")
DBX_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")

NOTEBOOKS_DIR    = os.path.join(os.path.dirname(__file__), "notebooks", "databricks")
WORKSPACE_FOLDER = "/POC"

# Notebooks to upload (order matters for display — mount_storage and create_catalog first)
NOTEBOOKS = [
    "mount_storage.py",
    "create_catalog.py",
    "00_config.py",
    "01_generate_data.py",
    "02_ingest_bronze.py",
    "03_transform_silver.py",
    "04_aggregate_gold.py",
    "05_validate.py",
    "run_pipeline.py",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_headers():
    if not DBX_TOKEN:
        print("ERROR: DATABRICKS_TOKEN not set.")
        print("  Set it with:  export DATABRICKS_TOKEN=dapi...")
        sys.exit(1)
    return {"Authorization": f"Bearer {DBX_TOKEN}"}


def ensure_folder(folder_path):
    url  = f"{DBX_HOST}/api/2.0/workspace/mkdirs"
    resp = requests.post(url, headers=get_headers(), json={"path": folder_path})
    if resp.status_code == 200:
        print(f"  Folder ready: {folder_path}")
    else:
        print(f"  Folder {folder_path}: {resp.status_code} — {resp.text}")


def upload_notebook(local_path, workspace_path):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "path":      workspace_path,
        "format":    "SOURCE",
        "language":  "PYTHON",
        "content":   encoded,
        "overwrite": True,
    }

    url  = f"{DBX_HOST}/api/2.0/workspace/import"
    resp = requests.post(url, headers=get_headers(), json=payload)

    if resp.status_code == 200:
        print(f"  OK  {workspace_path}")
    else:
        print(f"  ERR {workspace_path}  →  {resp.status_code}: {resp.text}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Utilitics — Upload Notebooks to Databricks")
    print(f"  Host:   {DBX_HOST}")
    print(f"  Target: {WORKSPACE_FOLDER}/")
    print("=" * 60)

    ensure_folder(WORKSPACE_FOLDER)

    missing = []
    for nb in NOTEBOOKS:
        local = os.path.join(NOTEBOOKS_DIR, nb)
        if not os.path.exists(local):
            missing.append(nb)

    if missing:
        print(f"\nERROR: These notebook files were not found locally:")
        for m in missing:
            print(f"  {os.path.join(NOTEBOOKS_DIR, m)}")
        sys.exit(1)

    print(f"\nUploading {len(NOTEBOOKS)} notebooks...")
    for nb in NOTEBOOKS:
        local          = os.path.join(NOTEBOOKS_DIR, nb)
        notebook_name  = nb.replace(".py", "")
        workspace_path = f"{WORKSPACE_FOLDER}/{notebook_name}"
        upload_notebook(local, workspace_path)

    print("\n" + "=" * 60)
    print("  Upload complete.")
    print(f"  Open: {DBX_HOST}/#workspace{WORKSPACE_FOLDER}")
    print("=" * 60)
    print()
    print("NEXT STEPS:")
    print("  1. Open Databricks UI → Workspace → /POC/")
    print("  2. Run mount_storage   (once — mounts ADLS containers)")
    print("  3. Check Unity Catalog is enabled (Admin Console)")
    print("  4. Run create_catalog  (once — creates catalog + schemas)")
    print("  5. Run 01_generate_data → 02_ingest_bronze → 03_transform_silver")
    print("       → 04_aggregate_gold → 05_validate")
    print("  6. Run create_catalog  Step 3 cells (register tables in Unity Catalog)")
    print()


if __name__ == "__main__":
    main()
