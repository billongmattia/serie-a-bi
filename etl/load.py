import pandas as pd
from sqlalchemy import text

from etl.extract import season_label

STAGING_COLUMNS = [
    "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HTHG", "HTAG", "HTR", "HS", "AS", "HST", "AST",
    "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
]
LOAD_ORDER = ["dim_season", "dim_date", "dim_team", "dim_match", "fact_team_match"]


def build_staging(raw_frames: dict[int, pd.DataFrame]) -> pd.DataFrame:
    parts = []
    for year, raw in sorted(raw_frames.items()):
        part = raw.reindex(columns=STAGING_COLUMNS).copy()
        part.insert(0, "season", season_label(year))
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def _nullify(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype(object).where(df.notna(), None)


def load_staging(engine, staging: pd.DataFrame) -> None:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM stg_matches"))
        _nullify(staging).to_sql(
            "stg_matches", conn, if_exists="append", index=False, chunksize=500
        )


def load_star(engine, tables: dict[str, pd.DataFrame]) -> None:
    with engine.begin() as conn:
        for name in reversed(LOAD_ORDER):
            conn.execute(text(f"DELETE FROM {name}"))
        for name in LOAD_ORDER:
            _nullify(tables[name]).to_sql(
                name, conn, if_exists="append", index=False, chunksize=500
            )
