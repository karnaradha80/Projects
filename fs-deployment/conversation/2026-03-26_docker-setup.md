# Docker Database Setup - Conversation Log
**Date:** 2026-03-26

---

## Context

Setting up a Docker-based Oracle XE database for the `fs-deployment` project (MAVIS DTC Staging).

---

## Conversation

**User:** For `fs-deployment/` as discussed earlier, can you create docker database?

**Assistant:** Checked existing Docker setup:
- `docker-compose.yaml` — already configured with Oracle XE 21-slim image
- `deploy.sh` — deployment script with start/stop/connect/deploy commands
- `docker/start-and-test.sh` — full setup and test script

Found Docker Desktop was not running. Provided workflow:

1. Start container:
   ```bash
   cd /c/Projects/fs-deployment
   docker-compose up -d
   ```
2. Wait for Oracle to be healthy (first run: 5–10 min)
3. Deploy schema: `./deploy.sh deploy`
4. Connect to verify: `./deploy.sh connect`

**Connection Details:**
| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `1521` |
| Service | `XEPDB1` |
| User | `MDQA_OWNER` |
| Password | `MdqA_0wn3r2026` |

---

**User:** Getting this error:
```
PS C:\Projects\fs-deployment> docker-compose up -d
unable to get image 'gvenzl/oracle-xe:21-slim': request returned 500 Internal Server Error
for API route and version http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.53/images/...
```

**Assistant:** Ran `docker version` — client v29.3.1 (API 1.54) but server returning 500. Diagnosed as Docker Desktop Linux engine not fully initialized.

Provided three options:
- **Option 1:** Restart via system tray (right-click Docker whale → Restart)
- **Option 2:** `wsl --shutdown` then restart Docker Desktop
- **Option 3:** Docker Desktop → Settings → General → Enable WSL2 engine → Apply & Restart

---

**User:** Option 1 — where to restart?

**Assistant:** Steps:
1. Click **^** arrow in Windows system tray (bottom-right taskbar)
2. Find the **Docker whale icon**
3. Right-click → **Restart**
4. Wait ~60 seconds, then retry `docker-compose up -d`

---

## Current Status

Docker Desktop restart in progress. Once complete, retry:
```bash
cd C:\Projects\fs-deployment
docker-compose up -d
```

Then monitor health:
```bash
docker ps
# Wait for STATUS: (healthy)
```

Then deploy:
```bash
./deploy.sh deploy
```
