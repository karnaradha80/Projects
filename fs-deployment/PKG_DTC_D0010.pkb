--------------------------------------------------------
--  DDL for Package Body PKG_DTC_D0010
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "MDQA_OWNER"."PKG_DTC_D0010" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0010 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0010 flow files (Meter Readings)
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Feb/2026   Danie             Initial version with group insert functions,
--                                  PRC_PROCESS_FILE_V2 and legacy PRC_PROCESS_FILE
--  06/Feb/2026   Danie             Fixed orphan child rejection - initialised v_028_valid
--                                  and v_030_valid to FALSE, scoped hierarchy validity
--  10/Feb/2026   Radha             Added NULL check for INSTR position in legacy line parser
--  25/Feb/2026   Radha             Added field_name/field_value params to ADD_ERROR calls
--                                  for ERR_FILE_COL/ERR_FILE_COL_VAL population
--  26/Feb/2026   Radha             Added handling for unknown/empty group IDs in
--                                  validation failure and insertion branches
--  27/Feb/2026   Radha             Child group validation failure no longer cascades to
--                                  parent - only rejects the specific record
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
-- Insert group 026 (parent)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_026(
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_pk           NUMBER;
  BEGIN
    INSERT INTO STAGE_D0010_026 (
      STG_026_PK,
      STG_026_FILE_PK,
      STG_026_FILE_REC_NUM,
      STG_026_MPAN,
      STG_026_BSC_VLDN_STATUS
    ) VALUES (
      STG_D0010_026_SEQ.NEXTVAL,
      p_file_pk,
      p_rec_num,
      TO_NUMBER(p_fields(2)),  -- MPAN
      p_fields(3)              -- BSC Validation Status
    ) RETURNING STG_026_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20101, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '026', SQLERRM));
  END FN_INSERT_GROUP_026;

----------------------------------------------------------------------------------------------------
-- Insert group 027
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_027(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) IS
  BEGIN
    INSERT INTO STAGE_D0010_027 (
      STG_027_026_PK,
      STG_027_FILE_REC_NUM,
      STG_027_SITE_VISIT_CHECK,
      STG_027_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Site Visit Check
      p_fields(3)   -- Additional Info
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20102, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '027', SQLERRM));
  END PRC_INSERT_GROUP_027;

----------------------------------------------------------------------------------------------------
-- Insert group 028 (parent of 029, 030)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_028(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_pk           NUMBER;
  BEGIN
    INSERT INTO STAGE_D0010_028 (
      STG_028_PK,
      STG_028_026_PK,
      STG_028_FILE_REC_NUM,
      STG_028_MTR_ID,
      STG_028_READING_TYPE
    ) VALUES (
      STG_D0010_028_SEQ.NEXTVAL,
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Meter Id
      p_fields(3)   -- Reading Type
    ) RETURNING STG_028_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20103, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '028', SQLERRM));
  END FN_INSERT_GROUP_028;

----------------------------------------------------------------------------------------------------
-- Insert group 029
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_029(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) IS
  BEGIN
    INSERT INTO STAGE_D0010_029 (
      STG_029_028_PK,
      STG_029_FILE_REC_NUM,
      STG_029_SITE_VISIT_CHECK,
      STG_029_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Site Visit Check
      p_fields(3)   -- Additional Info
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20104, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '029', SQLERRM));
  END PRC_INSERT_GROUP_029;

----------------------------------------------------------------------------------------------------
-- Insert group 030 (parent of 032, 033)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_030(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_pk           NUMBER;
  BEGIN
    INSERT INTO STAGE_D0010_030 (
      STG_030_PK,
      STG_030_028_PK,
      STG_030_FILE_REC_NUM,
      STG_030_MTR_REG_ID,
      STG_030_READ_DTTM,
      STG_030_READ_VAL,
      STG_030_MD_RESET_DTTM,
      STG_030_MD_RESET_NUM,
      STG_030_READ_IND,
      STG_030_READING_MTHD
    ) VALUES (
      STG_D0010_030_SEQ.NEXTVAL,
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Meter Register Id
      PKG_DTC_COMMON.FN_CONVERT_DATE(p_fields(3)),  -- Read DateTime
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(p_fields(4)),  -- Read Value
      PKG_DTC_COMMON.FN_CONVERT_DATE(p_fields(5)),  -- Max Demand Reset DateTime
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(p_fields(6)),  -- Max Demand Reset Number
      p_fields(7),  -- Read Indicator
      p_fields(8)   -- Reading Method
    ) RETURNING STG_030_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20105, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '030', SQLERRM));
  END FN_INSERT_GROUP_030;

----------------------------------------------------------------------------------------------------
-- Insert group 032
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_032(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) IS
  BEGIN
    INSERT INTO STAGE_D0010_032 (
      STG_032_030_PK,
      STG_032_FILE_REC_NUM,
      STG_032_READ_REASON_CODE,
      STG_032_READ_STATUS
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Read Reason Code
      p_fields(3)   -- Read Status
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20106, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '032', SQLERRM));
  END PRC_INSERT_GROUP_032;

----------------------------------------------------------------------------------------------------
-- Insert group 033
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_033(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_fields       IN PKG_DTC_COMMON.t_fields_array,
    p_rec_num      IN NUMBER
  ) IS
  BEGIN
    INSERT INTO STAGE_D0010_033 (
      STG_033_030_PK,
      STG_033_FILE_REC_NUM,
      STG_033_SITE_VISIT_CHECK,
      STG_033_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      p_fields(2),  -- Site Visit Check
      p_fields(3)   -- Additional Info
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20107, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '033', SQLERRM));
  END PRC_INSERT_GROUP_033;

----------------------------------------------------------------------------------------------------
-- Process D0010 file with integrated validation (V2) - 2-PASS APPROACH
-- Pass 1: Stage 1 validation (file-level)
-- Pass 2: Validate each row (Stage 2) and insert if valid
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_PROCESS_FILE_V2(
    p_file_pk      IN NUMBER,
    p_lines        IN DBMS_SQL.VARCHAR2A,
    p_flow_type    IN VARCHAR2,
    p_stage1_data  IN PKG_DTC_VALIDATION.t_file_validation_result,
    p_result       OUT PKG_DTC_VALIDATION.t_file_validation_result
  ) IS
    v_lines           DBMS_SQL.VARCHAR2A;
    v_config_json     CLOB;
    v_parsed_config   JSON_OBJECT_T;
    v_group_cache     PKG_DTC_VALIDATION.t_field_config_cache;
    v_group_id        VARCHAR2(10);
    v_rec_num         NUMBER := 0;

    -- Stage 2 tracking
    v_line_errors          PKG_DTC_VALIDATION.t_validation_errors;
    v_current_parent_line  NUMBER  := NULL;
    v_current_parent_valid BOOLEAN := TRUE;
    v_current_parent_lines NUMBER  := 0;
    v_parent_group_id      VARCHAR2(10) := '026';
    v_group_range          PKG_DTC_VALIDATION.t_parent_group_range;
    v_line_valid           BOOLEAN;
    v_fields               PKG_DTC_COMMON.t_fields_array;

    -- Hierarchical validity flags
    v_026_valid  BOOLEAN := TRUE;
    v_028_valid  BOOLEAN := FALSE;
    v_030_valid  BOOLEAN := FALSE;

    -- Parent PKs (for child FK resolution)
    v_parent_026_pk  NUMBER;
    v_parent_028_pk  NUMBER;
    v_parent_030_pk  NUMBER;

  BEGIN
    p_result.errors := PKG_DTC_VALIDATION.t_validation_errors();
    p_result.parent_groups := PKG_DTC_VALIDATION.t_parent_group_ranges();
    p_result.staged_rec_count := 0;
    p_result.staged_flow_count := 0;
    p_result.rejected_rec_count := 0;
    p_result.rejected_flow_count := 0;
    p_result.stage1_passed := FALSE;
    p_result.status := 'REJECTED';

    v_config_json := PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG(p_flow_type);
    IF v_config_json IS NULL THEN
      PKG_DTC_VALIDATION.ADD_ERROR(p_result.errors, 'CONFIG_NOT_FOUND',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8003', p_flow_type), NULL, 'flowType', p_flow_type);
      RETURN;
    END IF;

    v_lines := p_lines;
    v_parsed_config := JSON_OBJECT_T(v_config_json);
    v_group_cache   := PKG_DTC_VALIDATION.FN_BUILD_GROUP_CACHE(
                         JSON_ARRAY_T(v_parsed_config.get('groups')));

    IF v_lines.COUNT < 3 THEN
      PKG_DTC_VALIDATION.ADD_ERROR(p_result.errors, 'FILE_TOO_SHORT',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8004'), NULL, 'fileContent');
      RETURN;
    END IF;

    p_result.stage1_passed    := TRUE;
    p_result.header_data      := p_stage1_data.header_data;
    p_result.footer_data      := p_stage1_data.footer_data;
    p_result.total_rec_count  := p_stage1_data.total_rec_count;
    p_result.total_flow_count := p_stage1_data.total_flow_count;

    -- ======================================================================
    -- PASS 2: Validate each line (Stage 2) and insert immediately if valid
    -- ======================================================================
    FOR i IN 2 .. v_lines.COUNT - 1 LOOP
      v_rec_num  := v_rec_num + 1;
      v_fields   := PKG_DTC_COMMON.FN_PARSE_LINE(v_lines(i));
      v_group_id := v_fields(1);  -- group ID is always the first field (avoids redundant FN_GET_GROUP_ID call)

      -- Track parent group boundary
      IF v_group_id = v_parent_group_id THEN
        IF v_current_parent_line IS NOT NULL THEN
          v_group_range.parent_group_id := v_parent_group_id;
          v_group_range.start_line      := v_current_parent_line;
          v_group_range.end_line        := i - 1;
          v_group_range.is_valid        := v_current_parent_valid;
          p_result.parent_groups.EXTEND;
          p_result.parent_groups(p_result.parent_groups.COUNT) := v_group_range;
        END IF;
        v_current_parent_line  := i;
        v_current_parent_valid := TRUE;
        v_current_parent_lines := 1;
        v_026_valid := TRUE;
        v_028_valid := FALSE;
        v_030_valid := FALSE;
      ELSE
        v_current_parent_lines := v_current_parent_lines + 1;
      END IF;

      -- Validate line (no JSON, no REPLACE — uses pre-built cache)
      v_line_valid := PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE(
        v_fields, v_group_id, v_group_cache, i, v_line_errors
      );

      -- Update hierarchy validity
      IF NOT v_line_valid THEN
        IF v_group_id = '026' THEN
          v_current_parent_valid := FALSE;
          v_026_valid := FALSE;
        ELSIF v_group_id = '028' THEN
          v_028_valid := FALSE;
          v_030_valid := FALSE;
        ELSIF v_group_id = '030' THEN
          v_030_valid := FALSE;
        END IF;
        IF v_line_errors IS NOT NULL THEN
          FOR j IN 1 .. v_line_errors.COUNT LOOP
            v_line_errors(j).group_id := v_group_id;
            p_result.errors.EXTEND;
            p_result.errors(p_result.errors.COUNT) := v_line_errors(j);
          END LOOP;
        END IF;
      ELSE
        IF v_group_id = '026' THEN
          v_current_parent_valid := TRUE;
          v_026_valid := TRUE;
        ELSIF v_group_id = '028' THEN
          v_028_valid := TRUE;
          v_030_valid := FALSE;
        ELSIF v_group_id = '030' THEN
          v_030_valid := TRUE;
        END IF;
      END IF;

      -- Insert valid rows
      IF v_group_id = '026' THEN
        IF v_line_valid AND v_026_valid THEN
          v_parent_026_pk := FN_INSERT_GROUP_026(p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count  := p_result.staged_rec_count + 1;
          p_result.staged_flow_count := p_result.staged_flow_count + 1;
        ELSE
          p_result.rejected_rec_count  := p_result.rejected_rec_count + 1;
          p_result.rejected_flow_count := p_result.rejected_flow_count + 1;
        END IF;

      ELSIF v_group_id = '027' THEN
        IF v_line_valid AND v_026_valid THEN
          PRC_INSERT_GROUP_027(v_parent_026_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '028' THEN
        IF v_line_valid AND v_026_valid THEN
          v_parent_028_pk := FN_INSERT_GROUP_028(v_parent_026_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '029' THEN
        IF v_line_valid AND v_026_valid AND v_028_valid THEN
          PRC_INSERT_GROUP_029(v_parent_028_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '030' THEN
        IF v_line_valid AND v_026_valid AND v_028_valid THEN
          v_parent_030_pk := FN_INSERT_GROUP_030(v_parent_028_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '032' THEN
        IF v_line_valid AND v_026_valid AND v_028_valid AND v_030_valid THEN
          PRC_INSERT_GROUP_032(v_parent_030_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '033' THEN
        IF v_line_valid AND v_026_valid AND v_028_valid AND v_030_valid THEN
          PRC_INSERT_GROUP_033(v_parent_030_pk, p_file_pk, v_fields, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSE
        p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
      END IF;

    END LOOP;

    -- Final status
    IF p_result.staged_flow_count > 0 THEN
      p_result.status := 'STAGING';
    ELSE
      p_result.status := 'REJECTED';
    END IF;
    p_result.error_rec_count  := p_result.rejected_rec_count;
    p_result.error_flow_count := p_result.rejected_flow_count;

  EXCEPTION
    WHEN OTHERS THEN
      PKG_DTC_VALIDATION.ADD_ERROR(
        p_result.errors, 'PROCESSING_ERROR',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8002', 'D0010', SQLERRM),
        NULL, 'processing'
      );
      p_result.status := 'REJECTED';
      ROLLBACK;
  END PRC_PROCESS_FILE_V2;

----------------------------------------------------------------------------------------------------
-- Process D0010 file (legacy - no validation)
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_PROCESS_FILE(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_success      OUT BOOLEAN,
    p_error_msg    OUT VARCHAR2
  ) IS
    v_lines           DBMS_SQL.VARCHAR2A;
    v_line            VARCHAR2(32767);
    v_fields          PKG_DTC_COMMON.t_fields_array;
    v_group_id        VARCHAR2(10);
    v_rec_num         NUMBER := 0;
    v_parent_026_pk   NUMBER;
    v_parent_028_pk   NUMBER;
    v_parent_030_pk   NUMBER;
    v_offset          NUMBER := 1;
    v_clob_len        NUMBER;
    v_read_amount     NUMBER;
    v_buffer          VARCHAR2(32767);
    v_line_idx        NUMBER := 1;
    v_pos             NUMBER;
    v_remaining       VARCHAR2(32767) := '';
  BEGIN
    p_success := TRUE;
    p_error_msg := NULL;

    -- Split file into lines
    v_clob_len := DBMS_LOB.GETLENGTH(p_file_content);
    WHILE v_offset <= v_clob_len LOOP
      v_read_amount := 32767 - NVL(LENGTH(v_remaining), 0);
      IF v_read_amount <= 0 THEN
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

    IF LENGTH(TRIM(v_remaining)) > 0 THEN
      v_lines(v_line_idx) := v_remaining;
    END IF;

    -- Process each line
    FOR i IN 1 .. v_lines.COUNT LOOP
      v_line := v_lines(i);
      v_group_id := SUBSTR(v_line, 1, INSTR(v_line, PKG_DTC_COMMON.C_DELIMITER) - 1);

      -- Skip header and footer
      IF v_group_id = PKG_DTC_COMMON.C_HEADER_ID OR v_group_id = PKG_DTC_COMMON.C_FOOTER_ID THEN
        CONTINUE;
      END IF;

      v_rec_num := v_rec_num + 1;
      v_fields  := PKG_DTC_COMMON.FN_PARSE_LINE(v_line);

      -- Process based on group ID
      IF v_group_id = '026' THEN
        v_parent_026_pk := FN_INSERT_GROUP_026(p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '027' THEN
        PRC_INSERT_GROUP_027(v_parent_026_pk, p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '028' THEN
        v_parent_028_pk := FN_INSERT_GROUP_028(v_parent_026_pk, p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '029' THEN
        PRC_INSERT_GROUP_029(v_parent_028_pk, p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '030' THEN
        v_parent_030_pk := FN_INSERT_GROUP_030(v_parent_028_pk, p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '032' THEN
        PRC_INSERT_GROUP_032(v_parent_030_pk, p_file_pk, v_fields, v_rec_num);

      ELSIF v_group_id = '033' THEN
        PRC_INSERT_GROUP_033(v_parent_030_pk, p_file_pk, v_fields, v_rec_num);

      END IF;
    END LOOP;

  EXCEPTION
    WHEN OTHERS THEN
      p_success := FALSE;
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8002', 'D0010', SQLERRM);
  END PRC_PROCESS_FILE;

END PKG_DTC_D0010;
/