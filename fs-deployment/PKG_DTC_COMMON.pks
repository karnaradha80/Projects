--------------------------------------------------------
--  DDL for Package PKG_DTC_COMMON
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_COMMON" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : Common DTC Utilities Package
--
--  NOTES       : This package provides common utility functions shared across all DTC packages.
--                It includes error message retrieval and formatting capabilities with caching
--                support for improved performance.
--
--  FUNCTIONS   :
--    - FN_GET_ERROR_MESSAGE : Retrieves error messages from MDQ_APP_MSG_REF with caching
--    - FN_FORMAT_ERROR      : Formats error messages with parameter substitution (@1-@5)
--    - FN_PARSE_LINE        : Parses pipe-delimited line into fields array
--    - FN_CONVERT_DATE      : Converts YYYYMMDD string to DATE (NULL-safe)
--    - FN_CONVERT_NUMBER    : Converts string to NUMBER (NULL-safe)
--    - FN_SPLIT_FILE_LINES  : Splits CLOB into lines array
--    - FN_GET_GROUP_ID      : Extracts group ID (first field) from line
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  04/Feb/2026   Danie Selvaraju      Initial version - Extracted common error functions
----------------------------------------------------------------------------------------------------

    -- Package-level cache type definition for error messages
  TYPE t_msg_cache IS TABLE OF VARCHAR2(4000) INDEX BY VARCHAR2(20);

  -- Type for parsed line fields (used by FN_PARSE_LINE)
  TYPE t_fields_array IS TABLE OF VARCHAR2(4000) INDEX BY PLS_INTEGER;

  -- DTC file format constants
  C_DELIMITER     CONSTANT VARCHAR2(1) := '|';
  C_HEADER_ID     CONSTANT VARCHAR2(3) := 'ZHV';
  C_FOOTER_ID     CONSTANT VARCHAR2(3) := 'ZPT';

  ----------------------------------------------------------------------------
  -- Function: FN_GET_ERROR_MESSAGE
  -- Description: Retrieves error message text from MDQ_APP_MSG_REF table
  --              Uses package-level cache to minimize database queries
  -- Parameters:
  --   p_msg_pk : Message primary key (error code)
  -- Returns: Message text or default error message if not found
  ----------------------------------------------------------------------------
  FUNCTION FN_GET_ERROR_MESSAGE(
      p_msg_pk VARCHAR2
    ) RETURN VARCHAR2;
  
  ----------------------------------------------------------------------------
  -- Function: FN_FORMAT_ERROR
  -- Description: Formats error message with parameter substitution
  --              Replaces @1, @2, @3, @4, @5 with provided parameter values
  -- Parameters:
  --   p_msg_pk  : Message primary key (error code)
  --   p_param1-5: Optional parameters to substitute into message template
  -- Returns: Fully formatted error message with parameters substituted
  ----------------------------------------------------------------------------
  FUNCTION FN_FORMAT_ERROR(
      p_msg_pk  VARCHAR2, 
      p_param1  VARCHAR2 DEFAULT NULL, 
      p_param2  VARCHAR2 DEFAULT NULL, 
      p_param3  VARCHAR2 DEFAULT NULL, 
      p_param4  VARCHAR2 DEFAULT NULL, 
      p_param5  VARCHAR2 DEFAULT NULL
    ) RETURN VARCHAR2;

  ----------------------------------------------------------------------------
  -- Function: FN_PARSE_LINE
  -- Description: Parses a pipe-delimited line into an array of fields
  -- Parameters:
  --   p_line : The pipe-delimited line to parse
  -- Returns: Array of field values (t_fields_array)
  ----------------------------------------------------------------------------
  FUNCTION FN_PARSE_LINE(
      p_line IN VARCHAR2
    ) RETURN t_fields_array;

  ----------------------------------------------------------------------------
  -- Function: FN_CONVERT_DATE
  -- Description: Converts YYYYMMDD string to DATE with NULL handling
  -- Parameters:
  --   p_date_str : Date string in YYYYMMDD format
  -- Returns: DATE value or NULL if conversion fails
  ----------------------------------------------------------------------------
  FUNCTION FN_CONVERT_DATE(
      p_date_str IN VARCHAR2
    ) RETURN DATE DETERMINISTIC;

  ----------------------------------------------------------------------------
  -- Function: FN_CONVERT_NUMBER
  -- Description: Converts string to NUMBER with NULL handling
  -- Parameters:
  --   p_num_str : Numeric string
  -- Returns: NUMBER value or NULL if conversion fails
  ----------------------------------------------------------------------------
  FUNCTION FN_CONVERT_NUMBER(
      p_num_str IN VARCHAR2
    ) RETURN NUMBER DETERMINISTIC;

  ----------------------------------------------------------------------------
  -- Function: FN_SPLIT_FILE_LINES
  -- Description: Splits CLOB file content into an array of lines
  --              Handles both Unix (LF) and Windows (CRLF) line endings
  -- Parameters:
  --   p_file_content : CLOB containing the file content
  -- Returns: Array of lines (DBMS_SQL.VARCHAR2A)
  ----------------------------------------------------------------------------
  FUNCTION FN_SPLIT_FILE_LINES(
      p_file_content IN CLOB
    ) RETURN DBMS_SQL.VARCHAR2A;

  ----------------------------------------------------------------------------
  -- Function: FN_GET_GROUP_ID
  -- Description: Extracts the group ID (first field) from a pipe-delimited line
  -- Parameters:
  --   p_line : The pipe-delimited line
  -- Returns: Group identifier (first field before delimiter)
  ----------------------------------------------------------------------------
  FUNCTION FN_GET_GROUP_ID(
      p_line IN VARCHAR2
    ) RETURN VARCHAR2;

END PKG_DTC_COMMON;
/