-- Fact table / view: Gas Escape incidents
-- Source: abcbimart schema (Redshift)

CREATE TABLE abcbimart.fct_gas_escapes_v (
    id                          BIGINT          NOT NULL,
    dwor_id_root                BIGINT          NOT NULL,   -- FK to dim_work_orders (root work order)
    dwor_id_gas_prevented       BIGINT          NOT NULL,   -- FK to dim_work_orders (gas prevented work order)
    dorg_id_root                BIGINT          NOT NULL,   -- FK to dim_organisation
    dadr_id_root                BIGINT          NOT NULL,   -- FK to dim_addresses
    dcal_id_gas_prevented_date  BIGINT          NOT NULL,   -- FK to dim_calendar (gas prevented date)
    dtim_id_gas_prevented_time  BIGINT          NOT NULL,   -- FK to dim_time (gas prevented time)
    latest                      CHAR(1)         NOT NULL    -- 'Y' = latest record, 'N' = superseded
);
