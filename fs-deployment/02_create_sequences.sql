--------------------------------------------------------
--  DDL for Sequences - MAVIS DTC Staging
--  Run as: MDQA_OWNER user
--------------------------------------------------------

-- ============================================
-- Common Sequences
-- ============================================

-- SEQ_MDQ_ETL_FILE - File PK sequence
CREATE SEQUENCE SEQ_MDQ_ETL_FILE
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    NOCACHE
    NOORDER
    NOCYCLE;

-- SEQ_AUDIT - Audit PK sequence
CREATE SEQUENCE SEQ_AUDIT
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    NOCACHE
    NOORDER
    NOCYCLE;

-- SEQ_ERROR - Error PK sequence
CREATE SEQUENCE SEQ_ERROR
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    NOCACHE
    NOORDER
    NOCYCLE;

-- MEVC_SEQ - Validation config PK sequence
CREATE SEQUENCE MEVC_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    NOCACHE
    NOORDER
    NOCYCLE;

-- ============================================
-- D0010 Sequences
-- ============================================

-- STG_D0010_026_SEQ - Group 026 PK sequence
CREATE SEQUENCE STG_D0010_026_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    CACHE 500
    NOORDER
    NOCYCLE;

-- STG_D0010_028_SEQ - Group 028 PK sequence
CREATE SEQUENCE STG_D0010_028_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    CACHE 500
    NOORDER
    NOCYCLE;

-- STG_D0010_030_SEQ - Group 030 PK sequence
CREATE SEQUENCE STG_D0010_030_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    CACHE 500
    NOORDER
    NOCYCLE;

-- ============================================
-- D0150 Sequences
-- ============================================

-- STG_D0150_288_SEQ - Group 288 PK sequence
CREATE SEQUENCE STG_D0150_288_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    CACHE 500
    NOORDER
    NOCYCLE;

-- STG_D0150_290_SEQ - Group 290 PK sequence
CREATE SEQUENCE STG_D0150_290_SEQ
    MINVALUE 1
    MAXVALUE 999999999999999999999999999
    INCREMENT BY 1
    START WITH 1
    CACHE 500
    NOORDER
    NOCYCLE;

 --------------------------------------------------------
--  DDL for Sequence SEQ_ETL_RUN
--------------------------------------------------------
CREATE SEQUENCE  SEQ_ETL_RUN
  MINVALUE 1 
  MAXVALUE 999999999999999999999999999 
  INCREMENT BY 1 
  START WITH 1 
  NOCACHE  
  NOORDER  
  NOCYCLE;
   

COMMIT;
/
