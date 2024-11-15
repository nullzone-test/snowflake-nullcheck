# Contributing to snowflake-nullcheck

## Development Setup

```bash
git clone https://github.com/snowflake-labs/snowflake-nullcheck.git
cd snowflake-nullcheck
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

- We use `black` for formatting and `ruff` for linting
- Type hints are encouraged
- Docstrings for all public methods

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a PR with a clear description

## Reporting Issues

Please include:
- snowflake-nullcheck version (`nullcheck --version`)
- Python version
- Snowflake connector version
- Full error output / stack trace
- Config file (redact connection details)
