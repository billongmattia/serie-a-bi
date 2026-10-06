import pandas as pd

from etl import transform as t


def raw(rows):
    return pd.DataFrame(rows, dtype="object")


FULL = {
    "Date": "2016-08-20", "HomeTeam": "Juventus", "AwayTeam": "Fiorentina",
    "FTHG": "2", "FTAG": "1", "HTHG": "1", "HTAG": "0",
    "HS": "15", "AS": "8", "HST": "6", "AST": "3",
    "HF": "12", "AF": "14", "HC": "6", "AC": "2",
    "HY": "2", "AY": "3", "HR": "0", "AR": "1",
    "Referee": None,
}


def star_from(rows, year=2016, team_map=None):
    cleaned, rejected = t.clean_matches(raw(rows), year, team_map or {})
    return t.build_star(cleaned), rejected


def test_parse_dates_reads_iso_and_flags_invalid():
    out = t.parse_dates(pd.Series(["2016-08-20", "20/08/2016", "", None], dtype="object"))
    assert out.iloc[0] == pd.Timestamp("2016-08-20")
    assert pd.isna(out.iloc[1]) and pd.isna(out.iloc[2]) and pd.isna(out.iloc[3])


def test_normalize_team_names_with_map():
    star, _ = star_from([{**FULL, "HomeTeam": "Verona"}], team_map={"Verona": "Hellas Verona"})
    assert "Hellas Verona" in set(star["dim_team"]["team_name"])
    assert "Verona" not in set(star["dim_team"]["team_name"])


def test_invalid_rows_are_rejected_and_counted():
    rows = [FULL, {**FULL, "Date": None}, {**FULL, "HomeTeam": None}, {**FULL, "FTHG": ""}]
    cleaned, rejected = t.clean_matches(raw(rows), 2016, {})
    assert len(cleaned) == 1
    assert rejected == 3


def test_missing_optional_columns_become_null():
    minimal = {k: FULL[k] for k in ("Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG")}
    star, rejected = star_from([minimal])
    fact = star["fact_team_match"]
    assert rejected == 0
    assert len(fact) == 2
    assert fact["shots_for"].isna().all()
    assert fact["yellow_for"].isna().all()
    assert fact["goals_for"].notna().all()


def test_referee_column_is_ignored():
    star, _ = star_from([{**FULL, "Referee": "P Mazzoleni"}])
    assert "dim_referee" not in star
    assert "referee_key" not in star["dim_match"].columns


def test_one_match_gives_one_dim_match_and_two_fact_rows():
    star, _ = star_from([FULL])
    assert len(star["dim_match"]) == 1
    fact = star["fact_team_match"]
    assert len(fact) == 2

    home = fact[fact["is_home"] == 1].iloc[0]
    away = fact[fact["is_home"] == 0].iloc[0]
    assert (home["goals_for"], home["goals_against"]) == (2, 1)
    assert (away["goals_for"], away["goals_against"]) == (1, 2)
    assert (home["result"], home["points"]) == ("W", 3)
    assert (away["result"], away["points"]) == ("L", 0)
    assert (home["shots_for"], home["shots_against"]) == (15, 8)
    assert (away["shots_for"], away["shots_against"]) == (8, 15)
    assert (home["yellow_for"], away["yellow_for"]) == (2, 3)
    assert (home["red_for"], away["red_for"]) == (0, 1)
    assert home["opponent_team_key"] == away["team_key"]


def test_draw_gives_one_point_each():
    star, _ = star_from([{**FULL, "FTHG": "1", "FTAG": "1"}])
    fact = star["fact_team_match"]
    assert set(fact["result"]) == {"D"}
    assert list(fact["points"]) == [1, 1]


def test_match_id_is_stable_and_unique():
    a = t.make_match_id(2016, pd.Timestamp("2016-08-20"), "Juventus", "Fiorentina")
    b = t.make_match_id(2016, pd.Timestamp("2016-08-20"), "Juventus", "Fiorentina")
    c = t.make_match_id(2016, pd.Timestamp("2016-08-20"), "Fiorentina", "Juventus")
    assert a == b
    assert a != c
    assert len(a) == 16


def test_matchday_follows_each_teams_sequence():
    rows = [
        {**FULL, "Date": "2016-08-20", "HomeTeam": "A", "AwayTeam": "B"},
        {**FULL, "Date": "2016-08-27", "HomeTeam": "A", "AwayTeam": "C"},
        {**FULL, "Date": "2016-09-03", "HomeTeam": "B", "AwayTeam": "C"},
    ]
    star, _ = star_from(rows)
    assert list(star["dim_match"].sort_values("match_key")["matchday"]) == [1, 2, 2]


def test_dim_date_and_season_columns():
    star, _ = star_from([FULL])
    d = star["dim_date"].iloc[0]
    assert (d["date_key"], d["date"], d["day"], d["month"], d["year"]) == (
        20160820, "2016-08-20", 20, 8, 2016,
    )
    assert d["weekday"] == "Saturday"
    s = star["dim_season"].iloc[0]
    assert (s["season_key"], s["label"], s["start_year"], s["end_year"]) == (
        2016, "2016/17", 2016, 2017,
    )


def test_dim_date_is_a_continuous_calendar():
    rows = [
        {**FULL, "Date": "2016-08-20"},
        {**FULL, "Date": "2016-08-27", "HomeTeam": "Roma", "AwayTeam": "Udinese"},
    ]
    star, _ = star_from(rows)
    dates = pd.to_datetime(star["dim_date"]["date"])
    assert len(dates) == 8  # dal 20 al 27 agosto compresi
    assert (dates.diff().dropna() == pd.Timedelta(days=1)).all()
    assert star["dim_date"]["date_key"].is_unique
    assert set(star["dim_match"]["date_key"]) <= set(star["dim_date"]["date_key"])


def test_transform_all_counts_rejections_per_season():
    frames = {2016: raw([FULL, {**FULL, "Date": None}]), 2017: raw([FULL])}
    star, rejected = t.transform_all(frames, {})
    assert rejected == {2016: 1, 2017: 0}
    assert len(star["dim_season"]) == 2
