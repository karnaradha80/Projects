--------------------------------------------------------
--  Master Deployment Script - MAVIS DTC Staging
--
--  INSTRUCTIONS:
--  1. Start the Oracle container: docker-compose up -d
--  2. Wait for the database to be ready (check with docker logs -f mavis-oracle-xe)
--  3. Connect to the database as MDQA_OWNER:
--     sqlplus MDQA_OWNER/Mdq@_0wn3r#2026!@localhost:1521/XEPDB1
--  4. Run this script: @run_deployment.sql
--------------------------------------------------------

SET ECHO ON
SET SERVEROUTPUT ON
SPOOL deployment_log.txt

PROMPT ========================================
PROMPT MAVIS DTC Staging - Database Deployment
PROMPT ========================================
PROMPT

PROMPT Step 1: Creating Tables...
@@01_create_tables.sql
PROMPT Tables created successfully.
PROMPT

PROMPT Step 2: Creating Sequences...
@@02_create_sequences.sql
PROMPT Sequences created successfully.
PROMPT

PROMPT Step 3: Inserting Seed Data (Network Refs & Error Messages)...
@@04_seed_data.sql
PROMPT Seed data inserted successfully.
PROMPT

PROMPT Step 4: Creating Packages...
@@03_create_packages.sql
PROMPT Packages created successfully.
PROMPT

PROMPT Step 5: Inserting Validation Configurations...
@@05_insert_validation_configs.sql
PROMPT Validation configurations inserted successfully.
PROMPT

PROMPT ========================================
PROMPT Deployment Summary
PROMPT ========================================

PROMPT
PROMPT Tables:
SELECT table_name FROM user_tables ORDER BY table_name;

PROMPT
PROMPT Sequences:
SELECT sequence_name FROM user_sequences ORDER BY sequence_name;

PROMPT
PROMPT Packages:
SELECT object_name, object_type, status FROM user_objects
WHERE object_type IN ('PACKAGE', 'PACKAGE BODY') ORDER BY object_name, object_type;

PROMPT
PROMPT Validation Configs:
SELECT MEVC_FLOW_TYPE, MEVC_CONFIG_VERSION, MEVC_ACTIVE_YN FROM MDQ_ETL_VALIDATION_CONFIG;

PROMPT
PROMPT Network Areas:
SELECT NTA_MPAN_CD, NTA_TERM, NTA_SHORT_TERM FROM MDQ_APP_NTWKAREA_REF;

PROMPT
PROMPT ========================================
PROMPT Deployment Complete!
PROMPT ========================================

SPOOL OFF
