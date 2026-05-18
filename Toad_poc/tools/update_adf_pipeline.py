"""
Updates ADF pipeline PL_Toad_POC to:
1. Add Job Type to SQL query
2. Add Populate_Excel_Template WebActivity after Copy_ReportData_To_Blob
3. Update Copy_Archive_File to copy .xlsm instead of .csv
"""

import subprocess, json, sys

FACTORY     = "adf-toad-poc"
RG          = "rg-toad-poc"
PIPELINE    = "PL_Toad_POC"
FUNC_KEY    = sys.argv[1]
FUNC_URL    = f"https://func-toad-poc.azurewebsites.net/api/populate_template?code={FUNC_KEY}"
LA_URL      = (
    "https://prod-20.uksouth.logic.azure.com:443/workflows/a494dc2a42ec491b8d914af8749d4f50"
    "/triggers/manual/paths/invoke?api-version=2016-06-01"
    "&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0"
    "&sig=tBu6x8My_5vrYVuct7oVgQ9HYnVspEYTfH7twZ_0k5A"
)

SQL_QUERY = (
    "SELECT\n"
    "    sub.[Network], sub.[LDZ], sub.[Depot],\n"
    "    sub.[Work Order], sub.[Job Type], sub.[Root Work Order],\n"
    "    sub.[Emergency Date], sub.[Gas Prevented],\n"
    "    sub.[Time Difference], sub.[Address],\n"
    "    CASE WHEN sub.[Gas Prevented] > DATEFROMPARTS(YEAR(DATEADD(DAY,-1,GETDATE())), MONTH(DATEADD(DAY,-1,GETDATE())), 1) THEN 1 ELSE 0 END AS [MTD],\n"
    "    CASE WHEN sub.[Time Difference] <= 12 THEN 1 ELSE 0 END AS [Less 12],\n"
    "    CASE WHEN sub.[Time Difference] > 12  THEN 1 ELSE 0 END AS [Great 12],\n"
    "    1 AS [Count]\n"
    "FROM (\n"
    "    SELECT\n"
    "        dorg.network AS [Network], dorg.ldz AS [LDZ],\n"
    "        CASE WHEN dorg.depot_work_group = 'DEPOT_K' THEN 'DEPOT_L' ELSE dorg.depot_work_group END AS [Depot],\n"
    "        prev_dwor.work_order_number AS [Work Order],\n"
    "        dwor.job_type AS [Job Type],\n"
    "        dwor.work_order_number AS [Root Work Order],\n"
    "        dwor.reported_date_time AS [Emergency Date],\n"
    "        DATEADD(SECOND, DATEDIFF(SECOND,'00:00:00', CAST(RIGHT(dtim.hour_24_minute,8) AS TIME)), CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATETIME2)) AS [Gas Prevented],\n"
    "        ROUND(CAST(DATEDIFF(MINUTE, dwor.reported_date_time, DATEADD(SECOND, DATEDIFF(SECOND,'00:00:00', CAST(RIGHT(dtim.hour_24_minute,8) AS TIME)), CAST(CONVERT(DATE, dcal.date_disp_1, 103) AS DATETIME2))) AS FLOAT)/60, 2) AS [Time Difference],\n"
    "        dadr.display_address AS [Address]\n"
    "    FROM abcbimart.fct_gas_escapes_v ge\n"
    "        JOIN abcbimart.dim_work_orders  dwor      ON ge.dwor_id_root               = dwor.id\n"
    "        JOIN abcbimart.dim_work_orders  prev_dwor ON ge.dwor_id_gas_prevented      = prev_dwor.id\n"
    "        JOIN abcbimart.dim_organisation dorg      ON ge.dorg_id_root               = dorg.id\n"
    "        JOIN abcbimart.dim_addresses    dadr      ON ge.dadr_id_root               = dadr.id\n"
    "        JOIN abcbimart.dim_calendar     dcal      ON ge.dcal_id_gas_prevented_date = dcal.id\n"
    "        JOIN abcbimart.dim_time         dtim      ON ge.dtim_id_gas_prevented_time = dtim.id\n"
    "    WHERE ge.latest = 'Y'\n"
    "      AND dcal.date_oracle >= DATEADD(MONTH, 3, DATEFROMPARTS(YEAR(DATEADD(MONTH,-3,DATEADD(DAY,-4,GETDATE()))),1,1))\n"
    "      AND dcal.date_oracle <  CAST(GETDATE() AS DATE)\n"
    ") sub"
)

pipeline_def = {
    "description": "Toad POC pipeline — migrated from Toad automation script",
    "parameters": {
        "logic_app_email_url": {
            "type": "string",
            "defaultValue": LA_URL
        }
    },
    "variables": {
        "report_date": {"type": "String"}
    },
    "activities": [
        {
            "name": "Lookup_ODS_Refresh_Check",
            "type": "Lookup",
            "policy": {"timeout": "0.00:05:00", "retry": 1, "retryIntervalInSeconds": 30},
            "typeProperties": {
                "source": {
                    "type": "AzureSqlSource",
                    "sqlReaderQuery": "SELECT COUNT(*) AS row_count FROM MAXRPD.T_ODS_LOG WHERE CAST(ems AS DATE) = CAST(GETDATE() AS DATE)",
                    "queryTimeout": "00:05:00"
                },
                "dataset": {"referenceName": "DS_AzureSQL_ODS_Log", "type": "DatasetReference"},
                "firstRowOnly": True
            }
        },
        {
            "name": "SetVar_ReportDate",
            "type": "SetVariable",
            "dependsOn": [{"activity": "Lookup_ODS_Refresh_Check", "dependencyConditions": ["Succeeded"]}],
            "typeProperties": {
                "variableName": "report_date",
                "value": {"value": "@formatDateTime(addDays(utcNow(), -1), 'dd.MM.yyyy')", "type": "Expression"}
            }
        },
        {
            "name": "If_ODS_Refreshed",
            "type": "IfCondition",
            "dependsOn": [{"activity": "SetVar_ReportDate", "dependencyConditions": ["Succeeded"]}],
            "typeProperties": {
                "expression": {
                    "value": "@greater(activity('Lookup_ODS_Refresh_Check').output.firstRow.ROW_COUNT, 0)",
                    "type": "Expression"
                },
                "ifFalseActivities": [
                    {
                        "name": "Email_ODS_Not_Refreshed",
                        "type": "WebActivity",
                        "typeProperties": {
                            "url": {"value": "@pipeline().parameters.logic_app_email_url", "type": "Expression"},
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {"value": "@concat('{\"subject\":\"Toad POC - Daily Report For_', variables('report_date'), '\",\"to\":\"operations-distribution@abc.co.uk\",\"body\":\"ODS data has not been refreshed today. Report cannot be generated.\"}')", "type": "Expression"}
                        }
                    }
                ],
                "ifTrueActivities": [
                    {
                        "name": "Copy_ReportData_To_Blob",
                        "type": "Copy",
                        "policy": {"timeout": "0.01:00:00", "retry": 1, "retryIntervalInSeconds": 30},
                        "typeProperties": {
                            "source": {
                                "type": "AzureSqlSource",
                                "sqlReaderQuery": {"value": SQL_QUERY, "type": "Expression"},
                                "queryTimeout": "00:30:00"
                            },
                            "sink": {
                                "type": "DelimitedTextSink",
                                "storeSettings": {"type": "AzureBlobStorageWriteSettings"},
                                "formatSettings": {"type": "DelimitedTextWriteSettings", "quoteAllText": True, "fileExtension": ".csv"}
                            },
                            "enableStaging": False
                        },
                        "inputs":  [{"referenceName": "DS_AzureSQL_GasEscapes", "type": "DatasetReference"}],
                        "outputs": [{"referenceName": "DS_Blob_Excel_Output", "type": "DatasetReference",
                                     "parameters": {"file_name": {"value": "@concat('BC_BIMIO_267_PRECOPY_', variables('report_date'), '.csv')", "type": "Expression"}}}]
                    },
                    {
                        "name": "Populate_Excel_Template",
                        "type": "WebActivity",
                        "dependsOn": [{"activity": "Copy_ReportData_To_Blob", "dependencyConditions": ["Succeeded"]}],
                        "typeProperties": {
                            "url": FUNC_URL,
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {
                                "value": "@concat('{\"report_date\":\"', variables('report_date'), '\",\"csv_blob\":\"output/BC_BIMIO_267_PRECOPY_', variables('report_date'), '.csv\",\"out_blob\":\"output/BC_BIMIO_267_PRECOPY_', variables('report_date'), '.xlsm\"}')",
                                "type": "Expression"
                            }
                        }
                    },
                    {
                        "name": "Copy_Archive_File",
                        "type": "Copy",
                        "dependsOn": [{"activity": "Populate_Excel_Template", "dependencyConditions": ["Succeeded"]}],
                        "typeProperties": {
                            "source": {"type": "DelimitedTextSource", "storeSettings": {"type": "AzureBlobStorageReadSettings"}, "formatSettings": {"type": "DelimitedTextReadSettings"}},
                            "sink":   {"type": "DelimitedTextSink",   "storeSettings": {"type": "AzureBlobStorageWriteSettings"}, "formatSettings": {"type": "DelimitedTextWriteSettings", "quoteAllText": True, "fileExtension": ".xlsm"}},
                            "enableStaging": False
                        },
                        "inputs":  [{"referenceName": "DS_Blob_Excel_Output", "type": "DatasetReference",
                                     "parameters": {"file_name": {"value": "@concat('BC_BIMIO_267_PRECOPY_', variables('report_date'), '.xlsm')", "type": "Expression"}}}],
                        "outputs": [{"referenceName": "DS_Blob_Archive", "type": "DatasetReference",
                                     "parameters": {"archive_file_name": {"value": "@concat('BIMIO267_12Hour_Prevented_Daily_For_', variables('report_date'), '.xlsm')", "type": "Expression"}}}]
                    },
                    {
                        "name": "Email_Report_To_Operations",
                        "type": "WebActivity",
                        "dependsOn": [{"activity": "Copy_Archive_File", "dependencyConditions": ["Succeeded"]}],
                        "typeProperties": {
                            "url": {"value": "@pipeline().parameters.logic_app_email_url", "type": "Expression"},
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {"value": "@concat('{\"subject\":\"Toad POC - Daily Report For_', variables('report_date'), '\",\"to\":\"operations-distribution@abc.co.uk\",\"attachment_path\":\"toad-poc-reports/archive/BIMIO267_12Hour_Prevented_Daily_For_', variables('report_date'), '.xlsm\"}')", "type": "Expression"}
                        }
                    },
                    {
                        "name": "Email_Confirmation_To_BI_Team",
                        "type": "WebActivity",
                        "dependsOn": [{"activity": "Email_Report_To_Operations", "dependencyConditions": ["Succeeded"]}],
                        "typeProperties": {
                            "url": {"value": "@pipeline().parameters.logic_app_email_url", "type": "Expression"},
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {"value": "@concat('{\"subject\":\"Toad POC For_', variables('report_date'), ' - Has Run and Been Emailed\",\"to\":\"buin@abc.co.uk\",\"body\":\"Pipeline completed successfully.\"}')", "type": "Expression"}
                        }
                    }
                ]
            }
        }
    ]
}

import tempfile, os

AZ_CMD = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
json.dump(pipeline_def, tmp)
tmp.close()

try:
    result = subprocess.run(
        [AZ_CMD, "datafactory", "pipeline", "create",
         "--factory-name", FACTORY,
         "--resource-group", RG,
         "--name", PIPELINE,
         "--pipeline", f"@{tmp.name}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("Pipeline updated successfully.")
    else:
        print("ERROR:", result.stderr)
        sys.exit(1)
finally:
    os.unlink(tmp.name)
