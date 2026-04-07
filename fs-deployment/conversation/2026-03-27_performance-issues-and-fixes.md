# Performance Issues and Fixes
**Date:** 2026-03-27

---

## Context

Debugging why `PKG_DTC_PROCESSING.PRC_PROCESS_FILE` is slow when loading data for D0010 flow type.
The analysis was done by reading all relevant package bodies — no code was changed.
UAT is ongoing so any fixes must not change logic, validation rules, error codes, or output.

---

## Test Query Used

```sql
SET SERVEROUTPUT ON;

DECLARE
  v_file_content CLOB;
  v_flow_type    VARCHAR2(50)  := 'D0010';
  v_file_name    VARCHAR2(100) := 'Claude_Testing_D0010Test1.txt';
  v_run_num      NUMBER        := 12;
  v_result       VARCHAR2(4000);
BEGIN
  SELECT filedata INTO v_file_content FROM TBD_SRC_DATA;

  v_result := PKG_DTC_PROCESSING.PRC_PROCESS_FILE(
    p_file_content => v_file_content,
    p_flow_type    => v_flow_type,
    p_file_name    => v_file_name,
    p_run_num      => v_run_num
  );

  DBMS_OUTPUT.PUT_LINE('Function Result: ' || v_result);
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
/
```

---

## Performance Root Cause Analysis

### Issue 1 — CLOB Split Into Lines Twice *(Most Significant)*

The file content is split into a line-by-line array by `FN_SPLIT_FILE_LINES` **twice** for every file:

| Call # | Where | Why |
|--------|-------|-----|
| 1st | `PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2` (Step 3 of `PRC_PROCESS_FILE`) | Structure + Stage 1 validation |
| 2nd | `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` (Step 6) | Stage 1 re-validated + Stage 2 + insertion |

`FN_SPLIT_FILE_LINES` reads the CLOB in 32KB chunks via `DBMS_LOB.READ` in a loop, building a `VARCHAR2A` array. For a large file this is the most expensive single operation — and the entire CLOB traversal is done twice.

---

### Issue 2 — JSON Config Parsed on Every Single Line *(Second Biggest)*

Inside `FN_VALIDATE_GROUP_LINE` (called once per data line, in both passes):

```plsql
-- Runs for EVERY line in the file
v_config := JSON_OBJECT_T(p_config_json);
v_groups_array := JSON_ARRAY_T(v_config.get('groups'));
-- Then iterates all group configs to find the matching group ID
FOR i IN 0 .. v_groups_array.get_size - 1 LOOP ...
```

The entire JSON config document is parsed from scratch on **every line**. If the file has 5,000 data lines, the JSON is parsed 5,000+ times. There is no caching at this level.

---

### Issue 3 — Stage 1 Validation Done Twice

`FN_VALIDATE_STAGE1` (header/footer/record count validation) is called:
- Once inside `FN_VALIDATE_FILE_V2` (Step 3)
- Again inside `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` (Step 6, Pass 1)

The header and footer are validated twice with identical logic and config.

---

### Issue 4 — Each Line is Parsed Twice (Validation + Insertion)

For every data line in Pass 2 of `PRC_PROCESS_FILE_V2`:

1. `FN_VALIDATE_GROUP_LINE` splits the line by delimiter internally
2. Then `FN_INSERT_GROUP_026/028/030` calls `PKG_DTC_COMMON.FN_PARSE_LINE(p_line)` — splits the **same line again**

Every line is pipe-split twice: once to validate fields, once to insert them.

---

### Issue 5 — REGEXP_LIKE on Every Field with a Pattern

`FN_VALIDATE_FIELD` calls `REGEXP_LIKE(p_field_value, v_pattern)` for every field that has a pattern rule. Regular expression evaluation is relatively expensive and runs for every field on every line.

Additionally, the pattern `REPLACE` cleanup (`\\d → \d` etc.) runs on every call rather than being pre-processed once.

---

### Issue 6 — No Bulk Insert (Row-by-Row)

Every group insert (026, 027, 028, 029, 030, 032, 033) is a single `INSERT` per line. For a file with thousands of records this means thousands of individual INSERT context switches between PL/SQL and SQL engines. No `FORALL` bulk collect is used.

---

## Summary — Priority Order

| # | Problem | Impact |
|---|---------|--------|
| 1 | CLOB split into lines twice | Very High — entire file read twice via `DBMS_LOB.READ` |
| 2 | JSON config parsed per line (not per file) | Very High — thousands of JSON parse operations |
| 3 | Stage 1 validation run twice | Medium — header/footer re-validated unnecessarily |
| 4 | Line pipe-split twice (validate + insert) | Medium — double string parsing per line |
| 5 | REGEXP per field per line | Medium — expensive for high field-count groups |
| 6 | Row-by-row INSERTs, no bulk | Medium — thousands of individual SQL context switches |

---

## Proposed Safe Fixes (Zero Logic Change Risk)

The two highest-impact fixes are safe because they are internal to the processing pipeline
and do not touch any validation logic, field rules, error codes, or output.

### Fix A — Pass Pre-Split Lines Into PRC_PROCESS_FILE_V2
Pass the already-split `v_lines` array from `FN_VALIDATE_FILE_V2` into `PRC_PROCESS_FILE_V2`
instead of re-splitting. The lines array already exists in `PKG_DTC_PROCESSING` after Step 3
— it just needs to be passed through rather than rebuilt.

### Fix B — Parse JSON Once Before the Loop
Parse `JSON_OBJECT_T(p_config_json)` **once before the loop** and pass the parsed object
(or pre-extracted group map) into `FN_VALIDATE_GROUP_LINE` rather than re-parsing on each call.
Requires a signature change to `FN_VALIDATE_GROUP_LINE` but does not change what it validates
or how.

---

## Status

- Analysis complete. No code changed.
- Fixes A and B approved to proceed when UAT window allows.
