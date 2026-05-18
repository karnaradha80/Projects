# Phase 0 — Day 1 Practice Exercises
# Run this file in VS Code or paste each block in Python terminal
# Your C# skills transfer directly — just new syntax

# ─────────────────────────────────────────────
# EXERCISE 1 — Variables & F-strings
# ─────────────────────────────────────────────
# Create variables for your name, years of experience, and tech stack list
# Print a sentence using f-string

name = "Radha"
experience = 15
tech_stack = ["C#", "SQL Server", "Azure SQL", "Oracle"]

# TODO: print this using f-string:
# "Radha has 15 years of experience in: C#, SQL Server, Azure SQL, Oracle"
print(f"{name} has {experience} years of experience in: {', '.join(tech_stack)}")


# ─────────────────────────────────────────────
# EXERCISE 2 — List operations
# ─────────────────────────────────────────────
# Start with this list of technologies
technologies = ["C#", "SQL Server", "Azure SQL", "Oracle", "Python", "Spark"]

# TODO: complete each task
print(technologies[0])           # first item
print(technologies[-1])          # last item
print(technologies[1:3])         # second and third items
print(technologies[::-1])        # reversed list
print(len(technologies))         # count

# Add Databricks to the list
technologies.append("Databricks")
print(technologies)

# Remove C# from the list
technologies.remove("C#")
print(technologies)


# ─────────────────────────────────────────────
# EXERCISE 3 — Dictionary
# ─────────────────────────────────────────────
# Create a profile dictionary
profile = {
    "name": "Radha",
    "experience_years": 15,
    "current_role": "Data Engineer",
    "skills": ["SQL", "C#", "Oracle"],
    "learning": "Databricks"
}

# TODO: complete each task
print(profile["name"])                        # access name
print(profile.get("city", "Not provided"))    # safe access with default
profile["city"] = "Hyderabad"                 # add new key
print(profile)

# Loop and print all key: value pairs
for key, value in profile.items():
    print(f"  {key}: {value}")


# ─────────────────────────────────────────────
# EXERCISE 4 — List Comprehension
# ─────────────────────────────────────────────
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Using list comprehensions (replace the [] with your answer):
squares     = [x ** 2 for x in numbers]                   # square each number
evens       = [x for x in numbers if x % 2 == 0]          # only even numbers
even_squares= [x ** 2 for x in numbers if x % 2 == 0]     # square of evens only

print("Squares:", squares)
print("Evens:", evens)
print("Even squares:", even_squares)


# ─────────────────────────────────────────────
# EXERCISE 5 — Conditionals & Loops
# ─────────────────────────────────────────────
# Given a list of exam scores, classify each as Pass/Fail
# Pass = 70 or above

scores = [85, 62, 91, 55, 78, 43, 88, 70]

# TODO: print each score with its result
for score in scores:
    result = "Pass" if score >= 70 else "Fail"
    print(f"Score {score}: {result}")

# Bonus: count how many passed using list comprehension
passed_count = len([s for s in scores if s >= 70])
print(f"\nTotal passed: {passed_count} out of {len(scores)}")


# ─────────────────────────────────────────────
# EXERCISE 6 — Tuple unpacking
# ─────────────────────────────────────────────
# This is a common Python pattern — return multiple values as tuple
def get_salary_stats(salaries):
    return min(salaries), max(salaries), sum(salaries) // len(salaries)

salaries = [75000, 90000, 65000, 110000, 85000]

# Unpack all 3 return values at once
low, high, avg = get_salary_stats(salaries)
print(f"\nSalary stats:")
print(f"  Min: ${low:,}")
print(f"  Max: ${high:,}")
print(f"  Avg: ${avg:,}")


# ─────────────────────────────────────────────
# EXERCISE 7 — Set operations (data dedup)
# ─────────────────────────────────────────────
# This is very useful in data engineering — finding duplicates/overlap

team_a_skills = {"SQL", "Python", "Azure", "Databricks"}
team_b_skills = {"Python", "Spark", "Databricks", "Scala"}

shared     = team_a_skills & team_b_skills   # intersection
all_skills = team_a_skills | team_b_skills   # union
only_a     = team_a_skills - team_b_skills   # only in team A

print(f"\nShared skills: {shared}")
print(f"All skills: {all_skills}")
print(f"Team A only: {only_a}")
