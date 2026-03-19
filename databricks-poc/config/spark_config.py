"""
Spark Session Factory
Creates a configured SparkSession with Delta Lake support.
Used by all pipeline notebooks.
"""

import os
import sys
from pyspark.sql import SparkSession

# Ensure Spark workers use the same Python as the current process (venv Python)
# Fixes "Python was not found" errors caused by Windows App Execution Aliases
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Fix Windows console encoding to support Unicode characters (e.g. box-drawing ─)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_spark_session(app_name="DataSharingPOC", extra_packages=None):
    """
    Create and return a SparkSession configured for Delta Lake.

    Tuned for: Windows 11, 24 GB RAM, SSD storage
    Allocates 12 GB to Spark (leaving 12 GB for OS + other apps)

    extra_packages: additional Maven coords to append to spark.jars.packages
                    e.g. "org.xerial:sqlite-jdbc:3.44.1.0"
    """
    base_packages = "io.delta:delta-spark_2.12:3.1.0"
    all_packages = f"{base_packages},{extra_packages}" if extra_packages else base_packages

    spark = (SparkSession.builder
        .appName(app_name)

        # Delta Lake configuration
        .config("spark.jars.packages", all_packages)
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")

        # Memory configuration (tuned for 24 GB RAM)
        .config("spark.driver.memory", "12g")
        .config("spark.sql.shuffle.partitions", "8")

        # Performance tuning
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.parquet.compression.codec", "snappy")

        # Delta Lake optimisations
        .config("spark.databricks.delta.optimizeWrite.enabled", "true")
        .config("spark.databricks.delta.autoCompact.enabled", "true")

        # Windows-specific: avoid permission issues
        .config("spark.sql.warehouse.dir", "C:/Projects/databricks-poc/lake/spark-warehouse")

        # Local mode using all CPU cores
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark
