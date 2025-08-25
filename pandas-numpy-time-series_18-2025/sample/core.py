# app.py
import numpy as np
import pandas as pd
from pathlib import Path

import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go

# ----------------------------
# Config
# ----------------------------
CSV_PATH = Path("long_preview.csv")  # adjust if needed
VALUE_COL = "Value"
COUNTRY_COL = "Country Name"
YEAR_COL = "Year"

# ----------------------------
# Helpers (NumPy-based)
# ----------------------------
def np_growth(values: pd.Series) -> np.ndarray:
    arr = values.to_numpy(dtype=float)
    out = np.empty_like(arr, dtype=float)
    out[:] = np.nan
    prev = arr[:-1]
    curr = arr[1:]
    with np.errstate(invalid="ignore", divide="ignore"):
        res = (curr - prev) / prev * 100.0
    res[np.isclose(prev, 0.0)] = np.nan
    out[1:] = res
    return out

def moving_average_nan(series: pd.Series, window: int = 3) -> np.ndarray:
    x = series.to_numpy(dtype=float)
    mask = ~np.isnan(x)
    x_filled = np.where(mask, x, 0.0)
    k = np.ones(window, dtype=float)

    num = np.convolve(x_filled, k, mode="same")
    den = np.convolve(mask.astype(float), k, mode="same")
    ma = np.divide(num, den, out=np.full_like(num, np.nan), where=den > 0)
    return ma

def zscore_nan(series: pd.Series) -> np.ndarray:
    x = series.to_numpy(dtype=float)
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or np.isclose(sd, 0.0):
        return np.full_like(x, np.nan)
    return (x - mu) / sd

# ----------------------------
# Load & preprocess once
# ----------------------------
df = pd.read_csv(CSV_PATH)

# Keep necessary cols and clean
df = df[[COUNTRY_COL, YEAR_COL, VALUE_COL]].dropna(subset=[VALUE_COL])
df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce")
df = df.dropna(subset=[VALUE_COL])
df[YEAR_COL] = pd.to_datetime(df[YEAR_COL], format="%Y", errors="coerce")
df = df.dropna(subset=[YEAR_COL])

df = df.sort_values([COUNTRY_COL, YEAR_COL]).set_index([COUNTRY_COL, YEAR_COL])

# Make annual and fill forward within each country (safe even if already annual)
df = df.groupby(level=0).resample("Y", level=1).ffill()

# Precompute raw GDP growth (%)
df["GDP Growth (%)"] = df.groupby(level=0)[VALUE_COL].transform(np_growth)

# Precompute per-country z-scores on raw growth (used for outliers)
df["z"] = df.groupby(level=0)["GDP Growth (%)"].transform(zscore_nan)

# For the UI
countries = sorted(df.index.get_level_values(0).unique().tolist())
year_min = int(df.index.get_level_values(1).min().year)
year_max = int(df.index.get_level_values(1).max().year)

# ----------------------------
# Dash app
# ----------------------------
app = Dash(__name__)
app.title = "GDP Growth Dashboard"

app.layout = html.Div([
    html.H2("GDP Growth Trends (World Bank)"),
    html.Div([
        html.Label("Countries"),
        dcc.Dropdown(
            options=[{"label": c, "value": c} for c in countries],
            value=countries[:5],    # initial selection
            multi=True,
            id="country-dropdown",
            placeholder="Select one or more countries…"
        ),
    ], style={"maxWidth": 800}),

    html.Div([
        html.Div([
            html.Label("Year range"),
            dcc.RangeSlider(
                min=year_min, max=year_max, step=1, allowCross=False,
                value=[max(year_min, year_max-30), year_max],
                marks={y: str(y) if (y - year_min) % 5 == 0 else "" for y in range(year_min, year_max+1)},
                id="year-range"
            ),
        ], style={"flex": 2, "marginRight": "16px"}),

        html.Div([
            html.Label("Smoothing window (years)"),
            dcc.Slider(min=1, max=9, step=2, value=3, marks={i: str(i) for i in range(1, 10, 2)}, id="smooth-window"),
            dcc.Checklist(options=[{"label": " Show Smoothed", "value": "smooth"}],
                          value=["smooth"], id="smooth-toggle", style={"marginTop": "6px"})
        ], style={"flex": 1, "marginRight": "16px"}),

        html.Div([
            html.Label("Outliers"),
            dcc.Checklist(options=[{"label": " Highlight z>|2.5|", "value": "outliers"}],
                          value=[], id="outlier-toggle"),
            html.Div("Tip: double‑click a legend item to isolate a country.", style={"fontSize": 12, "marginTop": 8})
        ], style={"flex": 1}),
    ], style={"display": "flex", "marginTop": "12px"}),

    dcc.Loading(dcc.Graph(id="growth-graph", style={"height": "70vh"}), type="default")
], style={"padding": "18px"})

# ----------------------------
# Callbacks
# ----------------------------
@app.callback(
    Output("growth-graph", "figure"),
    Input("country-dropdown", "value"),
    Input("year-range", "value"),
    Input("smooth-window", "value"),
    Input("smooth-toggle", "value"),
    Input("outlier-toggle", "value"),
)
def update_chart(selected_countries, year_range, window, smooth_toggle, outlier_toggle):
    if not selected_countries:
        selected_countries = []

    y0, y1 = year_range
    # Filter once
    mask = (
        df.index.get_level_values(0).isin(selected_countries) &
        (df.index.get_level_values(1).year >= y0) &
        (df.index.get_level_values(1).year <= y1)
    )
    sub = df.loc[mask].copy()
    if sub.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data for the current selection",
            xaxis_title="Year", yaxis_title="GDP Growth (%)"
        )
        return fig

    # Compute (or recompute) smoothed growth with chosen window
    show_smoothed = "smooth" in (smooth_toggle or [])
    if show_smoothed:
        sub["Smoothed Growth (%)"] = (
            sub.groupby(level=0)["GDP Growth (%)"].transform(lambda s: moving_average_nan(s, window))
        )

    # Build figure
    fig = go.Figure()

    # Lines: either raw or smoothed
    y_col = "Smoothed Growth (%)" if show_smoothed else "GDP Growth (%)"

    for c in selected_countries:
        cs = sub.xs(c, level=0, drop_level=False)
        fig.add_trace(go.Scatter(
            x=cs.index.get_level_values(1),
            y=cs[y_col],
            mode="lines",
            name=c + (" (smoothed)" if show_smoothed else ""),
            hovertemplate=f"Country: {c}<br>Year: %{x|%Y}<br>{y_col}: %{y:.2f}%<extra></extra>"
        ))

        # Outlier markers (always based on RAW growth z-score)
        if "outliers" in (outlier_toggle or []):
            out = cs[cs["z"].abs() > 2.5]
            if not out.empty:
                fig.add_trace(go.Scatter(
                    x=out.index.get_level_values(1),
                    y=out["GDP Growth (%)"],
                    mode="markers",
                    name=f"{c} outliers",
                    marker=dict(size=8, symbol="x"),
                    hovertemplate=f"Country: {c}<br>Year: %{x|%Y}<br>Raw Growth: %{y:.2f}%<br>z: %{customdata:.2f}<extra></extra>",
                    customdata=out["z"],
                    showlegend=False
                ))

    fig.update_layout(
        title=f"GDP Growth ({'Smoothed' if show_smoothed else 'Raw'}) — {y0}–{y1}",
        xaxis_title="Year",
        yaxis_title="GDP Growth (%)",
        hovermode="x unified",
        legend_title="Countries",
        margin=dict(l=40, r=20, t=60, b=40),
        height=720,
    )
    return fig

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
