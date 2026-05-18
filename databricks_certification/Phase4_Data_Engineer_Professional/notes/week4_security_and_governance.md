# Week 4 — Security & Unity Catalog

## Study Checklist
- [ ] Understand Unity Catalog hierarchy and three-part namespace
- [ ] Practice GRANT/REVOKE at catalog, schema, and table level
- [ ] Implement row-level security using row filters
- [ ] Implement column-level masking
- [ ] Use Databricks Secrets for credential management
- [ ] Understand data lineage in Unity Catalog

## Unity Catalog Architecture

### Hierarchy
```
Databricks Account
  └── Metastore (one per region — shared across workspaces)
        └── Catalog
              └── Schema (= Database)
                    ├── Table
                    ├── View
                    ├── Function (UDF)
                    └── Volume (file storage in Unity Catalog)
```

### Three-Part Namespace
```sql
-- Always reference objects as: catalog.schema.table
SELECT * FROM prod_catalog.sales_schema.orders;

-- Set default catalog/schema (avoids repeating in every query)
USE CATALOG prod_catalog;
USE SCHEMA sales_schema;
SELECT * FROM orders;   -- now resolves to prod_catalog.sales_schema.orders

-- Show available objects
SHOW CATALOGS;
SHOW SCHEMAS IN prod_catalog;
SHOW TABLES IN prod_catalog.sales_schema;
```

### Creating the Hierarchy
```sql
-- Create catalog (metastore admin required)
CREATE CATALOG IF NOT EXISTS prod_catalog;

-- Create schema
CREATE SCHEMA IF NOT EXISTS prod_catalog.sales_schema;

-- Create table in catalog
CREATE TABLE prod_catalog.sales_schema.orders (
  id INT, customer_id INT, amount DECIMAL(10,2)
) USING DELTA;
```

## Access Control (GRANT / REVOKE)

### Permission Hierarchy — Must Grant USAGE at each level
```sql
-- Step 1: Grant USAGE on catalog (required to navigate into it)
GRANT USAGE ON CATALOG prod_catalog TO `analysts`;

-- Step 2: Grant USAGE on schema (required to navigate into it)
GRANT USAGE ON SCHEMA prod_catalog.sales_schema TO `analysts`;

-- Step 3: Grant actual data permission
GRANT SELECT ON TABLE prod_catalog.sales_schema.orders TO `analysts`;

-- Without USAGE grants → table access denied even with SELECT grant
```

### Common Permission Patterns
```sql
-- Read-only analyst access to a schema
GRANT USAGE  ON CATALOG mycat TO `analysts`;
GRANT USAGE  ON SCHEMA  mycat.myschema TO `analysts`;
GRANT SELECT ON SCHEMA  mycat.myschema TO `analysts`;   -- all tables in schema

-- Data engineer — read + write
GRANT USAGE, CREATE ON SCHEMA mycat.myschema TO `data_engineers`;
GRANT SELECT, MODIFY ON TABLE mycat.myschema.orders TO `data_engineers`;

-- Full admin on catalog
GRANT ALL PRIVILEGES ON CATALOG mycat TO `admins`;

-- Individual user (email)
GRANT SELECT ON TABLE orders TO `analyst@company.com`;

-- Service principal (for jobs/pipelines)
GRANT SELECT ON TABLE orders TO `service-principal://my-sp`;

-- Revoke
REVOKE SELECT ON TABLE orders FROM `analysts`;

-- Check grants
SHOW GRANTS ON TABLE orders;
SHOW GRANTS ON SCHEMA myschema;
```

### Permission Types
| Permission | Applies To | What It Allows |
|-----------|-----------|---------------|
| `USAGE` | Catalog, Schema | Navigate into the object |
| `SELECT` | Table, View | Read data |
| `MODIFY` | Table | INSERT, UPDATE, DELETE |
| `CREATE` | Catalog, Schema | Create objects inside |
| `CREATE TABLE` | Schema | Create tables only |
| `EXECUTE` | Function | Run the UDF |
| `ALL PRIVILEGES` | Any | Everything |

## Row-Level Security

### Row Filters (Unity Catalog)
```sql
-- Create a row filter function
CREATE OR REPLACE FUNCTION prod_catalog.sales_schema.orders_filter(region STRING)
RETURN is_member(region);
-- This function returns TRUE if current user is a member of the 'region' group

-- Apply filter to table (one filter per table)
ALTER TABLE orders SET ROW FILTER prod_catalog.sales_schema.orders_filter ON (region);

-- US team members see only US rows; EU team members see only EU rows
-- Admin with full access sees all rows

-- Remove filter
ALTER TABLE orders DROP ROW FILTER;
```

### Dynamic Views (alternative — works without Unity Catalog)
```sql
CREATE OR REPLACE VIEW secure_orders AS
SELECT
  order_id,
  customer_id,
  region,
  -- Only finance group sees actual amounts
  CASE WHEN is_member('finance') THEN amount ELSE NULL END AS amount,
  order_date
FROM orders
-- Only rows in user's region
WHERE region = session_user_group() OR is_account_admin();
```

## Column-Level Security (Column Masking)

### Column Masks (Unity Catalog)
```sql
-- Create masking function
CREATE OR REPLACE FUNCTION prod_catalog.sales_schema.mask_salary(salary DOUBLE)
RETURNS DOUBLE
RETURN CASE
  WHEN is_member('hr_team') THEN salary        -- HR sees real salary
  WHEN is_member('managers') THEN salary * 0   -- Managers see 0
  ELSE NULL                                     -- Everyone else sees NULL
END;

-- Apply mask to column
ALTER TABLE employees ALTER COLUMN salary
SET MASK prod_catalog.sales_schema.mask_salary;

-- Remove mask
ALTER TABLE employees ALTER COLUMN salary DROP MASK;
```

## Data Lineage
- Unity Catalog automatically tracks: which tables are read by which queries/jobs
- View lineage in Databricks UI: Data → Table → Lineage tab
- Shows upstream sources and downstream consumers
- Helps with: impact analysis, compliance, debugging

```sql
-- Query lineage programmatically (Unity Catalog system tables)
SELECT * FROM system.access.table_lineage
WHERE target_table_full_name = 'prod_catalog.sales_schema.gold_summary'
ORDER BY event_time DESC;
```

## Secrets Management

### Why Secrets?
- Never hardcode credentials, API keys, or passwords in notebooks
- Databricks Secrets store encrypted credentials

### Managing Secrets (CLI)
```bash
# Create secret scope
databricks secrets create-scope --scope my-scope

# Add a secret
databricks secrets put --scope my-scope --key db-password

# List secrets (shows keys, not values)
databricks secrets list --scope my-scope
```

### Using Secrets in Notebooks
```python
# Retrieve secret value (value is never shown in notebook output)
password = dbutils.secrets.get(scope="my-scope", key="db-password")
jdbc_url = f"jdbc:sqlserver://server:1433;password={password}"

# Use in connection
df = spark.read.format("jdbc") \
  .option("url", jdbc_url) \
  .option("dbtable", "dbo.employees") \
  .load()
```

### Secret Scopes
| Type | Backed By | Use When |
|------|-----------|---------|
| Databricks-managed | Databricks encrypted storage | Simple use cases |
| Azure Key Vault-backed | Azure Key Vault | Enterprise — centralized secrets |
| AWS Secrets Manager-backed | AWS Secrets Manager | Enterprise — centralized secrets |

## Audit Logs
```sql
-- Unity Catalog audit logs (system tables)
SELECT
  event_time,
  user_identity.email,
  action_name,
  request_params,
  response.status_code
FROM system.access.audit
WHERE action_name IN ('getTable', 'updateTable', 'deleteTable')
  AND event_time > current_timestamp() - INTERVAL 7 DAYS
ORDER BY event_time DESC;
```

## Exam Tips
- USAGE must be granted at EVERY level (catalog AND schema) before table access works
- Row filters and column masks require Unity Catalog — not available with Hive metastore
- `is_member('group')` = current user is member of that group
- Secrets: `dbutils.secrets.get()` — value never printed/logged
- Data lineage is automatic in Unity Catalog — no extra setup
- Service principals used for jobs/automation, not personal user accounts
- Unity Catalog governs across all workspaces; Hive metastore is per-workspace

## Notes
_(Write your own notes here as you study)_
