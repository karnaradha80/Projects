# KT Step 1 — MAVIS DTC File Processing: End-to-End Walkthrough

## Sample File Being Processed

```
ZHV|DS0000IE16|D0010002|N|UPLD|R|EELC|20260320160032||||OPER|
026|1023527784227|F|
028|25P2083306|R|
030|01|20260316000000|78.4|||F|N|
ZPT|DS0000IE16|3||1|20260320160032|
```

**Flow type: D0010** (Meter Readings)

---

## System Architecture Overview

```
Caller
  │
  ▼
PRC_DTC_PROCESS_FILE_WRAPPER        ← Entry point wrapper (06_Procedures.sql)
  │
  ▼
PKG_DTC_PROCESSING.PRC_PROCESS_FILE  ← Orchestrator (PKG_DTC_PROCESSING.pkb)
  │
  ├─► PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2  ← Stage 1 + Stage 2 prep
  │       └─► MDQ_ETL_VALIDATION_CONFIG        ← JSON rules config
  │
  ├─► MDQ_ETL_FILE          ← File-level tracking record
  ├─► MDQ_ETL_AUDIT         ← Audit trail
  ├─► MDQ_ETL_ERROR         ← Error log
  │
  └─► PKG_DTC_D0010.PRC_PROCESS_FILE_V2  ← Flow-specific staging
          ├─► STAGE_D0010_026  (MPAN parent)
          ├─► STAGE_D0010_028  (Meter)
          └─► STAGE_D0010_030  (Meter Register Reading)
```

---

## Step-by-Step Execution

### ENTRY POINT — `PRC_DTC_PROCESS_FILE_WRAPPER` (`06_Procedures.sql`)

```sql
BEGIN
  Delete From DTC_PROCESSING_STATUS;
  p_result := PKG_DTC_PROCESSING.PRC_PROCESS_FILE(
      p_file_content,   -- The CLOB file content
      p_flow_type,      -- 'D0010'
      p_file_name,      -- e.g. 'DS0000IE16_D0010.txt'
      p_run_num         -- e.g. 1
  );
  insert into DTC_PROCESSING_STATUS Values (p_result);  -- saves 'STAGING' or 'REJECTED'
  Commit;
END;
```

- First clears the `DTC_PROCESSING_STATUS` table (single-row status indicator).
- Calls the main processing function and saves the result (`STAGING` or `REJECTED`) back to that table.
- This is what external callers (scripts, jobs) invoke.

---

### STEP 1 — Generate a unique File PK (`PKG_DTC_PROCESSING.pkb` line 209)

```sql
SELECT SEQ_MDQ_ETL_FILE.NEXTVAL INTO v_file_pk FROM DUAL;
```

- Pulls the next value from `SEQ_MDQ_ETL_FILE` sequence.
- This `v_file_pk` is used as the primary key for every record inserted during this file's processing — it ties audit rows, error rows, and staging rows all together.

---

### STEP 2 — Create Initial Audit Entry — status `RUNNING` (line 214)

```sql
PRC_CREATE_AUDIT(
  p_file_pk    => v_file_pk,
  p_job_name   => 'PKG_DTC_PROCESSING',
  p_parent_job => NULL,
  p_status     => 'RUNNING',
  p_audit_pk   => v_initial_audit_pk
);
COMMIT;
```

- Inserts a row into `MDQ_ETL_AUDIT` with status `RUNNING`, start time = now, all counts = 0.
- Commits immediately so the row is visible even if a crash happens later — useful for ops monitoring.
- `v_initial_audit_pk` is stored to update this row at the end.

---

### STEP 2A — Validate mandatory inputs (line 226)

```sql
IF p_flow_type IS NULL OR LENGTH(TRIM(p_flow_type)) = 0 THEN ...
```

- Rejects immediately if `p_flow_type` is blank/null.
- For our sample: `p_flow_type = 'D0010'` → passes.

---

### STEP 3 — File Validation (Stage 1 + Stage 2 prep) via `PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2` (line 238)

This is the most important function call. It:

1. **Splits the CLOB into lines** (`FN_SPLIT_FILE_LINES`) — handles both Unix `\n` and Windows `\r\n` endings:
   ```
   Line 1: ZHV|DS0000IE16|D0010002|N|UPLD|R|EELC|20260320160032||||OPER|
   Line 2: 026|1023527784227|F|
   Line 3: 028|25P2083306|R|
   Line 4: 030|01|20260316000000|78.4|||F|N|
   Line 5: ZPT|DS0000IE16|3||1|20260320160032|
   ```

2. **Loads active JSON config** from `MDQ_ETL_VALIDATION_CONFIG` where `MEVC_FLOW_TYPE = 'D0010'` and `MEVC_ACTIVE_YN = 'Y'`. The config defines which fields are mandatory, their lengths, data types, and patterns for each group.

3. **Stage 1 Validation** (`FN_VALIDATE_STAGE1`) — file-level critical checks:

   | Check | What it does | Our file result |
   |---|---|---|
   | Header present | First line starts with `ZHV` | ✅ Pass |
   | Footer present | Last line starts with `ZPT` | ✅ Pass |
   | Header fields | Parses `ZHV` line into `t_header_data` | ✅ Extracts all fields |
   | Footer fields | Parses `ZPT` line into `t_footer_data` | ✅ Extracts counts |
   | Record count match | Footer says `3`, actual data lines = 3 | ✅ Match |
   | Flow count match | Footer says `1`, one `026` parent group | ✅ Match |

   **Header parsed values** (from `ZHV|DS0000IE16|D0010002|N|UPLD|R|EELC|20260320160032||||OPER|`):
   | Field | Position | Value |
   |---|---|---|
   | `file_identifier` | 1 | `DS0000IE16` |
   | `flow_name` | 2 | `D0010002` |
   | `flow_type` (derived) | — | `D0010` |
   | `flow_version` (derived) | — | `002` |
   | `src_mp_role` | 3 | `N` |
   | `src_mp_id` | 4 | `UPLD` |
   | `dstn_mp_role` | 5 | `R` |
   | `dstn_mp_id` | 6 | `EELC` |
   | `data_timestamp` | 7 | `20260320160032` |
   | `network_id` | 11 | `OPER` |

   **Footer parsed values** (from `ZPT|DS0000IE16|3||1|20260320160032|`):
   | Field | Position | Value |
   |---|---|---|
   | `file_identifier` | 1 | `DS0000IE16` |
   | `record_count` | 2 | `3` |
   | `checksum` | 3 | *(empty)* |
   | `flow_count` | 4 | `1` |
   | `data_timestamp` | 5 | `20260320160032` |

   If Stage 1 fails (e.g. record count mismatch) → `stage1_passed = FALSE` → file gets `REJECTED` immediately, no staging occurs.

   For our sample → **Stage 1 passes**.

4. The pre-split lines array `v_split_lines` is returned to the caller so Stage 2 / the flow package does NOT need to re-split the CLOB.

---

### STEP 3A — Look up Network ID (line 259)

```sql
SELECT nta_mpan_cd INTO v_network_id
FROM MDQ_APP_NTWKAREA_REF
WHERE nta_term = 'EELC';   -- dstn_mp_id from header
```

- Looks up `EELC` in `MDQ_APP_NTWKAREA_REF.NTA_TERM`.
- `EELC` maps to `NTA_MPAN_CD = '10'` (Eastern Power Networks).
- `v_network_id = '10'` — stored into `MDQ_ETL_FILE.FIL_NETWORK_ID`.

---

### STEP 4 — Insert File Tracking Record into `MDQ_ETL_FILE` (line 274)

A row is inserted with all header/footer data extracted in Step 3:

| Column | Value | Source |
|---|---|---|
| `FIL_FILE_PK` | `<seq value>` | `SEQ_MDQ_ETL_FILE` |
| `FIL_FILE_NAME` | `'DS0000IE16_D0010.txt'` | `p_file_name` (truncated to 40 chars if needed) |
| `FIL_FILE_TYPE` | `'D0010'` | From header `flow_type` |
| `FIL_FLOW_VERSION` | `'002'` | From header `flow_version` |
| `FIL_SRC_MP_ROLE` | `'N'` | Header position 3 |
| `FIL_SRC_MP_ID` | `'UPLD'` | Header position 4 |
| `FIL_DSTN_MP_ROLE` | `'R'` | Header position 5 |
| `FIL_DSTN_MP_ID` | `'EELC'` | Header position 6 |
| `FIL_DATA_DT` | `20-MAR-2026 16:00:32` | Header timestamp converted to DATE |
| `FIL_NETWORK_ID` | `'10'` | From `MDQ_APP_NTWKAREA_REF` lookup |
| `FIL_INP_OUT_IND` | `'I'` | Hardcoded (Inbound) |
| `FIL_REC_CNT` | `3` | Footer `record_count` |
| `FIL_LOAD_STUS` | `'STAGING'` | Validation result status (initial) |
| `FIL_STG_LOAD_RUN_NUM` | `p_run_num` | Passed in by caller |
| `FIL_FLOW_CNT` | `1` | Footer `flow_count` |
| `FIL_MP_FILE_ID` | `'DS0000IE16'` | Header `file_identifier` |
| `FIL_CR_DTTM` | `SYSDATE` | Current date |

> **Note on overflow protection**: All fields have `CASE WHEN LENGTH(...) > max THEN NULL ELSE value END` guards. If the file name exceeds 40 characters, the truncated value is stored, an error is logged, and the file is immediately rejected.

---

### STEP 5 — Log Stage 1 Errors (line 354)

Only runs if **Stage 1 failed**. Inserts each error from `v_validation_result.errors` into `MDQ_ETL_ERROR`.

For our sample → Stage 1 passed, so **no errors are logged here**.

---

### STEP 6 — Flow-Specific Staging via `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` (line 383)

Because Stage 1 passed:

#### 6a — Create Child Audit Entry — status `RUNNING`
```sql
PRC_CREATE_AUDIT(
  p_job_name   => 'PKG_DTC_D0010',
  p_parent_job => 'PKG_DTC_PROCESSING',
  ...
);
```
A second audit row is created. This one tracks the D0010-specific staging work.

#### 6b — Inside `PKG_DTC_D0010.PRC_PROCESS_FILE_V2`

The function receives:
- `p_file_pk` — file PK from Step 1
- `p_lines` — pre-split lines from Step 3 (no re-splitting needed)
- `p_stage1_data` — already-parsed header/footer/counts

It loads the JSON config and builds a **field config cache** (pre-parses all group definitions once, so validation doesn't re-parse JSON for every single line).

It then iterates lines 2 to N-1 (skipping header line 1 and footer last line):

---

#### Processing Line 2: `026|1023527784227|F|`

- `v_group_id = '026'` — this is a new parent group boundary
- Hierarchy flags reset: `v_026_valid = TRUE`, `v_028_valid = FALSE`, `v_030_valid = FALSE`
- **Validation**: checks MPAN `1023527784227` — 13-digit number, mandatory → ✅
- **Validation**: BSC Validation Status `F` → ✅
- **Insert** → `FN_INSERT_GROUP_026`:
  ```sql
  INSERT INTO STAGE_D0010_026 (STG_026_PK, STG_026_FILE_PK, STG_026_FILE_REC_NUM,
                                STG_026_MPAN, STG_026_BSC_VLDN_STATUS)
  VALUES (STG_D0010_026_SEQ.NEXTVAL, <file_pk>, 1, 1023527784227, 'F')
  RETURNING STG_026_PK INTO v_parent_026_pk;
  ```
- `staged_rec_count += 1`, `staged_flow_count += 1`

---

#### Processing Line 3: `028|25P2083306|R|`

- `v_group_id = '028'` — child of 026
- **Validation**: Meter ID `25P2083306` (alphanumeric, up to 10 chars) → ✅
- **Validation**: Reading Type `R` → ✅
- `v_026_valid = TRUE` → parent is valid, so insert is allowed
- **Insert** → `FN_INSERT_GROUP_028`:
  ```sql
  INSERT INTO STAGE_D0010_028 (STG_028_PK, STG_028_026_PK, STG_028_FILE_REC_NUM,
                                STG_028_MTR_ID, STG_028_READING_TYPE)
  VALUES (STG_D0010_028_SEQ.NEXTVAL, <026_pk>, 2, '25P2083306', 'R')
  RETURNING STG_028_PK INTO v_parent_028_pk;
  ```
- `v_028_valid = TRUE`
- `staged_rec_count += 1`

---

#### Processing Line 4: `030|01|20260316000000|78.4|||F|N|`

- `v_group_id = '030'` — child of 028
- **Validation** of each field:
  | Field position | Value | Check |
  |---|---|---|
  | `01` (Register ID) | mandatory, max 2 chars | ✅ |
  | `20260316000000` (Read DateTime) | DATETIME format `YYYYMMDDHH24MISS` | ✅ → 16-MAR-2026 |
  | `78.4` (Read Value) | numeric | ✅ |
  | *(empty)* (MD Reset DateTime) | optional | ✅ |
  | *(empty)* (MD Reset Number) | optional | ✅ |
  | `F` (Read Indicator) | mandatory, 1 char | ✅ |
  | `N` (Reading Method) | mandatory, 1 char | ✅ |
- `v_026_valid = TRUE` and `v_028_valid = TRUE` → insert allowed
- **Insert** → `FN_INSERT_GROUP_030`:
  ```sql
  INSERT INTO STAGE_D0010_030 (STG_030_PK, STG_030_028_PK, STG_030_FILE_REC_NUM,
    STG_030_MTR_REG_ID, STG_030_READ_DTTM, STG_030_READ_VAL,
    STG_030_MD_RESET_DTTM, STG_030_MD_RESET_NUM, STG_030_READ_IND, STG_030_READING_MTHD)
  VALUES (STG_D0010_030_SEQ.NEXTVAL, <028_pk>, 3, '01',
    TO_DATE('20260316000000','YYYYMMDDHH24MISS'), 78.4, NULL, NULL, 'F', 'N')
  RETURNING STG_030_PK INTO v_parent_030_pk;
  ```
- `v_030_valid = TRUE`
- `staged_rec_count += 1`

---

#### Final Status from `PRC_PROCESS_FILE_V2`

- `staged_flow_count = 1` → `p_result.status = 'STAGING'`
- `staged_rec_count = 3`, `rejected_rec_count = 0`, `rejected_flow_count = 0`

---

#### Back in `PKG_DTC_PROCESSING` — Determine final status (line 447)

```
rejected_flow_count = 0 AND rejected_rec_count = 0
  → v_final_status = 'STAGING'  (from v_staging_result.status)
  → v_validation_audit_status = 'SUCCESSFUL'
```

The **child audit** (`PKG_DTC_D0010`) is updated:
- `AUD_JOB_STATUS = 'SUCCESSFUL'`
- `AUD_REC_PROC_CNT = 3`, `AUD_REC_SUCC_CNT = 3`, fail/rej = 0

---

### STEP 7 — Update Initial Audit with Final Status (line 539)

```
v_final_status = 'STAGING'
  → v_initial_audit_status = 'SUCCESSFUL'
```

The **initial audit** (`PKG_DTC_PROCESSING`) row is updated:
- `AUD_JOB_END_DTTM = now`
- `AUD_JOB_STATUS = 'SUCCESSFUL'`
- `AUD_REC_PROC_CNT = 3` (from footer), `AUD_REC_SUCC_CNT = 3`

---

### STEP 8 — Update `MDQ_ETL_FILE` with Final Counts (line 551)

```sql
UPDATE MDQ_ETL_FILE
SET FIL_LOAD_STUS     = 'STAGING',
    FIL_STG_LOAD_DTTM = SYSTIMESTAMP,
    FIL_STG_REC_CNT   = 3,
    FIL_STG_FLOW_CNT  = 1,
    FIL_STG_ERR_REC_CNT  = 0,
    FIL_STG_ERR_FLOW_CNT = 0,
    FIL_STG_REJ_REC_CNT  = 0,
    FIL_STG_REJ_FLOW_CNT = 0
WHERE FIL_FILE_PK = <file_pk>;
COMMIT;
```

---

### STEP 9 — Return `'STAGING'`

The wrapper stores `'STAGING'` in `DTC_PROCESSING_STATUS`.

---

## Final Database State After Processing

### `MDQ_ETL_FILE` — 1 row
| Column | Value |
|---|---|
| `FIL_FILE_TYPE` | `D0010` |
| `FIL_LOAD_STUS` | `STAGING` |
| `FIL_DSTN_MP_ID` | `EELC` |
| `FIL_NETWORK_ID` | `10` |
| `FIL_REC_CNT` | `3` |
| `FIL_FLOW_CNT` | `1` |
| `FIL_STG_REC_CNT` | `3` |
| `FIL_STG_REJ_REC_CNT` | `0` |

### `MDQ_ETL_AUDIT` — 2 rows
| `AUD_JOB_NAME` | `AUD_JOB_STATUS` | `AUD_REC_SUCC_CNT` |
|---|---|---|
| `PKG_DTC_PROCESSING` | `SUCCESSFUL` | `3` |
| `PKG_DTC_D0010` | `SUCCESSFUL` | `3` |

### `STAGE_D0010_026` — 1 row
| `STG_026_MPAN` | `STG_026_BSC_VLDN_STATUS` |
|---|---|
| `1023527784227` | `F` |

### `STAGE_D0010_028` — 1 row (linked to 026 via FK)
| `STG_028_MTR_ID` | `STG_028_READING_TYPE` |
|---|---|
| `25P2083306` | `R` |

### `STAGE_D0010_030` — 1 row (linked to 028 via FK)
| `STG_030_MTR_REG_ID` | `STG_030_READ_DTTM` | `STG_030_READ_VAL` | `STG_030_READ_IND` | `STG_030_READING_MTHD` |
|---|---|---|---|---|
| `01` | `16-MAR-2026` | `78.4` | `F` | `N` |

### `MDQ_ETL_ERROR` — 0 rows (clean file)

---

## What Causes `REJECTED` Instead of `STAGING`?

| Scenario | What fails | Result |
|---|---|---|
| Record count in footer doesn't match actual data lines | Stage 1 | `REJECTED` (whole file) |
| Header missing or malformed | Stage 1 | `REJECTED` |
| Blank `p_flow_type` passed | Input validation | `REJECTED` |
| File name > 40 chars | Overflow check | `REJECTED` |
| MPAN in group 026 is not a 13-digit number | Stage 2 (group level) | That flow group `REJECTED`, others can still stage |
| 028 line invalid (bad meter ID) | Stage 2 | 028 + all its children (030, 032, 033) rejected |
| 030 line invalid | Stage 2 | Only 030 and its children (032, 033) rejected |
| Exception in staging | `WHEN OTHERS` | `ROLLBACK`, file marked `REJECTED` |

---

## Key Tables Quick Reference

| Table | Purpose |
|---|---|
| `MDQ_ETL_VALIDATION_CONFIG` | JSON config rules for each flow type (D0010, D0150, D0302) |
| `MDQ_APP_NTWKAREA_REF` | Maps recipient IDs (e.g. `EELC`) to network MPAN codes |
| `MDQ_APP_MSG_REF` | Error message templates (e.g. `ERR8013`, `ERR8042`) |
| `MDQ_ETL_FILE` | One row per file processed — tracks status and counts |
| `MDQ_ETL_AUDIT` | Two rows per file — overall job + flow-specific job |
| `MDQ_ETL_ERROR` | One row per validation/staging error |
| `STAGE_D0010_026/028/030` | Staged D0010 data — hierarchical (026 → 028 → 030) |
| `DTC_PROCESSING_STATUS` | Single-row table holding last run result (`STAGING`/`REJECTED`) |

---

## Sequences Used

| Sequence | Used For |
|---|---|
| `SEQ_MDQ_ETL_FILE` | `FIL_FILE_PK` |
| `SEQ_AUDIT` | `AUD_PK` |
| `SEQ_ERROR` | `ERR_PK` |
| `STG_D0010_026_SEQ` | `STG_026_PK` |
| `STG_D0010_028_SEQ` | `STG_028_PK` |
| `STG_D0010_030_SEQ` | `STG_030_PK` |
