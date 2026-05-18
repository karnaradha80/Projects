# 2026-05-14 — Generate 1000 Sample Records

## Summary
Generated 1000 gas escape records with supporting dimension data, loaded into Azure SQL.

## What was done

### generate_sample_data.py
Writes all CSV files to `sample_data/`:
- `dim_organisation.csv` — 20 rows (3 networks, 5 LDZs, 20 depots)
- `dim_addresses.csv` — 50 rows (generic street addresses)
- `dim_calendar.csv` — 43 rows (2026-04-01 to 2026-05-13, matching SQL WHERE clause date range)
- `dim_time.csv` — 24 rows (hourly slots 00:00:00 to 23:00:00)
- `dim_work_orders.csv` — 2000 rows (ids 1-1000 root WOs, 1001-2000 gas-prevented WOs)
- `fct_gas_escapes_v.csv` — 1000 rows (each linking root WO + prev WO + org + address + date + time)

### load_sample_data.py
Truncates and reloads all tables from CSVs into Azure SQL (`abcbimart` schema).
- Uses pyodbc with `{SQL Server}` driver
- Loads dims first, then fact (respects FK order)
- No IDENTITY_INSERT needed (abcbimart tables use plain int PKs, not IDENTITY)

### Fix discovered
`SET IDENTITY_INSERT` fails on tables without the IDENTITY property.
abcbimart dimension tables use plain INT PKs — removed the identity flag from the loader.

## Row counts confirmed in Azure SQL
| Table | Rows |
|---|---|
| dim_organisation | 20 |
| dim_addresses | 50 |
| dim_calendar | 43 |
| dim_time | 24 |
| dim_work_orders | 2000 |
| fct_gas_escapes_v | 1000 |

## Also completed earlier this session (continuation)

### ADF Pipeline update (update_adf_pipeline.py)
- Fixed `az datafactory pipeline create-or-update` → correct command is `create`
- Fixed command-line-too-long error by writing JSON to temp file and passing `@file.json`
- Fixed `az` not found in Python subprocess — use full path `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`
- Pipeline updated successfully

### Pipeline test run
- Run ID: `70f37069-4fc0-11f1-92aa-7cfa80a234fc`
- Status: Succeeded (96 seconds)
- Blobs confirmed:
  - `output/BC_BIMIO_267_PRECOPY_13.05.2026.csv` — 1,818 bytes
  - `output/BC_BIMIO_267_PRECOPY_13.05.2026.xlsm` — 99,530 bytes
  - `archive/BIMIO267_12Hour_Prevented_Daily_For_13.05.2026.xlsm` — 99,530 bytes

## Pending
- Commit all changes to git
- Email step: Logic App needs Office 365 connection — deferred by user
- AWS equivalent (Glue + S3 + SES) — after Azure POC proven
- Set spending alert on rg-toad-poc
