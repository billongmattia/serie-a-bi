import hashlib
from pathlib import Path

import pandas as pd

from etl.extract import season_label

REQUIRED = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
NUMERIC = [
    "FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST",
    "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
]
OPTIONAL = NUMERIC[2:]  # tutto tranne FTHG/FTAG

HOME_COLUMNS = {
    "goals_for": "FTHG", "goals_against": "FTAG",
    "goals_ht_for": "HTHG", "goals_ht_against": "HTAG",
    "shots_for": "HS", "shots_against": "AS",
    "shots_on_target_for": "HST", "shots_on_target_against": "AST",
    "fouls_for": "HF", "fouls_against": "AF",
    "corners_for": "HC", "corners_against": "AC",
    "yellow_for": "HY", "red_for": "HR",
}
AWAY_COLUMNS = {
    "goals_for": "FTAG", "goals_against": "FTHG",
    "goals_ht_for": "HTAG", "goals_ht_against": "HTHG",
    "shots_for": "AS", "shots_against": "HS",
    "shots_on_target_for": "AST", "shots_on_target_against": "HST",
    "fouls_for": "AF", "fouls_against": "HF",
    "corners_for": "AC", "corners_against": "HC",
    "yellow_for": "AY", "red_for": "AR",
}
POINTS = {"W": 3, "D": 1, "L": 0}


def load_team_map(path: Path) -> dict[str, str]:
    df = pd.read_csv(path, dtype=str)
    return dict(zip(df["raw_name"].str.strip(), df["normalized_name"].str.strip()))


def parse_dates(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")


def _clean_team(series: pd.Series, team_map: dict[str, str]) -> pd.Series:
    text = series.astype("string").str.strip()
    text = text.mask(text == "", pd.NA)
    return text.map(lambda name: team_map.get(name, name), na_action="ignore")


def clean_matches(raw: pd.DataFrame, start_year: int, team_map: dict[str, str]):
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(f"Colonne obbligatorie mancanti: {missing}")

    df = raw.copy()
    for column in OPTIONAL:
        if column not in df.columns:
            df[column] = float("nan")

    df["date"] = parse_dates(df["Date"])
    for column in NUMERIC:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    df["home"] = _clean_team(df["HomeTeam"], team_map)
    df["away"] = _clean_team(df["AwayTeam"], team_map)
    df["season_start"] = start_year

    valid = df[["date", "home", "away", "FTHG", "FTAG"]].notna().all(axis=1)
    keep = ["season_start", "date", "home", "away"] + NUMERIC
    return df.loc[valid, keep].reset_index(drop=True), int((~valid).sum())


def make_match_id(season_start: int, date, home: str, away: str) -> str:
    text = f"{season_label(int(season_start))}|{date:%Y-%m-%d}|{home}|{away}"
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def _matchday(df: pd.DataFrame) -> pd.Series:
    """Giornata = max tra il n. di partita di casa e quello della trasferta
    (approssimazione: i recuperi possono spostarla di poco)."""
    long = pd.concat([
        df[["season_start", "match_key", "home"]].rename(columns={"home": "team"}),
        df[["season_start", "match_key", "away"]].rename(columns={"away": "team"}),
    ]).sort_values(["season_start", "match_key"])
    long["n"] = long.groupby(["season_start", "team"]).cumcount() + 1
    return df["match_key"].map(long.groupby("match_key")["n"].max())


def _side_rows(df, mapping, team_col, opp_col, is_home, team_keys) -> pd.DataFrame:
    out = pd.DataFrame({
        "match_key": df["match_key"],
        "team_key": df[team_col].map(team_keys),
        "opponent_team_key": df[opp_col].map(team_keys),
        "is_home": 1 if is_home else 0,
    })
    for target, source in mapping.items():
        out[target] = df[source]
    return out


def _result(goals_for, goals_against) -> str:
    if goals_for > goals_against:
        return "W"
    return "D" if goals_for == goals_against else "L"


def build_star(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    df = cleaned.sort_values(["season_start", "date", "home", "away"]).reset_index(drop=True)
    df["match_key"] = df.index + 1
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
    df["match_id"] = [
        make_match_id(s, d, h, a)
        for s, d, h, a in zip(df["season_start"], df["date"], df["home"], df["away"])
    ]
    df["matchday"] = _matchday(df)

    team_names = sorted(set(df["home"]) | set(df["away"]))
    team_keys = {name: i + 1 for i, name in enumerate(team_names)}

    seasons = sorted(df["season_start"].unique())
    dim_season = pd.DataFrame({
        "season_key": seasons,
        "label": [season_label(int(s)) for s in seasons],
        "start_year": seasons,
        "end_year": [int(s) + 1 for s in seasons],
    })

    # Calendario continuo (tutti i giorni, anche senza partite): serve a Power BI
    # per usare dim_date come tabella data.
    calendar = pd.Series(pd.date_range(df["date"].min(), df["date"].max(), freq="D"))
    dim_date = pd.DataFrame({
        "date_key": calendar.dt.strftime("%Y%m%d").astype(int).values,
        "date": calendar.dt.strftime("%Y-%m-%d").values,
        "day": calendar.dt.day.values,
        "month": calendar.dt.month.values,
        "year": calendar.dt.year.values,
        "weekday": calendar.dt.day_name().values,
    })

    dim_team = pd.DataFrame({"team_key": list(team_keys.values()), "team_name": team_names})

    dim_match = pd.DataFrame({
        "match_key": df["match_key"],
        "match_id": df["match_id"],
        "date_key": df["date_key"],
        "season_key": df["season_start"],
        "matchday": df["matchday"],
        "home_team_key": df["home"].map(team_keys),
        "away_team_key": df["away"].map(team_keys),
    })

    fact = pd.concat([
        _side_rows(df, HOME_COLUMNS, "home", "away", True, team_keys),
        _side_rows(df, AWAY_COLUMNS, "away", "home", False, team_keys),
    ])
    fact["result"] = [
        _result(gf, ga) for gf, ga in zip(fact["goals_for"], fact["goals_against"])
    ]
    fact["points"] = fact["result"].map(POINTS)
    fact = fact.sort_values(["match_key", "is_home"], ascending=[True, False]).reset_index(drop=True)

    return {
        "dim_season": dim_season,
        "dim_date": dim_date,
        "dim_team": dim_team,
        "dim_match": dim_match,
        "fact_team_match": fact,
    }


def transform_all(raw_frames: dict[int, pd.DataFrame], team_map: dict[str, str]):
    parts, rejected = [], {}
    for year, raw in sorted(raw_frames.items()):
        cleaned, count = clean_matches(raw, year, team_map)
        parts.append(cleaned)
        rejected[year] = count
    return build_star(pd.concat(parts, ignore_index=True)), rejected
