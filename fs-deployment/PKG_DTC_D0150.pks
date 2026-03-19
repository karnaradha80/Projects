--------------------------------------------------------
--  DDL for Package PKG_DTC_D0150
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_D0150" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0150 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0150 flow files
--                (Non Half Hourly Meter Technical Details)
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  26/Nov/2024   Danie Selvaraju      Initial version
----------------------------------------------------------------------------------------------------

  -- Process D0150 file and insert into staging tables
  PROCEDURE PRC_PROCESS_FILE(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_success      OUT BOOLEAN,
    p_error_msg    OUT VARCHAR2
  );

  -- NEW: Process file with integrated validation (V2)
  PROCEDURE PRC_PROCESS_FILE_V2(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT PKG_DTC_VALIDATION.t_file_validation_result
  );

  -- Parse and insert group 288 (parent)
  FUNCTION FN_INSERT_GROUP_288(
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 289
  PROCEDURE PRC_INSERT_GROUP_289(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 290 (parent of 291, 293, 295, 296)
  FUNCTION FN_INSERT_GROUP_290(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 291
  PROCEDURE PRC_INSERT_GROUP_291(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 293
  PROCEDURE PRC_INSERT_GROUP_293(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 295
  PROCEDURE PRC_INSERT_GROUP_295(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 296
  PROCEDURE PRC_INSERT_GROUP_296(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 762
  PROCEDURE PRC_INSERT_GROUP_762(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 08A
  PROCEDURE PRC_INSERT_GROUP_08A(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

END PKG_DTC_D0150;
/