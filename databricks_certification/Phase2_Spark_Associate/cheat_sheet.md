# Spark Associate — Cheat Sheet

## Read / Write
```python
spark.read.csv("/path", header=True, inferSchema=True)
spark.read.json("/path")
spark.read.parquet("/path")
spark.read.format("delta").load("/path")
spark.read.table("my_table")

df.write.mode("overwrite").format("delta").save("/path")
df.write.mode("append").saveAsTable("my_table")
```

## DataFrame Operations
```python
df.select("col1", "col2")
df.filter(col("age") > 30)
df.withColumn("new", col("salary") * 1.1)
df.withColumnRenamed("old", "new")
df.drop("col")
df.groupBy("dept").agg(avg("salary"), count("*"))
df.orderBy(col("salary").desc())
df.limit(100)
df.distinct()
df.dropDuplicates(["id"])
```

## Joins
```python
df1.join(df2, "key")                          # inner
df1.join(df2, "key", "left")
df1.join(df2, "key", "outer")
df1.join(df2, "key", "left_semi")             # EXISTS
df1.join(df2, "key", "left_anti")             # NOT EXISTS
df1.join(broadcast(df2), "key")               # broadcast
```

## Key Functions
```python
col("name"), lit(42)
when(cond, val).when(cond2, val2).otherwise(default)
coalesce(col("a"), col("b"), lit("default"))
upper, lower, trim, length, substring, split, regexp_replace
year, month, dayofmonth, date_add, datediff, date_format
explode, collect_list, collect_set, array_contains, size
```

## Performance
```python
df.cache() / df.unpersist()
df.repartition(n) / df.coalesce(n)
spark.conf.set("spark.sql.shuffle.partitions", "100")
df.explain(True)
broadcast(small_df)
```

## Transformations vs Actions
| Transformations (lazy) | Actions (eager) |
|-----------------------|----------------|
| filter, select, join | show, count |
| groupBy, withColumn | collect, take |
| map, flatMap, union | write, save |

## Narrow vs Wide
| Narrow (no shuffle) | Wide (shuffle) |
|--------------------|---------------|
| filter, select, map | groupBy, join |
| union, withColumn | distinct, repartition |
