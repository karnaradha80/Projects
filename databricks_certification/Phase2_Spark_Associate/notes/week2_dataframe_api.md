# Week 2 — DataFrame API

## Study Checklist
- [ ] Read CSV, JSON, Parquet into a DataFrame
- [ ] Use select, filter, withColumn, drop
- [ ] Use groupBy and agg
- [ ] Write DataFrame to Delta table
- [ ] Use display() and printSchema()

## Key Concepts

### SparkSession
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("MyApp").getOrCreate()
```

### Reading Data
```python
# CSV
df = spark.read.csv("/path/to/file.csv", header=True, inferSchema=True)
df = spark.read.format("csv").option("header", True).load("/path/")

# JSON
df = spark.read.json("/path/to/file.json")

# Parquet
df = spark.read.parquet("/path/to/file.parquet")

# Delta
df = spark.read.format("delta").load("/path/to/delta/")
df = spark.read.table("my_table")
```

### Inspecting DataFrames
```python
df.show(5)                  # display first 5 rows
df.display()                # Databricks-only, rich display
df.printSchema()            # column names and types
df.dtypes                   # list of (name, type) tuples
df.columns                  # list of column names
df.count()                  # row count (action)
df.describe().show()        # statistics
```

### Selecting & Filtering
```python
from pyspark.sql.functions import col

# Select columns
df.select("name", "age")
df.select(col("name"), col("salary") * 1.1)

# Filter (WHERE equivalent)
df.filter(col("age") > 30)
df.filter("age > 30")                           # SQL string also works
df.where(col("dept") == "IT")

# Multiple conditions
df.filter((col("age") > 30) & (col("dept") == "HR"))
df.filter((col("age") > 30) | (col("salary") > 80000))
```

### Adding & Modifying Columns
```python
from pyspark.sql.functions import col, lit, when

# Add new column
df.withColumn("bonus", col("salary") * 0.1)

# Conditional column (like SQL CASE WHEN)
df.withColumn("grade",
  when(col("salary") > 100000, "A")
  .when(col("salary") > 70000, "B")
  .otherwise("C")
)

# Rename column
df.withColumnRenamed("old_name", "new_name")

# Drop column
df.drop("unwanted_col")

# Cast type
df.withColumn("age", col("age").cast("integer"))
```

### Aggregations
```python
from pyspark.sql.functions import count, sum, avg, min, max, countDistinct

# GroupBy + aggregate
df.groupBy("dept").agg(
  count("*").alias("headcount"),
  avg("salary").alias("avg_salary"),
  sum("salary").alias("total_salary"),
  max("salary").alias("max_salary")
).show()

# Simple aggregations
df.select(avg("salary"), max("salary")).show()
```

### Writing Data
```python
# Write to Delta (default format on Databricks)
df.write.format("delta").mode("overwrite").save("/path/to/output/")
df.write.mode("append").saveAsTable("my_table")

# Write modes
# overwrite — replace all existing data
# append    — add to existing data
# ignore    — do nothing if data exists
# error     — raise error if data exists (default)
```

## Notes
_(Write your own notes here as you study)_
