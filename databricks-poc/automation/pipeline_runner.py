"""
pipeline_runner.py
==================
Wraps run.py and individual pipeline scripts.
Captures stdout, returns structured result dicts.
Used by claude_tools.py to execute pipeline actions.
"""

import subprocess
import sys
import os
import time
import re

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
PYTHON       = sys.executable
RUN_PY       = os.path.join(PROJECT_ROOT, "run.py")

STEP_SCRIPTS = {
    "generate":  os.path.join(PROJECT_ROOT, "notebooks", "01_generate_data.py"),
    "bronze":    os.path.join(PROJECT_ROOT, "notebooks", "02_ingest_bronze.py"),
    "silver":    os.path.join(PROJECT_ROOT, "notebooks", "03_transform_silver.py"),
    "gold":      os.path.join(PROJECT_ROOT, "notebooks", "04_aggregate_gold.py"),
    "validate":  os.path.join(PROJECT_ROOT, "notebooks", "05_validate.py"),
    "sharing":   os.path.join(PROJECT_ROOT, "delta_sharing", "simulate_sharing.py"),
}

STEP_NAMES = {
    "generate": "Data Generation",
    "bronze":   "Bronze Ingestion",
    "silver":   "Silver Transformation",
    "gold":     "Gold Aggregation",
    "validate": "Pipeline Validation",
    "sharing":  "Delta Sharing Simulation",
}

# State file for last run result
STATE_FILE = os.path.join(PROJECT_ROOT, ".last_pipeline_run.txt")


def _run(cmd, timeout=900):
    """Run a command, capture output, return (returncode, stdout, elapsed)."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        elapsed = round(time.time() - start, 1)
        return result.returncode, result.stdout + result.stderr, elapsed
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start, 1)
        return 1, f"[TIMEOUT] Command exceeded {timeout}s", elapsed


def _save_state(text):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(text)


def _extract_summary(output):
    """Pull key lines from pipeline output for a concise reply."""
    lines = output.splitlines()
    summary = []
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in [
            "COMPLETE", "SUCCESS", "FAILED", "PASS", "FAIL",
            "records", "Elapsed", "Overall", "RESULT", "STATUS",
            "Generated", "Written", "Rows:", "Total"
        ]):
            # Strip ANSI / box-drawing noise
            clean = re.sub(r"[^\x20-\x7E]", "", line).strip()
            if clean and len(clean) > 3:
                summary.append(clean)
    return "\n".join(summary[:30])   # cap at 30 lines


def run_full_pipeline(runtime_override=None):
    """Run the complete pipeline via run_pipeline.py directly."""
    runtime = runtime_override or get_current_runtime()
    if runtime == "databricks":
        cmd = [PYTHON, RUN_PY, "--cloud"]
    else:
        cmd = [PYTHON, os.path.join(PROJECT_ROOT, "notebooks", "run_pipeline.py")]

    returncode, output, elapsed = _run(cmd, timeout=900)
    success = returncode == 0
    summary = _extract_summary(output)

    result = {
        "action":   "run_pipeline",
        "success":  success,
        "elapsed":  elapsed,
        "summary":  summary,
        "runtime":  runtime,
    }
    _save_state(str(result))
    return result


def run_step(step):
    """Run a single pipeline step by name."""
    step = step.lower()
    if step not in STEP_SCRIPTS:
        return {
            "action":  "run_step",
            "success": False,
            "summary": f"Unknown step '{step}'. Valid: {', '.join(STEP_SCRIPTS.keys())}",
        }

    script = STEP_SCRIPTS[step]
    returncode, output, elapsed = _run([PYTHON, script])
    success  = returncode == 0
    summary  = _extract_summary(output)

    result = {
        "action":  "run_step",
        "step":    STEP_NAMES[step],
        "success": success,
        "elapsed": elapsed,
        "summary": summary,
    }
    _save_state(str(result))
    return result


def run_sharing():
    """Run the Delta Sharing simulation (Option A)."""
    returncode, output, elapsed = _run(
        [PYTHON, STEP_SCRIPTS["sharing"]], timeout=300)
    success = returncode == 0
    summary = _extract_summary(output)

    result = {
        "action":  "run_sharing",
        "success": success,
        "elapsed": elapsed,
        "summary": summary,
    }
    _save_state(str(result))
    return result


def get_status():
    """Return the result of the last pipeline run."""
    if not os.path.exists(STATE_FILE):
        return {
            "action":  "get_status",
            "success": True,
            "summary": "No pipeline run recorded yet. Send 'run pipeline' to start.",
        }
    with open(STATE_FILE, encoding="utf-8") as f:
        content = f.read()
    return {
        "action":  "get_status",
        "success": True,
        "summary": f"Last run result:\n{content}",
    }


def get_current_runtime():
    """Read RUNTIME directly from pipeline_config.py (avoids cached imports)."""
    try:
        config_path = os.path.join(PROJECT_ROOT, "config", "pipeline_config.py")
        with open(config_path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'^RUNTIME\s*=\s*["\'](\w+)["\']', line)
                if m:
                    return m.group(1)
        return "unknown"
    except Exception:
        return "unknown"


def set_runtime(runtime):
    """Toggle RUNTIME flag in pipeline_config.py between local and databricks."""
    runtime = runtime.lower().strip()
    if runtime not in ("local", "databricks"):
        return {
            "action":  "set_runtime",
            "success": False,
            "summary": f"Invalid runtime '{runtime}'. Use 'local' or 'databricks'.",
        }

    config_path = os.path.join(PROJECT_ROOT, "config", "pipeline_config.py")
    with open(config_path, encoding="utf-8") as f:
        content = f.read()

    import re
    new_content = re.sub(
        r'^RUNTIME\s*=\s*["\'].*?["\']',
        f'RUNTIME = "{runtime}"',
        content,
        flags=re.MULTILINE
    )

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "action":  "set_runtime",
        "success": True,
        "summary": f"Runtime switched to '{runtime}'. Next pipeline run will use {runtime}.",
        "runtime": runtime,
    }
