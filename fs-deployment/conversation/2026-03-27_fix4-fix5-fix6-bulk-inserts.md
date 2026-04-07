# Performance Fixes: Fix 4, Fix 5, Fix 6 Attempt
**Date:** 2026-03-27

---

## Summary

Continuation of performance optimization work. Applied Fix 4 (single line parse), Fix 5 (JSON field config cache), attempted Fix 6 (FORALL bulk inserts), measured, and reverted Fix 6 as a regression.

---

## Fix 4: Single FN_PARSE_LINE Per Loop Iteration

All insert function bodies in D0010 (7 functions) and D0150 (9 functions) changed from accepting `p_line IN VARCHAR2` to `p_fields IN PKG_DTC_COMMON.t_fields_array`. `PRC_PROCESS_FILE_V2` now calls `FN_PARSE_LINE` once per iteration and passes the result to both validation and insert calls.

**Files changed:** `PKG_DTC_D0010.pkb`, `PKG_DTC_D0010.pks`, `PKG_DTC_D0150.pkb`, `PKG_DTC_D0150.pks`

---

## Fix 5: Pre-Built Field Config Cache

Added `t_field_config` RECORD and `t_field_config_cache TABLE INDEX BY VARCHAR2(20)` to `PKG_DTC_VALIDATION_v2.pks`. Added `FN_BUILD_GROUP_CACHE` (builds cache keyed `group_id || '~' || field_idx`) and a new `FN_VALIDATE_GROUP_LINE` overload that accepts the cache instead of JSON.

Inner validation loop now does: cache lookup → private `FN_VALIDATE_FIELD(p_field_value, t_field_config, p_error_msg)` overload — **zero** JSON method calls, **zero** REPLACE calls per line.

**Result: ~160s → 139s**

**Files changed:** `PKG_DTC_VALIDATION_v2.pks`, `PKG_DTC_VALIDATION_v2_complete.pkb`, `PKG_DTC_D0010.pkb`, `PKG_DTC_D0150.pkb`

### Attempted: Session-Level Regex Result Cache
Added `TYPE t_regex_cache IS TABLE OF BOOLEAN INDEX BY VARCHAR2(4201); g_regex_cache t_regex_cache;` at package level to avoid re-running `REGEXP_LIKE` for repeated `(pattern, value)` pairs.

**Result: +22s regression (161s vs 139s).** Root cause: D0010 fields are mostly high-cardinality (MPANs, meter IDs, datetimes — unique per line), so cache mostly misses; the hash insert overhead per miss outweighs any benefit from low-cardinality fields. **Reverted.**

---

## Fix 6: FORALL Bulk Inserts (Attempted, Reverted)

### Design
Two-pass approach in `PRC_PROCESS_FILE_V2`:
- **Pass 1:** Validate each line and collect valid rows into per-group parallel arrays (one array per column per group table, plus `_pidx` arrays linking children to their parent's slot)
- **Pass 2:** `FORALL i IN 1 .. v_xxx_cnt` bulk INSERT per group table; parents with PKs needed by children use `RETURNING STG_xxx_PK BULK COLLECT INTO v_xxx_pk`

### Parent-child PK resolution
Children store their parent's **array slot index** (`v_xxx_pidx(i) := v_cur_xxx_idx`) during collection. In Pass 2, `v_parent_pk(v_child_pidx(i))` resolves the FK without any sequential dependency between FORALL statements.

### Results
| Run | Fix | Seconds |
|-----|-----|---------|
| 7 | Fix 5 (cache, no regex cache) | 139 |
| 8 | Fix 5 + regex cache (reverted) | 161 |
| 9 | Fix 6 (FORALL) | 160 |
| 10 | Fix 6 (FORALL, 2nd run) | 165 |

**Result: ~160s — regression from Fix 5's 139s. Reverted.**

### Why FORALL was slower
The test file has ~408k rows across 7 group tables, with ~130k rows each in groups 026, 028, 030. The parallel arrays needed to hold all this data simultaneously in PGA before any INSERT fires:
- Memory pressure from holding ~400k+ array entries (multiple columns per group)
- `RETURNING BULK COLLECT INTO` for 130k rows creates large temporary arrays
- Array element assignment overhead in Pass 1 adds to total cost

FORALL pays off when total volume is moderate. At this scale, PGA memory overhead exceeds context-switch savings. Row-by-row within a single transaction is fast enough in Oracle.

---

## Final State

Both D0010 and D0150 are at Fix 5 (row-by-row with pre-built field config cache). Best achieved: **~139s** for 408k record D0010 file (down from ~315s baseline = 56% improvement).

### Remaining bottlenecks (not worth optimizing further)
- `REGEXP_LIKE` per field — unavoidable for validation; result caching proven net negative
- `FN_PARSE_LINE` — once per line, already minimal
- Individual INSERTs — fast within single transaction, FORALL overhead exceeds benefit at this scale

---

## Performance Progression

| Baseline | Fix 1-3 | Fix 4 | Fix 5 | Fix 6 |
|----------|---------|-------|-------|-------|
| ~315s | ~160s | ~160s | **139s** | 160s (reverted) |
