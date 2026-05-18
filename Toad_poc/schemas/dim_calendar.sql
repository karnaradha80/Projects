-- Dimension table: Calendar
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.dim_calendar (
    id              BIGINT          NOT NULL PRIMARY KEY,
    date_disp_1     VARCHAR(20)     NOT NULL,   -- Date in display format 'dd/mm/yyyy'
    date_oracle     DATE            NOT NULL    -- Date in Oracle/standard DATE format for filtering
);
