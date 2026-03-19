--------------------------------------------------------
--  DDL for Package PKG_DTC_D0302
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_D0302" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0302 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0302 flow files
--                (Customer and Supplier Customer Details)
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  26/Nov/2024   Danie Selvaraju      Initial version
----------------------------------------------------------------------------------------------------

  -- Process D0302 file and insert into staging tables
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

  -- Parse and insert group 68C (parent)
  FUNCTION FN_INSERT_GROUP_68C(
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 69C
  PROCEDURE PRC_INSERT_GROUP_69C(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 70C
  PROCEDURE PRC_INSERT_GROUP_70C(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 15J (parent of 16J and 17J)
  FUNCTION FN_INSERT_GROUP_15J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER;

  -- Parse and insert group 16J
  PROCEDURE PRC_INSERT_GROUP_16J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

  -- Parse and insert group 17J
  PROCEDURE PRC_INSERT_GROUP_17J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  );

END PKG_DTC_D0302;
/
