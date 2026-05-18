# Databricks Certification — Week-by-Week Study Calendar

**Start Date:** 2026-05-13 (Wednesday)
**Target Exam:** ~2026-11-08 (Data Engineer Professional)
**Daily Commitment:** 1.5 hrs weekdays | 3 hrs Saturday | 2 hrs Sunday

**Legend:**
- 📖 = Read notes / theory
- 💻 = Hands-on in Databricks Community Edition
- 📝 = Practice questions
- ✅ = Milestone / Gate

---

## PHASE 0 — Python Basics
### Week 1 — May 13–19
> Goal: Python syntax, data types, collections

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Wed | May 13 | Setup: install Python, VS Code, create Databricks + Academy accounts | 💻 |
| Thu | May 14 | Variables, data types, strings, f-strings | 📖 |
| Fri | May 15 | Lists, tuples, slicing (`list[start:end:step]`) | 📖 |
| Sat | May 16 | Dictionaries, sets — operations and iteration (deep dive) | 📖 💻 |
| Sun | May 17 | Loops (for, while), conditionals, ternary operator | 📖 |

---

### Week 2 — May 18–24
> Goal: Functions, OOP, Pandas — gate: write a CSV pipeline in Python

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | May 18 | Functions, default parameters, *args, **kwargs | 📖 |
| Tue | May 19 | Lambda functions, list comprehensions | 📖 |
| Wed | May 20 | Classes, constructors, methods, `__str__` | 📖 |
| Thu | May 21 | Exception handling (try/except/finally), file I/O | 📖 |
| Fri | May 22 | Pandas — read CSV, filter rows, groupBy aggregations | 📖 💻 |
| Sat | May 23 | Complete all 10 exercises in `Phase0_Python_Basics/practice/exercises.md` | 💻 |
| Sun | May 24 | Review cheat sheet — Python vs C# side-by-side | 📖 |

> ✅ **Phase 0 Gate:** Can you write a Python script that reads a CSV, filters rows, and outputs a grouped summary? If yes → move to Phase 1.

---

## PHASE 1 — Data Analyst Associate (EXAM)
### Week 3 — May 25–31
> Goal: Databricks platform, SQL Warehouses, Delta basics

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | May 25 | Explore Databricks UI — workspace, notebooks, SQL Editor, Data tab | 💻 |
| Tue | May 26 | Create SQL Warehouse, run first query on `samples` catalog | 💻 |
| Wed | May 27 | `CREATE TABLE USING DELTA`, INSERT, basic SELECT | 📖 💻 |
| Thu | May 28 | `DESCRIBE TABLE`, `DESCRIBE DETAIL`, `DESCRIBE HISTORY` | 📖 💻 |
| Fri | May 29 | Window functions — ROW_NUMBER, RANK, LAG, LEAD | 📖 |
| Sat | May 30 | Hands-on: build sample Delta database, run 20 SQL queries | 💻 |
| Sun | May 31 | Window functions practice on real data | 💻 |

---

### Week 4 — Jun 1–7
> Goal: Advanced SQL, MERGE, time travel, views

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jun 1 | `MERGE INTO` — full syntax, all WHEN clauses | 📖 |
| Tue | Jun 2 | `MERGE` hands-on — upsert employee records | 💻 |
| Wed | Jun 3 | Time travel — `VERSION AS OF`, `TIMESTAMP AS OF` | 📖 💻 |
| Thu | Jun 4 | `RESTORE TABLE` to previous version | 📖 💻 |
| Fri | Jun 5 | Views — standard, temporary, dynamic (row-level security) | 📖 |
| Sat | Jun 6 | Hands-on: full MERGE + time travel + view exercises | 💻 |
| Sun | Jun 7 | Practice questions — Phase 1 topics so far | 📝 |

---

### Week 5 — Jun 8–14
> Goal: Dashboards, alerts, Unity Catalog, governance

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jun 8 | Databricks SQL Dashboards — build a dashboard with 3 charts | 💻 |
| Tue | Jun 9 | Alerts — create query-based alert with email notification | 💻 |
| Wed | Jun 10 | Unity Catalog hierarchy — Metastore > Catalog > Schema > Table | 📖 |
| Thu | Jun 11 | `GRANT` / `REVOKE` — catalog, schema, table level | 📖 💻 |
| Fri | Jun 12 | `SHOW GRANTS`, query history, audit basics | 📖 |
| Sat | Jun 13 | Hands-on: full governance setup — grants at all levels | 💻 |
| Sun | Jun 14 | **First attempt: Data Analyst Associate practice exam** | 📝 |

---

### Week 6 — Jun 15–21
> Goal: Review + pass the exam

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jun 15 | Review all incorrect answers from practice exam | 📝 |
| Tue | Jun 16 | Re-study weak topics | 📖 |
| Wed | Jun 17 | Review `Phase1_Data_Analyst_Associate/cheat_sheet.md` | 📖 |
| Thu | Jun 18 | Second practice exam attempt | 📝 |
| Fri | Jun 19 | Light review only — no new topics | 📖 |
| Sat | Jun 20 | ✅ **TAKE DATA ANALYST ASSOCIATE EXAM** | |
| Sun | Jun 21 | Rest and celebrate | |

> ✅ **Phase 1 Gate:** Pass Data Analyst Associate exam → move to Phase 2.

---

## PHASE 2 — Spark Associate (Prep Only)
### Week 7 — Jun 22–28
> Goal: Spark architecture and mental model

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jun 22 | Spark architecture — Driver, Executor, Cluster Manager | 📖 |
| Tue | Jun 23 | DAG — how Spark builds and optimizes execution plans | 📖 |
| Wed | Jun 24 | Transformations (lazy) vs Actions (eager) | 📖 |
| Thu | Jun 25 | Narrow vs Wide transformations, what causes a shuffle | 📖 |
| Fri | Jun 26 | RDD vs DataFrame vs Dataset — when to use each | 📖 |
| Sat | Jun 27 | Hands-on: first PySpark notebook — read, transform, write | 💻 |
| Sun | Jun 28 | Review + write your own notes on Spark architecture | 📖 |

---

### Week 8 — Jun 29–Jul 5
> Goal: DataFrame API — reading, selecting, filtering, aggregating

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jun 29 | SparkSession, `spark.read.csv/json/parquet/table()` | 📖 💻 |
| Tue | Jun 30 | `select`, `filter`, `where`, `withColumn`, `drop` | 📖 💻 |
| Wed | Jul 1 | `groupBy`, `agg`, `count`, `sum`, `avg`, `max`, `min` | 📖 💻 |
| Thu | Jul 2 | `orderBy`, `sort`, `limit`, `distinct`, `dropDuplicates` | 📖 💻 |
| Fri | Jul 3 | Writing data — `saveAsTable`, `save`, write modes | 📖 💻 |
| Sat | Jul 4 | Hands-on: full DataFrame pipeline on a real dataset | 💻 |
| Sun | Jul 5 | Practice — 10 DataFrame transformation exercises | 💻 |

---

### Week 9 — Jul 6–12
> Goal: Joins and built-in functions

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jul 6 | Join types — inner, left, right, outer | 📖 💻 |
| Tue | Jul 7 | Semi join, anti join, cross join | 📖 💻 |
| Wed | Jul 8 | Broadcast join — when, why, how to force it | 📖 💻 |
| Thu | Jul 9 | String functions — upper, lower, trim, split, regexp_replace | 📖 💻 |
| Fri | Jul 10 | Date functions — year, month, date_add, datediff, date_format | 📖 💻 |
| Sat | Jul 11 | Array functions — explode, collect_list, collect_set, array_contains | 📖 💻 |
| Sun | Jul 12 | Practice questions — joins and functions | 📝 |

---

### Week 10 — Jul 13–19
> Goal: Spark SQL and UDFs

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jul 13 | `spark.sql()`, `createOrReplaceTempView` | 📖 💻 |
| Tue | Jul 14 | Global temp views, mixing SQL and DataFrame API | 📖 💻 |
| Wed | Jul 15 | UDFs — define Python function, register, apply to column | 📖 💻 |
| Thu | Jul 16 | Why UDFs are slow — Catalyst optimizer bypass | 📖 |
| Fri | Jul 17 | Pandas UDFs (vectorized) — when and how to use | 📖 💻 |
| Sat | Jul 18 | Hands-on: SQL + UDF combined exercises | 💻 |
| Sun | Jul 19 | Review `Phase2_Spark_Associate/cheat_sheet.md` | 📖 |

---

### Week 11 — Jul 20–26
> Goal: Performance optimization

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jul 20 | Caching — `cache()`, `persist()`, storage levels, `unpersist()` | 📖 💻 |
| Tue | Jul 21 | Repartition vs Coalesce — difference and when to use each | 📖 💻 |
| Wed | Jul 22 | Shuffle partitions — configure `spark.sql.shuffle.partitions` | 📖 💻 |
| Thu | Jul 23 | AQE — what it does automatically (partition coalescing, skew) | 📖 |
| Fri | Jul 24 | Explain plans — `df.explain(True)`, reading the output | 📖 💻 |
| Sat | Jul 25 | Hands-on: compare performance with/without caching and broadcast | 💻 |
| Sun | Jul 26 | **First attempt: Spark Associate practice exam** | 📝 |

---

### Week 12 — Jul 27–Aug 2
> Goal: Review + hit 80% gate

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Jul 27 | Review all incorrect answers from practice exam | 📝 |
| Tue | Jul 28 | Re-study weak topics | 📖 |
| Wed | Jul 29 | Review full Spark cheat sheet | 📖 |
| Thu | Jul 30 | **Second practice exam attempt** | 📝 |
| Fri | Jul 31 | Review remaining gaps | 📖 |
| Sat | Aug 1 | Rest + preview Phase 3 material | |
| Sun | Aug 2 | Read Phase 3 README — set expectations | 📖 |

> ✅ **Phase 2 Gate:** Score 80%+ on Spark Associate practice exam → move to Phase 3. Do NOT pay for exam.

---

## PHASE 3 — Data Engineer Associate (Prep Only)
### Week 13 — Aug 3–9
> Goal: Delta Lake foundations

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Aug 3 | Why Delta Lake — problems it solves over plain Parquet/CSV | 📖 |
| Tue | Aug 4 | Transaction log `_delta_log/` — explore the JSON files | 📖 💻 |
| Wed | Aug 5 | `CREATE TABLE USING DELTA`, INSERT, UPDATE, DELETE | 📖 💻 |
| Thu | Aug 6 | `DESCRIBE TABLE`, `DESCRIBE DETAIL`, `DESCRIBE HISTORY` | 📖 💻 |
| Fri | Aug 7 | Time travel — `VERSION AS OF`, `TIMESTAMP AS OF`, `RESTORE` | 📖 💻 |
| Sat | Aug 8 | Hands-on: full Delta table lifecycle — create, modify, time travel | 💻 |
| Sun | Aug 9 | Managed vs External tables — DROP behavior difference | 📖 |

---

### Week 14 — Aug 10–16
> Goal: Advanced Delta — MERGE, OPTIMIZE, VACUUM, CDF

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Aug 10 | `MERGE INTO` — full syntax, all WHEN clauses | 📖 |
| Tue | Aug 11 | `MERGE` hands-on — upsert, delete, conditional update | 💻 |
| Wed | Aug 12 | `OPTIMIZE` — file compaction | 📖 💻 |
| Thu | Aug 13 | `ZORDER BY` — what it does, when to use, vs partitioning | 📖 💻 |
| Fri | Aug 14 | `VACUUM` — default retention, DRY RUN, risks | 📖 💻 |
| Sat | Aug 15 | Auto Optimize table properties — optimizeWrite, autoCompact | 📖 💻 |
| Sun | Aug 16 | Practice questions — Delta Lake | 📝 |

---

### Week 15 — Aug 17–23
> Goal: CDF, schema evolution, Auto Loader intro

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Aug 17 | Change Data Feed — enable, what it captures, limitations | 📖 |
| Tue | Aug 18 | CDF — batch read with `startingVersion`, `endingVersion` | 📖 💻 |
| Wed | Aug 19 | CDF — streaming read, `_change_type` column | 📖 💻 |
| Thu | Aug 20 | Schema evolution — `mergeSchema` vs `overwriteSchema` | 📖 💻 |
| Fri | Aug 21 | Auto Loader overview — problem it solves, two modes | 📖 |
| Sat | Aug 22 | Hands-on: CDF end-to-end — enable, insert/update/delete, read changes | 💻 |
| Sun | Aug 23 | Review Delta advanced notes | 📖 |

---

### Week 16 — Aug 24–30
> Goal: Auto Loader deep dive

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Aug 24 | Directory listing mode — how it works, limitations | 📖 |
| Tue | Aug 25 | File notification mode — cloud queues, why it scales | 📖 |
| Wed | Aug 26 | Schema inference, `schemaLocation`, schema hints | 📖 💻 |
| Thu | Aug 27 | Schema evolution — `mergeSchema`, `rescuedDataColumn` | 📖 💻 |
| Fri | Aug 28 | Checkpoint — purpose, structure, unique per query rule | 📖 |
| Sat | Aug 29 | Hands-on: build full Auto Loader Bronze ingestion pipeline | 💻 |
| Sun | Aug 30 | `_metadata` columns — file_path, file_name, file_size | 📖 |

---

### Week 17 — Aug 31–Sep 6
> Goal: Delta Live Tables

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Aug 31 | What DLT solves vs standard notebooks | 📖 |
| Tue | Sep 1 | `@dlt.table` decorator, LIVE vs STREAMING LIVE | 📖 |
| Wed | Sep 2 | `dlt.read()` vs `dlt.read_stream()` | 📖 💻 |
| Thu | Sep 3 | Expectations — `expect`, `expect_or_drop`, `expect_or_fail` | 📖 💻 |
| Fri | Sep 4 | DLT pipeline modes — Development vs Production | 📖 |
| Sat | Sep 5 | Hands-on: build full Bronze → Silver → Gold DLT pipeline | 💻 |
| Sun | Sep 6 | DLT event log — query expectations pass/fail counts | 📖 💻 |

---

### Week 18 — Sep 7–13
> Goal: Medallion architecture + 80% gate

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Sep 7 | Bronze layer rules — raw, append-only, metadata columns | 📖 |
| Tue | Sep 8 | Silver layer — deduplication strategies (dropDuplicates vs MERGE) | 📖 💻 |
| Wed | Sep 9 | Gold layer — business aggregations, query-optimized | 📖 💻 |
| Thu | Sep 10 | ELT vs ETL — why Databricks uses ELT | 📖 |
| Fri | Sep 11 | Review `Phase3_Data_Engineer_Associate/cheat_sheet.md` | 📖 |
| Sat | Sep 12 | **Full Data Engineer Associate practice exam** | 📝 |
| Sun | Sep 13 | Review incorrect answers | 📝 |

> ✅ **Phase 3 Gate:** Score 80%+ on Data Engineer Associate practice exam → move to Phase 4. Do NOT pay for exam.

---

## PHASE 4 — Data Engineer Professional (EXAM TARGET)
### Week 19 — Sep 14–20
> Goal: Advanced Delta Lake

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Sep 14 | Shallow clone — create, behavior, risk after VACUUM on source | 📖 💻 |
| Tue | Sep 15 | Deep clone — create, independence, incremental sync | 📖 💻 |
| Wed | Sep 16 | Liquid Clustering — `CLUSTER BY`, vs partitioning + Z-Order | 📖 💻 |
| Thu | Sep 17 | Change clustering columns with `ALTER TABLE` | 📖 💻 |
| Fri | Sep 18 | Deletion Vectors — enable, soft delete behavior | 📖 |
| Sat | Sep 19 | Table constraints — NOT NULL, CHECK | 📖 💻 |
| Sun | Sep 20 | Hands-on: clones + liquid clustering exercises | 💻 |

---

### Week 20 — Sep 21–27
> Goal: Advanced MERGE patterns + Delta properties

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Sep 21 | `WHEN NOT MATCHED BY SOURCE THEN DELETE` — full sync pattern | 📖 💻 |
| Tue | Sep 22 | MERGE with audit columns — `current_timestamp()`, `current_user()` | 📖 💻 |
| Wed | Sep 23 | Conditional MERGE — only update if value changed | 📖 💻 |
| Thu | Sep 24 | Delta table properties reference — all key `TBLPROPERTIES` | 📖 |
| Fri | Sep 25 | Review advanced Delta cheat sheet | 📖 |
| Sat | Sep 26 | Hands-on: advanced MERGE scenarios end-to-end | 💻 |
| Sun | Sep 27 | Practice questions — advanced Delta Lake | 📝 |

---

### Week 21 — Sep 28–Oct 4
> Goal: Structured Streaming triggers, output modes, watermarking

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Sep 28 | Triggers — `processingTime`, `once`, `availableNow` — when to use each | 📖 |
| Tue | Sep 29 | Output modes — `append`, `complete`, `update` — rules for each | 📖 |
| Wed | Sep 30 | Watermarking — concept, `withWatermark` syntax | 📖 💻 |
| Thu | Oct 1 | Window types — tumbling, sliding, session | 📖 💻 |
| Fri | Oct 2 | Stateful streaming aggregations | 📖 💻 |
| Sat | Oct 3 | Hands-on: watermarked aggregation pipeline end-to-end | 💻 |
| Sun | Oct 4 | Review streaming notes | 📖 |

---

### Week 22 — Oct 5–11
> Goal: Advanced streaming patterns

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Oct 5 | Streaming deduplication with `dropDuplicates` + watermark | 📖 💻 |
| Tue | Oct 6 | `foreachBatch` — write to multiple sinks, custom logic | 📖 💻 |
| Wed | Oct 7 | Rate limiting — `maxFilesPerTrigger`, `maxBytesPerTrigger` | 📖 |
| Thu | Oct 8 | Streaming monitoring — `lastProgress`, `status`, `recentProgress` | 📖 💻 |
| Fri | Oct 9 | Streaming + Delta — `startingVersion`, `startingTimestamp` | 📖 💻 |
| Sat | Oct 10 | Hands-on: `foreachBatch` multi-sink pipeline | 💻 |
| Sun | Oct 11 | Practice questions — streaming | 📝 |

---

### Week 23 — Oct 12–18
> Goal: Performance optimization

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Oct 12 | File size optimization — target 128MB–1GB, OPTIMIZE | 📖 💻 |
| Tue | Oct 13 | Partitioning vs Z-Ordering vs Liquid Clustering — full comparison | 📖 |
| Wed | Oct 14 | Bloom filter indexes — create, when to use, fpp parameter | 📖 💻 |
| Thu | Oct 15 | AQE deep dive — skew handling, broadcast conversion | 📖 |
| Fri | Oct 16 | Photon engine — what it accelerates, what it doesn't | 📖 |
| Sat | Oct 17 | Hands-on: Spark UI analysis — diagnose a slow job | 💻 |
| Sun | Oct 18 | Practice questions — performance | 📝 |

---

### Week 24 — Oct 19–25
> Goal: Security and Unity Catalog

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Oct 19 | Unity Catalog — hierarchy, three-part namespace | 📖 |
| Tue | Oct 20 | `GRANT` / `REVOKE` — USAGE required at every level | 📖 💻 |
| Wed | Oct 21 | Row filters — `CREATE FUNCTION`, `ALTER TABLE SET ROW FILTER` | 📖 💻 |
| Thu | Oct 22 | Column masks — `CREATE FUNCTION`, `ALTER COLUMN SET MASK` | 📖 💻 |
| Fri | Oct 23 | Databricks Secrets — scopes, `dbutils.secrets.get()` | 📖 💻 |
| Sat | Oct 24 | Data lineage — system tables, lineage queries | 📖 💻 |
| Sun | Oct 25 | Practice questions — security and governance | 📝 |

---

### Week 25 — Oct 26–Nov 1
> Goal: Monitoring, CI/CD + first full Professional mock exam

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Oct 26 | Spark UI — Jobs, Stages, Tasks tabs, diagnosing skew | 📖 💻 |
| Tue | Oct 27 | System tables — query history, audit log, billing | 📖 💻 |
| Wed | Oct 28 | Testing — pytest unit tests for transformation functions | 📖 💻 |
| Thu | Oct 29 | Databricks Asset Bundles — structure, `databricks.yml`, CLI commands | 📖 |
| Fri | Oct 30 | CI/CD flow — Dev → Staging → Prod promotion | 📖 |
| Sat | Nov 1 | **Full Professional Practice Exam — Attempt 1** | 📝 |
| Sun | Nov 2 | Review ALL incorrect answers, map to notes | 📝 |

---

### Week 26 — Nov 2–10
> Goal: Final review + pass the exam

| Day | Date | Topic | Type |
|-----|------|-------|------|
| Mon | Nov 2 | Re-study any topic scored below 75% | 📖 |
| Tue | Nov 3 | Re-study any topic scored below 75% | 📖 |
| Wed | Nov 4 | Review `Phase4_Data_Engineer_Professional/cheat_sheet.md` | 📖 |
| Thu | Nov 5 | **Full Professional Practice Exam — Attempt 2** | 📝 |
| Fri | Nov 6 | Light review only — must score 80%+ before booking | 📖 |
| Sat | Nov 7 | Rest — mental preparation only | |
| Sun/Mon | Nov 8–9 | ✅ **TAKE DATA ENGINEER PROFESSIONAL EXAM** | |

---

## Summary at a Glance

| Phase | Dates | Weeks | Exam? |
|-------|-------|-------|-------|
| Phase 0 — Python Basics | May 13–24 | 1–2 | No |
| Phase 1 — Data Analyst Associate | May 25–Jun 21 | 3–6 | **YES — Jun 20** |
| Phase 2 — Spark Associate | Jun 22–Aug 2 | 7–12 | No (80% gate) |
| Phase 3 — Data Engineer Associate | Aug 3–Sep 13 | 13–18 | No (80% gate) |
| Phase 4 — Data Engineer Professional | Sep 14–Nov 9 | 19–26 | **YES — Nov 8–9** |

## Daily Time Commitment

| Day | Time | Split |
|-----|------|-------|
| Mon–Fri | 1.5 hours | 45 min theory + 30 min hands-on + 15 min notes |
| Saturday | 3 hours | Deep hands-on practice |
| Sunday | 2 hours | Review + practice questions |
| **Per week** | **~12.5 hours** | |

## 80% Gate Rule
Before moving to the next phase, score 80%+ on the official Databricks practice exam.
If below 80% — add one extra week of review before retesting. Do not skip the gate.
