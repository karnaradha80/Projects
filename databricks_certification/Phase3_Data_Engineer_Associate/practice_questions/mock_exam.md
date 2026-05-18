# Phase 3 — Data Engineer Associate Practice Questions

## Delta Lake

**Q1.** A data engineer runs VACUUM on a Delta table with default settings. A colleague then tries to query `VERSION AS OF 3` which was created 10 days ago. What happens?
- A) Query succeeds — transaction log still has version 3
- B) Query fails — data files for version 3 were deleted by VACUUM
- C) Query returns empty results
- D) Query automatically falls back to the latest version

**Answer: B** — VACUUM default retention is 7 days. Files for version 3 (10 days old) were deleted. Transaction log entry exists but data files are gone.

---

**Q2.** A team enables Change Data Feed on a Delta table that already has 1 million rows. They then run a query to read CDF changes from `startingVersion=0`. What does the result contain?
- A) All 1 million existing rows as inserts
- B) Only changes made AFTER CDF was enabled
- C) An error — CDF cannot read from version 0
- D) All rows plus all future changes

**Answer: B** — CDF only captures changes made AFTER it was enabled. Pre-existing data is NOT retroactively captured.

---

**Q3.** Which command would you use to see the number of files, total size, and location of a Delta table?
- A) `DESCRIBE TABLE orders`
- B) `DESCRIBE HISTORY orders`
- C) `DESCRIBE DETAIL orders`
- D) `SHOW TABLE EXTENDED orders`

**Answer: C** — `DESCRIBE DETAIL` shows file count, size, location, format, and partitioning info.

---

**Q4.** A MERGE operation needs to: update matching rows, insert new rows, AND delete rows from the target that no longer exist in the source. Which clause handles the deletions?
- A) `WHEN MATCHED THEN DELETE`
- B) `WHEN NOT MATCHED THEN DELETE`
- C) `WHEN NOT MATCHED BY SOURCE THEN DELETE`
- D) `WHEN NOT MATCHED BY TARGET THEN DELETE`

**Answer: C** — `WHEN NOT MATCHED BY SOURCE` targets rows that exist in the target but have no matching row in the source.

---

**Q5.** A team wants to co-locate data for `customer_id` (high cardinality — 5 million unique values) to speed up point lookups. What should they use?
- A) Partition by customer_id
- B) ZORDER BY customer_id
- C) Bucket by customer_id
- D) Sort by customer_id

**Answer: B** — Partitioning by a high-cardinality column creates millions of tiny folders. Z-Ordering co-locates data within files — correct for high-cardinality columns used in filters.

---

## Auto Loader

**Q6.** A pipeline uses Auto Loader to ingest files. After a server crash, the job restarts. What ensures files are not reprocessed?
- A) The schema location
- B) The checkpoint location
- C) The cloudFiles.format option
- D) Delta transaction log

**Answer: B** — Checkpoint location stores processed file offsets. On restart, Auto Loader reads the checkpoint and resumes from where it left off.

---

**Q7.** A team receives 10 million new files per day. Which Auto Loader mode should they use to avoid performance issues?
- A) Directory listing mode
- B) File notification mode
- C) Schema inference mode
- D) Batch mode

**Answer: B** — File notification mode uses cloud event queues (SQS, Event Grid) to receive file arrival notifications. Directory listing mode must scan all files each trigger — infeasible at 10 million files/day.

---

**Q8.** An Auto Loader pipeline encounters a new column in the source files that wasn't in the original schema. Which option preserves pipeline continuity while adding the new column?
- A) `.option("failOnNewColumns", "true")`
- B) `.option("cloudFiles.rescuedDataColumn", "_rescued")`
- C) `.option("mergeSchema", "true")`
- D) `.option("overwriteSchema", "true")`

**Answer: C** — `mergeSchema=true` automatically adds new columns to the Delta table schema when they appear in incoming files.

---

## Delta Live Tables

**Q9.** A DLT table has this expectation: `@dlt.expect_or_drop("valid_email", "email LIKE '%@%'")`. What happens to a row where email = 'not_an_email'?
- A) Pipeline fails immediately
- B) Row is written to a quarantine table
- C) Row is silently dropped from the output table
- D) Row is kept but flagged with a warning

**Answer: C** — `expect_or_drop` silently removes rows that violate the constraint. The pipeline continues.

---

**Q10.** When should you use `dlt.read_stream()` instead of `dlt.read()` inside a DLT pipeline?
- A) When the source table is a Gold layer aggregate
- B) When you want incremental processing of new records only
- C) When the source is a static reference table
- D) When you want to recompute the full table every run

**Answer: B** — `dlt.read_stream()` processes only new/changed records incrementally. `dlt.read()` does a full batch read every run.

---

## Medallion Architecture

**Q11.** A Bronze layer table was accidentally populated with transformed data instead of raw source data. Why is this a problem?
- A) Bronze tables cannot store transformed data technically
- B) Raw data is lost — if transformation logic changes, you cannot reprocess
- C) Delta format requires raw data in Bronze
- D) This is acceptable if the transformation is simple

**Answer: B** — Bronze must store raw data so you can reprocess with new logic later. If Bronze is already transformed, the original source data is gone and you cannot recover or rerun differently.

---

**Q12.** Which layer of the Medallion architecture is the primary source for BI dashboards and reports?
- A) Bronze — freshest data
- B) Silver — cleaned data
- C) Gold — business aggregates
- D) Platinum — reporting layer

**Answer: C** — Gold layer contains business-level aggregations optimized for querying. Bronze and Silver are intermediate processing layers, not query-optimized for BI.
