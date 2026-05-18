# Config-Driven Email Distribution — 2026-05-14

## Summary
Replaced hardcoded email lists in the pipeline with a config table approach.
Email distribution is now managed in Azure SQL — no pipeline changes needed to add/remove recipients.

---

## Problem Solved
Email addresses were hardcoded in the Toad XML and replicated into the ADF pipeline.
This means any recipient change requires a developer to modify and redeploy the pipeline.

## Solution
Two new config tables in Azure SQL (`config` schema) store all report metadata and email distribution lists.
Pipeline reads from these tables at runtime — fully dynamic.

---

## Config Tables Design

### config.report
One row per report — stores report metadata.

```sql
report_id | report_name         | description                          | schedule | output_format | is_active
----------|---------------------|--------------------------------------|----------|---------------|----------
1         | BC_BIMIO_267_Daily  | BIMIO 267 - 12 Hour Prevented Daily  | Daily    | CSV           | Y
```

### config.report_email
Many rows per report — email distribution list.

```sql
id | report_id | email_address           | email_type | recipient_group | is_active
---|-----------|-------------------------|------------|-----------------|----------
1  | 1         | ops.depot_a@abc.co.uk   | TO         | OPERATIONS      | Y
2  | 1         | buin@abc.co.uk          | BCC        | BI_TEAM         | Y
3  | 1         | manager.name1@abc.co.uk | CC         | ALERT_ONLY      | Y
```

**email_type** values: `TO`, `CC`, `BCC`
**recipient_group** values: `OPERATIONS`, `BI_TEAM`, `ALERT_ONLY`

---

## Email Flow Per Pipeline Branch

| Branch | Email | TO | CC | BCC |
|---|---|---|---|---|
| ODS NOT refreshed | Alert email | OPERATIONS | ALERT_ONLY | — |
| ODS refreshed | Report email | OPERATIONS | ALERT_ONLY | BI_TEAM |
| ODS refreshed | Confirmation | BI_TEAM | — | — |

---

## Files Created / Updated

| File | Change |
|---|---|
| `sql_scripts/01_create_schemas.sql` | Added `config` schema |
| `sql_scripts/02_create_tables.sql` | Added `config.report` and `config.report_email` tables |
| `sql_scripts/03_load_sample_data.sql` | Added sample config data |
| `sample_data/config_report.csv` | New — report config sample data |
| `sample_data/config_report_email.csv` | New — email distribution sample data |
| `pipeline/pipeline.py` | Added `load_email_config()`, all email functions now config-driven |
| `adf_templates/datasets/DS_AzureSQL_Config.json` | New — config schema dataset |
| `adf_templates/pipelines/PL_BC_BIMIO_267_Daily.json` | Added 3 parallel email Lookup activities, dynamic email bodies |

---

## ADF Pipeline — Updated Activity Flow

```
Lookup_ODS_Refresh_Check
        ↓
SetVar_ReportDate
        ↓
Lookup_Ops_Email_List ──┐
Lookup_BI_Email_List  ──┤ (parallel — STRING_AGG queries)
Lookup_Alert_Email_List─┘
        ↓
If_ODS_Refreshed
    ├── FALSE (ODS not ready):
    │       Email_ODS_Not_Refreshed  (TO=OPERATIONS, CC=ALERT_ONLY — dynamic)
    └── TRUE (ODS ready):
            Copy_ReportData_To_Blob
            Copy_Archive_File
            Email_Report_To_Operations  (TO=OPERATIONS, CC=ALERT_ONLY, BCC=BI_TEAM — dynamic)
            Email_Confirmation_To_BI_Team  (TO=BI_TEAM — dynamic)
```

---

## ADF Email Lookup SQL (STRING_AGG)

```sql
-- Operations TO list
SELECT STRING_AGG(re.email_address, ';') AS email_list
FROM config.report_email re
JOIN config.report r ON re.report_id = r.report_id
WHERE r.report_name = 'BC_BIMIO_267_Daily'
  AND re.recipient_group = 'OPERATIONS'
  AND re.email_type = 'TO'
  AND re.is_active = 'Y'
  AND r.is_active = 'Y'

-- Same pattern for BI_TEAM (BCC) and ALERT_ONLY (CC)
```

---

## How to Manage Recipients (No Pipeline Changes Needed)

```sql
-- Add a new recipient
INSERT INTO config.report_email (report_id, email_address, email_type, recipient_group, is_active)
VALUES (1, 'newperson@abc.co.uk', 'TO', 'OPERATIONS', 'Y');

-- Remove a recipient (soft delete)
UPDATE config.report_email SET is_active = 'N'
WHERE email_address = 'oldperson@abc.co.uk' AND report_id = 1;

-- Add a new report
INSERT INTO config.report (report_name, description, schedule, output_format, is_active)
VALUES ('BC_BIMIO_268_Weekly', 'BIMIO 268 Weekly Report', 'Weekly', 'CSV', 'Y');
```

---

## Python Pipeline Output (verified running)
```
Loading email config...
  Operations TO  : ops.depot_a@abc.co.uk; ops.depot_b@abc.co.uk; ... (9 addresses)
  BI Team BCC    : buin@abc.co.uk; bi.support@abc.co.uk
  Alert CC       : manager.name1@abc.co.uk; manager.name2@abc.co.uk
...
Pipeline completed successfully.
```

---

## Next Steps
- Set up Azure subscription
- Create Azure SQL Server + Database
- Run SQL scripts 01 → 04
- Deploy ADF ARM template
- Set up Logic App for email
- Run and validate ADF pipeline
- AWS version after Azure POC proven
