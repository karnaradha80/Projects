# Databricks Data Engineer Professional — Master Study Plan

## Strategy
- **Take Exam:** Data Analyst Associate + Data Engineer Professional
- **Use as Prep Only (no exam):** Spark Associate + Data Engineer Associate
- **Gate:** Must score 80%+ on practice tests before moving to next phase
- **Total Investment:** ~$400 (2 exams) | ~7 months

---

## Overview Timeline

| Phase | Certification | Exam? | Duration | Target Date |
|-------|--------------|-------|----------|-------------|
| 0 | Python Basics (prerequisite) | No | 2 weeks | Week 2 |
| 1 | Data Analyst Associate | **YES** | 4 weeks | Week 6 |
| 2 | Spark Associate | No (prep only) | 6 weeks | Week 12 |
| 3 | Data Engineer Associate | No (prep only) | 6 weeks | Week 18 |
| 4 | Data Engineer Professional | **YES** | 8 weeks | Week 26 |

**Start Date:** 2026-05-13  
**Target Professional Exam:** ~November 2026

---

## Phase 0 — Python Basics (Weeks 1–2)
> Your C# background means Python syntax is quick to pick up

### Week 1
- [ ] Python vs C# — key differences (indentation, no types, dynamic)
- [ ] Variables, data types, strings, f-strings
- [ ] Lists, tuples, dictionaries, sets
- [ ] Loops (for, while), conditionals (if/elif/else)
- [ ] Functions, *args, **kwargs
- [ ] Lambda functions

### Week 2
- [ ] Classes and objects (map to C# classes)
- [ ] List comprehensions
- [ ] File I/O basics
- [ ] Exception handling (try/except — same as try/catch)
- [ ] Pandas basics — DataFrame = SQL result set
- [ ] Practice: solve 10 Python problems on HackerRank (Easy level)

### Resources
- Python.org official tutorial (free)
- "Python for C# Developers" articles online
- HackerRank Python track (free)

### Gate: Can you write a Python script that reads a CSV, filters rows, and aggregates? ✅

---

## Phase 1 — Data Analyst Associate (Weeks 3–6)
> Exam target | Your SQL background = 85% ready from day 1

### Week 3 — Databricks Platform + SQL Basics
- [ ] Create free Databricks Community Edition account
- [ ] Explore Workspace, Notebooks, SQL Editor
- [ ] Create a SQL Warehouse
- [ ] Run basic SELECT queries on sample datasets
- [ ] Understand Delta tables vs regular tables
- [ ] `DESCRIBE TABLE`, `SHOW TABLES`, `SHOW DATABASES`

### Week 4 — Databricks SQL Deep Dive
- [ ] Window functions in Databricks SQL (ROW_NUMBER, RANK, LAG, LEAD)
- [ ] CTEs and subqueries
- [ ] `CREATE TABLE USING DELTA`
- [ ] `MERGE INTO` syntax (upsert)
- [ ] Views (standard, materialized, dynamic)
- [ ] `DESCRIBE HISTORY` — Delta time travel via SQL

### Week 5 — Dashboards, Alerts & Governance
- [ ] Create a Databricks SQL Dashboard
- [ ] Set up a query alert
- [ ] Unity Catalog basics — Metastore > Catalog > Schema > Table
- [ ] `GRANT` / `REVOKE` permissions in SQL
- [ ] Row-level security basics

### Week 6 — Practice Exam + Exam
- [ ] Take official Databricks practice exam (Data Analyst Associate)
- [ ] Review all questions scored below 80%
- [ ] Re-study weak areas
- [ ] **Score 80%+ → Book and take the actual exam**

### Resources
- Databricks Academy: "Data Analysis with Databricks SQL" (free)
- Official exam guide: databricks.com/learn/certification
- Practice exam: ~$50 on Databricks website

### Exam Cost: $200

---

## Phase 2 — Spark Associate — Prep Only (Weeks 7–12)
> No exam — build PySpark foundation for Data Engineer path

### Week 7 — Spark Architecture
- [ ] What is Apache Spark? Driver vs Executor
- [ ] DAG (Directed Acyclic Graph) — how Spark plans execution
- [ ] Transformations (lazy) vs Actions (eager)
- [ ] Narrow vs Wide transformations
- [ ] Partitions and parallelism
- [ ] SparkSession, SparkContext basics

### Week 8 — DataFrame API
- [ ] `spark.read.csv/json/parquet()`
- [ ] `select`, `filter`, `where`, `withColumn`, `drop`
- [ ] `groupBy`, `agg`, `count`, `sum`, `avg`
- [ ] `orderBy`, `sort`, `limit`
- [ ] `alias`, `cast`, column expressions
- [ ] `show`, `printSchema`, `display`

### Week 9 — Joins + Functions
- [ ] Inner, left, right, outer joins in PySpark
- [ ] Broadcast joins — when and why
- [ ] Built-in functions: `col`, `lit`, `when`, `coalesce`
- [ ] String functions: `upper`, `lower`, `trim`, `split`, `regexp_replace`
- [ ] Date functions: `date_add`, `datediff`, `date_format`, `to_date`
- [ ] `explode`, `collect_list`, `collect_set`

### Week 10 — Spark SQL + UDFs
- [ ] `spark.sql()` — run SQL from Python
- [ ] Register temp views: `df.createOrReplaceTempView("name")`
- [ ] User-Defined Functions (UDFs) — Python function → Spark function
- [ ] `@udf` decorator pattern
- [ ] When NOT to use UDFs (performance cost)

### Week 11 — Performance + Optimization
- [ ] Caching: `df.cache()` vs `df.persist()`
- [ ] Repartition vs Coalesce
- [ ] Adaptive Query Execution (AQE)
- [ ] Explain plans: `df.explain(True)`
- [ ] Shuffle partitions: `spark.conf.set("spark.sql.shuffle.partitions", "200")`

### Week 12 — Practice Test
- [ ] Take official Spark Associate practice exam
- [ ] **Score 80%+ → Move to Phase 3 (do NOT pay for exam)**
- [ ] Below 80% → Review weak areas for 1 more week

### Resources
- Databricks Academy: "Apache Spark Programming with Databricks" (free)
- "Learning Spark" book (O'Reilly) — optional but excellent
- Spark documentation: spark.apache.org

---

## Phase 3 — Data Engineer Associate — Prep Only (Weeks 13–18)
> No exam — build the pipeline knowledge for Professional

### Week 13 — Delta Lake Foundations
- [ ] Why Delta Lake? Problems it solves over plain Parquet
- [ ] Transaction log (`_delta_log/`) — how it works
- [ ] ACID transactions on data lakes
- [ ] `CREATE TABLE USING DELTA`
- [ ] `INSERT`, `UPDATE`, `DELETE` on Delta tables
- [ ] `DESCRIBE HISTORY` and time travel (`VERSION AS OF`, `TIMESTAMP AS OF`)

### Week 14 — Delta Lake Advanced
- [ ] `MERGE INTO` — full upsert pattern (know this cold)
- [ ] `OPTIMIZE` and `ZORDER BY`
- [ ] `VACUUM` — retention and risk to time travel
- [ ] Change Data Feed (CDF) — enable, read, limitations
- [ ] Schema evolution: `mergeSchema`, `overwriteSchema`
- [ ] Managed vs External tables

### Week 15 — Auto Loader
- [ ] What problem Auto Loader solves
- [ ] Directory listing mode vs File notification mode
- [ ] Schema inference and schema evolution
- [ ] `cloudFiles` format options
- [ ] Checkpoint location purpose
- [ ] Hands-on: ingest CSV files from DBFS using Auto Loader

### Week 16 — Delta Live Tables (DLT)
- [ ] DLT vs standard notebooks — when to use each
- [ ] `@dlt.table` decorator
- [ ] `@dlt.expect`, `@dlt.expect_or_drop`, `@dlt.expect_or_fail`
- [ ] `LIVE` tables vs `STREAMING LIVE` tables
- [ ] DLT pipeline modes: Development vs Production
- [ ] Hands-on: build Bronze → Silver → Gold DLT pipeline

### Week 17 — Medallion Architecture + ELT
- [ ] Bronze layer: raw, append-only ingestion
- [ ] Silver layer: deduplicated, cleaned, filtered
- [ ] Gold layer: business aggregates, query-optimized
- [ ] ELT vs ETL — why ELT on Databricks
- [ ] Hands-on: implement full Medallion pipeline

### Week 18 — Practice Test
- [ ] Take official Data Engineer Associate practice exam
- [ ] **Score 80%+ → Move to Phase 4 (do NOT pay for exam)**
- [ ] Below 80% → Review weak areas for 1 more week

### Resources
- Databricks Academy: "Data Engineering with Databricks" (free)
- Delta Lake documentation: docs.delta.io
- Official exam study guide

---

## Phase 4 — Data Engineer Professional (Weeks 19–26)
> EXAM TARGET — this is what you're paying for

### Week 19 — Advanced Delta Lake
- [ ] CDF deep dive — consumer patterns, lag handling
- [ ] Liquid clustering (newer alternative to partitioning)
- [ ] Deletion vectors
- [ ] Table clones (shallow vs deep)
- [ ] Row-level concurrency
- [ ] `RESTORE` operations and recovery scenarios

### Week 20 — Structured Streaming at Scale
- [ ] Streaming triggers deep dive (processingTime, once, availableNow)
- [ ] Output modes (append, complete, update) — know every scenario
- [ ] Watermarking and late data handling
- [ ] Stateful streaming — aggregations, deduplication
- [ ] `foreachBatch` — write to multiple sinks
- [ ] Streaming + Delta Lake together

### Week 21 — Performance Optimization
- [ ] File size optimization — target 128MB-1GB per file
- [ ] Partitioning strategy — when to partition, what columns
- [ ] Z-Ordering vs Liquid Clustering
- [ ] Bloom filter indexes
- [ ] Caching strategies for production pipelines
- [ ] Photon engine — what it accelerates

### Week 22 — Security + Unity Catalog
- [ ] Unity Catalog architecture — metastore, catalogs, schemas
- [ ] Data lineage in Unity Catalog
- [ ] Row-level and column-level security
- [ ] Dynamic views for masking
- [ ] Service principals vs users vs groups
- [ ] Secret management with Databricks Secrets

### Week 23 — Monitoring + Logging
- [ ] Audit logs — what they capture, where they go
- [ ] Cluster event logs and metrics
- [ ] Job run history and alerting
- [ ] Ganglia UI vs Spark UI
- [ ] Structured Streaming query metrics
- [ ] Setting up job failure notifications

### Week 24 — Testing + Deployment (CI/CD)
- [ ] Databricks Repos — Git integration workflow
- [ ] Bundle CLI (Databricks Asset Bundles)
- [ ] Testing notebooks with pytest + `dbutils.notebook.run`
- [ ] CI/CD pipeline patterns (GitHub Actions / Azure DevOps)
- [ ] Environment promotion: Dev → Staging → Prod
- [ ] Deployment best practices

### Week 25 — Full Review + Mock Exams
- [ ] Take official Professional practice exam (attempt 1)
- [ ] Review all incorrect answers — map to study notes
- [ ] Re-study any topic below 75%
- [ ] Take practice exam again (attempt 2)
- [ ] **Score 80%+ consistently → Book the exam**

### Week 26 — Exam Week
- [ ] Light review only — no new topics
- [ ] Re-read cheat sheet daily
- [ ] **Take Databricks Certified Data Engineer Professional exam**

### Exam Cost: $200

---

## Practice Exam Scoring Gate

| Phase | Practice Exam | Score Gate | Action |
|-------|--------------|-----------|--------|
| End of Phase 1 | Data Analyst Associate | 80%+ | Book real exam |
| End of Phase 2 | Spark Associate | 80%+ | Move to Phase 3 (no exam) |
| End of Phase 3 | Data Engineer Associate | 80%+ | Move to Phase 4 (no exam) |
| End of Phase 4 | Data Engineer Professional | 80%+ | Book real exam |

---

## Daily Study Schedule (Recommended)

| Day Type | Time | Activity |
|----------|------|----------|
| Weekdays | 1 hour | Theory — read notes, watch videos |
| Weekdays | 30 min | Hands-on — Databricks Community Edition |
| Weekend | 3-4 hours | Deep dive + practice questions |

---

## Total Cost Summary

| Item | Cost |
|------|------|
| Data Analyst Associate exam | $200 |
| Data Analyst Associate practice exam | $50 |
| Data Engineer Professional exam | $200 |
| Data Engineer Professional practice exam | $50 |
| Databricks Academy courses | FREE |
| Databricks Community Edition | FREE |
| **Total** | **~$500** |

---

## Key Tools to Set Up (Do This Week)
1. Databricks Community Edition account — free at community.databricks.com
2. VS Code with Python extension — for local Python practice
3. Python 3.x installed locally
4. Databricks Academy account — academy.databricks.com (free)
