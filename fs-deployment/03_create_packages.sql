--------------------------------------------------------
--  DDL for Packages - MAVIS DTC Staging
--  Run as: MDQA_OWNER user
--  Order: PKG_DTC_COMMON -> PKG_DTC_VALIDATION -> PKG_DTC_D0010 -> PKG_DTC_D0150 -> PKG_DTC_PROCESSING
--------------------------------------------------------

SET SERVEROUTPUT ON

-- ============================================
-- 1. PKG_DTC_COMMON - Specification
-- ============================================

@@"PKG_DTC_COMMON.pks"

-- ============================================
-- 1. PKG_DTC_COMMON - Body
-- ============================================

@@"PKG_DTC_COMMON.pkb"

PROMPT PKG_DTC_COMMON created successfully.

-- ============================================
-- 2. PKG_DTC_VALIDATION - Specification
-- ============================================

@@"PKG_DTC_VALIDATION_v2.pks"

-- ============================================
-- 2. PKG_DTC_VALIDATION - Body
-- ============================================

@@"PKG_DTC_VALIDATION_v2_complete.pkb"

PROMPT PKG_DTC_VALIDATION created successfully.

-- ============================================
-- 3. PKG_DTC_D0010 - Specification
-- ============================================

@@"PKG_DTC_D0010.pks"

-- ============================================
-- 3. PKG_DTC_D0010 - Body
-- ============================================

@@"PKG_DTC_D0010.pkb"

PROMPT PKG_DTC_D0010 created successfully.

-- ============================================
-- 4. PKG_DTC_D0150 - Specification
-- ============================================

@@"PKG_DTC_D0150.pks"

-- ============================================
-- 4. PKG_DTC_D0150 - Body
-- ============================================

@@"PKG_DTC_D0150.pkb"

PROMPT PKG_DTC_D0150 created successfully.

-- ============================================
-- 5. PKG_DTC_PROCESSING - Specification
-- ============================================

@@"PKG_DTC_PROCESSING.pks"

-- ============================================
-- 5. PKG_DTC_PROCESSING - Body
-- ============================================

@@"PKG_DTC_PROCESSING.pkb"

PROMPT PKG_DTC_PROCESSING created successfully.

-- ============================================
-- Verify Package Creation
-- ============================================

SELECT object_name, object_type, status
FROM user_objects
WHERE object_type IN ('PACKAGE', 'PACKAGE BODY')
AND object_name LIKE 'PKG_DTC%'
ORDER BY object_name, object_type;
/
