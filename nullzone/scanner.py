"""Core scanning engine for null detection."""

import snowflake.connector
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ColumnResult:
    column_name: str
    null_count: int
    total_rows: int
    is_join_key: bool = False

    @property
    def null_percentage(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return (self.null_count / self.total_rows) * 100


@dataclass
class TableResult:
    database: str
    schema: str
    table_name: str
    columns: List[ColumnResult]

    @property
    def violations(self) -> List[ColumnResult]:
        return [c for c in self.columns if c.null_count > 0]


class NullScanner:
    """Scans Snowflake tables for null values in declared non-null columns."""

    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        self._conn: Optional[snowflake.connector.SnowflakeConnection] = None

    def _get_connection(self) -> snowflake.connector.SnowflakeConnection:
        if self._conn is None or self._conn.is_closed():
            self._conn = snowflake.connector.connect(
                connection_name=self.connection_name
            )
        return self._conn

    def scan_targets(self, targets: List[Dict]) -> List[TableResult]:
        """Scan all configured targets and return results."""
        results = []
        for target in targets:
            db = target["database"]
            schema = target["schema"]
            for table_cfg in target.get("tables", []):
                result = self._scan_table(db, schema, table_cfg)
                results.append(result)
        return results

    def _scan_table(self, database: str, schema: str, table_cfg: Dict) -> TableResult:
        """Scan a single table for null violations."""
        table_name = table_cfg["name"]
        required_columns = table_cfg.get("required_columns", [])
        join_keys = set(table_cfg.get("join_keys", []))
        fqn = f"{database}.{schema}.{table_name}"

        conn = self._get_connection()
        cursor = conn.cursor()

        # Build count query for all required columns
        count_exprs = [f"COUNT(*) AS total_rows"]
        for col in required_columns:
            count_exprs.append(
                f"SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS null_{col.lower()}"
            )

        query = f"SELECT {', '.join(count_exprs)} FROM {fqn}"

        try:
            cursor.execute(query)
            row = cursor.fetchone()
        finally:
            cursor.close()

        total_rows = row[0] if row else 0
        columns = []
        for i, col in enumerate(required_columns):
            null_count = row[i + 1] if row else 0
            columns.append(ColumnResult(
                column_name=col,
                null_count=null_count,
                total_rows=total_rows,
                is_join_key=col in join_keys,
            ))

        return TableResult(
            database=database,
            schema=schema,
            table_name=table_name,
            columns=columns,
        )

    def close(self):
        if self._conn and not self._conn.is_closed():
            self._conn.close()
