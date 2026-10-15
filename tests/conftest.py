import sqlite3

import pandas as pd
import pytest
from sqlalchemy import create_engine

from etl import config, transform as t
from etl.load import load_star


def _match(date, home, away, goals, yellows, away_red=0):
    return {
        "Date": date, "HomeTeam": home, "AwayTeam": away,
        "FTHG": str(goals[0]), "FTAG": str(goals[1]),
        "HTHG": "0", "HTAG": "0",
        "HS": "10", "AS": "8", "HST": "4", "AST": "3",
        "HF": "10", "AF": "14", "HC": "5", "AC": "4",
        "HY": str(yellows[0]), "AY": str(yellows[1]),
        "HR": "0", "AR": str(away_red),
    }


SEASON_2016 = [
    _match("2016-09-01", "A", "B", (2, 0), (1, 0)),
    _match("2016-09-02", "B", "C", (1, 1), (2, 3), away_red=1),
    _match("2016-09-03", "C", "A", (0, 3), (0, 1)),
    _match("2016-09-04", "B", "A", (0, 1), (1, 1)),
    _match("2016-09-05", "C", "B", (2, 1), (2, 1)),
    _match("2016-09-06", "A", "C", (1, 1), (0, 2)),
]
SEASON_2017 = [
    _match("2017-09-01", "A", "B", (1, 0), (0, 0)),
]


@pytest.fixture
def warehouse(tmp_path):
    """Mini-campionato (3 squadre, 7 partite, 2 stagioni) con risultati calcolati a mano."""
    db = tmp_path / "warehouse.db"
    con = sqlite3.connect(db)
    for name in ("01_staging.sql", "02_star_schema.sql"):
        con.executescript((config.ROOT / "sql" / name).read_text(encoding="utf-8"))
    con.close()
    engine = create_engine(f"sqlite:///{db}")
    frames = {
        2016: pd.DataFrame(SEASON_2016, dtype="object"),
        2017: pd.DataFrame(SEASON_2017, dtype="object"),
    }
    star, _ = t.transform_all(frames, {})
    load_star(engine, star)
    return engine
