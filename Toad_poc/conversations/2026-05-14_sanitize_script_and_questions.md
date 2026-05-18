# Sanitize Script & Architecture Questions — 2026-05-14

## Summary
Built a local Python sanitization script for Toad XML files.
Discussed Presidio as a better alternative.
Answered key architecture questions about reverse mapping, real values in deployment, and ADF central config.

---

## Sanitization Script — tools\sanitize.py

### What it does
Automatically removes sensitive data from Toad XML pipeline files before sharing.

### Auto-detects and replaces:
| Type | Method | Example |
|---|---|---|
| Email addresses | Regex — consistent `user1@domain` mapping | `john@company.com` → `user1@company.com` |
| Passwords | Regex — `Password=<value>` pattern | `Password=abc123` → `Password=***REDACTED***` |
| IP addresses | Regex — IPv4 pattern | `192.168.1.10` → `0.0.0.0` |
| SMTP ports | Regex — `SmtpPort="<value>"` | `SmtpPort="587"` → `SmtpPort="999"` |

### Custom mappings (sanitize_mappings.csv):
- Add org-specific values: server names, depot names, person names, paths
- Comment lines with `#`
- No code changes needed

### Usage:
```bash
# Basic
python tools\sanitize.py toad_xml_files\MyReport.txt

# Specify output
python tools\sanitize.py toad_xml_files\MyReport.txt --output toad_xml_files\MyReport_clean.txt

# Custom mappings file
python tools\sanitize.py toad_xml_files\MyReport.txt --mappings my_mappings.csv
```

---

## Better Alternative — Microsoft Presidio

### What it is
Open-source Python library by Microsoft for PII detection and anonymization using NLP.

### Why it's better
| Our Script | Presidio |
|---|---|
| Regex only — detects what we coded | NLP — understands context |
| Misses person names unless hardcoded | Auto-detects person names |
| Misses org names | Auto-detects organisation names |
| Misses locations | Auto-detects locations |

### Cost
**Completely free** — MIT licence, runs fully locally, no API calls, no cloud required.

### Install (one-time)
```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg   # ~700MB, one-time download
```

**Decision: Build Presidio-based sanitizer (pending)**

---

## Q: How to put real values back during development?

### Two layers:

**Layer 1 — Local development**
- Keep a private `tools\actual_mappings.csv` — maps generic → real values
- NEVER share or commit this file
- Add to `.gitignore`

```
# actual_mappings.csv (NEVER SHARE)
ORACLE_SERVER,REAL_PROD_SERVER_NAME
ORACLE_SCHEMA,REAL_SCHEMA_NAME
FILESERVER,\\real-server.company.net
```

**Layer 2 — Azure deployment**
- Real values never go back into templates
- Server names → `arm_template_parameters.json` (kept private)
- Passwords → Azure Key Vault
- ADF Linked Services reference Key Vault at runtime

### Flow
```
Sanitized templates (safe to share)
        +
arm_template_parameters.json (private)
        ↓
Azure deployment → ADF reads passwords from Key Vault at runtime
```

---

## Q: In ADF do all details sit in one place?

**Yes — Linked Services are the single source of truth for all connections.**

```
Azure Key Vault       ← passwords (one place)
        ↓
Linked Services       ← connection details (one place)
        ↓
Datasets              ← reference Linked Services
        ↓
Pipelines             ← reference Datasets
```

### If something changes — update ONE place only

| Change | Update | Impact |
|---|---|---|
| Oracle password | Key Vault secret | All pipelines auto-updated |
| Oracle server moves | LS_Oracle_Source | All pipelines auto-updated |
| Azure SQL changes | LS_AzureSQL_Target | All pipelines auto-updated |
| Email recipients | config.report_email table | No ADF changes needed |

---

## Files in tools\ folder

```
C:\Projects\Toad_poc\tools\
├── sanitize.py              ← sanitization script (safe to share)
├── sanitize_mappings.csv    ← generic custom mappings (safe to share)
└── actual_mappings.csv      ← NEVER share (to be created per environment)
```

---

## Next Steps
- Build Presidio-based sanitizer (upgrade from regex-based)
- Add .gitignore to project
- Add actual_mappings.csv template
- Set up Azure subscription
- Deploy ARM template
- Validate ADF pipeline end-to-end
