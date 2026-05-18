# Presidio Sanitizer, GitIgnore, and Actual Mappings — 2026-05-14

## Summary
Built Presidio NLP-based sanitizer as an upgrade over the regex-only script.
Added .gitignore to protect sensitive files.
Added actual_mappings_TEMPLATE.csv for reverse-mapping workflow.

---

## Presidio Sanitizer — tools\sanitize_presidio.py

### Why Presidio over regex
| Our Script | Presidio |
|---|---|
| Regex only — detects what we coded | NLP — understands context |
| Misses person names unless hardcoded | Auto-detects person names |
| Misses org names | Auto-detects organisation names |
| Misses locations | Auto-detects locations |

**Cost: Free** — MIT licence, fully local, no API calls.

### Install (one-time)
```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg   # ~700MB, one-time download
```

### What it detects
| Entity | Replacement |
|---|---|
| PERSON | REPORT_OWNER |
| EMAIL_ADDRESS | user1@domain (consistent mapping) |
| PHONE_NUMBER | 000-000-0000 |
| IP_ADDRESS | 0.0.0.0 |
| LOCATION | LOCATION_X |
| ORGANIZATION | ORG_X |
| URL | http://redacted |
| PASSWORD (custom) | ***REDACTED*** |
| SMTP_PORT (custom) | 999 |
| DB_CONNECTION (custom) | REDACTED |

### Custom recognisers
- **PasswordRecogniser**: detects `Password=<value>` in Toad XML auth strings
- **SmtpPortRecogniser**: detects `SmtpPort="<value>"` in XML
- **ConnectionStringRecogniser**: detects `Host=`, `Sid=`, `User Id=` values

### Processing pipeline (5 steps)
```
[1] Read file (auto-detect UTF-16 or UTF-8)
[2] Apply custom mappings (sanitize_mappings.csv — exact, fast)
[3] Anonymise emails consistently (user1@domain, user2@domain...)
[4] Presidio NLP analysis + anonymisation (person names, orgs, locations...)
[5] Verify + save output
```

### Usage
```bash
# Basic
python tools\sanitize_presidio.py toad_xml_files\Toad_267_Daily.txt

# With report (shows every PII instance detected)
python tools\sanitize_presidio.py toad_xml_files\Toad_267_Daily.txt --report

# Custom output path
python tools\sanitize_presidio.py toad_xml_files\Toad_267_Daily.txt --output output\sanitized.txt

# Custom mappings file
python tools\sanitize_presidio.py toad_xml_files\Toad_267_Daily.txt --mappings tools\my_mappings.csv
```

### Test results (against Toad_267_Daily.txt)
```
Replaced 17 unique email(s)
Detected 178 PII instance(s) via NLP:
  [IP_ADDRESS]   9 instance(s) replaced
  [LOCATION]     7 instance(s) replaced
  [ORGANIZATION] 44 instance(s) replaced
  [PASSWORD]     5 instance(s) replaced
  [PERSON]       2 instance(s) replaced
  [SMTP_PORT]    5 instance(s) replaced
  [URL]          106 instance(s) replaced
Verification passed — no known sensitive values remain
```

### Known limitation
Presidio NLP is designed for plain text, not XML.
Some XML tag names/SQL aliases are detected as URLs or Organizations (false positives).
For example: `dorg.net`, `Automation.Work`, `dwor.work` detected as URLs.
These are benign — the replacement of XML structure text does not break the logical content.
Potential future improvement: extract only XML attribute values before running Presidio NLP.

---

## .gitignore — Added

Protects the following from accidental commit:

```gitignore
tools/actual_mappings.csv          # reverse mapping with real values — NEVER commit
toad_xml_files/*.txt               # source Toad XML (may contain sensitive data)
toad_generated_reports/            # real Excel reports
adf_templates/arm_template_parameters.json  # real server names / resource IDs
output/                            # pipeline output
```

---

## actual_mappings_TEMPLATE.csv — Added

Location: `tools\actual_mappings_TEMPLATE.csv` (safe to share)

**Workflow for local development:**
1. Copy template: `cp tools\actual_mappings_TEMPLATE.csv tools\actual_mappings.csv`
2. Fill in real values in `actual_mappings.csv`
3. Never share or commit `actual_mappings.csv` (protected by .gitignore)
4. Use with sanitize scripts to restore real values locally:
```bash
python sanitize.py <sanitized_file> --mappings tools\actual_mappings.csv
```

---

## Files Added This Session

| File | Purpose | Safe to share? |
|---|---|---|
| `tools\sanitize_presidio.py` | NLP-based PII sanitizer | Yes |
| `.gitignore` | Protect sensitive files from git | Yes |
| `tools\actual_mappings_TEMPLATE.csv` | Template for reverse mapping | Yes |
| `tools\actual_mappings.csv` | Real reverse mapping values | **NEVER** |

---

## Complete Project Structure

```
C:\Projects\Toad_poc\
├── .gitignore
├── toad_xml_files\          (sanitized XML files only — real files gitignored)
├── toad_generated_reports\  (gitignored)
├── sample_data\             (9 CSV files with synthetic data)
├── pipeline\pipeline.py     (working Python pipeline)
├── sql_scripts\             (01-04 SQL scripts)
├── adf_templates\           (Linked Services, Datasets, ARM template)
│   └── arm_template_parameters.json  (gitignored — real values)
├── output\                  (gitignored — pipeline output)
├── tools\
│   ├── sanitize.py                     (regex sanitizer)
│   ├── sanitize_presidio.py            (NLP sanitizer — new)
│   ├── sanitize_mappings.csv           (generic mappings — shareable)
│   ├── actual_mappings_TEMPLATE.csv    (template — shareable)
│   └── actual_mappings.csv             (real values — gitignored, NEVER share)
└── conversations\           (session notes)
```

---

## Next Steps

### Immediate
- Create `tools\actual_mappings.csv` from template (private, local only)
- Run `git init` and first commit (all sensitive files already gitignored)

### Azure Setup (when ready)
1. Create free Azure account (azure.microsoft.com/en-us/free)
2. Create resource group: `rg-bimio267-poc`
3. Create Azure SQL Server + Database (Free tier / Basic)
4. Run SQL scripts 01 → 04 to create schemas, tables, load sample data
5. Deploy ARM template:
   ```bash
   az deployment group create \
     --resource-group rg-bimio267-poc \
     --template-file adf_templates/arm_template.json \
     --parameters adf_templates/arm_template_parameters.json
   ```
6. Create Blob Storage container: `bimio-reports`
7. Set up Logic App for email (HTTP trigger → Office 365)
8. Run ADF pipeline manually to validate
9. Start trigger `TR_Daily_0600` when validated

### Future
- AWS equivalent (Glue + S3/Redshift) after Azure POC proven
- Pre-process XML before Presidio to reduce false positives on XML tags
