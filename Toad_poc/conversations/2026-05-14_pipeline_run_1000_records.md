# 2026-05-14 — Pipeline Run with 1000 Records

## Summary
Ran ADF pipeline PL_Toad_POC with full 1000-row dataset. Succeeded end-to-end.

## Pipeline Run
- Run ID: `6eeaf09d-4fc2-11f1-b97f-7cfa80a234fc`
- Status: **Succeeded**
- Duration: 89 seconds
- Started: 2026-05-14T18:26:33Z
- Ended:   2026-05-14T18:28:02Z

## Output Blobs Confirmed
| Blob | Size |
|---|---|
| `output/BC_BIMIO_267_PRECOPY_13.05.2026.csv` | 173 KB (1000 rows) |
| `output/BC_BIMIO_267_PRECOPY_13.05.2026.xlsm` | 167 KB (populated Excel template) |
| `archive/BIMIO267_12Hour_Prevented_Daily_For_13.05.2026.xlsm` | 167 KB (final archive copy) |

CSV grew from 1.8 KB (10 rows) to 173 KB (1000 rows) — confirms all records flowing through.

## Full Pipeline Activity Chain
```
Lookup_ODS_Refresh_Check
  → SetVar_ReportDate
    → If_ODS_Refreshed
        [true branch]
        Copy_ReportData_To_Blob       (SQL → CSV, 1000 rows, includes Job Type)
          → Populate_Excel_Template   (Azure Function → fills Raw Data sheet → .xlsm)
            → Copy_Archive_File       (.xlsm copied to archive/ with report name)
              → Email_Report_To_Operations      (stub, not connected)
                → Email_Confirmation_To_BI_Team (stub, not connected)
```

## Infrastructure State (as of this session)
| Resource | Name | Notes |
|---|---|---|
| ADF | adf-toad-poc | Pipeline: PL_Toad_POC |
| SQL Server | sql-toad-poc / db-toad-poc | 1000 fact rows, 2000 work orders |
| Storage | sttoadpoc / toad-poc-reports | output/ and archive/ containers |
| Key Vault | kv-toad-poc | secrets: storage-account-key, azuresql-db-password, func-populate-template-key |
| Function App | func-toad-poc | populate_template HTTP trigger (Python 3.11) |
| Logic App | la-toad-poc-email | HTTP stub only — email NOT connected |

## Tools Written This Session
| Script | Purpose |
|---|---|
| `tools/generate_sample_data.py` | Generates all dimension + fact CSVs (1000 records) |
| `tools/load_sample_data.py` | Truncates and reloads Azure SQL tables from CSVs |
| `tools/update_adf_pipeline.py` | Updates ADF pipeline definition via az CLI |

## Pending / Next Discussion
- Questions from user (to be discussed)
- Commit all changes to git
- Email step: connect Logic App to Office 365 (deferred)
- AWS equivalent: Glue + S3 + SES (after Azure POC proven)
- Set spending alert on rg-toad-poc
