import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas
import numpy
from sample.helpers import np_growth, moving_average_nan, zscore_nan

def test_pipeline_end_to_end():
    # Simulated mini dataset
    data = pandas.DataFrame({
        "Country Name": ["Testland"] * 3,
        "Year": ["2020", "2021", "2022"],
        "Value": [100.0, 120.0, 144.0],
    })

    # Pipeline steps
    data["Value"] = pandas.to_numeric(data["Value"], errors="coerce")
    data["Year"] = pandas.to_datetime(data["Year"], format="%Y", errors="coerce")
    data = data.sort_values(["Country Name", "Year"]).set_index(["Country Name", "Year"])
    data = data.groupby(level=0).resample("YE", level=1).ffill()
    
    # Apply transformations
    data["GDP Growth (%)"] = data.groupby(level=0)["Value"].transform(np_growth)
    data["z"] = data.groupby(level=0)["GDP Growth (%)"].transform(zscore_nan)
    data["Smoothed"] = data.groupby(level=0)["GDP Growth (%)"].transform(
        lambda s: moving_average_nan(s, window=3)
    )

    # Assertions
    assert "GDP Growth (%)" in data.columns
    assert "z" in data.columns
    assert "Smoothed" in data.columns
    assert not data["GDP Growth (%)"].isna().all()
    assert not data["z"].isna().all()
    assert numpy.isclose(data.loc[("Testland", "2021-12-31"), "GDP Growth (%)"], 20.0)
