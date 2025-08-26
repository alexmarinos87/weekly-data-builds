# app.py
import numpy
import pandas
from pathlib import Path

import dash
import dash.dcc
import dash.html
import dash.dependencies
import plotly.graph_objects

# ----------------------------
# Config
# ----------------------------
CSV_PATH = Path("data/long_preview.csv")  
VALUE_COL = "Value"
COUNTRY_COL = "Country Name"
YEAR_COL = "Year"

# ----------------------------
# Helpers (NumPy-based)
# ----------------------------
def np_growth(values: pandas.Series) -> numpy.ndarray:
    arr = values.to_numpy(dtype=float)
    out = numpy.empty_like(arr, dtype=float)
    out[:] = numpy.nan
    prev = arr[:-1]
    curr = arr[1:]
    with numpy.errstate(invalid="ignore", divide="ignore"):
        res = (curr - prev) / prev * 100.0
    res[numpy.isclose(prev, 0.0)] = numpy.nan
    out[1:] = res
    return out

def moving_average_nan(series: pandas.Series, window: int = 3) -> numpy.ndarray:
    x = series.to_numpy(dtype=float)
    mask = ~numpy.isnan(x)
    x_filled = numpy.where(mask, x, 0.0)
    k = numpy.ones(window, dtype=float)

    num = numpy.convolve(x_filled, k, mode="same")
    den = numpy.convolve(mask.astype(float), k, mode="same")
    ma = numpy.divide(num, den, out=numpy.full_like(num, numpy.nan), where=den > 0)
    return ma

def zscore_nan(series: pandas.Series) -> numpy.ndarray:
    x = series.to_numpy(dtype=float)
    mu = numpy.nanmean(x)
    sd = numpy.nanstd(x)
    if not numpy.isfinite(sd) or numpy.isclose(sd, 0.0):
        return numpy.full_like(x, numpy.nan)
    return (x - mu) / sd

# ----------------------------
# Load & preprocess once
# ----------------------------
df = pandas.read_csv(CSV_PATH)

# Keep necessary cols and clean
df = df[[COUNTRY_COL, YEAR_COL, VALUE_COL]].dropna(subset=[VALUE_COL])
df[VALUE_COL] = pandas.to_numeric(df[VALUE_COL], errors="coerce")
df = df.dropna(subset=[VALUE_COL])
df[YEAR_COL] = pandas.to_datetime(df[YEAR_COL], format="%Y", errors="coerce")
df = df.dropna(subset=[YEAR_COL])

df = df.sort_values([COUNTRY_COL, YEAR_COL]).set_index([COUNTRY_COL, YEAR_COL])

# Make annual and fill forward within each country (safe even if already annual)
df = df.sort_values([COUNTRY_COL, YEAR_COL]).reset_index()

# Resample with datetime as index, avoid group-level duplication
resampled = []

for country, group in df.groupby(COUNTRY_COL):
    group = group.set_index(YEAR_COL)
    group = group.resample("YE").ffill()
    group[COUNTRY_COL] = country  # Reinsert the country name
    resampled.append(group)

df = pandas.concat(resampled).reset_index()
df = df.set_index([COUNTRY_COL, YEAR_COL])


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
app = dash.Dash(__name__)
app.title = "GDP Growth Dashboard"

app.layout = dash.html.Div([
    dash.html.H2("GDP Growth Trends (World Bank)"),
    dash.html.Div([
        dash.html.Label("Countries"),
        dash.dcc.Dropdown(
            options=[{"label": c, "value": c} for c in countries],
            value=countries[:5],
            multi=True,
            id="country-dropdown",
            placeholder="Select one or more countries…"
        ),
    ], style={"maxWidth": 800}),

    dash.html.Div([
        dash.html.Div([
            dash.html.Label("Year range"),
            dash.dcc.RangeSlider(
                min=year_min, max=year_max, step=1, allowCross=False,
                value=[max(year_min, year_max - 30), year_max],
                marks={y: str(y) if (y - year_min) % 5 == 0 else "" for y in range(year_min, year_max + 1)},
                id="year-range"
            ),
        ], style={"flex": 2, "marginRight": "16px"}),

        dash.html.Div([
            dash.html.Label("Smoothing window (years)"),
            dash.dcc.Slider(min=1, max=9, step=2, value=3, marks={i: str(i) for i in range(1, 10, 2)}, id="smooth-window"),
            dash.dcc.Checklist(options=[{"label": " Show Smoothed", "value": "smooth"}],
                               value=["smooth"], id="smooth-toggle", style={"marginTop": "6px"})
        ], style={"flex": 1, "marginRight": "16px"}),

        dash.html.Div([
            dash.html.Label("Outliers"),
            dash.dcc.Checklist(options=[{"label": " Highlight z>|2.5|", "value": "outliers"}],
                               value=[], id="outlier-toggle"),
            dash.html.Div("Tip: double-click a legend item to isolate a country.", style={"fontSize": 12, "marginTop": 8})
        ], style={"flex": 1}),
    ], style={"display": "flex", "marginTop": "12px"}),

    dash.dcc.Loading(dash.dcc.Graph(id="growth-graph", style={"height": "70vh"}), type="default")
], style={"padding": "18px"})

# ----------------------------
# Callbacks
# ----------------------------
@app.callback(
    dash.Output("growth-graph", "figure"),
    dash.Input("country-dropdown", "value"),
    dash.Input("year-range", "value"),
    dash.Input("smooth-window", "value"),
    dash.Input("smooth-toggle", "value"),
    dash.Input("outlier-toggle", "value"),
)
def update_chart(selected_countries, year_range, window, smooth_toggle, outlier_toggle):
    if not selected_countries:
        selected_countries = []

    y0, y1 = year_range
    mask = (
        df.index.get_level_values(0).isin(selected_countries) &
        (df.index.get_level_values(1).year >= y0) &
        (df.index.get_level_values(1).year <= y1)
    )
    sub = df.loc[mask].copy()
    if sub.empty:
        fig = plotly.graph_objects.Figure()
        fig.update_layout(
            title="No data for the current selection",
            xaxis_title="Year", yaxis_title="GDP Growth (%)"
        )
        return fig

    # Smoothed growth
    show_smoothed = "smooth" in (smooth_toggle or [])
    if show_smoothed:
        sub["Smoothed Growth (%)"] = (
            sub.groupby(level=0)["GDP Growth (%)"].transform(lambda s: moving_average_nan(s, window))
        )

    fig = plotly.graph_objects.Figure()
    y_col = "Smoothed Growth (%)" if show_smoothed else "GDP Growth (%)"

    for c in selected_countries:
        cs = sub.xs(c, level=0, drop_level=False)
        fig.add_trace(plotly.graph_objects.Scatter(
            x=cs.index.get_level_values(1),
            y=cs[y_col],
            mode="lines",
            name=c + (" (smoothed)" if show_smoothed else ""),
            hovertemplate=f"Country: {c}<br>Year: %{{x|%Y}}<br>{y_col}: %{{y:.2f}}%<extra></extra>"
        ))

        if "outliers" in (outlier_toggle or []):
            out = cs[cs["z"].abs() > 2.5]
            if not out.empty:
                fig.add_trace(plotly.graph_objects.Scatter(
                    x=out.index.get_level_values(1),
                    y=out["GDP Growth (%)"],
                    mode="markers",
                    name=f"{c} outliers",
                    marker=dict(size=8, symbol="x"),
                    hovertemplate=f"Country: {c}<br>Year: %{{x|%Y}}<br>Raw Growth: %{{y:.2f}}%<br>z: %{{customdata:.2f}}<extra></extra>",
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
    app.run(debug=True)

