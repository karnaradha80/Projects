# Week 1 — Delta Lake Foundations

## Study Checklist
- [ ] Understand why Delta Lake was created (problems with plain Parquet/CSV)
- [ ] Explore the `_delta_log/` folder in a Delta table
- [ ] Run basic DML: INSERT, UPDATE, DELETE on a Delta table
- [ ] Use DESCRIBE HISTORY and DESCRIBE DETAIL
- [ ] Query using time travel (VERSION AS OF, TIMESTAMP AS OF)

## Why Delta Lake?

### Problems with Plain Data Lakes (before Delta)
| Problem | Without Delta | With Delta |
|---------|--------------|-----------|
| Partial writes | Corrupt data if job fails | ACID — all or nothing |
| No updates/deletes | Must rewrite entire partition | Supports UPDATE, DELETE, MERGE |
| No history | Cannot go back to previous state | Time travel via transaction log |
| Schema drift | Any schema writes without validation | Schema enforcement + evolution |
| Slow reads (many small files) | No built-in optimization | OPTIMIZE, Z-Order, Auto Compact |

### Transaction Log (`_delta_log/`)
- JSON files recording every change (version 0, 1, 2 ...)
- Each JSON entry records: what files were added, removed, schema, metadata
- Spark reads the log to reconstruct any version of the table
- Checkpointed every 10 versions into Parquet for faster reads

```
my_delta_table/
├── _delta_log/
│   ├── 00000000000000000000.json   ← version 0 (CREATE TABLE)
│   ├── 00000000000000000001.json   ← version 1 (INSERT)
│   ├── 00000000000000000002.json   ← version 2 (UPDATE)
│   ├── 00000000000000000010.checkpoint.parquet
│   └── _last_checkpoint
├── part-00000-abc.snappy.parquet   ← actual data files
└── part-00001-xyz.snappy.parquet
```

## Creating Delta Tables

### SQL
```sql
-- Managed table (Databricks manages storage location)
CREATE TABLE IF NOT EXISTS employees (
  id        INT,
  name      STRING,
  dept      STRING,
  salary    DOUBLE,
  hire_date DATE
) USING DELTA;

-- External table (you control storage location)
CREATE TABLE IF NOT EXISTS employees_ext
USING DELTA
LOCATION '/mnt/datalake/employees/';

-- From SELECT
CREATE TABLE top_earners USING DELTA AS
SELECT * FROM employees WHERE salary > 100000;
```

### Python
```python
# Write DataFrame as Delta table
df.write.format("delta").mode("overwrite").saveAsTable("employees")
df.write.format("delta").mode("overwrite").save("/mnt/datalake/employees/")

# Read Delta table
df = spark.read.format("delta").load("/mnt/datalake/employees/")
df = spark.read.table("employees")
```

## DML Operations
```sql
-- INSERT
INSERT INTO employees VALUES (1, 'Alice', 'HR', 75000, '2022-01-15');
INSERT INTO employees SELECT * FROM staging_employees;

-- UPDATE
UPDATE employees SET salary = salary * 1.1 WHERE dept = 'Engineering';

-- DELETE
DELETE FROM employees WHERE hire_date < '2020-01-01';
```

## Inspecting Tables
```sql
DESCRIBE TABLE employees;           -- columns, types, nullable
DESCRIBE EXTENDED employees;        -- + location, format, properties
DESCRIBE DETAIL employees;          -- file count, size, partitioning, format
DESCRIBE HISTORY employees;         -- all versions with timestamp and operation

SHOW TBLPROPERTIES employees;       -- table properties/settings
```

## Time Travel
```sql
-- Query previous version
SELECT * FROM employees VERSION AS OF 0;    -- original CREATE
SELECT * FROM employees VERSION AS OF 3;    -- after 3rd operation

-- Query by timestamp
SELECT * FROM employees TIMESTAMP AS OF '2024-06-01 10:00:00';

-- Compare versions
SELECT * FROM employees VERSION AS OF 5
EXCEPT
SELECT * FROM employees VERSION AS OF 4;    -- rows added in version 5

-- Restore table to a previous version
RESTORE TABLE employees TO VERSION AS OF 2;
RESTORE TABLE employees TO TIMESTAMP AS OF '2024-06-01';
```

## Managed vs External Tables
| | Managed | External |
|-|---------|---------|
| Data location | Databricks default location | You specify path |
| DROP TABLE behavior | Deletes data + metadata | Deletes metadata only, data stays |
| Best for | Temporary tables, dev/test | Production data on your data lake |

## Exam Tips
- Transaction log is the source of truth for Delta — always check it for history
- Time travel uses the transaction log, not backups
- RESTORE creates a new version — it does NOT delete history
- DROP TABLE on a managed table deletes the actual data files
- DROP TABLE on an external table only removes Databricks metadata
- Version numbers start at 0

## Notes
_(Write your own notes here as you study)_
