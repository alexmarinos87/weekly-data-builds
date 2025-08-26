from pathlib import Path
import duckdb
from etl.io import csv_to_parquet, parquet_to_duck

def test_roundtrip(tmp_path: Path):
    csv = tmp_path / "tiny.csv"
    csv.write_text("a,b\n1,2\n3,4\n")
    pq = csv_to_parquet(csv, tmp_path)
    db = tmp_path / "unit.db"
    parquet_to_duck(db, pq, "tiny")
    assert duckdb.sql("SELECT COUNT(*) FROM tiny").fetchone()[0] == 2
