# Road‑Map: Weekly GitHub Projects for Aspiring Data Engineers

*Version 1.0 – July 2025*

---

## How to Use This Plan

1. **Create a private or public GitHub *organisation* named `weekly-data-builds`** (or similar).
2. **Fork the included *Template Repository*** (`de‑template`) containing:

   * `.github/workflows/ci.yml` – runs `black`, `ruff`, `pytest`, and uploads coverage.
   * `tasks.py` – invoke tasks: `clean`, `test`, `lint`, `run`.
   * `README_TEMPLATE.md`, `LICENSE`, `.gitignore`, `CODE_OF_CONDUCT.md`.
3. **Each Monday** click *Use this template* → name the repo `YYYY‑WW_<slug>` (e.g. `2025‑29_batch‑etl`).
4. Follow the sprint checklist (p. 4). Merge to *main* by Sunday night and tag `v0.1.0`.
5. After every four projects, record a 3‑min demo video and pin it to LinkedIn / your portfolio site.

---

## Weekly Sprint Checklist (applies to every project)

| When                  | Deliverable            | Details                                                         |
| --------------------- | ---------------------- | --------------------------------------------------------------- |
| **Mon  (1 h)**        | *Idea & Problem Brief* | Fill out `docs/one‑pager.md`: problem, scope, success criteria. |
| **Tue (15 m)**        | *Repo Scaffold*        | Initialise from template, push first commit.                    |
| **Tue – Wed (2‑3 h)** | *Core Build*           | Write minimal working pipeline + unit tests.                    |
| **Thu (1 h)**         | *Polish*               | Add logging, type hints, proper error handling.                 |
| **Fri (1 h)**         | *Docs & Demo*          | Update README, record asciinema / GIF, push schema diagram.     |
| **Sat (20 m)**        | *Review & Tag*         | Self‑review PR → squash & merge → `git tag -a v0.1.0`.          |
| **Sun (10 m)**        | *Retro & Share*        | Log takeaway in `CHANGELOG.md`, share link on social.           |

---

## 26‑Week Project Calendar

| Week | Theme & Repository                        | Core Tech                  | Learning Outcome                                    |
| ---- | ----------------------------------------- | -------------------------- | --------------------------------------------------- |
| 1    | **Batch‑ETL Starter** `YYYY‑WW_batch‑etl` | Python, Pandas, DuckDB     | CLI loads CSV → Parquet → DuckDB; introduce `COPY`. |
| 2    | **dbt Basics**                            | dbt 1.8, Postgres          | Star‑schema modelling, tests, docs site.            |
| 3    | **Airflow 101**                           | Airflow 2.9                | DAG to orchestrate Weeks 1‑2 pipeline.              |
| 4    | **Data Quality**                          | Great Expectations         | Create expectations, integrate with Airflow.        |
| 5    | **Incremental Loads**                     | Postgres partitions        | Upsert pattern (`INSERT … ON CONFLICT`).            |
| 6    | **Dashboard**                             | Metabase / Superset        | Connect to warehouse, build KPI board.              |
| 7    | **Change‑Data‑Capture**                   | Debezium, Kafka            | Stream Postgres updates to topic.                   |
| 8    | **Stream Processing**                     | Kafka Streams / Flink SQL  | Aggregate CDC stream to rolling metrics.            |
| 9    | **Low‑Latency OLAP**                      | ClickHouse                 | Consume topic, query latency < 5 s.                 |
| 10   | **Lineage & Metadata**                    | OpenLineage + Marquez      | Track job lineage and surface in UI.                |
| 11   | **Lakehouse Table Format**                | Apache Iceberg             | Write partition evolution demo.                     |
| 12   | **Orchestrated Lakehouse**                | Spark Structured Streaming | Stream into Iceberg, query via Trino.               |
| 13   | **Vector DB Basics**                      | pgvector                   | Store & query embeddings; similarity search API.    |
| 14   | **RAG Service**                           | FastAPI + LangChain        | Chat endpoint using Week 13 embeddings.             |
| 15   | **Feature Store Intro**                   | Feast + Redis              | Offline & online feature parity tests.              |
| 16   | **ML Pipeline**                           | scikit‑learn + mlflow      | Train model on Feast features; register & serve.    |
| 17   | **Observability**                         | Prometheus, Grafana        | Export query latency & DAG metrics, set alerts.     |
| 18   | **Cost Benchmark**                        | Snowflake vs BigQuery      | Load 10 GB and compare cost/perf.                   |
| 19   | **Security & RBAC**                       | Postgres RLS, Vault        | Implement row‑level security and secret rotation.   |
| 20   | **Data Contracts**                        | protobuf / pandera         | Validate schema changes in CI.                      |
| 21   | **Serverless Batch**                      | AWS Lambda + S3            | Micro‑ETL under 60 s cold start.                    |
| 22   | **IaC Foundations**                       | Terraform                  | One‑command deploy of Week 21.                      |
| 23   | **Pulumi Python**                         | Pulumi                     | Re‑implement IaC in Python for comparison.          |
| 24   | **Distributed Testing**                   | pytest‑xdist               | Parallel tests for large datasets.                  |
| 25   | **Scaling Challenge**                     | k6 / Locust                | Load‑test pipeline; produce report.                 |
| 26   | **Capstone Refactor**                     | Pick 3 favourite projects  | Integrate, add end‑to‑end docs, present demo.       |

---

## README Scaffold (quick copy‑paste)

````markdown
# <Project Title>

> One‑sentence summary of what this solves.

## Architecture
![diagram](docs/architecture.png)

## Quick Start
```bash
make up    # spin up Docker services
make load  # run the ETL job
make test  # execute tests + coverage
````

## Configuration

| Variable | Description                | Default        |
| -------- | -------------------------- | -------------- |
| `DB_URL` | Postgres connection string | `postgres://…` |

## Development

Explain branching strategy, pre‑commit hooks, how to run linters.

## License

MIT © Your Name 2025

````

---
## Evaluation Metrics (include in every README)
| Metric | Target |
|--------|--------|
| **Data freshness** | < 5 min lag from source to warehouse |
| **Pipeline success rate** | ≥ 99 % last 30 days |
| **Test coverage** | ≥ 85 % lines |
| **Cost per 1 GB processed** | Benchmark and record |

---
## Recommended Tool Versions (as of July 2025)
- Python 3.12
- Postgres 15.5
- dbt 1.8.1
- Apache Airflow 2.9
- Kafka 3.7
- Spark 3.6
- Iceberg 1.5

Update as new stable releases appear.

---
## Further Reading & Resources
1. *Designing Data‑Intensive Applications* – Martin Kleppmann.
2. dbt *Analytics Engineering* Guide.
3. Confluent *Streaming Platform* Training.
4. Lakehouse White Paper – Applecart 2025.
5. Great Expectations v0.18 Docs.

---
### Author
**<Your Name>** – data‑engineering enthusiast.

*Feel free to fork, star, and raise PRs—improvements welcome!*

---
## Example `README.md` for a Weekly Project Repo
Below is a ready‑to‑copy README you can drop into any individual project repository (e.g. `2025‑29_batch‑etl`). It expands the scaffold with concrete sections and badges.

```markdown
# Batch‑ETL Starter 🚀

![CI](https://github.com/<your‑org>/2025‑29_batch‑etl/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

A minimal, production‑style batch pipeline that ingests raw CSV files, converts them to columnar *Parquet*, and loads them into **DuckDB** for instant analytics.

---
## Architecture
```mermaid
graph TD;
    A[Raw CSV on disk] -->|invoke tasks.load| B[Parquet Staging];
    B --> C[DuckDB Warehouse];
    C --> D[Metabase Dashboard];
````

---

## Quick Start

```bash
# 1. Create virtual env & install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the pipeline
make load INPUT=data/raw OUTPUT=data/warehouse

# 3. Query the data
python - <<'PY'
import duckdb, pandas as pd
db = duckdb.connect('data/warehouse/etl.duckdb')
print(db.execute('SELECT COUNT(*) FROM trips').fetchall())
PY
```

---

## Configuration

| Variable    | Description                     | Default          |
| ----------- | ------------------------------- | ---------------- |
| `INPUT`     | Folder containing raw CSV files | `data/raw`       |
| `OUTPUT`    | DuckDB db path / Parquet folder | `data/warehouse` |
| `LOG_LEVEL` | Python logging level            | `INFO`           |

All variables can be set via env vars or passed as `make` arguments.

---

## Project Structure

```
├── data/
│   ├── raw/          # sample CSVs
│   └── warehouse/    # DuckDB & Parquet output
├── etl/
│   ├── loader.py     # file → parquet
│   └── models.py     # DuckDB DDL
├── tests/
│   └── test_etl.py
├── tasks.py          # invoke tasks
└── docker-compose.yml
```

---

## Development

1. **Coding standard** – `black`, `ruff`, `mypy` run in CI and pre‑commit hooks.
2. **Testing** – `pytest -q`; coverage ≥ 90 %.
3. **Branching** – feature branches → PR → squash & merge → tag.

---

## Roadmap

* [ ] Add incremental load mode
* [ ] Integrate Great Expectations tests
* [ ] Switch to S3 staging bucket

Have suggestions? Open an issue or PR!

---

## License

[MIT](LICENSE) © <Your Name> 2025

```

Use this as the default README for each new weekly repo—replace the title, diagram, and quick‑start commands as needed.

```
