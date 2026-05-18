"""
Truncates and reloads all dimension + fact tables from sample_data CSVs.
Order: dims first, then fct (respects FK constraints).
"""

import csv
import os
import pyodbc

CONN_STR = (
    "DRIVER={SQL Server};"
    "SERVER=sql-toad-poc.database.windows.net;"
    "DATABASE=db-toad-poc;"
    "UID=sqladmin;PWD=ToadPoc@2026!;"
    "Encrypt=yes;TrustServerCertificate=no;"
)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")

conn   = pyodbc.connect(CONN_STR, autocommit=False)
cursor = conn.cursor()


def load_table(schema, table, csv_file):
    path = os.path.join(DATA_DIR, csv_file)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cols   = list(rows[0].keys())
    col_list = ", ".join(f"[{c}]" for c in cols)
    placeholders = ", ".join("?" for _ in cols)

    cursor.execute(f"DELETE FROM [{schema}].[{table}]")
    for row in rows:
        values = [row[c] if row[c] != "" else None for c in cols]
        cursor.execute(
            f"INSERT INTO [{schema}].[{table}] ({col_list}) VALUES ({placeholders})",
            values
        )

    conn.commit()
    print(f"  {schema}.{table}: {len(rows)} rows loaded")


print("Loading dimension tables...")
load_table("abcbimart", "dim_organisation",  "dim_organisation.csv")
load_table("abcbimart", "dim_addresses",     "dim_addresses.csv")
load_table("abcbimart", "dim_calendar",      "dim_calendar.csv")
load_table("abcbimart", "dim_time",          "dim_time.csv")
load_table("abcbimart", "dim_work_orders",   "dim_work_orders.csv")

print("\nLoading fact table...")
load_table("abcbimart", "fct_gas_escapes_v", "fct_gas_escapes_v.csv")

print("\nDone.")
conn.close()
