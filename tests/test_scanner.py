"""Tests for null scanner."""

import pytest
from unittest.mock import MagicMock, patch
from nullzone.scanner import NullScanner, ColumnResult, TableResult


class TestColumnResult:
    def test_null_percentage_zero(self):
        col = ColumnResult("test_col", 0, 1000)
        assert col.null_percentage == 0.0

    def test_null_percentage_some(self):
        col = ColumnResult("test_col", 50, 1000)
        assert col.null_percentage == 5.0

    def test_null_percentage_empty_table(self):
        col = ColumnResult("test_col", 0, 0)
        assert col.null_percentage == 0.0

    def test_is_join_key(self):
        col = ColumnResult("id", 0, 100, is_join_key=True)
        assert col.is_join_key


class TestTableResult:
    def test_violations_empty(self):
        result = TableResult("DB", "SCHEMA", "TABLE", [
            ColumnResult("col1", 0, 100),
            ColumnResult("col2", 0, 100),
        ])
        assert len(result.violations) == 0

    def test_violations_present(self):
        result = TableResult("DB", "SCHEMA", "TABLE", [
            ColumnResult("col1", 0, 100),
            ColumnResult("col2", 5, 100),
            ColumnResult("col3", 10, 100),
        ])
        assert len(result.violations) == 2


class TestNullScanner:
    @patch("nullzone.scanner.snowflake.connector.connect")
    def test_scan_table(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1000, 0, 47, 0)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        scanner = NullScanner("test_conn")
        result = scanner._scan_table("DB", "SCHEMA", {
            "name": "ORDERS",
            "required_columns": ["ORDER_ID", "ORDER_DATE", "AMOUNT"],
        })

        assert result.table_name == "ORDERS"
        assert len(result.columns) == 3
        assert result.columns[1].null_count == 47
