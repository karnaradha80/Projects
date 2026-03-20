"""
upload_to_adls.py
=================
Upload local lake/ data to ADLS Gen2 storage.
Run: python upload_to_adls.py
"""

import os
import sys
from azure.storage.filedatalake import DataLakeServiceClient

STORAGE_NAME = "stpocadls4417"
STORAGE_KEY  = os.environ.get("STORAGE_KEY", "")

if not STORAGE_KEY:
    print("ERROR: Set STORAGE_KEY environment variable first.")
    print("Run: $env:STORAGE_KEY = '<your-storage-key>'")
    sys.exit(1)

service = DataLakeServiceClient(
    account_url=f"https://{STORAGE_NAME}.dfs.core.windows.net",
    credential=STORAGE_KEY
)


def upload_dir(container, local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"  SKIP (not found): {local_path}")
        return 0
    fs = service.get_file_system_client(container)
    count = 0
    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file = os.path.join(root, file)
            rel        = os.path.relpath(local_file, local_path).replace("\\", "/")
            remote_file = f"{remote_path}/{rel}"
            fc = fs.get_file_client(remote_file)
            with open(local_file, "rb") as f:
                fc.upload_data(f.read(), overwrite=True)
            print(f"  Uploaded: {remote_file}")
            count += 1
    return count


print("=" * 50)
print("  UPLOADING DATA TO ADLS Gen2")
print("=" * 50)

total = 0
total += upload_dir("raw-data", r"C:\Projects\databricks-poc\lake\raw\timeseries", "timeseries")
total += upload_dir("raw-data", r"C:\Projects\databricks-poc\lake\raw\files",      "files")
total += upload_dir("raw-data", r"C:\Projects\databricks-poc\lake\sources",        "snapshot")

print(f"\n  Total files uploaded: {total}")
print("=" * 50)
