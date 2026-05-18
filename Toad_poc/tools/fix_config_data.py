import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};SERVER=sql-toad-poc.database.windows.net;'
    'DATABASE=db-toad-poc;UID=sqladmin;PWD=ToadPoc@2026!;'
    'Encrypt=yes;TrustServerCertificate=no;',
    autocommit=True
)
cursor = conn.cursor()

cursor.execute("SET IDENTITY_INSERT config.report ON")
cursor.execute("DELETE FROM config.report WHERE report_id = 0")
cursor.execute(
    "INSERT INTO config.report (report_id, report_name, description, schedule, output_format, is_active) "
    "VALUES (1, 'BC_BIMIO_267_Daily', 'BIMIO 267 - 12 Hour Prevented Daily (MTD, YTD)', 'Daily', 'CSV', 'Y')"
)
cursor.execute("SET IDENTITY_INSERT config.report OFF")

rows = [
    (1, 'ops.depot_a@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_b@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_c@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_d@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_e@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_f@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_g@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_h@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'ops.depot_i@abc.co.uk',   'TO',  'OPERATIONS', 'Y'),
    (1, 'buin@abc.co.uk',          'BCC', 'BI_TEAM',    'Y'),
    (1, 'bi.support@abc.co.uk',    'BCC', 'BI_TEAM',    'Y'),
    (1, 'manager.name1@abc.co.uk', 'CC',  'ALERT_ONLY', 'Y'),
    (1, 'manager.name2@abc.co.uk', 'CC',  'ALERT_ONLY', 'Y'),
]
cursor.executemany(
    "INSERT INTO config.report_email (report_id, email_address, email_type, recipient_group, is_active) "
    "VALUES (?,?,?,?,?)", rows
)

cursor.execute("SELECT COUNT(*) FROM config.report")
print(f"config.report:       {cursor.fetchone()[0]} rows")
cursor.execute("SELECT COUNT(*) FROM config.report_email")
print(f"config.report_email: {cursor.fetchone()[0]} rows")

conn.close()
print("Done.")
