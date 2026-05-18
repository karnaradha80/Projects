# Week 3 — Auto Loader

## Study Checklist
- [ ] Understand what problem Auto Loader solves
- [ ] Know the difference between directory listing and file notification modes
- [ ] Write an Auto Loader pipeline from scratch
- [ ] Understand schema inference, schema hints, and schema evolution
- [ ] Set up a checkpoint and understand why it is required

## What Problem Auto Loader Solves

### Without Auto Loader
```python
# Must manually track which files were already processed
# Risk: reprocessing same files, missing new files
files = dbutils.fs.ls("/raw/data/")
new_files = [f for f in files if f.name not in already_processed]
```

### With Auto Loader
- Automatically detects and ingests only NEW files
- Tracks processed files via checkpoint
- Handles schema inference and evolution
- Scales to millions of files without listing the entire directory

## Two Ingestion Modes

### 1. Directory Listing Mode (default)
- Scans the directory for new files on each trigger
- Simple to set up — no cloud configuration needed
- **Limitation:** Slow with millions of files (has to list everything)
- Good for: low-to-medium volume, simple setup

### 2. File Notification Mode (recommended for scale)
- Uses cloud event services to get notified of new files
  - AWS: SQS + SNS
  - Azure: Event Grid + Queue Storage
  - GCP: Pub/Sub
- Never scans directory — gets push notifications
- Scales to millions of files per day efficiently
- Good for: high-volume production workloads

```python
# Switch to file notification mode
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.useNotifications", "true") \
  ...
```

## Basic Auto Loader Pipeline
```python
# Full Auto Loader pattern (Bronze ingestion)
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")           # source file format: json, csv, parquet, avro
  .option("cloudFiles.schemaLocation", "/checkpoint/schema/employees/")  # schema stored here
  .option("header", "true")                       # for CSV files
  .load("/raw/landing/employees/")               # source path
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoint/data/employees/")  # REQUIRED
  .option("mergeSchema", "true")                 # allow schema evolution
  .trigger(availableNow=True)                    # process all available, then stop
  .table("bronze_employees")                     # write to Delta table
  .start()
)
```

## Schema Handling

### Schema Inference (automatic)
```python
# Auto Loader infers schema from first batch of files
# Saves inferred schema to schemaLocation
.option("cloudFiles.schemaLocation", "/checkpoint/schema/my_table/")
```

### Schema Hints (partially guide inference)
```python
# Tell Auto Loader the type of specific columns
# Useful when inference gets types wrong
.option("cloudFiles.schemaHints", "id INT, amount DECIMAL(10,2), event_date DATE")
```

### Schema Evolution
```python
# When new columns appear in source files:
# Option 1: mergeSchema — add new columns to Delta table automatically
.option("mergeSchema", "true")

# Option 2: rescuedDataColumn — put unknown columns into a JSON column
.option("cloudFiles.rescuedDataColumn", "_rescued_data")
```

## Supported File Formats
| Format | Option Value |
|--------|-------------|
| JSON (one record per line) | `json` |
| CSV | `csv` |
| Parquet | `parquet` |
| Avro | `avro` |
| ORC | `orc` |
| Text | `text` |
| Binary | `binaryFile` |

## Checkpoint — Why It Is Required
- Checkpoint stores: which files have been processed, streaming offsets
- Without checkpoint: reprocesses all files on every run (duplicates)
- Checkpoint must be: unique per streaming query, persistent storage (DBFS or cloud)
- Never share checkpoint between two different streaming queries

```
/checkpoint/data/employees/
├── commits/           ← which batches completed
├── offsets/           ← file tracking
├── sources/           ← source file registry
└── metadata           ← query metadata
```

## Metadata Columns Added by Auto Loader
```python
# These columns are automatically available
df.select(
  "_metadata.file_path",          # full path of source file
  "_metadata.file_name",          # file name only
  "_metadata.file_size",          # file size in bytes
  "_metadata.file_modification_time",  # when file was last modified
  "*"                             # all data columns
)
```

## Common Patterns

### Ingest CSV with header
```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "csv") \
  .option("header", "true") \
  .option("cloudFiles.schemaLocation", "/checkpoint/schema/orders/") \
  .load("/raw/orders/") \
  .writeStream \
  .option("checkpointLocation", "/checkpoint/data/orders/") \
  .table("bronze_orders") \
  .start()
```

### Ingest with file metadata tracking
```python
from pyspark.sql.functions import current_timestamp

spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", "/checkpoint/schema/events/") \
  .load("/raw/events/") \
  .withColumn("ingestion_time", current_timestamp()) \
  .withColumn("source_file", col("_metadata.file_path")) \
  .writeStream \
  .option("checkpointLocation", "/checkpoint/data/events/") \
  .table("bronze_events") \
  .start()
```

## Exam Tips
- File notification mode = scalable, needs cloud queue setup
- Directory listing = simple, not scalable for millions of files
- `schemaLocation` ≠ `checkpointLocation` — they are different paths
- `rescuedDataColumn` captures unexpected columns safely
- Checkpoint is REQUIRED for Auto Loader — without it, data is reprocessed
- Auto Loader only processes NEW files — already-seen files are skipped
- `_metadata` columns are available without any extra configuration

## Notes
_(Write your own notes here as you study)_
