# Week 1 — Python Syntax & Collections

## Study Checklist
- [x] Understand dynamic typing (no type declarations)
- [x] Practice list slicing: `list[start:end:step]`
- [x] Practice dictionary operations: get, update, iterate
- [x] Write 5 functions using default and keyword arguments
- [x] Write 5 lambda expressions
- [x] Practice list comprehensions

**Completed: 2026-05-13** ✅

---

## 1. Variables & Data Types

### C# vs Python
```csharp
// C# — must declare type
int age = 40;
string name = "Radha";
bool isActive = true;
double salary = 95000.50;
```

```python
# Python — no type declaration, dynamic typing
age = 40
name = "Radha"
is_active = True          # note: True/False (capital T/F)
salary = 95000.50

# Check type at any time
print(type(age))          # <class 'int'>
print(type(name))         # <class 'str'>
print(type(is_active))    # <class 'bool'>
```

### Key Differences from C#
| C# | Python |
|----|--------|
| `int x = 5;` | `x = 5` |
| `string s = "hi";` | `s = "hi"` (single or double quotes) |
| `bool b = true;` | `b = True` |
| `null` | `None` |
| `//` comment | `#` comment |
| `;` at end of line | No semicolon |
| `{}` for blocks | Indentation (4 spaces) |

---

## 2. Strings & F-Strings

```python
name = "Radha"
city = "Hyderabad"
exp  = 15

# Concatenation (like C# + operator)
msg = "Hello " + name

# F-string (like C# $"Hello {name}" interpolation)
msg = f"Hello {name}, you are from {city} with {exp} years experience"

# Multi-line string (like C# verbatim @"...")
bio = """
Name: Radha
City: Hyderabad
Experience: 15 years
"""

# Common string methods
name.upper()              # "RADHA"
name.lower()              # "radha"
name.strip()              # removes leading/trailing spaces
name.replace("a", "o")   # "Rodho"
name.startswith("R")      # True
name.endswith("a")        # True
len(name)                 # 5
name[0]                   # "R"  (first character)
name[-1]                  # "a"  (last character)

# Split and join
"sql,python,spark".split(",")        # ['sql', 'python', 'spark']
",".join(["sql", "python", "spark"]) # "sql,python,spark"
```

---

## 3. Lists (like C# List\<T\>)

```python
# Create
skills = ["sql", "python", "spark", "delta"]
numbers = [10, 20, 30, 40, 50]
mixed  = [1, "hello", True, 3.14]   # Python allows mixed types

# Access
skills[0]       # "sql"    — first item
skills[-1]      # "delta"  — last item
skills[-2]      # "spark"  — second from last

# Slicing [start : stop : step]  (stop is exclusive)
numbers[1:3]    # [20, 30]      — index 1 and 2
numbers[:3]     # [10, 20, 30]  — from start to index 2
numbers[2:]     # [30, 40, 50]  — from index 2 to end
numbers[::2]    # [10, 30, 50]  — every 2nd item
numbers[::-1]   # [50, 40, 30, 20, 10] — reversed

# Modify
skills.append("databricks")       # add to end
skills.insert(1, "azure")         # insert at index 1
skills.remove("python")           # remove by value
skills.pop()                      # remove and return last item
skills.pop(0)                     # remove and return item at index 0

# Info
len(skills)                       # count of items
"sql" in skills                   # True — membership check
skills.count("sql")               # how many times "sql" appears
skills.index("spark")             # index of first "spark"
skills.sort()                     # sort in place (ascending)
skills.reverse()                  # reverse in place

# Loop through list
for skill in skills:
    print(skill)

for i, skill in enumerate(skills):   # with index
    print(f"{i}: {skill}")
```

---

## 4. Tuples (immutable list)

```python
# Like a List but CANNOT be changed after creation
coords = (10, 20)
rgb    = (255, 128, 0)

coords[0]          # 10 — access same as list
# coords[0] = 99  # ERROR — tuples are immutable

# Unpack tuple into variables (very common in Python)
x, y = coords
r, g, b = rgb
print(x, y)        # 10 20

# Use case: returning multiple values from a function
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = get_stats([10, 20, 30, 40])
```

---

## 5. Dictionaries (like C# Dictionary\<K,V\>)

```python
# Create
person = {
    "name": "Radha",
    "city": "Hyderabad",
    "exp":  15,
    "skills": ["sql", "python", "spark"]
}

# Access
person["name"]                  # "Radha"
person.get("name")              # "Radha"
person.get("country", "India")  # "India" (default if key missing — safe)

# Modify
person["city"] = "Mumbai"       # update existing key
person["role"] = "Data Engineer" # add new key
del person["exp"]               # delete key

# Check key existence
"name" in person                # True
"salary" in person              # False

# Iterate
for key in person:
    print(key)

for key, value in person.items():
    print(f"{key}: {value}")

person.keys()     # dict_keys(['name', 'city', ...])
person.values()   # dict_values(['Radha', 'Mumbai', ...])

# Useful methods
person.pop("role")              # remove and return value
person.update({"exp": 15, "country": "India"})  # merge another dict
```

---

## 6. Sets (unique values only)

```python
# Like a mathematical set — no duplicates, no order
tags = {"sql", "python", "spark", "sql"}  # duplicate "sql" removed
print(tags)   # {'sql', 'python', 'spark'} — order not guaranteed

tags.add("databricks")
tags.remove("spark")
"sql" in tags           # True

# Set operations (very useful for data work)
a = {"sql", "python", "spark"}
b = {"python", "scala", "spark"}

a | b   # Union      → {'sql', 'python', 'spark', 'scala'}
a & b   # Intersection → {'python', 'spark'}
a - b   # Difference  → {'sql'}
```

---

## 7. Loops & Conditionals

```python
# if / elif / else  (same as C# if / else if / else)
score = 85

if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "F"

# Ternary (inline if — like C# ? : operator)
result = "Pass" if score >= 60 else "Fail"

# for loop
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):       # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8  (step=2)
    print(i)

# while loop
x = 0
while x < 5:
    print(x)
    x += 1      # Python has no x++ operator — use x += 1

# Loop control
for i in range(10):
    if i == 3:
        continue    # skip iteration (same as C#)
    if i == 7:
        break       # exit loop (same as C#)
    print(i)
```

---

## 8. List Comprehensions (Python superpower)

```python
# C# LINQ equivalent — much more concise in Python

# C#: var squares = numbers.Select(x => x * x).ToList();
squares = [x * x for x in range(1, 6)]
# [1, 4, 9, 16, 25]

# C#: var evens = numbers.Where(x => x % 2 == 0).ToList();
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# Combined filter + transform
even_squares = [x * x for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# With strings
skills = ["sql server", "azure sql", "oracle"]
upper_skills = [s.upper() for s in skills]
# ['SQL SERVER', 'AZURE SQL', 'ORACLE']

# Dict comprehension
scores = {"alice": 85, "bob": 72, "carol": 91}
passed = {name: score for name, score in scores.items() if score >= 80}
# {'alice': 85, 'carol': 91}
```

---

## My Notes
_(Write your own observations here as you practice)_
