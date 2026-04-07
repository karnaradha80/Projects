# MAVIS Faster Staging — Cutover Plan
**Project:** MAVIS Faster Staging (D0010 & D0150)
**Version:** 0.2 — Draft
**Author:** Danie Selvaraju
**Cutover Date:** Saturday 11 April 2026
**Cutover Window:** Friday 10/04/2026 20:00 → Saturday 11/04/2026 17:00

---

## Key Contacts

| Name | Role |
|------|------|
| Peter Waymont | Income Services Manager |
| Neal Medley | Income Processes and Projects Manager (Systems) |
| Shivendra & Praveen | nxzen BAU — MPR Publication |
| nxzen DBA | RMAN Backup |
| nxzen Project Team + nxzen BAU | Deployment |

---

## Server Reference

| Server | Purpose |
|--------|---------|
| ukpnmvsprds31 | DataStage server |
| ukpnmvsprdb31 | MAVIS Application database |
| ukpnmvsprdm31 | MAVIS Datamart database |
| UKPNIMIBXPRMQ31, UKPNIMIBXPRMQ32 | eWAY application servers |
| 10.2.100.4, 10.2.100.5, 10.2.102.4 | GoAnywhere servers |
| BOP | Publication reporting server |

---

## Key Folder Paths (Production)

| Purpose | Path |
|---------|------|
| GoAnywhere pickup (eWAY drops files here) | `/dstage/projects/MAVIS_PROD/inbox_gaw` |
| GoAnywhere trigger file folder | `/dstage/projects/MAVIS_PROD/gaw_file_trigger` |
| DataStage inbox / archive / rejected | `/dstage/projects/MAVIS_PROD/inbox`, `/archive`, `/rejected` |

---

## PRE-CUTOVER CHECKLIST
> These activities **must be completed before cutover day**. They require lead time and cannot be done on the day.

| # | Activity | Owner | Server/Target | Due By |
|---|----------|-------|---------------|--------|
| PC-1 | Raise GoAnywhere firewall change request. Source: GoAnywhere servers 10.2.100.4, 10.2.100.5, 10.2.102.4. Destination 1: ukpnmvsprds31 port 22 (SSH). Destination 2: ukpnmvsprdb31 port 1525 (Oracle). | nxzen Project Team + nxzen BAU | Network/Infra team | At least 5 business days before cutover |
| PC-2 | Obtain and confirm email distribution list for GoAnywhere job alert notifications | nxzen Project Team + nxzen BAU | — | At least 2 business days before cutover |
| PC-3 | Prepare and review GoAnywhere job configuration (including email alerts) in non-prod environment | nxzen Project Team + nxzen BAU | GoAnywhere non-prod | At least 2 business days before cutover |
| PC-4 | Confirm RMAN backup schedule with DBA team (window: 11/04/2026 10:00–14:00) | nxzen DBA | ukpnmvsprdb31, ukpnmvsprdm31 | At least 2 business days before cutover |
| PC-5 | Confirm PAT participants (Peter / Neal / Sinida) are available on Saturday 11/04/2026 from 17:00 | nxzen Project Team | — | At least 2 business days before cutover |

---

## PHASE 1 — PREPARATION (Friday 10 April 2026)

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 1 | Request Control-M to put the D0010 and D0150 staging jobs on hold so no new files are picked up during the cutover window | nxzen BAU | ukpnmvsprds31 | 10/04/2026 20:00 | Confirm acknowledgement from Control-M team before proceeding |

---

## PHASE 2 — VERIFICATION & BACKUP (Saturday 11 April 2026)

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 2 | Wait for Friday overnight batch job to complete successfully before starting any deployment activity | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 10:00 | Do not proceed until confirmed |
| 3 | Confirm that the MPR (Meter Point Registration) Publication Report has run and completed successfully | nxzen BAU (Shivendra & Praveen) | BOP | 11/04/2026 10:00 | Obtain written confirmation |
| 4 | Verify the Saturday load completed successfully — check row counts and error logs | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 10:00 | |
| 5 | Take RMAN hot backup of the MAVIS Application database and Datamart database | nxzen DBA | ukpnmvsprdb31, ukpnmvsprdm31 | 11/04/2026 10:00 – 14:00 | Backup runs in the background. Phases 3, 4 and 5 may proceed in parallel during backup window. Do NOT proceed to Phase 6 until backup is confirmed complete. |

---

## PHASE 3 — DATABASE DEPLOYMENT
> Can run in parallel with Phases 4 and 5 during RMAN backup window.

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 6 | Create/Modify the required validation configuration table (MDQ_ETL_VALIDATION_CONFIG) and any other table-level changes (e.g. new columns, constraints) | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 10:00 | |
| 7 | Create application database views, stored procedures and packages (PKG_DTC_VALIDATION, PKG_DTC_D0010, PKG_DTC_D0150) | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 11:00 | |
| 8 | Run insert scripts for reference data: MDQ_APP_MSG_REF and MDQ_ETL_VALIDATION_CONFIG JSON configuration for D0010 and D0150 | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 11:30 | |
| 9 | Compile all modified and new packages and procedures in the MAVIS application schema | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 12:00 | |
| 10 | Verify all modified and new packages and procedures are in VALID compiled state — run a query against USER_OBJECTS to confirm no INVALID objects | nxzen Project Team + nxzen BAU | ukpnmvsprdb31 | 11/04/2026 12:30 | Abort and raise issue if any objects remain INVALID |

---

## PHASE 4 — DATASTAGE DEPLOYMENT
> Can run in parallel with Phases 3 and 5 during RMAN backup window.

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 11 | Take a backup of all impacted DataStage jobs before making any changes | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 10:00 | Export job definitions as a rollback safety net |
| 12 | Verify the existing DataStage folder structure is in place: inbox, archive and rejected folders for D0010 and D0150 | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 10:00 | |
| 13 | Create the GoAnywhere pickup folder and trigger file folder on the DataStage server for D0010 and D0150. Paths: `/dstage/projects/MAVIS_PROD/inbox_gaw` and `/dstage/projects/MAVIS_PROD/gaw_file_trigger` | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 10:30 | Ensure correct UNIX permissions so that both DataStage and GoAnywhere processes can read/write. **Use MAVIS_PROD — not MAVIS_DEV_MHHS.** |
| 14 | Deploy updated DataStage jobs — apply changes to route D0010 and D0150 files to the new `inbox_gaw` folder and to write trigger files to `gaw_file_trigger` on staging completion | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 11:00 | |
| 15 | Compile all modified DataStage jobs | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 12:30 | |
| 16 | Verify all modified DataStage jobs are in compiled state — no compile errors | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 13:00 | |

---

## PHASE 5 — eWAY DEPLOYMENT
> Can run in parallel with Phases 3 and 4 during RMAN backup window.

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 17 | Back up existing .ear files and note current JMS queue configuration on both eWAY servers before making any changes | nxzen Project Team + nxzen BAU | UKPNIMIBXPRMQ31, UKPNIMIBXPRMQ32 | 11/04/2026 10:00 | Required as a rollback point |
| 18 | Regenerate the .ear files on both eWAY production servers and update the MAVIS application, including changes to the JMS queues used for D0010 and D0150 file processing (eWAY will now deliver files to `/dstage/projects/MAVIS_PROD/inbox_gaw`) | nxzen Project Team + nxzen BAU | UKPNIMIBXPRMQ31, UKPNIMIBXPRMQ32 | 11/04/2026 10:30 | |
| 19 | Validate MAVIS subscriptions and ensure all applications and adapters are running correctly after .ear deployment | nxzen Project Team + nxzen BAU | UKPNIMIBXPRMQ31, UKPNIMIBXPRMQ32 | 11/04/2026 11:00 | |
| 20 | Restart both eWAY servers to ensure all changes take full effect | nxzen Project Team + nxzen BAU | UKPNIMIBXPRMQ31, UKPNIMIBXPRMQ32 | 11/04/2026 12:00 | Coordinate restart to avoid simultaneous downtime on both nodes |

---

## PHASE 6 — GOANYWHERE SETUP & END-TO-END TEST
> Start after RMAN backup is confirmed complete (target: 14:00).

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 21 | Confirm GoAnywhere firewall rules are active — verify SSH (port 22) connectivity to ukpnmvsprds31 and Oracle (port 1525) connectivity to ukpnmvsprdb31 from GoAnywhere servers | nxzen Project Team + nxzen BAU | 10.2.100.4, 10.2.100.5, 10.2.102.4 | 11/04/2026 14:00 | Firewall request must have been raised pre-cutover (PC-1). Raise P1 incident if connectivity fails. |
| 22 | Configure GoAnywhere job in production: set source folder to `/dstage/projects/MAVIS_PROD/inbox_gaw`, configure Oracle stored procedure call, set trigger file path `/dstage/projects/MAVIS_PROD/gaw_file_trigger`, and configure email alerts using the approved distribution list | nxzen Project Team + nxzen BAU | 10.2.100.4, 10.2.100.5, 10.2.102.4 | 11/04/2026 14:00 | |
| 23 | Place a sample D0010 and D0150 test file in the GoAnywhere source folder and verify: (a) file is picked up by GoAnywhere, (b) Oracle stored procedure is called, (c) data is staged correctly in the STAGE_ tables, (d) trigger file is created in `gaw_file_trigger` by DataStage, (e) trigger file is deleted by GoAnywhere after processing, (f) file is archived/rejected appropriately | nxzen Project Team + nxzen BAU | ukpnmvsprds31 | 11/04/2026 14:30 | This validates the full end-to-end flow before PAT |

---

## PHASE 7 — BUSINESS PAT (User Acceptance)

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 24 | Send checkpoint email to business stakeholders confirming the application is ready for PAT | nxzen Project Team | — | 11/04/2026 17:00 | Include summary of what was deployed and what to test |
| 25 | PAT performed by business stakeholders — validate D0010 and D0150 data in MAVIS is accessible and accurate | Peter / Neal / Sinida | — | 11/04/2026 17:00 | Business to follow agreed PAT script |
| 26 | Receive written confirmation from business stakeholders that PAT is complete and sign-off is given to go live | Peter / Neal / Sinida | — | 11/04/2026 17:00 | **Do not proceed to Phase 8 without sign-off** |

---

## PHASE 8 — GO-LIVE

| Step | Activity | Owner | Server | Target Time | Remarks |
|------|----------|-------|--------|-------------|---------|
| 27 | Request Control-M to put the Saturday UC018 job on hold — this prevents the legacy DataStage staging job from running while the new GoAnywhere/stored procedure flow goes live | nxzen BAU | ukpnmvsprds31 | After PAT sign-off | |
| 28 | Request Control-M to release the D0010 and D0150 staging load job so GoAnywhere can begin processing live files after UC018 completion | nxzen BAU | ukpnmvsprds31 | After Step 27 | |
| 29 | Perform go-live sanity check: (1) Confirm eWAY is delivering files to `/dstage/projects/MAVIS_PROD/inbox_gaw`, (2) During DataStage staging execution verify trigger file appears in `/dstage/projects/MAVIS_PROD/gaw_file_trigger`, (3) After D0010 and D0150 staging completes verify GoAnywhere has deleted the trigger file from `/dstage/projects/MAVIS_PROD/gaw_file_trigger` | nxzen BAU | ukpnmvsprds31 | 11/04/2026 15:00 – 16:30 | If any check fails escalate immediately to nxzen Project Team |
| 30 | Request Control-M to release the Saturday UC018 job once go-live sanity check is confirmed successful | nxzen BAU | ukpnmvsprds31 | After Step 29 confirmed | |
| 31 | Staging Load kickoff — confirm first live batch of D0010 and D0150 files is being processed by the new GoAnywhere/stored procedure pipeline | nxzen BAU | ukpnmvsprds31 | After Step 30 | |
| 32 | Application Load kickoff — confirm MAVIS application load is processing staged data correctly | nxzen BAU | ukpnmvsprds31 | After Step 31 | |

---

## ROLLBACK PLAN

In the event of a critical failure that cannot be resolved within the cutover window:

| # | Rollback Action | Owner |
|---|-----------------|-------|
| RB-1 | Restore RMAN backup of App and Datamart databases (taken in Step 5) | nxzen DBA |
| RB-2 | Restore DataStage jobs from backup taken in Step 11 | nxzen Project Team |
| RB-3 | Restore eWAY .ear files from backup taken in Step 17 | nxzen Project Team |
| RB-4 | Request Control-M to re-enable original DataStage staging jobs for D0010 and D0150 | nxzen BAU |
| RB-5 | Communicate rollback to business stakeholders and agree next cutover window | nxzen Project Team |

---

## NOTES

1. The RMAN backup window (10:00–14:00) overlaps with Phases 3–5. This is acceptable as RMAN takes a hot (online) backup and does not lock the database. However, Phase 6 (GoAnywhere) should not begin until backup is confirmed complete.
2. GoAnywhere and DataStage must **not** look at the same folder. eWAY routes D0010 and D0150 files to `inbox_gaw` (GoAnywhere picks up). All other flows continue to use the existing DataStage inbox. This separation avoids file contention.
3. The trigger file mechanism (`gaw_file_trigger`) is a **temporary** arrangement. Once all DataStage staging jobs migrate to GoAnywhere/stored procedures, scheduling can be managed directly in GoAnywhere and the trigger file folder will no longer be needed.
4. All production folder paths must use **`MAVIS_PROD`** — never `MAVIS_DEV_MHHS`.
