Batch‑ETL Starter 🚀

Lightweight CLI that ingests raw CSV files, converts them to columnar Parquet, and loads the result into DuckDB for instant analytics.

Quick Start

# 1. Install dependencies
poetry install --all-extras  # or: pip install -r requirements.txt

# 2. Run the pipeline
python -m etl.cli run data/raw/sample.csv

# 3. Query the warehouse
duckdb data/duckdb/batch.db \
  "SELECT * FROM batch_stage LIMIT 10;"

Project Structure

.
├── data/
│   ├── raw/          # source CSVs
│   └── staging/      # generated Parquet files
├── etl/              # importable Python package
│   ├── io.py         # csv↔parquet↔duckdb helpers
│   └── cli.py        # Typer CLI entrypoint
├── tests/            # pytest unit tests
└── pyproject.toml    # pinned runtime + dev deps

Development Workflow

Task

Command

Format & Lint

pre-commit run --all-files

Unit Tests

pytest -q

CLI Help

python -m etl.cli --help

Continuous Integration (GitHub Actions) runs lint and tests on every push.

Requirements

Tool

Version

Python

3.12

Pandas

2.2

DuckDB

0.10

License

MIT © 2025 

