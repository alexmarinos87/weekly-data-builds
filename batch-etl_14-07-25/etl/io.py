import duckdb
import pandas as pd
from pathlib import Path

def csv_to_parquet(src: Path, dest: Path, **read_opts) -> Path:
    df = pd.read_csv(src, **read_opts)
    dest_file = dest / (src.stem + ".parquet")
    df.to_parquet(dest_file, index=False)
    return dest_file

def parquet_to_duck(dest_db: Path, parquet_file: Path, table: str) -> None:
    con = duckdb.connect(dest_db)
    con.execute(f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_parquet('{parquet_file}');")
    con.close()