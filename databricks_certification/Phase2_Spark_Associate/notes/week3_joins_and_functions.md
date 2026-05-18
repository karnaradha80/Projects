# Week 3 — Joins & Built-in Functions

## Study Checklist
- [ ] Practice all join types (inner, left, right, outer, cross, semi, anti)
- [ ] Know when to use broadcast join
- [ ] Practice string functions
- [ ] Practice date functions
- [ ] Use explode and collect_list

## Joins
```python
from pyspark.sql.functions import broadcast

# Inner join (default)
df_result = df_orders.join(df_customers, "customer_id")
df_result = df_orders.join(df_customers, df_orders.customer_id == df_customers.id, "inner")

# Left join
df_orders.join(df_customers, "customer_id", "left")

# Right join
df_orders.join(df_customers, "customer_id", "right")

# Full outer join
df_orders.join(df_customers, "customer_id", "outer")

# Cross join (Cartesian product — be careful)
df1.crossJoin(df2)

# Semi join (like EXISTS in SQL — returns left rows that match right)
df_orders.join(df_customers, "customer_id", "left_semi")

# Anti join (like NOT EXISTS — returns left rows that DON'T match right)
df_orders.join(df_customers, "customer_id", "left_anti")

# Broadcast join (when one side is small — avoids shuffle)
df_large.join(broadcast(df_small), "key")
```

## String Functions
```python
from pyspark.sql.functions import (
  upper, lower, trim, ltrim, rtrim,
  length, substring, instr, locate,
  replace, regexp_replace, regexp_extract,
  concat, concat_ws, split, initcap
)

df.withColumn("name_upper", upper(col("name")))
df.withColumn("name_lower", lower(col("name")))
df.withColumn("name_trim", trim(col("name")))
df.withColumn("name_len", length(col("name")))
df.withColumn("first3", substring(col("name"), 1, 3))
df.withColumn("full_name", concat(col("first"), lit(" "), col("last")))
df.withColumn("full_name", concat_ws(" ", col("first"), col("last")))
df.withColumn("clean", regexp_replace(col("phone"), "[^0-9]", ""))
df.withColumn("parts", split(col("email"), "@"))
```

## Date Functions
```python
from pyspark.sql.functions import (
  current_date, current_timestamp,
  to_date, to_timestamp, date_format,
  year, month, dayofmonth, dayofweek,
  date_add, date_sub, datediff,
  months_between, trunc
)

df.withColumn("today", current_date())
df.withColumn("dt", to_date(col("date_str"), "yyyy-MM-dd"))
df.withColumn("yr", year(col("dt")))
df.withColumn("mo", month(col("dt")))
df.withColumn("day", dayofmonth(col("dt")))
df.withColumn("next_week", date_add(col("dt"), 7))
df.withColumn("days_diff", datediff(current_date(), col("dt")))
df.withColumn("formatted", date_format(col("dt"), "MM/dd/yyyy"))
```

## Array & Complex Type Functions
```python
from pyspark.sql.functions import (
  array, array_contains, array_distinct,
  explode, explode_outer,
  collect_list, collect_set,
  size, flatten, zip_with
)

# explode — one row per array element (null arrays → 0 rows)
df.withColumn("tag", explode(col("tags")))

# explode_outer — keeps nulls as a single null row
df.withColumn("tag", explode_outer(col("tags")))

# collect_list — aggregate rows into an array
df.groupBy("dept").agg(collect_list("name").alias("members"))

# collect_set — aggregate unique values
df.groupBy("dept").agg(collect_set("city").alias("cities"))

# array_contains
df.filter(array_contains(col("tags"), "python"))
```

## Notes
_(Write your own notes here as you study)_
