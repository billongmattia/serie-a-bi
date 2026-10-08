import sqlite3
from itertools import permutations

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from etl import config, transform as t
from etl.load import build_staging, load_staging, load_star
from etl.quality import parse_checks, run_quality_checks

ROW = {
    "Date": "2016-08-20", "HomeTeam": "Juventus", "AwayTeam": "Fiorentina",
    "FTHG": "2", "FTAG": "1", "HTHG": "1", "HTAG": "0",
    "HS": "15", "AS": "8", "HST": "6", "AST": "3",
    "HF": "12", "AF": "14", "HC": "6", "AC": "2",
    "HY": "2", "AY": "3", "HR": "0", "AR": "1",
}
ROW2 = {**ROW, "Date": "2016-08-27", "HomeTeam": "Roma", "AwayTeam": "Udinese"}


@pytest.fixture
def engine(tmp_path):
    db = tmp_path / "test.db"
    con = sqlite3.connect(db)
    for name in ("01_staging.sql", "02_star_schema.sql"):
        con.executescript((config.ROOT / "sql" / name).read_text(encoding="utf-8"))
    con.close()
    return create_engine(f"sqlite:///{db}")


def star():
    frames = {2016: pd.DataFrame([ROW, ROW2], dtype="object")}
    return frames, t.transform_all(frames, {})[0]


def count(engine, table):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()


def test_load_star_writes_all_tables(engine):
    _, tables = star()
    load_star(engine, tables)
    assert count(engine, "dim_match") == 2
    assert count(engine, "fact_team_match") == 4
    assert count(engine, "dim_team") == 4
    assert count(engine, "dim_season") == 1


def test_load_is_idempotent(engine):
    frames, tables = star()
    for _ in range(2):
        load_staging(engine, build_staging(frames))
        load_star(engine, tables)
    assert count(engine, "stg_matches") == 2
    assert count(engine, "dim_match") == 2
    assert count(engine, "fact_team_match") == 4


def test_staging_keeps_raw_values_and_season(engine):
    frames, _ = star()
    load_staging(engine, build_staging(frames))
    with engine.connect() as conn:
        row = conn.execute(text("SELECT season, HomeTeam, FTHG FROM stg_matches ORDER BY Date")).first()
    assert tuple(row) == ("2016/17", "Juventus", "2")


def test_parse_checks_splits_named_blocks():
    sql = "-- check: uno\nSELECT 1;\n\n-- check: due\nSELECT 2;\n"
    assert parse_checks(sql) == {"uno": "SELECT 1", "due": "SELECT 2"}


def test_quality_checks_flag_incomplete_season(engine):
    _, tables = star()
    load_star(engine, tables)
    problems = run_quality_checks(engine)
    assert any("girone" in p for p in problems)
    assert not any("due righe" in p for p in problems)


def test_quality_accepts_a_complete_season_of_any_size(engine):
    # 4 squadre, andata e ritorno = 12 partite: valido anche se non sono 20 squadre
    rows = [
        {**ROW, "Date": f"2000-09-{i + 1:02d}", "HomeTeam": home, "AwayTeam": away}
        for i, (home, away) in enumerate(permutations(["A", "B", "C", "D"], 2))
    ]
    frames = {2000: pd.DataFrame(rows, dtype="object")}
    load_star(engine, t.transform_all(frames, {})[0])
    assert run_quality_checks(engine) == []


def test_quality_flags_champion_check_when_the_team_is_missing(engine):
    # stagione 2016 caricata ma senza Juventus (es. nome cambiato nella mappa)
    rows = [
        {**ROW, "HomeTeam": "Roma", "AwayTeam": "Udinese"},
        {**ROW, "Date": "2016-08-27", "HomeTeam": "Lazio", "AwayTeam": "Milan"},
    ]
    frames = {2016: pd.DataFrame(rows, dtype="object")}
    load_star(engine, t.transform_all(frames, {})[0])
    problems = run_quality_checks(engine)
    assert any("Juventus" in p for p in problems)
