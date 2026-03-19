# Connecting to MAVIS Oracle Database from External IDEs

This guide explains how to connect to the Oracle XE database running in Docker from external machines using database tools like DBeaver, SQL Developer, or DataGrip.

## Prerequisites

1. **Docker container is running** on the host machine
2. **Port 1521 is accessible** from your external machine (firewall rules may need adjustment)
3. **Oracle JDBC driver** (most IDEs include this or can download automatically)

---

## Connection Details

| Parameter | Value |
|-----------|-------|
| **Host** | IP address of the Docker host machine |
| **Port** | 1521 |
| **Service Name** | XEPDB1 |
| **Username** | MDQA_OWNER |
| **Password** | MdqA_0wn3r2026 |
| **SID** | XE (alternative to Service Name) |

### JDBC URL Formats

```
# Using Service Name (Recommended)
jdbc:oracle:thin:@//<HOST_IP>:1521/XEPDB1

# Using SID
jdbc:oracle:thin:@<HOST_IP>:1521:XE

# TNS-style connection
jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=<HOST_IP>)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))
```

Replace `<HOST_IP>` with the actual IP address of your Docker host machine.

---

## DBeaver Connection Setup

### Step 1: Create New Connection
1. Open DBeaver
2. Click **Database** → **New Database Connection** (or press `Ctrl+Shift+N`)
3. Select **Oracle** from the list
4. Click **Next**

### Step 2: Configure Connection Settings

#### Main Tab
| Field | Value |
|-------|-------|
| Host | `<Docker Host IP>` (e.g., 192.168.1.100) |
| Port | `1521` |
| Database | `XEPDB1` |
| Connection Type | Select **Service Name** |
| Username | `MDQA_OWNER` |
| Password | `MdqA_0wn3r2026` |

#### Alternative: Use Custom JDBC URL
1. Check **Custom** checkbox
2. Enter: `jdbc:oracle:thin:@//<HOST_IP>:1521/XEPDB1`

### Step 3: Download Oracle Driver
1. Click **Edit Driver Settings** (if driver not installed)
2. Click **Download/Update** to get the Oracle JDBC driver
3. DBeaver will automatically download `ojdbc8.jar` or similar

### Step 4: Test Connection
1. Click **Test Connection**
2. If successful, you'll see "Connected"
3. Click **Finish** to save

---

## Oracle SQL Developer Connection Setup

### Step 1: Create New Connection
1. Open SQL Developer
2. Click the green **+** button in Connections panel
3. Or go to **File** → **New** → **Database Connection**

### Step 2: Configure Connection

| Field | Value |
|-------|-------|
| Connection Name | `MAVIS_DEV` (or any name you prefer) |
| Username | `MDQA_OWNER` |
| Password | `MdqA_0wn3r2026` |
| Save Password | ✓ Check this |
| Connection Type | **Basic** |
| Hostname | `<Docker Host IP>` |
| Port | `1521` |
| Service Name | `XEPDB1` (select Service Name radio button) |

### Step 3: Test and Connect
1. Click **Test** to verify connection
2. Click **Save** to store the connection
3. Click **Connect** to open the connection

---

## JetBrains DataGrip / IntelliJ IDEA

### Step 1: Add Data Source
1. Open **Database** tool window
2. Click **+** → **Data Source** → **Oracle**

### Step 2: Configure Connection

| Field | Value |
|-------|-------|
| Host | `<Docker Host IP>` |
| Port | `1521` |
| Service | `XEPDB1` |
| User | `MDQA_OWNER` |
| Password | `MdqA_0wn3r2026` |
| URL | `jdbc:oracle:thin:@//<HOST_IP>:1521/XEPDB1` |

### Step 3: Download Driver
1. Click **Download missing driver files** if prompted
2. Test connection and apply

---

## Firewall Configuration

If you cannot connect from an external machine, you may need to open port 1521 on the Docker host.

### Linux (Ubuntu/Debian)
```bash
# Using ufw
sudo ufw allow 1521/tcp

# Using iptables
sudo iptables -A INPUT -p tcp --dport 1521 -j ACCEPT
```

### Linux (RHEL/CentOS)
```bash
sudo firewall-cmd --permanent --add-port=1521/tcp
sudo firewall-cmd --reload
```

### Windows
```powershell
# PowerShell (Run as Administrator)
New-NetFirewallRule -DisplayName "Oracle 1521" -Direction Inbound -Protocol TCP -LocalPort 1521 -Action Allow
```

---

## Finding the Docker Host IP

### On the Docker Host Machine

```bash
# Linux
hostname -I | awk '{print $1}'

# Or
ip addr show | grep "inet " | grep -v 127.0.0.1

# macOS
ipconfig getifaddr en0
```

### From External Machine
If you know the hostname:
```bash
ping <hostname>
nslookup <hostname>
```

---

## Troubleshooting

### Error: "ORA-12541: TNS:no listener"
- Verify the container is running: `docker ps | grep mavis-oracle-xe`
- Check if port 1521 is exposed: `docker port mavis-oracle-xe`
- Verify listener is running inside container:
  ```bash
  docker exec mavis-oracle-xe lsnrctl status
  ```

### Error: "ORA-12514: TNS:listener does not currently know of service"
- Use `XEPDB1` as service name (not `XE`)
- Or try connecting with SID `XE` to the CDB (container database)

### Error: "ORA-01017: invalid username/password"
- Verify credentials: `MDQA_OWNER` / `MdqA_0wn3r2026`
- Ensure you're connecting to `XEPDB1` (the pluggable database where the user exists)

### Error: Connection Timeout
- Check firewall rules on Docker host
- Verify network connectivity: `telnet <HOST_IP> 1521`
- Ensure Docker container has port mapping: `-p 1521:1521`

### Error: "ORA-28040: No matching authentication protocol"
- Update your JDBC driver to a newer version
- In DBeaver: Edit Driver Settings → Download latest driver

---

## Quick Connection Test from Command Line

From the Docker host:
```bash
docker exec -it mavis-oracle-xe sqlplus MDQA_OWNER/MdqA_0wn3r2026@//localhost/XEPDB1
```

From external machine (if sqlplus is installed):
```bash
sqlplus MDQA_OWNER/MdqA_0wn3r2026@<HOST_IP>:1521/XEPDB1
```

---

## Connection Summary Card

```
┌─────────────────────────────────────────────────────┐
│          MAVIS Oracle Database Connection           │
├─────────────────────────────────────────────────────┤
│  Host:         <YOUR_DOCKER_HOST_IP>                │
│  Port:         1521                                 │
│  Service:      XEPDB1                               │
│  Username:     MDQA_OWNER                           │
│  Password:     MdqA_0wn3r2026                       │
├─────────────────────────────────────────────────────┤
│  JDBC URL:                                          │
│  jdbc:oracle:thin:@//<HOST_IP>:1521/XEPDB1          │
└─────────────────────────────────────────────────────┘
```

---

## SYS/Admin Access (if needed)

For administrative tasks, you can connect as SYS:

| Parameter | Value |
|-----------|-------|
| Username | `SYS` |
| Password | `Mav1sDb2026Xpr3ss` |
| Role | `SYSDBA` |
| Service | `XE` or `XEPDB1` |

**Note:** Connect as SYSDBA in DBeaver by checking the "Role" option and selecting SYSDBA.
