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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

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
      TO_NUMBER(v_fields(2)),  -- MPAN
      v_fields(3)              -- BSC Validation Status
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0010_027 (
      STG_027_026_PK,
      STG_027_FILE_REC_NUM,
      STG_027_SITE_VISIT_CHECK,
      STG_027_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Site Visit Check
      v_fields(3)   -- Additional Info
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

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
      v_fields(2),  -- Meter Id
      v_fields(3)   -- Reading Type
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0010_029 (
      STG_029_028_PK,
      STG_029_FILE_REC_NUM,
      STG_029_SITE_VISIT_CHECK,
      STG_029_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Site Visit Check
      v_fields(3)   -- Additional Info
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

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
      v_fields(2),  -- Meter Register Id
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(3)),  -- Read DateTime
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(4)),  -- Read Value
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(5)),  -- Max Demand Reset DateTime
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(6)),  -- Max Demand Reset Number
      v_fields(7),  -- Read Indicator
      v_fields(8)   -- Reading Method
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0010_032 (
      STG_032_030_PK,
      STG_032_FILE_REC_NUM,
      STG_032_READ_REASON_CODE,
      STG_032_READ_STATUS
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Read Reason Code
      v_fields(3)   -- Read Status
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
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0010_033 (
      STG_033_030_PK,
      STG_033_FILE_REC_NUM,
      STG_033_SITE_VISIT_CHECK,
      STG_033_ADD_INFO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Site Visit Check
      v_fields(3)   -- Additional Info
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
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT PKG_DTC_VALIDATION.t_file_validation_result
  ) IS
    v_lines           DBMS_SQL.VARCHAR2A;
    v_config_json     CLOB;
    v_group_id        VARCHAR2(10);
    v_rec_num         NUMBER := 0;
    v_parent_026_pk   NUMBER;
    v_parent_028_pk   NUMBER;
    v_parent_030_pk   NUMBER;

    -- Stage 1 validation results
    v_stage1_errors   PKG_DTC_VALIDATION.t_validation_errors;
    v_header_data     PKG_DTC_VALIDATION.t_header_data;
    v_footer_data     PKG_DTC_VALIDATION.t_footer_data;
    v_total_rec_count NUMBER;
    v_total_flow_count NUMBER;

    -- Stage 2 tracking
    v_line_errors     PKG_DTC_VALIDATION.t_validation_errors;
    v_current_parent_line NUMBER := NULL;
    v_current_parent_valid BOOLEAN := TRUE;
    v_current_parent_lines NUMBER := 0;
    v_parent_group_id VARCHAR2(10) := '026';  -- D0010 parent group
    v_group_range     PKG_DTC_VALIDATION.t_parent_group_range;
    v_line_valid      BOOLEAN;  -- Current line validation result

    -- Hierarchical validity tracking (for nested groups)
    v_026_valid       BOOLEAN := TRUE;  -- Parent 026 valid?
    v_028_valid       BOOLEAN := FALSE;  -- Intermediate parent 028 exists and valid?
    v_030_valid       BOOLEAN := FALSE;  -- Intermediate parent 030 exists and valid?
  BEGIN
    -- Initialize result
    p_result.errors := PKG_DTC_VALIDATION.t_validation_errors();
    p_result.parent_groups := PKG_DTC_VALIDATION.t_parent_group_ranges();
    p_result.staged_rec_count := 0;
    p_result.staged_flow_count := 0;
    p_result.rejected_rec_count := 0;
    p_result.rejected_flow_count := 0;
    p_result.stage1_passed := FALSE;
    p_result.status := 'REJECTED';

    -- Get validation config
    v_config_json := PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG(p_flow_type);
    IF v_config_json IS NULL THEN
      PKG_DTC_VALIDATION.ADD_ERROR(p_result.errors, 'CONFIG_NOT_FOUND',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8003', p_flow_type), NULL, 'flowType', p_flow_type);
      RETURN;
    END IF;

    -- Split file into lines
    v_lines := PKG_DTC_VALIDATION.FN_SPLIT_FILE_LINES(p_file_content);
    IF v_lines.COUNT < 3 THEN
      PKG_DTC_VALIDATION.ADD_ERROR(p_result.errors, 'FILE_TOO_SHORT',
        PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8004'), NULL, 'fileContent');
      RETURN;
    END IF;

    -- ========================================
    -- PASS 1: STAGE 1 VALIDATION (File-level)
    -- ========================================
    IF NOT PKG_DTC_VALIDATION.FN_VALIDATE_STAGE1(
      v_lines,
      v_config_json,
      p_flow_type,
      v_header_data,
      v_footer_data,
      v_total_rec_count,
      v_total_flow_count,
      v_stage1_errors
    ) THEN
      -- Stage 1 failed - reject entire file
      p_result.stage1_passed := FALSE;
      p_result.status := 'REJECTED';
      p_result.header_data := v_header_data;
      p_result.footer_data := v_footer_data;
      p_result.total_rec_count := v_total_rec_count;
      p_result.total_flow_count := v_total_flow_count;
      p_result.rejected_rec_count := v_total_rec_count;
      p_result.rejected_flow_count := v_total_flow_count;

      -- Copy errors
      IF v_stage1_errors IS NOT NULL THEN
        FOR i IN 1 .. v_stage1_errors.COUNT LOOP
          p_result.errors.EXTEND;
          p_result.errors(p_result.errors.COUNT) := v_stage1_errors(i);
        END LOOP;
      END IF;
      RETURN;
    END IF;

    -- Stage 1 passed
    p_result.stage1_passed := TRUE;
    p_result.header_data := v_header_data;
    p_result.footer_data := v_footer_data;
    p_result.total_rec_count := v_total_rec_count;
    p_result.total_flow_count := v_total_flow_count;

    -- ========================================================================
    -- PASS 2: STAGE 2 VALIDATION + INSERTION (Validate each row and insert)
    -- ========================================================================
    FOR i IN 2 .. v_lines.COUNT - 1 LOOP  -- Skip header (1) and footer (last)
      v_rec_num := v_rec_num + 1;
      v_group_id := PKG_DTC_VALIDATION.FN_GET_GROUP_ID(v_lines(i));

      -- Detect new parent group (026)
      IF v_group_id = v_parent_group_id THEN
        -- Finalize previous parent group
        IF v_current_parent_line IS NOT NULL THEN
          -- Record parent group range
          v_group_range.parent_group_id := v_parent_group_id;
          v_group_range.start_line := v_current_parent_line;
          v_group_range.end_line := i - 1;
          v_group_range.is_valid := v_current_parent_valid;
          p_result.parent_groups.EXTEND;
          p_result.parent_groups(p_result.parent_groups.COUNT) := v_group_range;
        END IF;

        -- Start new parent group
        v_current_parent_line := i;
        v_current_parent_valid := TRUE;
        v_current_parent_lines := 1;

        -- Reset hierarchy validity flags for new parent
        v_026_valid := TRUE;
        v_028_valid := FALSE;  -- No 028 exists yet for this new 026
        v_030_valid := FALSE;  -- No 030 exists yet for this new 026
      ELSE
        -- Child line
        v_current_parent_lines := v_current_parent_lines + 1;
      END IF;

      -- Validate this line's fields
      v_line_valid := PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE(
        v_lines(i), v_group_id, v_config_json, i, v_line_errors
      );

      IF NOT v_line_valid THEN
        -- Mark appropriate hierarchy level as invalid
        IF v_group_id = '026' THEN
          -- Mark parent group as invalid (any failed validation rejects the entire parent group)
          v_current_parent_valid := FALSE;
          v_026_valid := FALSE;
        ELSIF v_group_id = '028' THEN
          v_028_valid := FALSE;
          v_030_valid := FALSE;  -- New 028 means no 030 exists yet
        ELSIF v_group_id = '030' THEN
          v_030_valid := FALSE;
        -- ELSE: Child groups (027, 029, 032, 033) or unknown group IDs
        -- Only reject this specific record, do NOT cascade up to invalidate parent 026
        END IF;

        -- Add errors
        IF v_line_errors IS NOT NULL THEN
          FOR j IN 1 .. v_line_errors.COUNT LOOP
            v_line_errors(j).group_id := v_group_id;
            p_result.errors.EXTEND;
            p_result.errors(p_result.errors.COUNT) := v_line_errors(j);
          END LOOP;
        END IF;
      ELSE
        -- Mark appropriate hierarchy level as valid (only the current level, not children)
        IF v_group_id = '026' THEN
          v_current_parent_valid := TRUE;
          v_026_valid := TRUE;
          -- Do NOT set v_028_valid/v_030_valid to TRUE here - they don't exist yet
        ELSIF v_group_id = '028' THEN
          v_028_valid := TRUE;
          v_030_valid := FALSE;  -- New valid 028 means no 030 exists yet
        ELSIF v_group_id = '030' THEN
          v_030_valid := TRUE;
        END IF;
      END IF;

      IF v_group_id = '026' THEN
        -- Insert only if 026 is valid
        IF v_line_valid AND v_026_valid THEN
          v_parent_026_pk := FN_INSERT_GROUP_026(p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
          p_result.staged_flow_count := p_result.staged_flow_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
          p_result.rejected_flow_count := p_result.rejected_flow_count + 1;
        END IF;

      ELSIF v_group_id = '027' THEN
        -- Insert only if parent 026 is valid
        IF v_line_valid AND v_026_valid THEN
          PRC_INSERT_GROUP_027(v_parent_026_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '028' THEN
        -- Insert only if parent 026 is valid
        IF v_line_valid AND v_026_valid THEN
          v_parent_028_pk := FN_INSERT_GROUP_028(v_parent_026_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '029' THEN
        -- Insert only if parent 026 AND 028 are valid
        IF v_line_valid AND v_026_valid AND v_028_valid THEN
          PRC_INSERT_GROUP_029(v_parent_028_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '030' THEN
        -- Insert only if parent 026 AND 028 are valid
        IF v_line_valid AND v_026_valid AND v_028_valid THEN
          v_parent_030_pk := FN_INSERT_GROUP_030(v_parent_028_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '032' THEN
        -- Insert only if parent 026 AND 028 AND 030 are valid
        IF v_line_valid AND v_026_valid AND v_028_valid AND v_030_valid THEN
          PRC_INSERT_GROUP_032(v_parent_030_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '033' THEN
        -- Insert only if parent 026 AND 028 AND 030 are valid
        IF v_line_valid AND v_026_valid AND v_028_valid AND v_030_valid THEN
          PRC_INSERT_GROUP_033(v_parent_030_pk, p_file_pk, v_lines(i), v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSE
        -- Unknown/empty group ID - count as rejected
        p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
      END IF;

    END LOOP;


    -- Set final status
    IF p_result.staged_flow_count > 0 THEN
      p_result.status := 'STAGING';  -- Partial acceptance

    ELSE
      p_result.status := 'REJECTED';
    END IF;
    p_result.error_rec_count := p_result.rejected_rec_count;
    p_result.error_flow_count := p_result.rejected_flow_count;

  EXCEPTION
    WHEN OTHERS THEN
      PKG_DTC_VALIDATION.ADD_ERROR(
        p_result.errors,
        'PROCESSING_ERROR',
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

      -- Process based on group ID
      IF v_group_id = '026' THEN
        v_parent_026_pk := FN_INSERT_GROUP_026(p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '027' THEN
        PRC_INSERT_GROUP_027(v_parent_026_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '028' THEN
        v_parent_028_pk := FN_INSERT_GROUP_028(v_parent_026_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '029' THEN
        PRC_INSERT_GROUP_029(v_parent_028_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '030' THEN
        v_parent_030_pk := FN_INSERT_GROUP_030(v_parent_028_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '032' THEN
        PRC_INSERT_GROUP_032(v_parent_030_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '033' THEN
        PRC_INSERT_GROUP_033(v_parent_030_pk, p_file_pk, v_line, v_rec_num);

      END IF;
    END LOOP;

  EXCEPTION
    WHEN OTHERS THEN
      p_success := FALSE;
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8002', 'D0010', SQLERRM);
  END PRC_PROCESS_FILE;

END PKG_DTC_D0010;
/