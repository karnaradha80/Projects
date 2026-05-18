-- Step 4: Verify data loaded correctly and test report query

-- Row count checks
SELECT 'T_ODS_LOG'           AS table_name, COUNT(*) AS row_count FROM MAXRPD.T_ODS_LOG
UNION ALL
SELECT 'fct_gas_escapes_v',  COUNT(*) FROM abcbimart.fct_gas_escapes_v
UNION ALL
SELECT 'dim_work_orders',    COUNT(*) FROM abcbimart.dim_work_orders
UNION ALL
SELECT 'dim_organisation',   COUNT(*) FROM abcbimart.dim_organisation
UNION ALL
SELECT 'dim_addresses',      COUNT(*) FROM abcbimart.dim_addresses
UNION ALL
SELECT 'dim_calendar',       COUNT(*) FROM abcbimart.dim_calendar
UNION ALL
SELECT 'dim_time',           COUNT(*) FROM abcbimart.dim_time;

-- ODS refresh check (simulates ADF Lookup_ODS_Refresh_Check)
SELECT COUNT(*) AS row_count
FROM MAXRPD.T_ODS_LOG
WHERE CAST(ems AS DATE) = CAST(GETDATE() AS DATE);

-- Full report query (simulates ADF Copy_ReportData_To_Blob)
SELECT
    sub.[Network], sub.[LDZ], sub.[Depot],
    sub.[Work Order], sub.[Root Work Order],
    sub.[Emergency Date], sub.[Gas Prevented],
    sub.[Time Difference], sub.[Address],
    CASE WHEN sub.[Gas Prevented] > DATEFROMPARTS(YEAR(DATEADD(DAY,-1,GETDATE())), MONTH(DATEADD(DAY,-1,GETDATE())), 1) THEN 1 ELSE 0 END AS [MTD],
    CASE WHEN sub.[Time Difference] <= 12 THEN 1 ELSE 0 END AS [Less 12],
    CASE WHEN sub.[Time Difference] >  12 THEN 1 ELSE 0 END AS [Great 12],
    1 AS [Count]
FROM (
    SELECT
        dorg.network                                                                AS [Network],
        dorg.ldz                                                                    AS [LDZ],
        CASE WHEN dorg.depot_work_group = 'DEPOT_K' THEN 'DEPOT_L'
             ELSE dorg.depot_work_group END                                         AS [Depot],
        prev_dwor.work_order_number                                                 AS [Work Order],
        dwor.work_order_number                                                      AS [Root Work Order],
        dwor.reported_date_time                                                     AS [Emergency Date],
        DATEADD(SECOND,
            DATEDIFF(SECOND, '00:00:00', CAST(RIGHT(dtim.hour_24_minute, 8) AS TIME)),
            CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATETIME2)
        )                                                                           AS [Gas Prevented],
        ROUND(
            CAST(DATEDIFF(MINUTE,
                dwor.reported_date_time,
                DATEADD(SECOND,
                    DATEDIFF(SECOND, '00:00:00', CAST(RIGHT(dtim.hour_24_minute, 8) AS TIME)),
                    CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATETIME2)
                )
            ) AS FLOAT) / 60, 2
        )                                                                           AS [Time Difference],
        dadr.display_address                                                        AS [Address]
    FROM abcbimart.fct_gas_escapes_v ge
        JOIN abcbimart.dim_work_orders  dwor      ON ge.dwor_id_root               = dwor.id
        JOIN abcbimart.dim_work_orders  prev_dwor ON ge.dwor_id_gas_prevented      = prev_dwor.id
        JOIN abcbimart.dim_organisation dorg      ON ge.dorg_id_root               = dorg.id
        JOIN abcbimart.dim_addresses    dadr      ON ge.dadr_id_root               = dadr.id
        JOIN abcbimart.dim_calendar     dcal      ON ge.dcal_id_gas_prevented_date = dcal.id
        JOIN abcbimart.dim_time         dtim      ON ge.dtim_id_gas_prevented_time = dtim.id
    WHERE ge.latest = 'Y'
      AND dcal.date_oracle >= DATEADD(MONTH, 3,
                                  DATEFROMPARTS(
                                      YEAR(DATEADD(MONTH, -3, DATEADD(DAY, -4, GETDATE()))),
                                  1, 1))
      AND dcal.date_oracle < CAST(GETDATE() AS DATE)
) sub;
