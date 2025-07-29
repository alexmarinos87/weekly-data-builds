import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

df = pd.read_sql("SELECT * FROM risk_metrics", engine)
df.plot.bar(x='ticker', y=['sharpe_ratio', 'sortino_ratio'], title='Risk-adjusted Returns')

if __name__ == "__main__":
    # existing df.plot.bar(…) line
    df.plot.bar(x="ticker", y=["sharpe_ratio", "sortino_ratio"],
                title="Risk-adjusted Returns")
    plt.tight_layout()
    plt.show()                 # 👈 forces a window to appear
