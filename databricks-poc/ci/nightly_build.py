"""
ci/nightly_build.py
===================
Nightly Build — runs every night at 2 AM via Windows Task Scheduler.

What it does:
  1. Runs the full local pipeline (generate → bronze → silver → gold → validate)
  2. Sends a WhatsApp message with the result (pass/fail + elapsed time)
  3. Writes a log file to logs/nightly_YYYY-MM-DD.log

Setup (one-time):
  Run ci/setup_nightly.bat as Administrator to register the Task Scheduler job.
  Or run manually: python ci/nightly_build.py
"""

import os
import sys
import json
import time
import datetime
import subprocess
import logging

# ---- Resolve project root regardless of where this is launched from ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ---- Logging ----
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
today = datetime.date.today().isoformat()
LOG_FILE = os.path.join(LOG_DIR, f"nightly_{today}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("nightly")


def send_whatsapp(message: str):
    """Send a WhatsApp message via Twilio REST API (no FastAPI needed)."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, "automation", ".env"))

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token  = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_number = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    to_number   = os.environ.get("TWILIO_WHATSAPP_TO", "")   # your WhatsApp number

    if not all([account_sid, auth_token, to_number]):
        log.warning("Twilio credentials or TWILIO_WHATSAPP_TO not set — skipping WhatsApp notification")
        return

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        client.messages.create(
            from_=from_number,
            to=to_number,
            body=message,
        )
        log.info("WhatsApp notification sent.")
    except Exception as e:
        log.error(f"WhatsApp send failed: {e}")


def run_pipeline():
    """Run the local pipeline, return (success, elapsed, summary)."""
    log.info("Starting nightly pipeline run...")
    start = time.time()

    script = os.path.join(PROJECT_ROOT, "notebooks", "run_pipeline.py")
    python = sys.executable

    try:
        result = subprocess.run(
            [python, script],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min max
            cwd=PROJECT_ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        elapsed = round(time.time() - start, 1)
        success = result.returncode == 0
        output  = result.stdout + result.stderr

        # Write full output to log
        log.info(f"Pipeline exit code: {result.returncode}")
        for line in output.splitlines()[:100]:    # first 100 lines
            log.info(f"  {line}")

        # Pull key lines for the WhatsApp message
        key_lines = []
        for line in output.splitlines():
            line = line.strip()
            if any(kw in line for kw in [
                "COMPLETE", "SUCCESS", "FAILED", "PASS", "FAIL",
                "Overall", "Elapsed", "records", "Total"
            ]):
                import re
                clean = re.sub(r"[^\x20-\x7E]", "", line).strip()
                if clean and len(clean) > 3:
                    key_lines.append(clean)

        summary = "\n".join(key_lines[:10]) or "No summary captured"
        return success, elapsed, summary

    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start, 1)
        log.error("Pipeline TIMED OUT after 30 minutes!")
        return False, elapsed, "Pipeline timed out after 30 minutes"

    except Exception as e:
        elapsed = round(time.time() - start, 1)
        log.error(f"Pipeline error: {e}")
        return False, elapsed, str(e)


def run_ci_check():
    """Run the CI syntax/secrets check, return (passed, details)."""
    log.info("Running CI checks...")
    python = sys.executable
    script = os.path.join(PROJECT_ROOT, "ci", "check_syntax.py")

    result = subprocess.run(
        [python, script],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    passed = result.returncode == 0
    output = result.stdout + result.stderr
    return passed, output


def main():
    log.info("=" * 60)
    log.info(f"NIGHTLY BUILD — {today}")
    log.info("=" * 60)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Step 1: CI check
    ci_passed, ci_output = run_ci_check()
    ci_status = "PASS" if ci_passed else "FAIL"
    log.info(f"CI check: {ci_status}")

    # Step 2: Pipeline run
    pipeline_ok, elapsed, summary = run_pipeline()
    pipeline_status = "SUCCESS" if pipeline_ok else "FAILED"
    log.info(f"Pipeline: {pipeline_status} in {elapsed}s")

    # Step 3: Overall result
    overall = "ALL GOOD" if (ci_passed and pipeline_ok) else "ISSUES FOUND"
    emoji = "" if (ci_passed and pipeline_ok) else ""

    # Step 4: WhatsApp message
    msg = (
        f"{emoji} Utilitics Nightly Build — {now}\n\n"
        f"CI Check:  {ci_status}\n"
        f"Pipeline:  {pipeline_status}\n"
        f"Duration:  {elapsed}s\n\n"
        f"Summary:\n{summary}\n\n"
        f"Result: {overall}\n"
        f"Log: logs/nightly_{today}.log"
    )

    log.info("Sending WhatsApp notification...")
    send_whatsapp(msg)

    log.info("=" * 60)
    log.info(f"Nightly build complete. Result: {overall}")
    log.info("=" * 60)

    return 0 if (ci_passed and pipeline_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
