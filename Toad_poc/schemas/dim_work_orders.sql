-- Dimension table: Work Orders
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.dim_work_orders (
    id                  BIGINT          NOT NULL PRIMARY KEY,
    work_order_number   VARCHAR(50)     NOT NULL,   -- Work order reference number
    reported_date_time  TIMESTAMP       NOT NULL    -- Date and time the emergency was reported
);
