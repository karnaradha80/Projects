--------------------------------------------------------
--  DDL for Package Body PKG_DTC_D0302
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "MDQA_OWNER"."PKG_DTC_D0302" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0302 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0302 flow files
--               : Uses PKG_DTC_COMMON for shared parsing and conversion utilities
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Feb/2026   Danie             Initial version
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
-- Insert group 68C (parent)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_68C(
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_68C (
      STG_68C_PK,
      STG_68C_FILE_PK,
      STG_68C_FILE_REC_NUM,
      STG_68C_MPAN,
      STG_68C_REGI_DT
    ) VALUES (
      STG_D0302_68C_SEQ.NEXTVAL,
      p_file_pk,
      p_rec_num,
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(2)),  -- MPAN
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(3))  -- Registration Date
    ) RETURNING STG_68C_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20101, 'Error inserting group 68C: ' || SQLERRM);
  END FN_INSERT_GROUP_68C;

----------------------------------------------------------------------------------------------------
-- Insert group 69C
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_69C(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_69C (
      STG_69C_68C_PK,
      STG_69C_FILE_REC_NUM,
      STG_69C_CUST_NAME,
      STG_69C_ADD_INFO,
      STG_69C_CUST_PSWD,
      STG_69C_CUST_PSWD_DT,
      STG_69C_SPECIAL_ACCESS,
      STG_69C_MPR
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Customer Name
      v_fields(3),  -- Additional Info
      v_fields(4),  -- Customer Password
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(5)),  -- Customer Password Date
      v_fields(6),  -- Special Access
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(7))  -- MPR
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20102, 'Error inserting group 69C: ' || SQLERRM);
  END PRC_INSERT_GROUP_69C;

----------------------------------------------------------------------------------------------------
-- Insert group 70C
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_70C(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_70C (
      STG_70C_68C_PK,
      STG_70C_FILE_REC_NUM,
      STG_70C_MAIL_ADDR_DEL_IND,
      STG_70C_MAIL_ADDR_LINE_1,
      STG_70C_MAIL_ADDR_LINE_2,
      STG_70C_MAIL_ADDR_LINE_3,
      STG_70C_MAIL_ADDR_LINE_4,
      STG_70C_MAIL_ADDR_LINE_5,
      STG_70C_MAIL_ADDR_LINE_6,
      STG_70C_MAIL_ADDR_LINE_7,
      STG_70C_MAIL_ADDR_LINE_8,
      STG_70C_MAIL_ADDR_LINE_9,
      STG_70C_MAIL_ADDR_PCODE
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),   -- Mail Address Delivery Indicator
      v_fields(3),   -- Mail Address Line 1
      v_fields(4),   -- Mail Address Line 2
      v_fields(5),   -- Mail Address Line 3
      v_fields(6),   -- Mail Address Line 4
      v_fields(7),   -- Mail Address Line 5
      v_fields(8),   -- Mail Address Line 6
      v_fields(9),   -- Mail Address Line 7
      v_fields(10),  -- Mail Address Line 8
      v_fields(11),  -- Mail Address Line 9
      v_fields(12)   -- Mail Address Postcode
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20103, 'Error inserting group 70C: ' || SQLERRM);
  END PRC_INSERT_GROUP_70C;

----------------------------------------------------------------------------------------------------
-- Insert group 15J (parent of 16J and 17J)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_15J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_15J (
      STG_15J_PK,
      STG_15J_68C_PK,
      STG_15J_FILE_REC_NUM,
      STG_15J_CONT_NAME,
      STG_15J_CUST_PREF_CONT_MTHD
    ) VALUES (
      STG_D0302_15J_SEQ.NEXTVAL,
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Contact Name
      v_fields(3)   -- Customer Preferred Contact Method
    ) RETURNING STG_15J_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20104, 'Error inserting group 15J: ' || SQLERRM);
  END FN_INSERT_GROUP_15J;

----------------------------------------------------------------------------------------------------
-- Insert group 16J
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_16J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_16J (
      STG_16J_15J_PK,
      STG_16J_FILE_REC_NUM,
      STG_16J_CONT_TEL_NUM,
      STG_16J_CONT_FAX_NUM
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Contact Tel Number
      v_fields(3)   -- Contact Fax Number
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20105, 'Error inserting group 16J: ' || SQLERRM);
  END PRC_INSERT_GROUP_16J;

----------------------------------------------------------------------------------------------------
-- Insert group 17J
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_17J(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0302_17J (
      STG_17J_15J_PK,
      STG_17J_FILE_REC_NUM,
      STG_17J_CONT_EMAIL
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2)  -- Contact Email
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20106, 'Error inserting group 17J: ' || SQLERRM);
  END PRC_INSERT_GROUP_17J;

----------------------------------------------------------------------------------------------------
-- Process D0302 file
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
    v_parent_68C_pk   NUMBER;
    v_parent_15J_pk   NUMBER;
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
        IF v_pos = 0 THEN
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
      BEGIN
        IF v_group_id = '68C' THEN
          v_parent_68C_pk := FN_INSERT_GROUP_68C(p_file_pk, v_line, v_rec_num);

        ELSIF v_group_id = '69C' THEN
          PRC_INSERT_GROUP_69C(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);

        ELSIF v_group_id = '70C' THEN
          PRC_INSERT_GROUP_70C(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);

        ELSIF v_group_id = '15J' THEN
          v_parent_15J_pk := FN_INSERT_GROUP_15J(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);

        ELSIF v_group_id = '16J' THEN
          PRC_INSERT_GROUP_16J(v_parent_15J_pk, p_file_pk, v_line, v_rec_num);

        ELSIF v_group_id = '17J' THEN
          PRC_INSERT_GROUP_17J(v_parent_15J_pk, p_file_pk, v_line, v_rec_num);

        END IF;
      EXCEPTION
        WHEN OTHERS THEN
          -- Re-raise with more context
          RAISE_APPLICATION_ERROR(-20199, 'Error processing group ' || v_group_id || ' at line ' || i || ': ' || SQLERRM);
      END;
    END LOOP;

  EXCEPTION
    WHEN OTHERS THEN
      p_success := FALSE;
      p_error_msg := 'Error processing D0302 file: ' || SQLERRM;
  END PRC_PROCESS_FILE;

----------------------------------------------------------------------------------------------------
-- Process D0302 file with integrated validation (V2)
-- This version uses a 2-pass approach:
--   Pass 1: Stage 1 validation (file-level)
--   Pass 2: Validate each row (Stage 2) and insert immediately if valid
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_PROCESS_FILE_V2(
    p_file_pk      IN NUMBER,
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_result       OUT PKG_DTC_VALIDATION.t_file_validation_result
  ) IS
    -- Variables for file processing
    v_lines           DBMS_SQL.VARCHAR2A;
    v_line            VARCHAR2(32767);
    v_group_id        VARCHAR2(10);
    v_rec_num         NUMBER := 0;
    v_parent_68C_pk   NUMBER;
    v_parent_15J_pk   NUMBER;
    v_offset          NUMBER := 1;
    v_clob_len        NUMBER;
    v_read_amount     NUMBER;
    v_buffer          VARCHAR2(32767);
    v_line_idx        NUMBER := 1;
    v_pos             NUMBER;
    v_remaining       VARCHAR2(32767) := '';

    -- Parent group tracking
    v_parent_group_id       VARCHAR2(10) := '68C';  -- D0302 parent group
    v_current_parent_line   NUMBER := NULL;
    v_current_parent_valid  BOOLEAN := TRUE;
    v_current_parent_lines  NUMBER := 0;

    -- Hierarchical validity tracking
    v_68C_valid BOOLEAN := TRUE;  -- Root parent valid?
    v_15J_valid BOOLEAN := TRUE;  -- Intermediate parent valid?

    -- Validation result from Stage 2
    v_line_valid       BOOLEAN;
    v_stage2_result    PKG_DTC_VALIDATION.t_file_validation_result;

    -- Counts for result
    v_staged_flow_count   NUMBER := 0;
    v_rejected_flow_count NUMBER := 0;
    v_staged_rec_count    NUMBER := 0;

  BEGIN
    -- Initialize result
    p_result := PKG_DTC_VALIDATION.FN_INIT_RESULT;
    p_result.flow_type := p_flow_type;

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
        IF v_pos = 0 THEN
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

    --====================================================================================
    -- PASS 1: Stage 1 Validation (File-Level)
    --====================================================================================
    IF NOT PKG_DTC_VALIDATION.FN_VALIDATE_STAGE1(
      p_lines     => v_lines,
      p_flow_type => p_flow_type,
      p_result    => p_result
    ) THEN
      -- Stage 1 failed - reject entire file
      p_result.status := 'REJECTED';
      RETURN;
    END IF;

    --====================================================================================
    -- PASS 2: Validate Each Row (Stage 2) + Insert
    --====================================================================================
    FOR i IN 2 .. v_lines.COUNT - 1 LOOP  -- Skip header (1) and footer (last)
      v_rec_num := v_rec_num + 1;
      v_line := v_lines(i);
      v_group_id := PKG_DTC_VALIDATION.FN_GET_GROUP_ID(v_line);

      -- Detect start of new parent group
      IF v_group_id = v_parent_group_id THEN
        -- Start new parent group
        v_current_parent_line := i;
        v_current_parent_valid := TRUE;
        v_current_parent_lines := 1;

        -- Reset hierarchy validity flags
        v_68C_valid := TRUE;
        v_15J_valid := TRUE;

      ELSE
        v_current_parent_lines := v_current_parent_lines + 1;
      END IF;

      -- Validate this line
      v_line_valid := PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE(
        p_line      => v_line,
        p_line_num  => i,
        p_flow_type => p_flow_type,
        p_result    => p_result
      );

      IF NOT v_line_valid THEN
        -- Mark appropriate hierarchy level as invalid
        IF v_group_id = '68C' THEN
          v_current_parent_valid := FALSE;
          v_68C_valid := FALSE;
        ELSIF v_group_id = '15J' THEN
          v_15J_valid := FALSE;
        END IF;

        -- Add error with group context
        PKG_DTC_VALIDATION.ADD_ERROR(
          p_result   => p_result,
          p_line_num => i,
          p_field    => 'GROUP_' || v_group_id,
          p_message  => 'Validation failed for group ' || v_group_id || ' - parent group will be rejected',
          p_group_id => v_group_id
        );
      ELSE
        -- Mark appropriate hierarchy level as valid
        IF v_group_id = '68C' THEN
          v_current_parent_valid := TRUE;
          v_68C_valid := TRUE;
          v_15J_valid := TRUE;
        ELSIF v_group_id = '15J' THEN
          v_15J_valid := TRUE;
        END IF;
      END IF;

      IF v_group_id = '68C' THEN
        -- Insert only if 68C is valid
        IF v_line_valid AND v_68C_valid THEN
          v_parent_68C_pk := FN_INSERT_GROUP_68C(p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
          v_staged_flow_count := v_staged_flow_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
          v_rejected_flow_count := v_rejected_flow_count + 1;
        END IF;

      ELSIF v_group_id = '69C' THEN
        -- Insert only if parent 68C is valid
        IF v_line_valid AND v_68C_valid THEN
          PRC_INSERT_GROUP_69C(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '70C' THEN
        -- Insert only if parent 68C is valid
        IF v_line_valid AND v_68C_valid THEN
          PRC_INSERT_GROUP_70C(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '15J' THEN
        -- Insert only if parent 68C is valid
        IF v_line_valid AND v_68C_valid THEN
          v_parent_15J_pk := FN_INSERT_GROUP_15J(v_parent_68C_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '16J' THEN
        -- Insert only if parent 68C AND 15J are valid
        IF v_line_valid AND v_68C_valid AND v_15J_valid THEN
          PRC_INSERT_GROUP_16J(v_parent_15J_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '17J' THEN
        -- Insert only if parent 68C AND 15J are valid
        IF v_line_valid AND v_68C_valid AND v_15J_valid THEN
          PRC_INSERT_GROUP_17J(v_parent_15J_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      END IF;

    END LOOP;  -- End of Pass 2

    -- Set final result counts and status
    p_result.staged_flow_count := v_staged_flow_count;
    p_result.rejected_flow_count := v_rejected_flow_count;
    IF v_staged_flow_count > 0 THEN
      p_result.status := 'STAGING';
    ELSE
      p_result.status := 'REJECTED';
    END IF;
    p_result.error_rec_count := p_result.rejected_rec_count;
    p_result.error_flow_count := v_rejected_flow_count;

  EXCEPTION
    WHEN OTHERS THEN
      p_result.status := 'REJECTED';
      PKG_DTC_VALIDATION.ADD_ERROR(
        p_result   => p_result,
        p_line_num => 0,
        p_field    => 'PROCESS',
        p_message  => 'Fatal error processing file: ' || SQLERRM,
        p_group_id => NULL
      );
  END PRC_PROCESS_FILE_V2;

END PKG_DTC_D0302;
/
