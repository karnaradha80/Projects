"""
Global Mapping Registry
Maintains a consistent, persistent mapping of real values → mock values across all reports.
Same real value always produces the same mock value, regardless of which report it appears in.

Email mapping rules:
  - Each unique email gets a unique sequential mock: emailid{n}@company{m}.com
  - Domain-aware: each original domain gets its own number range and mock domain
    Domain 1 (first seen): emailid1, emailid2 ...       @ company1.com
    Domain 2:              emailid1001, emailid1002 ...  @ company2.com
    Domain 3:              emailid2001, emailid2002 ...  @ company3.com
"""

import csv
import os
import re
from datetime import date

REGISTRY_COLUMNS = [
    'original_value', 'mock_value', 'category',
    'domain_group', 'first_seen_report', 'created_date'
]

DOMAIN_RANGE_SIZE = 1000  # each domain gets a block of 1000 IDs


class MappingRegistry:
    def __init__(self, registry_path):
        self.registry_path = registry_path
        self._entries = {}          # original_value -> row dict
        self._domain_ranges = {}    # original_domain -> {mock_domain, counter}
        self._category_counts = {}  # category -> int
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_or_create(self, original_value, category, report_name=''):
        """Return mock value for original_value, creating a new mapping if needed."""
        original_value = original_value.strip()
        if not original_value:
            return original_value
        if original_value in self._entries:
            return self._entries[original_value]['mock_value']

        mock_value = self._generate(original_value, category)
        self._entries[original_value] = {
            'original_value': original_value,
            'mock_value':     mock_value,
            'category':       category,
            'domain_group':   self._get_domain(original_value) if category == 'EMAIL' else '',
            'first_seen_report': report_name,
            'created_date':   str(date.today()),
        }
        self._category_counts[category] = self._category_counts.get(category, 0) + 1
        self._save()
        return mock_value

    def get_report_mappings(self, original_values):
        """Return registry rows for the given set of original values."""
        return [
            {k: v for k, v in self._entries[val].items() if k in ('original_value', 'mock_value', 'category')}
            for val in original_values
            if val in self._entries
        ]

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def _load(self):
        if not os.path.exists(self.registry_path):
            return
        with open(self.registry_path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                self._entries[row['original_value']] = row
                self._rebuild_domain_range(row)
                cat = row['category']
                self._category_counts[cat] = self._category_counts.get(cat, 0) + 1

    def _save(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=REGISTRY_COLUMNS)
            writer.writeheader()
            writer.writerows(self._entries.values())

    def _rebuild_domain_range(self, row):
        """Reconstruct domain counter state from an existing registry row."""
        if row['category'] != 'EMAIL' or not row['domain_group']:
            return
        domain = row['domain_group']
        mock_email = row['mock_value']
        mock_domain = mock_email.split('@')[1] if '@' in mock_email else 'company1.com'
        m = re.search(r'emailid(\d+)@', mock_email)
        if m:
            n = int(m.group(1))
            if domain not in self._domain_ranges:
                self._domain_ranges[domain] = {'mock_domain': mock_domain, 'counter': 0}
            if n > self._domain_ranges[domain]['counter']:
                self._domain_ranges[domain]['counter'] = n

    # ------------------------------------------------------------------
    # Mock value generators
    # ------------------------------------------------------------------

    def _generate(self, value, category):
        n = self._category_counts.get(category, 0) + 1
        generators = {
            'EMAIL':       lambda: self._gen_email(value),
            'PASSWORD':    lambda: '***REDACTED***',
            'SERVER':      lambda: f'SERVER_{n:02d}',
            'SCHEMA':      lambda: f'SCHEMA_{n:02d}',
            'SMTP_SERVER': lambda: 'smtp.mockserver.com',
            'ACCOUNT':     lambda: f'svc_account{n:02d}',
            'DSN':         lambda: f'ODBC_DSN_{n:02d}',
            'PATH':        lambda: f'\\\\FILESERVER\\reports\\path{n:02d}',
            'PERSON':      lambda: f'user{n}',
        }
        return generators.get(category, lambda: f'{category.lower()}_{n}')()

    def _gen_email(self, email):
        domain = self._get_domain(email)
        if domain not in self._domain_ranges:
            slot = len(self._domain_ranges)          # 0-based slot
            counter_start = slot * DOMAIN_RANGE_SIZE + 1
            mock_domain = f'company{slot + 1}.com'
            self._domain_ranges[domain] = {
                'mock_domain': mock_domain,
                'counter':     counter_start - 1,    # will be incremented before use
            }
        self._domain_ranges[domain]['counter'] += 1
        n = self._domain_ranges[domain]['counter']
        mock_domain = self._domain_ranges[domain]['mock_domain']
        return f'emailid{n}@{mock_domain}'

    @staticmethod
    def _get_domain(email):
        return email.split('@')[1].lower().strip() if '@' in email else ''
