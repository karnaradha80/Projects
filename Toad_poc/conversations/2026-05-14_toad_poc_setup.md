# Toad POC Setup — 2026-05-14

## Summary
Initial session setting up the Toad to Azure/AWS migration POC locally.

---

## Context
- **Current tool**: Toad (Quest Software) — used for Oracle DB reporting
- **Migration target**: Azure (first), then AWS
- **Source DB**: Oracle
- **Target DB**: Azure SQL Server (POC uses local simulation)
- **Pipeline output**: Excel reports (.xlsm)

---

## Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Cloud target | Azure first, AWS later | Phased approach |
| POC approach | Local (no Azure cost) | Avoid unnecessary cloud spend |
| Local DB | No Docker needed | CSV sample data sufficient for POC |
| Target DB | Azure SQL Server | POC goal |
| SQL translation | Oracle/Redshift SQL → Python/pandas | Local simulation |

---

## Pipeline Analysis: BC_BIMIO_267_Daily

### What it does
Daily automated report — tracks gas escape incidents and whether gas was prevented within 12 hours.

### Pipeline Flow
```
START
  ├─ Step 1: Check ODS data refresh (Oracle — T_ODS_LOG)
  ├─ Step 2: Set date variable = yesterday's date
  └─ Step 3: IF/ELSE
        ├─ IF data NOT refreshed (count=0) → Alert email to operations teams
        └─ IF data IS refreshed (count=1)
              ├─ Run SQL → Export to Excel (BC_BIMIO_267_PRECOPY.xlsm)
              ├─ Copy & archive file with date suffix
              ├─ Send report email with Excel attached
              └─ Send confirmation email to BI team
  + Error Handler: crash → email log to BI team
```

### Databases Involved
- **Oracle** (ORACLE_SERVER/ORACLE_SCHEMA): ODS refresh check only
- **Redshift** (via ODBC): Main report SQL query

### Main SQL — Tables Used
| Table | Schema | Type | Purpose |
|---|---|---|---|
| fct_gas_escapes_v | abcbimart | Fact (view) | Main gas escape incidents |
| dim_work_orders | abcbimart | Dimension | Work order details |
| dim_organisation | abcbimart | Dimension | Network, LDZ, depot |
| dim_addresses | abcbimart | Dimension | Incident addresses |
| dim_calendar | abcbimart | Dimension | Date dimension |
| dim_time | abcbimart | Dimension | Time dimension |
| T_ODS_LOG | MAXRPD | Log table (Oracle) | ODS refresh check |

### Report Columns
| Column | Description |
|---|---|
| Network | Gas network name |
| LDZ | Local Distribution Zone |
| Depot | Depot name (DEPOT_K mapped to DEPOT_L) |
| Work Order | Gas prevented work order number |
| Root Work Order | Root emergency work order number |
| Emergency Date | When gas escape was reported |
| Gas Prevented | Timestamp when gas was stopped |
| Time Difference | Hours between report and prevention (rounded 2dp) |
| Address | Incident location |
| MTD | 1 if incident is within current month |
| Less 12 | 1 if prevented within 12 hours |
| Great 12 | 1 if took more than 12 hours |
| Count | Always 1 (for aggregation) |

### Date Range
Financial year start (April 1st) to yesterday.

---

## Folder Structure Created

```
C:\Projects\Toad_poc\
├── toad_xml_files\
│   ├── Toad_267_Daily.txt           (sanitized, UTF-16)
│   └── Toad_267_Daily_utf8.txt      (sanitized, UTF-8)
├── schemas\
│   ├── fct_gas_escapes_v.sql
│   ├── dim_work_orders.sql
│   ├── dim_organisation.sql
│   ├── dim_addresses.sql
│   ├── dim_calendar.sql
│   ├── dim_time.sql
│   └── t_ods_log.sql
├── sample_data\
│   ├── fct_gas_escapes_v.csv
│   ├── dim_work_orders.csv
│   ├── dim_organisation.csv
│   ├── dim_addresses.csv
│   ├── dim_calendar.csv
│   ├── dim_time.csv
│   └── t_ods_log.csv
├── pipeline\
│   └── pipeline.py
├── output\
│   ├── BC_BIMIO_267_PRECOPY.xlsx
│   └── archive\
│       └── BIMIO_267_12Hour_Prevented_Daily_For_13.05.2026.xlsx
└── conversations\
    └── 2026-05-14_toad_poc_setup.md
```

---

## Sanitization Applied to XML Files

| Original | Replaced With |
|---|---|
| [Real person name] | Report Owner |
| MAXRPPRD | ORACLE_SERVER |
| MAXIMORO | ORACLE_SCHEMA |
| \\scotia\ / \\scotia.abcgroup.net\ | \\FILESERVER\ |
| ADaPt DEV | REDSHIFT_ENV |
| u_svcDEVtoad | svc_account |
| Ashford | DEPOT_A |
| Epsom | DEPOT_B |
| Godstone | DEPOT_C |
| Horsham | DEPOT_D |
| Orpington | DEPOT_E |
| Aldershot | DEPOT_F |
| Oxford | DEPOT_G |
| PooleIOW | DEPOT_H |
| Solent | DEPOT_I |
| HILLINGTON | DEPOT_K |
| PAISLEY | DEPOT_L |
| GSMR | METRIC_X |

---

## Local POC Stack

| Component | Tool | Cost |
|---|---|---|
| Source data | CSV files (simulating Oracle/Redshift) | Free |
| Pipeline logic | Python (pandas + openpyxl) | Free |
| Excel output | .xlsx via openpyxl | Free |
| ADF artifacts | JSON/ARM templates (next step) | Free |

---

## Next Steps
- Generate ADF ARM templates from pipeline logic
- Map Python pipeline steps to ADF activities
- Later: Azure SQL Server as target DB
- Later: AWS Glue equivalent
