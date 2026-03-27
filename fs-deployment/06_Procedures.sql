 create or replace PROCEDURE logger(
  p_caller IN VARCHAR2,
  p_code IN INTEGER,
  p_description IN VARCHAR2,
  p_rowcount IN NUMBER DEFAULT NULL
)
IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO MDQ_APP_LOG_TABLE(ID, DTM, CALLER, CODE, DESCRIPTION, NUMROWS)
  VALUES(LOG_SEQ.nextval, sysdate, p_caller, p_code, p_description, p_rowcount);
  COMMIT;
END;
 
 create or replace PROCEDURE logger_wrapper(
  p_caller      IN VARCHAR2,
  p_code        IN INTEGER,
  p_description IN VARCHAR2,
  p_rowcount    IN NUMBER DEFAULT NULL,
  p_enable_log  IN BOOLEAN DEFAULT TRUE
)
IS
BEGIN
  IF p_enable_log THEN
     logger(p_caller, p_code, p_description, p_rowcount);
  END IF;
END;


CREATE OR REPLACE EDITIONABLE PROCEDURE "MDQA_OWNER"."PRC_DTC_PROCESS_FILE_WRAPPER" (
    p_file_content IN CLOB,
    p_flow_type    IN VARCHAR2,
    p_file_name    IN VARCHAR2,
    p_run_num      IN NUMBER
)
IS
p_result VARCHAR2(50);
BEGIN
Delete From DTC_PROCESSING_STATUS;
    -- Call the original function
    p_result := PKG_DTC_PROCESSING.PRC_PROCESS_FILE(
        p_file_content,
        p_flow_type,
        p_file_name,
        p_run_num
    );
    insert into DTC_PROCESSING_STATUS Values (p_result);
    Commit;
EXCEPTION
    WHEN OTHERS THEN
    Rollback;
    insert into DTC_PROCESSING_STATUS Values ('ERROR');
    Commit;
END PRC_DTC_PROCESS_FILE_WRAPPER;

/
