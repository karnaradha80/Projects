# Phase 0 — Day 2 Practice Exercises
# Topics: Functions, Lambda, OOP, Exception Handling, Pandas

# ─────────────────────────────────────────────
# EXERCISE 1 — Functions with default params
# ─────────────────────────────────────────────
# Write a function that calculates annual bonus
# Default bonus rate = 10%, but allow override

def calculate_bonus(salary, rate=0.10):
    return salary * rate

print(calculate_bonus(90000))         # 9000.0  (default 10%)
print(calculate_bonus(90000, 0.15))   # 13500.0 (override to 15%)
print(calculate_bonus(90000, rate=0.20))  # 18000.0 (keyword arg)


# ─────────────────────────────────────────────
# EXERCISE 2 — *args
# ─────────────────────────────────────────────
# Write a function that accepts any number of salaries
# and returns total, average, min, max

def salary_stats(*salaries):
    total   = sum(salaries)
    average = total / len(salaries)
    return {
        "total":   total,
        "average": round(average, 2),
        "min":     min(salaries),
        "max":     max(salaries)
    }

stats = salary_stats(75000, 90000, 110000, 65000, 85000)
for key, val in stats.items():
    print(f"  {key}: ${val:,}")


# ─────────────────────────────────────────────
# EXERCISE 3 — Lambda + sorted()
# ─────────────────────────────────────────────
employees = [
    {"name": "Alice", "dept": "IT",      "salary": 90000},
    {"name": "Bob",   "dept": "HR",      "salary": 75000},
    {"name": "Carol", "dept": "IT",      "salary": 110000},
    {"name": "Dave",  "dept": "Finance", "salary": 85000},
]

# Sort by salary descending using lambda
by_salary = sorted(employees, key=lambda e: e["salary"], reverse=True)
print("\nSorted by salary (high to low):")
for e in by_salary:
    print(f"  {e['name']}: ${e['salary']:,}")

# Sort by dept, then salary descending
by_dept_salary = sorted(employees, key=lambda e: (e["dept"], -e["salary"]))
print("\nSorted by dept, then salary:")
for e in by_dept_salary:
    print(f"  {e['dept']}: {e['name']} ${e['salary']:,}")


# ─────────────────────────────────────────────
# EXERCISE 4 — Lambda + map + filter
# ─────────────────────────────────────────────
salaries = [75000, 90000, 110000, 65000, 85000, 50000]

# Apply 10% bonus to all using map
with_bonus = list(map(lambda s: s * 1.10, salaries))
print(f"\nWith 10% bonus: {[f'${s:,.0f}' for s in with_bonus]}")

# Filter only salaries above $80,000
high_earners = list(filter(lambda s: s > 80000, salaries))
print(f"High earners (>$80k): {[f'${s:,}' for s in high_earners]}")


# ─────────────────────────────────────────────
# EXERCISE 5 — Class
# ─────────────────────────────────────────────
# Create a DatabaseTable class representing a SQL table

class DatabaseTable:
    def __init__(self, name, schema="dbo"):
        self.name    = name
        self.schema  = schema
        self.columns = []
        self.rows    = 0

    def add_column(self, col_name, col_type):
        self.columns.append({"name": col_name, "type": col_type})

    def load_data(self, row_count):
        self.rows = row_count
        print(f"Loaded {row_count:,} rows into [{self.schema}].[{self.name}]")

    def get_full_name(self):
        return f"[{self.schema}].[{self.name}]"

    def describe(self):
        print(f"\nTable: {self.get_full_name()}")
        print(f"Rows:  {self.rows:,}")
        print("Columns:")
        for col in self.columns:
            print(f"  - {col['name']} ({col['type']})")

    def __str__(self):
        return f"DatabaseTable({self.get_full_name()}, rows={self.rows:,})"


# Use the class
orders = DatabaseTable("Orders", schema="Sales")
orders.add_column("OrderID",    "INT")
orders.add_column("CustomerID", "INT")
orders.add_column("Amount",     "DECIMAL(10,2)")
orders.add_column("OrderDate",  "DATE")
orders.load_data(1_500_000)
orders.describe()
print(orders)


# ─────────────────────────────────────────────
# EXERCISE 6 — Inheritance
# ─────────────────────────────────────────────
# Extend DatabaseTable to create a DeltaTable class

class DeltaTable(DatabaseTable):
    def __init__(self, name, schema="dbo", location=None):
        super().__init__(name, schema)
        self.location = location or f"/mnt/datalake/{schema}/{name}"
        self.version  = 0

    def time_travel(self, version):
        print(f"Querying {self.get_full_name()} @ VERSION AS OF {version}")

    def optimize(self, zorder_col=None):
        msg = f"OPTIMIZE {self.get_full_name()}"
        if zorder_col:
            msg += f" ZORDER BY ({zorder_col})"
        print(msg)
        self.version += 1

    def __str__(self):
        return f"DeltaTable({self.get_full_name()}, v{self.version}, rows={self.rows:,})"


dt = DeltaTable("sales_bronze", schema="raw")
dt.add_column("id",     "INT")
dt.add_column("amount", "DECIMAL(10,2)")
dt.load_data(5_000_000)
dt.time_travel(3)
dt.optimize(zorder_col="id")
print(dt)


# ─────────────────────────────────────────────
# EXERCISE 7 — Exception Handling
# ─────────────────────────────────────────────
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("Error: Cannot divide by zero")
        return None

def parse_salary(value):
    try:
        return float(value.replace("$", "").replace(",", ""))
    except (ValueError, AttributeError) as e:
        print(f"Cannot parse salary '{value}': {e}")
        return 0.0

print(safe_divide(100, 4))        # 25.0
print(safe_divide(100, 0))        # Error message + None
print(parse_salary("$95,000"))    # 95000.0
print(parse_salary("not_a_number")) # Error + 0.0


# ─────────────────────────────────────────────
# EXERCISE 8 — Pandas (run after: pip install pandas)
# ─────────────────────────────────────────────
import pandas as pd

# Create sample employee data (like building a SQL result set)
data = {
    "emp_id": [1, 2, 3, 4, 5, 6],
    "name":   ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"],
    "dept":   ["IT", "HR", "IT", "Finance", "IT", "HR"],
    "salary": [90000, 75000, 110000, 85000, 95000, 70000],
    "active": [True, True, False, True, True, True]
}
df = pd.DataFrame(data)

# Inspect
print("\n--- DataFrame ---")
print(df)
print(f"\nShape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Filter active employees (like SQL WHERE active = 1)
active_df = df[df["active"] == True]
print(f"\nActive employees: {len(active_df)}")

# Add bonus column (like SQL computed column)
active_df = active_df.copy()
active_df["bonus"] = active_df["salary"] * 0.10

# Group by dept (like SQL GROUP BY)
summary = active_df.groupby("dept").agg(
    headcount    = ("name",   "count"),
    total_salary = ("salary", "sum"),
    avg_salary   = ("salary", "mean")
).reset_index()

print("\n--- Dept Summary ---")
print(summary.sort_values("total_salary", ascending=False).to_string(index=False))
