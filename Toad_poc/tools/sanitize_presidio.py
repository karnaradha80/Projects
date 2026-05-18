"""
sanitize_presidio.py — Presidio-based Toad XML Sanitizer
Uses Microsoft Presidio (NLP) to detect and replace PII automatically.

Detects automatically:
  - Person names           → PERSON_1, PERSON_2, ...
  - Email addresses        → user1@domain, user2@domain, ...
  - Phone numbers          → 000-000-0000
  - IP addresses           → 0.0.0.0
  - Locations              → LOCATION_1, LOCATION_2, ...
  - Organisations          → ORG_1, ORG_2, ...
  - URLs                   → http://redacted
  - Passwords              → ***REDACTED*** (custom recogniser)
  - SMTP ports             → 999 (custom recogniser)

Also applies custom mappings from sanitize_mappings.csv for known values.

Usage:
  python sanitize_presidio.py <input_file>
  python sanitize_presidio.py <input_file> --output <output_file>
  python sanitize_presidio.py <input_file> --mappings <mappings_csv>
  python sanitize_presidio.py <input_file> --report   (show full PII report)
"""

import os
import re
import sys
import csv
import argparse
import logging
from typing import List, Dict, Tuple

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DEFAULT_MAPPINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sanitize_mappings.csv")


# ── Custom Presidio Recognisers ────────────────────────────────────────────────

def build_password_recogniser():
    """Detect Password=<value> patterns in Toad XML authentication strings."""
    return PatternRecognizer(
        supported_entity="PASSWORD",
        patterns=[
            Pattern("PASSWORD", r'(?<=Password=)[^,\"&\s]+', 0.9)
        ],
        name="PasswordRecogniser"
    )


def build_smtp_port_recogniser():
    """Detect SmtpPort values in Toad XML."""
    return PatternRecognizer(
        supported_entity="SMTP_PORT",
        patterns=[
            Pattern("SMTP_PORT", r'(?<=SmtpPort=\")\d+(?=\")', 0.9)
        ],
        name="SmtpPortRecogniser"
    )


def build_connection_string_recogniser():
    """Detect connection string tokens like Host=, Sid=, User Id= values."""
    return PatternRecognizer(
        supported_entity="DB_CONNECTION",
        patterns=[
            Pattern("HOST",    r'(?<=Host=)[^;,\s\"]+',    0.85),
            Pattern("SID",     r'(?<=Sid=)[^;,\s\"]+',     0.85),
            Pattern("USER_ID", r'(?<=User Id=)[^;,\s\"]+', 0.85),
        ],
        name="ConnectionStringRecogniser"
    )


# ── Presidio Engine Setup ──────────────────────────────────────────────────────

def build_analyzer():
    """Build Presidio AnalyzerEngine with spaCy large model and custom recognisers."""
    log.info("  Initialising Presidio NLP engine (en_core_web_lg)...")
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    analyzer.registry.add_recognizer(build_password_recogniser())
    analyzer.registry.add_recognizer(build_smtp_port_recogniser())
    analyzer.registry.add_recognizer(build_connection_string_recogniser())

    log.info("  Analyzer ready.")
    return analyzer


# ── Anonymisation Operators ────────────────────────────────────────────────────

def build_operators():
    """Define how each entity type should be anonymised."""
    return {
        "PERSON":       OperatorConfig("replace", {"new_value": "REPORT_OWNER"}),
        "EMAIL_ADDRESS":OperatorConfig("replace", {"new_value": "user@example.com"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "000-000-0000"}),
        "IP_ADDRESS":   OperatorConfig("replace", {"new_value": "0.0.0.0"}),
        "LOCATION":     OperatorConfig("replace", {"new_value": "LOCATION_X"}),
        "ORGANIZATION": OperatorConfig("replace", {"new_value": "ORG_X"}),
        "URL":          OperatorConfig("replace", {"new_value": "http://redacted"}),
        "PASSWORD":     OperatorConfig("replace", {"new_value": "***REDACTED***"}),
        "SMTP_PORT":    OperatorConfig("replace", {"new_value": "999"}),
        "DB_CONNECTION":OperatorConfig("replace", {"new_value": "REDACTED"}),
        "DEFAULT":      OperatorConfig("replace", {"new_value": "REDACTED"}),
    }


# ── Make email replacements consistent ────────────────────────────────────────

def anonymise_emails_consistently(content: str) -> Tuple[str, Dict]:
    """
    Replace each unique email with a consistent user1@domain, user2@domain etc.
    Done before Presidio so Presidio doesn't see fragments.
    """
    found = {}
    counter = [1]

    def replacer(match):
        email = match.group(0).lower()
        if email not in found:
            domain = email.split("@")[1]
            found[email] = f"user{counter[0]}@{domain}"
            counter[0] += 1
        return found[email]

    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    new_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
    return new_content, found


# ── Custom mappings ────────────────────────────────────────────────────────────

def load_custom_mappings(mappings_file: str) -> List[Tuple[str, str]]:
    """Load custom find/replace pairs from CSV mappings file."""
    mappings = []
    if not os.path.exists(mappings_file):
        log.warning(f"  Mappings file not found: {mappings_file} — skipping")
        return mappings

    with open(mappings_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 1)
            if len(parts) == 2:
                original, replacement = parts[0].strip(), parts[1].strip()
                if original:
                    mappings.append((original, replacement))

    log.info(f"  Loaded {len(mappings)} custom mapping(s)")
    return mappings


def apply_custom_mappings(content: str, mappings: List[Tuple[str, str]]) -> Tuple[str, int]:
    """Apply custom find/replace mappings."""
    total = 0
    for original, replacement in mappings:
        count = content.count(original)
        if count > 0:
            content = content.replace(original, replacement)
            log.info(f"  [CUSTOM] [{count}] '{original}' → '{replacement}'")
            total += count
    if total == 0:
        log.info("  [CUSTOM] No custom mapping matches found")
    return content, total


# ── File I/O ───────────────────────────────────────────────────────────────────

def read_file(file_path: str) -> Tuple[str, str]:
    """Read file — auto-detect UTF-16 or UTF-8 encoding."""
    try:
        with open(file_path, "r", encoding="utf-16") as f:
            content = f.read()
        log.info(f"  Encoding detected: UTF-16")
        return content, "utf-16"
    except (UnicodeDecodeError, UnicodeError):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        log.info(f"  Encoding detected: UTF-8")
        return content, "utf-8"


def write_output(content: str, output_path: str):
    """Write sanitized content as UTF-8."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    log.info(f"  Saved: {output_path}")


# ── Verification ───────────────────────────────────────────────────────────────

def verify(content: str, email_map: Dict, mappings: List[Tuple[str, str]]):
    """Check no original sensitive values remain."""
    issues = []
    for original in email_map:
        if original in content.lower():
            issues.append(f"Email may still be present: {original}")
    for original, _ in mappings:
        if original in content:
            issues.append(f"Custom mapping value still present: {original}")
    return issues


# ── Main Sanitizer ─────────────────────────────────────────────────────────────

def sanitize(input_file: str, output_file: str = None,
             mappings_file: str = DEFAULT_MAPPINGS, show_report: bool = False):

    log.info("=" * 65)
    log.info(f"Presidio Sanitizer — {os.path.basename(input_file)}")
    log.info("=" * 65)

    # Output path
    if not output_file:
        base, _ = os.path.splitext(input_file)
        output_file = base + "_sanitized.txt"

    # Step 1: Read file
    log.info("\n[1/5] Reading file...")
    content, encoding = read_file(input_file)
    log.info(f"  Size: {len(content):,} characters")

    # Step 2: Custom mappings first (known values — fast, exact)
    log.info("\n[2/5] Applying custom mappings...")
    mappings = load_custom_mappings(mappings_file)
    content, _ = apply_custom_mappings(content, mappings)

    # Step 3: Consistent email anonymisation (before Presidio to avoid fragments)
    log.info("\n[3/5] Anonymising email addresses...")
    content, email_map = anonymise_emails_consistently(content)
    log.info(f"  Replaced {len(email_map)} unique email(s)")
    for original, replacement in email_map.items():
        log.info(f"    {original} → {replacement}")

    # Step 4: Presidio NLP analysis + anonymisation
    log.info("\n[4/5] Running Presidio NLP analysis...")
    analyzer  = build_analyzer()
    anonymizer = AnonymizerEngine()
    operators  = build_operators()

    # Analyse — Presidio works best on plain text chunks
    # Split on XML tag boundaries to improve NER accuracy
    results = analyzer.analyze(text=content, language="en",
                                entities=["PERSON", "PHONE_NUMBER", "IP_ADDRESS",
                                          "LOCATION", "ORGANIZATION", "URL",
                                          "PASSWORD", "SMTP_PORT", "DB_CONNECTION"])

    if show_report:
        log.info(f"\n  Presidio detected {len(results)} PII instance(s):")
        for r in sorted(results, key=lambda x: x.start):
            snippet = content[r.start:r.end]
            log.info(f"    [{r.entity_type}] score={r.score:.2f} → '{snippet}'")

    log.info(f"  Detected {len(results)} PII instance(s) via NLP")

    # Anonymise
    if results:
        anonymized = anonymizer.anonymize(
            text=content,
            analyzer_results=results,
            operators=operators
        )
        content = anonymized.text

        # Count by entity type
        from collections import Counter
        type_counts = Counter(r.entity_type for r in results)
        for entity_type, count in sorted(type_counts.items()):
            log.info(f"    [{entity_type}] {count} instance(s) replaced")
    else:
        log.info("  No additional PII detected by NLP")

    # Step 5: Verify and write output
    log.info("\n[5/5] Verifying and saving...")
    issues = verify(content, email_map, mappings)
    if issues:
        log.warning(f"  {len(issues)} potential issue(s) remaining:")
        for issue in issues:
            log.warning(f"    - {issue}")
    else:
        log.info("  Verification passed — no known sensitive values remain")

    write_output(content, output_file)

    log.info("\n" + "=" * 65)
    log.info(f"Done. Sanitized file saved to:")
    log.info(f"  {output_file}")
    log.info("=" * 65)
    return output_file


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Presidio-based Toad XML sanitizer — removes PII using NLP."
    )
    parser.add_argument("input_file",        help="Toad XML file to sanitize")
    parser.add_argument("--output",   "-o",  help="Output file path (default: <input>_sanitized.txt)")
    parser.add_argument("--mappings", "-m",  help="Custom mappings CSV", default=DEFAULT_MAPPINGS)
    parser.add_argument("--report",   "-r",  action="store_true",
                        help="Show full PII detection report")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        log.error(f"File not found: {args.input_file}")
        sys.exit(1)

    sanitize(args.input_file, args.output, args.mappings, args.report)


if __name__ == "__main__":
    main()
