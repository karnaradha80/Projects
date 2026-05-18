import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};SERVER=sql-toad-poc.database.windows.net;'
    'DATABASE=db-toad-poc;UID=sqladmin;PWD=ToadPoc@2026!;'
    'Encrypt=yes;TrustServerCertificate=no;',
    autocommit=True
)
cursor = conn.cursor()

# Add job_type column if not exists
cursor.execute("""
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='abcbimart' AND TABLE_NAME='dim_work_orders' AND COLUMN_NAME='job_type'
    )
    ALTER TABLE abcbimart.dim_work_orders ADD job_type VARCHAR(50) NOT NULL DEFAULT 'JOB_TYPE_A'
""")
print("Column added (or already exists).")

# Update each row with a job_type value
job_types = {
    1: 'JOB_TYPE_A', 2: 'JOB_TYPE_B', 3: 'JOB_TYPE_A', 4: 'JOB_TYPE_C', 5: 'JOB_TYPE_B',
    6: 'JOB_TYPE_A', 7: 'JOB_TYPE_C', 8: 'JOB_TYPE_B', 9: 'JOB_TYPE_A', 10: 'JOB_TYPE_A',
    11: 'JOB_TYPE_B', 12: 'JOB_TYPE_A', 13: 'JOB_TYPE_C', 14: 'JOB_TYPE_A', 15: 'JOB_TYPE_B',
    16: 'JOB_TYPE_A', 17: 'JOB_TYPE_C', 18: 'JOB_TYPE_B', 19: 'JOB_TYPE_A', 20: 'JOB_TYPE_A',
}
for id_, jt in job_types.items():
    cursor.execute("UPDATE abcbimart.dim_work_orders SET job_type=? WHERE id=?", jt, id_)
print("job_type values updated.")

cursor.execute("SELECT id, work_order_number, job_type FROM abcbimart.dim_work_orders ORDER BY id")
for row in cursor.fetchall():
    print(f"  {row[0]:>3}  {row[1]}  {row[2]}")

conn.close()
