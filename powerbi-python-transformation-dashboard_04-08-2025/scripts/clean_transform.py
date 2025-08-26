"""
Clean and transform project portfolio data for the Transformation Office Dashboard.

- Loads JSON from data/ simulated_projects.json (default) with structure:  {"projects": [...]}
- Normalises to a DataFrame and applies robust, vectorised data wrangling
- Adds derived KPI feilds (over_budget, late, budget variance, days late, etc.)
- Flags data quality issues using vectorised conditions and joins issue labels
- Export cleaned outputs for Power BI; also exposes 'dataset' for Power BI's Python connector

Run:
    python scripts/clean_transform.py \
    - - input data/ simulated_projects.json \
    - - outdir data \
    - - reference-date 2025-08-16

If you embed this file's contents into Power BI via the Python Script connector, 
Power BI will pick up the 'dataset' variable (a pandas DataFrame) as the output.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd

# Configuration constants
# These paths are relative to the project root
# Adjust as necessary for your project structure
DEFAULT_INPUT = Path("data/simulated_projects.json")
DEFAULT_OUTDIR = Path("data")

# Expected fields in the JSON "projects" objects.
REQUIRED_COLUMNS: Dict[str, object] = {
    "id": pd.NA,
    "name": pd.NA,
    "department": pd.NA,
    "owner": pd.NA,
    "start_date": pd.NA,
    "end_date": pd.NA,
    "budget": pd.NA,
    "actual_cost": pd.NA,
    "status": pd.NA,
    "strategic_pillar": pd.NA,
    "risk_score": pd.NA,
    "alignment_score": pd.NA,
}

# Canonical status values to standardise towards
STATUS_CATEGORIES: Iterable[str] = ("On Track", "At Risk", "Completed")

# Utilities

def _ensure_required_columns(df: pd.DataFrame, required: Dict[str, object]) -> pd.DataFrame:
    """
    Ensure the DataFrame has all required columns, filling missing with sensible defaults.
    """
    for col, default in required.items():
        if col not in df.columns:
            df[col] = default
    return df

def _standardise_status(raw_status: pd.Series) -> pd.Series:
    """
    Standardise free-text status values into a tidy set:
    ["On Track", "At Risk", "Completed"]
    Anything unknown is left as title-cased free text (still informative).
    """

    s = raw_status.astype("string").str.strip().str.lower()

# Normalise common variants
    replacements = {
        "ontrack": "on track",
        "on_track": "on track",
        "on-track": "on track",
        "ontime": "on track",
        "completed": "completed",
        "complete": "completed",
        "done": "completed",
        "closed": "completed",
        "atrisk": "at risk",
        "at-risk": "at risk",
        "delayed": "at risk",
        "late": "at risk",
    }

    s = s.replace(replacements)

    # Title case for presentation
    s = s.str.title()

    # Optionally convert to category for memory & consistency
    # Unknown statuses remain as their title-cased string (not forced into categories)
    s_cat = pd.Categorical(s, categories=list(STATUS_CATEGORIES))
    # Where not in categories, keep the string (so we don't lose information)
    # We'll return a string dtype series to avoid category NA surprised in BI tools
    return pd.Series(s, index= raw_status.index, dtype="string")

def _parse_dates(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """
    Parse date columns, converting to datetime and handling errors.
    """
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=False)
    return df

def _to_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """
    Coerce numeric columns; keep NaN for non-parsable values.
    """
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _tidy_strings(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """
    Trim whitespace; convert empty strings to <NA> using pandas' native string dtype.
    """
    for c in cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)  # Convert empty strings to <NA>
            )
    return df

def _compute_derived_fields(df: pd.DataFrame, reference_date: pd.Timestamp) -> pd.DataFrame:
    """
    Add derived KPI and helper fields using vectorised operations.
    """
    # Over budget (only if both values present)
    df["over_budget"] = (
        df["actual_cost"].gt(df["budget"])
        & df["actual_cost"].notna()
        & df["budget"].notna()
    )

    # Portfolio-level financial deltas
    df["budget_variance"] = np.where(
        df["budget"].notna() & df["actual_cost"].notna(),
        df["actual_cost"] - df["budget"],
        np.nan,
    )
    df["budget_variance_pct"] = np.where(
        df["budget"].notna() & df["budget"].ne(0) & df["actual_cost"].notna(),
        (df["actual_cost"] - df["budget"]) / df["budget"],
        np.nan,
    )

    # Active vs completed convenience fields
    df["active"] = df["status"].ne("Completed")

    # Late if active and end date has passed
    df["late"] = (
        df["active"]
        & df["end_date"].notna()
        & df["end_date"].lt(reference_date)
        )
    
    # Days late (nullable integer)
    df["days_late"] = np.where(
        df["late"],
        (reference_date - df["end_date"]).dt.days,
        np.nan,
    )
    df["days_late"] = pd.Series(days_late, index=df.index).astype("Int64")  # Nullable integer type

    # Duration (planned) in days where start/end present
    df["planned_duration_days"] = pd.Series(
        np.where(
            df["start_date"].notna() & df["end_date"].notna(),
            (df["end_date"] - df["start_date"]).dt.days,
            np.nan,
        ),
        index=df.index,
    ).astype("Int64")  # Nullable integer type

    # Last refreshed timestamp for data lineage/trust
    df["last_refreshed"] = reference_date.normalize()

    return df

def _flag_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create vectorised data quality flags and a joined human-readable description.
    """
    # Atomic boolean conditions (all vectorised)
    end_missing = df["end_date"].isna()
    budget_missing = df["budget"].isna()
    owner_missing = df["owner"].isna()
    zero_active = df["budget"].notna() & df["budget"].eq(0) & df["status"].ne("Completed")
    negative_budget = df["budget"].notna() & df["budget"].lt(0)
    negative_actual = df["actual _cost"].notna() & df["actual_cost"].lt(0)
    end_before_start = df["start_date"].notna() & df["end_date"].notna() & (df["end_date"] < df["start_date"])

    # Risk/alignment score validtity (1-5 expected; if you don't track this, these will simply be Nan)
    risk_invalid = df["risk_score"].notna() & ~df["risk_score"].between(1, 5, inclusive="both")
    alignment_invalid = df["alignment_score"].notna() & ~df["alignment_score"].between(1, 5, inclusive="both")

    issue_conditions: Dict[str, pd.Series] = {
        "Missing end date": end_missing,
        "Missing budget": budget_missing,
        "Missing owner": owner_missing,
        "Zero budget for active project": zero_active,
        "Negative budget": negative_budget,
        "Negative actual cost": negative_actual,
        "End date before start date": end_before_start,
        "Invalid risk score": risk_invalid,
        "Invalid alignment score": alignment_invalid,
    }

    issues_df = pd.DataFrame(
        {label: np.where(mask, label, np.nan) for label, mask in issue_conditions.items()},
        index=df.index
    )

    joined = (
        issues_df
        .stack(dropna=True)
        .groupby(level=0)
        .agg("; ".join)
    )

    