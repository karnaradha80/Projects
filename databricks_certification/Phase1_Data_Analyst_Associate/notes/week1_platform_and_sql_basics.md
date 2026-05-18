# Week 1 — Databricks Platform & SQL Basics

## Study Checklist
- [ ] Create Databricks Community Edition account
- [ ] Explore Workspace UI — notebooks, SQL Editor, Data tab
- [ ] Create and start a SQL Warehouse
- [ ] Run SELECT queries on sample datasets (use built-in `samples` catalog)
- [ ] Create a Delta table using SQL
- [ ] Understand DBFS (Databricks File System)

## Key Concepts

### Databricks SQL Warehouses
- SQL compute engine (not a cluster) — optimized for SQL workloads
- Types: Classic, Serverless
- Size: 2X-Small to 4X-Large (affects performance and cost)
- Auto-stop: configurable idle timeout

### Delta Tables via SQL
```sql
-- Create Delta table
CREATE TABLE employees (
  id INT,
  name STRING,
  dept STRING,
  salary DOUBLE
) USING DELTA;

-- Insert data
INSERT INTO employees VALUES (1, 'Alice', 'HR', 60000);

-- Query
SELECT dept, AVG(salary) as avg_salary
FROM employees
GROUP BY dept
ORDER BY avg_salary DESC;

-- Describe table
DESCRIBE TABLE employees;
DESCRIBE DETAIL employees;
DESCRIBE HISTORY employees;
```

### Database Objects
```sql
SHOW CATALOGS;
SHOW DATABASES;
SHOW TABLES IN my_database;
SHOW VIEWS;

-- Create database
CREATE DATABASE IF NOT EXISTS my_db;
USE my_db;

-- Drop
DROP TABLE IF EXISTS my_table;
DROP DATABASE IF EXISTS my_db CASCADE;
```

## Notes
_(Write your own notes here as you study)_
