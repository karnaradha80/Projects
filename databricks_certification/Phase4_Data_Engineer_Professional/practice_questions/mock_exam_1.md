# Phase 4 — Data Engineer Professional Practice Questions (Set 1)

## Advanced Delta Lake

**Q1.** A team creates a SHALLOW CLONE of a production table for testing. A week later, the production table has VACUUM run with default settings. What is the risk to the clone?
- A) None — shallow clones are independent
- B) The clone's transaction log is deleted
- C) Files the clone references may be deleted, breaking the clone
- D) The clone automatically upgrades to a deep clone

**Answer: C** — Shallow clones share data files with the source. VACUUM on the source removes old files. If the clone references files older than 7 days, it breaks. Use deep clone for independent copies.

---

**Q2.** A team wants to change the clustering columns of an existing Delta table without rewriting all the data. What feature makes this possible?
- A) Z-Ordering
- B) Partitioning with ALTER TABLE
- C) Liquid Clustering
- D) Deletion Vectors

**Answer: C** — Liquid Clustering allows changing clustering columns using `ALTER TABLE t CLUSTER BY (new_col)` without a full data rewrite. Traditional partitioning requires a complete rewrite to change partition columns.

---

**Q3.** A Delta table receives thousands of small DELETE operations per hour. Which feature reduces write amplification for these deletes?
- A) OPTIMIZE ZORDER
- B) Deletion Vectors
- C) Auto Compact
- D) Change Data Feed

**Answer: B** — Deletion Vectors perform soft deletes by writing a small marker file instead of rewriting entire data files. Physical removal happens at next VACUUM or OPTIMIZE.

---

## Structured Streaming

**Q4.** A streaming pipeline uses `groupBy("region").agg(sum("amount"))` without a watermark. What problem will this cause over time?
- A) The pipeline fails immediately — aggregation not allowed without watermark
- B) State size grows unboundedly — memory will eventually be exhausted
- C) Aggregation results are incorrect without watermark
- D) Spark automatically adds a watermark

**Answer: B** — Without a watermark, Spark must maintain state for every key (region) forever to handle late-arriving data. State accumulates without bound, eventually causing OOM errors.

---

**Q5.** A streaming job must write to both a Delta table and an external REST API for each micro-batch. Which feature enables this?
- A) Multiple writeStream calls on the same DataFrame
- B) `foreachBatch` with custom write logic
- C) `foreach` sink
- D) Dual output mode

**Answer: B** — `foreachBatch` provides a function that receives each micro-batch as a regular DataFrame, allowing you to write to multiple sinks or apply custom logic.

---

**Q6.** A pipeline uses `trigger(once=True)` to process a backlog of 500GB of data. The job times out after 2 hours. What is the better alternative?
- A) Increase cluster size and retry with `once=True`
- B) Use `trigger(availableNow=True)` — processes in multiple micro-batches, recoverable on failure
- C) Use `trigger(processingTime="0 seconds")`
- D) Split the data manually into smaller chunks

**Answer: B** — `availableNow=True` processes all available data in multiple micro-batches, checkpointing after each. On failure, it resumes from the last checkpoint. `once=True` is a single micro-batch — no mid-way recovery.

---

**Q7.** A streaming query uses `outputMode("complete")` with a `groupBy` aggregation. The result table has 10 million rows. What concern should the team have?
- A) Complete mode is not supported with groupBy
- B) Complete mode rewrites the entire 10M-row result every trigger — high I/O cost
- C) Complete mode only outputs changed rows
- D) Complete mode requires watermarking

**Answer: B** — `complete` mode rewrites the entire result table every trigger. For 10 million rows, this creates massive I/O overhead every micro-batch. Use `update` mode for large aggregation results instead.

---

## Performance Optimization

**Q8.** A query runs slow on a 500GB Delta table filtered by `customer_id`. The table has 5 million unique customer IDs. What is the BEST optimization strategy?
- A) Partition by customer_id
- B) Create a Bloom filter index on customer_id
- C) Z-ORDER BY customer_id
- D) Cache the table in memory

**Answer: B** — 5 million unique values is too high-cardinality for partitioning (millions of tiny folders). Bloom filter is ideal for high-cardinality equality lookups — it skips files that definitely don't contain the queried customer_id.

---

**Q9.** A Spark job stage shows one task taking 45 minutes while all other tasks complete in 2 minutes. What does this indicate?
- A) Cluster is undersized
- B) Data skew — one partition has disproportionately more data
- C) The query plan is suboptimal
- D) Broadcast join threshold is too low

**Answer: B** — Extreme task duration variance = data skew. One partition (mapped to one task) contains far more data than others. Solutions: AQE skew handling, salting the join key, or repartitioning.

---

## Security & Governance

**Q10.** A data engineer grants `SELECT` on a table to the `analysts` group but analysts still cannot query it. What is most likely missing?
- A) The table needs to be published first
- B) USAGE grants on the catalog AND schema are missing
- C) Analysts need the MODIFY permission too
- D) The grant needs to be applied to each table column

**Answer: B** — Unity Catalog requires USAGE at every level. Without `GRANT USAGE ON CATALOG` and `GRANT USAGE ON SCHEMA`, users cannot navigate to the table even if SELECT is granted.

---

**Q11.** A column mask function is applied to the `salary` column. A member of the `finance` group sees real values; all other users see NULL. A new user joins the `finance` group. When do they start seeing real salary values?
- A) After the table is refreshed
- B) Immediately — group membership is evaluated at query time
- C) After the mask is reapplied
- D) After the next OPTIMIZE on the table

**Answer: B** — Column masks and row filters use `is_member()` evaluated at query runtime, not at table definition time. Group membership changes take effect immediately on the next query.

---

## Monitoring & CI/CD

**Q12.** A CI/CD pipeline must ensure the deployment runs in a clean, reproducible environment with no shared state from previous runs. Which cluster type achieves this?
- A) All-purpose cluster (always running)
- B) High-concurrency cluster
- C) Job cluster (created fresh per run, terminated after)
- D) Single-node cluster

**Answer: C** — Job clusters are created fresh for each job run and terminated when done. No shared state between runs — ensures reproducible, isolated execution. All-purpose clusters persist and can accumulate state.

---

**Q13.** A DLT pipeline has `@dlt.expect_or_fail("no_nulls", "id IS NOT NULL")`. During a production run, 3 rows have null IDs. What happens?
- A) The 3 rows are dropped and pipeline continues
- B) The pipeline stops with a failure — all data from that update is rolled back
- C) The 3 rows are written to a quarantine table
- D) A warning is logged and rows are kept

**Answer: B** — `expect_or_fail` treats violations as a hard failure. The entire pipeline update fails and is rolled back. No partial updates are committed.

---

**Q14.** A team uses `dbutils.secrets.get(scope="prod", key="db-password")` in a notebook. A colleague tries to display the value using `print(dbutils.secrets.get(...))`. What appears in the notebook output?
- A) The actual password value
- B) `[REDACTED]`
- C) An error — secrets cannot be printed
- D) An asterisk-masked value like `****`

**Answer: B** — Databricks secrets are automatically redacted in all notebook outputs. Even if you explicitly try to print a secret, Databricks replaces it with `[REDACTED]`.
