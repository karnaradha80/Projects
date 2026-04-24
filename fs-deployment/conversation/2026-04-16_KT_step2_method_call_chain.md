# KT Step 2 — Complete Method Call Chain: Start to End

## Call Chain Tree

```
PRC_DTC_PROCESS_FILE_WRAPPER                          [06_Procedures.sql]
  └── PKG_DTC_PROCESSING.PRC_PROCESS_FILE             [PKG_DTC_PROCESSING.pkb]
        ├── SEQ_MDQ_ETL_FILE.NEXTVAL
        ├── PRC_CREATE_AUDIT                           [private]
        │     └── SEQ_AUDIT.NEXTVAL
        ├── PKG_DTC_COMMON.FN_FORMAT_ERROR             [if flow_type null]
        ├── PRC_LOG_ERROR                              [if flow_type null]
        ├── PRC_UPDATE_AUDIT                           [if flow_type null]
        ├── PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2
        │     ├── PKG_DTC_COMMON.FN_SPLIT_FILE_LINES
        │     ├── PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG
        │     └── PKG_DTC_VALIDATION.FN_VALIDATE_STAGE1
        │           ├── PKG_DTC_VALIDATION.FN_PARSE_HEADER
        │           │     ├── PKG_DTC_COMMON.FN_FORMAT_ERROR [on errors]
        │           │     └── ADD_ERROR                      [on errors]
        │           ├── PKG_DTC_VALIDATION.FN_VALIDATE_HEADER
        │           │     ├── FN_VALIDATE_FIELD              [per field]
        │           │     │     └── PKG_DTC_COMMON.FN_FORMAT_ERROR
        │           │     └── ADD_ERROR                      [on errors]
        │           ├── PKG_DTC_VALIDATION.FN_PARSE_FOOTER
        │           │     ├── PKG_DTC_COMMON.FN_FORMAT_ERROR [on errors]
        │           │     └── ADD_ERROR                      [on errors]
        │           ├── PKG_DTC_VALIDATION.FN_VALIDATE_FOOTER
        │           │     ├── FN_VALIDATE_FIELD              [per field]
        │           │     │     └── PKG_DTC_COMMON.FN_FORMAT_ERROR
        │           │     └── ADD_ERROR                      [on errors]
        │           └── ADD_ERROR                            [on count mismatch]
        ├── MDQ_APP_NTWKAREA_REF lookup (inline SQL)
        ├── INSERT MDQ_ETL_FILE
        ├── PKG_DTC_COMMON.FN_FORMAT_ERROR             [if file name overflow]
        ├── PRC_LOG_ERROR                              [if Stage 1 errors]
        │     └── SEQ_ERROR.NEXTVAL
        ├── PRC_CREATE_AUDIT                           [child audit, if Stage 1 passed]
        ├── PKG_DTC_D0010.PRC_PROCESS_FILE_V2          [if flow_type = D0010]
        │     ├── PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG
        │     ├── PKG_DTC_VALIDATION.FN_BUILD_GROUP_CACHE
        │     └── [loop per data line]
        │           ├── PKG_DTC_COMMON.FN_PARSE_LINE
        │           ├── PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE  [cache overload]
        │           │     ├── FN_VALIDATE_FIELD (t_field_config overload)
        │           │     │     └── PKG_DTC_COMMON.FN_FORMAT_ERROR
        │           │     └── ADD_ERROR
        │           ├── PKG_DTC_D0010.FN_INSERT_GROUP_026  [if group=026, valid]
        │           │     └── INSERT STAGE_D0010_026
        │           ├── PKG_DTC_D0010.PRC_INSERT_GROUP_027 [if group=027, valid]
        │           │     └── INSERT STAGE_D0010_027
        │           ├── PKG_DTC_D0010.FN_INSERT_GROUP_028  [if group=028, valid]
        │           │     └── INSERT STAGE_D0010_028
        │           ├── PKG_DTC_D0010.PRC_INSERT_GROUP_029 [if group=029, valid]
        │           │     └── INSERT STAGE_D0010_029
        │           ├── PKG_DTC_D0010.FN_INSERT_GROUP_030  [if group=030, valid]
        │           │     └── INSERT STAGE_D0010_030
        │           ├── PKG_DTC_D0010.PRC_INSERT_GROUP_032 [if group=032, valid]
        │           │     └── INSERT STAGE_D0010_032
        │           └── PKG_DTC_D0010.PRC_INSERT_GROUP_033 [if group=033, valid]
        │                 └── INSERT STAGE_D0010_033
        ├── INSERT MDQ_ETL_ERROR                       [staging errors, if any]
        ├── PRC_UPDATE_AUDIT                           [child audit]
        ├── PRC_UPDATE_AUDIT                           [initial audit]
        ├── UPDATE MDQ_ETL_FILE                        [final counts + status]
        └── RETURN 'STAGING' or 'REJECTED'
```

---

## Every Method — Signature + Purpose

---

### 1. `PRC_DTC_PROCESS_FILE_WRAPPER`
**Package**: Standalone procedure (`06_Procedures.sql`)

```sql
PROCEDURE PRC_DTC_PROCESS_FILE_WRAPPER (
    p_file_content IN CLOB,      -- Full file content as CLOB
    p_flow_type    IN VARCHAR2,  -- Flow type: 'D0010' or 'D0150'
    p_file_name    IN VARCHAR2,  -- Original file name for tracking
    p_run_num      IN NUMBER     -- Run number for audit
)
```

**What it does**:
- Entry point for all callers (scripts, jobs, UI).
- Deletes the previous status from `DTC_PROCESSING_STATUS`.
- Calls `PKG_DTC_PROCESSING.PRC_PROCESS_FILE` and stores the returned `'STAGING'` or `'REJECTED'` back into `DTC_PROCESSING_STATUS`.
- Wraps the call in a `WHEN OTHERS` block — stores `'ERROR'` if the main function throws.

---

### 2. `PKG_DTC_PROCESSING.PRC_PROCESS_FILE`
**Package**: `PKG_DTC_PROCESSING` (body: `PKG_DTC_PROCESSING.pkb`)

```sql
FUNCTION PRC_PROCESS_FILE(
    p_file_content IN CLOB,      -- Full file content as CLOB
    p_flow_type    IN VARCHAR2,  -- 'D0010' or 'D0150'
    p_file_name    IN VARCHAR2,  -- Original file name
    p_run_num      IN NUMBER     -- Run number
) RETURN VARCHAR2                -- Returns 'STAGING' or 'REJECTED'
```

**What it does**:
- The main orchestrator. Executes all 9 steps end-to-end.
- Generates `v_file_pk`, creates audit, validates, stages, updates audit and file record, returns final status.
- All private helpers (`PRC_CREATE_AUDIT`, `PRC_UPDATE_AUDIT`, `PRC_LOG_ERROR`) live inside this package.

---

### 3. `PRC_CREATE_AUDIT` *(private)*
**Package**: `PKG_DTC_PROCESSING`

```sql
PROCEDURE PRC_CREATE_AUDIT(
    p_file_pk    IN  NUMBER,      -- FK to MDQ_ETL_FILE
    p_job_name   IN  VARCHAR2,    -- 'PKG_DTC_PROCESSING' or 'PKG_DTC_D0010'
    p_parent_job IN  VARCHAR2,    -- NULL for initial; 'PKG_DTC_PROCESSING' for child
    p_status     IN  VARCHAR2,    -- Always 'RUNNING' at create time
    p_audit_pk   OUT NUMBER       -- Returns the new AUD_PK (to update later)
)
```

**What it does**:
- Inserts one row into `MDQ_ETL_AUDIT` with status `RUNNING`, start time = `SYSTIMESTAMP`, all counts = 0.
- Returns `p_audit_pk` so the caller can update this same row when done.
- Called twice per file: once for the overall job, once for the flow-specific job (after Stage 1 passes).
- Uses `SEQ_AUDIT.NEXTVAL` for `AUD_PK`.

---

### 4. `PRC_UPDATE_AUDIT` *(private)*
**Package**: `PKG_DTC_PROCESSING`

```sql
PROCEDURE PRC_UPDATE_AUDIT(
    p_audit_pk     IN NUMBER,           -- Which audit row to update
    p_status       IN VARCHAR2,         -- Final status: SUCCESSFUL / WARNING / ERROR / ABORTED
    p_rec_proc_cnt IN NUMBER DEFAULT 0, -- Total records processed
    p_rec_succ_cnt IN NUMBER DEFAULT 0, -- Successfully staged records
    p_rec_fail_cnt IN NUMBER DEFAULT 0, -- Failed records
    p_rec_rej_cnt  IN NUMBER DEFAULT 0  -- Rejected records
)
```

**What it does**:
- Updates an existing `MDQ_ETL_AUDIT` row with end time, final status, and all record counts.
- Called at the end of each job phase.
- Status values:
  - `SUCCESSFUL` — all records staged cleanly
  - `WARNING` — partial rejection (some staged, some rejected)
  - `ERROR` — all records rejected
  - `ABORTED` — unhandled critical exception

---

### 5. `PRC_LOG_ERROR` *(private)*
**Package**: `PKG_DTC_PROCESSING`

```sql
PROCEDURE PRC_LOG_ERROR(
    p_file_pk     IN NUMBER,             -- FK to MDQ_ETL_FILE
    p_row_num     IN NUMBER,             -- Line number in file that caused error
    p_error_msg   IN VARCHAR2,           -- Human-readable error message
    p_field_name  IN VARCHAR2 DEFAULT NULL,  -- Which field failed
    p_field_value IN VARCHAR2 DEFAULT NULL   -- What value caused the failure
)
```

**What it does**:
- Inserts one row into `MDQ_ETL_ERROR` for each error.
- Uses `SEQ_ERROR.NEXTVAL` for `ERR_PK`.
- Applies `SUBSTR` overflow protection: field name truncated to 100 chars, field value to 500 chars.
- Called for: missing flow type, file name too long, validation exceptions, staging exceptions.

---

### 6. `PKG_DTC_COMMON.FN_SPLIT_FILE_LINES`
**Package**: `PKG_DTC_COMMON` (body: `PKG_DTC_COMMON.pkb`)

```sql
FUNCTION FN_SPLIT_FILE_LINES(
    p_file_content IN CLOB          -- The raw file CLOB
) RETURN DBMS_SQL.VARCHAR2A          -- Indexed array of lines (1-based)
```

**What it does**:
- Reads the CLOB in 32767-byte chunks using `DBMS_LOB.READ`.
- Splits on `CHR(10)` (Unix newline).
- Strips `CHR(13)` (carriage return) from line endings — handles both Unix `\n` and Windows `\r\n`.
- Skips blank lines.
- Returns a `DBMS_SQL.VARCHAR2A` array where index 1 = header line, last index = footer line.
- Called **once** by `FN_VALIDATE_FILE_V2`; the array is reused for validation AND staging — avoiding double splitting.

---

### 7. `PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG`
**Package**: `PKG_DTC_VALIDATION` (body: `PKG_DTC_VALIDATION_v2_complete.pkb`)

```sql
FUNCTION FN_GET_ACTIVE_CONFIG(
    p_flow_type IN VARCHAR2    -- 'D0010', 'D0150', 'D0302'
) RETURN CLOB                  -- JSON config CLOB, or NULL if not found
```

**What it does**:
- Queries `MDQ_ETL_VALIDATION_CONFIG` for the latest active config:
  ```sql
  WHERE MEVC_FLOW_TYPE = p_flow_type AND MEVC_ACTIVE_YN = 'Y'
  ORDER BY MEVC_CONFIG_VERSION DESC
  ```
- Returns the `MEVC_CONFIG_JSON` CLOB.
- Returns `NULL` if no active config found (triggers `ERR8003` error upstream).
- Called twice: once in `FN_VALIDATE_FILE_V2` and once in `PRC_PROCESS_FILE_V2`.

---

### 8. `PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_VALIDATE_FILE_V2(
    p_file_content IN  CLOB,                       -- Raw file CLOB
    p_flow_type    IN  VARCHAR2,                   -- 'D0010' or 'D0150'
    p_result       OUT t_file_validation_result,   -- Full result record (status, counts, errors, header/footer data, parent group ranges)
    p_lines        OUT DBMS_SQL.VARCHAR2A           -- Pre-split lines (reused by flow packages)
) RETURN BOOLEAN                                   -- TRUE = Stage 1 passed; FALSE = Stage 1 failed
```

**What it does**:
- Top-level validation entry point.
- Calls `FN_SPLIT_FILE_LINES` → splits CLOB into lines.
- Calls `FN_GET_ACTIVE_CONFIG` → loads JSON rules.
- Calls `FN_VALIDATE_STAGE1` → critical file-level validation.
- Populates `p_result` with all parsed data, status, and counts.
- Returns the pre-split `p_lines` array so `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` does NOT re-split.

---

### 9. `PKG_DTC_VALIDATION.FN_VALIDATE_STAGE1`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_VALIDATE_STAGE1(
    p_lines            IN  DBMS_SQL.VARCHAR2A,   -- Pre-split file lines
    p_config_json      IN  CLOB,                 -- Active JSON config
    p_flow_type        IN  VARCHAR2,             -- Flow type
    p_header_data      OUT t_header_data,        -- Parsed header fields
    p_footer_data      OUT t_footer_data,        -- Parsed footer fields
    p_total_rec_count  OUT NUMBER,               -- Actual data line count
    p_total_flow_count OUT NUMBER,               -- Actual parent group count
    p_errors           OUT t_validation_errors   -- Any Stage 1 errors
) RETURN BOOLEAN                                  -- TRUE = pass; FALSE = fail (file rejected)
```

**What it does**:
- Calls `FN_PARSE_HEADER` → extracts all header field values into `t_header_data`.
- Calls `FN_VALIDATE_HEADER` → checks header fields against JSON config rules (mandatory, length, pattern).
- Calls `FN_PARSE_FOOTER` → extracts all footer field values into `t_footer_data`.
- Calls `FN_VALIDATE_FOOTER` → checks footer fields + record count match.
- Counts actual data lines (`p_lines.COUNT - 2`) and compares to footer's `record_count`.
- Counts parent group lines (lines starting with the parent group ID) and compares to footer's `flow_count`.
- If ANY Stage 1 check fails → returns `FALSE` → entire file is REJECTED, no staging occurs.

---

### 10. `PKG_DTC_VALIDATION.FN_PARSE_HEADER`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_PARSE_HEADER(
    p_header_line  IN  VARCHAR2,              -- The ZHV line
    p_config_json  IN  CLOB,                  -- Active JSON config
    p_header_data  OUT t_header_data,         -- Populated header record
    p_errors       OUT t_validation_errors    -- Parse errors
) RETURN BOOLEAN
```

**What it does**:
- Splits the `ZHV` line by `|` delimiter.
- Extracts each field by position into the `t_header_data` record:
  | Position | Field in `t_header_data` |
  |---|---|
  | 1 (always `ZHV`) | checked against config identifier |
  | 2 | `file_identifier` |
  | 3 | `flow_name` → also derives `flow_type` (chars 1-5) and `flow_version` (chars 6-8) |
  | 4 | `src_mp_role` |
  | 5 | `src_mp_id` |
  | 6 | `dstn_mp_role` |
  | 7 | `dstn_mp_id` |
  | 8 | `data_timestamp` → also converted to `data_dt` (DATE) |
  | 10 | `inp_out_ind` (optional) |
  | 12 | `network_id` (optional) |
- Each assignment is wrapped in its own `BEGIN/EXCEPTION` block to catch buffer overflow.

---

### 11. `PKG_DTC_VALIDATION.FN_PARSE_FOOTER`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_PARSE_FOOTER(
    p_footer_line  IN  VARCHAR2,              -- The ZPT line
    p_config_json  IN  CLOB,                  -- Active JSON config
    p_footer_data  OUT t_footer_data,         -- Populated footer record
    p_errors       OUT t_validation_errors    -- Parse errors
) RETURN BOOLEAN
```

**What it does**:
- Splits the `ZPT` line by `|` delimiter.
- Extracts each field into `t_footer_data`:
  | Position | Field in `t_footer_data` |
  |---|---|
  | 1 (always `ZPT`) | checked against config identifier |
  | 2 | `file_identifier` |
  | 3 | `record_count` (converted to NUMBER) |
  | 4 | `checksum` (optional) |
  | 5 | `flow_count` (converted to NUMBER) |
  | 6 | `data_timestamp` |

---

### 12. `PKG_DTC_VALIDATION.FN_VALIDATE_HEADER`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_VALIDATE_HEADER(
    p_header_line  IN  VARCHAR2,              -- The ZHV line
    p_config_json  IN  CLOB,                  -- Active JSON config
    p_errors       OUT t_validation_errors    -- Errors found
) RETURN BOOLEAN
```

**What it does**:
- Reads the `header.fields` array from JSON config.
- For each configured field, calls `FN_VALIDATE_FIELD` with the corresponding value from the header line.
- Validates: mandatory presence, min/max length, data type, pattern (e.g. recipient ID must match `^(LOND|SEEB|EELC)$`).
- Reports errors via `ADD_ERROR`.

---

### 13. `PKG_DTC_VALIDATION.FN_VALIDATE_FOOTER`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_VALIDATE_FOOTER(
    p_footer_line    IN  VARCHAR2,              -- The ZPT line
    p_config_json    IN  CLOB,                  -- Active JSON config
    p_expected_count IN  NUMBER,                -- Expected data line count
    p_errors         OUT t_validation_errors    -- Errors found
) RETURN BOOLEAN
```

**What it does**:
- Validates footer fields against JSON config rules.
- Specifically checks `recordCount` field: compares footer value against `p_expected_count` (actual number of data lines).
- If mismatch → adds `ERR8024` error → Stage 1 fails.

---

### 14. `PKG_DTC_VALIDATION.FN_VALIDATE_FIELD` *(two overloads)*
**Package**: `PKG_DTC_VALIDATION`

**Overload A — JSON object config** (used in header/footer/legacy validation):
```sql
FUNCTION FN_VALIDATE_FIELD(
    p_field_value  IN  VARCHAR2,          -- The actual value from the file
    p_field_config IN  JSON_OBJECT_T,     -- Field config parsed from JSON
    p_field_name   OUT VARCHAR2,          -- Field name (from config)
    p_error_msg    OUT VARCHAR2           -- Error message if validation fails
) RETURN BOOLEAN
```

**Overload B — pre-processed `t_field_config` record** (used in inner loop via cache — no JSON per call):
```sql
FUNCTION FN_VALIDATE_FIELD(
    p_field_value  IN  VARCHAR2,          -- The actual value from the file
    p_field_config IN  t_field_config,    -- Pre-built config record (from cache)
    p_error_msg    OUT VARCHAR2           -- Error message if validation fails
) RETURN BOOLEAN
```

**What both do** (same logic):
1. **Mandatory check**: if `mandatory = TRUE` and value is empty → `ERR8013`
2. **Min length check**: if value length < `minLength` → `ERR8014`
3. **Max length check**: if value length > `maxLength` → `ERR8015`
4. **Data type `NUMBER`**: attempts `TO_NUMBER()` → `ERR8016` if fails; then checks `precision`/`scale` → `ERR8017/ERR8018/ERR8019`
5. **Data type `DATE`/`DATETIME`**: attempts `TO_DATE()` with format → `ERR8020` if fails
6. **Pattern**: `REGEXP_LIKE` check → `ERR8021` (or custom `patternErrorCode`)
- Overload B is the **hot path** — called on every data line in the inner loop. It skips JSON parsing and regex escape processing (already done by `FN_BUILD_GROUP_CACHE`).

---

### 15. `PKG_DTC_VALIDATION.FN_BUILD_GROUP_CACHE`
**Package**: `PKG_DTC_VALIDATION`

```sql
FUNCTION FN_BUILD_GROUP_CACHE(
    p_groups_array IN JSON_ARRAY_T         -- Pre-parsed JSON groups array
) RETURN t_field_config_cache              -- Associative array keyed by 'groupId~fieldIndex'
```

**What it does**:
- Called **once** before the data line loop in `PRC_PROCESS_FILE_V2`.
- Iterates all groups and all fields in the JSON config.
- Pre-processes each field into a `t_field_config` record:
  - Resolves regex escape sequences (`\\d` → `\d`) — so they are not re-processed per line.
  - Stores `mandatory`, `min_length`, `max_length`, `data_type`, `pattern`, `fmt`, `precision`, `scale`, `position`.
- Stores each record in the cache with key `groupId || '~' || fieldIndex` (e.g. `'026~0'`, `'026~1'`).
- Also stores a sentinel entry `groupId || '~#'` whose `.position` field = total field count for that group.
- **Performance reason**: eliminates JSON parsing + 6 REPLACE calls per field per line in the inner loop.

---

### 16. `PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE` *(three overloads)*
**Package**: `PKG_DTC_VALIDATION`

**Overload 1 — raw line + JSON config** (original, legacy):
```sql
FUNCTION FN_VALIDATE_GROUP_LINE(
    p_line         IN  VARCHAR2,
    p_group_id     IN  VARCHAR2,
    p_config_json  IN  CLOB,
    p_line_number  IN  NUMBER,
    p_errors       OUT t_validation_errors
) RETURN BOOLEAN
```

**Overload 2 — raw line + pre-parsed groups array**:
```sql
FUNCTION FN_VALIDATE_GROUP_LINE(
    p_line          IN  VARCHAR2,
    p_group_id      IN  VARCHAR2,
    p_groups_array  IN  JSON_ARRAY_T,
    p_line_number   IN  NUMBER,
    p_errors        OUT t_validation_errors
) RETURN BOOLEAN
```

**Overload 3 — pre-split fields + pre-built cache** *(used in the inner loop — fastest path)*:
```sql
FUNCTION FN_VALIDATE_GROUP_LINE(
    p_fields        IN  PKG_DTC_COMMON.t_fields_array,  -- Already parsed fields
    p_group_id      IN  VARCHAR2,
    p_group_cache   IN  t_field_config_cache,            -- Pre-built cache from FN_BUILD_GROUP_CACHE
    p_line_number   IN  NUMBER,
    p_errors        OUT t_validation_errors
) RETURN BOOLEAN
```

**What all three do**:
- Look up the group definition (by `group_id`) in the config/cache.
- Validate each field in the line against its config rules by calling `FN_VALIDATE_FIELD`.
- If group ID not found → `ERR8027` (unknown group) or `ERR8044` (empty group ID).
- Overload 3 is used in the production inner loop — no JSON, no REPLACE, no line splitting.

---

### 17. `ADD_ERROR` *(public helper)*
**Package**: `PKG_DTC_VALIDATION`

```sql
PROCEDURE ADD_ERROR(
    p_errors         IN OUT t_validation_errors,   -- Collection to append to (lazy-initialised)
    p_error_code     IN     VARCHAR2,              -- Error code (e.g. 'ERR8013')
    p_error_msg      IN     VARCHAR2,              -- Formatted message text
    p_line_number    IN     NUMBER  DEFAULT NULL,  -- File line number
    p_field_name     IN     VARCHAR2 DEFAULT NULL, -- Field that failed
    p_field_value    IN     VARCHAR2 DEFAULT NULL, -- Value that failed
    p_group_id       IN     VARCHAR2 DEFAULT NULL, -- Group containing the field
    p_field_position IN     NUMBER  DEFAULT NULL   -- Position in pipe-delimited line
)
```

**What it does**:
- Appends one `t_validation_error` record to the `p_errors` collection.
- If `p_errors IS NULL` → initialises it first (lazy init — avoids unnecessary allocations on clean lines).
- If `p_field_position` is provided → stores `ERR_FILE_COL` as `'fieldName - position'` format.
- Used everywhere an error needs to be recorded: header, footer, group line validation.

---

### 18. `PKG_DTC_COMMON.FN_PARSE_LINE`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_PARSE_LINE(
    p_line IN VARCHAR2              -- One pipe-delimited line
) RETURN t_fields_array             -- Associative array, 1-based: fields(1)=groupId, fields(2)=field1, etc.
```

**What it does**:
- Splits a single pipe-delimited line into an indexed array of field values.
- Handles empty fields (two consecutive `||` delimiters → empty string stored).
- Handles trailing delimiter (last field after final `|` → empty string stored).
- Returns `t_fields_array` (associative array indexed by `PLS_INTEGER`).
- Called **per data line** in `PRC_PROCESS_FILE_V2` — result is reused for both validation and insert.

---

### 19. `PKG_DTC_COMMON.FN_GET_GROUP_ID`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_GET_GROUP_ID(
    p_line IN VARCHAR2    -- One pipe-delimited line
) RETURN VARCHAR2          -- The first field (before the first |)
```

**What it does**:
- Extracts the group identifier — everything before the first `|`.
- For `026|1023527784227|F|` → returns `'026'`.
- For `ZHV|DS0000IE16|...` → returns `'ZHV'`.
- Simple `SUBSTR + INSTR` — no array allocation.
- Not used in the V2 inner loop (the group ID is taken directly from `FN_PARSE_LINE` result `v_fields(1)` instead).

---

### 20. `PKG_DTC_COMMON.FN_CONVERT_DATE`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_CONVERT_DATE(
    p_date_str IN VARCHAR2    -- Date/datetime string e.g. '20260316000000' or '20260316'
) RETURN DATE DETERMINISTIC   -- Oracle DATE value, or NULL on failure
```

**What it does**:
- Converts `YYYYMMDD` string to Oracle DATE.
- Returns `NULL` if input is NULL, empty, or conversion fails (no exception thrown to caller).
- `DETERMINISTIC` — Oracle can cache repeated calls with the same input.
- Called in `FN_INSERT_GROUP_030` for `STG_030_READ_DTTM` and `STG_030_MD_RESET_DTTM`.

---

### 21. `PKG_DTC_COMMON.FN_CONVERT_NUMBER`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_CONVERT_NUMBER(
    p_num_str IN VARCHAR2    -- Numeric string e.g. '78.4'
) RETURN NUMBER DETERMINISTIC -- Oracle NUMBER value, or NULL on failure
```

**What it does**:
- Converts a string to NUMBER using `TO_NUMBER`.
- Returns `NULL` if input is NULL, empty, or conversion fails.
- `DETERMINISTIC` — Oracle can cache repeated calls.
- Called in `FN_INSERT_GROUP_030` for `STG_030_READ_VAL` and `STG_030_MD_RESET_NUM`.

---

### 22. `PKG_DTC_COMMON.FN_GET_ERROR_MESSAGE`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_GET_ERROR_MESSAGE(
    p_msg_pk IN VARCHAR2    -- Error code e.g. 'ERR8013'
) RETURN VARCHAR2            -- Message template e.g. 'Field @1 is mandatory'
```

**What it does**:
- Looks up the message template from `MDQ_APP_MSG_REF` by `MSG_PK`.
- Uses a **package-level session cache** (`g_msg_cache`) — first call queries the DB, subsequent calls for the same code return from memory without a DB round-trip.
- Returns a fallback string `'Error code ERR8013 not found in message reference'` if code not in table.

---

### 23. `PKG_DTC_COMMON.FN_FORMAT_ERROR`
**Package**: `PKG_DTC_COMMON`

```sql
FUNCTION FN_FORMAT_ERROR(
    p_msg_pk IN VARCHAR2,
    p_param1 IN VARCHAR2 DEFAULT NULL,
    p_param2 IN VARCHAR2 DEFAULT NULL,
    p_param3 IN VARCHAR2 DEFAULT NULL,
    p_param4 IN VARCHAR2 DEFAULT NULL,
    p_param5 IN VARCHAR2 DEFAULT NULL
) RETURN VARCHAR2    -- Fully formatted error message
```

**What it does**:
- Calls `FN_GET_ERROR_MESSAGE` to get the template.
- Substitutes `@1` through `@5` placeholders with the provided parameters.
- Uses `NVL(param, 'empty')` — so unset parameters show `'empty'` rather than raw `@N`.
- Example: `FN_FORMAT_ERROR('ERR8013', 'MPAN')` → `'Field MPAN is mandatory'`
- Called everywhere an error message needs to be built.

---

### 24. `PKG_DTC_D0010.PRC_PROCESS_FILE_V2`
**Package**: `PKG_DTC_D0010` (body: `PKG_DTC_D0010.pkb`)

```sql
PROCEDURE PRC_PROCESS_FILE_V2(
    p_file_pk     IN  NUMBER,                                      -- FK to MDQ_ETL_FILE
    p_lines       IN  DBMS_SQL.VARCHAR2A,                          -- Pre-split lines
    p_flow_type   IN  VARCHAR2,                                    -- 'D0010'
    p_stage1_data IN  PKG_DTC_VALIDATION.t_file_validation_result, -- Header/footer already parsed
    p_result      OUT PKG_DTC_VALIDATION.t_file_validation_result  -- Staging result with counts
)
```

**What it does**:
- Loads JSON config and calls `FN_BUILD_GROUP_CACHE` once.
- Iterates lines 2 to N-1 (data lines only — skips header and footer).
- Per line:
  1. Calls `FN_PARSE_LINE` → get `v_fields` array.
  2. `v_group_id = v_fields(1)` — identifies the group.
  3. Tracks parent group boundaries — records which lines belong to which 026 group.
  4. Calls `FN_VALIDATE_GROUP_LINE` (cache overload) → validates fields.
  5. Updates hierarchy validity flags (`v_026_valid`, `v_028_valid`, `v_030_valid`).
  6. If valid AND parent valid → calls the appropriate `FN_INSERT_GROUP_XXX` / `PRC_INSERT_GROUP_XXX`.
  7. Increments `staged_rec_count` or `rejected_rec_count` accordingly.
- Sets `p_result.status = 'STAGING'` if `staged_flow_count > 0`, else `'REJECTED'`.

**Hierarchy validity rules**:
| Condition | Effect |
|---|---|
| 026 fails | 026 + ALL its children (027, 028, 029, 030, 032, 033) rejected |
| 028 fails | 028 + its children (029, 030, 032, 033) rejected |
| 030 fails | 030 + its children (032, 033) rejected |
| 027/029/032/033 fails | Only that line rejected; parent unaffected |

---

### 25. `PKG_DTC_D0010.FN_INSERT_GROUP_026`
**Package**: `PKG_DTC_D0010`

```sql
FUNCTION FN_INSERT_GROUP_026(
    p_file_pk  IN NUMBER,                         -- FK to MDQ_ETL_FILE
    p_fields   IN PKG_DTC_COMMON.t_fields_array,  -- Parsed fields from line
    p_rec_num  IN NUMBER                          -- Sequential record number
) RETURN NUMBER                                   -- Returns new STG_026_PK (used as FK by children)
```

**What it does**:
- Inserts into `STAGE_D0010_026`:
  - `STG_026_PK` ← `STG_D0010_026_SEQ.NEXTVAL`
  - `STG_026_MPAN` ← `TO_NUMBER(p_fields(2))`
  - `STG_026_BSC_VLDN_STATUS` ← `p_fields(3)`
- Returns the new PK via `RETURNING ... INTO` — this PK becomes the FK for child groups 027, 028.

---

### 26. `PKG_DTC_D0010.PRC_INSERT_GROUP_027`
**Package**: `PKG_DTC_D0010`

```sql
PROCEDURE PRC_INSERT_GROUP_027(
    p_parent_pk IN NUMBER,                         -- FK → STG_026_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
)
```

**What it does**:
- Inserts into `STAGE_D0010_027`:
  - `STG_027_026_PK` ← `p_parent_pk`
  - `STG_027_SITE_VISIT_CHECK` ← `p_fields(2)`
  - `STG_027_ADD_INFO` ← `p_fields(3)`
- No PK returned (no children).

---

### 27. `PKG_DTC_D0010.FN_INSERT_GROUP_028`
**Package**: `PKG_DTC_D0010`

```sql
FUNCTION FN_INSERT_GROUP_028(
    p_parent_pk IN NUMBER,                         -- FK → STG_026_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
) RETURN NUMBER                                    -- Returns new STG_028_PK
```

**What it does**:
- Inserts into `STAGE_D0010_028`:
  - `STG_028_PK` ← `STG_D0010_028_SEQ.NEXTVAL`
  - `STG_028_026_PK` ← `p_parent_pk`
  - `STG_028_MTR_ID` ← `p_fields(2)` (Meter ID)
  - `STG_028_READING_TYPE` ← `p_fields(3)`
- Returns PK for use as FK by child groups 029, 030.

---

### 28. `PKG_DTC_D0010.PRC_INSERT_GROUP_029`
**Package**: `PKG_DTC_D0010`

```sql
PROCEDURE PRC_INSERT_GROUP_029(
    p_parent_pk IN NUMBER,   -- FK → STG_028_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
)
```

**What it does**:
- Inserts into `STAGE_D0010_029`:
  - `STG_029_028_PK` ← `p_parent_pk`
  - `STG_029_SITE_VISIT_CHECK` ← `p_fields(2)`
  - `STG_029_ADD_INFO` ← `p_fields(3)`

---

### 29. `PKG_DTC_D0010.FN_INSERT_GROUP_030`
**Package**: `PKG_DTC_D0010`

```sql
FUNCTION FN_INSERT_GROUP_030(
    p_parent_pk IN NUMBER,   -- FK → STG_028_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
) RETURN NUMBER               -- Returns new STG_030_PK
```

**What it does**:
- Inserts into `STAGE_D0010_030`:
  - `STG_030_028_PK` ← `p_parent_pk`
  - `STG_030_MTR_REG_ID` ← `p_fields(2)` (Register ID e.g. `'01'`)
  - `STG_030_READ_DTTM` ← `PKG_DTC_COMMON.FN_CONVERT_DATE(p_fields(3))` (e.g. `20260316000000`)
  - `STG_030_READ_VAL` ← `PKG_DTC_COMMON.FN_CONVERT_NUMBER(p_fields(4))` (e.g. `78.4`)
  - `STG_030_MD_RESET_DTTM` ← `PKG_DTC_COMMON.FN_CONVERT_DATE(p_fields(5))` (can be NULL)
  - `STG_030_MD_RESET_NUM` ← `PKG_DTC_COMMON.FN_CONVERT_NUMBER(p_fields(6))` (can be NULL)
  - `STG_030_READ_IND` ← `p_fields(7)` (e.g. `'F'`)
  - `STG_030_READING_MTHD` ← `p_fields(8)` (e.g. `'N'`)
- Returns PK for use as FK by child groups 032, 033.

---

### 30. `PKG_DTC_D0010.PRC_INSERT_GROUP_032`
**Package**: `PKG_DTC_D0010`

```sql
PROCEDURE PRC_INSERT_GROUP_032(
    p_parent_pk IN NUMBER,   -- FK → STG_030_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
)
```

**What it does**:
- Inserts into `STAGE_D0010_032`:
  - `STG_032_030_PK` ← `p_parent_pk`
  - `STG_032_READ_REASON_CODE` ← `p_fields(2)`
  - `STG_032_READ_STATUS` ← `p_fields(3)`

---

### 31. `PKG_DTC_D0010.PRC_INSERT_GROUP_033`
**Package**: `PKG_DTC_D0010`

```sql
PROCEDURE PRC_INSERT_GROUP_033(
    p_parent_pk IN NUMBER,   -- FK → STG_030_PK
    p_file_pk   IN NUMBER,
    p_fields    IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num   IN NUMBER
)
```

**What it does**:
- Inserts into `STAGE_D0010_033`:
  - `STG_033_030_PK` ← `p_parent_pk`
  - `STG_033_SITE_VISIT_CHECK` ← `p_fields(2)`
  - `STG_033_ADD_INFO` ← `p_fields(3)`

---

### 32. `logger` / `logger_wrapper`
**Package**: Standalone procedures (`06_Procedures.sql`)

```sql
PROCEDURE logger(
    p_caller      IN VARCHAR2,         -- Who is calling
    p_code        IN INTEGER,          -- Log code
    p_description IN VARCHAR2,         -- Message
    p_rowcount    IN NUMBER DEFAULT NULL
)
-- Uses PRAGMA AUTONOMOUS_TRANSACTION — commits independently from main transaction

PROCEDURE logger_wrapper(
    p_caller      IN VARCHAR2,
    p_code        IN INTEGER,
    p_description IN VARCHAR2,
    p_rowcount    IN NUMBER  DEFAULT NULL,
    p_enable_log  IN BOOLEAN DEFAULT TRUE  -- Can suppress logging
)
```

**What it does**:
- `logger` inserts into `MDQ_APP_LOG_TABLE` using an **autonomous transaction** — so the log commit is independent from the main data transaction (log entries survive even if the main transaction rolls back).
- `logger_wrapper` is a thin wrapper that checks `p_enable_log` before calling `logger`.
- Called inside `WHEN OTHERS` handlers in `PRC_CREATE_AUDIT`, `PRC_UPDATE_AUDIT`, `PRC_LOG_ERROR`, and `PRC_PROCESS_FILE` to capture unexpected secondary exceptions.

---

## Method Summary Table

| # | Method | Package | Type | Called From | Purpose |
|---|---|---|---|---|---|
| 1 | `PRC_DTC_PROCESS_FILE_WRAPPER` | Standalone | Procedure | External callers | Entry point wrapper |
| 2 | `PRC_PROCESS_FILE` | PKG_DTC_PROCESSING | Function | Wrapper | Main orchestrator |
| 3 | `PRC_CREATE_AUDIT` | PKG_DTC_PROCESSING | Private Procedure | PRC_PROCESS_FILE | Create audit row (RUNNING) |
| 4 | `PRC_UPDATE_AUDIT` | PKG_DTC_PROCESSING | Private Procedure | PRC_PROCESS_FILE | Finalize audit row |
| 5 | `PRC_LOG_ERROR` | PKG_DTC_PROCESSING | Private Procedure | PRC_PROCESS_FILE | Insert error row |
| 6 | `FN_SPLIT_FILE_LINES` | PKG_DTC_COMMON | Function | FN_VALIDATE_FILE_V2 | Split CLOB into lines |
| 7 | `FN_GET_ACTIVE_CONFIG` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_FILE_V2, PRC_PROCESS_FILE_V2 | Load JSON rules |
| 8 | `FN_VALIDATE_FILE_V2` | PKG_DTC_VALIDATION | Function | PRC_PROCESS_FILE | Top-level validation entry |
| 9 | `FN_VALIDATE_STAGE1` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_FILE_V2 | File-level critical checks |
| 10 | `FN_PARSE_HEADER` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_STAGE1 | Extract header fields |
| 11 | `FN_PARSE_FOOTER` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_STAGE1 | Extract footer fields |
| 12 | `FN_VALIDATE_HEADER` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_STAGE1 | Validate header against config |
| 13 | `FN_VALIDATE_FOOTER` | PKG_DTC_VALIDATION | Function | FN_VALIDATE_STAGE1 | Validate footer + record count |
| 14 | `FN_VALIDATE_FIELD` (×2) | PKG_DTC_VALIDATION | Function | FN_VALIDATE_HEADER/FOOTER/GROUP_LINE | Single field validation |
| 15 | `FN_BUILD_GROUP_CACHE` | PKG_DTC_VALIDATION | Function | PRC_PROCESS_FILE_V2 | Pre-compile JSON config to cache |
| 16 | `FN_VALIDATE_GROUP_LINE` (×3) | PKG_DTC_VALIDATION | Function | PRC_PROCESS_FILE_V2 | Validate one data line |
| 17 | `ADD_ERROR` | PKG_DTC_VALIDATION | Public Procedure | Throughout validation | Append error to collection |
| 18 | `FN_PARSE_LINE` | PKG_DTC_COMMON | Function | PRC_PROCESS_FILE_V2 | Split one line to fields array |
| 19 | `FN_GET_GROUP_ID` | PKG_DTC_COMMON | Function | Legacy only | Extract group ID from line |
| 20 | `FN_CONVERT_DATE` | PKG_DTC_COMMON | Function | FN_INSERT_GROUP_030 | String to DATE (null-safe) |
| 21 | `FN_CONVERT_NUMBER` | PKG_DTC_COMMON | Function | FN_INSERT_GROUP_030 | String to NUMBER (null-safe) |
| 22 | `FN_GET_ERROR_MESSAGE` | PKG_DTC_COMMON | Function | FN_FORMAT_ERROR | Load message from DB/cache |
| 23 | `FN_FORMAT_ERROR` | PKG_DTC_COMMON | Function | Throughout all packages | Build formatted error string |
| 24 | `PRC_PROCESS_FILE_V2` | PKG_DTC_D0010 | Procedure | PRC_PROCESS_FILE | D0010 staging loop |
| 25 | `FN_INSERT_GROUP_026` | PKG_DTC_D0010 | Function | PRC_PROCESS_FILE_V2 | Insert MPAN parent row |
| 26 | `PRC_INSERT_GROUP_027` | PKG_DTC_D0010 | Procedure | PRC_PROCESS_FILE_V2 | Insert site visit row |
| 27 | `FN_INSERT_GROUP_028` | PKG_DTC_D0010 | Function | PRC_PROCESS_FILE_V2 | Insert meter row |
| 28 | `PRC_INSERT_GROUP_029` | PKG_DTC_D0010 | Procedure | PRC_PROCESS_FILE_V2 | Insert meter site visit row |
| 29 | `FN_INSERT_GROUP_030` | PKG_DTC_D0010 | Function | PRC_PROCESS_FILE_V2 | Insert meter register reading |
| 30 | `PRC_INSERT_GROUP_032` | PKG_DTC_D0010 | Procedure | PRC_PROCESS_FILE_V2 | Insert reading reason row |
| 31 | `PRC_INSERT_GROUP_033` | PKG_DTC_D0010 | Procedure | PRC_PROCESS_FILE_V2 | Insert reading site visit row |
| 32 | `logger` / `logger_wrapper` | Standalone | Procedures | WHEN OTHERS handlers | Autonomous transaction logging |
