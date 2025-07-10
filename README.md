```markdown
# 🦆 Batch-ETL Starter

> **CSV → Parquet → DuckDB** — a tiny yet production-style pipeline you can clone, run, and extend in minutes.  
> Built for **Python 3.12**, **pandas 2.2**, and **DuckDB 0.10**.

[![CI](https://github.com/<org>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<org>/<repo>/actions/workflows/ci.yml)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents
1. [Why this repo exists](#why-this-repo-exists)  
2. [Quick Start](#quick-start)  
3. [Project Structure](#project-structure)  
4. [Installation](#installation)  
5. [CLI Reference](#cli-reference)  
6. [Testing](#testing)  
7. [Development Tooling](#development-tooling)  
8. [CI Workflow](#ci-workflow)  
9. [Docker Image (optional)](#docker-image-optional)  
10. [Configuration & Patterns](#configuration--patterns)  
11. [Contributing](#contributing)  
12. [License](#license)  

---

## Why this repo exists
* **Focus on first principles** — one conversion (CSV → Parquet) and one load step (Parquet → DuckDB) cover ≈ 90 % of classic batch-ETL without cloud overhead.  
* **Pure-Python stack** — no JVM or external services; everything runs in \< 1 s on a laptop.  
* **Launchpad for learning** — Week 1 of a 26-week data-engineering journey (see `docs/roadmap.md`).  
* **Opinionated, not rigid** — Black + Ruff, type hints, and pre-commit hooks keep code healthy while the repo stays small enough to hack freely. ✔️  

---

## Quick Start
````bash
# Clone & enter repo
git clone https://github.com/<you>/batch-etl-starter.git
cd batch-etl-starter

# 1️⃣  Install dependencies (Poetry)
poetry install --all-extras

# 2️⃣  Run the pipeline on the sample dataset
poetry run python -m etl.cli run data/raw/orders.csv

# 3️⃣  Inspect the result
duckdb
> .open data/duckdb/batch.db
> SELECT COUNT(*) FROM batch_stage;
````

---

## Project Structure
````text
.
├── data/
│   ├── raw/            # 💾 sample CSVs checked into Git
│   ├── staging/        # ⚙️  auto-generated Parquet files
│   └── duckdb/         # 🦆 DuckDB database(s)
├── etl/
│   ├── __init__.py
│   ├── io.py           # csv_to_parquet + parquet_to_duck
│   └── cli.py          # Typer-powered command line
├── tests/
│   └── test_io.py      # pytest unit tests
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml      # Poetry config + dependency lock
├── Makefile            # convenience aliases
└── README.md
````

---

## Installation
| Environment              | Command                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------ |
| **Poetry** (recommended) | `poetry install --all-extras`                                                                                |
| **pip + venv**           | `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`                       |
| **Conda**                | `conda env create -f environment.yml && conda activate batch-etl`                                            |

---

## CLI Reference
````text
Usage: python -m etl.cli run [OPTIONS] SRC

Arguments:
  SRC  Path to a CSV file.  [required]

Options:
  --db     TEXT  DuckDB file (written if missing)  [default: data/duckdb/batch.db]
  --table  TEXT  Destination table name            [default: batch_stage]
  --help         Show this message and exit.
````

Internally:

````python
pq = csv_to_parquet(src, src.parent / "staging")  # converts & stores alongside raw file
parquet_to_duck(db, pq, table)                    # single COPY … TO for near-zero-copy load
````

---

## Testing
````bash
pytest -q   # runs in <0.5 s
````

DuckDB runs entirely in-process, so no external services are required.

---

## Development Tooling
| Tool           | Purpose              | How to run                                   |
| -------------- | -------------------- | -------------------------------------------- |
| **Black 24.4** | Auto-formatting      | `make lint-format` or commit hook            |
| **Ruff 0.4**   | Lint + import-sort   | `make lint`                                  |
| **pre-commit** | Git hooks            | `pre-commit install`                         |
| **Make**       | Task runner          | `make test`, `make run SRC=…`                |

---

## CI Workflow
````yaml
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: 3.12
      - run: pip install poetry
      - run: poetry install --with dev
      - run: poetry run pytest -q
````

---

## Docker Image (optional)
````dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-dev
ENTRYPOINT ["poetry", "run", "python", "-m", "etl.cli"]
````
````bash
docker build -t batch-etl .
docker run -v $(pwd)/data:/app/data batch-etl data/raw/orders.csv
````

---

## Configuration & Patterns
| Aspect        | Default                    | How to override                           |
| ------------- | -------------------------- | ----------------------------------------- |
| DuckDB path   | `data/duckdb/batch.db`     | `--db` flag or `BATCH_DB` env var         |
| Table name    | `batch_stage`              | `--table` flag                            |
| Staging dir   | `data/staging`             | edit `etl/io.py::csv_to_parquet`          |
| Logging level | `INFO`                     | `LOG_LEVEL` env var                       |

*Design note 💡*: we use DuckDB’s `COPY (SELECT * FROM read_parquet(...)) TO …` then `CREATE OR REPLACE TABLE` — heavy lifting stays in C++ for maximum throughput.

---

## Contributing
1. **Fork** → create a feature branch (`feat/*` or `fix/*`).  
2. Ensure `make lint test` passes.  
3. Open a **PR** — the CI workflow above will run automatically. 🤝  

---

## License
[MIT](LICENSE) © 2025 Your Name
```
