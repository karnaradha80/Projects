--------------------------------------------------------
--  Sequence Cache Update — MAVIS DTC Staging
--  Run as: MDQA_OWNER user (or DBA)
--
--  Purpose: Set CACHE 500 on all high-volume staging sequences.
--           NOCACHE causes a redo log write on every NEXTVAL call.
--           For large files (~400k rows) this was the dominant
--           bottleneck (~150s out of ~165s total processing time).
--
--  Safe to run on live databases — ALTER SEQUENCE takes effect
--  immediately, no downtime required, no data is affected.
--  Surrogate PK gaps may occur on instance restart (acceptable).
--------------------------------------------------------

-- D0010 staging sequences
ALTER SEQUENCE STG_D0010_026_SEQ CACHE 500;
ALTER SEQUENCE STG_D0010_028_SEQ CACHE 500;
ALTER SEQUENCE STG_D0010_030_SEQ CACHE 500;

-- D0150 staging sequences
ALTER SEQUENCE STG_D0150_288_SEQ CACHE 500;
ALTER SEQUENCE STG_D0150_290_SEQ CACHE 500;

-- Verify
SELECT sequence_name, cache_size
FROM user_sequences
WHERE sequence_name IN (
    'STG_D0010_026_SEQ',
    'STG_D0010_028_SEQ',
    'STG_D0010_030_SEQ',
    'STG_D0150_288_SEQ',
    'STG_D0150_290_SEQ'
)
ORDER BY sequence_name;
