# Data Engineer Associate — Cheat Sheet

## Delta Lake Core Commands
```sql
CREATE TABLE t USING DELTA LOCATION '/path/';
INSERT INTO t VALUES (...);
UPDATE t SET col = val WHERE condition;
DELETE FROM t WHERE condition;

DESCRIBE HISTORY t;
DESCRIBE DETAIL t;

-- Time Travel
SELECT * FROM t VERSION AS OF 5;
SELECT * FROM t TIMESTAMP AS OF '2024-01-01';
RESTORE TABLE t TO VERSION AS OF 3;

-- Maintenance
OPTIMIZE t;
OPTIMIZE t ZORDER BY (col1, col2);
VACUUM t RETAIN 168 HOURS;
```

## MERGE (know cold)
```sql
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

## Change Data Feed
```sql
-- Enable
ALTER TABLE t SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Read in streaming
spark.readStream.option("readChangeFeed", "true").table("t")

-- Read batch
spark.read.option("readChangeFeed", "true")
  .option("startingVersion", 0).table("t")
```

## Auto Loader
```python
spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/schema/path")
  .load("/raw/data/")
  .writeStream
  .option("checkpointLocation", "/checkpoint/path")
  .table("bronze_table")
```

## Delta Live Tables
```python
import dlt

@dlt.table
def bronze(): return spark.readStream.format("cloudFiles").load("/raw/")

@dlt.table
@dlt.expect("valid_id", "id IS NOT NULL")           # warn, keep row
@dlt.expect_or_drop("valid_email", "email LIKE '%@%'")  # drop row
@dlt.expect_or_fail("not_null_amount", "amount IS NOT NULL")  # fail pipeline
def silver(): return dlt.read_stream("bronze").filter("active = true")

@dlt.table
def gold(): return dlt.read("silver").groupBy("region").agg(sum("amount"))
```

## Medallion Architecture
| Layer | Purpose | Pattern |
|-------|---------|---------|
| Bronze | Raw, as-is | Append-only, Auto Loader |
| Silver | Cleaned, filtered | Dedup, MERGE, validated |
| Gold | Business aggregates | GROUP BY, joins, reporting |

## Key Gotchas
- VACUUM default retention = 168 hours (7 days)
- CDF cannot capture changes BEFORE it was enabled
- Auto Loader schema location must be separate from checkpoint
- DLT expect_or_drop = silent drop; expect = warn only; expect_or_fail = stop pipeline
- Managed table = Databricks owns data + metadata
- External table = you own data location, Databricks owns metadata
