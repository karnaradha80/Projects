# Week 2 — Delta Lake Advanced

## Study Checklist
- [ ] Write a complete MERGE INTO statement from scratch
- [ ] Run OPTIMIZE and ZORDER on a table
- [ ] Run VACUUM and understand the retention risk
- [ ] Enable and read Change Data Feed on a table
- [ ] Practice schema evolution with mergeSchema option

## MERGE INTO (Upsert — most important Delta command)

### Full Syntax
```sql
MERGE INTO target_table t
USING source_table s
ON t.id = s.id

WHEN MATCHED AND s.operation = 'DELETE'
  THEN DELETE

WHEN MATCHED AND s.operation = 'UPDATE'
  THEN UPDATE SET
    t.name   = s.name,
    t.salary = s.salary,
    t.updated_at = current_timestamp()

WHEN MATCHED
  THEN UPDATE SET *           -- update all matching columns

WHEN NOT MATCHED
  THEN INSERT *               -- insert all columns

WHEN NOT MATCHED BY SOURCE    -- rows in target with no match in source
  THEN DELETE;                -- useful for full sync
```

### Python MERGE
```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "employees")
source = spark.read.table("staging_employees")

target.alias("t").merge(
    source.alias("s"),
    "t.id = s.id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

## OPTIMIZE — File Compaction
```sql
-- Compact small files into larger ones (target ~1GB per file)
OPTIMIZE employees;

-- Compact + Z-Order (co-locate related data in files)
OPTIMIZE employees ZORDER BY (dept, hire_date);

-- Partial optimize (specific partition)
OPTIMIZE employees WHERE hire_date >= '2024-01-01' ZORDER BY (dept);
```

## Z-Ordering vs Partitioning
| | Partitioning | Z-Ordering |
|-|-------------|-----------|
| How it works | Separate folders by column value | Co-locates data within files |
| Best for | High-cardinality cols (date, country) | Medium-cardinality cols used in filters |
| File structure | Physical folder separation | Data layout within files |
| Combined use | Yes — both can be used together | Yes |

```
-- Partitioned table folder structure
/employees/
  ├── country=US/
  │   └── part-00001.parquet
  └── country=UK/
      └── part-00002.parquet

-- Z-Ordered — same folder, but data sorted/clustered inside files
/employees/
  └── part-00001.parquet   ← engineering rows grouped together in file
```

## VACUUM — Remove Old Files
```sql
-- Default: remove files older than 7 days (168 hours)
VACUUM employees;

-- Custom retention
VACUUM employees RETAIN 336 HOURS;   -- 14 days

-- DRY RUN — see what would be deleted (does not delete)
VACUUM employees DRY RUN;

-- WARNING: removing below 7-day default requires disabling safety check
SET spark.databricks.delta.retentionDurationCheck.enabled = false;
VACUUM employees RETAIN 0 HOURS;     -- dangerous — breaks time travel
```

**Risk:** After VACUUM, time travel to versions that reference deleted files will fail.

## Auto Optimize (Table Properties)
```sql
-- Automatically compact files on write
ALTER TABLE employees SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact'   = 'true'
);

-- optimizeWrite: writes optimal file sizes (128MB target)
-- autoCompact: triggers background compaction after write
```

## Change Data Feed (CDF / CDC)

### Enable CDF
```sql
-- Must be enabled BEFORE capturing changes
ALTER TABLE employees SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Or at table creation
CREATE TABLE employees (...) TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
```

### Read CDF — Batch
```python
# Read changes between two versions
changes = spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 5) \
  .option("endingVersion", 10) \
  .table("employees")

# Read changes since a timestamp
changes = spark.read \
  .option("readChangeFeed", "true") \
  .option("startingTimestamp", "2024-06-01") \
  .table("employees")
```

### Read CDF — Streaming
```python
changes = spark.readStream \
  .option("readChangeFeed", "true") \
  .option("startingVersion", "latest") \
  .table("employees")
```

### CDF Columns Added
| Column | Values | Meaning |
|--------|--------|---------|
| `_change_type` | `insert`, `update_preimage`, `update_postimage`, `delete` | Type of change |
| `_commit_version` | Integer | Delta version when change happened |
| `_commit_timestamp` | Timestamp | When the change was committed |

## Schema Evolution
```python
# Add new columns on write (schema merging)
df_new.write.option("mergeSchema", "true").mode("append").saveAsTable("employees")

# Replace schema entirely on overwrite
df_new.write.option("overwriteSchema", "true").mode("overwrite").saveAsTable("employees")

# SQL equivalent
ALTER TABLE employees ADD COLUMNS (bonus DOUBLE);
ALTER TABLE employees CHANGE COLUMN salary salary DOUBLE COMMENT 'Annual salary';
```

## Exam Tips
- MERGE is the single most tested command — know all WHEN clauses
- CDF only captures changes AFTER it was enabled — no retroactive history
- VACUUM default = 168 hours; below this breaks time travel for deleted files
- `optimizeWrite` = during write; `autoCompact` = after write (separate triggers)
- Z-Order only improves queries that filter on Z-ordered columns
- Schema `mergeSchema` = additive (new columns); `overwriteSchema` = destructive

## Notes
_(Write your own notes here as you study)_
