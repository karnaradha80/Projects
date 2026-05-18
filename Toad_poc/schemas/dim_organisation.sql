-- Dimension table: Organisation / Operational Areas
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.dim_organisation (
    id                  BIGINT          NOT NULL PRIMARY KEY,
    network             VARCHAR(100)    NOT NULL,   -- Gas network name
    ldz                 VARCHAR(50)     NOT NULL,   -- Local Distribution Zone
    depot_work_group    VARCHAR(100)    NOT NULL    -- Depot name (HILLINGTON mapped to PAISLEY)
);
