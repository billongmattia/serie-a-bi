from decimal import Decimal

import pandas as pd
import pytest
from sqlalchemy import create_engine

from app import queries as q


def test_to_numbers_converts_decimals():
    df = pd.DataFrame({"x": [Decimal("1.5"), Decimal("2")], "y": ["a", "b"]})
    out = q.to_numbers(df, ["x"])
    assert out["x"].dtype.kind == "f"
    assert out["x"].sum() == pytest.approx(3.5)
    assert list(out["y"]) == ["a", "b"]


def test_list_seasons_latest_first(warehouse):
    assert q.list_seasons(warehouse) == ["2017/18", "2016/17"]


def test_list_teams_of_a_season(warehouse):
    assert q.list_teams(warehouse, "2016/17") == ["A", "B", "C"]
    assert q.list_teams(warehouse, "2017/18") == ["A", "B"]


def test_standings_2016_17(warehouse):
    df = q.standings(warehouse, "2016/17")
    assert list(df.columns) == [
        "Posizione", "Squadra", "Partite", "Vittorie", "Pareggi", "Sconfitte",
        "Gol Fatti", "Gol Subiti", "Diff Reti", "Punti",
    ]
    assert list(df["Squadra"]) == ["A", "C", "B"]
    a, c, b = (df.iloc[i] for i in range(3))
    assert (a["Posizione"], a["Partite"], a["Vittorie"], a["Pareggi"], a["Sconfitte"]) == (1, 4, 3, 1, 0)
    assert (a["Gol Fatti"], a["Gol Subiti"], a["Diff Reti"], a["Punti"]) == (7, 1, 6, 10)
    assert (c["Posizione"], c["Vittorie"], c["Pareggi"], c["Sconfitte"], c["Diff Reti"], c["Punti"]) == (2, 1, 2, 1, -2, 5)
    assert (b["Posizione"], b["Vittorie"], b["Pareggi"], b["Sconfitte"], b["Diff Reti"], b["Punti"]) == (3, 0, 1, 3, -4, 1)


def test_standings_positions_without_ties(warehouse):
    # 2017/18: una sola partita, A vince 1-0: A prima, B secondo (nessuna parità)
    df = q.standings(warehouse, "2017/18")
    assert list(df["Posizione"]) == [1, 2]


def test_standings_equal_points_and_goal_difference_get_same_position():
    # due squadre identiche (stessa partita pareggiata) condividono la posizione
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        for stmt in (
            "CREATE TABLE dim_season (season_key INT, label TEXT)",
            "CREATE TABLE dim_team (team_key INT, team_name TEXT)",
            "CREATE TABLE dim_match (match_key INT, season_key INT)",
            "CREATE TABLE fact_team_match (match_key INT, team_key INT, result TEXT, goals_for INT, goals_against INT, points INT)",
            "INSERT INTO dim_season VALUES (1, 'S')",
            "INSERT INTO dim_team VALUES (1, 'X'), (2, 'Y')",
            "INSERT INTO dim_match VALUES (1, 1)",
            "INSERT INTO fact_team_match VALUES (1, 1, 'D', 1, 1, 1), (1, 2, 'D', 1, 1, 1)",
        ):
            conn.exec_driver_sql(stmt)
    df = q.standings(engine, "S")
    assert list(df["Squadra"]) == ["X", "Y"]
    assert list(df["Posizione"]) == [1, 1]


def test_standings_of_unknown_season_is_empty(warehouse):
    assert q.standings(warehouse, "1999/00").empty


def test_recent_form_most_recent_first(warehouse):
    df = q.recent_form(warehouse, "2016/17", "A", 3)
    assert list(df.columns) == ["Data", "Risultato", "Gol fatti", "Gol subiti", "Avversario"]
    assert [tuple(r) for r in df.itertuples(index=False)] == [
        ("2016-09-06", "D", 1, 1, "C"),
        ("2016-09-04", "W", 1, 0, "B"),
        ("2016-09-03", "W", 3, 0, "C"),
    ]


def test_recent_form_limits_to_available_matches(warehouse):
    assert len(q.recent_form(warehouse, "2016/17", "A", 10)) == 4


def test_team_summary(warehouse):
    s = q.team_summary(warehouse, "2016/17", "A")
    assert (s["punti"], s["gol_fatti"], s["gol_subiti"]) == (10, 7, 1)
    assert s["conversione_tiri"] == pytest.approx(7 / 36)


def test_team_summary_none_when_team_did_not_play(warehouse):
    assert q.team_summary(warehouse, "2017/18", "C") is None


def test_home_away_points(warehouse):
    df = q.home_away_points(warehouse, "2016/17", "A")
    assert dict(zip(df["Campo"], df["Punti"])) == {"Casa": 4, "Trasferta": 6}


def test_season_trends(warehouse):
    df = q.season_trends(warehouse)
    assert list(df.columns) == [
        "Stagione", "Gol a Partita", "% Vittorie Casa",
        "Gialli a Partita", "Rossi a Partita", "Falli a Partita",
    ]
    assert list(df["Stagione"]) == ["2016/17", "2017/18"]
    r16, r17 = df.iloc[0], df.iloc[1]
    assert r16["Gol a Partita"] == pytest.approx(13 / 6)
    assert r16["% Vittorie Casa"] == pytest.approx(2 / 6)
    assert r16["Gialli a Partita"] == pytest.approx(14 / 6)
    assert r16["Rossi a Partita"] == pytest.approx(1 / 6)
    assert r16["Falli a Partita"] == pytest.approx(24)
    assert r17["Gol a Partita"] == pytest.approx(1.0)
    assert r17["% Vittorie Casa"] == pytest.approx(1.0)
    assert r17["Gialli a Partita"] == pytest.approx(0)


def test_discipline_by_team(warehouse):
    df = q.discipline_by_team(warehouse, "2016/17")
    assert list(df.columns) == [
        "Squadra", "Falli a Partita", "Falli Subiti a Partita",
        "Gialli a Partita", "Rossi a Partita",
    ]
    assert list(df["Squadra"]) == ["C", "B", "A"]  # più ammoniti prima
    by_team = df.set_index("Squadra")
    assert by_team.loc["A", "Gialli a Partita"] == pytest.approx(0.75)
    assert by_team.loc["B", "Gialli a Partita"] == pytest.approx(1.0)
    assert by_team.loc["C", "Gialli a Partita"] == pytest.approx(1.75)
    assert by_team.loc["C", "Rossi a Partita"] == pytest.approx(0.25)
    assert by_team.loc["A", "Falli a Partita"] == pytest.approx(12.0)
    assert by_team.loc["A", "Falli Subiti a Partita"] == pytest.approx(12.0)
