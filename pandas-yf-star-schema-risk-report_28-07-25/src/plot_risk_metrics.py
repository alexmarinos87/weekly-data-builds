# src/plot_risk_metrics.py
import os
import pathlib

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv

# ── 0. Load .env no matter where you run from ───────────────────────────
load_dotenv(find_dotenv())

# ── 1. Build SQLAlchemy engine ─────────────────────────────────────────
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ── 2. Prepare output directory ────────────────────────────────────────
OUTPUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "docs" / "img"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Create Sharpe & Sortino bar-charts side-by-side and save as PNG."""

    # ── 3. Read the risk_metrics table from Postgres ────────────────────
    df = pd.read_sql("SELECT * FROM risk_metrics", engine)

    # ── 4. Side-by-side subplots (best practice) ────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), sharex=True)

    # Sharpe ratio
    df.plot.bar(
        x="ticker",
        y="sharpe_ratio",
        ax=ax1,
        legend=False,
        title="Sharpe Ratio",
    )
    ax1.set_ylabel("Sharpe Ratio")

    # Sortino ratio
    df.plot.bar(
        x="ticker",
        y="sortino_ratio",
        ax=ax2,
        legend=False,
        title="Sortino Ratio",
    )
    ax2.set_ylabel("Sortino Ratio")

    plt.tight_layout()

    # ── 5. Save the figure ─────────────────────────────────────────────
    out_file = OUTPUT_DIR / "risk_chart.png"
    fig.savefig(out_file, dpi=150, bbox_inches="tight")
    print(f"✅ chart saved → {out_file}")

    # ── 6. (Optional) show locally ────────────────────────────────────
    plt.show()


if __name__ == "__main__":
    main()
