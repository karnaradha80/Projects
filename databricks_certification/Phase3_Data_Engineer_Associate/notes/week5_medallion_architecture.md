# Week 5 — Medallion Architecture & ELT Patterns

## Study Checklist
- [ ] Build a full Bronze → Silver → Gold pipeline end-to-end
- [ ] Understand the purpose and rules of each layer
- [ ] Know ELT vs ETL and why Databricks uses ELT
- [ ] Apply deduplication strategies in Silver layer
- [ ] Build a Gold layer aggregation table

## Medallion Architecture Overview

```
External Sources
    │
    ▼
┌─────────────────────────────────┐
│  BRONZE (Raw / Landing Zone)    │
│  - Exact copy of source data    │
│  - Append-only                  │
│  - Delta format                 │
│  - No transformations applied   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  SILVER (Cleaned / Conformed)   │
│  - Deduplicated                 │
│  - Nulls handled                │
│  - Types cast correctly         │
│  - Validated (expectations)     │
│  - Joined with reference data   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  GOLD (Business / Aggregated)   │
│  - Aggregated by business rules │
│  - Optimized for queries/BI     │
│  - Joined, enriched             │
│  - Used by dashboards, reports  │
└─────────────────────────────────┘
```

## Layer Rules

### Bronze — Raw Ingestion
```python
# Rules:
# 1. Never transform data — store exactly as received
# 2. Always append — never overwrite or delete
# 3. Add metadata: ingestion_time, source_file, batch_id
# 4. Use Auto Loader for file ingestion

@dlt.table(name="bronze_sales")
def bronze_sales():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", "/schema/sales")
        .option("header", "true")
        .load("/raw/landing/sales/")
        .withColumn("_ingestion_time", current_timestamp())
        .withColumn("_source_file", col("_metadata.file_path"))
    )
```

### Silver — Cleaned & Validated
```python
# Rules:
# 1. Deduplicate (remove duplicates from Bronze)
# 2. Cast to correct types
# 3. Filter out invalid/null records
# 4. Apply data quality expectations
# 5. Join with reference/lookup tables if needed

@dlt.table(name="silver_sales")
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("positive_quantity", "quantity > 0")
def silver_sales():
    return (
        dlt.read_stream("bronze_sales")
        .withColumn("amount",      col("amount").cast("decimal(12,2)"))
        .withColumn("sale_date",   to_date(col("sale_date_str"), "yyyy-MM-dd"))
        .withColumn("quantity",    col("quantity").cast("integer"))
        .withColumn("customer_id", col("customer_id").cast("integer"))
        .dropDuplicates(["order_id"])
        .drop("sale_date_str", "_source_file")
    )
```

### Gold — Business Aggregations
```python
# Rules:
# 1. Aggregate by business dimensions (date, region, product)
# 2. Use batch processing (full recompute or incremental)
# 3. Optimize for query performance (Z-Order, partitioning)
# 4. Source for BI dashboards and reports

@dlt.table(
    name="gold_daily_sales",
    table_properties={"delta.autoOptimize.optimizeWrite": "true"}
)
def gold_daily_sales():
    return (
        dlt.read("silver_sales")
        .groupBy("sale_date", "region", "product_category")
        .agg(
            sum("amount").alias("total_revenue"),
            count("order_id").alias("order_count"),
            avg("amount").alias("avg_order_value"),
            countDistinct("customer_id").alias("unique_customers")
        )
    )
```

## ELT vs ETL

| | ETL (Extract-Transform-Load) | ELT (Extract-Load-Transform) |
|-|------------------------------|------------------------------|
| Transform step | Before loading to destination | After loading to destination |
| Traditional tool | SSIS, Informatica, Talend | Databricks, dbt, Spark |
| Storage | Transform happens on ETL server | Raw data stored first, then transformed |
| Flexibility | Schema-on-write (fixed schema) | Schema-on-read (flexible) |
| Databricks approach | ❌ | ✅ |

### Why ELT on Databricks
- Load raw data cheaply to cloud storage (Bronze)
- Transform using distributed Spark compute (Silver/Gold)
- Scale compute independently from storage
- Keep raw data forever — re-process if logic changes

## Deduplication Patterns

### In Streaming (Silver layer)
```python
# dropDuplicates in streaming — needs watermark for stateful dedup
df.withWatermark("event_time", "1 hour") \
  .dropDuplicates(["order_id", "event_time"])

# Simple dedup (within each micro-batch only)
df.dropDuplicates(["order_id"])
```

### In Batch (using MERGE)
```python
# Upsert pattern — handles duplicates from source
DeltaTable.forName(spark, "silver_sales").alias("t") \
  .merge(
    source.alias("s"),
    "t.order_id = s.order_id"
  ) \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .execute()
```

## Full Pipeline Flow

```
/raw/landing/sales/*.csv          (new files arrive daily)
         │
         │  Auto Loader (cloudFiles)
         ▼
bronze_sales                       (Delta, append-only, raw)
         │
         │  DLT streaming table
         ▼
silver_sales                       (Delta, deduplicated, typed, validated)
         │
         │  DLT batch table (full recompute)
         ▼
gold_daily_sales                   (Delta, aggregated, BI-ready)
         │
         │  Databricks SQL / Dashboard
         ▼
Business Reports & Dashboards
```

## Exam Tips
- Bronze = append-only; Silver = deduplicated; Gold = aggregated
- Never transform Bronze — it is always a raw copy of source
- ELT = load first, then transform; ETL = transform before loading
- Gold layer uses batch DLT tables (not streaming) for aggregations
- Silver deduplication strategy depends on use case — MERGE or dropDuplicates
- Medallion is a design pattern, not a Databricks product feature

## Notes
_(Write your own notes here as you study)_
