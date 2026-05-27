"""
test_unit.py — Unit tests for func-excel-writer (no Azure connection needed).
Tests the Excel template writing logic in isolation using in-memory files.

Usage:
    python test_unit.py
    python -m pytest test_unit.py -v
"""

import csv
import io
import sys
import unittest
from unittest.mock import MagicMock, patch

import openpyxl


# ── Import the functions under test (no Azure env vars needed) ────────────────
sys.path.insert(0, '.')
from function_app import _write_csv_into_template, _find_data_sheet, _history_start, _history_end


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_template_bytes(sheet_name='Data', headers=None, existing_data_rows=0):
    """Create a minimal in-memory xlsm-style workbook as bytes."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    if headers:
        ws.append(headers)
        for i in range(existing_data_rows):
            ws.append([f'old_val_{i}_{j}' for j in range(len(headers))])

    buf = io.BytesIO()
    # Save as xlsx — openpyxl writes identical format; xlsm just has a different extension
    wb.save(buf)
    return buf.getvalue()


def _make_csv_bytes(headers, rows):
    """Create a CSV as bytes (with header row)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue().encode('utf-8')


def _read_sheet_rows(xlsm_bytes, sheet_name='Data'):
    """Open workbook bytes and return all rows as lists of values."""
    wb = openpyxl.load_workbook(io.BytesIO(xlsm_bytes))
    ws = wb[sheet_name]
    return [[cell.value for cell in row] for row in ws.iter_rows()]


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestFindDataSheet(unittest.TestCase):

    def test_finds_sheet_named_Data(self):
        wb = openpyxl.Workbook()
        wb.active.title = 'Cover'
        wb.create_sheet('Data')
        ws = _find_data_sheet(wb)
        self.assertEqual(ws.title, 'Data')

    def test_finds_sheet_named_Sheet1(self):
        wb = openpyxl.Workbook()
        wb.active.title = 'Sheet1'
        ws = _find_data_sheet(wb)
        self.assertEqual(ws.title, 'Sheet1')

    def test_falls_back_to_active_sheet(self):
        wb = openpyxl.Workbook()
        wb.active.title = 'Summary'
        ws = _find_data_sheet(wb)
        self.assertEqual(ws.title, 'Summary')


class TestWriteCsvIntoTemplate(unittest.TestCase):

    HEADERS = ['Network', 'Depot', 'Work Order', 'Gas Prevented', 'Time Difference']
    ROWS = [
        ['NW1', 'DEPOT_A', 'WO-001', '2026-05-19 08:30', '10.5'],
        ['NW1', 'DEPOT_B', 'WO-002', '2026-05-19 09:15', '14.2'],
        ['NW2', 'DEPOT_C', 'WO-003', '2026-05-19 11:00', '8.0'],
    ]

    def test_writes_data_rows_after_header(self):
        tmpl = _make_template_bytes(headers=self.HEADERS)
        csv_b = _make_csv_bytes(self.HEADERS, self.ROWS)

        result = _write_csv_into_template(tmpl, csv_b)

        rows = _read_sheet_rows(result)
        self.assertEqual(len(rows), 4)                          # 1 header + 3 data rows
        self.assertEqual(rows[0], self.HEADERS)                 # header preserved
        self.assertEqual(rows[1][0], 'NW1')                     # first data row correct
        self.assertEqual(rows[3][2], 'WO-003')                  # last data row correct

    def test_clears_old_data_rows_before_writing(self):
        # Template already has 5 old data rows
        tmpl = _make_template_bytes(headers=self.HEADERS, existing_data_rows=5)
        csv_b = _make_csv_bytes(self.HEADERS, self.ROWS)

        result = _write_csv_into_template(tmpl, csv_b)

        rows = _read_sheet_rows(result)
        self.assertEqual(len(rows), 4)                          # old rows replaced, not appended
        self.assertNotIn('old_val_0_0', [r[0] for r in rows])  # no stale data

    def test_handles_empty_csv(self):
        tmpl = _make_template_bytes(headers=self.HEADERS)
        csv_b = _make_csv_bytes(self.HEADERS, [])               # header only, no data

        result = _write_csv_into_template(tmpl, csv_b)

        rows = _read_sheet_rows(result)
        self.assertEqual(len(rows), 1)                          # header row only

    def test_preserves_header_row_from_template(self):
        tmpl = _make_template_bytes(headers=self.HEADERS)
        csv_b = _make_csv_bytes(['ColA', 'ColB'], [['a', 'b']])  # CSV has different header

        result = _write_csv_into_template(tmpl, csv_b)

        rows = _read_sheet_rows(result)
        self.assertEqual(rows[0], self.HEADERS)                 # template header kept, not CSV header

    def test_utf8_bom_csv_handled(self):
        tmpl = _make_template_bytes(headers=['Name', 'Value'])
        # BOM prefix simulates Excel-exported CSV
        csv_b = b'\xef\xbb\xbf' + b'Name,Value\r\nAlpha,1\r\nBeta,2\r\n'

        result = _write_csv_into_template(tmpl, csv_b)

        rows = _read_sheet_rows(result)
        self.assertEqual(len(rows), 3)                          # header + 2 data rows
        self.assertEqual(rows[1][0], 'Alpha')

    def test_returns_bytes(self):
        tmpl = _make_template_bytes(headers=self.HEADERS)
        csv_b = _make_csv_bytes(self.HEADERS, self.ROWS)
        result = _write_csv_into_template(tmpl, csv_b)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)


class TestHistoryStart(unittest.TestCase):
    """_history_start must be non-fatal; must INSERT and return history_id on success."""

    def _make_mock_conn(self, report_id=42, history_id=7):
        """Return a mock connection whose cursor mimics the two SELECT calls."""
        cursor = MagicMock()
        # First fetchone: report_id lookup; second fetchone: SCOPE_IDENTITY
        cursor.fetchone.side_effect = [(report_id,), (history_id,)]
        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: conn
        conn.__exit__ = MagicMock(return_value=False)
        return conn, cursor

    @patch('function_app._pymssql_connect')
    def test_returns_history_id_on_success(self, mock_connect):
        conn, cursor = self._make_mock_conn(report_id=1, history_id=99)
        mock_connect.return_value = conn

        result = _history_start('Daily_BIMIO_267')

        self.assertEqual(result, 99)
        conn.commit.assert_called_once()

    @patch('function_app._pymssql_connect')
    def test_returns_none_when_report_not_found(self, mock_connect):
        cursor = MagicMock()
        cursor.fetchone.return_value = None      # report not in config.report
        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: conn
        conn.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = conn

        result = _history_start('NoSuchReport')

        self.assertIsNone(result)

    @patch('function_app._pymssql_connect')
    def test_returns_none_on_db_error(self, mock_connect):
        mock_connect.side_effect = Exception("connection refused")

        result = _history_start('Daily_BIMIO_267')   # must not raise

        self.assertIsNone(result)


class TestHistoryEnd(unittest.TestCase):
    """_history_end must be non-fatal; must UPDATE when history_id is known."""

    @patch('function_app._pymssql_connect')
    def test_updates_status_to_success(self, mock_connect):
        cursor = MagicMock()
        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: conn
        conn.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = conn

        _history_end(7, 'Success')   # must not raise

        cursor.execute.assert_called_once()
        call_args = cursor.execute.call_args[0]
        self.assertIn('UPDATE', call_args[0])
        self.assertIn('Success', call_args[1])
        conn.commit.assert_called_once()

    @patch('function_app._pymssql_connect')
    def test_updates_status_to_failed(self, mock_connect):
        cursor = MagicMock()
        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = lambda s: conn
        conn.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = conn

        _history_end(7, 'Failed')

        call_args = cursor.execute.call_args[0]
        self.assertIn('Failed', call_args[1])

    def test_noop_when_history_id_is_none(self):
        # No DB call should be made; no exception raised
        _history_end(None, 'Success')   # must not raise or connect

    @patch('function_app._pymssql_connect')
    def test_silently_absorbs_db_error(self, mock_connect):
        mock_connect.side_effect = Exception("network timeout")

        _history_end(99, 'Success')     # must not raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
