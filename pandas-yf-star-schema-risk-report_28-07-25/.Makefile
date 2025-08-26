# --- Load .env into shell ----
export $(shell grep -v '^#' .env | xargs)

.PHONY: db-init etl plot lint

db-init:
	psql -h $(DB_HOST) -U $(DB_USER) -d $(DB_NAME) -f sql/001_init_star_schema.sql

etl:
	python -m src.risk_metrics_etl

plot:
	python -m src.plot_risk_metrics

lint:
	ruff src && mypy src
