-- Step 1: Create schemas in Azure SQL
-- Run this first before creating tables

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'MAXRPD')
    EXEC('CREATE SCHEMA MAXRPD');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'abcbimart')
    EXEC('CREATE SCHEMA abcbimart');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'config')
    EXEC('CREATE SCHEMA config');
