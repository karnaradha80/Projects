-- ============================================================
-- config data for report: Weekly__BIMIO_384
-- Tool 3 output -- idempotent, safe to re-run.
-- ============================================================

DECLARE @report_id INT;

-- ── config.report ──────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM config.report WHERE report_name = 'Weekly__BIMIO_384')
BEGIN
    INSERT INTO config.report
        (report_name, display_name, pipeline_name, report_category, description, schedule_time,
         output_container, template_container, template_name, template_blob_path, is_active)
    VALUES (
        'Weekly__BIMIO_384',
        NULL,
        'PL_Generic_Weekly',
        'WEEKLY',
        'Script Attributes',
        '06:00',
        'weekly-bimio-384',
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
    SET    pipeline_name      = 'PL_Generic_Weekly',
           report_category    = 'WEEKLY',
           template_container = 'toad-poc-reports'
    WHERE  report_name = 'Weekly__BIMIO_384';
END
SET @report_id = (SELECT report_id FROM config.report WHERE report_name = 'Weekly__BIMIO_384');

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
    VALUES (@report_id, 'REPORT_MAIN', N'SELECT s.xldz AS "LDZ",
       s.xdepot AS "Depot",
       s.worktype AS "Workstream",
       s.LEAD AS "Engineer",
       name.fco AS "Engineer Name",
       name.tm AS "Team Manager Name",
       s.wonum AS "Workorder No.",
       s.XJOBTYPE "Job Type",
       s.XJOBPRIORITY "Job Priority",
       s.ACTSTART AS "Actual Start",
       s.ACTFINISH AS "Actual Finish",
    extract(hour from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR''))||'':''||
    extract(minute from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR''))||'':''||
    round(extract(second from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR'')))
    AS "Time On Site (HH:MM:SS)",
    (select max(estdur) from maximo.workorder where wonum = s.wonum) AS "Duration (Hours)"

  FROM MAXRPD.T_ODS_WOSTATUS s join
  (select a.personid, a.firstname||'' ''||a.lastname fco, b.firstname||'' ''||b.lastname tm from maximo.person a join maximo.person b on a.SUPERVISOR = b.personid
  where a.title = ''FCO'' ) name
  on  name.personid = s.lead
 WHERE

s.STAT_ONSITE BETWEEN CAST(GETDATE() AS DATE) - 7 AND CAST(GETDATE() AS DATE)
       AND s.WORKTYPE IN (''EMERGENCY'', ''METERING'', ''REPAIR'')
       AND s.WONUM LIKE ''W%''
       AND s.status IN (''COMP'', ''CLOSE'')
       AND (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24 >
              (SELECT MAX (estdur + (10 / 60))
                 FROM maximo.workorder
                WHERE wonum = s.wonum)
       AND s.stat_lnjob IS NULL
GROUP BY s.xldz,
         s.xdepot,
         s.worktype,
         s.LEAD,
         name.fco,
         name.tm,
         s.wonum,
         s.REPORT_DATE,
         s.XJOBTYPE,
         s.XJOBPRIORITY,
         s.actstart,
         s.actfinish,
          (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24', 'Y');
ELSE
    UPDATE config.report_sql
    SET    query_text = N'SELECT s.xldz AS "LDZ",
       s.xdepot AS "Depot",
       s.worktype AS "Workstream",
       s.LEAD AS "Engineer",
       name.fco AS "Engineer Name",
       name.tm AS "Team Manager Name",
       s.wonum AS "Workorder No.",
       s.XJOBTYPE "Job Type",
       s.XJOBPRIORITY "Job Priority",
       s.ACTSTART AS "Actual Start",
       s.ACTFINISH AS "Actual Finish",
    extract(hour from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR''))||'':''||
    extract(minute from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR''))||'':''||
    round(extract(second from numtodsinterval(( (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24),''HOUR'')))
    AS "Time On Site (HH:MM:SS)",
    (select max(estdur) from maximo.workorder where wonum = s.wonum) AS "Duration (Hours)"

  FROM MAXRPD.T_ODS_WOSTATUS s join
  (select a.personid, a.firstname||'' ''||a.lastname fco, b.firstname||'' ''||b.lastname tm from maximo.person a join maximo.person b on a.SUPERVISOR = b.personid
  where a.title = ''FCO'' ) name
  on  name.personid = s.lead
 WHERE

s.STAT_ONSITE BETWEEN CAST(GETDATE() AS DATE) - 7 AND CAST(GETDATE() AS DATE)
       AND s.WORKTYPE IN (''EMERGENCY'', ''METERING'', ''REPAIR'')
       AND s.WONUM LIKE ''W%''
       AND s.status IN (''COMP'', ''CLOSE'')
       AND (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24 >
              (SELECT MAX (estdur + (10 / 60))
                 FROM maximo.workorder
                WHERE wonum = s.wonum)
       AND s.stat_lnjob IS NULL
GROUP BY s.xldz,
         s.xdepot,
         s.worktype,
         s.LEAD,
         name.fco,
         name.tm,
         s.wonum,
         s.REPORT_DATE,
         s.XJOBTYPE,
         s.XJOBPRIORITY,
         s.actstart,
         s.actfinish,
          (NVL (s.STAT_COMP, s.STAT_TRMNT) - s.STAT_ONSITE) * 24', is_active = 'Y'
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
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid166@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid166@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid166@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid169@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid169@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid169@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid160@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid160@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid160@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid196@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid196@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid196@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid182@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid182@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid182@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid125@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid125@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid125@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid64@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid64@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid64@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid171@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid171@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid171@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid119@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid119@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid119@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid191@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid191@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid191@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid161@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid161@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid161@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid165@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid165@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid165@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid180@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid180@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid180@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid164@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid164@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid164@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid173@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid173@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid173@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid177@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid177@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid177@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid41@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid41@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid41@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid111@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid111@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid111@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid2@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid2@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid2@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid185@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid185@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid185@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid167@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid167@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid167@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid6@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid168@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid168@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid168@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid170@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid170@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid170@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid174@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid174@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid174@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid178@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid178@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid178@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid45@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid45@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid45@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid48@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid48@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid48@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid181@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid181@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid181@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid183@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid183@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid183@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid187@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid187@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid187@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid62@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid62@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid62@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid188@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid188@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid188@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid190@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid190@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid190@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid124@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid124@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid124@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid109@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid109@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid109@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid192@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid192@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid192@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid194@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid194@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid194@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid120@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid120@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid120@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid195@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid195@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid195@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid136@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid136@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid136@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid14@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid14@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid14@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid52@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid52@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid52@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid115@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid115@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid115@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid176@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid176@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid176@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid179@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid179@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid179@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid175@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid175@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid175@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid186@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid186@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid186@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid163@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid163@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid163@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid162@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid162@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid162@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid72@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid72@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid72@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid139@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid114@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid114@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid114@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid172@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid172@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid172@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid105@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid105@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid105@company1.com' AND recipient_group = 'OPERATIONS';
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
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid193@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid193@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid193@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid77@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid77@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid77@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid189@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid189@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid189@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid132@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid132@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid132@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid184@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid184@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid184@company1.com' AND recipient_group = 'OPERATIONS';
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
WHERE  r.report_name = 'Weekly__BIMIO_384';

SELECT rs.query_type, LEFT(rs.query_text, 100) AS query_preview
FROM   config.report_sql rs
JOIN   config.report r ON r.report_id = rs.report_id
WHERE  r.report_name = 'Weekly__BIMIO_384';

SELECT r.report_name, re.recipient_group, re.email_type, re.email_address
FROM   config.report r
JOIN   config.report_email re ON re.report_id = r.report_id
WHERE  r.report_name = 'Weekly__BIMIO_384'
ORDER  BY re.recipient_group, re.email_type, re.email_address;
