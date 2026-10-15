import pandas as pd
from sqlalchemy import text

_FROM_TEAM_MATCH = """
FROM fact_team_match f
JOIN dim_match m ON m.match_key = f.match_key
JOIN dim_season s ON s.season_key = m.season_key
JOIN dim_team t ON t.team_key = f.team_key
"""


def _read(engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def to_numbers(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """MySQL restituisce Decimal per SUM e medie: li converte in numeri."""
    df = df.copy()
    for column in columns:
        df[column] = pd.to_numeric(df[column])
    return df


def list_seasons(engine) -> list[str]:
    df = _read(engine, "SELECT label FROM dim_season ORDER BY season_key DESC")
    return df["label"].tolist()


def list_teams(engine, season: str) -> list[str]:
    df = _read(
        engine,
        "SELECT DISTINCT t.team_name AS team " + _FROM_TEAM_MATCH
        + "WHERE s.label = :season ORDER BY t.team_name",
        {"season": season},
    )
    return df["team"].tolist()


def standings(engine, season: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT t.team_name AS squadra,
               COUNT(*) AS partite,
               SUM(CASE WHEN f.result = 'W' THEN 1 ELSE 0 END) AS vittorie,
               SUM(CASE WHEN f.result = 'D' THEN 1 ELSE 0 END) AS pareggi,
               SUM(CASE WHEN f.result = 'L' THEN 1 ELSE 0 END) AS sconfitte,
               SUM(f.goals_for) AS gol_fatti,
               SUM(f.goals_against) AS gol_subiti,
               SUM(f.points) AS punti
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season GROUP BY t.team_name",
        {"season": season},
    )
    numeric = ["partite", "vittorie", "pareggi", "sconfitte", "gol_fatti", "gol_subiti", "punti"]
    df = to_numbers(df, numeric)
    df[numeric] = df[numeric].astype(int)
    df["diff_reti"] = df["gol_fatti"] - df["gol_subiti"]
    score = df["punti"] * 1000 + df["diff_reti"]
    df["posizione"] = score.rank(method="dense", ascending=False).astype(int)
    df = df.sort_values(["posizione", "squadra"]).reset_index(drop=True)
    df = df.rename(columns={
        "posizione": "Posizione", "squadra": "Squadra", "partite": "Partite",
        "vittorie": "Vittorie", "pareggi": "Pareggi", "sconfitte": "Sconfitte",
        "gol_fatti": "Gol Fatti", "gol_subiti": "Gol Subiti",
        "diff_reti": "Diff Reti", "punti": "Punti",
    })
    return df[[
        "Posizione", "Squadra", "Partite", "Vittorie", "Pareggi", "Sconfitte",
        "Gol Fatti", "Gol Subiti", "Diff Reti", "Punti",
    ]]


def recent_form(engine, season: str, team: str, n: int = 5) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT d.date AS data, f.result AS risultato, f.goals_for AS gol_fatti,
               f.goals_against AS gol_subiti, o.team_name AS avversario
        """ + _FROM_TEAM_MATCH + """
        JOIN dim_date d ON d.date_key = m.date_key
        JOIN dim_team o ON o.team_key = f.opponent_team_key
        WHERE s.label = :season AND t.team_name = :team
        ORDER BY m.match_key DESC
        LIMIT :n
        """,
        {"season": season, "team": team, "n": int(n)},
    )
    df["data"] = df["data"].astype(str)
    return df.rename(columns={
        "data": "Data", "risultato": "Risultato", "gol_fatti": "Gol fatti",
        "gol_subiti": "Gol subiti", "avversario": "Avversario",
    })


def team_summary(engine, season: str, team: str) -> dict | None:
    df = _read(
        engine,
        """
        SELECT SUM(f.points) AS punti, SUM(f.goals_for) AS gol_fatti,
               SUM(f.goals_against) AS gol_subiti, SUM(f.shots_for) AS tiri
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season AND t.team_name = :team",
        {"season": season, "team": team},
    )
    row = df.iloc[0]
    if pd.isna(row["punti"]):
        return None
    shots = row["tiri"]
    conversion = None if pd.isna(shots) or float(shots) == 0 else float(row["gol_fatti"]) / float(shots)
    return {
        "punti": int(row["punti"]),
        "gol_fatti": int(row["gol_fatti"]),
        "gol_subiti": int(row["gol_subiti"]),
        "conversione_tiri": conversion,
    }


def home_away_points(engine, season: str, team: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT CASE WHEN f.is_home = 1 THEN 'Casa' ELSE 'Trasferta' END AS campo,
               SUM(f.points) AS punti
        """ + _FROM_TEAM_MATCH + """
        WHERE s.label = :season AND t.team_name = :team
        GROUP BY f.is_home
        ORDER BY f.is_home DESC
        """,
        {"season": season, "team": team},
    )
    df = to_numbers(df, ["punti"])
    df["punti"] = df["punti"].astype(int)
    return df.rename(columns={"campo": "Campo", "punti": "Punti"})


def season_trends(engine) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT s.label AS stagione,
               SUM(f.goals_for) * 1.0 / COUNT(DISTINCT f.match_key) AS gol,
               SUM(CASE WHEN f.is_home = 1 AND f.result = 'W' THEN 1 ELSE 0 END) * 1.0
                   / SUM(f.is_home) AS vittorie_casa,
               SUM(f.yellow_for) * 1.0 / COUNT(DISTINCT f.match_key) AS gialli,
               SUM(f.red_for) * 1.0 / COUNT(DISTINCT f.match_key) AS rossi,
               SUM(f.fouls_for) * 1.0 / COUNT(DISTINCT f.match_key) AS falli
        """ + _FROM_TEAM_MATCH + "GROUP BY s.label ORDER BY s.label",
    )
    df = to_numbers(df, ["gol", "vittorie_casa", "gialli", "rossi", "falli"])
    return df.rename(columns={
        "stagione": "Stagione", "gol": "Gol a Partita", "vittorie_casa": "% Vittorie Casa",
        "gialli": "Gialli a Partita", "rossi": "Rossi a Partita", "falli": "Falli a Partita",
    })


def discipline_by_team(engine, season: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT t.team_name AS squadra,
               SUM(f.fouls_for) * 1.0 / COUNT(*) AS falli,
               SUM(f.fouls_against) * 1.0 / COUNT(*) AS falli_subiti,
               SUM(f.yellow_for) * 1.0 / COUNT(*) AS gialli,
               SUM(f.red_for) * 1.0 / COUNT(*) AS rossi
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season GROUP BY t.team_name ORDER BY gialli DESC, t.team_name",
        {"season": season},
    )
    df = to_numbers(df, ["falli", "falli_subiti", "gialli", "rossi"])
    return df.rename(columns={
        "squadra": "Squadra", "falli": "Falli a Partita", "falli_subiti": "Falli Subiti a Partita",
        "gialli": "Gialli a Partita", "rossi": "Rossi a Partita",
    })
