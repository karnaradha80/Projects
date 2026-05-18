# Azure SQL as POC Source — 2026-05-14

## Summary
Decided to use Azure SQL Server as the POC source (loaded with sample data) instead of Oracle.
Updated ADF templates and created SQL setup scripts accordingly.

---

## Key Decision

**Question raised:** Why do we need Azure SQL Server as target if the output is Excel?

**Answer:** Azure SQL Server is NOT the final destination. It is used as the **POC source** only — loaded with sample data to simulate Oracle. The real output is CSV/Excel in Blob Storage.

**Updated Architecture:**
```
Azure SQL (sample data — simulates Oracle)
    ├── MAXRPD.T_ODS_LOG        → ODS refresh check
    └── abcbimart.*             → Report query (all dimension joins)
            ↓
        ADF Pipeline
            ↓
    Azure Blob Storage (CSV output + archive)
            ↓
    Logic App (email notification)
```

---

## What Changed from Previous Session

| Component | Before | After |
|---|---|---|
| ODS check source | Oracle (DS_Oracle_ODS_Log) | Azure SQL (DS_AzureSQL_ODS_Log) |
| ODS check query | Oracle SQL (TRUNC/SYSDATE) | T-SQL (CAST AS DATE / GETDATE()) |
| Report query source | Azure SQL (unchanged) | Azure SQL (unchanged) |
| Oracle linked service | Active | Kept for future production use |

---

## SQL Scripts Created (`sql_scripts\`)

| File | Purpose |
|---|---|
| `01_create_schemas.sql` | Create MAXRPD and abcbimart schemas in Azure SQL |
| `02_create_tables.sql` | Create all 7 tables (T-SQL DDL) |
| `03_load_sample_data.sql` | Insert sample data matching sample_data\ CSVs |
| `04_verify_data.sql` | Row count checks + full report query test |

### Run Order
```sql
-- In Azure SQL (SSMS or Azure Data Studio):
-- 1. Run 01_create_schemas.sql
-- 2. Run 02_create_tables.sql
-- 3. Run 03_load_sample_data.sql
-- 4. Run 04_verify_data.sql  ← confirms everything works
```

---

## ADF Templates Updated

| File | Change |
|---|---|
| `datasets/DS_AzureSQL_ODS_Log.json` | New dataset — Azure SQL MAXRPD.T_ODS_LOG |
| `pipelines/PL_BC_BIMIO_267_Daily.json` | ODS Lookup now uses DS_AzureSQL_ODS_Log + AzureSqlSource |
| `arm_template.json` | Pipeline dependency updated to DS_AzureSQL_ODS_Log |

---

## Oracle Linked Service — Future Use
`LS_Oracle_Source.json` and `DS_Oracle_ODS_Log.json` are kept in the templates.
When connecting to real Oracle in production:
- Switch pipeline ODS Lookup dataset from `DS_AzureSQL_ODS_Log` → `DS_Oracle_ODS_Log`
- Change source type from `AzureSqlSource` → `OracleSource`
- Change query from T-SQL → Oracle SQL (`TRUNC(ems) = TRUNC(SYSDATE)`)

---

## Full Deployment Steps (when Azure subscription is ready)

```bash
# 1. Create resource group
az group create --name rg-bimio267-poc --location uksouth

# 2. Create Azure SQL Server + Database
az sql server create --name sql-bimio267-poc --resource-group rg-bimio267-poc --location uksouth --admin-user sqladmin --admin-password <password>
az sql db create --resource-group rg-bimio267-poc --server sql-bimio267-poc --name db-bimio267 --edition Basic

# 3. Run SQL scripts in order (via SSMS or Azure Data Studio)
#    01_create_schemas.sql → 02_create_tables.sql → 03_load_sample_data.sql → 04_verify_data.sql

# 4. Deploy ADF ARM template
az deployment group create \
  --resource-group rg-bimio267-poc \
  --template-file adf_templates/arm_template.json \
  --parameters adf_templates/arm_template_parameters.json

# 5. Add secrets to Key Vault
az keyvault secret set --vault-name kv-bimio267-poc --name azuresql-db-password --value "<password>"

# 6. Create Blob Storage container: bimio-reports
# 7. Set up Logic App for email (HTTP trigger → Office 365 connector)
# 8. Update logic_app_email_url in pipeline parameter
# 9. Run pipeline manually to validate
# 10. Start trigger TR_Daily_0600 when validated
```

---

## Complete Folder Structure (end of session)

```
C:\Projects\Toad_poc\
├── toad_xml_files\
│   ├── Toad_267_Daily.txt              (sanitized UTF-16)
│   └── Toad_267_Daily_utf8.txt         (sanitized UTF-8)
├── schemas\                            (7 SQL DDL files — original schema reference)
├── sample_data\                        (7 CSV files — generic test data)
├── pipeline\
│   └── pipeline.py                     (local Python pipeline — runs successfully)
├── sql_scripts\
│   ├── 01_create_schemas.sql
│   ├── 02_create_tables.sql
│   ├── 03_load_sample_data.sql
│   └── 04_verify_data.sql
├── adf_templates\
│   ├── linkedServices\
│   │   ├── LS_Oracle_Source.json       (kept for future production use)
│   │   ├── LS_AzureSQL_Target.json
│   │   ├── LS_AzureBlobStorage.json
│   │   └── LS_AzureKeyVault.json
│   ├── datasets\
│   │   ├── DS_Oracle_ODS_Log.json      (kept for future production use)
│   │   ├── DS_AzureSQL_ODS_Log.json    (POC — ODS check via Azure SQL)
│   │   ├── DS_AzureSQL_GasEscapes.json
│   │   ├── DS_Blob_Excel_Output.json
│   │   └── DS_Blob_Archive.json
│   ├── pipelines\
│   │   └── PL_BC_BIMIO_267_Daily.json
│   ├── arm_template.json
│   └── arm_template_parameters.json
├── output\
│   ├── BC_BIMIO_267_PRECOPY.xlsx
│   └── archive\
│       └── BIMIO_267_12Hour_Prevented_Daily_For_13.05.2026.xlsx
└── conversations\
    ├── 2026-05-14_toad_poc_setup.md
    ├── 2026-05-14_adf_arm_templates.md
    └── 2026-05-14_azure_sql_poc_source.md
```

---

## Next Steps
- Set up Azure subscription (new free account)
- Create Azure SQL Server + Database
- Run SQL scripts to set up tables and load sample data
- Deploy ADF ARM template
- Set up Logic App for email
- Run and validate ADF pipeline
- AWS equivalent after Azure POC is proven
