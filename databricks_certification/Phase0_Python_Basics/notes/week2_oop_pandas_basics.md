# Week 2 — Functions, OOP, Exception Handling & Pandas

## Study Checklist
- [ ] Write functions with default params, *args, **kwargs
- [ ] Write lambda expressions and use with map/filter
- [ ] Create a class with constructor, methods, inheritance
- [ ] Handle exceptions with try/except/finally
- [ ] Read a CSV with Pandas and run groupBy aggregations
- [ ] Write a full mini-pipeline: load → filter → aggregate → output

---

## 1. Functions

```python
# Basic function — no return type needed (vs C# void/int/string)
def greet(name):
    return f"Hello, {name}!"

print(greet("Radha"))   # Hello, Radha!

# Default parameters (like C# optional params)
def connect(host, port=1433, timeout=30):
    return f"Connecting to {host}:{port} (timeout={timeout}s)"

connect("sql-server-01")            # uses defaults
connect("sql-server-01", 5432)      # overrides port
connect("sql-server-01", timeout=60) # keyword argument — skip port

# *args — variable number of positional arguments (like C# params keyword)
def sum_all(*args):
    return sum(args)

sum_all(1, 2, 3)        # 6
sum_all(10, 20, 30, 40) # 100

# **kwargs — variable keyword arguments (like a dict of params)
def create_profile(**kwargs):
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

create_profile(name="Radha", city="Hyderabad", exp=15)

# Combining all types
def full_example(required_arg, default_arg="default", *args, **kwargs):
    print(f"Required: {required_arg}")
    print(f"Default:  {default_arg}")
    print(f"Args:     {args}")
    print(f"Kwargs:   {kwargs}")

full_example("hello", "world", 1, 2, 3, name="Radha", exp=15)
```

---

## 2. Lambda Functions

```python
# Lambda = anonymous function (like C# arrow functions x => x * 2)
# Syntax: lambda arguments: expression

double   = lambda x: x * 2
square   = lambda x: x ** 2
add      = lambda x, y: x + y
is_even  = lambda x: x % 2 == 0

double(5)       # 10
square(4)       # 16
add(3, 7)       # 10
is_even(6)      # True

# Lambda with map() — apply function to every item
numbers = [1, 2, 3, 4, 5]
doubled  = list(map(lambda x: x * 2, numbers))    # [2, 4, 6, 8, 10]

# Lambda with filter() — keep items that return True
evens    = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# Lambda with sorted() — custom sort key
employees = [
    {"name": "Alice", "salary": 90000},
    {"name": "Bob",   "salary": 75000},
    {"name": "Carol", "salary": 110000}
]
# Sort by salary ascending
sorted_by_salary = sorted(employees, key=lambda e: e["salary"])
# Sort by salary descending
sorted_desc = sorted(employees, key=lambda e: e["salary"], reverse=True)

# Lambda in list comprehension context
salaries = [75000, 90000, 110000, 65000]
bonuses = list(map(lambda s: s * 0.10, salaries))  # 10% bonus each
```

---

## 3. Classes & OOP

```python
# Python class maps directly to C# class
# C# constructor = __init__ in Python
# C# this = self in Python

class Employee:
    # Class variable (shared across all instances — like C# static)
    company = "Databricks Corp"
    headcount = 0

    # Constructor (like C# public Employee(...))
    def __init__(self, name, dept, salary):
        self.name   = name       # instance variables
        self.dept   = dept
        self.salary = salary
        Employee.headcount += 1  # increment class variable

    # Instance method
    def get_bonus(self, rate=0.10):
        return self.salary * rate

    def promote(self, new_salary):
        old = self.salary
        self.salary = new_salary
        return f"{self.name} promoted: ${old:,} → ${new_salary:,}"

    def __str__(self):              # like C# ToString()
        return f"Employee({self.name}, {self.dept}, ${self.salary:,})"

    def __repr__(self):             # for debugging output
        return f"Employee(name={self.name!r}, dept={self.dept!r})"


# Create instances
emp1 = Employee("Alice", "Engineering", 95000)
emp2 = Employee("Bob",   "HR",          75000)

print(emp1)                         # Employee(Alice, Engineering, $95,000)
print(emp1.get_bonus())             # 9500.0
print(emp1.get_bonus(0.15))         # 14250.0
print(emp1.promote(110000))
print(f"Total employees: {Employee.headcount}")   # 2


# Inheritance (like C# : BaseClass)
class Manager(Employee):
    def __init__(self, name, dept, salary, team_size):
        super().__init__(name, dept, salary)   # call parent constructor
        self.team_size = team_size

    # Override parent method
    def get_bonus(self, rate=0.20):            # managers get 20% default
        return self.salary * rate

    def __str__(self):
        return f"Manager({self.name}, team={self.team_size})"


mgr = Manager("Carol", "Engineering", 140000, 8)
print(mgr)
print(mgr.get_bonus())              # 28000.0  (uses Manager's override)
print(isinstance(mgr, Employee))   # True — Manager IS an Employee
```

---

## 4. Exception Handling

```python
# Same concept as C# try/catch/finally — different keywords
# Python: except  =  C#: catch
# Python: raise   =  C#: throw

# Basic
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Math error: {e}")

# Multiple except blocks (like multiple catch in C#)
try:
    value = int("not_a_number")
except ValueError as e:
    print(f"Value error: {e}")
except TypeError as e:
    print(f"Type error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")   # catch-all
finally:
    print("This always runs")         # like C# finally

# Raise your own exception
def divide(a, b):
    if b == 0:
        raise ValueError("Denominator cannot be zero")
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(f"Caught: {e}")

# Real-world pattern — reading a file safely
def read_config(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        return None
    except PermissionError:
        print(f"No permission to read: {filepath}")
        return None
```

---

## 5. Pandas — The SQL Result Set in Python

```python
import pandas as pd

# ── Reading Data ──────────────────────────────
df = pd.read_csv("employees.csv")
df = pd.read_excel("employees.xlsx")
df = pd.read_json("employees.json")

# Create from dictionary (like building a DataTable manually)
data = {
    "name":   ["Alice", "Bob", "Carol", "Dave"],
    "dept":   ["IT",    "HR",  "IT",    "Finance"],
    "salary": [90000,   75000, 110000,  85000],
    "active": [True,    True,  False,   True]
}
df = pd.DataFrame(data)

# ── Inspect (like SELECT TOP + DESCRIBE) ──────
df.head(3)            # first 3 rows
df.tail(2)            # last 2 rows
df.shape              # (rows, columns) → (4, 4)
df.columns            # Index(['name', 'dept', 'salary', 'active'])
df.dtypes             # data types of each column
df.info()             # summary: shape, types, nulls
df.describe()         # stats: count, mean, std, min, max

# ── Select Columns (like SELECT col1, col2) ───
df["name"]              # single column → Series
df[["name", "salary"]]  # multiple columns → DataFrame

# ── Filter Rows (like WHERE) ──────────────────
df[df["salary"] > 80000]
df[df["dept"] == "IT"]
df[df["active"] == True]

# Multiple conditions
df[(df["dept"] == "IT") & (df["salary"] > 85000)]   # AND
df[(df["dept"] == "IT") | (df["dept"] == "HR")]      # OR

# ── Add / Modify Columns (like computed columns) ──
df["bonus"]    = df["salary"] * 0.10
df["annual"]   = df["salary"] * 12
df["dept_code"]= df["dept"].str.upper().str[:2]     # "IT" → "IT", "HR" → "HR"

# ── Aggregations (like GROUP BY) ──────────────
# Total salary by dept
df.groupby("dept")["salary"].sum()

# Multiple aggregations
df.groupby("dept").agg(
    headcount    = ("name",   "count"),
    total_salary = ("salary", "sum"),
    avg_salary   = ("salary", "mean"),
    max_salary   = ("salary", "max")
).reset_index()

# ── Sorting (like ORDER BY) ───────────────────
df.sort_values("salary", ascending=False)
df.sort_values(["dept", "salary"], ascending=[True, False])

# ── Missing Values (like IS NULL) ────────────
df.isnull().sum()            # count nulls per column
df.dropna()                  # drop rows with any null
df.fillna(0)                 # replace nulls with 0
df.fillna({"salary": 0, "dept": "Unknown"})

# ── Write Output ──────────────────────────────
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
```

---

## 6. Full Mini-Pipeline (Combining Everything)

```python
import pandas as pd

def load_employees(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None

def process_employees(df):
    # Filter active employees only
    active = df[df["active"] == True].copy()

    # Add bonus column
    active["bonus"] = active["salary"] * 0.10

    # Remove duplicates
    active = active.drop_duplicates(subset=["emp_id"])

    return active

def summarize_by_dept(df):
    return df.groupby("dept").agg(
        headcount    = ("name",   "count"),
        total_salary = ("salary", "sum"),
        avg_salary   = ("salary", "mean")
    ).reset_index().sort_values("total_salary", ascending=False)

# Run the pipeline
df_raw     = load_employees("employees.csv")
df_clean   = process_employees(df_raw)
df_summary = summarize_by_dept(df_clean)
df_summary.to_csv("dept_summary.csv", index=False)
print("Pipeline complete.")
print(df_summary)
```

---

## My Notes
_(Write your own observations here as you practice)_
