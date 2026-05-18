"""
Toad XML Parser
Extracts all sensitive values from a Toad Automation XML file.

Toad XML structure:
  <ToadAutomationScript>
    <ConnectionTrl>...</ConnectionTrl>
    <Xoml Name="ReportName.xoml">
      <Source><![CDATA[ ...XAML pipeline definition... ]]></Source>
    </Xoml>
  </ToadAutomationScript>

All sensitive data lives inside the CDATA block as XAML attributes.
"""

import re

# ---- Regex patterns -------------------------------------------------------

EMAIL_RE      = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PASSWORD_RE   = re.compile(r'Password=([^,\s"&<>]+)')
AUTH_USER_RE  = re.compile(r'UserName=([^,\s"&<>]+)')
ORACLE_TRL_RE = re.compile(r'oracle://([^@]+)@([^/"]+)')   # oracle://SCHEMA@SERVER
ODBC_TRL_RE   = re.compile(r'odbc://([^@]+)@([^/"]+)')     # odbc://account@DSN
UNC_PATH_RE   = re.compile(r'\\\\[A-Za-z0-9_\-\.]+\\[^\s"&<>]+')
SMTP_RE       = re.compile(r'SmtpServer="([^"]+)"')
XOML_NAME_RE  = re.compile(r'<Xoml Name="([^"]+)"')
ACTIVITY_RE   = re.compile(r'<(ta\d*:[A-Za-z]+Activity)[^>]*x:Name="([^"]+)"')
FROM_RE       = re.compile(r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
JOIN_RE       = re.compile(r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
FILE_ATTR_RE  = re.compile(
    r'(?:FileName|SourceFileName|DestinationFolder|BodyFileName|ResultFileName|ExcelFileName|FileDirectory)'
    r'="([^"]*\\\\[^"]*)"'
)

def _decode_entities(text):
    return (text
            .replace('&#xD;&#xA;', '\n')
            .replace('&#xD;', '\r')
            .replace('&#xA;', '\n')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&amp;', '&')
            .replace('&quot;', '"'))


class ToadXmlParser:

    def __init__(self, file_path):
        self.file_path  = file_path
        self.raw        = self._read()
        self.report_name = ''

        # Collected sensitive values (sets avoid duplicates)
        self.emails         = set()
        self.passwords      = set()
        self.servers        = set()
        self.oracle_schemas = set()
        self.usernames      = set()
        self.dsns           = set()
        self.unc_paths      = set()
        self.smtp_servers   = set()
        self.schemas        = set()
        self.tables         = set()
        self.pipeline_steps = []    # ordered list of {name, type}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def parse(self):
        xoml_m = XOML_NAME_RE.search(self.raw)
        if xoml_m:
            self.report_name = xoml_m.group(1).replace('.xoml', '')

        cdata_m = re.search(r'<!\[CDATA\[(.*?)\]\]>', self.raw, re.DOTALL)
        xaml = cdata_m.group(1) if cdata_m else self.raw

        self._extract(xaml)
        self._extract_steps(xaml)
        return self

    def summary(self):
        return {
            'report_name':    self.report_name,
            'emails':         sorted(self.emails),
            'passwords':      sorted(self.passwords),
            'servers':        sorted(self.servers),
            'oracle_schemas': sorted(self.oracle_schemas),
            'usernames':      sorted(self.usernames),
            'dsns':           sorted(self.dsns),
            'unc_paths':      sorted(self.unc_paths, key=len, reverse=True),  # longest first
            'smtp_servers':   sorted(self.smtp_servers),
            'schemas':        sorted(self.schemas),
            'tables':         sorted(self.tables),
            'pipeline_steps': self.pipeline_steps,
        }

    # ------------------------------------------------------------------
    # Private -- extraction
    # ------------------------------------------------------------------

    def _extract(self, text):
        # Emails (covers To/From/Cc/Bcc attributes and UserName in auth strings)
        for email in EMAIL_RE.findall(text):
            self.emails.add(email.lower())

        # Auth UserName -- if it's an email it's already caught above,
        # otherwise treat as service account
        for uname in AUTH_USER_RE.findall(text):
            if '@' in uname:
                self.emails.add(uname.lower())
            else:
                self.usernames.add(uname)

        # Passwords
        for pwd in PASSWORD_RE.findall(text):
            clean = pwd.strip()
            if clean and clean != '***REDACTED***':
                self.passwords.add(clean)

        # Oracle connections: oracle://SCHEMA@SERVER
        for schema, server in ORACLE_TRL_RE.findall(text):
            self.oracle_schemas.add(schema)
            self.servers.add(server)

        # ODBC/Redshift: odbc://account@DSN
        for account, dsn in ODBC_TRL_RE.findall(text):
            dsn_clean = dsn.replace('+', ' ').strip('/')
            if '@' not in account:
                self.usernames.add(account)
            self.dsns.add(dsn_clean)

        # UNC file paths -- extract from dedicated file attributes first,
        # then fall back to raw UNC scan
        for path in FILE_ATTR_RE.findall(text):
            self.unc_paths.add(path.rstrip('\\'))
        for path in UNC_PATH_RE.findall(text):
            clean = path.rstrip('\\"').rstrip('\\')
            self.unc_paths.add(clean)

        # SMTP servers
        for smtp in SMTP_RE.findall(text):
            self.smtp_servers.add(smtp)

        # SQL schemas and tables (decode entities first)
        sql_text = _decode_entities(text)
        for schema, table in FROM_RE.findall(sql_text):
            self.schemas.add(schema)
            self.tables.add(f'{schema}.{table}')
        for schema, table in JOIN_RE.findall(sql_text):
            self.schemas.add(schema)
            self.tables.add(f'{schema}.{table}')

    def _extract_steps(self, text):
        for tag, name in ACTIVITY_RE.findall(text):
            self.pipeline_steps.append({
                'name': name,
                'type': tag.split(':')[1],
            })

    # ------------------------------------------------------------------
    # File reading -- handles UTF-16 and UTF-8 Toad files
    # ------------------------------------------------------------------

    def _read(self):
        for enc in ('utf-16', 'utf-8-sig', 'utf-8', 'latin-1'):
            try:
                with open(self.file_path, encoding=enc) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise IOError(f'Cannot decode {self.file_path}')
