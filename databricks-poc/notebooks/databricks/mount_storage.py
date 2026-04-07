# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Mount Storage — ADLS Gen2
# MAGIC **Utilitics Data Sharing POC**
# MAGIC
# MAGIC Mounts the two ADLS Gen2 containers to Databricks filesystem.
# MAGIC
# MAGIC **Run this notebook ONCE** after workspace setup. Mounts persist across cluster restarts.
# MAGIC
# MAGIC | Mount Point | Container | Purpose |
# MAGIC |-------------|-----------|---------|
# MAGIC | `/mnt/raw-data` | `raw-data` | Parquet raw sources (timeseries, snapshot, files) |
# MAGIC | `/mnt/processed-data` | `processed-data` | Bronze / Silver / Gold Delta tables |
# MAGIC
# MAGIC **Prerequisites:** Secret scope `poc-secrets` must exist with keys:
# MAGIC - `storage-account-name`
# MAGIC - `storage-account-key`

# COMMAND ----------

# Retrieve credentials from secret scope (never hardcode keys)
storage_account = dbutils.secrets.get(scope="poc-secrets", key="storage-account-name")
storage_key     = dbutils.secrets.get(scope="poc-secrets", key="storage-account-key")

mount_config = {
    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net": storage_key
}

print(f"Storage account: {storage_account}")
print(f"Storage key:     {'*' * 20} (hidden)")

# COMMAND ----------

# MAGIC %md ## Mount raw-data container

# COMMAND ----------

def mount_container(container, mount_point, storage_account, config):
    source = f"abfss://{container}@{storage_account}.dfs.core.windows.net"
    try:
        dbutils.fs.mount(
            source=source,
            mount_point=mount_point,
            extra_configs=config
        )
        print(f"  Mounted:  {mount_point}  →  {source}")
    except Exception as e:
        if "already mounted" in str(e).lower():
            print(f"  Already mounted:  {mount_point}  (no action needed)")
        else:
            raise e

mount_container("raw-data",       "/mnt/raw-data",       storage_account, mount_config)
mount_container("processed-data", "/mnt/processed-data", storage_account, mount_config)

# COMMAND ----------

# MAGIC %md ## Verify Mounts

# COMMAND ----------

print("\nActive mounts (POC containers):")
for m in dbutils.fs.mounts():
    if "raw-data" in m.mountPoint or "processed-data" in m.mountPoint:
        print(f"  {m.mountPoint:<25} →  {m.source}")

# COMMAND ----------

# MAGIC %md ## Test: List raw-data contents

# COMMAND ----------

print("Contents of /mnt/raw-data:")
try:
    for f in dbutils.fs.ls("/mnt/raw-data"):
        print(f"  {f.name}")
except Exception as e:
    print(f"  ERROR: {e}")
    print("  → Check that raw-data container exists in storage account")

print("\nContents of /mnt/processed-data:")
try:
    for f in dbutils.fs.ls("/mnt/processed-data"):
        print(f"  {f.name}")
except Exception as e:
    print(f"  ERROR: {e}")
    print("  → Check that processed-data container exists in storage account")
