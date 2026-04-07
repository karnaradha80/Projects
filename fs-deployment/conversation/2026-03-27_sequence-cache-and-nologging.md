# Sequence Cache + NOLOGGING Investigation
**Date:** 2026-03-27

---

## Context

Continuing from Fix 5 (~165s stable baseline). Investigating remaining gap vs data stage environment (36s).

---

## Finding: Sequences were NOCACHE

All 5 staging sequences had `CACHE_SIZE = 0` (NOCACHE):

| Sequence | Before | After |
|----------|--------|-------|
| STG_D0010_026_SEQ | NOCACHE | CACHE 500 |
| STG_D0010_028_SEQ | NOCACHE | CACHE 500 |
| STG_D0010_030_SEQ | NOCACHE | CACHE 500 |
| STG_D0150_288_SEQ | NOCACHE | CACHE 500 |
| STG_D0150_290_SEQ | NOCACHE | CACHE 500 |

**Root cause:** NOCACHE means every `NEXTVAL` call writes to the redo log to persist the sequence value. With ~387k rows across groups 026/028/030, that was ~387k synchronous redo writes just for sequence values.

**Fix:** `ALTER SEQUENCE ... CACHE 500` on all 5 sequences.

**Script:** `alter_sequence_cache.sql` — safe to run on live databases, takes effect immediately.

**Also updated:** `02_create_sequences.sql` changed from NOCACHE to CACHE 500 so fresh deployments are correct from the start.

---

## Result

| Run | Tables state | Seconds |
|-----|-------------|---------|
| Pre-change runs 8–12 | Accumulated 1.7M+ rows | 160–165 |
| Run 13 (first post-cache) | Warm SGA from 12 prior runs | **16** *(outlier)* |
| Run 14 | Tables had 1.7M+ rows, cooler cache | 89 |
| Run 15 (truncated tables, clean) | Empty tables, cold cache | **90** |

Run 13 at 16s was an anomaly — extremely warm Oracle SGA buffer cache from 12 consecutive prior runs had all data pages in memory. Not reproducible in normal conditions.

True stable result with sequence cache: **~90s**.

---

## Why CACHE 500 is safe for this workload

- Most files have <50 records — CACHE 500 and CACHE 50 behave identically for small files (1 refill covers all rows, unused values carry forward to next file)
- Large files (<10%) benefit from fewer redo writes: 387k → ~774 refills
- Gaps on instance restart: up to 500 values skipped per sequence — acceptable for surrogate staging PKs

---

## NOLOGGING Investigation (not implemented)

**Proposed:** `ALTER TABLE STAGE_Dxxxx_xxx NOLOGGING` + `INSERT /*+ APPEND_VALUES */` hint on all 16 INSERT statements.

**How it would work:** `APPEND_VALUES` triggers direct-path inserts for single-row VALUES inserts in PL/SQL loops. Combined with NOLOGGING, redo for INSERT data is suppressed.

**Decision: Not implemented** — logging is required on staging tables (recoverability requirement).

**Without NOLOGGING:** `APPEND_VALUES` hint still does direct-path but redo is still generated — no performance benefit.

---

## Remaining bottleneck (accepted)

With LOGGING required, the remaining ~90s cost is redo generation for ~387k conventional inserts — unavoidable without either:
- NOLOGGING (not allowed)
- Batched FORALL (high complexity, uncertain gain without NOLOGGING, not pursued)

The gap between ~90s and the data stage's 36s is likely hardware/environment differences (faster storage, larger SGA).

---

## Final Performance Summary (all sessions)

| State | Time | Improvement |
|-------|------|-------------|
| Baseline | ~315s | — |
| After Fixes 1–5 (code optimisations) | ~165s | -48% |
| + Sequence CACHE 500 | **~90s** | **-71%** |

---

## Files Created/Modified

| File | Change |
|------|--------|
| `alter_sequence_cache.sql` | New — ALTER SEQUENCE CACHE 500 for all 5 sequences + verify query |
| `alter_tables_nologging.sql` | New — prepared but not deployed (logging required) |
| `02_create_sequences.sql` | Updated NOCACHE → CACHE 500 for D0010/D0150 sequences |
