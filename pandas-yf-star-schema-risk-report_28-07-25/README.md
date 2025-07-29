```markdown
# Pandas-YF Star-Schema Risk Report

**Date:** 2025-07-28

A simple ETL + analytics pipeline that:

1. Downloads one year of **adjusted-close** prices from Yahoo! Finance.
2. Calculates annualized Sharpe & Sortino ratios.
3. Stores results in a PostgreSQL **star schema**.
4. Generates a quick bar-chart comparison of risk-adjusted returns.

---

## 📁 Project Structure

```text
pandas-yf-star-schema-risk-report_28-07-25/
├─ src/
│  ├─ risk_metrics_etl.py      # ETL: fetch, compute, load
│  └─ plot_risk_metrics.py     # Reporting: bar-chart plot
├─ sql/
│  └─ 001_init_star_schema.sql # Star schema DDL
├─ notebooks/                  # Ad-hoc exploration
├─ .env.example                # Template for environment vars
└─ requirements.txt            # Python dependencies
```

---

## ⚙️ Prerequisites

- Docker Desktop (or PostgreSQL 15+ installed locally)  
- Python 3.9+

---

## 🔧 Setup

1. **Clone repo**  
   ```bash
   git clone <repo-url>
   cd pandas-yf-star-schema-risk-report_28-07-25
   ```

2. **Environment variables**  
   Copy and edit `.env` (never commit secrets):
   ```bash
   cp .env.example .env
   ```
   | Variable   | Example     | Description             |
   | ---------- | ----------- | ----------------------- |
   | `DB_USER`  | `postgres`  | PostgreSQL user         |
   | `DB_PASS`  | `pass`      | PostgreSQL password     |
   | `DB_HOST`  | `localhost` | Host or container name  |
   | `DB_PORT`  | `5432`      | Port                    |
   | `DB_NAME`  | `finance`   | Database name           |

3. **Start PostgreSQL**  
   ```bash
   docker run --name finance_pg \
     -e POSTGRES_PASSWORD=$DB_PASS \
     -p $DB_PORT:5432 \
     -d postgres:latest
   ```

4. **Create and activate virtual environment**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .venv\Scripts\activate       # Windows
   pip install -r requirements.txt
   ```

---

## 🗄️ Initialize Database

Run the DDL script to create your star schema:

```bash
make db-init
# which runs:
#   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f sql/001_init_star_schema.sql
```

**Schema**:

```sql
-- tickers dimension
CREATE TABLE IF NOT EXISTS tickers (
  ticker       TEXT PRIMARY KEY,
  company_name TEXT
);

-- risk_metrics fact
CREATE TABLE IF NOT EXISTS risk_metrics (
  ticker        TEXT REFERENCES tickers(ticker),
  sharpe_ratio  DOUBLE PRECISION,
  sortino_ratio DOUBLE PRECISION
);
```

---

## 🔄 Daily Workflow

1. **Refresh data & metrics**  
   ```bash
   make etl
   # Equivalent to: python -m src.risk_metrics_etl
   ```

2. **Generate report**  
   ```bash
   make plot
   # Equivalent to: python -m src.plot_risk_metrics
   ```

3. **(Optional) Lint & type-check**  
   ```bash
   make lint
   # Runs ruff + mypy
   ```

> You can schedule `make etl` daily via cron, Task Scheduler, or GitHub Actions.

---

## 🛠️ Commands Reference

| Command         | Description                                    |
| --------------- | ---------------------------------------------- |
| `make db-init`  | Apply SQL schema to Postgres                  |
| `make etl`      | Run ETL pipeline (fetch → compute → load)      |
| `make plot`     | Generate bar-chart of Sharpe & Sortino ratios  |
| `make lint`     | Run code quality checks (ruff & mypy)          |

---

## Contributing

PRs are welcome! Please:

1. Fork the repo.  
2. Run `make lint && make etl` and ensure all checks pass.  
3. Open a pull request with a clear description.

---

## License

[MIT License](LICENSE)
```

**How to copy without messing up formatting:**

- **Use the “Copy code” button**: Hover over the code block and click the clipboard icon at top-right to copy the entire fenced block.
- **Paste into a plain-text or Markdown editor** (e.g., VS Code, Sublime, Atom). Avoid pasting into rich-text editors like Word.
- **Ensure the file extension is `.md`** so your editor highlights Markdown syntax correctly.
- **If using GitHub’s web UI**, click “Raw” on the file view and then copy all contents directly.
- **Verify indentation** and fence markers (` ```markdown ` and ` ``` `) are intact after pasting.