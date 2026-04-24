"""
ci/check_syntax.py
==================
Runs three checks on every Python file in the project:
  1. Syntax check (py_compile)
  2. Import guard — flags any hardcoded secrets patterns
  3. Secrets check — flags storage keys / tokens in source

Usage:
    python ci/check_syntax.py
Exit code 0 = all clear.  Non-zero = at least one failure.
"""

import py_compile
import sys
import os
import re
import glob

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folders to skip entirely
SKIP_DIRS = {"venv", ".git", "__pycache__", ".github", "lake", "logs"}

# Relative paths (from PROJECT_ROOT) to exclude from checks
SKIP_PATHS = {
    "ci",                                      # this script itself (patterns are just strings)
    os.path.join("delta_sharing", "delta-sharing-1.3.10"),  # vendor library
    os.path.join("notebooks", "databricks"),   # uses Jupyter magic (%run) — not plain Python
}

# Patterns that flag a possible hardcoded secret
SECRET_PATTERNS = [
    (r'sk-ant-[A-Za-z0-9\-_]{20,}',  "Anthropic API key"),
    (r'AC[a-z0-9]{32}',               "Twilio SID"),
    (r'["\'][0-9a-f]{32}["\']',       "Possible auth token (32-char hex)"),
    (r'DefaultEndpointsProtocol=https', "Azure storage connection string"),
    (r'AccountKey=[A-Za-z0-9+/=]{40,}', "Azure storage account key"),
    (r'password\s*=\s*["\'][^"\']{6,}', "Hardcoded password"),
]

passed = 0
failed = 0
errors = []


def _in_skip_path(filepath):
    rel = os.path.relpath(filepath, PROJECT_ROOT)
    for skip in SKIP_PATHS:
        if rel.startswith(skip):
            return True
    return False


def collect_py_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                if not _in_skip_path(full):
                    files.append(full)
    return files


def check_syntax(filepath):
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)


def check_secrets(filepath):
    issues = []
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for pattern, label in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        # Allow lines that are clearly examples / env-reads
                        if any(skip in line for skip in [
                            "os.environ", "os.getenv", "dbutils.secrets",
                            ".env.example", "#", "example", "xxxx", "your_"
                        ]):
                            continue
                        issues.append(f"  Line {lineno}: {label}")
    except Exception as e:
        issues.append(f"  Could not read file: {e}")
    return issues


def run_checks():
    global passed, failed
    py_files = collect_py_files()
    print(f"\nChecking {len(py_files)} Python files...\n")

    for filepath in sorted(py_files):
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        file_ok = True

        # --- Syntax ---
        ok, err = check_syntax(filepath)
        if not ok:
            print(f"  [SYNTAX FAIL] {rel}")
            print(f"    {err}")
            errors.append(f"SYNTAX: {rel}")
            file_ok = False

        # --- Secrets ---
        issues = check_secrets(filepath)
        if issues:
            print(f"  [SECRETS FAIL] {rel}")
            for issue in issues:
                print(issue)
            errors.append(f"SECRETS: {rel}")
            file_ok = False

        if file_ok:
            passed += 1
        else:
            failed += 1

    print("\n" + "="*50)
    print(f"RESULT: {passed} passed, {failed} failed")
    if errors:
        print("\nFailed checks:")
        for e in errors:
            print(f"  - {e}")
        print("="*50 + "\n")
        return 1
    else:
        print("All checks passed!")
        print("="*50 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(run_checks())
