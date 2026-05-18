# ADF ARM Templates Generation — 2026-05-14

## Summary
Generated Azure Data Factory ARM templates from the local Python POC pipeline, completing the full Toad → ADF migration artefacts.

---

## ADF Templates Folder Structure

```
C:\Projects\Toad_poc\adf_templates\
├── linkedServices\
│   ├── LS_Oracle_Source.json        — Oracle connection (ODS refresh check)
│   ├── LS_AzureSQL_Target.json      — Azure SQL Server connection (target DB)
│   ├── LS_AzureBlobStorage.json     — Blob Storage (report output + archive)
│   └── LS_AzureKeyVault.json        — Key Vault (all secrets)
├── datasets\
│   ├── DS_Oracle_ODS_Log.json       — MAXRPD.T_ODS_LOG (Oracle)
│   ├── DS_AzureSQL_GasEscapes.json  — abcbimart.fct_gas_escapes_v (Azure SQL)
│   ├── DS_Blob_Excel_Output.json    — output/PRECOPY CSV file (Blob)
│   └── DS_Blob_Archive.json         — archive/sent files (Blob)
├── pipelines\
│   └── PL_BC_BIMIO_267_Daily.json  — full pipeline with all activities
├── arm_template.json                — combined deployable ARM template
└── arm_template_parameters.json    — environment parameter values
```

---

## Toad → ADF Activity Mapping

| Toad Activity | Type | ADF Equivalent | ADF Type |
|---|---|---|---|
| Execute_1 | SelectDataActivity | Lookup_ODS_Refresh_Check | Lookup Activity |
| Set_Variable_1 | VariableActivity | SetVar_ReportDate | SetVariable Activity |
| If_1 | VariableIfElseActivity | If_ODS_Refreshed | IfCondition Activity |
| File_1 | SelectToExcelActivity | Copy_ReportData_To_Blob | Copy Activity → Blob (CSV) |
| Copy_1 | CopyFileActivity | Copy_Archive_File | Copy Activity → Blob archive |
| Email_1 | SendEmailActivity | Email_Report_To_Operations | WebActivity → Logic App |
| Email_2 | SendEmailActivity | Email_ODS_Not_Refreshed | WebActivity → Logic App |
| Email_3 | SendEmailActivity | Email_Confirmation_To_BI_Team | WebActivity → Logic App |
| FaultHandlersActivity | Error handler | Pipeline failure path | ADF failure dependency |

---

## SQL Translation: Redshift/Oracle → T-SQL (Azure SQL)

| Redshift/Oracle | T-SQL Equivalent |
|---|---|
| `DECODE(col, 'A', 'B', col)` | `CASE WHEN col = 'A' THEN 'B' ELSE col END` |
| `date_trunc('month', sysdate-1)` | `DATEFROMPARTS(YEAR(DATEADD(DAY,-1,GETDATE())), MONTH(DATEADD(DAY,-1,GETDATE())), 1)` |
| `date_trunc('year', date)` | `DATEFROMPARTS(YEAR(date), 1, 1)` |
| `date_add('month', N, date)` | `DATEADD(MONTH, N, date)` |
| `date_add('day', N, date)` | `DATEADD(DAY, N, date)` |
| `DATEDIFF(minutes, a, b)` | `DATEDIFF(MINUTE, a, b)` |
| `::TIMESTAMP` cast | `CAST(... AS DATETIME2)` |
| `(date \|\| ' ' \|\| time)::TIMESTAMP` | `DATEADD(SECOND, DATEDIFF(SECOND,'00:00:00', CAST(RIGHT(time,8) AS TIME)), CAST(CONVERT(DATE, date, 103) AS DATETIME2))` |
| `to_date(col,'dd/mm/yyyy')` | `CONVERT(DATE, col, 103)` |
| `TRUNC(sysdate)` | `CAST(GETDATE() AS DATE)` |

---

## Financial Year Start Calculation

**Redshift:**
```sql
date_add('month', 3,
    date_trunc('year',
        date_add('month', -3,
            date_add('day', -1, SYSDATE-3))))
```

**T-SQL:**
```sql
DATEADD(MONTH, 3,
    DATEFROMPARTS(
        YEAR(DATEADD(MONTH, -3, DATEADD(DAY, -4, GETDATE()))),
    1, 1))
```
Result: April 1st of current UK financial year.

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Excel output | CSV via Copy Activity | ADF doesn't natively write .xlsm; downstream Azure Function can convert |
| Secrets | Azure Key Vault | Best practice — no passwords in pipeline config |
| Auth to Blob | Managed Identity | No storage keys needed |
| Email | Logic App via WebActivity | ADF has no native SMTP; Logic App handles Office 365 |
| Trigger | Daily at 06:00 GMT | Matches original Toad schedule; set to Stopped by default |

---

## To Deploy to Azure (when ready)

```bash
# 1. Create resource group
az group create --name rg-bimio267-poc --location uksouth

# 2. Deploy ARM template
az deployment group create \
  --resource-group rg-bimio267-poc \
  --template-file arm_template.json \
  --parameters arm_template_parameters.json

# 3. Add secrets to Key Vault
az keyvault secret set --vault-name kv-bimio267-poc --name oracle-db-password  --value "your-oracle-password"
az keyvault secret set --vault-name kv-bimio267-poc --name azuresql-db-password --value "your-sql-password"

# 4. Grant ADF Managed Identity access to Key Vault and Blob Storage

# 5. Set Logic App URL in pipeline parameter: logic_app_email_url

# 6. Start the trigger when ready
```

---

## Parameters to Update Before Deployment (arm_template_parameters.json)

| Parameter | Description |
|---|---|
| `factoryName` | ADF instance name |
| `storage_account_name` | Azure Blob Storage account |
| `azure_sql_server` | Azure SQL Server hostname |
| `azure_sql_db` | Azure SQL database name |
| `key_vault_name` | Key Vault name |
| `oracle_host` | Oracle server hostname |
| `logic_app_email_url` | Logic App HTTP trigger URL |

---

## Full POC Folder Structure (end of session)

```
C:\Projects\Toad_poc\
├── toad_xml_files\
│   ├── Toad_267_Daily.txt              (sanitized UTF-16)
│   └── Toad_267_Daily_utf8.txt         (sanitized UTF-8)
├── schemas\                            (7 SQL DDL files)
├── sample_data\                        (7 CSV files)
├── pipeline\
│   └── pipeline.py                     (local Python pipeline)
├── adf_templates\                      (ADF ARM templates)
├── output\
│   ├── BC_BIMIO_267_PRECOPY.xlsx
│   └── archive\
│       └── BIMIO_267_12Hour_Prevented_Daily_For_13.05.2026.xlsx
└── conversations\
    ├── 2026-05-14_toad_poc_setup.md
    └── 2026-05-14_adf_arm_templates.md
```

---

## Next Steps
- Set up Azure subscription (new free account or re-activate with spend limit)
- Fill in `arm_template_parameters.json` with real Azure resource names
- Deploy ARM template to Azure
- Set up Logic App for email delivery
- Load schema + sample data into Azure SQL
- Run ADF pipeline and validate output matches local Python pipeline
- AWS equivalent (Glue + S3) — after Azure POC validated
