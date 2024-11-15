"""Result reporters for nullzone-test."""

from typing import List
from rich.console import Console
from rich.table import Table

from .scanner import TableResult, ColumnResult


class ConsoleReporter:
    """Pretty-print results to terminal."""

    def __init__(self, threshold: float = 0.0):
        self.threshold = threshold
        self.console = Console()

    def report(self, results: List[TableResult]) -> int:
        """Print results and return violation count."""
        total_violations = 0

        self.console.print(f"\nnullzone v0.4.2 — scanning {len(results)} table(s)\n")

        for table_result in results:
            fqn = f"{table_result.database}.{table_result.schema}.{table_result.table_name}"
            self.console.print(f"[bold]{table_result.table_name}[/bold]")

            for col in table_result.columns:
                pct = col.null_percentage
                is_violation = pct > self.threshold

                if is_violation:
                    total_violations += 1
                    icon = "✗"
                    style = "red"
                else:
                    icon = "✓"
                    style = "green"

                jk = " [dim](join key)[/dim]" if col.is_join_key else ""
                self.console.print(
                    f"  [{style}]{icon}[/{style}] {col.column_name:<20} — "
                    f"{col.null_count:,} nulls / {col.total_rows:,} rows ({pct:.3f}%){jk}"
                )

            self.console.print()

        summary_style = "red" if total_violations > 0 else "green"
        self.console.print(
            f"[{summary_style}]Summary: {total_violations} violation(s) found "
            f"across {len(results)} table(s)[/{summary_style}]"
        )

        return total_violations


class JUnitReporter:
    """Output results as JUnit XML for CI integration."""

    def __init__(self, output_path: str = "nullzone-results.xml"):
        self.output_path = output_path

    def report(self, results: List[TableResult]) -> int:
        """Write JUnit XML and return violation count."""
        from junitparser import JUnitXml, TestSuite, TestCase, Failure

        xml = JUnitXml()
        total_violations = 0

        for table_result in results:
            suite = TestSuite(
                f"{table_result.database}.{table_result.schema}.{table_result.table_name}"
            )

            for col in table_result.columns:
                tc = TestCase(f"null_check_{col.column_name}")
                tc.time = 0

                if col.null_count > 0:
                    total_violations += 1
                    tc.result = [Failure(
                        message=f"{col.null_count} nulls found ({col.null_percentage:.3f}%)",
                        type="NullViolation"
                    )]

                suite.add_testcase(tc)

            xml.add_testsuite(suite)

        xml.write(self.output_path)
        return total_violations
