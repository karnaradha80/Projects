# Week 5 — Performance Optimization

## Study Checklist
- [ ] Understand when to cache vs persist
- [ ] Know repartition vs coalesce difference
- [ ] Understand AQE and what it optimizes
- [ ] Know when Spark uses broadcast join automatically
- [ ] Read an explain plan

## Caching
```python
# Cache in memory (default storage level)
df.cache()
df.persist()  # same as cache() with default level

# Specific storage levels
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)  # spills to disk if memory full
df.persist(StorageLevel.DISK_ONLY)

# Always unpersist when done
df.unpersist()

# Cache a table
spark.sql("CACHE TABLE my_table")
spark.sql("UNCACHE TABLE my_table")
```

## Repartition vs Coalesce
| | Repartition | Coalesce |
|-|-------------|---------|
| Shuffle | Yes (full shuffle) | No (combines adjacent partitions) |
| Can increase partitions | Yes | No |
| Can decrease partitions | Yes | Yes |
| Use when | Need even distribution | Reducing partitions before write |

```python
df.repartition(100)                    # repartition to 100 partitions
df.repartition(100, col("dept"))       # partition by column (like hash)
df.coalesce(10)                        # reduce to 10 partitions, no shuffle
```

## Shuffle Partitions
```python
# Default is 200 — often too high for small data, too low for large data
spark.conf.set("spark.sql.shuffle.partitions", "100")

# Rule of thumb: target 128MB per partition
# If data after shuffle = 10GB → 10000/128 ≈ 80 partitions
```

## Adaptive Query Execution (AQE)
- Enabled by default in Databricks Runtime 7.3+
- Automatically:
  - Coalesces small shuffle partitions
  - Converts sort-merge joins to broadcast joins when one side is small
  - Handles skewed joins by splitting large partitions

```python
# Check if AQE is enabled
spark.conf.get("spark.sql.adaptive.enabled")  # should be "true"
```

## Broadcast Joins
```python
from pyspark.sql.functions import broadcast

# Force broadcast of small table
df_large.join(broadcast(df_small), "key")

# Spark auto-broadcasts tables under this threshold
spark.conf.get("spark.sql.autoBroadcastJoinThreshold")  # default 10MB
```

## Explain Plans
```python
# Simple explain
df.explain()

# Verbose explain (shows all plan stages)
df.explain(True)
df.explain("extended")  # logical + physical plan

# Key terms in explain output:
# FileScan — reading data
# Filter — filtering rows (pushed down = good)
# HashAggregate — groupBy
# Exchange — shuffle (expensive)
# BroadcastHashJoin — broadcast join used
# SortMergeJoin — full shuffle join
```

## Exam Tips
- Cache only when you use a DataFrame multiple times — otherwise overhead
- Coalesce before writing to avoid many small output files
- Broadcast join threshold: 10MB default, configurable
- AQE handles skew automatically — know what skew is
- Wide transformations cause shuffles; narrow do not

## Notes
_(Write your own notes here as you study)_
