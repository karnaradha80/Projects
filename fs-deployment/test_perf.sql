ALTER SESSION SET CONTAINER = XEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = MDQA_OWNER;
SET SERVEROUTPUT ON;

DECLARE
  v_file_content CLOB;
  v_flow_type    VARCHAR2(50)  := 'D0010';
  v_file_name    VARCHAR2(100) := 'Claude_Testing_D0010Test1.txt';
  v_run_num      NUMBER        := 18;
  v_result       VARCHAR2(4000);
BEGIN
  SELECT filedata INTO v_file_content FROM TBD_SRC_DATA;

  v_result := PKG_DTC_PROCESSING.PRC_PROCESS_FILE(
    p_file_content => v_file_content,
    p_flow_type    => v_flow_type,
    p_file_name    => v_file_name,
    p_run_num      => v_run_num
  );

  DBMS_OUTPUT.PUT_LINE('Result: ' || v_result);
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
/

SELECT FIL_FILE_PK, ROUND((FIL_STG_LOAD_DTTM - FIL_CR_DTTM) * 86400, 1) AS seconds
FROM MDQ_ETL_FILE
ORDER BY FIL_FILE_PK DESC
FETCH FIRST 3 ROWS ONLY;
EXIT;
