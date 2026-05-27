-- ============================================================
-- config schema DDL  (Tool 3 output -- run once per environment)
-- Idempotent: safe to re-run.
-- ============================================================

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'config')
    EXEC('CREATE SCHEMA [config]');
GO

-- ── config.report ─────────────────────────────────────────────
IF OBJECT_ID('config.report', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report]
    (
        [report_id]          INT          IDENTITY(1,1) NOT NULL,
        [report_name]        VARCHAR(200) NOT NULL,
        [pipeline_name]      VARCHAR(200) NOT NULL,
        [report_category]    VARCHAR(50)  NOT NULL CONSTRAINT [DF_report_category] DEFAULT 'CUSTOM',
        [description]        VARCHAR(500) NULL,
        [schedule_time]      VARCHAR(10)  NOT NULL CONSTRAINT [DF_report_schedule] DEFAULT '06:00',
        [output_container]   VARCHAR(100) NOT NULL,
        [template_container] VARCHAR(100) NULL,
        [template_name]      VARCHAR(500) NULL,
        [template_blob_path] VARCHAR(500) NULL,
        [display_name]       VARCHAR(300) NULL,
        [is_active]          CHAR(1)      NOT NULL CONSTRAINT [DF_report_active]   DEFAULT 'Y',
        CONSTRAINT [PK_report]      PRIMARY KEY ([report_id]),
        CONSTRAINT [UQ_report_name] UNIQUE      ([report_name])
    );
END
ELSE
BEGIN
    -- Add columns if upgrading from older schema version
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'template_name')
        ALTER TABLE [config].[report] ADD [template_name] VARCHAR(500) NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'template_blob_path')
        ALTER TABLE [config].[report] ADD [template_blob_path] VARCHAR(500) NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'template_container')
        ALTER TABLE [config].[report] ADD [template_container] VARCHAR(100) NULL;
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'report_category')
        ALTER TABLE [config].[report] ADD [report_category] VARCHAR(50) NOT NULL CONSTRAINT [DF_report_category] DEFAULT 'CUSTOM';
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('config.report') AND name = 'display_name')
        ALTER TABLE [config].[report] ADD [display_name] VARCHAR(300) NULL;
END
GO

-- ── config.report_email ───────────────────────────────────────
IF OBJECT_ID('config.report_email', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report_email]
    (
        [email_id]        INT          IDENTITY(1,1) NOT NULL,
        [report_id]       INT          NOT NULL,
        [email_address]   VARCHAR(200) NOT NULL,
        [recipient_group] VARCHAR(50)  NOT NULL,
        [email_type]      VARCHAR(10)  NOT NULL,
        [is_active]       CHAR(1)      NOT NULL CONSTRAINT [DF_report_email_active] DEFAULT 'Y',
        CONSTRAINT [PK_report_email] PRIMARY KEY ([email_id]),
        CONSTRAINT [FK_report_email_report]
            FOREIGN KEY ([report_id]) REFERENCES [config].[report] ([report_id])
    );
END
GO

-- ── config.report_sql ────────────────────────────────────────
IF OBJECT_ID('config.report_sql', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[report_sql]
    (
        [sql_id]       INT           IDENTITY(1,1) NOT NULL,
        [report_id]    INT           NOT NULL,
        [query_type]   VARCHAR(50)   NOT NULL,   -- ODS_CHECK | REPORT_MAIN
        [query_text]   NVARCHAR(MAX) NOT NULL,
        [is_active]    CHAR(1)       NOT NULL CONSTRAINT [DF_report_sql_active] DEFAULT 'Y',
        CONSTRAINT [PK_report_sql] PRIMARY KEY ([sql_id]),
        CONSTRAINT [UQ_report_sql_type]
            UNIQUE ([report_id], [query_type]),
        CONSTRAINT [FK_report_sql_report]
            FOREIGN KEY ([report_id]) REFERENCES [config].[report] ([report_id])
    );
END
GO

-- ── config.Report_Process_History ────────────────────────────
-- Tracks every execution of the Excel writer Azure Function.
-- Status lifecycle: InProgress -> Success | Failed
IF OBJECT_ID('config.Report_Process_History', 'U') IS NULL
BEGIN
    CREATE TABLE [config].[Report_Process_History]
    (
        [History_id]            INT          IDENTITY(1,1) NOT NULL,
        [Report_id]             INT          NOT NULL,
        [Report_Run_Datetime]   DATETIME2    NOT NULL
            CONSTRAINT [DF_rph_run_dt]      DEFAULT GETUTCDATE(),
        [Report_Process_Status] VARCHAR(20)  NOT NULL
            CONSTRAINT [DF_rph_status]      DEFAULT 'InProgress',
        [Created_Datetime]      DATETIME2    NOT NULL
            CONSTRAINT [DF_rph_created_dt]  DEFAULT GETUTCDATE(),
        CONSTRAINT [PK_Report_Process_History]
            PRIMARY KEY ([History_id]),
        CONSTRAINT [CK_rph_status]
            CHECK ([Report_Process_Status] IN ('InProgress', 'Success', 'Failed')),
        CONSTRAINT [FK_Report_Process_History_report]
            FOREIGN KEY ([Report_id]) REFERENCES [config].[report] ([report_id])
    );
END
GO
