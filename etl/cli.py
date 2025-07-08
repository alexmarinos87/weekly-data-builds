import typer
from pathlib import Path
from etl.io import csv_to_parquet, parquet_to_duck

app = typer.Typer(help="Batch ETL: CSV ➜ Parquet ➜ DuckDB")

@app.command()
def run(
    src: Path = typer.Argument(..., exists=True, help="CSV file"),
    db: Path = typer.Option("data/duckdb/batch.db", help="DuckDB path"),
    table: str = typer.Option("batch_stage"),
):
    pq = csv_to_parquet(src, src.parent / "staging")
    parquet_to_duck(db, pq, table)
    typer.echo(f"Loaded {src.name} ➜ {table} in {db}")

if __name__ == "__main__":
    app()
