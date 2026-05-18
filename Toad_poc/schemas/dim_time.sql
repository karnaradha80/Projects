-- Dimension table: Time
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.dim_time (
    id                  BIGINT          NOT NULL PRIMARY KEY,
    hour_24_minute      VARCHAR(20)     NOT NULL    -- Time in 'HH:MM:SS' format (right 8 chars used)
);
