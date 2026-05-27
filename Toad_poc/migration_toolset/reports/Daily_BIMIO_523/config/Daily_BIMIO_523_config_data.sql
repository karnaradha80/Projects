-- ============================================================
-- config data for report: Daily_BIMIO_523
-- Tool 3 output -- idempotent, safe to re-run.
-- ============================================================

DECLARE @report_id INT;

-- ── config.report ──────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM config.report WHERE report_name = 'Daily_BIMIO_523')
BEGIN
    INSERT INTO config.report
        (report_name, display_name, pipeline_name, report_category, description, schedule_time,
         output_container, template_container, template_name, template_blob_path, is_active)
    VALUES (
        'Daily_BIMIO_523',
        NULL,
        'PL_Generic_Daily',
        'DAILY',
        'Script Attributes',
        '06:00',
        'daily-bimio-523',
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
    WHERE  report_name = 'Daily_BIMIO_523';
END
SET @report_id = (SELECT report_id FROM config.report WHERE report_name = 'Daily_BIMIO_523');

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
    VALUES (@report_id, 'REPORT_MAIN', N'With Assetnum_depot_mapp as (
  select toa.assetnum, lh2.parent depot
    FROM maxrpd.t_ods_assetattr toa
    JOIN maximo.lochierarchy lh ON toa.location = lh.location
    JOIN maximo.lochierarchy lh2 ON lh.parent = lh2.location)

SELECT Rep_Inc_GiP.Work_Order,
       Rep_Inc_GiP.Root_Work_Order,
       CASE WHEN Rep_Inc_GiP.wo_depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE Rep_Inc_GiP.wo_depot END"wo_depot",
       CASE WHEN Rep_Inc_GiP.asset_depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE Rep_Inc_GiP.asset_depot END"asset_depot",
       Rep_Inc_GiP.Asset,

       Rep_Inc_GiP.description,
       Rep_Inc_GiP."Comment on WO SiteReport",
       Rep_Inc_GiP.priority,
       Rep_Inc_GiP.job_type,
       Rep_Inc_GiP."Gas in Property",
       Rep_Inc_GiP."Component",
       Rep_Inc_GiP.RR_Corr_Action "Corrective Action",
       Rep_Inc_GiP.Repairs,
       Rep_Cause.Corrosion,
       Rep_Cause.Fracture,
       Rep_Cause.Failure,
       Rep_Cause.Interference,
       Rep_Cause.Other,
       Rep_Inc_GiP.status,
       Rep_Inc_GiP.status_date,
       Rep_Inc_GiP.scheduled_start,
       Rep_Inc_GiP.actual_finish,
       Rep_Inc_GiP.Location,
       Rep_Inc_GiP.principal_street,
       Rep_Inc_GiP.post_town,
       Rep_Inc_GiP.out_code,
       Rep_Inc_GiP.in_code,
       Rep_Inc_GiP.Lead_Id,
       Rep_Inc_GiP.Lead_Name,
       Rep_Inc_GiP.Material,
       Rep_Inc_GiP.Diameter
  FROM    (

             SELECT RepairWO.wonum Work_Order,
                    RepairWO.xrootwonum Root_Work_Order,
                    RepairWO.persongroup wo_depot,
                    RepairWO.depot asset_depot,
                    RepairWO.description description,
                    RepairWO.xjobtype job_type,

                    CASE
                       WHEN RepairWO.xjobtype = ''MR''
                       THEN
                          CASE
                             WHEN RepairWO.RR_Gas = ''NO''
                             THEN
                                CASE
                                   WHEN RootWO.xisgasinproperty = ''YES''
                                   THEN
                                      ''NO  [Root WO: Gas in Property = YES]''
                                   ELSE
                                      CASE
                                         WHEN RootWO.xisgasinproperty = ''NO''
                                         THEN
                                            ''NO  [Root WO: Gas in Property = NO]''
                                         ELSE
                                            ''NO  [Root WO: Gas in Property not recorded]''
                                      END
                                END
                             ELSE
                                RepairWO.RR_Gas
                          END
                       ELSE
                          RepairWO.RR_Gas
                    END
                       AS "Gas in Property",
                    RepairWO.RR_Component AS "Component",
                    RepairWO.RR_Corr_Action,
                    RepairWO.wopriority priority,
                    RepairWO.status status,
                    RepairWO.statusdate status_date,
                    RepairWO.schedstart scheduled_start,
                    RepairWO.actfinish actual_finish,
                    RepairWO.Asset,
                    RepairWO.Location,
                    RepairWO.material,
                    RepairWO.Diameter,
                    RepairWO.xprincipalstreet principal_street,
                    RepairWO.xposttown post_town,
                    RepairWO.xoutcode out_code,
                    RepairWO.xincode in_code,
                    RepairWO.Lead_Id,
                    RepairWO.Lead_Name,
                    COUNT (RepairWO.wonum) Repairs,
                    RepairWO.xcomment AS "Comment on WO SiteReport"
               FROM    (

                        SELECT w.wonum,
                               w.xrootwonum,
                               CASE WHEN w.persongroup = ''HILLINGTON'' THEN ''PAISLEY'' ELSE w.persongroup END persongroup,
                               CASE WHEN b.depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE b.depot END depot,
                               w.description,
                               w.xjobtype,
                               w.wopriority,
                               w.status,
                               rr.xgasinproperty RR_Gas,
                               rr.xleakage_comp RR_Component,
                               rr.xleak_corr_action RR_Corr_Action,
                               w.statusdate,
                               w.schedstart,
                               w.actfinish,
                               TO_NUMBER (w.assetnum)AS Asset,
                               a.MATERIAL,
                               a.DIAMETER,
                               TO_NUMBER (w.location) AS Location,
                               x.xprincipalstreet,
                               x.xposttown,
                               x.xoutcode,
                               x.xincode,
                               w.siteid,
                               w.LEAD AS Lead_Id,
                               p.lastname || ('', '' || p.firstname) AS Lead_Name,
                               sr.xcomment
                         FROM maxrpd.workorder_mv w
                         left outer  join maximo.person p
                         on w.LEAD = p.personid
                         left outer join maxrpd.t_ods_assetattr a
                         on w.assetnum = a.assetnum

                         left outer join Assetnum_depot_mapp b
                         on a.assetnum = b.assetnum
                         left outer join maximo.xwoaddress x
                         on w.wonum = x.xwonum
                         left outer join maximo.xsitereport sr
                         on w.wonum = sr.xwonum
                         left outer join maximo.xwocompletion rr
                         on w.wonum = rr.xwonum
                         WHERE
                                w.worktype = ''REPAIR''
                               AND w.status = ''COMP''
                               AND w.siteid = ''SCOTLAND''
                               AND w.statusdate
                               >=

                                      CASE
                                         WHEN trim(TO_CHAR (GETDATE(), ''DAY'')) = ''MONDAY''
                                         THEN
                                            TO_CHAR (GETDATE() - 3,
                                                     ''DD-Mon-YYYY'')
                                         ELSE
                                            TO_CHAR (GETDATE() - 1,
                                                     ''DD-Mon-YYYY'')
                                      END
                               AND w.statusdate <

                                     TO_CHAR (GETDATE(), ''DD-Mon-YYYY'')
                               AND rr.xigt <> 1
                               AND rr.xigtcode IS NULL
                               AND rr.xleakage_cause IS NOT NULL) RepairWO
                    LEFT JOIN
                       (

                        SELECT w.wonum, s.xisgasinproperty
                          FROM maxrpd.workorder_mv w
                        left outer join maximo.xsitereport s
                          on  w.wonum = s.xwonum
                         ) RootWO
                    ON RootWO.wonum = RepairWO.xrootwonum
           GROUP BY RepairWO.wonum,
                    RepairWO.xrootwonum,
                    RepairWO.persongroup,
                    RepairWO.depot,
                    RepairWO.description,
                    RepairWO.xjobtype,
                    RepairWO.wopriority,
                    RepairWO.status,
                    RepairWO.RR_Gas,
                    RepairWO.RR_Component,
                    RepairWO.RR_Corr_Action,
                    RootWO.xisgasinproperty,
                    RepairWO.statusdate,
                    RepairWO.schedstart,
                    RepairWO.actfinish,
                    RepairWO.Asset,
                    RepairWO.LOCATION,
                    RepairWO.Material,
                    RepairWO.Diameter,
                    RepairWO.xprincipalstreet,
                    RepairWO.xposttown,
                    RepairWO.xoutcode,
                    RepairWO.xincode,
                    RepairWO.siteid,
                    RepairWO.Lead_Id,
                    RepairWO.Lead_Name,
                    RepairWO.xcomment
           ORDER BY RepairWO.xjobtype) Rep_Inc_GiP
       INNER JOIN
          (

             SELECT WO,
                    SUM (Repairs) AS Repairs,
                    NVL (MAX (DECODE (Rep_Category, ''Corrosion'', Repairs)), 0)
                       AS Corrosion,
                    NVL (MAX (DECODE (Rep_Category, ''Fracture'', Repairs)), 0)
                       AS Fracture,
                    NVL (MAX (DECODE (Rep_Category, ''Failure'', Repairs)), 0)
                       AS Failure,
                    NVL (MAX (DECODE (Rep_Category, ''Interference'', Repairs)),
                         0)
                       AS Interference,
                    NVL (MAX (DECODE (Rep_Category, ''Other'', Repairs)), 0)
                       AS Other
               FROM (
                     SELECT   WO_ID AS WO, Rep_Category, COUNT (WO_ID) AS Repairs
                         FROM (

                               SELECT w.wonum WO_ID,
                                      CASE rr.xleakage_cause
                                         WHEN ''CO'' THEN ''Corrosion''
                                         WHEN ''EB'' THEN ''Corrosion''
                                         WHEN ''PH'' THEN ''Corrosion''
                                         WHEN ''SC'' THEN ''Corrosion''
                                         WHEN ''CR'' THEN ''Fracture''
                                         WHEN ''LG'' THEN ''Fracture''
                                         WHEN ''ST'' THEN ''Fracture''
                                         WHEN ''FA'' THEN ''Failure''
                                         WHEN ''IN'' THEN ''Interference''
                                         ELSE ''Other''
                                      END
                                         AS Rep_Category
                                 FROM maxrpd.workorder_mv w
                                 join maximo.xwocompletion rr
                                 on w.wonum = rr.xwonum
                                WHERE
                                       w.worktype = ''REPAIR''
                                      AND w.status = ''COMP''
                                      AND w.siteid = ''SCOTLAND''
                                      AND w.statusdate

                                      >=

                                             CASE
                                                WHEN trim(TO_CHAR (GETDATE(), ''DAY'')) = ''MONDAY''
                                                THEN
                                                   TO_CHAR (GETDATE() - 3,
                                                            ''DD-Mon-YYYY'')
                                                ELSE
                                                   TO_CHAR (GETDATE() - 1,
                                                            ''DD-Mon-YYYY'')
                                             END
                                      AND w.statusdate <
                                             TO_CHAR (GETDATE(), ''DD-Mon-YYYY'')
                                      AND rr.xigt <> 1
                                      AND rr.xigtcode IS NULL
                                      AND rr.xleakage_cause IS NOT NULL)
                     GROUP BY WO_ID, Rep_Category)
           GROUP BY WO) Rep_Cause
       ON Rep_Inc_GiP.Work_Order = REP_Cause.WO', 'Y');
ELSE
    UPDATE config.report_sql
    SET    query_text = N'With Assetnum_depot_mapp as (
  select toa.assetnum, lh2.parent depot
    FROM maxrpd.t_ods_assetattr toa
    JOIN maximo.lochierarchy lh ON toa.location = lh.location
    JOIN maximo.lochierarchy lh2 ON lh.parent = lh2.location)

SELECT Rep_Inc_GiP.Work_Order,
       Rep_Inc_GiP.Root_Work_Order,
       CASE WHEN Rep_Inc_GiP.wo_depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE Rep_Inc_GiP.wo_depot END"wo_depot",
       CASE WHEN Rep_Inc_GiP.asset_depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE Rep_Inc_GiP.asset_depot END"asset_depot",
       Rep_Inc_GiP.Asset,

       Rep_Inc_GiP.description,
       Rep_Inc_GiP."Comment on WO SiteReport",
       Rep_Inc_GiP.priority,
       Rep_Inc_GiP.job_type,
       Rep_Inc_GiP."Gas in Property",
       Rep_Inc_GiP."Component",
       Rep_Inc_GiP.RR_Corr_Action "Corrective Action",
       Rep_Inc_GiP.Repairs,
       Rep_Cause.Corrosion,
       Rep_Cause.Fracture,
       Rep_Cause.Failure,
       Rep_Cause.Interference,
       Rep_Cause.Other,
       Rep_Inc_GiP.status,
       Rep_Inc_GiP.status_date,
       Rep_Inc_GiP.scheduled_start,
       Rep_Inc_GiP.actual_finish,
       Rep_Inc_GiP.Location,
       Rep_Inc_GiP.principal_street,
       Rep_Inc_GiP.post_town,
       Rep_Inc_GiP.out_code,
       Rep_Inc_GiP.in_code,
       Rep_Inc_GiP.Lead_Id,
       Rep_Inc_GiP.Lead_Name,
       Rep_Inc_GiP.Material,
       Rep_Inc_GiP.Diameter
  FROM    (

             SELECT RepairWO.wonum Work_Order,
                    RepairWO.xrootwonum Root_Work_Order,
                    RepairWO.persongroup wo_depot,
                    RepairWO.depot asset_depot,
                    RepairWO.description description,
                    RepairWO.xjobtype job_type,

                    CASE
                       WHEN RepairWO.xjobtype = ''MR''
                       THEN
                          CASE
                             WHEN RepairWO.RR_Gas = ''NO''
                             THEN
                                CASE
                                   WHEN RootWO.xisgasinproperty = ''YES''
                                   THEN
                                      ''NO  [Root WO: Gas in Property = YES]''
                                   ELSE
                                      CASE
                                         WHEN RootWO.xisgasinproperty = ''NO''
                                         THEN
                                            ''NO  [Root WO: Gas in Property = NO]''
                                         ELSE
                                            ''NO  [Root WO: Gas in Property not recorded]''
                                      END
                                END
                             ELSE
                                RepairWO.RR_Gas
                          END
                       ELSE
                          RepairWO.RR_Gas
                    END
                       AS "Gas in Property",
                    RepairWO.RR_Component AS "Component",
                    RepairWO.RR_Corr_Action,
                    RepairWO.wopriority priority,
                    RepairWO.status status,
                    RepairWO.statusdate status_date,
                    RepairWO.schedstart scheduled_start,
                    RepairWO.actfinish actual_finish,
                    RepairWO.Asset,
                    RepairWO.Location,
                    RepairWO.material,
                    RepairWO.Diameter,
                    RepairWO.xprincipalstreet principal_street,
                    RepairWO.xposttown post_town,
                    RepairWO.xoutcode out_code,
                    RepairWO.xincode in_code,
                    RepairWO.Lead_Id,
                    RepairWO.Lead_Name,
                    COUNT (RepairWO.wonum) Repairs,
                    RepairWO.xcomment AS "Comment on WO SiteReport"
               FROM    (

                        SELECT w.wonum,
                               w.xrootwonum,
                               CASE WHEN w.persongroup = ''HILLINGTON'' THEN ''PAISLEY'' ELSE w.persongroup END persongroup,
                               CASE WHEN b.depot = ''HILLINGTON'' THEN ''PAISLEY'' ELSE b.depot END depot,
                               w.description,
                               w.xjobtype,
                               w.wopriority,
                               w.status,
                               rr.xgasinproperty RR_Gas,
                               rr.xleakage_comp RR_Component,
                               rr.xleak_corr_action RR_Corr_Action,
                               w.statusdate,
                               w.schedstart,
                               w.actfinish,
                               TO_NUMBER (w.assetnum)AS Asset,
                               a.MATERIAL,
                               a.DIAMETER,
                               TO_NUMBER (w.location) AS Location,
                               x.xprincipalstreet,
                               x.xposttown,
                               x.xoutcode,
                               x.xincode,
                               w.siteid,
                               w.LEAD AS Lead_Id,
                               p.lastname || ('', '' || p.firstname) AS Lead_Name,
                               sr.xcomment
                         FROM maxrpd.workorder_mv w
                         left outer  join maximo.person p
                         on w.LEAD = p.personid
                         left outer join maxrpd.t_ods_assetattr a
                         on w.assetnum = a.assetnum

                         left outer join Assetnum_depot_mapp b
                         on a.assetnum = b.assetnum
                         left outer join maximo.xwoaddress x
                         on w.wonum = x.xwonum
                         left outer join maximo.xsitereport sr
                         on w.wonum = sr.xwonum
                         left outer join maximo.xwocompletion rr
                         on w.wonum = rr.xwonum
                         WHERE
                                w.worktype = ''REPAIR''
                               AND w.status = ''COMP''
                               AND w.siteid = ''SCOTLAND''
                               AND w.statusdate
                               >=

                                      CASE
                                         WHEN trim(TO_CHAR (GETDATE(), ''DAY'')) = ''MONDAY''
                                         THEN
                                            TO_CHAR (GETDATE() - 3,
                                                     ''DD-Mon-YYYY'')
                                         ELSE
                                            TO_CHAR (GETDATE() - 1,
                                                     ''DD-Mon-YYYY'')
                                      END
                               AND w.statusdate <

                                     TO_CHAR (GETDATE(), ''DD-Mon-YYYY'')
                               AND rr.xigt <> 1
                               AND rr.xigtcode IS NULL
                               AND rr.xleakage_cause IS NOT NULL) RepairWO
                    LEFT JOIN
                       (

                        SELECT w.wonum, s.xisgasinproperty
                          FROM maxrpd.workorder_mv w
                        left outer join maximo.xsitereport s
                          on  w.wonum = s.xwonum
                         ) RootWO
                    ON RootWO.wonum = RepairWO.xrootwonum
           GROUP BY RepairWO.wonum,
                    RepairWO.xrootwonum,
                    RepairWO.persongroup,
                    RepairWO.depot,
                    RepairWO.description,
                    RepairWO.xjobtype,
                    RepairWO.wopriority,
                    RepairWO.status,
                    RepairWO.RR_Gas,
                    RepairWO.RR_Component,
                    RepairWO.RR_Corr_Action,
                    RootWO.xisgasinproperty,
                    RepairWO.statusdate,
                    RepairWO.schedstart,
                    RepairWO.actfinish,
                    RepairWO.Asset,
                    RepairWO.LOCATION,
                    RepairWO.Material,
                    RepairWO.Diameter,
                    RepairWO.xprincipalstreet,
                    RepairWO.xposttown,
                    RepairWO.xoutcode,
                    RepairWO.xincode,
                    RepairWO.siteid,
                    RepairWO.Lead_Id,
                    RepairWO.Lead_Name,
                    RepairWO.xcomment
           ORDER BY RepairWO.xjobtype) Rep_Inc_GiP
       INNER JOIN
          (

             SELECT WO,
                    SUM (Repairs) AS Repairs,
                    NVL (MAX (DECODE (Rep_Category, ''Corrosion'', Repairs)), 0)
                       AS Corrosion,
                    NVL (MAX (DECODE (Rep_Category, ''Fracture'', Repairs)), 0)
                       AS Fracture,
                    NVL (MAX (DECODE (Rep_Category, ''Failure'', Repairs)), 0)
                       AS Failure,
                    NVL (MAX (DECODE (Rep_Category, ''Interference'', Repairs)),
                         0)
                       AS Interference,
                    NVL (MAX (DECODE (Rep_Category, ''Other'', Repairs)), 0)
                       AS Other
               FROM (
                     SELECT   WO_ID AS WO, Rep_Category, COUNT (WO_ID) AS Repairs
                         FROM (

                               SELECT w.wonum WO_ID,
                                      CASE rr.xleakage_cause
                                         WHEN ''CO'' THEN ''Corrosion''
                                         WHEN ''EB'' THEN ''Corrosion''
                                         WHEN ''PH'' THEN ''Corrosion''
                                         WHEN ''SC'' THEN ''Corrosion''
                                         WHEN ''CR'' THEN ''Fracture''
                                         WHEN ''LG'' THEN ''Fracture''
                                         WHEN ''ST'' THEN ''Fracture''
                                         WHEN ''FA'' THEN ''Failure''
                                         WHEN ''IN'' THEN ''Interference''
                                         ELSE ''Other''
                                      END
                                         AS Rep_Category
                                 FROM maxrpd.workorder_mv w
                                 join maximo.xwocompletion rr
                                 on w.wonum = rr.xwonum
                                WHERE
                                       w.worktype = ''REPAIR''
                                      AND w.status = ''COMP''
                                      AND w.siteid = ''SCOTLAND''
                                      AND w.statusdate

                                      >=

                                             CASE
                                                WHEN trim(TO_CHAR (GETDATE(), ''DAY'')) = ''MONDAY''
                                                THEN
                                                   TO_CHAR (GETDATE() - 3,
                                                            ''DD-Mon-YYYY'')
                                                ELSE
                                                   TO_CHAR (GETDATE() - 1,
                                                            ''DD-Mon-YYYY'')
                                             END
                                      AND w.statusdate <
                                             TO_CHAR (GETDATE(), ''DD-Mon-YYYY'')
                                      AND rr.xigt <> 1
                                      AND rr.xigtcode IS NULL
                                      AND rr.xleakage_cause IS NOT NULL)
                     GROUP BY WO_ID, Rep_Category)
           GROUP BY WO) Rep_Cause
       ON Rep_Inc_GiP.Work_Order = REP_Cause.WO', is_active = 'Y'
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
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid141@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid141@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid141@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid149@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid149@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid149@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid143@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid143@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid143@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid146@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid146@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid146@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid140@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid140@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid140@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid144@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid144@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid144@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid6@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid6@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid44@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid44@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid44@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid21@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid21@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid21@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid16@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid16@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid16@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid83@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid83@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid83@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid95@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid95@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid95@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid151@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid151@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid151@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid116@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid116@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid116@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid68@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid68@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid68@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid139@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid139@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid152@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid152@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid152@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid73@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid73@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid73@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid147@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid147@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid147@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid76@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid76@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid76@company1.com' AND recipient_group = 'OPERATIONS';
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
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid11@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid11@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid11@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid145@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid145@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid145@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid150@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid150@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid150@company1.com' AND recipient_group = 'OPERATIONS';
IF NOT EXISTS (SELECT 1 FROM config.report_email WHERE report_id = @report_id AND email_address = 'emailid148@company1.com' AND recipient_group = 'OPERATIONS')
    INSERT INTO config.report_email (report_id, email_address, recipient_group, email_type, is_active)
    VALUES (@report_id, 'emailid148@company1.com', 'OPERATIONS', 'TO', 'N');
ELSE
    UPDATE config.report_email
    SET    is_active = 'N'
    WHERE  report_id = @report_id AND email_address = 'emailid148@company1.com' AND recipient_group = 'OPERATIONS';
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
WHERE  r.report_name = 'Daily_BIMIO_523';

SELECT rs.query_type, LEFT(rs.query_text, 100) AS query_preview
FROM   config.report_sql rs
JOIN   config.report r ON r.report_id = rs.report_id
WHERE  r.report_name = 'Daily_BIMIO_523';

SELECT r.report_name, re.recipient_group, re.email_type, re.email_address
FROM   config.report r
JOIN   config.report_email re ON re.report_id = r.report_id
WHERE  r.report_name = 'Daily_BIMIO_523'
ORDER  BY re.recipient_group, re.email_type, re.email_address;
