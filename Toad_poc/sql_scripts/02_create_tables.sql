-- Step 2: Create all tables in Azure SQL
-- Translated from Oracle/Redshift schemas to T-SQL

-- ODS refresh log (simulates Oracle MAXRPD.T_ODS_LOG)
IF OBJECT_ID('MAXRPD.T_ODS_LOG', 'U') IS NOT NULL DROP TABLE MAXRPD.T_ODS_LOG;
CREATE TABLE MAXRPD.T_ODS_LOG (
    id   INT           IDENTITY(1,1) PRIMARY KEY,
    ems  DATETIME2     NOT NULL
);

-- Fact table: gas escape incidents
IF OBJECT_ID('abcbimart.fct_gas_escapes_v', 'U') IS NOT NULL DROP TABLE abcbimart.fct_gas_escapes_v;
CREATE TABLE abcbimart.fct_gas_escapes_v (
    id                          BIGINT   NOT NULL PRIMARY KEY,
    dwor_id_root                BIGINT   NOT NULL,
    dwor_id_gas_prevented       BIGINT   NOT NULL,
    dorg_id_root                BIGINT   NOT NULL,
    dadr_id_root                BIGINT   NOT NULL,
    dcal_id_gas_prevented_date  BIGINT   NOT NULL,
    dtim_id_gas_prevented_time  BIGINT   NOT NULL,
    latest                      CHAR(1)  NOT NULL
);

-- Dimension: work orders
IF OBJECT_ID('abcbimart.dim_work_orders', 'U') IS NOT NULL DROP TABLE abcbimart.dim_work_orders;
CREATE TABLE abcbimart.dim_work_orders (
    id                  BIGINT        NOT NULL PRIMARY KEY,
    work_order_number   VARCHAR(50)   NOT NULL,
    reported_date_time  DATETIME2     NOT NULL
);

-- Dimension: organisation
IF OBJECT_ID('abcbimart.dim_organisation', 'U') IS NOT NULL DROP TABLE abcbimart.dim_organisation;
CREATE TABLE abcbimart.dim_organisation (
    id                  BIGINT        NOT NULL PRIMARY KEY,
    network             VARCHAR(100)  NOT NULL,
    ldz                 VARCHAR(50)   NOT NULL,
    depot_work_group    VARCHAR(100)  NOT NULL
);

-- Dimension: addresses
IF OBJECT_ID('abcbimart.dim_addresses', 'U') IS NOT NULL DROP TABLE abcbimart.dim_addresses;
CREATE TABLE abcbimart.dim_addresses (
    id               BIGINT        NOT NULL PRIMARY KEY,
    display_address  VARCHAR(500)  NOT NULL
);

-- Dimension: calendar
IF OBJECT_ID('abcbimart.dim_calendar', 'U') IS NOT NULL DROP TABLE abcbimart.dim_calendar;
CREATE TABLE abcbimart.dim_calendar (
    id            BIGINT       NOT NULL PRIMARY KEY,
    date_disp_1   VARCHAR(20)  NOT NULL,
    date_oracle   DATE         NOT NULL
);

-- Dimension: time
IF OBJECT_ID('abcbimart.dim_time', 'U') IS NOT NULL DROP TABLE abcbimart.dim_time;
CREATE TABLE abcbimart.dim_time (
    id               BIGINT       NOT NULL PRIMARY KEY,
    hour_24_minute   VARCHAR(20)  NOT NULL
);

-- ── Config Tables ──────────────────────────────────────────────────────────────

-- Config: report metadata (one row per report)
IF OBJECT_ID('config.report_email', 'U') IS NOT NULL DROP TABLE config.report_email;
IF OBJECT_ID('config.report',       'U') IS NOT NULL DROP TABLE config.report;

CREATE TABLE config.report (
    report_id       INT           IDENTITY(1,1) PRIMARY KEY,
    report_name     VARCHAR(100)  NOT NULL UNIQUE,
    description     VARCHAR(500)  NULL,
    schedule        VARCHAR(50)   NOT NULL,          -- Daily, Weekly, Monthly
    output_format   VARCHAR(20)   NOT NULL DEFAULT 'CSV',
    is_active       CHAR(1)       NOT NULL DEFAULT 'Y',
    created_date    DATETIME2     NOT NULL DEFAULT GETDATE(),
    modified_date   DATETIME2     NOT NULL DEFAULT GETDATE()
);

-- Config: email distribution list (many rows per report)
CREATE TABLE config.report_email (
    id               INT           IDENTITY(1,1) PRIMARY KEY,
    report_id        INT           NOT NULL REFERENCES config.report(report_id),
    email_address    VARCHAR(200)  NOT NULL,
    email_type       VARCHAR(5)    NOT NULL CHECK (email_type IN ('TO', 'CC', 'BCC')),
    recipient_group  VARCHAR(50)   NOT NULL,         -- OPERATIONS, BI_TEAM, ALERT_ONLY
    is_active        CHAR(1)       NOT NULL DEFAULT 'Y',
    created_date     DATETIME2     NOT NULL DEFAULT GETDATE()
);
