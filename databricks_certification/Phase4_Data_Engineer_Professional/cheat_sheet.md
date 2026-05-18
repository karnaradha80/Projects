# Data Engineer Professional — Cheat Sheet

## Advanced Delta Lake
```sql
-- Shallow clone (metadata only, references original files)
CREATE TABLE clone_t SHALLOW CLONE source_t;

-- Deep clone (copies all data files)
CREATE TABLE clone_t DEEP CLONE source_t;

-- Liquid clustering (alternative to partitioning)
CREATE TABLE t (id INT, date DATE, region STRING)
CLUSTER BY (date, region);

-- Enable deletion vectors (faster deletes/updates)
ALTER TABLE t SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');
```

## Structured Streaming
```python
# Triggers
.trigger(processingTime="1 minute")   # fixed interval
.trigger(once=True)                    # one-shot (single micro-batch)
.trigger(availableNow=True)            # one-shot, multiple micro-batches

# Output modes
.outputMode("append")    # new rows only — stateless streaming
.outputMode("complete")  # full result rewritten — aggregations
.outputMode("update")    # changed rows only

# Watermark (late data)
df.withWatermark("event_time", "10 minutes")
  .groupBy(window("event_time", "5 minutes"), "region")
  .agg(sum("amount"))

# foreachBatch (write to multiple sinks)
def write_batch(df, epoch_id):
    df.write.mode("append").saveAsTable("table_a")
    df.write.mode("append").saveAsTable("table_b")

query = df.writeStream.foreachBatch(write_batch).start()

# Deduplication in streaming
df.withWatermark("event_time", "1 hour")
  .dropDuplicates(["id", "event_time"])
```

## Unity Catalog Security
```sql
-- Row filter
CREATE FUNCTION row_filter(dept STRING)
RETURN is_member(dept);
ALTER TABLE employees SET ROW FILTER row_filter ON (dept);

-- Column mask
CREATE FUNCTION mask_salary(salary DOUBLE)
RETURN CASE WHEN is_member('finance') THEN salary ELSE -1 END;
ALTER TABLE employees ALTER COLUMN salary SET MASK mask_salary;

-- Dynamic view (alternative)
CREATE VIEW secure_view AS
SELECT *, CASE WHEN is_member('hr') THEN salary ELSE NULL END as salary
FROM employees;
```

## Secrets
```python
# In notebook — never hardcode credentials
token = dbutils.secrets.get(scope="my-scope", key="api-token")
```

## CI/CD with Asset Bundles
```yaml
# databricks.yml
bundle:
  name: my_pipeline

resources:
  jobs:
    my_job:
      name: "Production Pipeline"
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./notebooks/ingest
```

## Monitoring
```python
# Streaming query progress
query.lastProgress         # last micro-batch stats
query.status               # current status
query.recentProgress       # list of recent micro-batch stats

# Key metrics to watch
# inputRowsPerSecond, processedRowsPerSecond
# numInputRows, batchDuration
```

## Key Gotchas — Professional Level
- `availableNow` > `once` for large backfill (uses multiple micro-batches)
- Watermark delay = how late data is accepted; data older = dropped
- `complete` output mode requires aggregation — cannot use with append-only
- Liquid clustering = no partitioning needed; auto-optimizes on write
- Deep clone is independent — changes don't affect source
- Shallow clone shares files — vacuum on source can break clone
- Deletion vectors = soft deletes (marked, not removed until VACUUM)
- Row filter + column mask = Unity Catalog only, not legacy Hive metastore
- Asset Bundles replaces legacy dbx CLI
