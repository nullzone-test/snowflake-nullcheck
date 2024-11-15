"""CLI entry point for nullzone-test."""

import click
import yaml
import sys

from .scanner import NullScanner
from .reporter import ConsoleReporter, JUnitReporter


@click.group()
@click.version_option()
def main():
    """nullzone-test — Null value detection for Snowflake."""
    pass


@main.command()
@click.option("--config", "-c", default="nullzone.yaml", help="Config file path")
@click.option("--format", "-f", type=click.Choice(["console", "junit"]), default="console")
@click.option("--output", "-o", default=None, help="Output file (for junit format)")
@click.option("--threshold", "-t", type=float, default=0.0, help="Null % threshold for failure")
@click.option("--connection", default=None, help="Override connection name")
def scan(config, format, output, threshold, connection):
    """Scan tables for null value violations."""
    try:
        with open(config) as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"Error: Config file '{config}' not found.", err=True)
        sys.exit(2)

    conn_name = connection or cfg.get("connection")
    if not conn_name:
        click.echo("Error: No connection specified (use --connection or set in config).", err=True)
        sys.exit(2)

    scanner = NullScanner(conn_name)
    results = scanner.scan_targets(cfg.get("targets", []))

    if format == "console":
        reporter = ConsoleReporter(threshold=threshold)
    else:
        reporter = JUnitReporter(output_path=output or "nullzone-results.xml")

    violations = reporter.report(results)

    if violations > 0:
        sys.exit(1)


@main.command()
@click.option("--config", "-c", default="nullzone.yaml", help="Config file path")
def validate(config):
    """Validate configuration file syntax."""
    try:
        with open(config) as f:
            cfg = yaml.safe_load(f)
        targets = cfg.get("targets", [])
        table_count = sum(len(t.get("tables", [])) for t in targets)
        click.echo(f"✓ Valid config: {len(targets)} target(s), {table_count} table(s)")
    except Exception as e:
        click.echo(f"✗ Invalid config: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
