"""
Test script to verify all installations are working.
Run: python test_setup.py
"""

print("=" * 60)
print("  INSTALLATION VERIFICATION")
print("=" * 60)

# 1. Test Java
import subprocess
result = subprocess.run(["java", "-version"], capture_output=True, text=True)
java_version = result.stderr.split("\n")[0]
print(f"\n[1] Java: {java_version}")

# 2. Test PySpark
from pyspark.sql import SparkSession
spark = (SparkSession.builder
    .appName("SetupTest")
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .master("local[*]")
    .getOrCreate())

print(f"[2] PySpark: {spark.version}")
print(f"    Spark master: {spark.sparkContext.master}")
print(f"    Cores available: {spark.sparkContext.defaultParallelism}")

# 3. Test Delta Lake
df = spark.range(100).toDF("id")
df.write.format("delta").mode("overwrite").save("test_delta_table")
delta_df = spark.read.format("delta").load("test_delta_table")
print(f"[3] Delta Lake: Working (wrote & read {delta_df.count()} rows)")

# 4. Test Delta operations
from delta import DeltaTable
dt = DeltaTable.forPath(spark, "test_delta_table")
print(f"    Delta version: {dt.history().count() - 1}")

# 5. Cleanup
import shutil
shutil.rmtree("test_delta_table")
print("[4] Cleanup: test_delta_table removed")

# 6. Memory check
import psutil
ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
ram_available = round(psutil.virtual_memory().available / (1024**3), 1)
print(f"\n[5] System: {ram_gb} GB RAM ({ram_available} GB available)")

spark.stop()

print("\n" + "=" * 60)
print("  ALL CHECKS PASSED - Ready to build pipelines!")
print("=" * 60)
spark.stop()