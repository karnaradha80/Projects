# Performance Optimization Summary — All Fixes
**Date:** 2026-03-27

---

## Baseline: ~315 seconds

**Root causes identified:**
1. The CLOB was split into lines twice (once in validation, once in processing)
2. JSON config was parsed from scratch on every single data line
3. Stage 1 validation (header/footer/record count) ran twice
4. Each line was parsed twice — once for validation, once inside each insert function
5. REGEXP escape sequences resolved via 6× `REPLACE` calls on every field on every line

---

## Fix 1 — Eliminate double CLOB split + double Stage 1 validation
**~315s → ~208s (-107s)**

**What changed:**
- `PKG_DTC_PROCESSING.PRC_PROCESS_FILE` — split the CLOB into lines once using `FN_SPLIT_FILE_LINES`, then passed the resulting `DBMS_SQL.VARCHAR2A` array to both `FN_VALIDATE_FILE_V2` and `PRC_PROCESS_FILE_V2` directly
- `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` and `PKG_DTC_D0150.PRC_PROCESS_FILE_V2` — added `p_lines IN DBMS_SQL.VARCHAR2A` and `p_stage1_data IN t_file_validation_result` parameters; removed the internal `FN_SPLIT_FILE_LINES` call and removed the internal Stage 1 re-validation pass

**Before:** `FN_SPLIT_FILE_LINES` traversed the entire CLOB twice; header/footer/count validation ran twice
**After:** CLOB traversed once; Stage 1 results reused from the first pass

---

## Fix 2 — Parse JSON config once before the line loop
**~208s → ~163s (-45s)**

**What changed:**
- `PKG_DTC_D0010.PRC_PROCESS_FILE_V2` and `PKG_DTC_D0150.PRC_PROCESS_FILE_V2` — moved `JSON_OBJECT_T(v_config_json)` and `JSON_ARRAY_T(v_parsed_config.get('groups'))` calls to before the loop, storing the parsed array in `v_parsed_groups JSON_ARRAY_T`
- Changed `FN_VALIDATE_GROUP_LINE` call to use the overload that accepts a pre-parsed `JSON_ARRAY_T` instead of the raw `CLOB`
- Added the overload `FN_VALIDATE_GROUP_LINE(p_fields, p_group_id, p_groups_array, p_line_number, p_errors)` to `PKG_DTC_VALIDATION`

**Before:** `JSON_OBJECT_T(config_json)` and `JSON_ARRAY_T(...)` executed on every data line (408k times)
**After:** JSON parsed once; the parsed `JSON_ARRAY_T` object reused for every line

---

## Fix 3 — Eliminate REPLACE escape sequences inside the line loop
**~163s → ~160s (-3s)**

**What changed:**
- `PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE` (the `JSON_ARRAY_T` overload) — moved the 6× `REPLACE` calls that resolve regex escape sequences (`\\d`, `\\w`, etc.) from inside the field-loop to outside it, resolved once per group config lookup per file rather than per line

**Before:** For every data line, for every field with a pattern, 6× `REPLACE` calls ran on the pattern string
**After:** Pattern strings resolved once at config parse time

---

## Fix 4 — Parse each line once (not once per insert function)
**~160s → ~160s (minor, sets up Fix 5)**

**What changed:**
- All 7 insert function signatures in `PKG_DTC_D0010.pkb/.pks` — changed `p_line IN VARCHAR2` → `p_fields IN PKG_DTC_COMMON.t_fields_array`; removed `v_fields` local variable and `FN_PARSE_LINE` call from each function body
- All 9 insert function signatures in `PKG_DTC_D0150.pkb/.pks` — same change
- `PRC_PROCESS_FILE_V2` in both packages — added `v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(v_lines(i))` once at the top of the loop; passed `v_fields` to both the validation call and the insert calls

**Before:** Each line was pipe-split twice — once inside `FN_VALIDATE_GROUP_LINE` and once inside each `FN_INSERT_GROUP_xxx`
**After:** `FN_PARSE_LINE` called exactly once per line; the resulting `t_fields_array` passed everywhere

---

## Fix 5 — Pre-build field config cache (eliminate all JSON + REPLACE from inner loop)
**~160s → ~139s (-21s)**

**What changed:**

**`PKG_DTC_VALIDATION_v2.pks`** — added:
- `TYPE t_field_config IS RECORD` — stores all pre-processed field attributes (`field_name`, `mandatory`, `min_length`, `max_length`, `data_type`, `pattern` with escape sequences already resolved, `pattern_error_code`, `fmt`, `precision`, `scale`, `position`)
- `TYPE t_field_config_cache IS TABLE OF t_field_config INDEX BY VARCHAR2(20)` — flat cache keyed by `group_id || '~' || field_index`
- `FUNCTION FN_BUILD_GROUP_CACHE(p_groups_array IN JSON_ARRAY_T) RETURN t_field_config_cache`
- New overload `FN_VALIDATE_GROUP_LINE(p_fields, p_group_id, p_group_cache IN t_field_config_cache, p_line_number, p_errors)`

**`PKG_DTC_VALIDATION_v2_complete.pkb`** — added:
- Body of `FN_BUILD_GROUP_CACHE` — iterates the JSON groups array once, pre-processes every field's attributes including resolving all 6 REPLACE escape sequences, stores everything in the cache
- Private overload `FN_VALIDATE_FIELD(p_field_value, p_field_config t_field_config, p_error_msg)` — validates using the pre-processed record with no JSON calls and no REPLACE calls
- Body of the cache overload of `FN_VALIDATE_GROUP_LINE` — does `IF v_cache.EXISTS(...)` lookup instead of JSON iteration; calls the private `FN_VALIDATE_FIELD` overload

**`PKG_DTC_D0010.pkb`** and **`PKG_DTC_D0150.pkb`** — in `PRC_PROCESS_FILE_V2`:
- Replaced `v_parsed_groups JSON_ARRAY_T` with `v_group_cache PKG_DTC_VALIDATION.t_field_config_cache`
- `FN_BUILD_GROUP_CACHE` called once before the loop
- `FN_VALIDATE_GROUP_LINE` call updated to the new cache overload

**Before:** For every data line → JSON group array iterated → per-field: 6× REPLACE on pattern string
**After:** All JSON and REPLACE work done once before the loop; inner loop does array index lookup only

### Attempted within Fix 5: Session-Level Regex Result Cache
Added `TYPE t_regex_cache IS TABLE OF BOOLEAN INDEX BY VARCHAR2(4201); g_regex_cache t_regex_cache;` at package level to avoid re-running `REGEXP_LIKE` for repeated `(pattern, value)` pairs.

**Result: +22s regression (161s vs 139s). Reverted.** Root cause: D0010 fields are mostly high-cardinality (MPANs, meter IDs, datetimes — unique per line), so cache mostly misses; the hash insert overhead per miss outweighs any benefit.

---

## Fix 6 — FORALL Bulk Inserts *(Attempted and Reverted)*
**~139s → ~160-165s (+21-26s) — REVERTED**

**What was tried:**
Rewrote `PRC_PROCESS_FILE_V2` in both D0010 and D0150 as a two-pass approach:
- **Pass 1:** Validate each line, collect valid row data into per-group parallel arrays (`t_num_arr`, `t_str_arr`, `t_date_arr` INDEX BY PLS_INTEGER), track parent array slot indices instead of PKs
- **Pass 2:** One `FORALL` bulk INSERT per group table; parent PKs resolved via `RETURNING STG_xxx_PK BULK COLLECT INTO v_xxx_pk`; children look up FK as `v_parent_pk(v_child_pidx(i))`

**Why reverted:**
The test file has ~408k rows across 7 group tables (~130k rows each in groups 026/028/030). Holding all parallel column arrays in PGA memory simultaneously before any INSERT fires created more overhead than the context-switch savings:
- PGA memory pressure from ~400k+ array entries across all groups
- `RETURNING BULK COLLECT INTO` for 130k rows per parent table created large temporary arrays
- Array element assignment overhead in Pass 1 added to total cost

FORALL is beneficial for moderate volumes. At this scale, row-by-row INSERTs within a single transaction are already fast and the memory overhead of full pre-collection exceeds the savings.

**Both packages restored to Fix 5 state.**

---

## Final Result

| State | Time | Improvement |
|-------|------|-------------|
| Baseline | ~315s | — |
| After Fix 1 | ~208s | -34% |
| After Fix 2 | ~163s | -48% |
| After Fix 3 | ~160s | -49% |
| After Fix 4+5 | **~139s** | **-56%** |
| Fix 6 (reverted) | ~162s | regression |

---

## Files Changed (Final State)

| File | Changes |
|------|---------|
| `PKG_DTC_PROCESSING.pkb` | Split CLOB once, pass lines + stage1 data to flow packages |
| `PKG_DTC_VALIDATION_v2.pks` | Added `t_field_config`, `t_field_config_cache`, `FN_BUILD_GROUP_CACHE`, cache overload of `FN_VALIDATE_GROUP_LINE`; updated `FN_VALIDATE_FILE_V2` signature to return `p_lines` |
| `PKG_DTC_VALIDATION_v2_complete.pkb` | Added `FN_BUILD_GROUP_CACHE` body, private `FN_VALIDATE_FIELD` cache overload, cache overload of `FN_VALIDATE_GROUP_LINE` body |
| `PKG_DTC_D0010.pks` | All 7 insert function signatures: `p_line VARCHAR2` → `p_fields t_fields_array`; `PRC_PROCESS_FILE_V2` signature updated |
| `PKG_DTC_D0010.pkb` | All 7 insert function bodies updated; `PRC_PROCESS_FILE_V2` uses cache, single parse per line, row-by-row inserts |
| `PKG_DTC_D0150.pks` | All 9 insert function signatures: `p_line VARCHAR2` → `p_fields t_fields_array`; `PRC_PROCESS_FILE_V2` signature updated |
| `PKG_DTC_D0150.pkb` | All 9 insert function bodies updated; `PRC_PROCESS_FILE_V2` uses cache, single parse per line, row-by-row inserts |
