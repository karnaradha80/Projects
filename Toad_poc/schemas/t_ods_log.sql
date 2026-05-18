-- ODS refresh log table (Oracle)
-- Source: MAXRPD schema (Oracle)
-- Used to check if today's data load has completed before running the report

CREATE TABLE MAXRPD.T_ODS_LOG (
    id      NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ems     TIMESTAMP       NOT NULL    -- Timestamp of the ODS data load event
);
