# 2026-05-14 — PPT Creation & End of Day Pause

## Summary
Created NxZen-branded PowerPoint presentation for the Toad to Azure POC.
Updated Slide 5 to a proper flow diagram. Paused for the day.

## PPT: C:\Projects\Toad_poc\ppt\Toad_Azure_POC.pptx (592 KB)

### Slides
| # | Title | Notes |
|---|---|---|
| 1 | Title | NxZen logo, right-side panel image, dark background |
| 2 | Agenda | 7 numbered cards |
| 3 | Problem Statement | AS-IS Toad vs Migration Drivers |
| 4 | Solution Architecture | 6 Azure component cards |
| 5 | ADF Pipeline Flow | **Flow diagram** with boxes, arrows, branches, elbow connector |
| 6 | Azure Function Deep Dive | Execution flow + tech details |
| 7 | Sample Data & Testing | Table breakdown (1,000 records) |
| 8 | Pipeline Run Results | 3 run cards with metrics |
| 9 | Output Files Confirmed | 4 blob files |
| 10 | Next Steps | 4 tracks |

### Slide 5 Flow Diagram Layout
```
[Lookup ODS Check] → [Set Report Date] → [If ODS Refreshed?] → NO → [Email Not Refreshed]
                                                  |
                                                 YES (L-shaped elbow)
                                                  ↓
[Copy Data→Blob] → [Populate Excel Template] → [Copy Archive] → [Email Ops] → [Email BI]
```
- Arrow helpers: h_arrow(), v_arrow(), h_line(), v_line() using shape types 1 (rect), 13 (rightArrow), 36 (downArrow)
- Decision box (If): dark yellow background, thicker border
- Legend strip at bottom for colour coding

### Branding extracted from NxZen_Logos_and_Model_Template.pptx
- Background: #030304, Green: #8DE971, Cyan: #74D1EA, Purple: #AD96DC
- Yellow: #ECF166, Pink: #FF7176, Font: Arial
- Logo: ppt/extracted/Picture 3.png, Side panel: ppt/extracted/Picture 1.png

## Azure Infrastructure State (end of day)
| Resource | Name | Status |
|---|---|---|
| ADF | adf-toad-poc | Idle — no cost |
| SQL | sql-toad-poc / db-toad-poc | Running Basic tier — ~$0.16/day |
| Storage | sttoadpoc | Idle — negligible |
| Function App | func-toad-poc | Consumption — no cost when idle |
| Key Vault | kv-toad-poc | Idle — negligible |
| Logic App | la-toad-poc-email | HTTP stub — idle |

## Overnight cost
~$0.16 for SQL Basic (DTU tier, cannot be paused — not worth stopping for one night)

## Pending for next session
- Commit all changes to git
- Email step: connect Logic App to Office 365 (deferred by user)
- AWS equivalent: Glue + S3 + SES
- Set spending alert on rg-toad-poc
- Any questions the user wanted to discuss
