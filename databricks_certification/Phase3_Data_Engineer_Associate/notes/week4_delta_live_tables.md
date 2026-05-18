# Week 4 — Delta Live Tables (DLT)

## Study Checklist
- [ ] Understand what DLT solves vs standard notebooks
- [ ] Write a DLT pipeline with Bronze, Silver, Gold tables
- [ ] Use all three expectation types: expect, expect_or_drop, expect_or_fail
- [ ] Understand LIVE vs STREAMING LIVE tables
- [ ] Know Development vs Production pipeline modes

## What Is Delta Live Tables?

### Problems DLT Solves
| Problem | Without DLT | With DLT |
|---------|------------|---------|
| Dependency management | Manual ordering of notebooks | DLT auto-resolves dependencies |
| Error handling | Manual retry logic | Built-in retry and recovery |
| Data quality | Manual validation code | Declarative expectations |
| Monitoring | Separate monitoring setup | Built-in event log and UI |
| Incremental processing | Complex streaming code | Simple `@dlt.table` decorators |

## Core Concepts

### LIVE Table vs STREAMING LIVE Table
| Type | Description | Use When |
|------|------------|---------|
| `@dlt.table` (batch) | Full recompute each run | Small datasets, aggregations, gold layer |
| `@dlt.table` with `dlt.read_stream()` | Incremental, streaming | Large datasets, bronze/silver layers |

### Reading from DLT Tables
```python
dlt.read("table_name")         # batch read (for non-streaming tables)
dlt.read_stream("table_name")  # streaming read (incremental processing)
```

## Full DLT Pipeline Example

```python
import dlt
from pyspark.sql.functions import col, current_timestamp, regexp_replace

# ── BRONZE ── Raw ingestion with Auto Loader
@dlt.table(
  name="bronze_orders",
  comment="Raw orders from landing zone",
  table_properties={"quality": "bronze"}
)
def bronze_orders():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/schema/orders")
        .load("/raw/landing/orders/")
        .withColumn("ingestion_time", current_timestamp())
    )


# ── SILVER ── Cleaned and validated
@dlt.table(
  name="silver_orders",
  comment="Validated and cleaned orders",
  table_properties={"quality": "silver"}
)
@dlt.expect("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
@dlt.expect_or_fail("valid_status", "status IN ('pending', 'shipped', 'delivered', 'cancelled')")
def silver_orders():
    return (
        dlt.read_stream("bronze_orders")
        .filter(col("order_id").isNotNull())
        .withColumn("amount", col("amount").cast("decimal(10,2)"))
        .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", ""))
        .dropDuplicates(["order_id"])
    )


# ── GOLD ── Business aggregation
@dlt.table(
  name="gold_orders_by_region",
  comment="Daily order totals by region",
  table_properties={"quality": "gold"}
)
def gold_orders_by_region():
    return (
        dlt.read("silver_orders")
        .groupBy("region", "order_date")
        .agg(
            count("order_id").alias("order_count"),
            sum("amount").alias("total_revenue")
        )
    )
```

## Expectations — Data Quality Rules

### Three Types
| Decorator | On Violation | Use When |
|-----------|-------------|---------|
| `@dlt.expect("name", "condition")` | Log warning, keep row | Non-critical quality issue |
| `@dlt.expect_or_drop("name", "condition")` | Drop violating row silently | Remove bad records from pipeline |
| `@dlt.expect_or_fail("name", "condition")` | Stop entire pipeline | Critical data — must be 100% clean |

### Multiple Expectations
```python
@dlt.expect_all({
    "valid_id": "id IS NOT NULL",
    "valid_amount": "amount > 0",
    "valid_date": "order_date IS NOT NULL"
})
def my_table():
    ...

@dlt.expect_all_or_drop({
    "no_null_id": "id IS NOT NULL",
    "positive_qty": "quantity > 0"
})
def clean_table():
    ...
```

## Pipeline Modes

### Development Mode
- Re-runs failed tasks immediately for faster debugging
- Does NOT retry on failure — shows error right away
- Does NOT keep failed runs for auditing
- Lower cost (no retry overhead)
- Use when: building and testing the pipeline

### Production Mode
- Automatic retries on failure (configurable)
- Keeps failed run information for audit
- Sends failure notifications
- Use when: running in scheduled production

## DLT Table Types
```python
# Standard DLT table (managed by DLT)
@dlt.table
def my_table(): ...

# External DLT table (you specify storage)
@dlt.table(
  path="/mnt/datalake/my_table/"
)
def my_table(): ...

# View (not materialized — just a query definition)
@dlt.view
def my_view():
    return dlt.read("my_table").filter(...)
```

## Parameterization with pipeline_parameters
```python
# Access pipeline parameters inside DLT
start_date = spark.conf.get("pipeline.startDate", "2024-01-01")
```

## DLT Event Log
```sql
-- Query DLT event log (automatically created)
SELECT * FROM event_log("my_pipeline_id")
WHERE event_type = 'flow_progress'
ORDER BY timestamp DESC;
```

## Exam Tips
- `expect` = warn only; `expect_or_drop` = silent drop; `expect_or_fail` = pipeline stops
- `dlt.read()` = batch (full); `dlt.read_stream()` = incremental (streaming)
- Development mode = fast feedback, no retry; Production = retries, notifications
- DLT automatically handles dependency order — you just reference table names
- DLT tables are always Delta tables
- You cannot use regular `spark.read()` inside DLT — must use `dlt.read()` or `dlt.read_stream()`

## Notes
_(Write your own notes here as you study)_
