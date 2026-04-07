--------------------------------------------------------
--  Staging Table NOLOGGING Update — MAVIS DTC Staging
--  Run as: MDQA_OWNER user (or DBA)
--
--  Purpose: Set NOLOGGING on all staging tables so that
--           INSERT /*+ APPEND_VALUES */ (direct-path) inserts
--           suppress redo generation, eliminating the main
--           remaining INSERT overhead.
--
--  Safe to run on live databases — takes effect immediately.
--  Trade-off: staged data is not media-recoverable after a
--  crash without a backup taken after the load. For staging
--  tables that can be reloaded from source files this is
--  acceptable (same trade-off as any ETL staging layer).
--------------------------------------------------------

-- D0010 staging tables
ALTER TABLE STAGE_D0010_026 NOLOGGING;
ALTER TABLE STAGE_D0010_027 NOLOGGING;
ALTER TABLE STAGE_D0010_028 NOLOGGING;
ALTER TABLE STAGE_D0010_029 NOLOGGING;
ALTER TABLE STAGE_D0010_030 NOLOGGING;
ALTER TABLE STAGE_D0010_032 NOLOGGING;
ALTER TABLE STAGE_D0010_033 NOLOGGING;

-- D0150 staging tables
ALTER TABLE STAGE_D0150_288 NOLOGGING;
ALTER TABLE STAGE_D0150_289 NOLOGGING;
ALTER TABLE STAGE_D0150_290 NOLOGGING;
ALTER TABLE STAGE_D0150_291 NOLOGGING;
ALTER TABLE STAGE_D0150_293 NOLOGGING;
ALTER TABLE STAGE_D0150_295 NOLOGGING;
ALTER TABLE STAGE_D0150_296 NOLOGGING;
ALTER TABLE STAGE_D0150_762 NOLOGGING;
ALTER TABLE STAGE_D0150_08A NOLOGGING;

-- Verify
SELECT table_name, logging
FROM user_tables
WHERE table_name IN (
    'STAGE_D0010_026','STAGE_D0010_027','STAGE_D0010_028',
    'STAGE_D0010_029','STAGE_D0010_030','STAGE_D0010_032','STAGE_D0010_033',
    'STAGE_D0150_288','STAGE_D0150_289','STAGE_D0150_290',
    'STAGE_D0150_291','STAGE_D0150_293','STAGE_D0150_295',
    'STAGE_D0150_296','STAGE_D0150_762','STAGE_D0150_08A'
)
ORDER BY table_name;
