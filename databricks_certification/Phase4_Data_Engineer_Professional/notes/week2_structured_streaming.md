# Week 2 — Structured Streaming at Scale

## Study Checklist
- [ ] Know all 3 trigger types and when to use each
- [ ] Know all 3 output modes and valid scenarios for each
- [ ] Write a watermarking query for late-arriving data
- [ ] Write a stateful streaming aggregation
- [ ] Use foreachBatch to write to multiple sinks
- [ ] Implement streaming deduplication with watermark

## Triggers — When to Process Data

### Three Trigger Types
```python
# 1. Fixed interval — process every N seconds/minutes
.trigger(processingTime="30 seconds")
.trigger(processingTime="5 minutes")

# 2. Once — process ALL available data in ONE micro-batch, then stop
.trigger(once=True)
# Use case: scheduled batch-style execution

# 3. availableNow — process ALL available data in MULTIPLE micro-batches, then stop
.trigger(availableNow=True)
# Use case: large backfill — better than once=True for big datasets
# Advantages over once=True:
#   - Multiple micro-batches = less memory pressure
#   - Can recover mid-way if it fails
#   - More efficient for large data volumes
```

### Choosing the Right Trigger
| Scenario | Trigger |
|----------|---------|
| Real-time pipeline (continuous) | `processingTime="30 seconds"` |
| Scheduled job, small data | `once=True` |
| Scheduled job, large backfill | `availableNow=True` ← preferred |
| Near-real-time with rate control | `processingTime="1 minute"` |

## Output Modes — Where Results Go

### Three Output Modes
```python
.outputMode("append")    # Only NEW rows added since last trigger
.outputMode("complete")  # Entire result table rewritten every trigger
.outputMode("update")    # Only CHANGED rows output every trigger
```

### Rules — What Mode Works With What
| Output Mode | Stateless | Aggregation | Aggregation + Watermark |
|-------------|-----------|-------------|------------------------|
| `append` | ✅ | ❌ | ✅ |
| `complete` | ❌ | ✅ | ❌ (too large) |
| `update` | ✅ | ✅ | ✅ |

```python
# append — only for stateless or aggregation WITH watermark
df.writeStream.outputMode("append")

# complete — full result rewrite, typically for aggregations to memory/console
df.writeStream.outputMode("complete")

# update — most efficient, only changed rows
df.writeStream.outputMode("update")
```

## Watermarking — Handle Late Data

### The Problem
- Events arrive out of order in real-world streaming
- An event with timestamp 10:00 AM may arrive at 10:20 AM
- Without watermark: Spark holds all state forever → memory blows up

### Solution: Watermark
```python
from pyspark.sql.functions import window

# Watermark tells Spark: "I will accept data up to N minutes late"
# Data older than (max_event_time - delay) is dropped
(df
  .withWatermark("event_time", "10 minutes")     # accept up to 10 min late
  .groupBy(
    window(col("event_time"), "5 minutes"),       # 5-minute tumbling window
    col("region")
  )
  .agg(sum("amount").alias("total_amount"))
  .writeStream
  .outputMode("append")                           # append works with watermark
  .option("checkpointLocation", "/checkpoint/sales_agg/")
  .start()
)
```

### Window Types
```python
from pyspark.sql.functions import window

# Tumbling window (non-overlapping, fixed size)
window(col("event_time"), "5 minutes")

# Sliding window (overlapping)
window(col("event_time"), "10 minutes", "5 minutes")  # 10 min window, every 5 min

# Session window (closes after gap of inactivity)
session_window(col("event_time"), "10 minutes")
```

## Stateful Streaming

### Streaming Aggregation (stateful)
```python
# Spark maintains running state across micro-batches
(spark.readStream.table("bronze_events")
  .withWatermark("event_time", "30 minutes")
  .groupBy("user_id", window("event_time", "1 hour"))
  .agg(count("*").alias("event_count"), sum("value").alias("total_value"))
  .writeStream
  .outputMode("append")
  .option("checkpointLocation", "/checkpoint/user_hourly/")
  .table("silver_user_hourly")
  .start()
)
```

### Streaming Deduplication (stateful)
```python
# dropDuplicates in streaming maintains a seen-ids state
# Without watermark: state grows forever
# With watermark: state cleared after delay passes

(spark.readStream.table("bronze_events")
  .withWatermark("event_time", "1 hour")
  .dropDuplicates(["event_id", "event_time"])   # dedup within watermark window
  .writeStream
  .outputMode("append")
  .option("checkpointLocation", "/checkpoint/dedup_events/")
  .table("silver_events_deduped")
  .start()
)
```

## foreachBatch — Write to Multiple Sinks
```python
# Standard writeStream only writes to one sink
# foreachBatch allows writing to multiple destinations per micro-batch

def process_batch(batch_df, batch_id):
    batch_df.persist()   # cache so we don't recompute for each write

    # Write to Delta table
    batch_df.write.mode("append").saveAsTable("silver_events")

    # Write summary to another table
    batch_df.groupBy("region").agg(sum("amount")) \
            .write.mode("append").saveAsTable("gold_region_summary")

    # Write to external system (e.g., Kafka, JDBC)
    batch_df.write.format("jdbc").options(**jdbc_opts).mode("append").save()

    batch_df.unpersist()

(spark.readStream.table("bronze_events")
  .writeStream
  .foreachBatch(process_batch)
  .option("checkpointLocation", "/checkpoint/multi_sink/")
  .trigger(availableNow=True)
  .start()
)
```

## Monitoring Streaming Queries
```python
# Start query and monitor
query = df.writeStream.table("output_table").start()

# Check status
query.status
# {'message': 'Processing new data', 'isDataAvailable': True, 'isTriggerActive': True}

# Last batch stats
query.lastProgress
# Shows: inputRowsPerSecond, processedRowsPerSecond, batchDuration, numInputRows

# Recent batch history
query.recentProgress

# Stop query
query.stop()

# Wait for termination (blocking)
query.awaitTermination()
```

## Streaming + Delta Lake Pattern
```python
# Read from Delta as stream (changes only)
spark.readStream.table("silver_events")

# Or read from specific version onwards
spark.readStream \
  .option("startingVersion", 10) \
  .table("silver_events")

# Read only from specific timestamp
spark.readStream \
  .option("startingTimestamp", "2024-06-01") \
  .table("silver_events")

# Limit rate of processing (avoid overwhelming downstream)
spark.readStream \
  .option("maxFilesPerTrigger", 10) \     # max files per micro-batch
  .option("maxBytesPerTrigger", "10g") \  # max data per micro-batch
  .table("bronze_events")
```

## Exam Tips
- `availableNow` > `once` for large datasets (multiple micro-batches, recoverable)
- `complete` output mode rewrites full result — only practical for small aggregations
- Watermark defines state retention window — data beyond it is dropped
- Without watermark, stateful ops (groupBy, dropDuplicates) cause unbounded state
- `foreachBatch` enables writing to multiple destinations or custom logic
- Checkpoint = mandatory for fault tolerance; unique per query
- `append` output mode requires watermark when used with aggregation

## Notes
_(Write your own notes here as you study)_
