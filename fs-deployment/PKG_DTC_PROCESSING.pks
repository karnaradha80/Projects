CREATE OR REPLACE EDITIONABLE PACKAGE "MDQA_OWNER"."PKG_DTC_PROCESSING" AS
  -- ============================================================================
  -- Package: PKG_DTC_PROCESSING
  -- Purpose: Process DTC files directly from CLOB content
  --
  -- Main function accepts file content as CLOB and processes it through:
  -- 1. Validation (Stage 1 and Stage 2)
  -- 2. Staging to appropriate flow tables (D0010 or D0150)
  -- 3. Comprehensive audit trail with RUNNING/SUCCESSFUL/WARNING/ABORTED statuses
  --
  -- Returns: 'STAGING' if file accepted, 'REJECTED' if file rejected
  -- ============================================================================
  --
  --  CHANGE HISTORY
  --  =================
  --    DATE               WHO                    DESCRIPTION
  --  ==========   ================  ===============================================
  --  05/Feb/2026   Danie             Initial version
  --  10/Feb/2026   Radha             Cosmetic cleanup, no logic change
  -- ============================================================================

  -- Main processing function
  -- Parameters:
  --   p_file_content: CLOB containing the file content to process
  --   p_flow_type: Flow type (D0010 or D0150)
  --   p_file_name: Original file name for tracking
  --   p_run_num: Run number for FIL_STG_LOAD_RUN_NUM
  -- Returns: 'STAGING' or 'REJECTED'
  FUNCTION PRC_PROCESS_FILE(
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_file_name    IN VARCHAR2,
    p_run_num      IN NUMBER
  ) RETURN VARCHAR2;

END PKG_DTC_PROCESSING;
/