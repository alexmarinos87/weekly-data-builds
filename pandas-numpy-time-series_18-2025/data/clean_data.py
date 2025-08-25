import pandas
import pathlib
import re
import pyarrow

# Locate the CSV next to this script
csv_path = pathlib.Path(__file__).parent / "raw.csv"

# Load
dataframe = pandas.read_csv(csv_path)

# 1) Pick year columns using regex (YYYY)
year_cols = [c for c in dataframe.columns if re.fullmatch(r"\d{4}", str(c))]

# 2) Identifier columns are everything else
id_cols = [c for c in dataframe.columns if c not in year_cols]

# 3) Reshape (wide → long)
dataframe_long = dataframe.melt(
    id_vars=id_cols,
    value_vars=year_cols,
    var_name="Year",
    value_name="Value"
)

# 4) Tidy types
dataframe_long["Year"] = dataframe_long["Year"].astype(int)
dataframe_long["Value"] = dataframe_long["Value"].astype(float)

print(dataframe_long.head(10))

# Optional: save for fast downstream work (needs `pip install pyarrow` or `fastparquet`)
out_path = pathlib.Path(__file__).parent / "long.parquet"
dataframe_long.to_parquet(out_path, index=False)
print(f"Saved to {out_path}")

dataframe_long.to_csv("data/long_preview.csv", index=False)
