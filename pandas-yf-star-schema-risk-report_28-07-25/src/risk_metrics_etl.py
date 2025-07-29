"""
ETL: download daily prices → compute Sharpe / Sortino → write to Postgres
"""

import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os

# ── 0. load secrets ────────────────────────────────────────────────────
load_dotenv(find_dotenv())  # finds the .env no matter where you run

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ── 1. download prices (patched) ───────────────────────────────────────
tickers = ["AAPL", "MSFT", "GOOGL"]

# yfinance ≥ 0.2 auto-adjusts prices into the Close column
data = (
    yf.download(tickers, start="2023-01-01", end="2024-01-01")["Close"]
    .rename_axis(columns="ticker")
)

# ── 2. risk metrics ────────────────────────────────────────────────────
returns       = data.pct_change().dropna()
mean_returns  = returns.mean() * 252
volatility    = returns.std() * np.sqrt(252)
sharpe        = mean_returns / volatility

# **FIXED**: annualize downside deviation, then divide
downside_std_daily   = returns.where(returns < 0).std()         # daily downside stdev
downside_std_annual  = downside_std_daily * np.sqrt(252)       # annualized downside stdev
sortino              = mean_returns / downside_std_annual      # correct Sortino

metrics = pd.DataFrame({
    "ticker":        sharpe.index,
    "sharpe_ratio":  sharpe.values,
    "sortino_ratio": sortino.values,
})

# ── 3. write to Postgres ───────────────────────────────────────────────
metrics.to_sql("risk_metrics", engine, if_exists="replace", index=False)
print("✅ wrote", len(metrics), "rows → risk_metrics (replace)")
