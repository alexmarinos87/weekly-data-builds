# Week 2 – dbt Basics

## 🧠 Problem
Operational data is too raw for analytics. We need to transform it into a clean, queryable schema.

## 🎯 Goal
Use dbt to model raw `orders` and `customers` into a star schema (`dim_customers`, `fct_orders`), with tests and documentation.

## 🔍 Scope
- Seed CSVs: `orders.csv`, `customers.csv`
- Staging models: `stg_orders`, `stg_customers`
- Marts: `fct_orders`, `dim_customers`
- Tests: `not_null`, `unique`, `relationships`
- Docs: generate with `dbt docs`

## ✅ Success Criteria
- All models run with `dbt run`
- Tests pass with `dbt test`
- Lineage graph shows `ref()` chain
- Docs served via `dbt docs serve`
- Coverage >90%, all models documented

## 👩‍💻 Assumptions
- Local Postgres + `~/.dbt/profiles.yml` available
- Using dbt v1.8+, Python 3.12

## 📅 Timeline
| Day     | Task                       |
|-------- |---------------------------|
| Monday  | Write this brief           |
| Tuesday | Scaffold + seed CSVs       |
| Wed     | Build core models          |
| Thursday| Add docs + test polish     |
| Friday  | Record demo, screenshot    |
| Weekend | Tag, retro, share post     |
