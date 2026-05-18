import pyodbc
conn = pyodbc.connect(
    'DRIVER={SQL Server};SERVER=sql-toad-poc.database.windows.net;'
    'DATABASE=db-toad-poc;UID=sqladmin;PWD=ToadPoc@2026!;'
    'Encrypt=yes;TrustServerCertificate=no;',
    autocommit=True
)
cursor = conn.cursor()
cursor.execute("""
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA='abcbimart' AND TABLE_NAME='dim_work_orders'
    ORDER BY ORDINAL_POSITION
""")
print('dim_work_orders columns:')
for row in cursor.fetchall():
    print(f'  {row[0]}')
conn.close()
