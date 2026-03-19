--------------------------------------------------------
--  DDL for Package Body PKG_DTC_COMMON
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "MDQA_OWNER"."PKG_DTC_COMMON" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : Common DTC Utilities Package Body
--
--  NOTES       : Implementation of common utility functions shared across all DTC packages
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Feb/2026   Danie             Initial version
--  25/Feb/2026   Radha             FN_FORMAT_ERROR: replaced NULL-check with
--                                  INSTR-based placeholder replacement, NVL default '(empty)'
--  25/Feb/2026   Radha             FN_FORMAT_ERROR: changed NVL default from
--                                  '(empty)' to 'empty' for ERR_FILE_COL_VAL consistency
--  17/Mar/2026   Radha             FN_SPLIT_FILE_LINES: fixed ORA-06502 buffer
--                                  overflow when v_remaining || v_buffer > 32767
----------------------------------------------------------------------------------------------------

  -- Package-level cache variable for error messages
  -- Persists for the session lifetime to minimize database queries
  g_msg_cache t_msg_cache;

----------------------------------------------------------------------------------------------------
-- Function: FN_GET_ERROR_MESSAGE
-- Description: Retrieves error message from cache or database
----------------------------------------------------------------------------------------------------
  FUNCTION FN_GET_ERROR_MESSAGE(
    p_msg_pk VARCHAR2
  ) RETURN VARCHAR2 IS
    v_msg_text VARCHAR2(4000);
  BEGIN
    -- Check cache first for performance
    IF g_msg_cache.EXISTS(p_msg_pk) THEN
      RETURN g_msg_cache(p_msg_pk);
    END IF;

    -- Not in cache, query from MDQ_APP_MSG_REF table
    BEGIN
      SELECT MSG_TEXT
        INTO v_msg_text
        FROM MDQ_APP_MSG_REF
       WHERE MSG_PK = p_msg_pk;

      -- Store in cache for future use
      g_msg_cache(p_msg_pk) := v_msg_text;

      RETURN v_msg_text;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        -- Message code not found in reference table
        v_msg_text := 'Error code ' || p_msg_pk || ' not found in message reference';
        g_msg_cache(p_msg_pk) := v_msg_text;
        RETURN v_msg_text;
      WHEN OTHERS THEN
        -- Unexpected error during query
        RETURN 'Error retrieving message for code ' || p_msg_pk || ': ' || SQLERRM;
    END;
  END FN_GET_ERROR_MESSAGE;

----------------------------------------------------------------------------------------------------
-- Function: FN_FORMAT_ERROR
-- Description: Formats error message with parameter substitution
----------------------------------------------------------------------------------------------------
  FUNCTION FN_FORMAT_ERROR(
    p_msg_pk  VARCHAR2,
    p_param1  VARCHAR2 DEFAULT NULL,
    p_param2  VARCHAR2 DEFAULT NULL,
    p_param3  VARCHAR2 DEFAULT NULL,
    p_param4  VARCHAR2 DEFAULT NULL,
    p_param5  VARCHAR2 DEFAULT NULL
  ) RETURN VARCHAR2 IS
    v_message VARCHAR2(4000);
  BEGIN
    -- Get the message template from cache or database
    v_message := FN_GET_ERROR_MESSAGE(p_msg_pk);

    -- Replace @1, @2, @3, @4, @5 placeholders with parameter values
    -- Always replace to avoid raw @N placeholders in output; use 'empty' for NULL
    IF INSTR(v_message, '@1') > 0 THEN
      v_message := REPLACE(v_message, '@1', NVL(p_param1, 'empty'));
    END IF;

    IF INSTR(v_message, '@2') > 0 THEN
      v_message := REPLACE(v_message, '@2', NVL(p_param2, 'empty'));
    END IF;

    IF INSTR(v_message, '@3') > 0 THEN
      v_message := REPLACE(v_message, '@3', NVL(p_param3, 'empty'));
    END IF;

    IF INSTR(v_message, '@4') > 0 THEN
      v_message := REPLACE(v_message, '@4', NVL(p_param4, 'empty'));
    END IF;

    IF INSTR(v_message, '@5') > 0 THEN
      v_message := REPLACE(v_message, '@5', NVL(p_param5, 'empty'));
    END IF;

    RETURN v_message;
  END FN_FORMAT_ERROR;

----------------------------------------------------------------------------------------------------
-- Function: FN_PARSE_LINE
-- Description: Parses a pipe-delimited line into an array of fields
----------------------------------------------------------------------------------------------------
  FUNCTION FN_PARSE_LINE(
    p_line IN VARCHAR2
  ) RETURN t_fields_array IS
    v_fields      t_fields_array;
    v_field_idx   NUMBER := 1;
    v_pos         NUMBER := 1;
    v_next_pos    NUMBER;
  BEGIN
    IF p_line IS NULL OR LENGTH(p_line) = 0 THEN
      RETURN v_fields;
    END IF;

    LOOP
      v_next_pos := INSTR(p_line, C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        -- No more delimiters, get the rest of the string
        v_fields(v_field_idx) := SUBSTR(p_line, v_pos);
        EXIT;
      END IF;

      -- Extract field (can be empty)
      v_fields(v_field_idx) := SUBSTR(p_line, v_pos, v_next_pos - v_pos);
      v_field_idx := v_field_idx + 1;
      v_pos := v_next_pos + 1;

      -- If we just processed a delimiter at the end of the string, add one more empty field
      IF v_pos > LENGTH(p_line) THEN
        v_fields(v_field_idx) := '';
        EXIT;
      END IF;
    END LOOP;

    RETURN v_fields;
  END FN_PARSE_LINE;

----------------------------------------------------------------------------------------------------
-- Function: FN_CONVERT_DATE
-- Description: Converts YYYYMMDD string to DATE with NULL handling
----------------------------------------------------------------------------------------------------
  FUNCTION FN_CONVERT_DATE(
    p_date_str IN VARCHAR2
  ) RETURN DATE DETERMINISTIC IS
  BEGIN
    IF p_date_str IS NULL OR LENGTH(TRIM(p_date_str)) = 0 THEN
      RETURN NULL;
    END IF;
    RETURN TO_DATE(p_date_str, 'YYYYMMDD');
  EXCEPTION
    WHEN OTHERS THEN
      RETURN NULL;
  END FN_CONVERT_DATE;

----------------------------------------------------------------------------------------------------
-- Function: FN_CONVERT_NUMBER
-- Description: Converts string to NUMBER with NULL handling
----------------------------------------------------------------------------------------------------
  FUNCTION FN_CONVERT_NUMBER(
    p_num_str IN VARCHAR2
  ) RETURN NUMBER DETERMINISTIC IS
  BEGIN
    IF p_num_str IS NULL OR LENGTH(TRIM(p_num_str)) = 0 THEN
      RETURN NULL;
    END IF;
    RETURN TO_NUMBER(p_num_str);
  EXCEPTION
    WHEN OTHERS THEN
      RETURN NULL;
  END FN_CONVERT_NUMBER;

----------------------------------------------------------------------------------------------------
-- Function: FN_SPLIT_FILE_LINES
-- Description: Splits CLOB file content into an array of lines
----------------------------------------------------------------------------------------------------
  FUNCTION FN_SPLIT_FILE_LINES(
    p_file_content IN CLOB
  ) RETURN DBMS_SQL.VARCHAR2A IS
    v_lines       DBMS_SQL.VARCHAR2A;
    v_offset      NUMBER := 1;
    v_clob_len    NUMBER;
    v_read_amount NUMBER;
    v_buffer      VARCHAR2(32767);
    v_line        VARCHAR2(32767);
    v_line_idx    NUMBER := 1;
    v_pos         NUMBER;
    v_remaining   VARCHAR2(32767) := '';
  BEGIN
    v_clob_len := DBMS_LOB.GETLENGTH(p_file_content);

    WHILE v_offset <= v_clob_len LOOP
      -- Calculate read size: leave room for v_remaining to avoid overflow
      v_read_amount := 32767 - NVL(LENGTH(v_remaining), 0);
      IF v_read_amount <= 0 THEN
        -- Single line exceeds buffer; store what we have and continue
        v_lines(v_line_idx) := v_remaining;
        v_line_idx := v_line_idx + 1;
        v_remaining := '';
        v_read_amount := 32767;
      END IF;

      DBMS_LOB.READ(p_file_content, v_read_amount, v_offset, v_buffer);
      v_offset := v_offset + v_read_amount;

      v_buffer := v_remaining || v_buffer;
      v_remaining := '';

      LOOP
        v_pos := INSTR(v_buffer, CHR(10));
        IF v_pos = 0 OR v_pos IS NULL THEN
          v_remaining := v_buffer;
          EXIT;
        END IF;

        v_line := TRIM(CHR(13) FROM SUBSTR(v_buffer, 1, v_pos - 1));
        IF LENGTH(TRIM(v_line)) > 0 THEN
          v_lines(v_line_idx) := v_line;
          v_line_idx := v_line_idx + 1;
        END IF;

        v_buffer := SUBSTR(v_buffer, v_pos + 1);
      END LOOP;
    END LOOP;

    -- Handle last line if any
    IF LENGTH(TRIM(v_remaining)) > 0 THEN
      v_lines(v_line_idx) := v_remaining;
    END IF;

    RETURN v_lines;
  END FN_SPLIT_FILE_LINES;

----------------------------------------------------------------------------------------------------
-- Function: FN_GET_GROUP_ID
-- Description: Extracts the group ID (first field) from a pipe-delimited line
----------------------------------------------------------------------------------------------------
  FUNCTION FN_GET_GROUP_ID(
    p_line IN VARCHAR2
  ) RETURN VARCHAR2 IS
    v_group_id VARCHAR2(10);
  BEGIN
    -- Group ID is the first field before the first delimiter
    v_group_id := SUBSTR(p_line, 1, INSTR(p_line, C_DELIMITER) - 1);
    RETURN v_group_id;
  EXCEPTION
    WHEN OTHERS THEN
      RETURN NULL;
  END FN_GET_GROUP_ID;

END PKG_DTC_COMMON;
/
