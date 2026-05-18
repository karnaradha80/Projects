# Week 5 — Monitoring & Logging

## Study Checklist
- [ ] Navigate Spark UI and interpret key tabs
- [ ] Find slow stages in a Spark job using the Spark UI
- [ ] Set up job failure email notifications
- [ ] Query audit logs from system tables
- [ ] Monitor a streaming query using lastProgress

## Spark UI — Understanding Job Execution

### Key Tabs in Spark UI
```
Spark UI (http://<driver>:4040)
├── Jobs         ← list of all jobs triggered by actions
├── Stages       ← each job broken into stages (separated by shuffles)
├── Tasks        ← individual work units per stage, per executor
├── Storage      ← cached RDDs/DataFrames
├── Environment  ← Spark configuration values
├── Executors    ← executor health, memory, task counts
└── SQL/DataFrame ← visual query plan for structured queries
```

### Diagnosing Performance Issues
```
1. Jobs tab → find the slow job (high duration)
2. Stages tab → find the slow stage (high shuffle read/write)
3. Tasks tab → look for:
   - Skewed tasks (one task takes 10x longer)
   - High GC time (memory pressure)
   - Spill to disk (partition too large for memory)
4. SQL tab → look at query plan:
   - Exchange = shuffle (expensive)
   - FileScan with pushdown = good (filter applied at read)
   - BroadcastHashJoin = good (no shuffle)
   - SortMergeJoin = expensive (full shuffle)
```

### Key Metrics to Watch
| Metric | High Value Means |
|--------|-----------------|
| Shuffle Read/Write | Wide transformation — lots of data movement |
| GC Time | Memory pressure — executors spending too much time garbage collecting |
| Spill (Memory) | Partition too large for RAM |
| Spill (Disk) | Even disk spill — very large partitions |
| Task Duration Variance | Data skew — some partitions much larger |

## Cluster Event Logs

```python
# Access cluster logs via Databricks UI:
# Compute → Cluster → Event Log tab
# Events include: cluster creation, start, terminate, resize, errors

# Driver logs
# Compute → Cluster → Driver Logs
# Includes: stdout (print statements), stderr (errors/warnings), log4j

# Access logs programmatically
dbutils.fs.ls("dbfs:/cluster-logs/<cluster-id>/")
```

## Job Monitoring & Alerting

### Job Run History
```
Workflows → Job → Runs tab
- Status: Success / Failed / Running / Skipped
- Duration, start time, triggered by (schedule or manual)
- Click a run → see task-level status and logs
```

### Setting Up Notifications
```python
# In Job definition (JSON / UI):
{
  "email_notifications": {
    "on_start": ["engineer@company.com"],
    "on_success": [],
    "on_failure": ["engineer@company.com", "manager@company.com"],
    "no_alert_for_skipped_runs": true
  }
}
```

### Retry Configuration
```python
{
  "max_retries": 3,
  "min_retry_interval_millis": 300000,   # 5 minutes between retries
  "retry_on_timeout": true
}
```

## Databricks System Tables (Unity Catalog)

### Available System Tables
```sql
-- All system tables are in: system.*
SHOW SCHEMAS IN system;
-- billing, access, compute, lakeflow, etc.

-- Query history (all SQL queries run)
SELECT
  statement_id,
  executed_by,
  statement_text,
  execution_status,
  total_duration_ms,
  start_time
FROM system.query.history
WHERE start_time > current_timestamp() - INTERVAL 1 DAY
  AND execution_status = 'FAILED'
ORDER BY total_duration_ms DESC;

-- Table access audit log
SELECT
  event_time,
  user_identity.email AS user,
  action_name,
  request_params:full_name_arg AS table_name
FROM system.access.audit
WHERE action_name = 'getTable'
  AND event_time > current_timestamp() - INTERVAL 7 DAYS;

-- Cluster usage / billing
SELECT
  workspace_id,
  cluster_id,
  usage_date,
  usage_quantity,
  usage_unit
FROM system.billing.usage
WHERE usage_date >= '2024-06-01'
ORDER BY usage_quantity DESC;
```

## DLT Pipeline Monitoring

### Event Log
```python
# DLT automatically creates an event log for each pipeline
# Query it to see expectations, data quality stats, flow progress

# Find your pipeline's event log location
# UI: Delta Live Tables → Pipeline → Event Log tab

# Query via SQL
SELECT
  timestamp,
  event_type,
  message,
  details:flow_name AS flow,
  details:num_output_rows AS output_rows
FROM event_log("pipeline_id_here")
WHERE event_type IN ('flow_progress', 'create_update', 'user_action')
ORDER BY timestamp DESC;

-- Data quality metrics
SELECT
  details:flow_name        AS table_name,
  details:name             AS expectation_name,
  details:passed_records   AS passed,
  details:failed_records   AS failed
FROM event_log("pipeline_id_here")
WHERE event_type = 'flow_progress'
  AND details:metrics IS NOT NULL;
```

## Structured Streaming Monitoring

### Query Progress Metrics
```python
query = df.writeStream.table("output").start()

# Current status
print(query.status)
# {'message': 'Processing new data', 'isDataAvailable': True}

# Last batch stats (most useful)
progress = query.lastProgress
print(f"Input rows/sec: {progress['inputRowsPerSecond']}")
print(f"Processed rows/sec: {progress['processedRowsPerSecond']}")
print(f"Batch duration: {progress['batchDuration']} ms")
print(f"Input rows this batch: {progress['numInputRows']}")
print(f"Watermark: {progress['eventTime']['watermark']}")

# Recent batches (list)
for p in query.recentProgress:
    print(p['batchId'], p['numInputRows'], p['batchDuration'])
```

### Streaming UI
```
Spark UI → Streaming tab
- Shows: input rate, processing rate, batch duration over time
- Graph shows if streaming is keeping up or falling behind
- If processing rate < input rate → pipeline is falling behind
```

## Ganglia UI (Cluster Metrics)
```
Compute → Cluster → Metrics tab (Ganglia)
- CPU usage per executor
- Memory usage (heap, off-heap)
- Network I/O
- Disk I/O

High CPU + Low memory → CPU-bound (more cores needed)
Low CPU + High memory → Memory-bound (larger instances or more RAM)
High network I/O → Too much shuffle (optimize joins/partitioning)
```

## Exam Tips
- Spark UI Stages tab is the best place to find shuffle bottlenecks
- Skewed tasks show as one task taking much longer than others in Tasks tab
- System tables in `system.*` require Unity Catalog
- DLT event log captures expectations pass/fail counts per batch
- Streaming `lastProgress` has `inputRowsPerSecond` and `processedRowsPerSecond`
- Job retry: up to N times, with configurable delay between retries
- Email notifications: on_start, on_success, on_failure are the three events

## Notes
_(Write your own notes here as you study)_
