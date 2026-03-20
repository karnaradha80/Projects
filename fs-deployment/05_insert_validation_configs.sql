--------------------------------------------------------
--  Insert Validation Configs for D0010, D0150 and D0302
--  Using CLOB handling for large JSON strings
--------------------------------------------------------

SET SERVEROUTPUT ON

DECLARE
  v_json_config CLOB;
  v_pk NUMBER;
BEGIN

  -- ========================================
  -- Insert D0150 Validation Config
  -- ========================================
  DBMS_OUTPUT.PUT_LINE('Inserting D0150 validation config...');

  -- Build JSON as CLOB
  v_json_config := '{
  "flowType": "D0150",
  "version": 1,
  "allowPartialProcessing": false,
  "header": {
    "identifier": "ZHV",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 10},
      {"position": 2, "name": "flowName", "mandatory": true, "minLength": 8, "maxLength": 8, "pattern": "^D0150002$"},
      {"position": 3, "name": "senderRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 4, "name": "senderId", "mandatory": true, "minLength": 4, "maxLength": 4},
      {"position": 5, "name": "recipientRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 6, "name": "recipientId", "mandatory": true, "minLength": 4, "maxLength": 4, "pattern": "^(LOND|SEEB|EELC|EDFI)$"},
      {"position": 7, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "footer": {
    "identifier": "ZPT",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 10},
      {"position": 2, "name": "recordCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 4, "name": "flowCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 5, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "groups": [
    {
      "groupId": "288",
      "parentGroup": null,
      "tableName": "STAGE_D0150_288",
      "fields": [
        {"position": 1, "name": "MPAN", "column": "STG_288_MPAN", "mandatory": true, "dataType": "NUMBER", "minLength": 13, "maxLength": 13, "precision": 13, "scale": 0},
        {"position": 2, "name": "MeasurementSystemTransferDate", "column": "STG_288_MSMTD", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 3, "name": "MeterConfigurationId", "column": "STG_288_MC_ID", "mandatory": false, "minLength": 0, "maxLength": 1},
        {"position": 4, "name": "MeterSerialEquipmentStatus", "column": "STG_288_MSES", "mandatory": true, "minLength": 1, "maxLength": 1}
      ]
    },
    {
      "groupId": "289",
      "parentGroup": "288",
      "tableName": "STAGE_D0150_289",
      "fields": [
        {"position": 1, "name": "SupplierContractorId", "column": "STG_289_SCON_ID", "mandatory": true, "minLength": 4, "maxLength": 4},
        {"position": 2, "name": "SupplierContractorDate", "column": "STG_289_SCON_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 3, "name": "MeterSerialNumbersFromContractorId", "column": "STG_289_MSNSFC_ID", "mandatory": false, "minLength": 0, "maxLength": 10},
        {"position": 4, "name": "MeterSerialNumbersFromContractorDate", "column": "STG_289_MSNSFC_DT", "mandatory": false, "dataType": "DATE", "minLength": 0, "maxLength": 8, "format": "YYYYMMDD"}
      ]
    },
    {
      "groupId": "290",
      "parentGroup": "288",
      "tableName": "STAGE_D0150_290",
      "fields": [
        {"position": 1, "name": "MeterId", "column": "STG_290_MTR_ID", "mandatory": true, "minLength": 1, "maxLength": 10},
        {"position": 2, "name": "MeterCOP", "column": "STG_290_MTR_COP", "mandatory": false, "minLength": 0, "maxLength": 3},
        {"position": 3, "name": "MeterCOPDisplacement", "column": "STG_290_MTR_COP_DISP", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 3, "precision": 3, "scale": 0},
        {"position": 4, "name": "MeterCurrentRating", "column": "STG_290_MTR_CUR_RATING", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 3, "precision": 3, "scale": 0},
        {"position": 5, "name": "MeterLocation", "column": "STG_290_MTR_LOC", "mandatory": true, "minLength": 1, "maxLength": 1},
        {"position": 6, "name": "ManufacturersMakeAndType", "column": "STG_290_MANF_MAKE_TYPE", "mandatory": true, "minLength": 1, "maxLength": 60},
        {"position": 7, "name": "MeterAssetProviderId", "column": "STG_290_MTR_ASST_PROV_ID", "mandatory": true, "minLength": 4, "maxLength": 4},
        {"position": 8, "name": "CommunicationsAddress", "column": "STG_290_COMMS_ADDR", "mandatory": false, "minLength": 0, "maxLength": 65},
        {"position": 9, "name": "CommunicationsMethod", "column": "STG_290_COMMS_MTHD", "mandatory": false, "minLength": 0, "maxLength": 2},
        {"position": 10, "name": "OutstationPIN", "column": "STG_290_OUTSTN_PIN", "mandatory": false, "minLength": 0, "maxLength": 12},
        {"position": 11, "name": "OutstationCOP", "column": "STG_290_OUTSTN_COP", "mandatory": false, "minLength": 0, "maxLength": 20},
        {"position": 12, "name": "OutstationCOPDispensation", "column": "STG_290_OUTSTN_COP_DISP", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 3, "precision": 3, "scale": 0},
        {"position": 13, "name": "OutstationEncryptionKey", "column": "STG_290_OUTSTN_ENCRYP", "mandatory": false, "minLength": 0, "maxLength": 20},
        {"position": 14, "name": "OutstationNumberOfChannels", "column": "STG_290_OUTSTN_CHANNELS", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 3, "precision": 3, "scale": 0},
        {"position": 15, "name": "OutstationPasswordLevel1", "column": "STG_290_OUTSTN_PSWD", "mandatory": false, "minLength": 0, "maxLength": 12},
        {"position": 16, "name": "OutstationType", "column": "STG_290_OUTSTN_TYPE", "mandatory": false, "minLength": 0, "maxLength": 3},
        {"position": 17, "name": "VTRatio", "column": "STG_290_VT_RATIO", "mandatory": false, "minLength": 0, "maxLength": 10},
        {"position": 18, "name": "MeterType", "column": "STG_290_MTR_TYPE", "mandatory": true, "minLength": 1, "maxLength": 5},
        {"position": 19, "name": "DateOfMeterInstallation", "column": "STG_290_MTR_INSTLN_DT", "mandatory": false, "dataType": "DATE", "minLength": 0, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 20, "name": "CertificationDate", "column": "STG_290_CERT_DT", "mandatory": false, "dataType": "DATE", "minLength": 0, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 21, "name": "CertificationExpiryDate", "column": "STG_290_CERT_EXPIRY_DT", "mandatory": false, "dataType": "DATE", "minLength": 0, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 22, "name": "TimingDeviceId", "column": "STG_290_TIMING_DEV_ID", "mandatory": false, "minLength": 0, "maxLength": 10},
        {"position": 23, "name": "TeleSwitchClockIndicator", "column": "STG_290_TELE_SWITCH_ID", "mandatory": false, "minLength": 0, "maxLength": 1},
        {"position": 24, "name": "RetrievalMethod", "column": "STG_290_RTVL_MTHD", "mandatory": true, "minLength": 1, "maxLength": 1},
        {"position": 25, "name": "RetrievalMethodEffectiveDate", "column": "STG_290_RTVL_MTHD_EFF_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"}
      ]
    },
    {
      "groupId": "291",
      "parentGroup": "290",
      "tableName": "STAGE_D0150_291",
      "fields": [
        {"position": 1, "name": "CTRatio", "column": "STG_291_CT_RATIO", "mandatory": true, "minLength": 1, "maxLength": 6}
      ]
    },
    {
      "groupId": "293",
      "parentGroup": "290",
      "tableName": "STAGE_D0150_293",
      "fields": [
        {"position": 1, "name": "MeterRegisterId", "column": "STG_293_MTR_REG_ID", "mandatory": true, "minLength": 1, "maxLength": 2},
        {"position": 2, "name": "MeterRegisterType", "column": "STG_293_MTR_REG_TYPE", "mandatory": true, "minLength": 1, "maxLength": 1},
        {"position": 3, "name": "MQId", "column": "STG_293_MQ_ID", "mandatory": true, "minLength": 1, "maxLength": 2},
        {"position": 4, "name": "MeterRegisterMultiplier", "column": "STG_293_MTR_REG_MULTIPLIER", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 9, "scale": 2},
        {"position": 5, "name": "MainCheckIndicator", "column": "STG_293_MAIN_CHECK_ID", "mandatory": false, "minLength": 0, "maxLength": 1},
        {"position": 6, "name": "NumberOfRegisterDigits", "column": "STG_293_REG_DIGITS", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 1, "precision": 1, "scale": 0},
        {"position": 7, "name": "AssociatedMeterId", "column": "STG_293_ASSC_MTR_ID", "mandatory": false, "minLength": 0, "maxLength": 10},
        {"position": 8, "name": "AssociatedMeterRegisterId", "column": "STG_293_ASSC_MTR_REG_ID", "mandatory": false, "minLength": 0, "maxLength": 2}
      ]
    },
    {
      "groupId": "295",
      "parentGroup": "290",
      "tableName": "STAGE_D0150_295",
      "fields": [
        {"position": 1, "name": "ChannelNumber", "column": "STG_295_CHANNEL_NUM", "mandatory": false, "minLength": 0, "maxLength": 3},
        {"position": 2, "name": "MQId", "column": "STG_295_MQ_ID", "mandatory": false, "minLength": 0, "maxLength": 2},
        {"position": 3, "name": "PulseMultiplier", "column": "STG_295_PULSE_MULTIPLIER", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 10, "precision": 9, "scale": 6}
      ]
    },
    {
      "groupId": "296",
      "parentGroup": "290",
      "tableName": "STAGE_D0150_296",
      "fields": [
        {"position": 1, "name": "MaintenanceDate", "column": "STG_296_MAINT_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 2, "name": "MaintenanceDescription", "column": "STG_296_MAINT_DESC", "mandatory": true, "minLength": 1, "maxLength": 200}
      ]
    },
    {
      "groupId": "762",
      "parentGroup": "288",
      "tableName": "STAGE_D0150_762",
      "fields": [
        {"position": 1, "name": "MaintenanceDate", "column": "STG_762_MAINT_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 2, "name": "MaintenanceDescription", "column": "STG_762_MAINT_DESC", "mandatory": true, "minLength": 1, "maxLength": 200}
      ]
    },
    {
      "groupId": "08A",
      "parentGroup": "288",
      "tableName": "STAGE_D0150_08A",
      "fields": [
        {"position": 1, "name": "MeterId", "column": "STG_08A_MTR_ID", "mandatory": true, "minLength": 1, "maxLength": 10},
        {"position": 2, "name": "MeterRemovalDate", "column": "STG_08A_MTR_REMOVAL_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 3, "name": "MeterAssetProviderId", "column": "STG_08A_MTR_ASST_PROV_ID", "mandatory": true, "minLength": 1, "maxLength": 4}
      ]
    }
  ]
}';

  INSERT INTO MDQ_ETL_VALIDATION_CONFIG (
    MEVC_PK,
    MEVC_FLOW_TYPE,
    MEVC_CONFIG_VERSION,
    MEVC_CONFIG_JSON,
    MEVC_ACTIVE_YN,
    MEVC_CR_USER,
    MEVC_CR_DTTM,
    MEVC_NOTES
  ) VALUES (
    MEVC_SEQ.NEXTVAL,
    'D0150',
    1,
    v_json_config,
    'Y',
    USER,
    SYSDATE,
    'Initial D0150 validation configuration'
  ) RETURNING MEVC_PK INTO v_pk;

  DBMS_OUTPUT.PUT_LINE('D0150 config inserted with PK: ' || v_pk);

  -- ========================================
  -- Insert D0302 Validation Config
  -- ========================================
  DBMS_OUTPUT.PUT_LINE('Inserting D0302 validation config...');

  v_json_config := '{
  "flowType": "D0302",
  "version": 1,
  "allowPartialProcessing": false,
  "header": {
    "identifier": "ZHV",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 20},
      {"position": 2, "name": "flowName", "mandatory": true, "minLength": 8, "maxLength": 8, "pattern": "^D0302\\\\d{3}$"},
      {"position": 3, "name": "senderRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 4, "name": "senderId", "mandatory": true, "minLength": 4, "maxLength": 4},
      {"position": 5, "name": "recipientRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 6, "name": "recipientId", "mandatory": true, "minLength": 4, "maxLength": 4, "pattern": "^(LOND|SEEB|EELC|EDFI)$"},
      {"position": 7, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "footer": {
    "identifier": "ZPT",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 20},
      {"position": 2, "name": "recordCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 4, "name": "flowCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 5, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "groups": [
    {
      "groupId": "68C",
      "parentGroup": null,
      "tableName": "STAGE_D0302_68C",
      "minOccurrences": 1,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "MPAN", "column": "STG_68C_MPAN", "mandatory": true, "dataType": "NUMBER", "minLength": 13, "maxLength": 13, "precision": 13, "scale": 0},
        {"position": 2, "name": "RegistrationDate", "column": "STG_68C_REGI_DT", "mandatory": true, "dataType": "DATE", "minLength": 8, "maxLength": 8, "format": "YYYYMMDD"}
      ]
    },
    {
      "groupId": "69C",
      "parentGroup": "68C",
      "tableName": "STAGE_D0302_69C",
      "minOccurrences": 0,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "CustomerName", "column": "STG_69C_CUST_NAME", "mandatory": true, "minLength": 1, "maxLength": 100},
        {"position": 2, "name": "AdditionalInfo", "column": "STG_69C_ADD_INFO", "mandatory": false, "minLength": 0, "maxLength": 200},
        {"position": 3, "name": "CustomerPassword", "column": "STG_69C_CUST_PSWD", "mandatory": false, "minLength": 0, "maxLength": 10},
        {"position": 4, "name": "CustomerPasswordDate", "column": "STG_69C_CUST_PSWD_DT", "mandatory": false, "dataType": "DATE", "minLength": 0, "maxLength": 8, "format": "YYYYMMDD"},
        {"position": 5, "name": "SpecialAccess", "column": "STG_69C_SPECIAL_ACCESS", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 6, "name": "MPR", "column": "STG_69C_MPR", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 6, "precision": 6, "scale": 0}
      ]
    },
    {
      "groupId": "70C",
      "parentGroup": "68C",
      "tableName": "STAGE_D0302_70C",
      "minOccurrences": 0,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "MailAddressDeliveryIndicator", "column": "STG_70C_MAIL_ADDR_DEL_IND", "mandatory": false, "minLength": 0, "maxLength": 1},
        {"position": 2, "name": "MailAddressLine1", "column": "STG_70C_MAIL_ADDR_LINE_1", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 3, "name": "MailAddressLine2", "column": "STG_70C_MAIL_ADDR_LINE_2", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 4, "name": "MailAddressLine3", "column": "STG_70C_MAIL_ADDR_LINE_3", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 5, "name": "MailAddressLine4", "column": "STG_70C_MAIL_ADDR_LINE_4", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 6, "name": "MailAddressLine5", "column": "STG_70C_MAIL_ADDR_LINE_5", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 7, "name": "MailAddressLine6", "column": "STG_70C_MAIL_ADDR_LINE_6", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 8, "name": "MailAddressLine7", "column": "STG_70C_MAIL_ADDR_LINE_7", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 9, "name": "MailAddressLine8", "column": "STG_70C_MAIL_ADDR_LINE_8", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 10, "name": "MailAddressLine9", "column": "STG_70C_MAIL_ADDR_LINE_9", "mandatory": false, "minLength": 0, "maxLength": 40},
        {"position": 11, "name": "MailAddressPostcode", "column": "STG_70C_MAIL_ADDR_PCODE", "mandatory": false, "minLength": 0, "maxLength": 10}
      ]
    },
    {
      "groupId": "15J",
      "parentGroup": "68C",
      "tableName": "STAGE_D0302_15J",
      "minOccurrences": 0,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "ContactName", "column": "STG_15J_CONT_NAME", "mandatory": true, "minLength": 1, "maxLength": 50},
        {"position": 2, "name": "CustomerPreferredContactMethod", "column": "STG_15J_CUST_PREF_CONT_MTHD", "mandatory": false, "minLength": 0, "maxLength": 1}
      ]
    },
    {
      "groupId": "16J",
      "parentGroup": "15J",
      "tableName": "STAGE_D0302_16J",
      "minOccurrences": 0,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "ContactTelNumber", "column": "STG_16J_CONT_TEL_NUM", "mandatory": true, "minLength": 1, "maxLength": 14},
        {"position": 2, "name": "ContactFaxNumber", "column": "STG_16J_CONT_FAX_NUM", "mandatory": false, "minLength": 0, "maxLength": 14}
      ]
    },
    {
      "groupId": "17J",
      "parentGroup": "15J",
      "tableName": "STAGE_D0302_17J",
      "minOccurrences": 0,
      "maxOccurrences": null,
      "fields": [
        {"position": 1, "name": "ContactEmail", "column": "STG_17J_CONT_EMAIL", "mandatory": true, "minLength": 1, "maxLength": 100}
      ]
    }
  ]
}';

  INSERT INTO MDQ_ETL_VALIDATION_CONFIG (
    MEVC_PK,
    MEVC_FLOW_TYPE,
    MEVC_CONFIG_VERSION,
    MEVC_CONFIG_JSON,
    MEVC_ACTIVE_YN,
    MEVC_CR_USER,
    MEVC_CR_DTTM,
    MEVC_NOTES
  ) VALUES (
    MEVC_SEQ.NEXTVAL,
    'D0302',
    1,
    v_json_config,
    'Y',
    USER,
    SYSDATE,
    'Initial D0302 validation configuration'
  ) RETURNING MEVC_PK INTO v_pk;

  DBMS_OUTPUT.PUT_LINE('D0302 config inserted with PK: ' || v_pk);

  -- ========================================
  -- Insert D0010 Validation Config
  -- ========================================
  DBMS_OUTPUT.PUT_LINE('Inserting D0010 validation config...');

  v_json_config := '{
  "flowType": "D0010",
  "version": 1,
   "header": {
    "identifier": "ZHV",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 10},
      {"position": 2, "name": "flowName", "mandatory": true, "minLength": 8, "maxLength": 8, "pattern": "^D0010002$"},
      {"position": 3, "name": "senderRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 4, "name": "senderId", "mandatory": true, "minLength": 4, "maxLength": 4},
      {"position": 5, "name": "recipientRole", "mandatory": true, "minLength": 1, "maxLength": 1},
      {"position": 6, "name": "recipientId", "mandatory": true, "minLength": 4, "maxLength": 4, "pattern": "^(LOND|SEEB|EELC|EDFI)$"},
      {"position": 7, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "footer": {
    "identifier": "ZPT",
    "fields": [
      {"position": 1, "name": "fileIdentifier", "mandatory": true, "minLength": 1, "maxLength": 10},
      {"position": 2, "name": "recordCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 4, "name": "flowCount", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 10, "scale": 0},
      {"position": 5, "name": "timestamp", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"}
    ]
  },
  "groups": [
    {
      "groupId": "026",
      "parentGroup": null,
      "tableName": "STAGE_D0010_026",
      "fields": [
        {"position": 1, "name": "MPAN", "column": "STG_026_MPAN", "mandatory": true, "dataType": "NUMBER", "minLength": 13, "maxLength": 13, "precision": 13, "scale": 0},
        {"position": 2, "name": "BSCValidationStatus", "column": "STG_026_BSC_VLDN_STATUS", "mandatory": true, "minLength": 1, "maxLength": 1}
      ]
    },
    {
      "groupId": "027",
      "parentGroup": "026",
      "tableName": "STAGE_D0010_027",
      "fields": [
        {"position": 1, "name": "SiteVisitCheck", "column": "STG_027_SITE_VISIT_CHECK", "mandatory": true, "minLength": 2, "maxLength": 2},
        {"position": 2, "name": "AdditionalInfo", "column": "STG_027_ADD_INFO", "mandatory": false, "minLength": 0, "maxLength": 200}
      ]
    },
    {
      "groupId": "028",
      "parentGroup": "026",
      "tableName": "STAGE_D0010_028",
      "fields": [
        {"position": 1, "name": "MeterId", "column": "STG_028_MTR_ID", "mandatory": true, "minLength": 1, "maxLength": 10},
        {"position": 2, "name": "ReadingType", "column": "STG_028_READING_TYPE", "mandatory": true, "minLength": 1, "maxLength": 1}
      ]
    },
    {
      "groupId": "029",
      "parentGroup": "028",
      "tableName": "STAGE_D0010_029",
      "fields": [
        {"position": 1, "name": "SiteVisitCheck", "column": "STG_029_SITE_VISIT_CHECK", "mandatory": true, "minLength": 2, "maxLength": 2},
        {"position": 2, "name": "AdditionalInfo", "column": "STG_029_ADD_INFO", "mandatory": false, "minLength": 0, "maxLength": 200}
      ]
    },
    {
      "groupId": "030",
      "parentGroup": "028",
      "tableName": "STAGE_D0010_030",
      "fields": [
        {"position": 1, "name": "MeterRegisterId", "column": "STG_030_MTR_REG_ID", "mandatory": true, "minLength": 1, "maxLength": 2},
        {"position": 2, "name": "ReadDateTime", "column": "STG_030_READ_DTTM", "mandatory": true, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"},
        {"position": 3, "name": "ReadValue", "column": "STG_030_READ_VAL", "mandatory": true, "dataType": "NUMBER", "minLength": 1, "maxLength": 10, "precision": 9, "scale": 1},
        {"position": 4, "name": "MaxDemandResetDateTime", "column": "STG_030_MD_RESET_DTTM", "mandatory": false, "dataType": "DATETIME", "minLength": 14, "maxLength": 14, "format": "YYYYMMDDHH24MISS"},
        {"position": 5, "name": "MaxDemandResetNumber", "column": "STG_030_MD_RESET_NUM", "mandatory": false, "dataType": "NUMBER", "minLength": 0, "maxLength": 20, "precision": 20, "scale": 0},
        {"position": 6, "name": "ReadIndicator", "column": "STG_030_READ_IND", "mandatory": false, "minLength": 0, "maxLength": 1},
        {"position": 7, "name": "ReadingMethod", "column": "STG_030_READING_MTHD", "mandatory": true, "minLength": 1, "maxLength": 1}
      ]
    },
    {
      "groupId": "032",
      "parentGroup": "030",
      "tableName": "STAGE_D0010_032",
      "fields": [
        {"position": 1, "name": "ReadReasonCode", "column": "STG_032_READ_REASON_CODE", "mandatory": true, "minLength": 2, "maxLength": 2},
        {"position": 2, "name": "ReadStatus", "column": "STG_032_READ_STATUS", "mandatory": true, "minLength": 1, "maxLength": 1}
      ]
    },
    {
      "groupId": "033",
      "parentGroup": "030",
      "tableName": "STAGE_D0010_033",
      "fields": [
        {"position": 1, "name": "SiteVisitCheck", "column": "STG_033_SITE_VISIT_CHECK", "mandatory": true, "minLength": 2, "maxLength": 2},
        {"position": 2, "name": "AdditionalInfo", "column": "STG_033_ADD_INFO", "mandatory": false, "minLength": 0, "maxLength": 200}
      ]
    }
  ]
}';

  INSERT INTO MDQ_ETL_VALIDATION_CONFIG (
    MEVC_PK,
    MEVC_FLOW_TYPE,
    MEVC_CONFIG_VERSION,
    MEVC_CONFIG_JSON,
    MEVC_ACTIVE_YN,
    MEVC_CR_USER,
    MEVC_CR_DTTM,
    MEVC_NOTES
  ) VALUES (
    MEVC_SEQ.NEXTVAL,
    'D0010',
    1,
    v_json_config,
    'Y',
    USER,
    SYSDATE,
    'Initial D0010 validation configuration'
  ) RETURNING MEVC_PK INTO v_pk;

  DBMS_OUTPUT.PUT_LINE('D0010 config inserted with PK: ' || v_pk);

  COMMIT;
  DBMS_OUTPUT.PUT_LINE('All validation configs inserted successfully!');

EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
    RAISE;
END;
/

-- Verify insertions
SELECT MEVC_PK,
       MEVC_FLOW_TYPE,
       MEVC_CONFIG_VERSION,
       MEVC_ACTIVE_YN,
       LENGTH(MEVC_CONFIG_JSON) as JSON_SIZE,
       MEVC_CR_DTTM,
       MEVC_NOTES
FROM MDQ_ETL_VALIDATION_CONFIG
ORDER BY MEVC_FLOW_TYPE, MEVC_CONFIG_VERSION;
