# Azure Deployment and Pipeline Run — 2026-05-14

## Summary
Reactivated Azure subscription, cleaned up old Databricks resources, deployed all Toad POC
infrastructure to Azure, and successfully ran the ADF pipeline end-to-end.

---

## Azure Subscription

- Account: karnaradha80@gmail.com
- Subscription: Azure subscription 1
- Subscription ID: d926b212-30a3-4e2b-aa1c-dcec14dd7ad1
- Region: UK South

### Why it was disabled
Left-over Databricks POC resources kept running after the certification study finished:
- NAT Gateway (~£30-50/month idle) — most expensive
- Public IP (hourly charge)
- Storage accounts (Data Lake Gen2 LRS + GRS)
These exhausted the free trial credits and disabled the subscription.

### Fix
Reactivated subscription → Azure auto-deleted all Databricks resources during the disabled period
(Azure deletes resources after grace period) → clean slate, no manual deletion needed.

---

## Resources Deployed — rg-toad-poc (UK South)

| Resource | Name | Notes |
|---|---|---|
| Resource Group | `rg-toad-poc` | Container for all POC resources |
| Storage Account | `sttoadpoc` | Standard LRS, StorageV2 |
| Blob Container | `toad-poc-reports` | Report output + archive |
| SQL Server | `sql-toad-poc` | Admin: sqladmin |
| SQL Database | `db-toad-poc` | Basic tier (~£4/month) |
| Key Vault | `kv-toad-poc` | Vault access policy mode |
| ADF Factory | `adf-toad-poc` | System-assigned managed identity |
| ADF Pipeline | `PL_Toad_POC` | Trigger stopped by default |
| Logic App | `la-toad-poc-email` | HTTP trigger stub (no email yet) |

### Secrets in Key Vault
| Secret | Value |
|---|---|
| `azuresql-db-password` | SQL admin password |
| `storage-account-key` | Blob Storage account key |

### Key Vault Access Policies
| Principal | Permissions |
|---|---|
| karnaradha80@gmail.com (user) | get, list, set, delete |
| adf-toad-poc managed identity | get, list |

### SQL Firewall Rules
| Rule | IP |
|---|---|
| AllowAzureServices | 0.0.0.0 |
| AllowLocalDev | 82.43.104.231 |

---

## Data Loaded in Azure SQL

| Table | Rows |
|---|---|
| MAXRPD.T_ODS_LOG | 1 |
| abcbimart.fct_gas_escapes_v | 10 |
| abcbimart.dim_work_orders | 20 |
| abcbimart.dim_organisation | 10 |
| abcbimart.dim_addresses | 10 |
| abcbimart.dim_calendar | 8 |
| abcbimart.dim_time | 10 |
| config.report | 1 |
| config.report_email | 13 |

Note: SQL scripts loaded via Python pyodbc (sqlcmd not installed).
config.report_email needed a separate fix — DBCC RESEED gave report_id=0 instead of 1.
Fixed via `tools/fix_config_data.py` using IDENTITY_INSERT ON.

---

## ADF ARM Template Changes Made

| Change | Reason |
|---|---|
| Renamed pipeline `PL_BC_BIMIO_267_Daily` → `PL_Toad_POC` | Use generic name |
| Removed `LS_Oracle_Source` linked service | Not needed for POC (Azure SQL used instead) |
| Replaced `DS_Oracle_ODS_Log` with `DS_AzureSQL_ODS_Log` | POC uses Azure SQL as source |
| Removed managed identity credential from Blob LS | RBAC role assignment failing on fresh sub |
| Changed Blob LS to use account key from Key Vault | Works without RBAC role assignments |
| Added `User ID=sqladmin` to SQL connection string | Was missing, caused null userId error |
| Updated `logic_app_email_url` parameter | Set to real Logic App trigger URL |

---

## ADF Linked Services (final state)

### LS_AzureKeyVault
```
Type: AzureKeyVault
URL:  https://kv-toad-poc.vault.azure.net/
```

### LS_AzureSQL_Target
```
Type:   AzureSqlDatabase
Server: sql-toad-poc.database.windows.net
DB:     db-toad-poc
User:   sqladmin
Pass:   Key Vault secret: azuresql-db-password
```

### LS_AzureBlobStorage
```
Type:              AzureBlobStorage
ConnectionString:  DefaultEndpointsProtocol=https;AccountName=sttoadpoc;...
AccountKey:        Key Vault secret: storage-account-key
```

---

## Logic App — la-toad-poc-email

HTTP trigger stub — accepts POST from ADF, returns 200 OK.
Does NOT send real emails yet — Office 365 connector needs one-time browser OAuth login.

**Trigger URL:**
```
https://prod-20.uksouth.logic.azure.com:443/workflows/a494dc2a42ec491b8d914af8749d4f50/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=tBu6x8My_5vrYVuct7oVgQ9HYnVspEYTfH7twZ_0k5A
```

### To add real email sending (one-time portal setup):
1. Open Azure Portal → la-toad-poc-email → Logic App Designer
2. Add action after HTTP trigger: Office 365 Outlook → Send an email
3. Sign in with karnaradha80@gmail.com when prompted
4. Map fields: To, Subject, Body from trigger body
5. Save

---

## Pipeline Run — Succeeded

Run ID: e81f33c0-4fae-11f1-b280-7cfa80a234fc
Duration: 80 seconds

| Activity | Status | Duration |
|---|---|---|
| Lookup_ODS_Refresh_Check | Succeeded | 6.6s |
| SetVar_ReportDate | Succeeded | 0.3s |
| If_ODS_Refreshed | Succeeded | 61.6s (TRUE branch) |
| Copy_ReportData_To_Blob | Succeeded | 16.1s |
| Copy_Archive_File | Succeeded | 15.6s |
| Email_Report_To_Operations | Succeeded | 14.6s |
| Email_Confirmation_To_BI_Team | Succeeded | 5.7s |

### Output files in Blob Storage (toad-poc-reports)
```
output/BC_BIMIO_267_PRECOPY_13.05.2026.csv         1,679 bytes
archive/BIMIO267_12Hour_Prevented_Daily_For_13.05.2026.csv  1,679 bytes
```

---

## Issues Encountered and Fixes

| Issue | Fix |
|---|---|
| Subscription disabled | Reactivated via portal |
| Databricks extension blocking CLI | Renamed folder to `databricks_disabled` |
| Key Vault RBAC mode blocking secret write | Recreated KV with `--enable-rbac-authorization false` |
| ADF managed identity RBAC role assignment failing | Used storage account key in KV instead |
| ADF Key Vault access denied on first run | Set KV access policy for ADF managed identity |
| SQL connection string missing User ID | Updated LS_AzureSQL_Target via CLI |
| config.report_email 0 rows (report_id=0) | Fixed via tools/fix_config_data.py |
| Logic App CLI needs interactive install | Pre-installed with `az extension add --name logic` |

---

## Deployment Commands (for re-deployment)

```bash
# 1. Create resource group
az group create --name rg-toad-poc --location uksouth

# 2. Create supporting resources
az storage account create --name sttoadpoc --resource-group rg-toad-poc --location uksouth --sku Standard_LRS --kind StorageV2
az storage container create --name toad-poc-reports --account-name sttoadpoc
az sql server create --name sql-toad-poc --resource-group rg-toad-poc --location uksouth --admin-user sqladmin --admin-password "ToadPoc@2026!"
az sql db create --resource-group rg-toad-poc --server sql-toad-poc --name db-toad-poc --edition Basic
az sql server firewall-rule create --resource-group rg-toad-poc --server sql-toad-poc --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
az keyvault create --name kv-toad-poc --resource-group rg-toad-poc --location uksouth --enable-rbac-authorization false
az keyvault set-policy --name kv-toad-poc --resource-group rg-toad-poc --object-id b3fdd49b-3ae9-4209-999b-caa886c9b222 --secret-permissions get list set delete

# 3. Store secrets
az keyvault secret set --vault-name kv-toad-poc --name "azuresql-db-password" --value "ToadPoc@2026!"
STORAGE_KEY=$(az storage account keys list --account-name sttoadpoc --resource-group rg-toad-poc --query "[0].value" -o tsv)
az keyvault secret set --vault-name kv-toad-poc --name "storage-account-key" --value "$STORAGE_KEY"

# 4. Deploy ADF
az deployment group create --resource-group rg-toad-poc --template-file adf_templates/arm_template.json --parameters adf_templates/arm_template_parameters.json

# 5. Grant ADF Key Vault access (get ADF principal ID first)
ADF_PRINCIPAL=$(az datafactory show --factory-name adf-toad-poc --resource-group rg-toad-poc --query "identity.principalId" -o tsv)
az keyvault set-policy --name kv-toad-poc --resource-group rg-toad-poc --object-id $ADF_PRINCIPAL --secret-permissions get list

# 6. Load sample data
python tools/fix_config_data.py  # after running sql_scripts 01-03
```

---

## Next Steps

### Immediate
- Add real email to Logic App (one-time portal step — see instructions above)
- Test pipeline with email sending validated

### Future
- AWS equivalent (Glue + S3 + SES) after Azure POC proven
- Add spending alerts in Azure Cost Management (prevent surprise charges)
- Set budget alert: £10/month threshold on rg-toad-poc
