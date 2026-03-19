--------------------------------------------------------
--  DDL for Package Body PKG_DTC_D0150
--------------------------------------------------------
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "MDQA_OWNER"."PKG_DTC_D0150" AS
----------------------------------------------------------------------------------------------------
--  DESCRIPTION : D0150 Flow Processing Package
--
--  NOTES       : This package handles parsing and staging of D0150 flow files
----------------------------------------------------------------------------------------------------
--
--  CHANGE HISTORY
--  =================
--    DATE               WHO                    DESCRIPTION
--  ==========   ================  ===============================================
--  05/Feb/2026   Danie             Initial version
--  06/Feb/2026   Danie             Fixed orphan child rejection - changed v_290_valid
--                                  initial value to FALSE, fixed hierarchy cascade logic
--  10/Feb/2026   Radha             Added NULL check for INSTR position in legacy line parser
--  25/Feb/2026   Radha             Added field_name param to ADD_ERROR call for
--                                  ERR_FILE_COL population
--  26/Feb/2026   Radha             Added handling for unknown/empty group IDs - mark
--                                  parent 288 invalid and count as rejected records
--  17/Mar/2026   Radha             Fixed ORA-06502 buffer overflow in file splitting
--                                  when v_remaining || v_buffer exceeds 32767
----------------------------------------------------------------------------------------------------

  -- All constants and types are now in PKG_DTC_COMMON

----------------------------------------------------------------------------------------------------
-- Insert group 288 (parent)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_288(
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_288 (
      STG_288_PK,
      STG_288_FILE_PK,
      STG_288_FILE_REC_NUM,
      STG_288_MPAN,
      STG_288_MSMTD,
      STG_288_MC_ID,
      STG_288_MSES
    ) VALUES (
      STG_D0150_288_SEQ.NEXTVAL,
      p_file_pk,
      p_rec_num,
      TO_NUMBER(v_fields(2)),  -- MPAN
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(3)),  -- Measurement System Transfer Date
      v_fields(4),  -- Meter Configuration Id
      v_fields(5)   -- Meter Serial Equipment Status
    ) RETURNING STG_288_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20001, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '288', SQLERRM));
  END FN_INSERT_GROUP_288;

----------------------------------------------------------------------------------------------------
-- Insert group 289
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_289(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_289 (
      STG_289_288_PK,
      STG_289_FILE_REC_NUM,
      STG_289_SCON_ID,
      STG_289_SCON_DT,
      STG_289_MSNSFC_ID,
      STG_289_MSNSFC_DT
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Supplier Contractor Id
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(3)),  -- Supplier Contractor Date
      v_fields(4),  -- Meter Serial Numbers From Contractor Id
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(5))   -- Meter Serial Numbers From Contractor Date
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20002, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '289', SQLERRM));
  END PRC_INSERT_GROUP_289;

----------------------------------------------------------------------------------------------------
-- Insert group 290 (parent of 291, 293, 295, 296)
----------------------------------------------------------------------------------------------------
  FUNCTION FN_INSERT_GROUP_290(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) RETURN NUMBER IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
    v_pk           NUMBER;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_290 (
      STG_290_PK,
      STG_290_288_PK,
      STG_290_FILE_REC_NUM,
      STG_290_MTR_ID,
      STG_290_MTR_COP,
      STG_290_MTR_COP_DISP,
      STG_290_MTR_CUR_RATING,
      STG_290_MTR_LOC,
      STG_290_MANF_MAKE_TYPE,
      STG_290_MTR_ASST_PROV_ID,
      STG_290_COMMS_ADDR,
      STG_290_COMMS_MTHD,
      STG_290_OUTSTN_PIN,
      STG_290_OUTSTN_COP,
      STG_290_OUTSTN_COP_DISP,
      STG_290_OUTSTN_ENCRYP,
      STG_290_OUTSTN_CHANNELS,
      STG_290_OUTSTN_PSWD,
      STG_290_OUTSTN_TYPE,
      STG_290_VT_RATIO,
      STG_290_MTR_TYPE,
      STG_290_MTR_INSTLN_DT,
      STG_290_CERT_DT,
      STG_290_CERT_EXPIRY_DT,
      STG_290_TIMING_DEV_ID,
      STG_290_TELE_SWITCH_ID,
      STG_290_RTVL_MTHD,
      STG_290_RTVL_MTHD_EFF_DT
    ) VALUES (
      STG_D0150_290_SEQ.NEXTVAL,
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Meter Id
      v_fields(3),  -- Meter COP
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(4)),  -- Meter COP Displacement
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(5)),  -- Meter Current Rating
      v_fields(6),  -- Meter Location
      v_fields(7),  -- Manufacturers Make And Type
      v_fields(8),  -- Meter Asset Provider Id
      v_fields(9),  -- Communications Address
      v_fields(10), -- Communications Method
      v_fields(11), -- Outstation PIN
      v_fields(12), -- Outstation COP
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(13)),  -- Outstation COP Dispensation
      v_fields(14), -- Outstation Encryption Key
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(15)),  -- Outstation Number Of Channels
      v_fields(16), -- Outstation Password Level 1
      v_fields(17), -- Outstation Type
      v_fields(18), -- VT Ratio
      v_fields(19), -- Meter Type
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(20)),  -- Date Of Meter Installation
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(21)),  -- Certification Date
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(22)),  -- Certification Expiry Date
      v_fields(23), -- Timing Device Id
      v_fields(24), -- Tele-Switch/Clock Indicator
      v_fields(25), -- Retrieval Method
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(26))   -- Retrieval Method Effective Date
    ) RETURNING STG_290_PK INTO v_pk;

    RETURN v_pk;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20003, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '290', SQLERRM));
  END FN_INSERT_GROUP_290;

----------------------------------------------------------------------------------------------------
-- Insert group 291
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_291(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_291 (
      STG_291_290_PK,
      STG_291_FILE_REC_NUM,
      STG_291_CT_RATIO
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2)  -- CT Ratio
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20004, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '291', SQLERRM));
  END PRC_INSERT_GROUP_291;

----------------------------------------------------------------------------------------------------
-- Insert group 293
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_293(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_293 (
      STG_293_290_PK,
      STG_293_FILE_REC_NUM,
      STG_293_MTR_REG_ID,
      STG_293_MTR_REG_TYPE,
      STG_293_MQ_ID,
      STG_293_MTR_REG_MULTIPLIER,
      STG_293_MAIN_CHECK_ID,
      STG_293_REG_DIGITS,
      STG_293_ASSC_MTR_ID,
      STG_293_ASSC_MTR_REG_ID
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Meter Register Id
      v_fields(3),  -- Meter Register Type
      v_fields(4),  -- MQ Id
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(5)),  -- Meter Register Multiplier
      v_fields(6),  -- Main/Check Indicator
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(7)),  -- Number Of Register Digits
      v_fields(8),  -- Associated Meter Id
      v_fields(9)   -- Associated Meter Register Id
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20005, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '293', SQLERRM));
  END PRC_INSERT_GROUP_293;

----------------------------------------------------------------------------------------------------
-- Insert group 295
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_295(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_295 (
      STG_295_290_PK,
      STG_295_FILE_REC_NUM,
      STG_295_CHANNEL_NUM,
      STG_295_MQ_ID,
      STG_295_PULSE_MULTIPLIER
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Channel Number
      v_fields(3),  -- MQ Id
      PKG_DTC_COMMON.FN_CONVERT_NUMBER(v_fields(4))  -- Pulse Multiplier
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20006, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '295', SQLERRM));
  END PRC_INSERT_GROUP_295;

----------------------------------------------------------------------------------------------------
-- Insert group 296
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_296(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_296 (
      STG_296_290_PK,
      STG_296_FILE_REC_NUM,
      STG_296_MAINT_DT,
      STG_296_MAINT_DESC
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(2)),  -- Maintenance Date
      v_fields(3)  -- Maintenance Description
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20007, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '296', SQLERRM));
  END PRC_INSERT_GROUP_296;

----------------------------------------------------------------------------------------------------
-- Insert group 762
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_762(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_762 (
      STG_762_288_PK,
      STG_762_FILE_REC_NUM,
      STG_762_MAINT_DT,
      STG_762_MAINT_DESC
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(2)),  -- Maintenance Date
      v_fields(3)  -- Maintenance Description
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20008, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '762', SQLERRM));
  END PRC_INSERT_GROUP_762;

----------------------------------------------------------------------------------------------------
-- Insert group 08A
----------------------------------------------------------------------------------------------------
  PROCEDURE PRC_INSERT_GROUP_08A(
    p_parent_pk    IN NUMBER,
    p_file_pk      IN NUMBER,
    p_line         IN VARCHAR2,
    p_rec_num      IN NUMBER
  ) IS
    v_fields       PKG_DTC_COMMON.t_fields_array;
  BEGIN
    v_fields := PKG_DTC_COMMON.FN_PARSE_LINE(p_line);

    INSERT INTO STAGE_D0150_08A (
      STG_08A_288_PK,
      STG_08A_FILE_REC_NUM,
      STG_08A_MTR_ID,
      STG_08A_MTR_REMOVAL_DT,
      STG_08A_MTR_ASST_PROV_ID
    ) VALUES (
      p_parent_pk,
      p_rec_num,
      v_fields(2),  -- Meter Id
      PKG_DTC_COMMON.FN_CONVERT_DATE(v_fields(3)),  -- Meter Removal Date
      v_fields(4)  -- Meter Asset Provider Id
    );
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20009, PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8001', '08A', SQLERRM));
  END PRC_INSERT_GROUP_08A;

----------------------------------------------------------------------------------------------------
-- Process D0150 file
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
    v_parent_288_pk   NUMBER;
    v_parent_290_pk   NUMBER;
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
      IF v_group_id = '288' THEN
        v_parent_288_pk := FN_INSERT_GROUP_288(p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '289' THEN
        PRC_INSERT_GROUP_289(v_parent_288_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '290' THEN
        v_parent_290_pk := FN_INSERT_GROUP_290(v_parent_288_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '291' THEN
        PRC_INSERT_GROUP_291(v_parent_290_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '293' THEN
        PRC_INSERT_GROUP_293(v_parent_290_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '295' THEN
        PRC_INSERT_GROUP_295(v_parent_290_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '296' THEN
        PRC_INSERT_GROUP_296(v_parent_290_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '762' THEN
        PRC_INSERT_GROUP_762(v_parent_288_pk, p_file_pk, v_line, v_rec_num);

      ELSIF v_group_id = '08A' THEN
        PRC_INSERT_GROUP_08A(v_parent_288_pk, p_file_pk, v_line, v_rec_num);

      END IF;
    END LOOP;

  EXCEPTION
    WHEN OTHERS THEN
      p_success := FALSE;
      p_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8002', 'D0150', SQLERRM);
  END PRC_PROCESS_FILE;

----------------------------------------------------------------------------------------------------
-- Process D0150 file with integrated validation (V2)
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
    v_parent_288_pk   NUMBER;
    v_parent_290_pk   NUMBER;
    v_offset          NUMBER := 1;
    v_clob_len        NUMBER;
    v_read_amount     NUMBER;
    v_buffer          VARCHAR2(32767);
    v_line_idx        NUMBER := 1;
    v_pos             NUMBER;
    v_remaining       VARCHAR2(32767) := '';

    -- Parent group tracking
    v_parent_group_id       VARCHAR2(10) := '288';  -- D0150 parent group
    v_current_parent_line   NUMBER := NULL;
    v_current_parent_valid  BOOLEAN := TRUE;
    v_current_parent_lines  NUMBER := 0;

    -- Hierarchical validity tracking
    v_288_valid BOOLEAN := TRUE;  -- Root parent valid?
    v_290_valid BOOLEAN := FALSE;  -- Intermediate parent 290 exists and valid?

    -- Validation result from Stage 2
    v_line_valid       BOOLEAN;
    v_line_errors      PKG_DTC_VALIDATION.t_validation_errors;

    -- Stage 1 validation outputs
    v_config_json      CLOB;
    v_header_data      PKG_DTC_VALIDATION.t_header_data;
    v_footer_data      PKG_DTC_VALIDATION.t_footer_data;
    v_total_rec_count  NUMBER;
    v_total_flow_count NUMBER;
    v_stage1_errors    PKG_DTC_VALIDATION.t_validation_errors;

    -- Counts for result
    v_staged_flow_count   NUMBER := 0;
    v_rejected_flow_count NUMBER := 0;
    v_staged_rec_count    NUMBER := 0;

  BEGIN
    -- Initialize result
    p_result.errors := PKG_DTC_VALIDATION.t_validation_errors();
    p_result.parent_groups := PKG_DTC_VALIDATION.t_parent_group_ranges();
    p_result.status := 'REJECTED';
    p_result.stage1_passed := FALSE;
    p_result.staged_rec_count := 0;
    p_result.staged_flow_count := 0;
    p_result.rejected_rec_count := 0;
    p_result.rejected_flow_count := 0;
    p_result.error_rec_count := 0;
    p_result.error_flow_count := 0;

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

    -- Get validation config
    v_config_json := PKG_DTC_VALIDATION.FN_GET_ACTIVE_CONFIG(p_flow_type);
    IF v_config_json IS NULL THEN
      PKG_DTC_VALIDATION.ADD_ERROR(
        p_errors      => p_result.errors,
        p_error_code  => 'ERR8003',
        p_error_msg   => PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8003', p_flow_type),
        p_field_name  => 'flowType',
        p_field_value => p_flow_type
      );
      p_result.status := 'REJECTED';
      RETURN;
    END IF;

    --====================================================================================
    -- PASS 1: Stage 1 Validation (File-Level)
    --====================================================================================
    IF NOT PKG_DTC_VALIDATION.FN_VALIDATE_STAGE1(
      p_lines            => v_lines,
      p_config_json      => v_config_json,
      p_flow_type        => p_flow_type,
      p_header_data      => v_header_data,
      p_footer_data      => v_footer_data,
      p_total_rec_count  => v_total_rec_count,
      p_total_flow_count => v_total_flow_count,
      p_errors           => v_stage1_errors
    ) THEN
      -- Stage 1 failed - reject entire file
      p_result.status := 'REJECTED';
      p_result.header_data := v_header_data;
      p_result.footer_data := v_footer_data;
      p_result.total_rec_count := v_total_rec_count;
      p_result.total_flow_count := v_total_flow_count;
      -- Merge errors
      IF v_stage1_errors IS NOT NULL AND v_stage1_errors.COUNT > 0 THEN
        FOR i IN 1 .. v_stage1_errors.COUNT LOOP
          p_result.errors.EXTEND;
          p_result.errors(p_result.errors.COUNT) := v_stage1_errors(i);
        END LOOP;
      END IF;
      RETURN;
    END IF;

    -- Copy Stage 1 data to result
    p_result.stage1_passed := TRUE;
    p_result.header_data := v_header_data;
    p_result.footer_data := v_footer_data;
    p_result.total_rec_count := v_total_rec_count;
    p_result.total_flow_count := v_total_flow_count;

    --====================================================================================
    -- PASS 2: Validate Each Row (Stage 2) + Insert
    --====================================================================================
    FOR i IN 2 .. v_lines.COUNT - 1 LOOP  -- Skip header (1) and footer (last)
      v_rec_num := v_rec_num + 1;
      v_line := v_lines(i);
      v_group_id := PKG_DTC_COMMON.FN_GET_GROUP_ID(v_line);

      -- Detect start of new parent group
      IF v_group_id = v_parent_group_id THEN
        -- Start new parent group
        v_current_parent_line := i;
        v_current_parent_valid := TRUE;
        v_current_parent_lines := 1;

        -- Reset hierarchy validity flags
        v_288_valid := TRUE;
        v_290_valid := FALSE;  -- No 290 exists yet for this new 288

      ELSE
        v_current_parent_lines := v_current_parent_lines + 1;
      END IF;

      -- Validate this line
      v_line_valid := PKG_DTC_VALIDATION.FN_VALIDATE_GROUP_LINE(
        p_line        => v_line,
        p_group_id    => v_group_id,
        p_config_json => v_config_json,
        p_line_number => i,
        p_errors      => v_line_errors
      );

      IF NOT v_line_valid THEN
        -- Mark appropriate hierarchy level as invalid
        IF v_group_id = '288' THEN
          v_current_parent_valid := FALSE;
          v_288_valid := FALSE;
        ELSIF v_group_id = '290' THEN
          v_290_valid := FALSE;
        ELSE
          -- Unknown/empty group ID - mark current parent group as invalid
          v_current_parent_valid := FALSE;
          v_288_valid := FALSE;
        END IF;
      ELSE
        -- Mark appropriate hierarchy level as valid (only the current level, not children)
        IF v_group_id = '288' THEN
          v_current_parent_valid := TRUE;
          v_288_valid := TRUE;
          -- Do NOT set v_290_valid to TRUE here - it doesn't exist yet
        ELSIF v_group_id = '290' THEN
          v_290_valid := TRUE;
        END IF;
      END IF;

        -- Add errors from line validation
        IF v_line_errors IS NOT NULL AND v_line_errors.COUNT > 0 THEN
          FOR j IN 1 .. v_line_errors.COUNT LOOP
            v_line_errors(j).group_id := v_group_id;
            p_result.errors.EXTEND;
            p_result.errors(p_result.errors.COUNT) := v_line_errors(j);
          END LOOP;
        END IF;
      IF v_group_id = '288' THEN
        -- Insert only if 288 is valid
        IF v_line_valid AND v_288_valid THEN
          v_parent_288_pk := FN_INSERT_GROUP_288(p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
          v_staged_flow_count := v_staged_flow_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
          v_rejected_flow_count := v_rejected_flow_count + 1;
        END IF;

      ELSIF v_group_id = '289' THEN
        -- Insert only if parent 288 is valid
        IF v_line_valid AND v_288_valid THEN
          PRC_INSERT_GROUP_289(v_parent_288_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '290' THEN
        -- Insert only if parent 288 is valid
        IF v_line_valid AND v_288_valid THEN
          v_parent_290_pk := FN_INSERT_GROUP_290(v_parent_288_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '291' THEN
        -- Insert only if parent 288 AND 290 are valid
        IF v_line_valid AND v_288_valid AND v_290_valid THEN
          PRC_INSERT_GROUP_291(v_parent_290_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '293' THEN
        -- Insert only if parent 288 AND 290 are valid
        IF v_line_valid AND v_288_valid AND v_290_valid THEN
          PRC_INSERT_GROUP_293(v_parent_290_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '295' THEN
        -- Insert only if parent 288 AND 290 are valid
        IF v_line_valid AND v_288_valid AND v_290_valid THEN
          PRC_INSERT_GROUP_295(v_parent_290_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '296' THEN
        -- Insert only if parent 288 AND 290 are valid
        IF v_line_valid AND v_288_valid AND v_290_valid THEN
          PRC_INSERT_GROUP_296(v_parent_290_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '762' THEN
        -- Insert only if parent 288 is valid
        IF v_line_valid AND v_288_valid THEN
          PRC_INSERT_GROUP_762(v_parent_288_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSIF v_group_id = '08A' THEN
        -- Insert only if parent 288 is valid
        IF v_line_valid AND v_288_valid THEN
          PRC_INSERT_GROUP_08A(v_parent_288_pk, p_file_pk, v_line, v_rec_num);
          p_result.staged_rec_count := p_result.staged_rec_count + 1;
        ELSE
          p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
        END IF;

      ELSE
        -- Unknown/empty group ID - count as rejected
        p_result.rejected_rec_count := p_result.rejected_rec_count + 1;
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
        p_errors      => p_result.errors,
        p_error_code  => 'ERR8005',
        p_error_msg   => PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8005', SQLERRM),
        p_line_number => 0,
        p_field_name  => 'PROCESS',
        p_group_id    => NULL
      );
  END PRC_PROCESS_FILE_V2;

END PKG_DTC_D0150;
/