# mock_data

Mock CSV files simulating the output ADF would write to blob storage for each report.

## Folder structure

```
mock_data/
  Daily_BIMIO_267/        ← 12 Hour Gas Prevented Daily
  Daily_BIMIO_523/        ← SC Repair Workorders (Scotland)
  Monthly_BIMIO_494/      ← E1/E2/M1/M2 Created Manually
  Weekly__BIMIO_384/      ← Long Job Report
```

## File naming

Files follow the same convention the Azure Function expects from blob storage:

```
{report_name}_{report_date}.csv
```

e.g. `Daily_BIMIO_267_27.05.2026.csv`

## Column source

Each CSV's columns are derived directly from the `REPORT_MAIN` SQL query stored in
`config.report_sql` for that report (see `reports/{report}/config/{report}_config_data.sql`).

## Using mock data for local testing

To test the Azure Function locally without ADF, upload a mock CSV to the report's
blob container and call the function:

```powershell
# Upload mock CSV to blob
az storage blob upload `
  --account-name sttoadpoc `
  --container-name daily-bimio-267 `
  --name "output_csv/Daily_BIMIO_267_27.05.2026.csv" `
  --file "mock_data/Daily_BIMIO_267/Daily_BIMIO_267_27.05.2026.csv" `
  --auth-mode login

# Trigger the function
curl -X POST https://<func-app>.azurewebsites.net/api/excel_writer \
  -H "Content-Type: application/json" \
  -d '{"report_name":"Daily_BIMIO_267","report_date":"27.05.2026"}'
```

## Report column summary

| Report | Key columns |
|--------|-------------|
| Daily_BIMIO_267 | Network, LDZ, Depot, Work Order, Emergency Date, Gas Prevented, Time Difference, Address, MTD, Less 12, Great 12 |
| Daily_BIMIO_523 | Work Order, Depot, Asset, Description, Gas in Property, Component, Corrective Action, Cause flags (Corrosion/Fracture/Failure), Status, Location, Material, Diameter |
| Monthly_BIMIO_494 | Workorder, Job Type, ID, Name, Reported Date, Job Priority, Reported By Group |
| Weekly__BIMIO_384 | LDZ, Depot, Workstream, Engineer, Engineer Name, Team Manager, Workorder No., Job Type, Priority, Actual Start/Finish, Time On Site, Duration |
