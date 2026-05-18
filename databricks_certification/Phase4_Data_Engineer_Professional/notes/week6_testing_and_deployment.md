# Week 6 — Testing & Deployment (CI/CD)

## Study Checklist
- [ ] Understand Databricks Repos and Git integration
- [ ] Know the Dev → Staging → Prod promotion workflow
- [ ] Write a basic pytest test for a transformation function
- [ ] Understand Databricks Asset Bundles structure
- [ ] Know the difference between job cluster and all-purpose cluster for CI/CD

## Databricks Repos — Git Integration

### What Repos Provides
- Full Git integration inside Databricks Workspace
- Supported: GitHub, GitLab, Azure DevOps, Bitbucket, AWS CodeCommit
- Each branch = separate environment
- Enables CI/CD: push code → trigger pipeline tests → deploy

### Git Operations in Repos UI
```
Workspace → Repos → [Your Repo]
Actions: Pull, Push, Commit, Create Branch, Merge, Compare
```

### Git Operations via CLI
```bash
# Clone a repo into Databricks
databricks repos create \
  --url https://github.com/org/data-pipelines \
  --provider github

# Update repo to latest (pull)
databricks repos update --repo-id 12345 --branch main

# Switch branch
databricks repos update --repo-id 12345 --branch feature/new-pipeline
```

## Environment Promotion Strategy

### Typical Setup
```
Feature Branch → Dev Workspace
       │
       │  Pull Request
       ▼
Main Branch → Staging Workspace (integration tests)
       │
       │  Release / Tag
       ▼
Release Branch → Production Workspace
```

### Environment Configuration
```python
# Use Databricks Widgets or Job parameters to handle environment differences
# DON'T hardcode paths — parameterize them

# In notebook or pipeline code:
env = dbutils.widgets.get("environment")  # "dev", "staging", "prod"

config = {
    "dev":     {"catalog": "dev_catalog",  "path": "/mnt/dev/"},
    "staging": {"catalog": "stg_catalog",  "path": "/mnt/staging/"},
    "prod":    {"catalog": "prod_catalog", "path": "/mnt/prod/"}
}

catalog = config[env]["catalog"]
base_path = config[env]["path"]
```

## Testing Strategies

### Unit Testing (Python functions)
```python
# transformation.py — pure Python function (no Spark dependency)
def calculate_bonus(salary: float, multiplier: float = 0.10) -> float:
    if salary <= 0:
        raise ValueError("Salary must be positive")
    return salary * multiplier

def categorize_salary(salary: float) -> str:
    if salary > 100000:
        return "High"
    elif salary > 60000:
        return "Medium"
    return "Low"
```

```python
# test_transformation.py — pytest unit tests
import pytest
from transformation import calculate_bonus, categorize_salary

def test_calculate_bonus_standard():
    assert calculate_bonus(100000) == 10000.0

def test_calculate_bonus_custom_multiplier():
    assert calculate_bonus(100000, 0.15) == 15000.0

def test_calculate_bonus_invalid_salary():
    with pytest.raises(ValueError):
        calculate_bonus(-1000)

def test_categorize_high():
    assert categorize_salary(150000) == "High"

def test_categorize_medium():
    assert categorize_salary(75000) == "Medium"

def test_categorize_low():
    assert categorize_salary(40000) == "Low"
```

### PySpark Testing (SparkSession in tests)
```python
# conftest.py — shared Spark session for tests
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local[2]") \
        .appName("test") \
        .getOrCreate()

# test_pipeline.py
def test_silver_deduplication(spark):
    from pipeline import transform_to_silver

    # Create test input
    input_data = [
        (1, "Alice", "HR", 75000, "2024-01-01"),
        (1, "Alice", "HR", 75000, "2024-01-01"),  # duplicate
        (2, "Bob",   "IT", 90000, "2024-01-02"),
    ]
    input_df = spark.createDataFrame(input_data, ["id", "name", "dept", "salary", "date"])

    result = transform_to_silver(input_df)

    # Assert deduplication worked
    assert result.count() == 2
    assert result.filter("id = 1").count() == 1
```

### Integration Testing in Databricks
```python
# Run a notebook programmatically and check result
result = dbutils.notebook.run(
    "/Repos/main/pipelines/silver_pipeline",
    timeout_seconds=600,
    arguments={"environment": "staging", "test_mode": "true"}
)
assert result == "SUCCESS"
```

## Databricks Asset Bundles (DAB)

### What Are Asset Bundles?
- Infrastructure-as-code for Databricks resources
- Replaces legacy `dbx` CLI
- Define jobs, pipelines, clusters in YAML → deploy consistently across environments

### Bundle Structure
```
my_project/
├── databricks.yml         ← main bundle config
├── resources/
│   ├── jobs.yml           ← job definitions
│   └── pipelines.yml      ← DLT pipeline definitions
├── src/
│   ├── notebooks/
│   └── python/
└── tests/
```

### databricks.yml Example
```yaml
bundle:
  name: sales_data_platform

workspace:
  host: https://adb-1234567890.azuredatabricks.net

targets:
  dev:
    mode: development
    workspace:
      root_path: /Users/${workspace.current_user.userName}/.bundle/${bundle.name}/dev

  prod:
    mode: production
    workspace:
      root_path: /Shared/bundles/${bundle.name}/prod

resources:
  jobs:
    daily_pipeline:
      name: "Daily Sales Pipeline"
      schedule:
        quartz_cron_expression: "0 0 6 * * ?"
        timezone_id: "UTC"
      tasks:
        - task_key: bronze_ingestion
          new_cluster:
            spark_version: "13.3.x-scala2.12"
            num_workers: 4
          notebook_task:
            notebook_path: ./src/notebooks/bronze_ingestion
        - task_key: silver_transform
          depends_on:
            - task_key: bronze_ingestion
          notebook_task:
            notebook_path: ./src/notebooks/silver_transform
```

### Bundle CLI Commands
```bash
# Validate bundle config
databricks bundle validate

# Deploy to target environment
databricks bundle deploy --target dev
databricks bundle deploy --target prod

# Run a job from bundle
databricks bundle run daily_pipeline --target dev

# Destroy (remove deployed resources)
databricks bundle destroy --target dev
```

## CI/CD with GitHub Actions

### Example Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Databricks Bundle

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Run Unit Tests
        run: pytest tests/ -v

      - name: Deploy to Staging
        env:
          DATABRICKS_HOST: ${{ secrets.STAGING_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.STAGING_TOKEN }}
        run: databricks bundle deploy --target staging

      - name: Run Integration Tests
        run: databricks bundle run integration_tests --target staging

      - name: Deploy to Production
        if: success()
        env:
          DATABRICKS_HOST: ${{ secrets.PROD_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.PROD_TOKEN }}
        run: databricks bundle deploy --target prod
```

## Job Cluster vs All-Purpose Cluster for CI/CD

| | Job Cluster | All-Purpose Cluster |
|-|-------------|-------------------|
| Created | Per job run | Pre-existing |
| Terminated | After job completes | Stays running |
| Cost | Lower | Higher |
| CI/CD use | ✅ Recommended — clean environment each run | ❌ Shared state between runs |
| Interactive dev | ❌ | ✅ |

**Best practice:** Always use job clusters in production CI/CD — ensures clean, reproducible environment.

## Exam Tips
- Asset Bundles replaced `dbx` as the recommended deployment tool
- Job clusters are preferred for CI/CD — clean state per run, lower cost
- Tests should be environment-agnostic — use parameters for paths/catalogs
- `dbutils.notebook.run()` can chain notebooks and capture return values
- CI/CD pipeline: unit tests → deploy to staging → integration tests → deploy to prod
- Never hardcode credentials — use Databricks Secrets
- `databricks bundle validate` before every deploy to catch config errors

## Notes
_(Write your own notes here as you study)_
