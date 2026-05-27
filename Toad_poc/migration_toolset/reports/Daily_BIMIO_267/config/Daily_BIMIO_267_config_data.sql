-- ============================================================
-- config data for report: Daily_BIMIO_267
-- Tool 3 output -- idempotent, safe to re-run.
-- ============================================================

DECLARE @report_id INT;

-- ── config.report ──────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM config.report WHERE report_name = 'Daily_BIMIO_267')
BEGIN
    INSERT INTO config.report
        (report_name, display_name, pipeline_name, report_category, description, schedule_time,
         output_container, template_container, template_name, template_blob_path, is_active)
    VALUES (
        'Daily_BIMIO_267',
        NULL,
        'PL_Generic_Daily',
        'DAILY',
        'Script Attributes',
        '06:00',
        'daily-bimio-267',
        'toad-poc-reports',
        NULL,
        NULL,
        'Y'
    );
END
ELSE
BEGIN
    -- Update pipeline_name, category and template container if re-run
    UPDATE config.report
    SET    pipeline_name      = 'PL_Generic_Daily',
           report_category    = 'DAILY',
           template_container = 'toad-poc-reports'
    WHERE  report_name = 'Daily_BIMIO_267';
END
SET @report_id = (SELECT report_id FROM config.report WHERE report_name = 'Daily_BIMIO_267');

-- ── config.report_sql ──────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM config.report_sql
              WHERE report_id = @report_id AND query_type = 'ODS_CHECK')
    INSERT INTO config.report_sql (report_id, query_type, query_text, is_active)
    VALUES (@report_id, 'ODS_CHECK', N'SELECT COUNT(*) AS row_count
from MAXRPD.T_ODS_LOG
where CAST(ems AS DATE) = CAST(GETDATE() AS DATE)', 'Y');
ELSE
    UPDATE config.report_sql
    SET    query_text = N'SELECT COUNT(*) AS row_count
from MAXRPD.T_ODS_LOG
where CAST(ems AS DATE) = CAST(GETDATE() AS DATE)', is_active = 'Y'
    WHERE  report_id = @report_id AND query_type = 'ODS_CHECK';

IF NOT EXISTS (SELECT 1 FROM config.report_sql
              WHERE report_id = @report_id AND query_type = 'REPORT_MAIN')
    INSERT INTO config.report_sql (report_id, query_type, query_text, is_active)
    VALUES (@report_id, 'REPORT_MAIN', N'SELECT
network AS "Network"
,ldz
,depot AS "Depot"
,work_order_number AS "Work Order"
,rwonum AS "Root Work Order"
,reported_date_time AS "Emergency Date"
,prevented AS "Gas Prevented"
,difference AS "Time Difference"
,display_address AS "Address"

,CASE WHEN prevented > DATEFROMPARTS(YEAR(GETDATE(), MONTH(GETDATE(), 1)-1) then 1 else 0 end AS "MTD"
,CASE WHEN difference <=12 then 1 else 0 end AS "Less 12"
,CASE WHEN difference >12 then 1 else 0 end AS "Great 12"
,1 AS "Count"

FROM
(SELECT dorg.network,
       dorg.ldz,
       CASE WHEN dorg.depot_work_group = ''HILLINGTON'' THEN ''PAISLEY'' ELSE dorg.depot_work_group END depot,
       prev_dwor.work_order_number,
       dwor.work_order_number rwonum,
       dwor.reported_date_time,

       (CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATE) || '' '' || RIGHT(dtim.hour_24_minute,8)) AS DATETIME2 prevented,

        ROUND(1.0* DATEDIFF(MINUTE,
                dwor.reported_date_time,
                (CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATE) || '' '' || RIGHT(dtim.hour_24_minute,8)) AS DATETIME2
                )
                /60, 2) difference,

       dadr.DISPLAY_ADDRESS
  FROM abctozbimart.fct_gas_escapes_v ge
       JOIN abctozbimart.dim_work_orders dwor
          ON ge.dwor_id_root = dwor.ID
       JOIN abctozbimart.dim_organisation dorg
          ON ge.dorg_id_root = dorg.ID
       JOIN abctozbimart.dim_addresses dadr
          ON ge.dadr_id_root = dadr.ID
        JOIN abctozbimart.dim_calendar dcal
          ON ge.dcal_id_gas_prevented_date = dcal.ID
        JOIN abctozbimart.dim_time dtim
          ON ge.dtim_id_gas_prevented_time = dtim.ID
        JOIN abctozbimart.dim_work_orders prev_dwor
          ON ge.dwor_id_gas_prevented = prev_dwor.ID
 WHERE ge.latest = ''Y''
 and dcal.DATE_ORACLE >= DATEADD(MONTH, 3, DATEFROMPARTS(YEAR(date_add(''month'', -3,(DATEADD(DAY, -1, GETDATE(), 1, 1)-3)))))
 and dcal.DATE_ORACLE < CAST(GETDATE( AS DATE)))', 'Y');
ELSE
    UPDATE config.report_sql
    SET    query_text = N'SELECT
network AS "Network"
,ldz
,depot AS "Depot"
,work_order_number AS "Work Order"
,rwonum AS "Root Work Order"
,reported_date_time AS "Emergency Date"
,prevented AS "Gas Prevented"
,difference AS "Time Difference"
,display_address AS "Address"

,CASE WHEN prevented > DATEFROMPARTS(YEAR(GETDATE(), MONTH(GETDATE(), 1)-1) then 1 else 0 end AS "MTD"
,CASE WHEN difference <=12 then 1 else 0 end AS "Less 12"
,CASE WHEN difference >12 then 1 else 0 end AS "Great 12"
,1 AS "Count"

FROM
(SELECT dorg.network,
       dorg.ldz,
       CASE WHEN dorg.depot_work_group = ''HILLINGTON'' THEN ''PAISLEY'' ELSE dorg.depot_work_group END depot,
       prev_dwor.work_order_number,
       dwor.work_order_number rwonum,
       dwor.reported_date_time,

       (CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATE) || '' '' || RIGHT(dtim.hour_24_minute,8)) AS DATETIME2 prevented,

        ROUND(1.0* DATEDIFF(MINUTE,
                dwor.reported_date_time,
                (CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATE) || '' '' || RIGHT(dtim.hour_24_minute,8)) AS DATETIME2
                )
                /60, 2) difference,

       dadr.DISPLAY_ADDRESS
  FROM abctozbimart.fct_gas_escapes_v ge
       JOIN abctozbimart.dim_work_orders dwor
          ON ge.dwor_id_root = dwor.ID
       JOIN abctozbimart.dim_organisation dorg
          ON ge.dorg_id_root = dorg.ID
       JOIN abctozbimart.dim_addresses dadr
          ON ge.dadr_id_root = dadr.ID
        JOIN abctozbimart.dim_calendar dcal
          ON ge.dcal_id_gas_prevented_date = dcal.ID
        JOIN abctozbimart.dim_time dtim
          ON ge.dtim_id_gas_prevented_time = dtim.ID
        JOIN abctozbimart.dim_work_orders prev_dwor
          ON ge.dwor_id_gas_prevented = prev_dwor.ID
 WHERE ge.latest = ''Y''
 and dcal.DATE_ORACLE >= DATEADD(MONTH, 3, DATEFROMPARTS(YEAR(date_add(''month'', -3,(DATEADD(DAY, -1, GETDATE(), 1, 1)-3)))))
 and dcal.DATE_ORACLE < CAST(GETDATE( AS DATE)))', is_active = 'Y'
    WHERE  report_id = @report_id AND query_type = 'REPORT_MAIN';

-- ── config.report_email ────────────────────────────────────
-- Real emails: is_active=N (inactive)  |  POC team emails: is_active=Y (active)
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid80@company1.com' AND recipient_group = 'ALERT_ONLY')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid80@company1.com', 'ALERT_ONLY', 'CC', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid80@company1.com' AND recipient_group = 'ALERT_ONLY';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'karnaradha80@gmail.com' AND recipient_group = 'ALERT_ONLY')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'karnaradha80@gmail.com', 'ALERT_ONLY', 'CC', 'Y');
ELSE
    UPDATE config.report_email
    SET    is_active = 'Y'
    WHERE  report_id = @report_id AND email_address = 'karnaradha80@gmail.com' AND recipient_group = 'ALERT_ONLY';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid18@company1.com' AND recipient_group = 'BI_TEAM')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid18@company1.com', 'BI_TEAM', 'BCC', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid18@company1.com' AND recipient_group = 'BI_TEAM';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'krkrishnan80@gmail.com' AND recipient_group = 'BI_TEAM')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'krkrishnan80@gmail.com', 'BI_TEAM', 'BCC', 'Y');
ELSE
    UPDATE config.report_email
    SET    is_active = 'Y'
    WHERE  report_id = @report_id AND email_address = 'krkrishnan80@gmail.com' AND recipient_group = 'BI_TEAM';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid30@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid30@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid30@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid31@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid31@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid31@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid32@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid32@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid32@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid33@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid33@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid33@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid34@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid34@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid34@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid29@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid29@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid29@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid35@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid35@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid35@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid36@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid36@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid36@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid37@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid37@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid37@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid53@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid53@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid53@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid3@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid3@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid3@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid98@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid98@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid98@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid44@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid44@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid44@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid49@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid49@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid49@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid117@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid117@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid117@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid8@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid8@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid8@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid26@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid26@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid26@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid21@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid21@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid21@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid109@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid109@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid109@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid22@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid22@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid22@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid95@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid95@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid95@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid16@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid16@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid16@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid129@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid129@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid129@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid24@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid24@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid24@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid87@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid87@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid87@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid50@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid50@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid50@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid43@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid43@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid43@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid116@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid116@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid116@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid104@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid104@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid104@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid7@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid7@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid7@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid99@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid99@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid99@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid70@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid70@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid70@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid93@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid93@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid93@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid13@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid13@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid13@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid97@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid97@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid97@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid101@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid101@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid101@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid115@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid115@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid115@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid137@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid137@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid137@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid73@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid73@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid73@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid94@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid94@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid94@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid110@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid110@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid110@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid40@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid40@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid40@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid41@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid41@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid41@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid76@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid76@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid76@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid128@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid128@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid128@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid122@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid122@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid122@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid71@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid71@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid71@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid51@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid51@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid51@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid100@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid100@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid100@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid10@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid10@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid10@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid135@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid135@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid135@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid78@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid78@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid78@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid23@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid23@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid23@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid12@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid12@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid12@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid1@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid1@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid1@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid27@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid27@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid27@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid9@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid9@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid9@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid111@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid111@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid111@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid90@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid90@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid90@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid79@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid79@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid79@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid2@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid2@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid2@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid6@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid85@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid85@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid85@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid133@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid133@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid133@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid61@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid61@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid61@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid127@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid127@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid127@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid106@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid106@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid106@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid14@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid14@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid14@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid121@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid121@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid121@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid91@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid91@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid91@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid69@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid69@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid69@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid118@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid118@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid118@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid96@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid96@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid96@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid5@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid5@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid5@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid19@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid19@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid19@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid25@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid25@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid25@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid28@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid28@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid28@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid38@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid38@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid38@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid39@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid39@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid39@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid48@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid48@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid48@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid52@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid52@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid52@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid55@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid55@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid55@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid59@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid59@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid59@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid60@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid60@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid60@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid62@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid62@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid62@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid64@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid64@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid64@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid65@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid65@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid65@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid66@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid66@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid66@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid68@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid68@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid68@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid74@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid74@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid74@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid75@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid75@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid75@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid81@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid81@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid81@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid82@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid82@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid82@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid84@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid84@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid84@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid89@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid89@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid89@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid124@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid124@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid124@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid102@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid102@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid102@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid107@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid107@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid107@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid108@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid108@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid108@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid113@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid113@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid113@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid114@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid114@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid114@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid126@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid126@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid126@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid130@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid130@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid130@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid134@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid134@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid134@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid136@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid136@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid136@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid138@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid138@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid138@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid139@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid86@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid86@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid86@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid20@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid20@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid20@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid92@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid92@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid92@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid67@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid67@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid67@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid17@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid17@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid17@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid120@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid120@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid120@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid119@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid119@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid119@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid15@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid15@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid15@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid72@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid72@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid72@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid88@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid88@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid88@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid103@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid103@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid103@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid105@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid105@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid105@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid57@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid57@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid57@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid63@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid63@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid63@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid123@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid123@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid123@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid125@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid125@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid125@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid54@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid54@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid54@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid112@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid112@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid112@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid46@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid46@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid46@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid47@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid47@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid47@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid4@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid4@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid4@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid77@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid77@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid77@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid83@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid83@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid83@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid11@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid11@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid11@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid45@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid45@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid45@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid56@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid56@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid56@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid58@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid58@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid58@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid42@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid42@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid42@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid132@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid132@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid132@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'karnaradha80@gmail.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'karnaradha80@gmail.com', 'OPERATIONS', 'TO', 'Y');
ELSE
    UPDATE config.report_email
    SET    is_active = 'Y'
    WHERE  report_id = @report_id AND email_address = 'karnaradha80@gmail.com' AND recipient_group = 'OPERATIONS';

-- ── verify ─────────────────────────────────────────────────
SELECT r.report_name, r.template_container, r.template_name, r.template_blob_path
FROM   config.report r
WHERE  r.report_name = 'Daily_BIMIO_267';

SELECT rs.query_type, LEFT(rs.query_text, 100) AS query_preview
FROM   config.report_sql rs
JOIN   config.report r ON r.report_id = rs.report_id
WHERE  r.report_name = 'Daily_BIMIO_267';

SELECT r.report_name, re.recipient_group, re.email_type, re.email_address
FROM   config.report r
JOIN   config.report_email re ON re.report_id = r.report_id
WHERE  r.report_name = 'Daily_BIMIO_267'
ORDER  BY re.recipient_group, re.email_type, re.email_address;
