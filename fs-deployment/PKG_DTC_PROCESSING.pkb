create or replace PACKAGE BODY              "PKG_DTC_PROCESSING" AS
  -- ============================================================================
  -- Package Body: PKG_DTC_PROCESSING
  -- Purpose: Process DTC files directly from CLOB content
  -- ============================================================================
  --
  --  CHANGE HISTORY
  --  =================
  --    DATE               WHO                    DESCRIPTION
  --  ==========   ================  ===============================================
  --  05/Feb/2026   Danie             Initial version
  --  10/Feb/2026   Radha             Added exception handlers with logger_wrapper to
  --                                  PRC_CREATE_AUDIT, PRC_UPDATE_AUDIT, PRC_LOG_ERROR
  --  17/Feb/2026   Radha             Removed duplicate staging error INSERT block,
  --                                  added FIL_LOAD_STUS update in file update step
  --  18/Feb/2026   Radha             Added C_AUD_ERROR constant, changed audit status
  --                                  from ABORTED to ERROR for rejection scenarios,
  --                                  added null/empty flow_type input validation
  --  19/Feb/2026   Radha             Audit WARNING status now also considers
  --                                  rejected_rec_count (not just rejected_flow_count)
  --  25/Feb/2026   Radha             Added field_name/field_value params to PRC_LOG_ERROR,
  --                                  populated ERR_FILE_COL/ERR_FILE_COL_VAL
  --  26/Feb/2026   Radha             Header/footer field overflow protection, refined
  --                                  audit status logic (ERROR when all rejected)
  --  27/Feb/2026   Radha             Fixed AUD_REC_SUCC_CNT to use actual staging counts
  --                                  instead of validation counts
  --  10/Mar/2026   Radha             Added file name overflow protection (max 40 chars)
  --                                  truncates via SUBSTR in INSERT, then rejects
  --  17/Mar/2026   Radha             Added SUBSTR overflow protection for ERR_FILE_COL
  --                                  and ERR_FILE_COL_VAL in error INSERTs
  --  17/Mar/2026   Radha             File status REJECTED if any partial data rejected,
  --                                  STAGING only when all data loads clean; audit
  --                                  SUCCESSFUL only when file status is STAGING;
  --                                  insert staging errors from flow package into
  --                                  MDQ_ETL_ERROR (were previously missing)
  -- ============================================================================

  -- Constants for audit statuses
  C_AUD_RUNNING    CONSTANT VARCHAR2(20) := 'RUNNING';
  C_AUD_SUCCESSFUL CONSTANT VARCHAR2(20) := 'SUCCESSFUL';
  C_AUD_ABORTED    CONSTANT VARCHAR2(20) := 'ABORTED';
  C_AUD_WARNING    CONSTANT VARCHAR2(20) := 'WARNING';
  C_AUD_ERROR      CONSTANT VARCHAR2(20) := 'ERROR';

  -- Constants for file statuses
  C_STATUS_STAGING  CONSTANT VARCHAR2(20) := 'STAGING';
  C_STATUS_REJECTED CONSTANT VARCHAR2(20) := 'REJECTED';

  -- Constants for audit run number
  C_RUN_NUM CONSTANT NUMBER := 1;

  -- ============================================================================
  -- Private Procedure: PRC_CREATE_AUDIT
  -- Purpose: Insert a new audit record
  -- ============================================================================
  PROCEDURE PRC_CREATE_AUDIT(
    p_file_pk        IN NUMBER,
    p_job_name       IN VARCHAR2,
    p_parent_job     IN VARCHAR2,
    p_status         IN VARCHAR2,
    p_audit_pk       OUT NUMBER
  ) IS
  BEGIN
  
  Begin
    INSERT INTO MDQ_ETL_AUDIT (
      AUD_PK,
      AUD_FILE_PK,
      AUD_JOB_NAME,
      AUD_RUN_NUM,
      AUD_PR_JOB_NAME,
      AUD_JOB_START_DTTM,
      AUD_JOB_STATUS,
      AUD_REC_PROC_CNT,
      AUD_REC_SUCC_CNT,
      AUD_REC_FAIL_CNT,
      AUD_REC_REJ_CNT
    ) VALUES (
      SEQ_AUDIT.NEXTVAL,
      p_file_pk,
      p_job_name,
      C_RUN_NUM,
      p_parent_job,
      SYSTIMESTAMP,
      p_status,
      0,
      0,
      0,
      0
    ) RETURNING AUD_PK INTO p_audit_pk;
     EXCEPTION
      WHEN OTHERS THEN
        logger_wrapper('PRC_CREATE_AUDIT', 1, 'Unexpected error' || SQLERRM);
     End;
        
  END PRC_CREATE_AUDIT;

  -- ============================================================================
  -- Private Procedure: PRC_UPDATE_AUDIT
  -- Purpose: Update an existing audit record with final status and counts
  -- ============================================================================
  PROCEDURE PRC_UPDATE_AUDIT(
    p_audit_pk       IN NUMBER,
    p_status         IN VARCHAR2,
    p_rec_proc_cnt   IN NUMBER DEFAULT 0,
    p_rec_succ_cnt   IN NUMBER DEFAULT 0,
    p_rec_fail_cnt   IN NUMBER DEFAULT 0,
    p_rec_rej_cnt    IN NUMBER DEFAULT 0
  ) IS
  BEGIN
  
  Begin
    UPDATE MDQ_ETL_AUDIT
    SET AUD_JOB_END_DTTM  = SYSTIMESTAMP,
        AUD_JOB_STATUS    = p_status,
        AUD_REC_PROC_CNT  = p_rec_proc_cnt,
        AUD_REC_SUCC_CNT  = p_rec_succ_cnt,
        AUD_REC_FAIL_CNT  = p_rec_fail_cnt,
        AUD_REC_REJ_CNT   = p_rec_rej_cnt
    WHERE AUD_PK = p_audit_pk;
    EXCEPTION
      WHEN OTHERS THEN
        logger_wrapper('PRC_UPDATE_AUDIT', 1, 'Unexpected error' || SQLERRM);
    End;
  END PRC_UPDATE_AUDIT;

  -- ============================================================================
  -- Private Procedure: PRC_LOG_ERROR
  -- Purpose: Insert error record into MDQ_ETL_ERROR
  -- ============================================================================
  PROCEDURE PRC_LOG_ERROR(
    p_file_pk      IN NUMBER,
    p_row_num      IN NUMBER,
    p_error_msg    IN VARCHAR2,
    p_field_name   IN VARCHAR2 DEFAULT NULL,
    p_field_value  IN VARCHAR2 DEFAULT NULL
  ) IS
  BEGIN
  
  Begin
    INSERT INTO MDQ_ETL_ERROR (
      ERR_PK,
      ERR_FILE_PK,
      ERR_JOB_ID,
      ERR_RUN_NUM,
      ERR_FILE_ROW_NUM,
      ERR_FILE_COL,
      ERR_FILE_COL_VAL,
      ERR_TIMESTAMP,
      ERR_MSG_TEXT
    ) VALUES (
      SEQ_ERROR.NEXTVAL,
      p_file_pk,
      '-1',
      C_RUN_NUM,
      p_row_num,
      SUBSTR(p_field_name, 1, 100),
      SUBSTR(p_field_value, 1, 500),
      SYSDATE,
      p_error_msg
    );
    
    EXCEPTION
      WHEN OTHERS THEN
        logger_wrapper('PRC_LOG_ERROR', 1, 'Unexpected error' || SQLERRM);
    End;    
    
  END PRC_LOG_ERROR;

  -- ============================================================================
  -- Main Function: PRC_PROCESS_FILE
  -- Purpose: Process DTC file from CLOB content
  -- ============================================================================
  FUNCTION PRC_PROCESS_FILE(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_file_name    IN VARCHAR2,
    p_run_num      IN NUMBER
  ) RETURN VARCHAR2 IS
    -- Variables
    v_file_pk               NUMBER;
    v_initial_audit_pk      NUMBER;
    v_validation_audit_pk   NUMBER;
    v_validation_result     PKG_DTC_VALIDATION.t_file_validation_result;
    v_staging_result        PKG_DTC_VALIDATION.t_file_validation_result;
    v_final_status          VARCHAR2(20);
    v_initial_audit_status  VARCHAR2(20);
    v_validation_audit_status VARCHAR2(20);
    v_error_msg             VARCHAR2(4000);
    v_job_name              VARCHAR2(100);
    v_network_id            VARCHAR2(100);

    -- Computed staging count variables (to avoid BOOLEAN in SQL CASE)
    v_succ_cnt              NUMBER := 0;
    v_fail_cnt              NUMBER := 0;
    v_rej_cnt               NUMBER := 0;
    v_stg_rec_cnt           NUMBER := 0;
    v_stg_flow_cnt          NUMBER := 0;
    v_stg_err_rec_cnt       NUMBER := 0;
    v_stg_err_flow_cnt      NUMBER := 0;
    v_stg_rej_rec_cnt       NUMBER := 0;
    v_stg_rej_flow_cnt      NUMBER := 0;

  BEGIN
    -- ============================================================================
    -- STEP 1: Initialize - Generate FILE_PK using sequence
    -- ============================================================================
    SELECT SEQ_MDQ_ETL_FILE.NEXTVAL INTO v_file_pk FROM DUAL;

    -- ============================================================================
    -- STEP 2: Create Initial Audit Entry (status = RUNNING)
    -- ============================================================================
    PRC_CREATE_AUDIT(
      p_file_pk    => v_file_pk,
      p_job_name   => 'PKG_DTC_PROCESSING',
      p_parent_job => NULL,
      p_status     => C_AUD_RUNNING,
      p_audit_pk   => v_initial_audit_pk
    );
    COMMIT;  -- Commit audit entry to ensure it persists

    -- ============================================================================
    -- STEP 2A: Validate mandatory input parameters
    -- ============================================================================
    IF p_flow_type IS NULL OR LENGTH(TRIM(p_flow_type)) = 0 THEN
      v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8013', 'Flow Type');
      PRC_LOG_ERROR(v_file_pk, 0, v_error_msg, 'flowType', p_flow_type);
      PRC_UPDATE_AUDIT(v_initial_audit_pk, C_AUD_ERROR, 0, 0, 0, 0);
      COMMIT;
      RETURN C_STATUS_REJECTED;
    END IF;

    -- ============================================================================
    -- STEP 3: Validate File (Stage 1 and Stage 2 structure validation)
    -- ============================================================================
    BEGIN
      IF NOT PKG_DTC_VALIDATION.FN_VALIDATE_FILE_V2(
        p_file_content => p_file_content,
        p_flow_type    => p_flow_type,
        p_result       => v_validation_result
      ) THEN
        -- Validation failed but we still have partial results to process
        NULL;
      END IF;
    EXCEPTION
      WHEN OTHERS THEN
        v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8038', SQLERRM);
        PRC_LOG_ERROR(v_file_pk, 0, v_error_msg, 'validation');
        PRC_UPDATE_AUDIT(v_initial_audit_pk, C_AUD_ERROR, 0, 0, 0, 0);
        COMMIT;
        RETURN C_STATUS_REJECTED;
    END;

    -- ============================================================================
    -- STEP 3A: Get Network ID from recipient ID (position 6 in header)
    -- ============================================================================
    BEGIN
      SELECT nta_mpan_cd
      INTO v_network_id
      FROM MDQ_APP_NTWKAREA_REF
      WHERE nta_term = v_validation_result.header_data.dstn_mp_id;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        v_network_id := NULL;  -- Network ID not found for this recipient
      WHEN OTHERS THEN
        v_network_id := NULL;  -- Handle any other exceptions gracefully
    END;

    -- ============================================================================
    -- STEP 4: Insert File Record into MDQ_ETL_FILE
    -- ============================================================================
    INSERT INTO MDQ_ETL_FILE (
      FIL_FILE_PK,
      FIL_FILE_NAME,
      FIL_FILE_TYPE,
      FIL_FLOW_VERSION,
      FIL_SRC_MP_ROLE,
      FIL_SRC_MP_ID,
      FIL_DSTN_MP_ROLE,
      FIL_DSTN_MP_ID,
      FIL_DATA_DT,
      FIL_NETWORK_ID,
      FIL_INP_OUT_IND,
      FIL_REC_CNT,
      FIL_LOAD_STUS,
      FIL_STG_LOAD_RUN_NUM,
      FIL_FLOW_CNT,
      FIL_STG_LOAD_DTTM,
      FIL_MP_FILE_ID,
      FIL_STG_REC_CNT,
      FIL_STG_FLOW_CNT,
      FIL_STG_ERR_REC_CNT,
      FIL_STG_ERR_FLOW_CNT,
      FIL_STG_REJ_REC_CNT,
      FIL_STG_REJ_FLOW_CNT,
      FIL_APP_RUN_NUM,
      FIL_APP_PROC_DTTM,
      FIL_APP_SUC_REC_CNT,
      FIL_APP_ERR_REC_CNT,
      FIL_APP_REJ_REC_CNT,
      FIL_CR_DTTM
    ) VALUES (
      v_file_pk,
      CASE WHEN LENGTH(p_file_name) > 40 THEN SUBSTR(p_file_name, 1, 40) ELSE p_file_name END,
      CASE WHEN LENGTH(v_validation_result.header_data.flow_type) > 10 THEN NULL ELSE v_validation_result.header_data.flow_type END,
      CASE WHEN LENGTH(v_validation_result.header_data.flow_version) > 3 THEN NULL ELSE v_validation_result.header_data.flow_version END,
      CASE WHEN LENGTH(v_validation_result.header_data.src_mp_role) > 1 THEN NULL ELSE v_validation_result.header_data.src_mp_role END,
      CASE WHEN LENGTH(v_validation_result.header_data.src_mp_id) > 4 THEN NULL ELSE v_validation_result.header_data.src_mp_id END,
      CASE WHEN LENGTH(v_validation_result.header_data.dstn_mp_role) > 1 THEN NULL ELSE v_validation_result.header_data.dstn_mp_role END,
      CASE WHEN LENGTH(v_validation_result.header_data.dstn_mp_id) > 4 THEN NULL ELSE v_validation_result.header_data.dstn_mp_id END,
      v_validation_result.header_data.data_dt,
      CASE WHEN LENGTH(v_network_id) > 2 THEN NULL ELSE v_network_id END,  -- FIL_NETWORK_ID from MDQ_APP_NTWKAREA_REF
      'I',   -- FIL_INP_OUT_IND hardcoded to 'I'
      CASE WHEN v_validation_result.footer_data.record_count > 9999999999 THEN NULL ELSE v_validation_result.footer_data.record_count END,
      v_validation_result.status,
      p_run_num,
      CASE WHEN v_validation_result.footer_data.flow_count > 9999999999 THEN NULL ELSE v_validation_result.footer_data.flow_count END,
      NULL,  -- FIL_STG_LOAD_DTTM updated later in Step 8
      CASE WHEN LENGTH(v_validation_result.header_data.file_identifier) > 10 THEN NULL ELSE v_validation_result.header_data.file_identifier END,
      v_validation_result.staged_rec_count,
      v_validation_result.staged_flow_count,
      v_validation_result.rejected_rec_count,
      v_validation_result.rejected_flow_count,
      v_validation_result.rejected_rec_count,
      v_validation_result.rejected_flow_count,
      NULL,  -- FIL_APP_RUN_NUM
      NULL,  -- FIL_APP_PROC_DTTM
      NULL,  -- FIL_APP_SUC_REC_CNT
      NULL,  -- FIL_APP_ERR_REC_CNT
      NULL,  -- FIL_APP_REJ_REC_CNT
      SYSDATE
    );

    -- File name overflow: log error, update file status and reject
    IF p_file_name IS NOT NULL AND LENGTH(p_file_name) > 40 THEN
      v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8015', 'File Name', TO_CHAR(LENGTH(p_file_name)), '40');
      PRC_LOG_ERROR(v_file_pk, 0, v_error_msg, 'fileName', p_file_name);
      UPDATE MDQ_ETL_FILE
        SET FIL_LOAD_STUS = C_STATUS_REJECTED,
            FIL_STG_LOAD_DTTM = SYSTIMESTAMP
        WHERE FIL_FILE_PK = v_file_pk;
      PRC_UPDATE_AUDIT(v_initial_audit_pk, C_AUD_ERROR, 0, 0, 0, 0);
      COMMIT;
      RETURN C_STATUS_REJECTED;
    END IF;

    -- ============================================================================
    -- STEP 5: Insert Validation Errors into MDQ_ETL_ERROR
    -- Only log when Stage 1 failed; when Stage 1 passes the flow package re-runs
    -- Stage 2 validation in Step 6 and logs its own errors, avoiding duplicates.
    -- ============================================================================
    IF NOT v_validation_result.stage1_passed AND v_validation_result.errors IS NOT NULL AND v_validation_result.errors.COUNT > 0 THEN
      FOR i IN v_validation_result.errors.FIRST .. v_validation_result.errors.LAST LOOP
        INSERT INTO MDQ_ETL_ERROR (
          ERR_PK,
          ERR_FILE_PK,
          ERR_JOB_ID,
          ERR_RUN_NUM,
          ERR_FILE_ROW_NUM,
          ERR_FILE_COL,
          ERR_FILE_COL_VAL,
          ERR_TIMESTAMP,
          ERR_MSG_TEXT
        ) VALUES (
          SEQ_ERROR.NEXTVAL,
          v_file_pk,
          -1,
          C_RUN_NUM,
          v_validation_result.errors(i).line_number,
          SUBSTR(v_validation_result.errors(i).field_name, 1, 100),
          SUBSTR(v_validation_result.errors(i).field_value, 1, 500),
          SYSDATE,
          v_validation_result.errors(i).error_message
        );
      END LOOP;
    END IF;

    -- ============================================================================
    -- STEP 6: Process Staging (only if Stage 1 passed)
    -- ============================================================================
    IF v_validation_result.stage1_passed THEN
      -- Create validation audit entry before calling flow package
      v_job_name := 'PKG_DTC_' || p_flow_type;
      PRC_CREATE_AUDIT(
        p_file_pk    => v_file_pk,
        p_job_name   => v_job_name,
        p_parent_job => 'PKG_DTC_PROCESSING',
        p_status     => C_AUD_RUNNING,
        p_audit_pk   => v_validation_audit_pk
      );
      COMMIT;  -- Commit audit before flow processing

      -- Call flow-specific package
      BEGIN
        IF p_flow_type = 'D0010' THEN
          PKG_DTC_D0010.PRC_PROCESS_FILE_V2(
            p_file_pk      => v_file_pk,
            p_file_content => p_file_content,
            p_flow_type    => p_flow_type,
            p_result       => v_staging_result
          );
        ELSIF p_flow_type = 'D0150' THEN
          PKG_DTC_D0150.PRC_PROCESS_FILE_V2(
            p_file_pk      => v_file_pk,
            p_file_content => p_file_content,
            p_flow_type    => p_flow_type,
            p_result       => v_staging_result
          );
        ELSE
          -- Unsupported flow type
          v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8042', p_flow_type);
          RAISE_APPLICATION_ERROR(-20001, v_error_msg);
        END IF;

        -- Insert staging errors from flow package (may differ from validation errors)
        IF v_staging_result.errors IS NOT NULL AND v_staging_result.errors.COUNT > 0 THEN
          FOR i IN v_staging_result.errors.FIRST .. v_staging_result.errors.LAST LOOP
            INSERT INTO MDQ_ETL_ERROR (
              ERR_PK,
              ERR_FILE_PK,
              ERR_JOB_ID,
              ERR_RUN_NUM,
              ERR_FILE_ROW_NUM,
              ERR_FILE_COL,
              ERR_FILE_COL_VAL,
              ERR_TIMESTAMP,
              ERR_MSG_TEXT
            ) VALUES (
              SEQ_ERROR.NEXTVAL,
              v_file_pk,
              -1,
              C_RUN_NUM,
              v_staging_result.errors(i).line_number,
              SUBSTR(v_staging_result.errors(i).field_name, 1, 100),
              SUBSTR(v_staging_result.errors(i).field_value, 1, 500),
              SYSDATE,
              v_staging_result.errors(i).error_message
            );
          END LOOP;
        END IF;

        -- Determine final file status: REJECTED if any rejections, STAGING only if all clean
        IF v_staging_result.rejected_flow_count > 0 OR v_staging_result.rejected_rec_count > 0 THEN
          v_final_status := C_STATUS_REJECTED;
        ELSE
          v_final_status := v_staging_result.status;
        END IF;

        -- Determine validation audit status based on final file status
        IF v_final_status = C_STATUS_STAGING THEN
          v_validation_audit_status := C_AUD_SUCCESSFUL;  -- All data loaded clean
        ELSIF (v_staging_result.staged_flow_count = 0 OR v_staging_result.staged_rec_count = 0)
              AND (v_staging_result.rejected_flow_count > 0 OR v_staging_result.rejected_rec_count > 0) THEN
          v_validation_audit_status := C_AUD_ERROR;  -- All flows/records rejected
        ELSE
          v_validation_audit_status := C_AUD_WARNING;  -- Partial rejection
        END IF;

        -- Update validation audit with success/warning
        PRC_UPDATE_AUDIT(
          p_audit_pk     => v_validation_audit_pk,
          p_status       => v_validation_audit_status,
          p_rec_proc_cnt => v_staging_result.staged_rec_count + v_staging_result.rejected_rec_count,
          p_rec_succ_cnt => v_staging_result.staged_rec_count,
          p_rec_fail_cnt => v_staging_result.rejected_rec_count,
          p_rec_rej_cnt  => v_staging_result.rejected_rec_count
        );
        COMMIT;

      EXCEPTION
        WHEN OTHERS THEN
          -- Rollback staging data only
          ROLLBACK;

          -- Log error
          v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8002', p_flow_type, SQLERRM);
          PRC_LOG_ERROR(v_file_pk, 0, v_error_msg, 'staging');

          -- Update validation audit to ERROR
          PRC_UPDATE_AUDIT(v_validation_audit_pk, C_AUD_ERROR, 0, 0, 0, 0);

          -- Update file status to REJECTED
          UPDATE MDQ_ETL_FILE
          SET FIL_LOAD_STUS = C_STATUS_REJECTED
          WHERE FIL_FILE_PK = v_file_pk;

          COMMIT;

          v_final_status := C_STATUS_REJECTED;
      END;
    ELSE
      -- Stage 1 failed - no staging performed
      v_final_status := C_STATUS_REJECTED;
    END IF;

    -- ============================================================================
    -- STEP 7: Update Initial Audit with final status
    -- ============================================================================
    -- Determine initial audit status based on final result
    -- Use v_staging_result (actual staging outcome) for consistency with validation audit
    IF v_final_status = C_STATUS_STAGING THEN
      v_initial_audit_status := C_AUD_SUCCESSFUL;  -- All data loaded clean
    ELSIF (v_staging_result.staged_flow_count = 0 OR v_staging_result.staged_rec_count = 0)
          AND (v_staging_result.rejected_flow_count > 0 OR v_staging_result.rejected_rec_count > 0) THEN
      v_initial_audit_status := C_AUD_ERROR;  -- All flows/records rejected
    ELSIF v_staging_result.rejected_flow_count > 0 OR v_staging_result.rejected_rec_count > 0 THEN
      v_initial_audit_status := C_AUD_WARNING;  -- Partial rejection
    ELSE
      v_initial_audit_status := C_AUD_ERROR;  -- Stage 1 failed (no staging performed)
    END IF;

    -- Compute counts from staging result (actual) or validation result (fallback)
    IF v_validation_result.stage1_passed THEN
      v_succ_cnt         := NVL(v_staging_result.staged_rec_count, 0);
      v_fail_cnt         := NVL(v_staging_result.rejected_rec_count, 0);
      v_rej_cnt          := NVL(v_staging_result.rejected_rec_count, 0);
      v_stg_rec_cnt      := NVL(v_staging_result.staged_rec_count, 0);
      v_stg_flow_cnt     := NVL(v_staging_result.staged_flow_count, 0);
      v_stg_err_rec_cnt  := NVL(v_staging_result.rejected_rec_count, 0);
      v_stg_err_flow_cnt := NVL(v_staging_result.rejected_flow_count, 0);
      v_stg_rej_rec_cnt  := NVL(v_staging_result.rejected_rec_count, 0);
      v_stg_rej_flow_cnt := NVL(v_staging_result.rejected_flow_count, 0);
    ELSE
      v_succ_cnt         := 0;
      v_fail_cnt         := NVL(v_validation_result.rejected_rec_count, 0);
      v_rej_cnt          := NVL(v_validation_result.rejected_rec_count, 0);
      v_stg_rec_cnt      := 0;
      v_stg_flow_cnt     := 0;
      v_stg_err_rec_cnt  := NVL(v_validation_result.rejected_rec_count, 0);
      v_stg_err_flow_cnt := NVL(v_validation_result.rejected_flow_count, 0);
      v_stg_rej_rec_cnt  := NVL(v_validation_result.rejected_rec_count, 0);
      v_stg_rej_flow_cnt := NVL(v_validation_result.rejected_flow_count, 0);
    END IF;

    PRC_UPDATE_AUDIT(
      p_audit_pk     => v_initial_audit_pk,
      p_status       => v_initial_audit_status,
      p_rec_proc_cnt => CASE WHEN v_validation_result.footer_data.record_count > 9999999999 THEN NULL ELSE v_validation_result.footer_data.record_count END,
      p_rec_succ_cnt => v_succ_cnt,
      p_rec_fail_cnt => v_fail_cnt,
      p_rec_rej_cnt  => v_rej_cnt
    );

    -- ============================================================================
    -- STEP 8: Update File Record with final load timestamp
    -- ============================================================================
    UPDATE MDQ_ETL_FILE
    SET FIL_LOAD_STUS     = v_final_status,
        FIL_STG_LOAD_DTTM = SYSTIMESTAMP,
        FIL_STG_REC_CNT      = v_stg_rec_cnt,
        FIL_STG_FLOW_CNT     = v_stg_flow_cnt,
        FIL_STG_ERR_REC_CNT  = v_stg_err_rec_cnt,
        FIL_STG_ERR_FLOW_CNT = v_stg_err_flow_cnt,
        FIL_STG_REJ_REC_CNT  = v_stg_rej_rec_cnt,
        FIL_STG_REJ_FLOW_CNT = v_stg_rej_flow_cnt
    WHERE FIL_FILE_PK = v_file_pk;

    COMMIT;

    -- ============================================================================
    -- STEP 9: Return final status
    -- ============================================================================
    RETURN v_final_status;

  EXCEPTION
    WHEN OTHERS THEN
      -- Critical exception handler
      ROLLBACK;

      -- Log critical error
      v_error_msg := PKG_DTC_COMMON.FN_FORMAT_ERROR('ERR8005', SQLERRM);

      BEGIN
        PRC_LOG_ERROR(v_file_pk, 0, v_error_msg, 'processing');

        -- Update initial audit to ABORTED if it exists
        IF v_initial_audit_pk IS NOT NULL THEN
          PRC_UPDATE_AUDIT(v_initial_audit_pk, C_AUD_ABORTED, 0, 0, 0, 0);
        END IF;

        COMMIT;  -- Commit error records only
      EXCEPTION
        WHEN OTHERS THEN
          --NULL;  -- Suppress secondary exceptions
        logger_wrapper('PRC_PROCESS_FILE', 1, 'Unexpected error' || SQLERRM);
      END;

      RETURN C_STATUS_REJECTED;
  END PRC_PROCESS_FILE;

END PKG_DTC_PROCESSING;
/