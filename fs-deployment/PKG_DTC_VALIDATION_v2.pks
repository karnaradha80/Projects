--------------------------------------------------------
--  DDL for Package PKG_DTC_VALIDATION (Version 2)
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_VALIDATION" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : Generic DTC Flow Validation Package with Two-Stage Validation
--
--  NOTES       : This package provides generic validation logic for any DTC flow
--                using JSON-based configuration stored in MDQ_ETL_VALIDATION_CONFIG
--
--  Two-Stage Validation:
--    Stage 1: File-level validation (header, footer, record count, parent group existence)
--             If fails -> File is REJECTED
--    Stage 2: Group-level validation (each group and children)
--             If fails -> Groups are rejected, but other groups can be staged
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  26/Nov/2024   Danie Selvaraju      Initial version
--  27/Nov/2024   Danie Selvaraju      Added two-stage validation
--  05/Mar/2026   Radha                Added p_field_position param to ADD_ERROR
--                                     for ERR_FILE_COL 'name - position' format
----------------------------------------------------------------------------------------------------

  -- Type definitions
  TYPE t_validation_error IS RECORD (
    error_code    VARCHAR2(50),
    error_message VARCHAR2(4000),
    line_number   NUMBER,
    field_name    VARCHAR2(100),
    field_value   VARCHAR2(4000),  -- The actual value from the file that failed validation
    group_id      VARCHAR2(10)     -- Added to track which group has error
  );

  TYPE t_validation_errors IS TABLE OF t_validation_error;

  -- Header data extracted from ZHV line
  TYPE t_header_data IS RECORD (
    file_identifier   VARCHAR2(40),   -- Field 2
    flow_name         VARCHAR2(10),   -- Field 3 (e.g., D0150001)
    flow_type         VARCHAR2(10),   -- Derived from flow_name
    flow_version      VARCHAR2(3),    -- Derived from flow_name
    src_mp_role       VARCHAR2(1),    -- Field 5
    src_mp_id         VARCHAR2(4),    -- Field 6
    dstn_mp_role      VARCHAR2(1),    -- Field 7
    dstn_mp_id        VARCHAR2(4),    -- Field 8
    data_timestamp    VARCHAR2(14),   -- Field 9 (YYYYMMDDHH24MISS)
    data_dt           DATE,           -- Converted from data_timestamp
    network_id        VARCHAR2(10),   -- Field 12 (e.g., TEST, TR01, OPER)
    inp_out_ind       VARCHAR2(2)     -- Field 10 (optional)
  );

  -- Footer data extracted from ZPT line (6 fields total)
  -- ZPT|file_id|rec_count|checksum|flow_count|timestamp
  TYPE t_footer_data IS RECORD (
    file_identifier   VARCHAR2(40),   -- Field 2
    record_count      NUMBER,         -- Field 3
    checksum          VARCHAR2(20),   -- Field 4 (optional)
    flow_count        NUMBER,         -- Field 5
    data_timestamp    VARCHAR2(14)    -- Field 6
  );

  -- Parent group line range (for tracking which lines belong to which parent group)
  TYPE t_parent_group_range IS RECORD (
    parent_group_id    VARCHAR2(10),    -- Group ID (e.g., '026', '500')
    start_line         NUMBER,          -- First line of this parent group
    end_line           NUMBER,          -- Last line of this parent group (inclusive)
    is_valid           BOOLEAN          -- TRUE if valid, FALSE if rejected
  );

  TYPE t_parent_group_ranges IS TABLE OF t_parent_group_range;

  -- Validation result with all statistics
  TYPE t_file_validation_result IS RECORD (
    -- Overall status
    status                VARCHAR2(20),           -- REJECTED or STAGING
    stage1_passed         BOOLEAN,                -- Did Stage 1 pass?

    -- Parsed header/footer data
    header_data           t_header_data,
    footer_data           t_footer_data,

    -- Counts from file analysis
    total_rec_count       NUMBER,                 -- All data lines
    total_flow_count      NUMBER,                 -- Parent groups in file

    -- Staging statistics (successfully processed)
    staged_rec_count      NUMBER,                 -- Data lines staged
    staged_flow_count     NUMBER,                 -- Parent groups staged

    -- Error statistics (validation errors)
    error_rec_count       NUMBER,                 -- Data lines with errors
    error_flow_count      NUMBER,                 -- Parent groups with errors

    -- Rejection statistics (failed validation)
    rejected_rec_count    NUMBER,                 -- Data lines rejected
    rejected_flow_count   NUMBER,                 -- Parent groups rejected

    -- Error details
    errors                t_validation_errors,

    -- Parent group ranges (NEW - for selective data loading)
    parent_groups         t_parent_group_ranges   -- Line ranges for each parent group
  );

  -- Public function to get active validation config for a flow type
  FUNCTION FN_GET_ACTIVE_CONFIG(
    p_flow_type IN VARCHAR2
  ) RETURN CLOB;

  -- NEW: Two-stage validation - Main entry point
  FUNCTION FN_VALIDATE_FILE_V2(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT t_file_validation_result
  ) RETURN BOOLEAN;

  -- NEW: Parse header and extract all fields
  FUNCTION FN_PARSE_HEADER(
    p_header_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_header_data  OUT t_header_data,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN;

  -- NEW: Parse footer and extract all fields
  FUNCTION FN_PARSE_FOOTER(
    p_footer_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_footer_data  OUT t_footer_data,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN;

  -- NEW: Stage 1 validation (file-level - critical)
  FUNCTION FN_VALIDATE_STAGE1(
    p_lines           IN DBMS_SQL.VARCHAR2A,
    p_config_json     IN CLOB,
    p_flow_type       IN VARCHAR2,
    p_header_data     OUT t_header_data,
    p_footer_data     OUT t_footer_data,
    p_total_rec_count OUT NUMBER,
    p_total_flow_count OUT NUMBER,
    p_errors          OUT t_validation_errors
  ) RETURN BOOLEAN;

  -- NEW: Stage 2 validation (group-level - partial rejection allowed)
  FUNCTION FN_VALIDATE_STAGE2(
    p_lines               IN DBMS_SQL.VARCHAR2A,
    p_config_json         IN CLOB,
    p_flow_type           IN VARCHAR2,
    p_staged_rec_count    OUT NUMBER,
    p_staged_flow_count   OUT NUMBER,
    p_rejected_rec_count  OUT NUMBER,
    p_rejected_flow_count OUT NUMBER,
    p_parent_groups       OUT t_parent_group_ranges,
    p_errors              OUT t_validation_errors
  ) RETURN BOOLEAN;

  -- Existing functions (kept for backward compatibility)
  FUNCTION FN_VALIDATE_FILE(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN;

  FUNCTION FN_VALIDATE_HEADER(
    p_header_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN;

  FUNCTION FN_VALIDATE_FOOTER(
    p_footer_line      IN VARCHAR2,
    p_config_json      IN CLOB,
    p_expected_count   IN NUMBER,
    p_errors           OUT t_validation_errors
  ) RETURN BOOLEAN;

  FUNCTION FN_VALIDATE_FIELD(
    p_field_value  IN VARCHAR2,
    p_field_config IN JSON_OBJECT_T,
    p_field_name   OUT VARCHAR2,
    p_error_msg    OUT VARCHAR2
  ) RETURN BOOLEAN;

  FUNCTION FN_SPLIT_FILE_LINES(
    p_file_content IN CLOB
  ) RETURN DBMS_SQL.VARCHAR2A;

  FUNCTION FN_GET_GROUP_ID(
    p_line IN VARCHAR2
  ) RETURN VARCHAR2;

  FUNCTION FN_VALIDATE_GROUP_LINE(
    p_line         IN VARCHAR2,
    p_group_id     IN VARCHAR2,
    p_config_json  IN CLOB,
    p_line_number  IN NUMBER,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN;

  -- NEW: Helper function to check if a line belongs to a valid parent group
  FUNCTION FN_IS_LINE_IN_VALID_GROUP(
    p_line_number     IN NUMBER,
    p_parent_groups   IN t_parent_group_ranges
  ) RETURN BOOLEAN;

  -- NEW: Helper function to get parent group info for a line
  FUNCTION FN_GET_PARENT_GROUP_INFO(
    p_line_number     IN NUMBER,
    p_parent_groups   IN t_parent_group_ranges,
    p_parent_group_id OUT VARCHAR2,
    p_is_valid        OUT BOOLEAN
  ) RETURN BOOLEAN;

  -- Helper: Add error to collection (made public for use by flow packages)
  PROCEDURE ADD_ERROR(
    p_errors       IN OUT t_validation_errors,
    p_error_code   IN VARCHAR2,
    p_error_msg    IN VARCHAR2,
    p_line_number  IN NUMBER DEFAULT NULL,
    p_field_name   IN VARCHAR2 DEFAULT NULL,
    p_field_value  IN VARCHAR2 DEFAULT NULL,
    p_group_id     IN VARCHAR2 DEFAULT NULL,
    p_field_position IN NUMBER DEFAULT NULL
  );

END PKG_DTC_VALIDATION;
/