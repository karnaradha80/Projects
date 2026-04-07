# Deployment & Recovery Guide - Conversation Log
**Date:** 2026-03-27

---

## What Was Done

### 1. Docker Desktop Started
Docker Desktop was not running. Started it via:
```bash
"/c/Program Files/Docker/Docker/Docker Desktop.exe" &
```
Waited for daemon to be ready, then proceeded.

---

### 2. Oracle XE Container Started
```bash
cd /c/Projects/fs-deployment
docker compose up -d
```
- Image pulled: `gvenzl/oracle-xe:21-slim`
- Container name: `mavis-oracle-xe`
- Waited for health status: `healthy` (~30–60 seconds after image was ready)

---

### 3. Scripts Deployed (01–06)
Run against `MDQA_OWNER` user on `//localhost/XEPDB1`:

| Script | Description | Status |
|--------|-------------|--------|
| `01_create_tables.sql` | Core tables | ✅ |
| `02_create_sequences.sql` | Sequences | ✅ |
| `03_create_packages.sql` | Package specs & bodies | ✅ |
| `04_seed_data.sql` | Network refs & error messages | ✅ |
| `05_insert_validation_configs.sql` | Validation configs | ✅ |
| `06_Procedures.sql` | `logger`, `logger_wrapper`, `PRC_DTC_PROCESS_FILE_WRAPPER` | ⚠ Pending re-run |

**Fix applied to `06_Procedures.sql`:** Added missing `/` terminator after `LOGGER_WRAPPER` procedure.
`logger` procedure was also added to `06_Procedures.sql` by the user — needs to be re-run.

---

### 4. Additional Tables Created Manually

#### MDQ_ETL_FILE_STAGE
Staging table for DTC flow files dropped by MFT tool.
```sql
CREATE TABLE MDQ_ETL_FILE_STAGE (
    MEFS_PK             NUMBER(13,0),
    MEFS_FILE_NAME      VARCHAR2(100),
    MEFS_FILE_CONTENT   CLOB,
    MEFS_FLOW_TYPE      VARCHAR2(10),
    MEFS_FLOW_VERSION   VARCHAR2(5),
    MEFS_CR_DTTM        DATE DEFAULT SYSDATE,
    MEFS_UPD_DTTM       DATE,
    MEFS_PROCESSED_YN   VARCHAR2(1) DEFAULT 'N',
    MEFS_PROCESSED_DTTM DATE,
    MEFS_STATUS         VARCHAR2(20),
    MEFS_ERR_MSG        VARCHAR2(4000),
    CONSTRAINT MDQ_ETL_FILE_STAGE_PK PRIMARY KEY (MEFS_PK)
);
```

#### MDQ_ETL_RUN
Run tracking table.
```sql
CREATE TABLE MDQ_ETL_RUN (
    RUN_NUM        NUMBER(10,0),
    RUN_START_DTTM DATE,
    RUN_END_DTTM   DATE,
    RUN_SEQ_NAME   VARCHAR2(40)
);
```

---

## Connection Details

| Field | Value |
|-------|-------|
| Host | `localhost` |
| Port | `1521` |
| Service Name | `XEPDB1` |
| Username | `MDQA_OWNER` |
| Password | `MdqA_0wn3r2026` |
| SYS Password | `Mav1sDb2026Xpr3ss` |

SQL*Plus:
```
sqlplus MDQA_OWNER/MdqA_0wn3r2026@localhost:1521/XEPDB1
```
JDBC:
```
jdbc:oracle:thin:@localhost:1521/XEPDB1
```

---

## Auto-Start Behaviour

- Docker Desktop is registered in Windows startup (`HKCU\...\Run`)
- Container has `restart: unless-stopped`
- **After a reboot:** Docker Desktop starts automatically → container starts automatically → database available within ~1–2 minutes
- **Data is persisted** in named Docker volume `oracle-data` — survives reboots

---

## Recovery: If Something Goes Wrong

### Container not running
```bash
cd /c/Projects/fs-deployment
docker compose up -d
```

### Check container health
```bash
docker ps --filter name=mavis-oracle-xe
# Wait for STATUS: (healthy)
```

### Full redeploy (wipes and recreates everything)
> WARNING: This destroys all data. Only use if the schema is corrupt or unrecoverable.
```bash
# Stop and remove container + volume
docker compose down -v

# Start fresh
docker compose up -d

# Wait for healthy, then redeploy all scripts
docker exec -i mavis-oracle-xe sqlplus "MDQA_OWNER/MdqA_0wn3r2026@//localhost/XEPDB1" <<'EOF'
@@/opt/oracle/scripts/startup/01_create_tables.sql
@@/opt/oracle/scripts/startup/02_create_sequences.sql
@@/opt/oracle/scripts/startup/03_create_packages.sql
@@/opt/oracle/scripts/startup/04_seed_data.sql
@@/opt/oracle/scripts/startup/05_insert_validation_configs.sql
@@/opt/oracle/scripts/startup/06_Procedures.sql
EXIT;
EOF
```

Then re-create the manually added tables:
```sql
-- MDQ_ETL_FILE_STAGE
CREATE TABLE MDQ_ETL_FILE_STAGE (
    MEFS_PK             NUMBER(13,0),
    MEFS_FILE_NAME      VARCHAR2(100),
    MEFS_FILE_CONTENT   CLOB,
    MEFS_FLOW_TYPE      VARCHAR2(10),
    MEFS_FLOW_VERSION   VARCHAR2(5),
    MEFS_CR_DTTM        DATE DEFAULT SYSDATE,
    MEFS_UPD_DTTM       DATE,
    MEFS_PROCESSED_YN   VARCHAR2(1) DEFAULT 'N',
    MEFS_PROCESSED_DTTM DATE,
    MEFS_STATUS         VARCHAR2(20),
    MEFS_ERR_MSG        VARCHAR2(4000),
    CONSTRAINT MDQ_ETL_FILE_STAGE_PK PRIMARY KEY (MEFS_PK)
);

-- MDQ_ETL_RUN
CREATE TABLE MDQ_ETL_RUN (
    RUN_NUM        NUMBER(10,0),
    RUN_START_DTTM DATE,
    RUN_END_DTTM   DATE,
    RUN_SEQ_NAME   VARCHAR2(40)
);
```

### Check for invalid objects
```sql
SELECT object_name, object_type, status
FROM user_objects
WHERE status = 'INVALID'
ORDER BY object_type, object_name;
```

### Recompile all invalid objects
```sql
BEGIN
  DBMS_UTILITY.COMPILE_SCHEMA(schema => 'MDQA_OWNER', compile_all => FALSE);
END;
/
```

---

## Known Issues

| Object | Issue | Fix |
|--------|-------|-----|
| `LOGGER_WRAPPER` | Was INVALID — `logger` procedure missing | `logger` added to `06_Procedures.sql`, needs re-run |
| `PKG_DTC_PROCESSING` BODY | INVALID due to dependency on `LOGGER_WRAPPER` | Will resolve once `06_Procedures.sql` is re-run |
