-- Dimension table: Addresses
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.dim_addresses (
    id              BIGINT          NOT NULL PRIMARY KEY,
    display_address VARCHAR(500)    NOT NULL    -- Full formatted address of the incident
);
