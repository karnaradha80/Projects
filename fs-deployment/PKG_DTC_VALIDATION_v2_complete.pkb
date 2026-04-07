--------------------------------------------------------
--  DDL for Package Body PKG_DTC_VALIDATION (V2 - Complete)
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "MDQA_OWNER"."PKG_DTC_VALIDATION" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : Generic DTC Flow Validation Package
--
--  NOTES       : This package provides generic validation logic for any DTC flow
--                using JSON-based configuration stored in MDQ_ETL_VALIDATION_CONFIG
--
--  VERSION 2   : Added two-stage validation with partial rejection support
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Feb/2026   Danie             Initial version
--  10/Feb/2026   Radha             Cosmetic cleanup
--  12/Feb/2026   Radha             Added header/footer mandatory field validation
--                                  against config in Stage 1
--  18/Feb/2026   Radha             Set status to REJECTED when staged_flow_count=0,
--                                  removed duplicate error entries
--  19/Feb/2026   Radha             Added separate footer mandatory error code ERR8043,
--                                  NVL handling for NULL header/footer identifiers,
--                                  restructured mandatory validation flow
--  23/Feb/2026   Radha             Added data-level mandatory field error code ERR8044,
--                                  removed duplicate record count validation
--  25/Feb/2026   Radha             Added line_number to footer errors, added
--                                  field_name/field_value to all ADD_ERROR calls
--  26/Feb/2026   Radha             Added line_number to flow count/file ID errors,
--                                  skip minLength/maxLength for NUMBER precision fields,
--                                  header/footer parse overflow protection
--  05/Mar/2026   Radha             Added p_field_position param to ADD_ERROR,
--                                  ERR_FILE_COL now stores 'name - position' format
--  06/Mar/2026   Radha             Empty header/footer identifier now triggers mandatory
--                                  validation instead of immediate rejection
----------------------------------------------------------------------------------------------------

  -- Error codes (mapped to MDQ_APP_MSG_REF)
  C_ERR_CONFIG_NOT_FOUND    CONSTANT VARCHAR2(50) := 'ERR8003';
  C_ERR_HEADER_MISSING      CONSTANT VARCHAR2(50) := 'ERR8007';
  C_ERR_FOOTER_MISSING      CONSTANT VARCHAR2(50) := 'ERR8008';
  C_ERR_FIELD_MANDATORY     CONSTANT VARCHAR2(50) := 'ERR8013';
  C_ERR_FIELD_LENGTH        CONSTANT VARCHAR2(50) := 'ERR8014';
  C_ERR_FIELD_DATATYPE      CONSTANT VARCHAR2(50) := 'ERR8016';
  C_ERR_FIELD_PATTERN       CONSTANT VARCHAR2(50) := 'ERR8021';
  C_ERR_RECORD_COUNT        CONSTANT VARCHAR2(50) := 'ERR8024';
  C_ERR_FOOTER_FIELD_MANDATORY CONSTANT VARCHAR2(50) := 'ERR8043';
  C_ERR_DATA_FIELD_MANDATORY CONSTANT VARCHAR2(50) := 'ERR8044';
  C_ERR_GROUP_MIN_OCC       CONSTANT VARCHAR2(50) := 'ERR8030';
  C_ERR_GROUP_MAX_OCC       CONSTANT VARCHAR2(50) := 'ERR8031';
  C_ERR_RECIPIENT_ID        CONSTANT VARCHAR2(50) := 'ERR8045';

----------------------------------------------------------------------------------------------------
-- Helper function: Add error to collection (public)
----------------------------------------------------------------------------------------------------
  PROCEDURE ADD_ERROR(
    p_errors       IN OUT t_validation_errors,
    p_error_code   IN VARCHAR2,
    p_error_msg    IN VARCHAR2,
    p_line_number  IN NUMBER DEFAULT NULL,
    p_field_name   IN VARCHAR2 DEFAULT NULL,
    p_field_value  IN VARCHAR2 DEFAULT NULL,
    p_group_id     IN VARCHAR2 DEFAULT NULL,
    p_field_position IN NUMBER DEFAULT NULL
  ) IS
    v_error t_validation_error;
  BEGIN
    v_error.error_code := p_error_code;
    v_error.error_message := p_error_msg;
    v_error.line_number := p_line_number;
    v_error.field_name := CASE WHEN p_field_position IS NOT NULL THEN p_field_name || ' - ' || TO_CHAR(p_field_position) ELSE p_field_name END;
    v_error.field_value := p_field_value;
    v_error.group_id := p_group_id;

    IF p_errors IS NULL THEN
      p_errors := t_validation_errors();
    END IF;

    p_errors.EXTEND;
    p_errors(p_errors.COUNT) := v_error;
  END ADD_ERROR;

----------------------------------------------------------------------------------------------------
-- Get active validation config for a flow type
----------------------------------------------------------------------------------------------------
  FUNCTION FN_GET_ACTIVE_CONFIG(
    p_flow_type IN VARCHAR2
  ) RETURN CLOB IS
    v_config_json CLOB;
  BEGIN
    -- Use subquery to apply ORDER BY before ROWNUM filter
    SELECT MEVC_CONFIG_JSON
    INTO v_config_json
    FROM (
      SELECT MEVC_CONFIG_JSON
      FROM MDQ_ETL_VALIDATION_CONFIG
      WHERE MEVC_FLOW_TYPE = p_flow_type
        AND MEVC_ACTIVE_YN = 'Y'
      ORDER BY MEVC_CONFIG_VERSION DESC
    )
    WHERE ROWNUM = 1;

    RETURN v_config_json;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN NULL;
    WHEN OTHERS THEN
      RAISE;
  END FN_GET_ACTIVE_CONFIG;

----------------------------------------------------------------------------------------------------
-- Validate a single field value
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_FIELD(
    p_field_value  IN VARCHAR2,
    p_field_config IN JSON_OBJECT_T,
    p_field_name   OUT VARCHAR2,
    p_error_msg    OUT VARCHAR2
  ) RETURN BOOLEAN IS
    v_mandatory    BOOLEAN;
    v_min_length   NUMBER;
    v_max_length   NUMBER;
    v_data_type    VARCHAR2(20);
    v_pattern      VARCHAR2(200);
    v_format       VARCHAR2(50);
    v_field_length NUMBER;
    v_date_value   DATE;
    v_number_value NUMBER;
    v_precision    NUMBER;
    v_scale        NUMBER;
    v_integer_part VARCHAR2(100);
    v_decimal_part VARCHAR2(100);
    v_decimal_pos  NUMBER;
    v_total_digits NUMBER;
    v_decimal_digits NUMBER;
    v_pattern_error_code VARCHAR2(20);
  BEGIN
    p_field_name := p_field_config.get_String('name');
    v_mandatory := p_field_config.get_Boolean('mandatory');
    v_min_length := p_field_config.get_Number('minLength');
    v_max_length := p_field_config.get_Number('maxLength');

    IF p_field_config.has('dataType') THEN
      v_data_type := p_field_config.get_String('dataType');
    END IF;

    IF p_field_config.has('pattern') THEN
      v_pattern := p_field_config.get_String('pattern');
    END IF;

    IF p_field_config.has('patternErrorCode') THEN
      v_pattern_error_code := p_field_config.get_String('patternErrorCode');
    END IF;

    IF p_field_config.has('format') THEN
      v_format := p_field_config.get_String('format');
    END IF;

    IF p_field_config.has('precision') THEN
      v_precision := p_field_config.get_Number('precision');
    END IF;

    IF p_field_config.has('scale') THEN
      v_scale := p_field_config.get_Number('scale');
    END IF;

    v_field_length := NVL(LENGTH(p_field_value), 0);

    -- Check mandatory
    IF v_mandatory AND v_field_length = 0 THEN
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8013', p_field_name);
      RETURN FALSE;
    END IF;

    -- Check length (only if field has value)
    -- Skip minLength/maxLength for NUMBER fields with precision and scale defined
    -- as precision/scale validation checks digits before and after decimal separately
    IF v_field_length > 0 THEN
      IF NOT (v_data_type = 'NUMBER' AND v_precision IS NOT NULL AND v_scale IS NOT NULL) THEN
        IF v_field_length < v_min_length THEN
          p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8014', p_field_name, TO_CHAR(v_field_length), TO_CHAR(v_min_length));
          RETURN FALSE;
        END IF;

        IF v_field_length > v_max_length THEN
          p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', p_field_name, TO_CHAR(v_field_length), TO_CHAR(v_max_length));
          RETURN FALSE;
        END IF;
      END IF;

      -- Check data type
      IF v_data_type IS NOT NULL THEN
        IF v_data_type = 'NUMBER' THEN
          BEGIN
            v_number_value := TO_NUMBER(p_field_value);
          EXCEPTION
            WHEN OTHERS THEN
              p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8016', p_field_name, p_field_value);
              RETURN FALSE;
          END;

          -- Validate precision and scale if defined
          IF v_precision IS NOT NULL AND v_scale IS NOT NULL THEN
            -- Find decimal point position
            v_decimal_pos := INSTR(p_field_value, '.');

            IF v_decimal_pos > 0 THEN
              -- Has decimal point
              v_integer_part := SUBSTR(p_field_value, 1, v_decimal_pos - 1);
              v_decimal_part := SUBSTR(p_field_value, v_decimal_pos + 1);

              -- Remove leading zeros and sign from integer part for digit counting
              v_integer_part := LTRIM(LTRIM(v_integer_part, '0'), '-');
              IF v_integer_part IS NULL THEN
                v_integer_part := '0';
              END IF;

              -- Count digits
              v_total_digits := LENGTH(v_integer_part) + LENGTH(v_decimal_part);
              v_decimal_digits := LENGTH(v_decimal_part);

              -- Validate scale (decimal places)
              IF v_decimal_digits > v_scale THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8017', p_field_name, TO_CHAR(v_decimal_digits), TO_CHAR(v_scale));
                RETURN FALSE;
              END IF;

              -- Validate precision (total significant digits)
              IF v_total_digits > v_precision THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8018', p_field_name, TO_CHAR(v_total_digits), TO_CHAR(v_precision));
                RETURN FALSE;
              END IF;
            ELSE
              -- No decimal point - integer only
              v_integer_part := LTRIM(LTRIM(p_field_value, '0'), '-');
              IF v_integer_part IS NULL THEN
                v_integer_part := '0';
              END IF;

              v_total_digits := LENGTH(v_integer_part);

              -- For integers, precision minus scale gives max integer digits allowed
              IF v_total_digits > (v_precision - v_scale) THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8019', p_field_name, TO_CHAR(v_total_digits),
                                               TO_CHAR(v_precision - v_scale), TO_CHAR(v_precision), TO_CHAR(v_scale));
                RETURN FALSE;
              END IF;
            END IF;
          END IF;
        ELSIF v_data_type IN ('DATE', 'DATETIME') THEN
          BEGIN
            -- Convert format from JSON format to Oracle format
            v_format := REPLACE(v_format, 'YYYY', 'YYYY');
            v_format := REPLACE(v_format, 'MM', 'MM');
            v_format := REPLACE(v_format, 'DD', 'DD');
            v_format := REPLACE(v_format, 'HH24', 'HH24');
            v_format := REPLACE(v_format, 'MI', 'MI');
            v_format := REPLACE(v_format, 'SS', 'SS');
            v_date_value := TO_DATE(p_field_value, v_format);
          EXCEPTION
            WHEN OTHERS THEN
              p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8020', p_field_name, p_field_value, v_format);
              RETURN FALSE;
          END;
        END IF;
      END IF;

      -- Check pattern
      IF v_pattern IS NOT NULL THEN
        -- Fix escaped regex patterns from JSON (\\d -> \d, \\w -> \w, \\s -> \s, etc.)
        v_pattern := REPLACE(v_pattern, '\\d', '\d');
        v_pattern := REPLACE(v_pattern, '\\D', '\D');
        v_pattern := REPLACE(v_pattern, '\\w', '\w');
        v_pattern := REPLACE(v_pattern, '\\W', '\W');
        v_pattern := REPLACE(v_pattern, '\\s', '\s');
        v_pattern := REPLACE(v_pattern, '\\S', '\S');

        IF NOT REGEXP_LIKE(p_field_value, v_pattern) THEN
          IF v_pattern_error_code IS NOT NULL THEN
            p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR(v_pattern_error_code, p_field_value);
          ELSE
            p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8021', p_field_name, p_field_value, v_pattern);
          END IF;
          RETURN FALSE;
        END IF;
      END IF;
    END IF;

    RETURN TRUE;
  EXCEPTION
    WHEN OTHERS THEN
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8022', p_field_name, SQLERRM);
      RETURN FALSE;
  END FN_VALIDATE_FIELD;

----------------------------------------------------------------------------------------------------
-- Validate header line
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_HEADER(
    p_header_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config       JSON_OBJECT_T;
    v_header_config JSON_OBJECT_T;
    v_fields_array JSON_ARRAY_T;
    v_field_config JSON_OBJECT_T;
    v_header_parts DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_field_value  VARCHAR2(4000);
    v_field_name   VARCHAR2(100);
    v_error_msg    VARCHAR2(4000);
    v_valid        BOOLEAN := TRUE;
    v_header_id    VARCHAR2(10);
  BEGIN
    p_errors := t_validation_errors();

    -- Parse JSON config
    v_config := JSON_OBJECT_T(p_config_json);
    v_header_config := JSON_OBJECT_T(v_config.get('header'));
    v_header_id := v_header_config.get_String('identifier');
    v_fields_array := JSON_ARRAY_T(v_header_config.get('fields'));

    -- Split header line by delimiter
    WHILE v_pos <= LENGTH(p_header_line) LOOP
      v_next_pos := INSTR(p_header_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_header_line) + 1;
      END IF;

      v_header_parts(v_part_idx) := SUBSTR(p_header_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate header identifier (use NVL to handle Oracle NULL = empty string)
    IF NVL(v_header_parts(1), ' ') != v_header_id THEN
      IF NVL(LENGTH(v_header_parts(1)), 0) = 0 THEN
        -- Empty/null identifier - trigger mandatory validation
        ADD_ERROR(p_errors, C_ERR_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8013', 'headerIdentifier'),
          1, 'headerIdentifier', v_header_parts(1),
          p_field_position => 1);
        v_valid := FALSE;
      ELSE
        -- Non-empty but wrong identifier - file is invalid
        ADD_ERROR(p_errors, C_ERR_HEADER_MISSING,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8007', v_header_id, v_header_parts(1)),
          1, 'headerIdentifier', v_header_parts(1),
          p_field_position => 1);
        RETURN FALSE;
      END IF;
    END IF;

    -- Validate each field
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_config := JSON_OBJECT_T(v_fields_array.get(i));
      v_part_idx := v_field_config.get_Number('position') + 1; -- +1 because position 1 is header identifier

      IF v_header_parts.EXISTS(v_part_idx) THEN
        v_field_value := v_header_parts(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_field_config, v_field_name, v_error_msg) THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_MANDATORY, v_error_msg, 1, v_field_name, v_field_value,
          p_field_position => v_field_config.get_Number('position') + 1);
        v_valid := FALSE;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'HEADER_VALIDATION_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8009', SQLERRM), 1, 'header');
      RETURN FALSE;
  END FN_VALIDATE_HEADER;

----------------------------------------------------------------------------------------------------
-- Validate footer line
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_FOOTER(
    p_footer_line      IN VARCHAR2,
    p_config_json      IN CLOB,
    p_expected_count   IN NUMBER,
    p_errors           OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config       JSON_OBJECT_T;
    v_footer_config JSON_OBJECT_T;
    v_fields_array JSON_ARRAY_T;
    v_field_config JSON_OBJECT_T;
    v_footer_parts DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_field_value  VARCHAR2(4000);
    v_field_name   VARCHAR2(100);
    v_error_msg    VARCHAR2(4000);
    v_valid        BOOLEAN := TRUE;
    v_footer_id    VARCHAR2(10);
    v_record_count NUMBER;
  BEGIN
    p_errors := t_validation_errors();

    -- Parse JSON config
    v_config := JSON_OBJECT_T(p_config_json);
    v_footer_config := JSON_OBJECT_T(v_config.get('footer'));
    v_footer_id := v_footer_config.get_String('identifier');
    v_fields_array := JSON_ARRAY_T(v_footer_config.get('fields'));

    -- Split footer line by delimiter
    WHILE v_pos <= LENGTH(p_footer_line) LOOP
      v_next_pos := INSTR(p_footer_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_footer_line) + 1;
      END IF;

      v_footer_parts(v_part_idx) := SUBSTR(p_footer_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate footer identifier (use NVL to handle Oracle NULL = empty string)
    IF NVL(v_footer_parts(1), ' ') != v_footer_id THEN
      IF NVL(LENGTH(v_footer_parts(1)), 0) = 0 THEN
        -- Empty/null identifier - trigger mandatory validation
        ADD_ERROR(p_errors, C_ERR_FOOTER_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8043', 'footerIdentifier'),
          NULL, 'footerIdentifier', v_footer_parts(1),
          p_field_position => 1);
        v_valid := FALSE;
      ELSE
        -- Non-empty but wrong identifier - file is invalid
        ADD_ERROR(p_errors, C_ERR_FOOTER_MISSING,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8008', v_footer_id, v_footer_parts(1)),
          NULL, 'footerIdentifier', v_footer_parts(1),
          p_field_position => 1);
        RETURN FALSE;
      END IF;
    END IF;

    -- Validate each field
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_config := JSON_OBJECT_T(v_fields_array.get(i));
      v_part_idx := v_field_config.get_Number('position') + 1; -- +1 because position 1 is footer identifier

      IF v_footer_parts.EXISTS(v_part_idx) THEN
        v_field_value := v_footer_parts(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_field_config, v_field_name, v_error_msg) THEN
        -- Use footer-specific error code to distinguish from header mandatory errors
        IF NVL(LENGTH(v_field_value), 0) = 0 THEN
          -- Mandatory field missing - use footer-specific error code and message
          ADD_ERROR(p_errors, C_ERR_FOOTER_FIELD_MANDATORY,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8043', v_field_name), NULL, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        ELSE
          -- Other validation failure (length, datatype, pattern) - keep original message
          ADD_ERROR(p_errors, C_ERR_FOOTER_FIELD_MANDATORY, v_error_msg, NULL, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        END IF;
        v_valid := FALSE;
      END IF;

      -- Check record count if this is the record count field
      IF v_field_name = 'recordCount' THEN
        BEGIN
          v_record_count := TO_NUMBER(v_field_value);
          IF v_record_count != p_expected_count THEN
            ADD_ERROR(p_errors, C_ERR_RECORD_COUNT,
              PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8024', TO_CHAR(p_expected_count), TO_CHAR(v_record_count)),
              NULL, v_field_name, v_field_value,
              p_field_position => v_field_config.get_Number('position') + 1);
            v_valid := FALSE;
          END IF;
        EXCEPTION
          WHEN OTHERS THEN
            ADD_ERROR(p_errors, C_ERR_RECORD_COUNT, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8025', v_field_value),
              NULL, v_field_name, v_field_value,
              p_field_position => v_field_config.get_Number('position') + 1);
            v_valid := FALSE;
        END;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'FOOTER_VALIDATION_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8010', SQLERRM), NULL, 'footer');
      RETURN FALSE;
  END FN_VALIDATE_FOOTER;

----------------------------------------------------------------------------------------------------
-- Validate a single group line
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_GROUP_LINE(
    p_line         IN VARCHAR2,
    p_group_id     IN VARCHAR2,
    p_config_json  IN CLOB,
    p_line_number  IN NUMBER,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config       JSON_OBJECT_T;
    v_groups_array JSON_ARRAY_T;
    v_group_config JSON_OBJECT_T;
    v_fields_array JSON_ARRAY_T;
    v_field_config JSON_OBJECT_T;
    v_line_parts   DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_field_value  VARCHAR2(4000);
    v_field_name   VARCHAR2(100);
    v_error_msg    VARCHAR2(4000);
    v_valid        BOOLEAN := TRUE;
    v_found        BOOLEAN := FALSE;
    v_current_group_id VARCHAR2(10);
  BEGIN
    p_errors := t_validation_errors();

    -- Parse JSON config
    v_config := JSON_OBJECT_T(p_config_json);
    v_groups_array := JSON_ARRAY_T(v_config.get('groups'));

    -- Find the group configuration
    FOR i IN 0 .. v_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(v_groups_array.get(i));
      v_current_group_id := v_group_config.get_String('groupId');

      IF v_current_group_id = p_group_id THEN
        v_found := TRUE;
        EXIT;
      END IF;
    END LOOP;

    IF NOT v_found THEN
      IF NVL(LENGTH(p_group_id), 0) = 0 THEN
        -- Empty/null group ID - mandatory field not populated
        ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', 'groupId'), p_line_number, 'groupId', p_group_id,
            p_field_position => 1);
      ELSE
        -- Non-empty but invalid group ID
        ADD_ERROR(p_errors, 'UNKNOWN_GROUP',
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8027', p_group_id), p_line_number, 'groupId', p_group_id,
            p_field_position => 1);
      END IF;
      RETURN FALSE;
    END IF;

    -- Get fields configuration
    v_fields_array := JSON_ARRAY_T(v_group_config.get('fields'));

    -- Split line by delimiter
    WHILE v_pos <= LENGTH(p_line) LOOP
      v_next_pos := INSTR(p_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_line) + 1;
      END IF;

      v_line_parts(v_part_idx) := SUBSTR(p_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate each field
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_config := JSON_OBJECT_T(v_fields_array.get(i));
      v_part_idx := v_field_config.get_Number('position') + 1; -- +1 because position 1 is group ID

      IF v_line_parts.EXISTS(v_part_idx) THEN
        v_field_value := v_line_parts(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_field_config, v_field_name, v_error_msg) THEN
        -- Use data-specific error code for mandatory field failures (not header/footer)
        IF NVL(LENGTH(v_field_value), 0) = 0 THEN
          -- Mandatory field missing - use data-specific error code and message
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', v_field_name), p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        ELSE
          -- Other validation failure (length, datatype, pattern) - keep original message
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY, v_error_msg, p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        END IF;
        v_valid := FALSE;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'GROUP_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8028', p_group_id, SQLERRM), p_line_number, 'groupId', p_group_id,
          p_field_position => 1);
      RETURN FALSE;
  END FN_VALIDATE_GROUP_LINE;

----------------------------------------------------------------------------------------------------
-- Overload: Validate a single group line using pre-parsed groups array (avoids JSON re-parse per line)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_GROUP_LINE(
    p_line          IN VARCHAR2,
    p_group_id      IN VARCHAR2,
    p_groups_array  IN JSON_ARRAY_T,
    p_line_number   IN NUMBER,
    p_errors        OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_group_config JSON_OBJECT_T;
    v_fields_array JSON_ARRAY_T;
    v_field_config JSON_OBJECT_T;
    v_line_parts   DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_field_value  VARCHAR2(4000);
    v_field_name   VARCHAR2(100);
    v_error_msg    VARCHAR2(4000);
    v_valid        BOOLEAN := TRUE;
    v_found        BOOLEAN := FALSE;
    v_current_group_id VARCHAR2(10);
  BEGIN
    p_errors := t_validation_errors();

    -- Find the group configuration using the caller-provided pre-parsed array
    FOR i IN 0 .. p_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(p_groups_array.get(i));
      v_current_group_id := v_group_config.get_String('groupId');

      IF v_current_group_id = p_group_id THEN
        v_found := TRUE;
        EXIT;
      END IF;
    END LOOP;

    IF NOT v_found THEN
      IF NVL(LENGTH(p_group_id), 0) = 0 THEN
        ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', 'groupId'), p_line_number, 'groupId', p_group_id,
            p_field_position => 1);
      ELSE
        ADD_ERROR(p_errors, 'UNKNOWN_GROUP',
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8027', p_group_id), p_line_number, 'groupId', p_group_id,
            p_field_position => 1);
      END IF;
      RETURN FALSE;
    END IF;

    -- Get fields configuration
    v_fields_array := JSON_ARRAY_T(v_group_config.get('fields'));

    -- Split line by delimiter
    WHILE v_pos <= LENGTH(p_line) LOOP
      v_next_pos := INSTR(p_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_line) + 1;
      END IF;

      v_line_parts(v_part_idx) := SUBSTR(p_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate each field
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_config := JSON_OBJECT_T(v_fields_array.get(i));
      v_part_idx := v_field_config.get_Number('position') + 1;

      IF v_line_parts.EXISTS(v_part_idx) THEN
        v_field_value := v_line_parts(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_field_config, v_field_name, v_error_msg) THEN
        IF NVL(LENGTH(v_field_value), 0) = 0 THEN
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', v_field_name), p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        ELSE
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY, v_error_msg, p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        END IF;
        v_valid := FALSE;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'GROUP_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8028', p_group_id, SQLERRM), p_line_number, 'groupId', p_group_id,
          p_field_position => 1);
      RETURN FALSE;
  END FN_VALIDATE_GROUP_LINE;

----------------------------------------------------------------------------------------------------
-- Overload: Validate using pre-parsed fields array (avoids line splitting per call)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_GROUP_LINE(
    p_fields        IN PKG_DTC_COMMON.t_fields_array,
    p_group_id      IN VARCHAR2,
    p_groups_array  IN JSON_ARRAY_T,
    p_line_number   IN NUMBER,
    p_errors        OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_group_config     JSON_OBJECT_T;
    v_fields_array     JSON_ARRAY_T;
    v_field_config     JSON_OBJECT_T;
    v_part_idx         NUMBER;
    v_field_value      VARCHAR2(4000);
    v_field_name       VARCHAR2(100);
    v_error_msg        VARCHAR2(4000);
    v_valid            BOOLEAN := TRUE;
    v_found            BOOLEAN := FALSE;
    v_current_group_id VARCHAR2(10);
  BEGIN
    p_errors := t_validation_errors();

    -- Find group config using pre-parsed groups array
    FOR i IN 0 .. p_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(p_groups_array.get(i));
      v_current_group_id := v_group_config.get_String('groupId');
      IF v_current_group_id = p_group_id THEN
        v_found := TRUE;
        EXIT;
      END IF;
    END LOOP;

    IF NOT v_found THEN
      IF NVL(LENGTH(p_group_id), 0) = 0 THEN
        ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', 'groupId'), p_line_number, 'groupId', NULL,
            p_field_position => 1);
      ELSE
        ADD_ERROR(p_errors, 'UNKNOWN_GROUP',
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8027', p_group_id), p_line_number, 'groupId', p_group_id,
            p_field_position => 1);
      END IF;
      RETURN FALSE;
    END IF;

    -- Get fields configuration
    v_fields_array := JSON_ARRAY_T(v_group_config.get('fields'));

    -- Validate each field using pre-parsed fields (no line splitting needed)
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_config := JSON_OBJECT_T(v_fields_array.get(i));
      v_part_idx := v_field_config.get_Number('position') + 1;

      IF p_fields.EXISTS(v_part_idx) THEN
        v_field_value := p_fields(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_field_config, v_field_name, v_error_msg) THEN
        IF NVL(LENGTH(v_field_value), 0) = 0 THEN
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', v_field_name), p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        ELSE
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY, v_error_msg, p_line_number, v_field_name, v_field_value,
            p_field_position => v_field_config.get_Number('position') + 1);
        END IF;
        v_valid := FALSE;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'GROUP_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8028', p_group_id, SQLERRM), p_line_number, 'groupId', p_group_id,
          p_field_position => 1);
      RETURN FALSE;
  END FN_VALIDATE_GROUP_LINE;

----------------------------------------------------------------------------------------------------
-- Private overload: Validate a single field using pre-processed t_field_config (no JSON per call)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_FIELD(
    p_field_value  IN VARCHAR2,
    p_field_config IN t_field_config,
    p_error_msg    OUT VARCHAR2
  ) RETURN BOOLEAN IS
    v_field_length   NUMBER;
    v_number_value   NUMBER;
    v_date_value     DATE;
    v_integer_part   VARCHAR2(100);
    v_decimal_part   VARCHAR2(100);
    v_decimal_pos    NUMBER;
    v_total_digits   NUMBER;
    v_decimal_digits NUMBER;
  BEGIN
    v_field_length := NVL(LENGTH(p_field_value), 0);

    -- Check mandatory
    IF p_field_config.mandatory AND v_field_length = 0 THEN
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8013', p_field_config.field_name);
      RETURN FALSE;
    END IF;

    IF v_field_length > 0 THEN
      -- Check length (skip when NUMBER with precision+scale defined)
      IF NOT (p_field_config.data_type = 'NUMBER'
              AND p_field_config.precision IS NOT NULL
              AND p_field_config.scale     IS NOT NULL) THEN
        IF v_field_length < p_field_config.min_length THEN
          p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8014', p_field_config.field_name,
                           TO_CHAR(v_field_length), TO_CHAR(p_field_config.min_length));
          RETURN FALSE;
        END IF;
        IF v_field_length > p_field_config.max_length THEN
          p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', p_field_config.field_name,
                           TO_CHAR(v_field_length), TO_CHAR(p_field_config.max_length));
          RETURN FALSE;
        END IF;
      END IF;

      -- Check data type
      IF p_field_config.data_type IS NOT NULL THEN
        IF p_field_config.data_type = 'NUMBER' THEN
          BEGIN
            v_number_value := TO_NUMBER(p_field_value);
          EXCEPTION
            WHEN OTHERS THEN
              p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8016', p_field_config.field_name, p_field_value);
              RETURN FALSE;
          END;

          IF p_field_config.precision IS NOT NULL AND p_field_config.scale IS NOT NULL THEN
            v_decimal_pos := INSTR(p_field_value, '.');
            IF v_decimal_pos > 0 THEN
              v_integer_part   := SUBSTR(p_field_value, 1, v_decimal_pos - 1);
              v_decimal_part   := SUBSTR(p_field_value, v_decimal_pos + 1);
              v_integer_part   := LTRIM(LTRIM(v_integer_part, '0'), '-');
              IF v_integer_part IS NULL THEN v_integer_part := '0'; END IF;
              v_total_digits   := LENGTH(v_integer_part) + LENGTH(v_decimal_part);
              v_decimal_digits := LENGTH(v_decimal_part);
              IF v_decimal_digits > p_field_config.scale THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8017', p_field_config.field_name,
                                 TO_CHAR(v_decimal_digits), TO_CHAR(p_field_config.scale));
                RETURN FALSE;
              END IF;
              IF v_total_digits > p_field_config.precision THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8018', p_field_config.field_name,
                                 TO_CHAR(v_total_digits), TO_CHAR(p_field_config.precision));
                RETURN FALSE;
              END IF;
            ELSE
              v_integer_part := LTRIM(LTRIM(p_field_value, '0'), '-');
              IF v_integer_part IS NULL THEN v_integer_part := '0'; END IF;
              v_total_digits := LENGTH(v_integer_part);
              IF v_total_digits > (p_field_config.precision - p_field_config.scale) THEN
                p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8019', p_field_config.field_name,
                                 TO_CHAR(v_total_digits),
                                 TO_CHAR(p_field_config.precision - p_field_config.scale),
                                 TO_CHAR(p_field_config.precision), TO_CHAR(p_field_config.scale));
                RETURN FALSE;
              END IF;
            END IF;
          END IF;

        ELSIF p_field_config.data_type IN ('DATE', 'DATETIME') THEN
          BEGIN
            v_date_value := TO_DATE(p_field_value, p_field_config.fmt);
          EXCEPTION
            WHEN OTHERS THEN
              p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8020', p_field_config.field_name,
                               p_field_value, p_field_config.fmt);
              RETURN FALSE;
          END;
        END IF;
      END IF;

      -- Check pattern (already pre-processed — no REPLACE needed here)
      IF p_field_config.pattern IS NOT NULL THEN
        IF NOT REGEXP_LIKE(p_field_value, p_field_config.pattern) THEN
          IF p_field_config.pattern_error_code IS NOT NULL THEN
            p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR(p_field_config.pattern_error_code, p_field_value);
          ELSE
            p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8021', p_field_config.field_name,
                             p_field_value, p_field_config.pattern);
          END IF;
          RETURN FALSE;
        END IF;
      END IF;
    END IF;

    RETURN TRUE;
  EXCEPTION
    WHEN OTHERS THEN
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8022', p_field_config.field_name, SQLERRM);
      RETURN FALSE;
  END FN_VALIDATE_FIELD;

----------------------------------------------------------------------------------------------------
-- Build pre-processed field config cache from parsed JSON groups array
-- Call once before the line loop to eliminate all JSON parsing and REPLACE ops from the inner loop
----------------------------------------------------------------------------------------------------
  FUNCTION FN_BUILD_GROUP_CACHE(
    p_groups_array IN JSON_ARRAY_T
  ) RETURN t_field_config_cache IS
    v_cache        t_field_config_cache;
    v_group_obj    JSON_OBJECT_T;
    v_group_id     VARCHAR2(10);
    v_fields_arr   JSON_ARRAY_T;
    v_field_obj    JSON_OBJECT_T;
    v_fc           t_field_config;
    v_pattern      VARCHAR2(200);
  BEGIN
    FOR i IN 0 .. p_groups_array.get_size - 1 LOOP
      v_group_obj  := JSON_OBJECT_T(p_groups_array.get(i));
      v_group_id   := v_group_obj.get_String('groupId');
      v_fields_arr := JSON_ARRAY_T(v_group_obj.get('fields'));

      FOR j IN 0 .. v_fields_arr.get_size - 1 LOOP
        v_field_obj := JSON_OBJECT_T(v_fields_arr.get(j));

        v_fc.field_name         := v_field_obj.get_String('name');
        v_fc.mandatory          := v_field_obj.get_Boolean('mandatory');
        v_fc.min_length         := NVL(v_field_obj.get_Number('minLength'), 0);
        v_fc.max_length         := NVL(v_field_obj.get_Number('maxLength'), 32767);
        v_fc.data_type          := NULL;
        v_fc.pattern            := NULL;
        v_fc.pattern_error_code := NULL;
        v_fc.fmt                := NULL;
        v_fc.precision          := NULL;
        v_fc.scale              := NULL;
        v_fc.position           := v_field_obj.get_Number('position');

        IF v_field_obj.has('dataType') THEN
          v_fc.data_type := v_field_obj.get_String('dataType');
        END IF;

        IF v_field_obj.has('pattern') THEN
          v_pattern := v_field_obj.get_String('pattern');
          -- Resolve escape sequences once (avoids 6 REPLACEs per field per line)
          v_pattern := REPLACE(v_pattern, '\\d', '\d');
          v_pattern := REPLACE(v_pattern, '\\D', '\D');
          v_pattern := REPLACE(v_pattern, '\\w', '\w');
          v_pattern := REPLACE(v_pattern, '\\W', '\W');
          v_pattern := REPLACE(v_pattern, '\\s', '\s');
          v_pattern := REPLACE(v_pattern, '\\S', '\S');
          v_fc.pattern := v_pattern;
        END IF;

        IF v_field_obj.has('patternErrorCode') THEN
          v_fc.pattern_error_code := v_field_obj.get_String('patternErrorCode');
        END IF;

        IF v_field_obj.has('format') THEN
          v_fc.fmt := v_field_obj.get_String('format');
        END IF;

        IF v_field_obj.has('precision') THEN
          v_fc.precision := v_field_obj.get_Number('precision');
        END IF;

        IF v_field_obj.has('scale') THEN
          v_fc.scale := v_field_obj.get_Number('scale');
        END IF;

        -- Store with key: group_id || '~' || 0-based field index within group
        v_cache(v_group_id || '~' || TO_CHAR(j)) := v_fc;
      END LOOP;

      -- Store field count as sentinel (key: group_id || '~#') so the validate loop
      -- can use a bounded FOR loop instead of an EXISTS check on every iteration
      v_fc.position := v_fields_arr.get_size;
      v_cache(v_group_id || '~#') := v_fc;
    END LOOP;

    RETURN v_cache;
  END FN_BUILD_GROUP_CACHE;

----------------------------------------------------------------------------------------------------
-- Overload: Validate group line using pre-built config cache (no JSON, no REPLACE per line)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_GROUP_LINE(
    p_fields        IN PKG_DTC_COMMON.t_fields_array,
    p_group_id      IN VARCHAR2,
    p_group_cache   IN t_field_config_cache,
    p_line_number   IN NUMBER,
    p_errors        OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_valid        BOOLEAN := TRUE;
    v_fc           t_field_config;
    v_field_value  VARCHAR2(4000);
    v_error_msg    VARCHAR2(4000);
    v_cache_key    VARCHAR2(20);
    v_group_prefix VARCHAR2(15);   -- group_id || '~', computed once per call
    v_field_count  PLS_INTEGER;    -- number of fields for this group (from sentinel)
    v_part_idx     NUMBER;
  BEGIN
    -- Option B: p_errors NOT initialised here — ADD_ERROR does lazy init on first error,
    -- eliminating 408k nested-table allocations on the valid-line happy path.
    p_errors := NULL;

    -- Option C: use sentinel entry (key: group_id || '~#') to check group existence
    -- AND get field count in one lookup — avoids EXISTS check on every field iteration.
    v_cache_key := p_group_id || '~#';
    IF NOT p_group_cache.EXISTS(v_cache_key) THEN
      IF NVL(LENGTH(p_group_id), 0) = 0 THEN
        ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', 'groupId'), p_line_number, 'groupId', NULL,
          p_field_position => 1);
      ELSE
        ADD_ERROR(p_errors, 'UNKNOWN_GROUP',
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8027', p_group_id), p_line_number, 'groupId', p_group_id,
          p_field_position => 1);
      END IF;
      RETURN FALSE;
    END IF;

    v_field_count  := p_group_cache(v_cache_key).position;  -- field count stored here by FN_BUILD_GROUP_CACHE
    v_group_prefix := p_group_id || '~';                    -- compute once — saves one || per field in loop

    -- Validate each field using cache (no JSON, no REPLACE, no EXISTS per iteration)
    FOR v_idx IN 0 .. v_field_count - 1 LOOP
      v_fc       := p_group_cache(v_group_prefix || TO_CHAR(v_idx));
      v_part_idx := v_fc.position + 1;  -- +1: position 0 in JSON = field 1 in parsed line (0 is group ID)

      IF p_fields.EXISTS(v_part_idx) THEN
        v_field_value := p_fields(v_part_idx);
      ELSE
        v_field_value := NULL;
      END IF;

      IF NOT FN_VALIDATE_FIELD(v_field_value, v_fc, v_error_msg) THEN
        IF NVL(LENGTH(v_field_value), 0) = 0 THEN
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8044', v_fc.field_name),
            p_line_number, v_fc.field_name, v_field_value,
            p_field_position => v_part_idx);
        ELSE
          ADD_ERROR(p_errors, C_ERR_DATA_FIELD_MANDATORY, v_error_msg,
            p_line_number, v_fc.field_name, v_field_value,
            p_field_position => v_part_idx);
        END IF;
        v_valid := FALSE;
      END IF;

    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'GROUP_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8028', p_group_id, SQLERRM),
        p_line_number, 'groupId', p_group_id, p_field_position => 1);
      RETURN FALSE;
  END FN_VALIDATE_GROUP_LINE;

----------------------------------------------------------------------------------------------------
-- Validate entire file (ORIGINAL - V1)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_FILE(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config_json     CLOB;
    v_lines           DBMS_SQL.VARCHAR2A;
    v_header_errors   t_validation_errors;
    v_footer_errors   t_validation_errors;
    v_valid           BOOLEAN := TRUE;
    v_record_count    NUMBER := 0;
    v_group_id        VARCHAR2(10);
  BEGIN
    p_errors := t_validation_errors();

    -- Get active config
    v_config_json := FN_GET_ACTIVE_CONFIG(p_flow_type);
    IF v_config_json IS NULL THEN
      ADD_ERROR(p_errors, C_ERR_CONFIG_NOT_FOUND,
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8003', p_flow_type), NULL, 'flowType', p_flow_type);
      RETURN FALSE;
    END IF;

    -- Split file into lines
    v_lines := PKG_DTC_COMMON.FN_SPLIT_FILE_LINES(p_file_content);

    IF v_lines.COUNT = 0 THEN
      ADD_ERROR(p_errors, 'FILE_EMPTY', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8036'), NULL, 'fileContent');
      RETURN FALSE;
    END IF;

    -- Validate header (first line)
    IF NOT FN_VALIDATE_HEADER(v_lines(1), v_config_json, v_header_errors) THEN
      v_valid := FALSE;
      IF v_header_errors IS NOT NULL THEN
        FOR i IN 1 .. v_header_errors.COUNT LOOP
          p_errors.EXTEND;
          p_errors(p_errors.COUNT) := v_header_errors(i);
        END LOOP;
      END IF;
    END IF;

    -- Count data records (excluding header and footer)
    v_record_count := v_lines.COUNT - 2;

    -- Validate each data line (between header and footer)
    FOR i IN 2 .. v_lines.COUNT - 1 LOOP
      v_group_id := PKG_DTC_COMMON.FN_GET_GROUP_ID(v_lines(i));

      IF NOT FN_VALIDATE_GROUP_LINE(v_lines(i), v_group_id, v_config_json, i, v_header_errors) THEN
        v_valid := FALSE;
        IF v_header_errors IS NOT NULL THEN
          FOR j IN 1 .. v_header_errors.COUNT LOOP
            p_errors.EXTEND;
            p_errors(p_errors.COUNT) := v_header_errors(j);
          END LOOP;
        END IF;
      END IF;
    END LOOP;

    -- Validate footer (last line)
    IF NOT FN_VALIDATE_FOOTER(v_lines(v_lines.COUNT), v_config_json, v_record_count, v_footer_errors) THEN
      v_valid := FALSE;
      IF v_footer_errors IS NOT NULL THEN
        FOR i IN 1 .. v_footer_errors.COUNT LOOP
          p_errors.EXTEND;
          p_errors(p_errors.COUNT) := v_footer_errors(i);
        END LOOP;
      END IF;
    END IF;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'FILE_VALIDATION_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8037', SQLERRM), NULL, 'file');
      RETURN FALSE;
  END FN_VALIDATE_FILE;

----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
-- NEW FUNCTIONS FOR VERSION 2 - TWO-STAGE VALIDATION
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
-- Parse header line and extract all fields (V2)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_PARSE_HEADER(
    p_header_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_header_data  OUT t_header_data,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config       JSON_OBJECT_T;
    v_header_config JSON_OBJECT_T;
    v_header_parts DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_valid        BOOLEAN := TRUE;
    v_header_id    VARCHAR2(10);
    -- Field name and maxLength lookup from config (indexed by config position)
    v_fields_array JSON_ARRAY_T;
    v_field_obj    JSON_OBJECT_T;
    v_field_names  DBMS_SQL.VARCHAR2A;  -- position -> name
    v_field_max    DBMS_SQL.VARCHAR2A;  -- position -> maxLength as string
    v_cfg_pos      NUMBER;
  BEGIN
    p_errors := t_validation_errors();

    -- Parse JSON config
    v_config := JSON_OBJECT_T(p_config_json);
    v_header_config := JSON_OBJECT_T(v_config.get('header'));
    v_header_id := v_header_config.get_String('identifier');

    -- Build field name and maxLength lookup from config
    v_fields_array := JSON_ARRAY_T(v_header_config.get('fields'));
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_obj := JSON_OBJECT_T(v_fields_array.get(i));
      v_cfg_pos := v_field_obj.get_Number('position');
      v_field_names(v_cfg_pos) := v_field_obj.get_String('name');
      v_field_max(v_cfg_pos) := TO_CHAR(v_field_obj.get_Number('maxLength'));
    END LOOP;

    -- Split header line by delimiter
    WHILE v_pos <= LENGTH(p_header_line) LOOP
      v_next_pos := INSTR(p_header_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_header_line) + 1;
      END IF;

      v_header_parts(v_part_idx) := SUBSTR(p_header_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate header identifier (use NVL to handle Oracle NULL = empty string)
    IF NVL(v_header_parts(1), ' ') != v_header_id THEN
      IF NVL(LENGTH(v_header_parts(1)), 0) = 0 THEN
        -- Empty/null identifier - trigger mandatory validation
        ADD_ERROR(p_errors, C_ERR_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8013', 'headerIdentifier'),
          1, 'headerIdentifier', v_header_parts(1),
          p_field_position => 1);
        v_valid := FALSE;
      ELSE
        -- Non-empty but wrong identifier - file is invalid
        ADD_ERROR(p_errors, C_ERR_HEADER_MISSING,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8007', v_header_id, v_header_parts(1)),
          1, 'headerIdentifier', v_header_parts(1),
          p_field_position => 1);
        RETURN FALSE;
      END IF;
    END IF;

    -- Extract header fields (positions are 1-based, but position 1 is the identifier)
    -- Config position + 1 = header_parts index (position 1 in config = header_parts(2))
    -- Each assignment is wrapped to catch buffer overflow and report a proper validation error

    -- Config position 1: File Identifier -> header_parts(2)
    BEGIN
      p_header_data.file_identifier := v_header_parts(2);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(1), TO_CHAR(LENGTH(v_header_parts(2))), v_field_max(1)), 1, v_field_names(1), v_header_parts(2),
          p_field_position => 2);
        v_valid := FALSE;
    END;

    -- Config position 2: Flow Name -> header_parts(3)
    BEGIN
      p_header_data.flow_name := v_header_parts(3);

      -- Extract flow type and version from flow name
      IF LENGTH(p_header_data.flow_name) >= 5 THEN
        p_header_data.flow_type := SUBSTR(p_header_data.flow_name, 1, 5);
        p_header_data.flow_version := SUBSTR(p_header_data.flow_name, 6, 3);
      END IF;
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(2), TO_CHAR(LENGTH(v_header_parts(3))), v_field_max(2)), 1, v_field_names(2), v_header_parts(3),
          p_field_position => 3);
        v_valid := FALSE;
    END;

    -- Config position 3: Sender Role -> header_parts(4)
    BEGIN
      p_header_data.src_mp_role := v_header_parts(4);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(3), TO_CHAR(LENGTH(v_header_parts(4))), v_field_max(3)), 1, v_field_names(3), v_header_parts(4),
          p_field_position => 4);
        v_valid := FALSE;
    END;

    -- Config position 4: Sender ID -> header_parts(5)
    BEGIN
      p_header_data.src_mp_id := v_header_parts(5);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(4), TO_CHAR(LENGTH(v_header_parts(5))), v_field_max(4)), 1, v_field_names(4), v_header_parts(5),
          p_field_position => 5);
        v_valid := FALSE;
    END;

    -- Config position 5: Recipient Role -> header_parts(6)
    BEGIN
      p_header_data.dstn_mp_role := v_header_parts(6);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(5), TO_CHAR(LENGTH(v_header_parts(6))), v_field_max(5)), 1, v_field_names(5), v_header_parts(6),
          p_field_position => 6);
        v_valid := FALSE;
    END;

    -- Config position 6: Recipient ID -> header_parts(7)
    BEGIN
      p_header_data.dstn_mp_id := v_header_parts(7);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(6), TO_CHAR(LENGTH(v_header_parts(7))), v_field_max(6)), 1, v_field_names(6), v_header_parts(7),
          p_field_position => 7);
        v_valid := FALSE;
    END;

    -- Config position 7: Timestamp -> header_parts(8)
    BEGIN
      p_header_data.data_timestamp := v_header_parts(8);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(7), TO_CHAR(LENGTH(v_header_parts(8))), v_field_max(7)), 1, v_field_names(7), v_header_parts(8),
          p_field_position => 8);
        v_valid := FALSE;
    END;

    -- Convert timestamp to DATE
    BEGIN
      IF LENGTH(p_header_data.data_timestamp) = 14 THEN
        p_header_data.data_dt := TO_DATE(p_header_data.data_timestamp, 'YYYYMMDDHH24MISS');
      END IF;
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_DATATYPE,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8023', p_header_data.data_timestamp), 1, 'dataTimestamp', p_header_data.data_timestamp,
          p_field_position => 8);
        v_valid := FALSE;
    END;

    -- Field 12: Network ID (fields 9-11 are typically empty, not in config)
    IF v_header_parts.EXISTS(12) THEN
      BEGIN
        p_header_data.network_id := v_header_parts(12);
      EXCEPTION
        WHEN OTHERS THEN
          ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', 'networkId', TO_CHAR(LENGTH(v_header_parts(12))), '10'), 1, 'networkId', v_header_parts(12),
            p_field_position => 12);
          v_valid := FALSE;
      END;
    END IF;

    -- Field 10: Input/Output Indicator (optional, not in config)
    IF v_header_parts.EXISTS(10) AND LENGTH(v_header_parts(10)) > 0 THEN
      BEGIN
        p_header_data.inp_out_ind := v_header_parts(10);
      EXCEPTION
        WHEN OTHERS THEN
          ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', 'inputOutputIndicator', TO_CHAR(LENGTH(v_header_parts(10))), '2'), 1, 'inputOutputIndicator', v_header_parts(10),
            p_field_position => 10);
          v_valid := FALSE;
      END;
    END IF;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'HEADER_PARSE_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8011', SQLERRM), 1, 'header');
      RETURN FALSE;
  END FN_PARSE_HEADER;

----------------------------------------------------------------------------------------------------
-- Parse footer line and extract all fields (V2)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_PARSE_FOOTER(
    p_footer_line  IN VARCHAR2,
    p_config_json  IN CLOB,
    p_footer_data  OUT t_footer_data,
    p_errors       OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config       JSON_OBJECT_T;
    v_footer_config JSON_OBJECT_T;
    v_footer_parts DBMS_SQL.VARCHAR2A;
    v_part_idx     NUMBER := 1;
    v_pos          NUMBER := 1;
    v_next_pos     NUMBER;
    v_valid        BOOLEAN := TRUE;
    v_footer_id    VARCHAR2(10);
    -- Field name and maxLength lookup from config (indexed by config position)
    v_fields_array JSON_ARRAY_T;
    v_field_obj    JSON_OBJECT_T;
    v_field_names  DBMS_SQL.VARCHAR2A;  -- position -> name
    v_field_max    DBMS_SQL.VARCHAR2A;  -- position -> maxLength as string
    v_cfg_pos      NUMBER;
  BEGIN
    p_errors := t_validation_errors();

    -- Parse JSON config
    v_config := JSON_OBJECT_T(p_config_json);
    v_footer_config := JSON_OBJECT_T(v_config.get('footer'));
    v_footer_id := v_footer_config.get_String('identifier');

    -- Build field name and maxLength lookup from config
    v_fields_array := JSON_ARRAY_T(v_footer_config.get('fields'));
    FOR i IN 0 .. v_fields_array.get_size - 1 LOOP
      v_field_obj := JSON_OBJECT_T(v_fields_array.get(i));
      v_cfg_pos := v_field_obj.get_Number('position');
      v_field_names(v_cfg_pos) := v_field_obj.get_String('name');
      v_field_max(v_cfg_pos) := TO_CHAR(v_field_obj.get_Number('maxLength'));
    END LOOP;

    -- Split footer line by delimiter
    WHILE v_pos <= LENGTH(p_footer_line) LOOP
      v_next_pos := INSTR(p_footer_line, PKG_DTC_COMMON.C_DELIMITER, v_pos);
      IF v_next_pos = 0 THEN
        v_next_pos := LENGTH(p_footer_line) + 1;
      END IF;

      v_footer_parts(v_part_idx) := SUBSTR(p_footer_line, v_pos, v_next_pos - v_pos);
      v_part_idx := v_part_idx + 1;
      v_pos := v_next_pos + 1;
    END LOOP;

    -- Validate footer identifier (use NVL to handle Oracle NULL = empty string)
    IF NVL(v_footer_parts(1), ' ') != v_footer_id THEN
      IF NVL(LENGTH(v_footer_parts(1)), 0) = 0 THEN
        -- Empty/null identifier - trigger mandatory validation
        ADD_ERROR(p_errors, C_ERR_FOOTER_FIELD_MANDATORY,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8043', 'footerIdentifier'),
          NULL, 'footerIdentifier', v_footer_parts(1),
          p_field_position => 1);
        v_valid := FALSE;
      ELSE
        -- Non-empty but wrong identifier - file is invalid
        ADD_ERROR(p_errors, C_ERR_FOOTER_MISSING,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8008', v_footer_id, v_footer_parts(1)),
          NULL, 'footerIdentifier', v_footer_parts(1),
          p_field_position => 1);
        RETURN FALSE;
      END IF;
    END IF;

    -- Extract footer fields (6 fields: ZPT|file_id|rec_count|checksum|flow_count|timestamp)
    -- Config position + 1 = footer_parts index (position 1 in config = footer_parts(2))
    -- Each assignment is wrapped to catch buffer overflow and report a proper validation error

    -- Config position 1: File Identifier -> footer_parts(2)
    BEGIN
      p_footer_data.file_identifier := v_footer_parts(2);
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(1), TO_CHAR(LENGTH(v_footer_parts(2))), v_field_max(1)), NULL, v_field_names(1), v_footer_parts(2),
          p_field_position => 2);
        v_valid := FALSE;
    END;

    -- Config position 2: Record Count -> footer_parts(3)
    BEGIN
      p_footer_data.record_count := TO_NUMBER(v_footer_parts(3));
    EXCEPTION
      WHEN OTHERS THEN
        ADD_ERROR(p_errors, C_ERR_FIELD_DATATYPE,
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8026', v_footer_parts(3)), NULL, v_field_names(2), v_footer_parts(3),
          p_field_position => 3);
        v_valid := FALSE;
    END;

    -- Field 4: Checksum (optional, not in config)
    IF v_footer_parts.EXISTS(4) THEN
      BEGIN
        p_footer_data.checksum := v_footer_parts(4);
      EXCEPTION
        WHEN OTHERS THEN
          ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', 'checksum', TO_CHAR(LENGTH(v_footer_parts(4))), '20'), NULL, 'checksum', v_footer_parts(4),
            p_field_position => 4);
          v_valid := FALSE;
      END;
    END IF;

    -- Config position 4: Flow Count -> footer_parts(5)
    IF v_footer_parts.EXISTS(5) AND v_footer_parts(5) IS NOT NULL AND LENGTH(TRIM(v_footer_parts(5))) > 0 THEN
      BEGIN
        p_footer_data.flow_count := TO_NUMBER(v_footer_parts(5));
      EXCEPTION
        WHEN OTHERS THEN
          ADD_ERROR(p_errors, C_ERR_FIELD_DATATYPE,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8034', v_footer_parts(5)), NULL, v_field_names(4), v_footer_parts(5),
            p_field_position => 5);
          v_valid := FALSE;
      END;
    ELSE
      p_footer_data.flow_count := NULL;
    END IF;

    -- Config position 5: Timestamp -> footer_parts(6)
    IF v_footer_parts.EXISTS(6) THEN
      BEGIN
        p_footer_data.data_timestamp := v_footer_parts(6);
      EXCEPTION
        WHEN OTHERS THEN
          ADD_ERROR(p_errors, C_ERR_FIELD_LENGTH,
            PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', v_field_names(5), TO_CHAR(LENGTH(v_footer_parts(6))), v_field_max(5)), NULL, v_field_names(5), v_footer_parts(6),
            p_field_position => 6);
          v_valid := FALSE;
      END;
    END IF;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'FOOTER_PARSE_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8012', SQLERRM), NULL, 'footer');
      RETURN FALSE;
  END FN_PARSE_FOOTER;

----------------------------------------------------------------------------------------------------
-- Stage 1 Validation: File-level validation (critical - must pass) (V2)
-- Validates: header format, footer format, record count, parent group existence
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_STAGE1(
    p_lines           IN DBMS_SQL.VARCHAR2A,
    p_config_json     IN CLOB,
    p_flow_type       IN VARCHAR2,
    p_header_data     OUT t_header_data,
    p_footer_data     OUT t_footer_data,
    p_total_rec_count OUT NUMBER,
    p_total_flow_count OUT NUMBER,
    p_errors          OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_header_errors   t_validation_errors;
    v_footer_errors   t_validation_errors;
    v_valid           BOOLEAN := TRUE;
    v_actual_rec_count NUMBER := 0;
    v_parent_group_id VARCHAR2(10);
    v_parent_count    NUMBER := 0;
    v_group_id        VARCHAR2(10);
    v_config          JSON_OBJECT_T;
    v_groups_array    JSON_ARRAY_T;
    v_group_config    JSON_OBJECT_T;
    i                 NUMBER;
  BEGIN
    p_errors := t_validation_errors();

    -- 1. Parse and validate header
    IF NOT FN_PARSE_HEADER(p_lines(1), p_config_json, p_header_data, v_header_errors) THEN
      v_valid := FALSE;
      IF v_header_errors IS NOT NULL THEN
        FOR i IN 1 .. v_header_errors.COUNT LOOP
          p_errors.EXTEND;
          p_errors(p_errors.COUNT) := v_header_errors(i);
        END LOOP;
      END IF;
    ELSE
      -- 1b. Validate header mandatory fields against config (only if parse succeeded)
      IF NOT FN_VALIDATE_HEADER(p_lines(1), p_config_json, v_header_errors) THEN
        v_valid := FALSE;
        IF v_header_errors IS NOT NULL THEN
          FOR i IN 1 .. v_header_errors.COUNT LOOP
            p_errors.EXTEND;
            p_errors(p_errors.COUNT) := v_header_errors(i);
          END LOOP;
        END IF;
      END IF;
    END IF;

    -- 2. Calculate actual record count (all data lines, excluding header and footer)
    v_actual_rec_count := p_lines.COUNT - 2;
    p_total_rec_count := v_actual_rec_count;

    -- 3. Determine parent group ID for this flow type
    v_config := JSON_OBJECT_T(p_config_json);
    v_groups_array := JSON_ARRAY_T(v_config.get('groups'));

    FOR i IN 0 .. v_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(v_groups_array.get(i));
      -- Parent group has parentGroup = null (JSON null, not SQL NULL)
      IF v_group_config.has('parentGroup') THEN
        BEGIN
          IF v_group_config.get_String('parentGroup') IS NULL THEN
            v_parent_group_id := v_group_config.get_String('groupId');
            EXIT;
          END IF;
        EXCEPTION
          WHEN OTHERS THEN
            -- get_String throws error for JSON null, so this group is the parent
            v_parent_group_id := v_group_config.get_String('groupId');
            EXIT;
        END;
      END IF;
    END LOOP;

    -- 4. Count parent groups in file
    v_parent_count := 0;
    FOR i IN 2 .. p_lines.COUNT - 1 LOOP
      v_group_id := PKG_DTC_COMMON.FN_GET_GROUP_ID(p_lines(i));
      IF v_group_id = v_parent_group_id THEN
        v_parent_count := v_parent_count + 1;
      END IF;
    END LOOP;

    p_total_flow_count := v_parent_count;

    -- 5. Validate parent group exists
    IF v_parent_count = 0 THEN
      ADD_ERROR(p_errors, C_ERR_GROUP_MIN_OCC,
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8029', v_parent_group_id), NULL, 'parentGroupId', v_parent_group_id);
      v_valid := FALSE;
    END IF;

    -- 6. Parse and validate footer
    IF NOT FN_PARSE_FOOTER(p_lines(p_lines.COUNT), p_config_json, p_footer_data, v_footer_errors) THEN
      v_valid := FALSE;
      IF v_footer_errors IS NOT NULL THEN
        FOR i IN 1 .. v_footer_errors.COUNT LOOP
          v_footer_errors(i).line_number := p_lines.COUNT;
          p_errors.EXTEND;
          p_errors(p_errors.COUNT) := v_footer_errors(i);
        END LOOP;
      END IF;
    END IF;

    -- 6b. Always validate footer fields against config (even if parse had errors)
    -- Skip validation errors for fields that already have parse errors to avoid duplicates
    v_footer_errors := t_validation_errors();
    IF NOT FN_VALIDATE_FOOTER(p_lines(p_lines.COUNT), p_config_json, v_actual_rec_count, v_footer_errors) THEN
      v_valid := FALSE;
      IF v_footer_errors IS NOT NULL THEN
        FOR i IN 1 .. v_footer_errors.COUNT LOOP
          v_footer_errors(i).line_number := p_lines.COUNT;
          -- Check if this field already has a parse error
          DECLARE
            v_duplicate BOOLEAN := FALSE;
          BEGIN
            FOR j IN 1 .. p_errors.COUNT LOOP
              IF p_errors(j).field_name = v_footer_errors(i).field_name AND p_errors(j).line_number = v_footer_errors(i).line_number THEN
                v_duplicate := TRUE;
                EXIT;
              END IF;
            END LOOP;
            IF NOT v_duplicate THEN
              p_errors.EXTEND;
              p_errors(p_errors.COUNT) := v_footer_errors(i);
            END IF;
          END;
        END LOOP;
      END IF;
    END IF;

    -- 7. Record count validation is already handled by FN_VALIDATE_FOOTER at step 6b
    --    (removed duplicate check to prevent duplicate ERR8024 in MDQ_ETL_ERROR)

    -- 8. Validate flow count matches footer (if provided)
    IF p_footer_data.flow_count IS NOT NULL THEN
      IF p_footer_data.flow_count != v_parent_count THEN
        ADD_ERROR(p_errors, 'FLOW_COUNT_MISMATCH',
          PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8033', TO_CHAR(v_parent_count), TO_CHAR(p_footer_data.flow_count)),
          p_lines.COUNT, 'flowCount', TO_CHAR(p_footer_data.flow_count),
          p_field_position => 5);
        v_valid := FALSE;
      END IF;
    END IF;

    -- 9. Validate file identifiers match between header and footer
    IF p_header_data.file_identifier != p_footer_data.file_identifier THEN
      ADD_ERROR(p_errors, 'FILE_ID_MISMATCH',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8035', p_header_data.file_identifier, p_footer_data.file_identifier),
        p_lines.COUNT, 'fileIdentifier', p_footer_data.file_identifier,
        p_field_position => 2);
      v_valid := FALSE;
    END IF;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'STAGE1_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8039', SQLERRM), NULL, 'stage1Validation');
      RETURN FALSE;
  END FN_VALIDATE_STAGE1;

----------------------------------------------------------------------------------------------------
-- Validate group occurrences against minOccurrences and maxOccurrences constraints
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_GROUP_OCCURRENCES(
    p_parent_group_id    IN VARCHAR2,
    p_parent_line_number IN NUMBER,
    p_group_counts       IN VARCHAR2, -- Format: "groupId:count,groupId:count,..."
    p_config_json        IN CLOB,
    p_errors             OUT t_validation_errors
  ) RETURN BOOLEAN IS
    v_config          JSON_OBJECT_T;
    v_groups_array    JSON_ARRAY_T;
    v_group_config    JSON_OBJECT_T;
    v_group_id        VARCHAR2(10);
    v_parent_group    VARCHAR2(10);
    v_min_occ         NUMBER;
    v_max_occ         NUMBER;
    v_actual_count    NUMBER;
    v_valid           BOOLEAN := TRUE;
    v_count_str       VARCHAR2(4000);
    v_pos             NUMBER;
    v_next_pos        NUMBER;
    v_pair            VARCHAR2(100);
    v_colon_pos       NUMBER;
    v_curr_group_id   VARCHAR2(10);
    v_curr_count      NUMBER;
    TYPE t_group_count_map IS TABLE OF NUMBER INDEX BY VARCHAR2(10);
    v_group_count_map t_group_count_map;
  BEGIN
    p_errors := t_validation_errors();

    -- Parse the group counts string into a map
    v_count_str := p_group_counts;
    IF v_count_str IS NOT NULL AND LENGTH(v_count_str) > 0 THEN
      v_pos := 1;
      WHILE v_pos <= LENGTH(v_count_str) LOOP
        v_next_pos := INSTR(v_count_str, ',', v_pos);
        IF v_next_pos = 0 THEN
          v_next_pos := LENGTH(v_count_str) + 1;
        END IF;

        v_pair := SUBSTR(v_count_str, v_pos, v_next_pos - v_pos);
        v_colon_pos := INSTR(v_pair, ':');

        IF v_colon_pos > 0 THEN
          v_curr_group_id := SUBSTR(v_pair, 1, v_colon_pos - 1);
          v_curr_count := TO_NUMBER(SUBSTR(v_pair, v_colon_pos + 1));
          v_group_count_map(v_curr_group_id) := v_curr_count;
        END IF;

        v_pos := v_next_pos + 1;
      END LOOP;
    END IF;

    -- Parse config and get groups array
    v_config := JSON_OBJECT_T(p_config_json);
    v_groups_array := JSON_ARRAY_T(v_config.get('groups'));

    -- Check each child group's occurrences
    FOR i IN 0 .. v_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(v_groups_array.get(i));
      v_group_id := v_group_config.get_String('groupId');

      -- Check if this group is a child of the current parent
      IF v_group_config.has('parentGroup') THEN
        BEGIN
          v_parent_group := v_group_config.get_String('parentGroup');
        EXCEPTION
          WHEN OTHERS THEN
            v_parent_group := NULL;
        END;

        -- Only validate children of current parent
        IF v_parent_group = p_parent_group_id THEN
          -- Get min and max occurrences from config
          v_min_occ := NULL;
          v_max_occ := NULL;

          IF v_group_config.has('minOccurrences') THEN
            BEGIN
              v_min_occ := v_group_config.get_Number('minOccurrences');
            EXCEPTION
              WHEN OTHERS THEN
                v_min_occ := NULL;
            END;
          END IF;

          IF v_group_config.has('maxOccurrences') THEN
            BEGIN
              v_max_occ := v_group_config.get_Number('maxOccurrences');
            EXCEPTION
              WHEN OTHERS THEN
                v_max_occ := NULL;
            END;
          END IF;

          -- Get actual count (default to 0 if group not found)
          IF v_group_count_map.EXISTS(v_group_id) THEN
            v_actual_count := v_group_count_map(v_group_id);
          ELSE
            v_actual_count := 0;
          END IF;

          -- Validate minimum occurrences
          IF v_min_occ IS NOT NULL AND v_actual_count < v_min_occ THEN
            ADD_ERROR(p_errors, C_ERR_GROUP_MIN_OCC,
              PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8030', v_group_id, TO_CHAR(v_actual_count),
                             TO_CHAR(v_min_occ), p_parent_group_id),
              p_parent_line_number, 'groupId', v_group_id);
            v_valid := FALSE;
          END IF;

          -- Validate maximum occurrences (NULL means unlimited)
          IF v_max_occ IS NOT NULL AND v_actual_count > v_max_occ THEN
            ADD_ERROR(p_errors, C_ERR_GROUP_MAX_OCC,
              PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8031', v_group_id, TO_CHAR(v_actual_count),
                             TO_CHAR(v_max_occ), p_parent_group_id),
              p_parent_line_number, 'groupId', v_group_id);
            v_valid := FALSE;
          END IF;
        END IF;
      END IF;
    END LOOP;

    RETURN v_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'OCC_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8032', SQLERRM), p_parent_line_number, 'groupOccurrences',
          p_field_position => 1);
      RETURN FALSE;
  END FN_VALIDATE_GROUP_OCCURRENCES;


----------------------------------------------------------------------------------------------------
-- Stage 2 Validation: Group-level validation (partial rejection allowed) (V2 - SIMPLIFIED)
-- Validates field-level only. Tracks parent groups and marks them valid/invalid.
----------------------------------------------------------------------------------------------------
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
  ) RETURN BOOLEAN IS
    v_config              JSON_OBJECT_T;
    v_groups_array        JSON_ARRAY_T;
    v_group_config        JSON_OBJECT_T;
    v_parent_group_id     VARCHAR2(10);
    v_group_id            VARCHAR2(10);
    v_line_errors         t_validation_errors;
    v_current_parent_line NUMBER := NULL;
    v_current_parent_valid BOOLEAN := TRUE;
    v_current_parent_lines NUMBER := 0;
    v_overall_valid       BOOLEAN := TRUE;
    v_group_range         t_parent_group_range;
  BEGIN
    p_errors := t_validation_errors();
    p_parent_groups := t_parent_group_ranges();
    p_staged_rec_count := 0;
    p_staged_flow_count := 0;
    p_rejected_rec_count := 0;
    p_rejected_flow_count := 0;

    -- Find parent group ID (the one with parentGroup = null)
    v_config := JSON_OBJECT_T(p_config_json);
    v_groups_array := JSON_ARRAY_T(v_config.get('groups'));

    FOR i IN 0 .. v_groups_array.get_size - 1 LOOP
      v_group_config := JSON_OBJECT_T(v_groups_array.get(i));
      IF v_group_config.has('parentGroup') THEN
        BEGIN
          IF v_group_config.get_String('parentGroup') IS NULL THEN
            v_parent_group_id := v_group_config.get_String('groupId');
            EXIT;
          END IF;
        EXCEPTION
          WHEN OTHERS THEN
            v_parent_group_id := v_group_config.get_String('groupId');
            EXIT;
        END;
      END IF;
    END LOOP;

    -- Process each data line
    FOR i IN 2 .. p_lines.COUNT - 1 LOOP
      v_group_id := PKG_DTC_COMMON.FN_GET_GROUP_ID(p_lines(i));

      -- Detect new parent group
      IF v_group_id = v_parent_group_id THEN
        -- Finalize previous parent group (if exists)
        IF v_current_parent_line IS NOT NULL THEN
          -- Update counts
          IF v_current_parent_valid THEN
            p_staged_flow_count := p_staged_flow_count + 1;
            p_staged_rec_count := p_staged_rec_count + v_current_parent_lines;
          ELSE
            p_rejected_flow_count := p_rejected_flow_count + 1;
            p_rejected_rec_count := p_rejected_rec_count + v_current_parent_lines;
          END IF;

          -- Record parent group range
          v_group_range.parent_group_id := v_parent_group_id;
          v_group_range.start_line := v_current_parent_line;
          v_group_range.end_line := i - 1;
          v_group_range.is_valid := v_current_parent_valid;
          p_parent_groups.EXTEND;
          p_parent_groups(p_parent_groups.COUNT) := v_group_range;
        END IF;

        -- Start new parent group
        v_current_parent_line := i;
        v_current_parent_valid := TRUE;
        v_current_parent_lines := 1;
      ELSE
        -- Child line - increment counter
        v_current_parent_lines := v_current_parent_lines + 1;
      END IF;

      -- Validate this line's fields (pass pre-parsed groups array to avoid JSON re-parse per line)
      IF NOT FN_VALIDATE_GROUP_LINE(p_lines(i), v_group_id, v_groups_array, i, v_line_errors) THEN
        v_current_parent_valid := FALSE;
        v_overall_valid := FALSE;

        -- Add errors
        IF v_line_errors IS NOT NULL THEN
          FOR j IN 1 .. v_line_errors.COUNT LOOP
            v_line_errors(j).group_id := v_group_id;
            p_errors.EXTEND;
            p_errors(p_errors.COUNT) := v_line_errors(j);
          END LOOP;
        END IF;
      END IF;
    END LOOP;

    -- Finalize last parent group
    IF v_current_parent_line IS NOT NULL THEN
      -- Update counts
      IF v_current_parent_valid THEN
        p_staged_flow_count := p_staged_flow_count + 1;
        p_staged_rec_count := p_staged_rec_count + v_current_parent_lines;
      ELSE
        p_rejected_flow_count := p_rejected_flow_count + 1;
        p_rejected_rec_count := p_rejected_rec_count + v_current_parent_lines;
      END IF;

      -- Record parent group range
      v_group_range.parent_group_id := v_parent_group_id;
      v_group_range.start_line := v_current_parent_line;
      v_group_range.end_line := p_lines.COUNT - 1;
      v_group_range.is_valid := v_current_parent_valid;
      p_parent_groups.EXTEND;
      p_parent_groups(p_parent_groups.COUNT) := v_group_range;
    END IF;

    RETURN v_overall_valid;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_errors, 'STAGE2_ERROR', PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8040', SQLERRM), NULL, 'stage2Validation');
      RETURN FALSE;
  END FN_VALIDATE_STAGE2;

----------------------------------------------------------------------------------------------------
-- Main two-stage validation function (V2)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_VALIDATE_FILE_V2(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT t_file_validation_result,
    p_lines        OUT DBMS_SQL.VARCHAR2A
  ) RETURN BOOLEAN IS
    v_config_json     CLOB;
    v_lines           DBMS_SQL.VARCHAR2A;
    v_stage1_errors   t_validation_errors;
    v_stage2_errors   t_validation_errors;
    v_stage2_passed   BOOLEAN := TRUE;
  BEGIN
    -- Initialize result
    p_result.errors := t_validation_errors();
    p_result.parent_groups := t_parent_group_ranges();
    p_result.stage1_passed := FALSE;
    p_result.status := 'REJECTED';

    -- Get active config
    v_config_json := FN_GET_ACTIVE_CONFIG(p_flow_type);
    IF v_config_json IS NULL THEN
      ADD_ERROR(p_result.errors, C_ERR_CONFIG_NOT_FOUND,
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8003', p_flow_type), NULL, 'flowType', p_flow_type);
      RETURN FALSE;
    END IF;

    -- Split file into lines (once — returned to caller to avoid re-splitting in flow packages)
    v_lines := PKG_DTC_COMMON.FN_SPLIT_FILE_LINES(p_file_content);
    p_lines := v_lines;

    IF v_lines.COUNT < 3 THEN
      ADD_ERROR(p_result.errors, 'FILE_TOO_SHORT',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8004'), NULL, 'fileContent');
      RETURN FALSE;
    END IF;

    -- STAGE 1: File-level validation (critical)
    p_result.stage1_passed := FN_VALIDATE_STAGE1(
      v_lines,
      v_config_json,
      p_flow_type,
      p_result.header_data,
      p_result.footer_data,
      p_result.total_rec_count,
      p_result.total_flow_count,
      v_stage1_errors
    );

    -- Merge Stage 1 errors
    IF v_stage1_errors IS NOT NULL THEN
      FOR i IN 1 .. v_stage1_errors.COUNT LOOP
        p_result.errors.EXTEND;
        p_result.errors(p_result.errors.COUNT) := v_stage1_errors(i);
      END LOOP;
    END IF;

    -- STAGE 2: Group-level validation (always run to collect all errors)
    v_stage2_passed := FN_VALIDATE_STAGE2(
      v_lines,
      v_config_json,
      p_flow_type,
      p_result.staged_rec_count,
      p_result.staged_flow_count,
      p_result.rejected_rec_count,
      p_result.rejected_flow_count,
      p_result.parent_groups,
      v_stage2_errors
    );

    -- Merge Stage 2 errors
    IF v_stage2_errors IS NOT NULL THEN
      FOR i IN 1 .. v_stage2_errors.COUNT LOOP
        p_result.errors.EXTEND;
        p_result.errors(p_result.errors.COUNT) := v_stage2_errors(i);
      END LOOP;
    END IF;

    -- Determine final status
    IF NOT p_result.stage1_passed THEN
      -- Stage 1 failed - File is always REJECTED
      p_result.status := 'REJECTED';
      p_result.staged_rec_count := 0;
      p_result.staged_flow_count := 0;
      p_result.rejected_rec_count := p_result.total_rec_count;
      p_result.rejected_flow_count := p_result.total_flow_count;
      p_result.error_rec_count := p_result.total_rec_count;
      p_result.error_flow_count := p_result.total_flow_count;
      RETURN FALSE;
    ELSIF NOT v_stage2_passed THEN
      -- Stage 2 had some failures - check if any flows were actually staged
      IF p_result.staged_flow_count > 0 THEN
        p_result.status := 'STAGING';  -- Partial acceptance
      ELSE
        p_result.status := 'REJECTED';  -- All flows rejected
      END IF;
      p_result.error_rec_count := p_result.rejected_rec_count;
      p_result.error_flow_count := p_result.rejected_flow_count;
      RETURN TRUE; -- Return TRUE because file can be partially staged
    ELSE
      -- Both stages passed - all groups valid
      p_result.status := 'STAGING';
      p_result.error_rec_count := 0;
      p_result.error_flow_count := 0;
      p_result.rejected_rec_count := 0;
      p_result.rejected_flow_count := 0;
      RETURN TRUE;
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      ADD_ERROR(p_result.errors, 'FILE_VALIDATION_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8038', SQLERRM), NULL, 'file');
      p_result.status := 'REJECTED';
      RETURN FALSE;
  END FN_VALIDATE_FILE_V2;

----------------------------------------------------------------------------------------------------
-- Helper: Check if a line belongs to a valid parent group
----------------------------------------------------------------------------------------------------
  FUNCTION FN_IS_LINE_IN_VALID_GROUP(
    p_line_number     IN NUMBER,
    p_parent_groups   IN t_parent_group_ranges
  ) RETURN BOOLEAN IS
  BEGIN
    IF p_parent_groups IS NULL OR p_parent_groups.COUNT = 0 THEN
      RETURN FALSE;
    END IF;

    FOR i IN 1 .. p_parent_groups.COUNT LOOP
      IF p_line_number BETWEEN p_parent_groups(i).start_line
                           AND p_parent_groups(i).end_line THEN
        RETURN p_parent_groups(i).is_valid;
      END IF;
    END LOOP;

    RETURN FALSE;
  END FN_IS_LINE_IN_VALID_GROUP;

----------------------------------------------------------------------------------------------------
-- Helper: Get parent group info for a line
----------------------------------------------------------------------------------------------------
  FUNCTION FN_GET_PARENT_GROUP_INFO(
    p_line_number     IN NUMBER,
    p_parent_groups   IN t_parent_group_ranges,
    p_parent_group_id OUT VARCHAR2,
    p_is_valid        OUT BOOLEAN
  ) RETURN BOOLEAN IS
  BEGIN
    IF p_parent_groups IS NULL OR p_parent_groups.COUNT = 0 THEN
      p_parent_group_id := NULL;
      p_is_valid := FALSE;
      RETURN FALSE;
    END IF;

    FOR i IN 1 .. p_parent_groups.COUNT LOOP
      IF p_line_number BETWEEN p_parent_groups(i).start_line
                           AND p_parent_groups(i).end_line THEN
        p_parent_group_id := p_parent_groups(i).parent_group_id;
        p_is_valid := p_parent_groups(i).is_valid;
        RETURN TRUE;
      END IF;
    END LOOP;

    p_parent_group_id := NULL;
    p_is_valid := FALSE;
    RETURN FALSE;
  END FN_GET_PARENT_GROUP_INFO;

----------------------------------------------------------------------------------------------------
-- Split file content into lines (wrapper for PKG_DTC_COMMON)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_SPLIT_FILE_LINES(
    p_file_content IN CLOB
  ) RETURN DBMS_SQL.VARCHAR2A IS
  BEGIN
    RETURN PKG_DTC_COMMON.FN_SPLIT_FILE_LINES(p_file_content);
  END FN_SPLIT_FILE_LINES;

----------------------------------------------------------------------------------------------------
-- Get group ID from line (wrapper for PKG_DTC_COMMON)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_GET_GROUP_ID(
    p_line IN VARCHAR2
  ) RETURN VARCHAR2 IS
  BEGIN
    RETURN PKG_DTC_COMMON.FN_GET_GROUP_ID(p_line);
  END FN_GET_GROUP_ID;

END PKG_DTC_VALIDATION;
/