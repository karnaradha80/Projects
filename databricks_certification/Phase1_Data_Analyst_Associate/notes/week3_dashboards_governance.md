# Week 3 — Dashboards, Alerts & Governance

## Study Checklist
- [ ] Create a Databricks SQL Dashboard with 3+ visualizations
- [ ] Set up a query-based alert
- [ ] Explore Unity Catalog hierarchy in the UI
- [ ] Practice GRANT and REVOKE statements
- [ ] Understand the difference between catalog, schema, and table permissions

## Key Concepts

### Databricks SQL Dashboards
- Built from saved SQL queries
- Visualization types: bar, line, pie, counter, table, map
- Can be shared with workspace users
- Refresh: manual or scheduled

### Alerts
```sql
-- Alert is set on a saved query result
-- Trigger condition: value > threshold, value = target, etc.
-- Notifications: email, Slack, webhook
-- Check frequency: every N minutes/hours
```

### Unity Catalog Hierarchy
```
Metastore (one per region)
  └── Catalog
        └── Schema (= Database)
              └── Table / View / Function / Volume
```

```sql
-- Three-level namespace
SELECT * FROM my_catalog.my_schema.my_table;

-- Grant table access
GRANT SELECT ON TABLE my_catalog.my_schema.employees TO `user@company.com`;
GRANT SELECT ON TABLE my_catalog.my_schema.employees TO `analysts_group`;

-- Grant schema access
GRANT USAGE ON SCHEMA my_catalog.my_schema TO `analysts_group`;

-- Grant catalog access
GRANT USAGE ON CATALOG my_catalog TO `analysts_group`;

-- Revoke
REVOKE SELECT ON TABLE employees FROM `user@company.com`;

-- Show grants
SHOW GRANTS ON TABLE employees;
```

### Data Access Levels
| Permission | What it Allows |
|-----------|---------------|
| SELECT | Read table data |
| MODIFY | Insert, update, delete |
| CREATE | Create objects in schema |
| USAGE | Navigate to catalog/schema (required with other grants) |
| ALL PRIVILEGES | Everything |

### Query History & Governance
- Query history available in SQL Editor — all queries, users, duration
- Audit logs track: who ran what, when, from where
- Data lineage: Unity Catalog tracks where data came from

## Notes
_(Write your own notes here as you study)_
