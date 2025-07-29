import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

tickers = ['AAPL', 'MSFT', 'GOOGL']
data = yf.download(tickers, start="2023-01-01", end="2024-01-01")['Adj Close']

returns = data.pct_change().dropna()
mean_returns = returns.mean() * 252
volatility = returns.std() * np.sqrt(252)
sharpe = mean_returns / volatility
sortino = mean_returns / returns[returns < 0].std() * np.sqrt(252)

metrics = pd.DataFrame({
    'ticker': sharpe.index,
    'sharpe_ratio': sharpe.values,
    'sortino_ratio': sortino.values
})

# Save to PostgreSQL
metrics.to_sql('risk_metrics', engine, if_exists='replace', index=False)
