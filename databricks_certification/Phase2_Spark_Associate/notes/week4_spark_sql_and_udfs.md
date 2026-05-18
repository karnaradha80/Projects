# Week 4 — Spark SQL & UDFs

## Study Checklist
- [ ] Run SQL queries using spark.sql()
- [ ] Create and use temp views
- [ ] Write a Python UDF and register it
- [ ] Understand why UDFs are slower than built-in functions
- [ ] Know when to use Pandas UDFs (vectorized)

## Spark SQL
```python
# Run SQL directly
result = spark.sql("SELECT dept, AVG(salary) FROM employees GROUP BY dept")

# Register DataFrame as temp view
df.createOrReplaceTempView("employees")
result = spark.sql("SELECT * FROM employees WHERE salary > 80000")

# Global temp view (accessible across sessions)
df.createOrReplaceGlobalTempView("global_employees")
spark.sql("SELECT * FROM global_temp.global_employees")
```

## Mixing DataFrame API + SQL
```python
# Use temp view in SQL, then continue with DataFrame API
df.createOrReplaceTempView("sales")
result = spark.sql("""
  SELECT region, SUM(amount) as total
  FROM sales
  WHERE year = 2024
  GROUP BY region
""")
result.filter(col("total") > 1000000).show()
```

## UDFs — User Defined Functions
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType

# Define Python function
def categorize_salary(salary):
    if salary > 100000:
        return "High"
    elif salary > 60000:
        return "Medium"
    else:
        return "Low"

# Register as UDF
categorize_udf = udf(categorize_salary, StringType())

# Use in DataFrame
df.withColumn("category", categorize_udf(col("salary")))

# Decorator style
@udf(returnType=StringType())
def clean_name(name):
    return name.strip().title() if name else None

df.withColumn("name", clean_name(col("raw_name")))
```

## UDF Performance Warning
- UDFs break Spark's Catalyst optimizer — cannot optimize inside UDF
- Data serialized Python ↔ JVM for every row — slow
- **Always prefer built-in functions** (`when`, `regexp_replace`, etc.)
- Use UDF only when no built-in function does the job

## Pandas UDFs (Vectorized UDFs — much faster)
```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

# Pandas UDF processes a whole column at once (vectorized)
@pandas_udf(StringType())
def upper_pandas(series: pd.Series) -> pd.Series:
    return series.str.upper()

df.withColumn("name_upper", upper_pandas(col("name")))
```

## Notes
_(Write your own notes here as you study)_
