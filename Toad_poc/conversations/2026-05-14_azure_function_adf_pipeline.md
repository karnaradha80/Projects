# 2026-05-14 — Azure Function Deploy + ADF Pipeline Update

## Summary
Completed the Azure → ADF pipeline with Excel template population.
Full end-to-end pipeline `PL_Toad_POC` now runs successfully.

## What was done

### Azure Function `populate_template`
- Built and deployed to `func-toad-poc.azurewebsites.net`
- Python 3.11, Consumption plan (Linux), UK South
- Deployed via `func azure functionapp publish --python` (Core Tools v4)
- App setting `STORAGE_CONNECTION_STRING` wired up for blob access
- Function key stored in Key Vault as `func-populate-template-key`

**Flow:**
1. Reads `report_date`, `csv_blob`, `out_blob` from POST body
2. Downloads CSV from `toad-poc-reports/output/`
3. Downloads `.xlsm` template from `toad-poc-reports/templates/BC_BIMIO_267_TEMPLATE.xlsm`
4. Clears Raw Data sheet rows 2+, writes CSV rows in from row 2
5. Uploads populated `.xlsm` back to blob
6. Returns `{"status": "success", "output_blob": "..."}`

### ADF Pipeline `PL_Toad_POC` — updated
Updated via `tools/update_adf_pipeline.py`:
- Added `dwor.job_type AS [Job Type]` to SQL SELECT
- Added `Populate_Excel_Template` WebActivity (calls Azure Function) after `Copy_ReportData_To_Blob`
- `Copy_Archive_File` now depends on `Populate_Excel_Template` and copies `.xlsm`

**Final pipeline activity chain (inside IfTrue branch):**
```
Copy_ReportData_To_Blob
  → Populate_Excel_Template   (Azure Function call)
    → Copy_Archive_File        (.xlsm to archive/)
      → Email_Report_To_Operations   (stub — not connected)
        → Email_Confirmation_To_BI_Team  (stub — not connected)
```

### CLI fixes discovered
- `az datafactory pipeline create-or-update` doesn't exist — use `create`
- JSON too long for command line — must write to temp file and pass `@file.json`
- `az` not on PATH for Python subprocess on Windows — use full path `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`

## Test Run Results
- Run ID: `70f37069-4fc0-11f1-92aa-7cfa80a234fc`
- Status: **Succeeded** (96 seconds)
- Output blobs confirmed:
  - `output/BC_BIMIO_267_PRECOPY_13.05.2026.csv` — 1,818 bytes
  - `output/BC_BIMIO_267_PRECOPY_13.05.2026.xlsm` — 99,530 bytes
  - `archive/BIMIO267_12Hour_Prevented_Daily_For_13.05.2026.xlsm` — 99,530 bytes

## Infrastructure State
| Resource | Name |
|---|---|
| ADF | adf-toad-poc |
| SQL Server | sql-toad-poc / db-toad-poc |
| Storage | sttoadpoc / toad-poc-reports |
| Key Vault | kv-toad-poc |
| Function App | func-toad-poc |
| Logic App | la-toad-poc-email (HTTP stub, no email wired) |

## Pending
- Email step: Logic App needs Office 365 connection — deferred by user
- AWS equivalent (Glue + S3 + SES) — after Azure POC proven
- Set spending alert on rg-toad-poc
