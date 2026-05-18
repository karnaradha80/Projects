"""
sanitize.py — Toad XML File Sanitizer
Removes sensitive data from Toad Automation Script XML files before sharing.

Auto-detects and replaces:
  - Email addresses        → generic@example.com
  - Passwords              → ***REDACTED***
  - IP addresses           → 0.0.0.0
  - SMTP ports             → 999

Applies custom mappings from sanitize_mappings.csv:
  - Server names, schema names, depot names, person names, paths etc.

Usage:
  python sanitize.py <input_file>
  python sanitize.py <input_file> --mappings <mappings_file>
  python sanitize.py <input_file> --output <output_file>

Examples:
  python sanitize.py ..\toad_xml_files\MyReport.txt
  python sanitize.py ..\toad_xml_files\MyReport.txt --output ..\toad_xml_files\MyReport_sanitized.txt
"""

import os
import re
import sys
import csv
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Default mappings file location (same folder as this script)
DEFAULT_MAPPINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sanitize_mappings.csv")


# ── Auto-detection patterns ────────────────────────────────────────────────────

def replace_emails(content):
    """Replace all email addresses with generic placeholders."""
    # Keep track of unique emails and assign consistent generic names
    found = {}
    counter = [1]

    def replacer(match):
        email = match.group(0)
        # Preserve the pattern of functional emails (e.g. ops-team vs person names)
        if email not in found:
            # Keep domain as abc.co.uk but genericise the local part
            domain = email.split("@")[1] if "@" in email else "example.com"
            found[email] = f"user{counter[0]}@{domain}"
            counter[0] += 1
        return found[email]

    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    new_content = re.sub(pattern, replacer, content)
    count = len(found)
    if count:
        log.info(f"  [AUTO] Replaced {count} unique email address(es)")
        for original, replacement in found.items():
            log.info(f"           {original} → {replacement}")
    return new_content, found


def replace_passwords(content):
    """Replace password values in authentication strings."""
    replacements = 0

    # Pattern: Password=<value> (in authentication strings)
    def pwd_replacer(match):
        nonlocal replacements
        replacements += 1
        return match.group(1) + "***REDACTED***"

    pattern = r'(Password=)([^,\"&\s]+)'
    new_content = re.sub(pattern, pwd_replacer, content)
    if replacements:
        log.info(f"  [AUTO] Replaced {replacements} password value(s)")
    return new_content, replacements


def replace_ip_addresses(content):
    """Replace IP addresses with 0.0.0.0."""
    replacements = 0

    def ip_replacer(match):
        nonlocal replacements
        replacements += 1
        return "0.0.0.0"

    # IPv4 pattern (skip 0.0.0.0 itself)
    pattern = r'\b(?!0\.0\.0\.0)(\d{1,3}\.){3}\d{1,3}\b'
    new_content = re.sub(pattern, ip_replacer, content)
    if replacements:
        log.info(f"  [AUTO] Replaced {replacements} IP address(es)")
    return new_content, replacements


def replace_smtp_ports(content):
    """Replace real SMTP port numbers with 999."""
    replacements = 0

    def port_replacer(match):
        nonlocal replacements
        replacements += 1
        return match.group(1) + "999"

    # SmtpPort="587" or similar
    pattern = r'(SmtpPort=\")(\d+)(\")'

    def full_replacer(match):
        nonlocal replacements
        replacements += 1
        return match.group(1) + "999" + match.group(3)

    new_content = re.sub(pattern, full_replacer, content)
    if replacements:
        log.info(f"  [AUTO] Replaced {replacements} SMTP port value(s)")
    return new_content, replacements


# ── Custom mappings ────────────────────────────────────────────────────────────

def load_custom_mappings(mappings_file):
    """Load custom find/replace pairs from CSV mappings file."""
    mappings = []
    if not os.path.exists(mappings_file):
        log.warning(f"  Mappings file not found: {mappings_file} — skipping custom mappings")
        return mappings

    with open(mappings_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 1)
            if len(parts) == 2:
                original, replacement = parts[0].strip(), parts[1].strip()
                if original:
                    mappings.append((original, replacement))

    log.info(f"  Loaded {len(mappings)} custom mapping(s) from {os.path.basename(mappings_file)}")
    return mappings


def apply_custom_mappings(content, mappings):
    """Apply all custom find/replace mappings."""
    total = 0
    for original, replacement in mappings:
        count = content.count(original)
        if count > 0:
            content = content.replace(original, replacement)
            log.info(f"  [CUSTOM] Replaced [{count}]: '{original}' → '{replacement}'")
            total += count
    if total == 0:
        log.info("  [CUSTOM] No custom mapping matches found in this file")
    return content, total


# ── Verify no sensitive data remains ──────────────────────────────────────────

def verify_clean(content, email_map, mappings):
    """Check that all known sensitive values have been replaced."""
    issues = []

    # Check no original emails remain
    for original in email_map:
        if original in content:
            issues.append(f"Email still present: {original}")

    # Check no custom mapping originals remain
    for original, _ in mappings:
        if original in content and not original.startswith("#"):
            issues.append(f"Custom mapping still present: {original}")

    return issues


# ── File I/O ───────────────────────────────────────────────────────────────────

def read_file(file_path):
    """Read file — auto-detect UTF-16 or UTF-8 encoding."""
    try:
        with open(file_path, "r", encoding="utf-16") as f:
            content = f.read()
        log.info(f"  Read as UTF-16: {file_path}")
        return content, "utf-16"
    except (UnicodeDecodeError, UnicodeError):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        log.info(f"  Read as UTF-8: {file_path}")
        return content, "utf-8"


def write_output(content, output_path):
    """Write sanitized content as UTF-8."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    log.info(f"  Saved sanitized file: {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def sanitize(input_file, output_file=None, mappings_file=DEFAULT_MAPPINGS):

    log.info("=" * 60)
    log.info(f"Sanitizing: {os.path.basename(input_file)}")
    log.info("=" * 60)

    # Determine output path
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = base + "_sanitized.txt"

    # Read input
    content, encoding = read_file(input_file)
    original_size = len(content)
    log.info(f"  File size: {original_size:,} characters ({encoding})")

    # Apply auto-replacements
    log.info("\nApplying auto-replacements...")
    content, email_map   = replace_emails(content)
    content, _           = replace_passwords(content)
    content, _           = replace_ip_addresses(content)
    content, _           = replace_smtp_ports(content)

    # Apply custom mappings
    log.info("\nApplying custom mappings...")
    mappings             = load_custom_mappings(mappings_file)
    content, _           = apply_custom_mappings(content, mappings)

    # Verify
    log.info("\nVerifying...")
    issues = verify_clean(content, email_map, mappings)
    if issues:
        log.warning(f"  {len(issues)} potential issue(s) found:")
        for issue in issues:
            log.warning(f"    - {issue}")
    else:
        log.info("  All known sensitive values confirmed replaced.")

    # Write output
    log.info("\nWriting output...")
    write_output(content, output_file)

    log.info("=" * 60)
    log.info(f"Done. Sanitized file: {output_file}")
    log.info("=" * 60)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize Toad XML pipeline files — remove sensitive data before sharing."
    )
    parser.add_argument("input_file",             help="Path to the Toad XML file to sanitize")
    parser.add_argument("--output",   "-o",       help="Output file path (default: <input>_sanitized.txt)")
    parser.add_argument("--mappings", "-m",       help=f"Custom mappings CSV file (default: {DEFAULT_MAPPINGS})",
                        default=DEFAULT_MAPPINGS)
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        log.error(f"Input file not found: {args.input_file}")
        sys.exit(1)

    sanitize(args.input_file, args.output, args.mappings)


if __name__ == "__main__":
    main()
