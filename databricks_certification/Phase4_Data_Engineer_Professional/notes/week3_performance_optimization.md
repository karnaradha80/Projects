# Week 3 — Performance Optimization

## Study Checklist
- [ ] Know target file size for Delta tables
- [ ] Understand when to use partitioning vs Z-Ordering vs Liquid Clustering
- [ ] Know what Photon engine accelerates
- [ ] Understand Bloom filter indexes and when they help
- [ ] Know how AQE handles skew

## File Size Optimization

### Target File Size
- **Ideal file size: 128MB – 1GB per Parquet/Delta file**
- Too small → many files → slow metadata reads (small file problem)
- Too large → poor parallelism, slow reads on partial queries

```sql
-- See current file stats
DESCRIBE DETAIL my_table;
-- Look at: numFiles, sizeInBytes

-- Compact files to target size
OPTIMIZE my_table;

-- Set target file size (advanced)
ALTER TABLE my_table SET TBLPROPERTIES (
  'delta.targetFileSize' = '134217728'  -- 128MB in bytes
);
```

### Auto Optimize Settings
```sql
ALTER TABLE my_table SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',  -- compact on every write
  'delta.autoOptimize.autoCompact'   = 'true'   -- background compact after write
);
```

## Data Layout Strategies Compared

| Strategy | Best For | Mechanism | Change After Creation? |
|----------|----------|-----------|----------------------|
| Partitioning | Low-cardinality (date, country, year) | Physical folders | No — requires full rewrite |
| Z-Ordering | Medium-cardinality (customer_id, product_id) | Sort within files | Yes — re-run OPTIMIZE |
| Liquid Clustering | Any cardinality | Automatic clustering | Yes — ALTER TABLE |

### When to Use Each
```sql
-- Partitioning: date-based data, large tables, query filters always include partition column
CREATE TABLE events (...) USING DELTA PARTITIONED BY (event_date);

-- Z-Ordering: frequently filtered column, not great for partitioning
OPTIMIZE events ZORDER BY (customer_id, region);

-- Liquid Clustering: newest approach, most flexible
CREATE TABLE events (...) CLUSTER BY (event_date, customer_id);
```

### Combining Strategies
```sql
-- Partitioning + Z-Ordering (common pattern)
CREATE TABLE events (...) USING DELTA PARTITIONED BY (event_date);
OPTIMIZE events WHERE event_date = '2024-06-01' ZORDER BY (customer_id);
-- Partition prunes to the right date folder, Z-Order helps within that partition
```

## Bloom Filter Indexes

### What They Are
- Probabilistic data structure that answers: "Is this value definitely NOT in this file?"
- If Bloom filter says "no" → skip the file entirely (no I/O)
- Small false-positive rate (may read a file that has no match — acceptable)
- Best for: high-cardinality columns with equality filters (`WHERE id = 12345`)

```sql
-- Create Bloom filter index
CREATE BLOOMFILTER INDEX ON TABLE events FOR COLUMNS (user_id OPTIONS (fpp=0.1, numItems=50000000));
-- fpp = false positive probability (0.1 = 10% false positive rate, lower = larger index)

-- Drop index
DROP BLOOMFILTER INDEX ON TABLE events FOR COLUMNS (user_id);
```

**Use Bloom filters when:**
- Column has very high cardinality (user_id, session_id, UUID)
- Queries use equality filters on that column (`WHERE user_id = ?`)
- Z-Ordering doesn't help much (too many distinct values)

## Adaptive Query Execution (AQE)

### What AQE Does Automatically
```python
# Check AQE is enabled
spark.conf.get("spark.sql.adaptive.enabled")  # should be "true" on Databricks

# Three automatic optimizations:
# 1. Coalesces shuffle partitions (fewer, larger partitions after shuffle)
# 2. Converts sort-merge join → broadcast join when one side becomes small
# 3. Handles skewed partitions (splits large partitions)
```

### Handling Data Skew
```python
# Without AQE: one executor processes 10x more data than others → bottleneck
# With AQE: splits skewed partitions automatically

# Enable skew join optimization
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Manual skew handling (when AQE not enough)
from pyspark.sql.functions import spark_partition_id
df.groupBy(spark_partition_id()).count().show()   # diagnose skew

# Add salt to skewed key to distribute
from pyspark.sql.functions import concat, lit, (rand() * 10).cast("int")
df_skewed.withColumn("salted_key", concat(col("customer_id"), lit("_"), (rand() * 10).cast("int")))
```

## Caching Strategy

### When to Cache
```python
# Cache when: DataFrame used multiple times in same job
df_filtered = spark.table("silver_sales").filter("year = 2024")
df_filtered.cache()

summary = df_filtered.groupBy("region").agg(sum("amount"))
detail  = df_filtered.filter("amount > 10000")

df_filtered.unpersist()   # always unpersist when done
```

### Storage Levels
```python
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_ONLY)           # default cache() — RAM only
df.persist(StorageLevel.MEMORY_AND_DISK)       # spill to disk if RAM full
df.persist(StorageLevel.DISK_ONLY)             # disk only
df.persist(StorageLevel.MEMORY_ONLY_SER)       # serialized (less RAM, more CPU)
df.persist(StorageLevel.OFF_HEAP)              # off-heap memory
```

### Delta Cache (Databricks-specific)
- Caches data from cloud storage to local SSD on executor nodes
- Automatic — no code changes needed
- Faster than Spark cache for repeated reads of same files
- Only on certain instance types (Delta cache enabled nodes)

## Photon Engine

### What Photon Accelerates
- Vectorized query execution engine (C++ based, not JVM)
- Accelerates: SQL queries, DataFrame operations, Delta table reads
- Best gains on: aggregations, joins, string operations, sorting
- NOT faster for: Python UDFs (still runs in JVM/Python), ML operations

```python
# Photon is cluster-level setting — enable when creating cluster
# Runtime: Databricks Runtime with Photon (e.g., "13.3 LTS Photon")
# No code changes needed — transparent acceleration
```

## Join Optimization

### Broadcast Join Threshold
```python
# Spark auto-broadcasts tables smaller than this threshold
spark.conf.get("spark.sql.autoBroadcastJoinThreshold")  # default: 10MB

# Increase threshold to broadcast larger tables
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50MB")

# Force broadcast
from pyspark.sql.functions import broadcast
df_large.join(broadcast(df_small), "key")

# Disable broadcast (when it causes memory issues)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

### Join Types and Cost
| Join Type | When Used | Cost |
|-----------|----------|------|
| Broadcast Hash Join | Small table fits in memory | Cheapest — no shuffle |
| Sort Merge Join | Both tables large | Expensive — full shuffle |
| Shuffle Hash Join | One side smaller but not broadcastable | Moderate |

## Exam Tips
- Target file size: 128MB–1GB; below = small file problem; above = parallelism issue
- Partitioning = folders; Z-Order = within files; Liquid = automatic, flexible
- Bloom filter = equality filters on high-cardinality columns only
- AQE handles skew automatically; manual salting for extreme skew
- Photon accelerates SQL/DataFrame — UDFs still slow
- Cache only when DataFrame used multiple times — otherwise overhead
- `coalesce` before write to reduce output file count (no shuffle)

## Notes
_(Write your own notes here as you study)_
