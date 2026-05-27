-- ============================================================
-- config data for report: Monthly_BIMIO_494
-- Tool 3 output -- idempotent, safe to re-run.
-- ============================================================

DECLARE @report_id INT;

-- ── config.report ──────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM config.report WHERE report_name = 'Monthly_BIMIO_494')
BEGIN
    INSERT INTO config.report
        (report_name, display_name, pipeline_name, report_category, description, schedule_time,
         output_container, template_container, template_name, template_blob_path, is_active)
    VALUES (
        'Monthly_BIMIO_494',
        NULL,
        'PL_Generic_Monthly',
        'MONTHLY',
        'Script Attributes',
        '06:00',
        'monthly-bimio-494',
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
    SET    pipeline_name      = 'PL_Generic_Monthly',
           report_category    = 'MONTHLY',
           template_container = 'toad-poc-reports'
    WHERE  report_name = 'Monthly_BIMIO_494';
END
SET @report_id = (SELECT report_id FROM config.report WHERE report_name = 'Monthly_BIMIO_494');

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
    VALUES (@report_id, 'REPORT_MAIN', N'WITH dte AS
(SELECT maxrpd.fn_get_fin_start_dt (ADD_MONTHS (CAST(GETDATE(), ''mm'' AS DATE), -1)) stdte,
      CAST(GETDATE(), ''mm'' AS DATE) endte
 FROM DUAL)

SELECT w.WONUM
          "Workorder",
       w.XJOBTYPE
          "Job Type",
       w.REPORTEDBY
          "ID",
       CASE
          WHEN p.FIRSTNAME IS NULL THEN w.REPORTEDBY
          ELSE p.FIRSTNAME || '' '' || p.LASTNAME
       END
          "Name",
       TO_DATE(w.REPORT_DATE)
          "Reported Date",
       w.XJOBPRIORITY
          "Job Priority",
       w.REPORTEDBY,
       (SELECT MAX (persongroup)
        FROM maximo.persongroupteam
        WHERE persongroup LIKE ''CRM%'' AND respparty = w.reportedby)
          "Reported By Group"
FROM MAXRPD.T_ODS_WOSTATUS w
     JOIN maximo.person p ON p.PERSONID = w.REPORTEDBY
     CROSS JOIN dte
WHERE     w.WORKTYPE IN (''METERING'', ''EMERGENCY'')
      AND w.XJOBPRIORITY IN (''E1'',
                             ''E2'',
                             ''M1'',
                             ''M2'')

      AND w.REPORT_DATE BETWEEN dte.stdte AND dte.endte

ORDER BY w.REPORT_DATE', 'Y');
ELSE
    UPDATE config.report_sql
    SET    query_text = N'WITH dte AS
(SELECT maxrpd.fn_get_fin_start_dt (ADD_MONTHS (CAST(GETDATE(), ''mm'' AS DATE), -1)) stdte,
      CAST(GETDATE(), ''mm'' AS DATE) endte
 FROM DUAL)

SELECT w.WONUM
          "Workorder",
       w.XJOBTYPE
          "Job Type",
       w.REPORTEDBY
          "ID",
       CASE
          WHEN p.FIRSTNAME IS NULL THEN w.REPORTEDBY
          ELSE p.FIRSTNAME || '' '' || p.LASTNAME
       END
          "Name",
       TO_DATE(w.REPORT_DATE)
          "Reported Date",
       w.XJOBPRIORITY
          "Job Priority",
       w.REPORTEDBY,
       (SELECT MAX (persongroup)
        FROM maximo.persongroupteam
        WHERE persongroup LIKE ''CRM%'' AND respparty = w.reportedby)
          "Reported By Group"
FROM MAXRPD.T_ODS_WOSTATUS w
     JOIN maximo.person p ON p.PERSONID = w.REPORTEDBY
     CROSS JOIN dte
WHERE     w.WORKTYPE IN (''METERING'', ''EMERGENCY'')
      AND w.XJOBPRIORITY IN (''E1'',
                             ''E2'',
                             ''M1'',
                             ''M2'')

      AND w.REPORT_DATE BETWEEN dte.stdte AND dte.endte

ORDER BY w.REPORT_DATE', is_active = 'Y'
    WHERE  report_id = @report_id AND query_type = 'REPORT_MAIN';

-- ── config.report_email ────────────────────────────────────
-- Real emails: is_active=N (inactive)  |  POC team emails: is_active=Y (active)
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
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid156@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid156@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid156@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid158@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid158@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid158@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid159@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid159@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid159@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid155@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid155@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid155@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid153@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid153@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid153@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid154@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid154@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid154@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid157@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid157@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid157@company1.com' AND recipient_group = 'OPERATIONS';
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
WHERE  r.report_name = 'Monthly_BIMIO_494';

SELECT rs.query_type, LEFT(rs.query_text, 100) AS query_preview
FROM   config.report_sql rs
JOIN   config.report r ON r.report_id = rs.report_id
WHERE  r.report_name = 'Monthly_BIMIO_494';

SELECT r.report_name, re.recipient_group, re.email_type, re.email_address
FROM   config.report r
JOIN   config.report_email re ON re.report_id = r.report_id
WHERE  r.report_name = 'Monthly_BIMIO_494'
ORDER  BY re.recipient_group, re.email_type, re.email_address;
