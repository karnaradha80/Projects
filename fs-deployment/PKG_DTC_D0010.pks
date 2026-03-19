--------------------------------------------------------
--  DDL for Package PKG_DTC_D0010
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_D0010" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0010 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0010 flow files
--                (Meter Readings)
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Jan/2026   Danie Selvaraju      Initial version
----------------------------------------------------------------------------------------------------

  -- NEW: Process D0010 file with integrated validation (V2)
  -- This validates first, then only loads valid parent groups
  PROCEDURE PRC_PROCESS_FILE_V2(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT PKG_DTC_VALIDATION.t_file_validation_result
  );

  -- Process D0010 file and insert into staging tables (legacy - no validation)
  PROCEDURE PRC_PROCESS_FILE(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_success      OUT BOOLEAN,
    p_error_msg    OUT VARCHAR2
  );

  -- Parse and insert group 026 (parent)
  FUNCTION FN_INSERT_GROUP_026(
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 027
  PROCEDURE PRC_INSERT_GROUP_027(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 028 (parent of 029, 030)
  FUNCTION FN_INSERT_GROUP_028(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 029
  PROCEDURE PRC_INSERT_GROUP_029(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 030 (parent of 032, 033)
  FUNCTION FN_INSERT_GROUP_030(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 032
  PROCEDURE PRC_INSERT_GROUP_032(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 033
  PROCEDURE PRC_INSERT_GROUP_033(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

END PKG_DTC_D0010;
/