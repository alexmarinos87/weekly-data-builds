CREATE TABLE tickers (
    ticker TEXT PRIMARY KEY,
    company_name TEXT
);

CREATE TABLE risk_metrics (
    ticker TEXT REFERENCES tickers(ticker),
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT
);
