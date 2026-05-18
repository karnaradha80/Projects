# Data Analyst Associate — Cheat Sheet

## Must-Know SQL Commands
```sql
-- Time travel
SELECT * FROM t VERSION AS OF 5;
SELECT * FROM t TIMESTAMP AS OF '2024-01-01';
RESTORE TABLE t TO VERSION AS OF 3;
DESCRIBE HISTORY t;
DESCRIBE DETAIL t;

-- MERGE (upsert)
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;

-- Views
CREATE VIEW v AS SELECT ...;
CREATE TEMP VIEW v AS SELECT ...;

-- Governance
GRANT SELECT ON TABLE t TO `user@co.com`;
REVOKE SELECT ON TABLE t FROM `user@co.com`;
SHOW GRANTS ON TABLE t;
```

## Unity Catalog
```
Metastore → Catalog → Schema → Table/View/Function
SELECT * FROM catalog.schema.table;
GRANT USAGE ON CATALOG c TO `group`;
GRANT USAGE ON SCHEMA c.s TO `group`;
GRANT SELECT ON TABLE c.s.t TO `group`;
```

## Key Exam Gotchas
- USAGE grant required on catalog AND schema before table grant works
- TEMP VIEW is session-scoped — not visible to other users
- DESCRIBE HISTORY shows all versions; DESCRIBE DETAIL shows file stats
- Alerts trigger on query results — need a saved query first
- Time travel VERSION numbers start at 0
- RESTORE creates a new version — does not delete history
