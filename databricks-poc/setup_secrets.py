"""
setup_secrets.py
================
Store ADLS storage credentials in Databricks secret scope.
Run: python setup_secrets.py
"""

import requests
import subprocess
import sys

DBX_HOST = "https://adb-7405604806384457.17.azuredatabricks.net"
TOKEN    = "dapicce170a8f1c0a365317974791a3b733e"
STORAGE_NAME = "stpocadls4417"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get storage key from environment variable
import os
storage_key = os.environ.get("STORAGE_KEY", "").strip()
if not storage_key:
    print("ERROR: Set STORAGE_KEY environment variable first.")
    sys.exit(1)
print(f"Storage key retrieved: {storage_key[:10]}...")

# Store storage account name
print("\nStoring storage-account-name...")
r = requests.post(f"{DBX_HOST}/api/2.0/secrets/put", headers=headers, json={
    "scope": "poc-secrets",
    "key": "storage-account-name",
    "string_value": STORAGE_NAME
})
print(f"  Status: {r.status_code} — {r.text or 'OK'}")

# Store storage key
print("Storing storage-account-key...")
r = requests.post(f"{DBX_HOST}/api/2.0/secrets/put", headers=headers, json={
    "scope": "poc-secrets",
    "key": "storage-account-key",
    "string_value": storage_key
})
print(f"  Status: {r.status_code} — {r.text or 'OK'}")

# Verify
print("\nVerifying secrets...")
r = requests.get(f"{DBX_HOST}/api/2.0/secrets/list?scope=poc-secrets", headers=headers)
secrets = r.json().get("secrets", [])
for s in secrets:
    print(f"  {s['key']} (last updated: {s.get('last_updated_timestamp', 'N/A')})")

print("\nDone!")
