# Week 1 — Advanced Delta Lake

## Study Checklist
- [ ] Create shallow and deep clones and understand the difference
- [ ] Enable and test Liquid Clustering
- [ ] Understand Deletion Vectors and when they help
- [ ] Know the full MERGE syntax including WHEN NOT MATCHED BY SOURCE
- [ ] Compare table clone behaviors after VACUUM on source

## Table Clones

### Shallow Clone
```sql
-- Creates a new table that REFERENCES original data files (no copy)
CREATE TABLE silver_clone SHALLOW CLONE silver_sales;

-- With specific version
CREATE TABLE silver_clone SHALLOW CLONE silver_sales VERSION AS OF 5;

-- With specific timestamp
CREATE TABLE silver_clone SHALLOW CLONE silver_sales TIMESTAMP AS OF '2024-06-01';
```

**Shallow Clone behavior:**
- Zero copy — no data files duplicated
- Clone has its own transaction log
- Changes to clone don't affect source
- **Risk:** VACUUM on source removes files clone depends on → clone breaks
- Use for: dev/test against production data without copying cost

### Deep Clone
```sql
-- Copies all data files to new location (independent copy)
CREATE TABLE silver_backup DEEP CLONE silver_sales;
CREATE TABLE silver_backup DEEP CLONE silver_sales LOCATION '/backup/silver/';

-- Incremental deep clone (re-run to sync new changes)
CREATE OR REPLACE TABLE silver_backup DEEP CLONE silver_sales;
```

**Deep Clone behavior:**
- Full copy — all data files duplicated to new location
- Completely independent — VACUUM on source does not affect clone
- Can incrementally sync by re-running the command
- Copies table properties, partitioning, constraints
- Use for: disaster recovery, cross-environment migration, archiving

| | Shallow Clone | Deep Clone |
|-|--------------|-----------|
| Data copied | No (references) | Yes (full copy) |
| VACUUM safe | No (source VACUUM breaks clone) | Yes (independent) |
| Cost | Free | Storage cost |
| Incremental sync | No | Yes (re-run command) |

## Liquid Clustering (Alternative to Partitioning)

### Problem with Partitioning
- Partition column must be low-cardinality (date, country)
- Wrong partition column = many small files = slow queries
- Cannot change partitioning after table creation without rewrite
- Too many partitions = metadata overhead

### Liquid Clustering Solution
```sql
-- Create table with liquid clustering
CREATE TABLE sales (
  id INT,
  order_date DATE,
  region STRING,
  amount DECIMAL(10,2)
) CLUSTER BY (order_date, region);

-- Add clustering to existing table
ALTER TABLE sales CLUSTER BY (order_date, region);

-- Remove clustering
ALTER TABLE sales CLUSTER BY NONE;

-- Trigger clustering (like OPTIMIZE for partitioned tables)
OPTIMIZE sales;
```

**Liquid Clustering benefits:**
- Can cluster on high-cardinality columns (no folder explosion)
- Can change clustering columns without rewriting data
- Works with any column type
- Automatically applied incrementally during OPTIMIZE
- Better data skipping than Z-Ordering

## Deletion Vectors

### What Are Deletion Vectors?
- Soft delete mechanism — marks rows as deleted without rewriting files
- Before: DELETE rewrites entire data files (expensive)
- With deletion vectors: write a small "deleted rows" file instead

```sql
-- Enable deletion vectors
ALTER TABLE employees SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');
```

**When they help:**
- Frequent small DELETEs or UPDATEs on large tables
- Reduces write amplification significantly
- Actual files cleaned up during next VACUUM or OPTIMIZE

## Advanced MERGE Patterns

### WHEN NOT MATCHED BY SOURCE (full sync)
```sql
-- Sync target to exactly match source
-- Rows in source but not target → INSERT
-- Rows in both → UPDATE
-- Rows in target but not source → DELETE (this is the new clause)

MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

### MERGE with Audit Columns
```sql
MERGE INTO customers t
USING updates s ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET
  t.email       = s.email,
  t.updated_at  = current_timestamp(),
  t.updated_by  = current_user()
WHEN NOT MATCHED THEN INSERT (
  customer_id, email, created_at, updated_at
) VALUES (
  s.customer_id, s.email, current_timestamp(), current_timestamp()
);
```

### Conditional MERGE (only update if changed)
```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED AND (t.value != s.value OR t.status != s.status)
  THEN UPDATE SET *
WHEN NOT MATCHED
  THEN INSERT *;
```

## Table Constraints
```sql
-- NOT NULL constraint
ALTER TABLE employees ALTER COLUMN id SET NOT NULL;

-- CHECK constraint (validate data on insert/update)
ALTER TABLE employees ADD CONSTRAINT salary_positive CHECK (salary > 0);
ALTER TABLE employees ADD CONSTRAINT valid_dept CHECK (dept IN ('HR', 'IT', 'Finance', 'Engineering'));

-- View constraints
DESCRIBE DETAIL employees;

-- Drop constraint
ALTER TABLE employees DROP CONSTRAINT salary_positive;
```

## Delta Table Optimization Settings Reference
| Property | Effect | Default |
|----------|--------|---------|
| `delta.autoOptimize.optimizeWrite` | Compact files on write | false |
| `delta.autoOptimize.autoCompact` | Auto-compact after write | false |
| `delta.enableDeletionVectors` | Soft deletes | false |
| `delta.enableChangeDataFeed` | Track row-level changes | false |
| `delta.logRetentionDuration` | How long to keep transaction log | 30 days |
| `delta.deletedFileRetentionDuration` | Files kept before VACUUM removes them | 7 days |
| `delta.dataSkippingNumIndexedCols` | Columns with min/max statistics | 32 |

## Exam Tips
- Shallow clone shares files with source — VACUUM on source can break it
- Deep clone is fully independent — safe for backup/migration
- Liquid clustering replaces both partitioning and Z-Ordering
- Deletion vectors = soft deletes; physical removal happens at VACUUM
- `WHEN NOT MATCHED BY SOURCE THEN DELETE` = full sync pattern
- Table constraints are enforced at write time — violations cause errors

## Notes
_(Write your own notes here as you study)_
