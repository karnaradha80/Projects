--------------------------------------------------------
--  Seed Data - MAVIS DTC Staging
--  Run as: MDQA_OWNER user
--------------------------------------------------------

SET SERVEROUTPUT ON

-- ============================================
-- MDQ_APP_NTWKAREA_REF - Network Area Reference Data
-- ============================================

INSERT INTO MDQ_APP_NTWKAREA_REF (
    NTA_MPAN_CD, NTA_TERM, NTA_SHORT_TERM, NTA_NC1_BASE_DIR,
    NTA_EDF_REG_ADDR1, NTA_EDF_REG_ADDR2, NTA_EDF_REG_ADDR3, NTA_EDF_REG_ADDR4,
    NTA_EDF_REG_ADDR5, NTA_EDF_REG_ADDR6, NTA_EDF_REG_ADDR7, NTA_EDF_REG_ADDR8,
    NTA_EDF_REG_ADDR9, NTA_EDF_REG_PCODE, NTA_EDF_REG_CO_NO, NTA_EDF_REG_CO_NAME
) VALUES (
    '19', 'SEEB', 'SPN', '/MAVISNC1/SPN NC1 Forms',
    NULL, NULL, NULL, NULL,
    'Newington House', NULL, '237 Southwark Bridge Road', 'London',
    NULL, 'SE1 6NP', '03043097', 'South Eastern Power Networks plc'
);

INSERT INTO MDQ_APP_NTWKAREA_REF (
    NTA_MPAN_CD, NTA_TERM, NTA_SHORT_TERM, NTA_NC1_BASE_DIR,
    NTA_EDF_REG_ADDR1, NTA_EDF_REG_ADDR2, NTA_EDF_REG_ADDR3, NTA_EDF_REG_ADDR4,
    NTA_EDF_REG_ADDR5, NTA_EDF_REG_ADDR6, NTA_EDF_REG_ADDR7, NTA_EDF_REG_ADDR8,
    NTA_EDF_REG_ADDR9, NTA_EDF_REG_PCODE, NTA_EDF_REG_CO_NO, NTA_EDF_REG_CO_NAME
) VALUES (
    '28', 'EDFI', 'IDN', '/MAVISNC1/IDN NC1 Forms',
    NULL, NULL, NULL, NULL,
    'Newington House', NULL, '237 Southwark Bridge Road', 'London',
    NULL, 'SE1 6NP', '06489447', 'UK Power Networks (IDNO) Ltd'
);

INSERT INTO MDQ_APP_NTWKAREA_REF (
    NTA_MPAN_CD, NTA_TERM, NTA_SHORT_TERM, NTA_NC1_BASE_DIR,
    NTA_EDF_REG_ADDR1, NTA_EDF_REG_ADDR2, NTA_EDF_REG_ADDR3, NTA_EDF_REG_ADDR4,
    NTA_EDF_REG_ADDR5, NTA_EDF_REG_ADDR6, NTA_EDF_REG_ADDR7, NTA_EDF_REG_ADDR8,
    NTA_EDF_REG_ADDR9, NTA_EDF_REG_PCODE, NTA_EDF_REG_CO_NO, NTA_EDF_REG_CO_NAME
) VALUES (
    '10', 'EELC', 'EPN', '/MAVISNC1/EPN NC1 Forms',
    NULL, NULL, NULL, NULL,
    'Newington House', NULL, '237 Southwark Bridge Road', 'London',
    NULL, 'SE1 6NP', '02366906', 'Eastern Power Networks plc'
);

INSERT INTO MDQ_APP_NTWKAREA_REF (
    NTA_MPAN_CD, NTA_TERM, NTA_SHORT_TERM, NTA_NC1_BASE_DIR,
    NTA_EDF_REG_ADDR1, NTA_EDF_REG_ADDR2, NTA_EDF_REG_ADDR3, NTA_EDF_REG_ADDR4,
    NTA_EDF_REG_ADDR5, NTA_EDF_REG_ADDR6, NTA_EDF_REG_ADDR7, NTA_EDF_REG_ADDR8,
    NTA_EDF_REG_ADDR9, NTA_EDF_REG_PCODE, NTA_EDF_REG_CO_NO, NTA_EDF_REG_CO_NAME
) VALUES (
    '12', 'LOND', 'LPN', '/MAVISNC1/LPN NC1 Forms',
    NULL, NULL, NULL, NULL,
    'Newington House', NULL, '237 Southwark Bridge Road', 'London',
    NULL, 'SE1 6NP', '03929195', 'London Power Networks plc'
);

-- ============================================
-- MDQ_APP_MSG_REF - Error Messages
-- ============================================

-- Validation error messages
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8001', 'Error inserting group @1: @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8002', 'Error processing @1 flow: @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8003', 'No active validation configuration found for flow type @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8004', 'File must have at least header, one data line and footer', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8005', 'Critical processing error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8006', 'Group @1 validation failed', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8007', 'Invalid header identifier.expected @1, but got @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8008', 'Invalid footer identifier.expected @1, but got @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8009', 'Header validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8010', 'Footer validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8011', 'Error parsing Header: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8012', 'Error parsing Footer: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8013', 'Header field @1 is mandatory but is not populated', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8014', 'Field @1 length @2 is less than minimum @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8015', 'Field @1 length @2 exceeds maximum @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8016', 'Field @1 value @2 is not a valid number', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8017', 'Field @1 has @2 decimal places but scale is @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8018', 'Field @1 total digits @2 exceed precision @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8019', 'Field @1 integer digits @2 exceed allowed @3 (precision @4 - scale @5)', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8020', 'Field @1 value @2 is not a valid date in format @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8021', 'Field @1 value @2 does not match pattern @3', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8022', 'Field @1 validation error: @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8023', 'Invalid header timestamp format: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8024', 'Expected @1 but footer shows @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8025', 'Invalid record count value: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8026', 'Invalid footer record count: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8027', 'Unknown group ID: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8028', 'Group @1 validation error: @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8029', 'No parent group @1 found in file', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8030', 'Group @1 occurrences @2 below minimum @3 for parent @4', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8031', 'Group @1 occurrences @2 exceed maximum @3 for parent @4', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8032', 'Occurrence validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8033', 'Found @1 parent groups but footer shows @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8034', 'Invalid flow count value: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8035', 'File identifier mismatch between header @1 and footer @2', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8036', 'File content is empty', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8037', 'File validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8038', 'Validation exception: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8039', 'Stage 1 validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8040', 'Stage 2 validation error: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8041', 'Unknown flow type: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8042', 'Unsupported flow type: @1', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8043', 'Footer field @1 is mandatory but is not populated', 'E');
INSERT INTO MDQ_APP_MSG_REF (MSG_PK, MSG_TEXT, MSG_TYPE) VALUES ('ERR8044', 'Field @1 is mandatory but is not populated', 'E');

COMMIT;

DBMS_OUTPUT.PUT_LINE('Network area reference data and error messages inserted successfully.');
/
