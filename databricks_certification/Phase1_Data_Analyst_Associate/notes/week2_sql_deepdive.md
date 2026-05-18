# Week 2 — SQL Deep Dive (Databricks-Specific)

## Study Checklist
- [ ] Practice window functions on real data
- [ ] Write a MERGE INTO statement
- [ ] Use time travel to query historical data
- [ ] Create standard and dynamic views
- [ ] Query Delta table history

## Key Concepts

### Window Functions (same as SQL Server)
```sql
SELECT
  name,
  dept,
  salary,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) as rank,
  RANK()       OVER (PARTITION BY dept ORDER BY salary DESC) as dense_rank,
  LAG(salary)  OVER (PARTITION BY dept ORDER BY salary) as prev_salary,
  LEAD(salary) OVER (PARTITION BY dept ORDER BY salary) as next_salary,
  SUM(salary)  OVER (PARTITION BY dept) as dept_total,
  AVG(salary)  OVER (PARTITION BY dept) as dept_avg
FROM employees;
```

### MERGE INTO (Upsert — key exam topic)
```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED AND s.action = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET t.name = s.name, t.salary = s.salary
WHEN NOT MATCHED THEN INSERT (id, name, salary) VALUES (s.id, s.name, s.salary);
```

### Delta Time Travel
```sql
-- By version number
SELECT * FROM employees VERSION AS OF 3;

-- By timestamp
SELECT * FROM employees TIMESTAMP AS OF '2024-01-15 10:00:00';

-- See all versions
DESCRIBE HISTORY employees;

-- Restore to a previous version
RESTORE TABLE employees TO VERSION AS OF 2;
```

### Views
```sql
-- Standard view
CREATE VIEW active_employees AS
SELECT * FROM employees WHERE status = 'active';

-- Temporary view (session-scoped)
CREATE TEMP VIEW high_earners AS
SELECT * FROM employees WHERE salary > 100000;

-- Dynamic view (row-level security)
CREATE VIEW secure_employees AS
SELECT id, name, dept,
  CASE WHEN is_member('hr_team') THEN salary ELSE 'REDACTED' END as salary
FROM employees;
```

### Higher-Order Functions (Databricks-specific)
```sql
-- TRANSFORM (apply function to array elements)
SELECT TRANSFORM(array(1, 2, 3), x -> x * 2);  -- [2, 4, 6]

-- FILTER (filter array elements)
SELECT FILTER(array(1, 2, 3, 4), x -> x > 2);  -- [3, 4]

-- AGGREGATE (reduce array)
SELECT AGGREGATE(array(1, 2, 3), 0, (acc, x) -> acc + x);  -- 6
```

## Notes
_(Write your own notes here as you study)_
