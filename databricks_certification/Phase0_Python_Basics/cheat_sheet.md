# Python vs C# — Quick Reference Cheat Sheet

## Variables & Types
| C# | Python |
|----|--------|
| `int x = 5;` | `x = 5` |
| `string name = "John";` | `name = "John"` |
| `bool isActive = true;` | `is_active = True` |
| `var items = new List<string>();` | `items = []` |
| `Console.WriteLine(x);` | `print(x)` |

## String Formatting
```python
name = "Radha"
age = 15

# f-string (like C# interpolation $"")
print(f"Name: {name}, Age: {age}")

# String methods
"hello world".upper()        # HELLO WORLD
"hello world".title()        # Hello World
"  hello  ".strip()          # hello
"a,b,c".split(",")           # ['a', 'b', 'c']
",".join(["a", "b", "c"])    # a,b,c
```

## Collections
```python
# List (like C# List<T>)
nums = [1, 2, 3, 4, 5]
nums.append(6)
nums[0]        # 1 (first element)
nums[-1]       # 5 (last element)
nums[1:3]      # [2, 3] (slicing)

# Dictionary (like C# Dictionary<K,V>)
person = {"name": "Radha", "age": 40}
person["name"]           # Radha
person.get("city", "NA") # NA (safe get with default)
person.keys()
person.values()
person.items()           # key-value pairs

# Tuple (immutable list)
coords = (10, 20)

# Set (unique values)
tags = {"sql", "python", "spark"}
```

## Loops
```python
# for loop
for i in range(5):        # 0,1,2,3,4
    print(i)

for item in my_list:
    print(item)

for key, value in my_dict.items():
    print(f"{key}: {value}")

# while loop
x = 0
while x < 5:
    x += 1
```

## Functions
```python
# Basic function (no types needed)
def add(a, b):
    return a + b

# Default parameters
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Lambda (like C# arrow functions)
square = lambda x: x * x
double = lambda x: x * 2

# *args (variable arguments)
def sum_all(*args):
    return sum(args)
```

## Conditionals
```python
# if/elif/else (same as C# if/else if/else)
if x > 10:
    print("big")
elif x > 5:
    print("medium")
else:
    print("small")

# Ternary (inline if)
result = "yes" if x > 0 else "no"
```

## List Comprehensions (Python superpower)
```python
# C# LINQ equivalent
# C#: var evens = nums.Where(x => x % 2 == 0).ToList();
evens = [x for x in nums if x % 2 == 0]

# C#: var squares = nums.Select(x => x * x).ToList();
squares = [x * x for x in nums]

# With condition
result = [x * 2 for x in range(10) if x % 2 == 0]
```

## Classes
```python
# C# class equivalent
class Person:
    def __init__(self, name, age):   # constructor
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, I'm {self.name}"

    def __str__(self):               # like C# ToString()
        return f"Person({self.name}, {self.age})"

p = Person("Radha", 40)
print(p.greet())
```

## Exception Handling
```python
# Same concept as C# try/catch/finally
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected: {e}")
finally:
    print("Always runs")
```

## File I/O
```python
# Read file
with open("file.txt", "r") as f:
    content = f.read()

# Write file
with open("output.txt", "w") as f:
    f.write("Hello World")
```

## Pandas Basics (think SQL result set)
```python
import pandas as pd

# Read CSV (like SqlDataReader into a DataTable)
df = pd.read_csv("data.csv")

# Inspect
df.head(5)           # first 5 rows
df.shape             # (rows, cols)
df.columns           # column names
df.dtypes            # data types
df.describe()        # stats summary

# Filter (like SQL WHERE)
df[df["age"] > 30]
df[(df["age"] > 30) & (df["city"] == "NY")]

# Select columns (like SQL SELECT)
df[["name", "age"]]

# Aggregate (like SQL GROUP BY)
df.groupby("city")["salary"].mean()
df.groupby("dept").agg({"salary": "sum", "age": "mean"})

# New column (like SQL computed column)
df["full_name"] = df["first"] + " " + df["last"]

# Sort (like SQL ORDER BY)
df.sort_values("salary", ascending=False)
```
