import pytest

from etl.extract import extract_all, extract_season, season_code, season_label

CSV = b"Date,HomeTeam,AwayTeam\n2016-08-20,Juventus,Fiorentina\n"


def test_season_helpers():
    assert season_code(2016) == "1617"
    assert season_code(1999) == "9900"
    assert season_label(2016) == "2016/17"
    assert season_label(2025) == "2025/26"


def test_extract_downloads_and_caches(tmp_path):
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return CSV

    path = extract_season(2016, tmp_path, fake_fetch)
    assert path.name == "season-1617.csv"
    assert path.read_bytes() == CSV
    assert calls == ["https://datahub.io/football/italian-serie-a/_r/-/season-1617.csv"]

    extract_season(2016, tmp_path, fake_fetch)
    assert len(calls) == 1  # seconda volta: arriva dalla cache


def test_extract_rejects_html_and_does_not_cache(tmp_path):
    with pytest.raises(ValueError):
        extract_season(2016, tmp_path, lambda url: b"<!DOCTYPE html><html></html>")
    assert list(tmp_path.iterdir()) == []


def test_extract_all_continues_after_a_failure(tmp_path):
    def fake_fetch(url):
        if "1718" in url:
            raise RuntimeError("rete non raggiungibile")
        return CSV

    paths, failures = extract_all([2016, 2017, 2018], tmp_path, fake_fetch)
    assert sorted(paths) == [2016, 2018]
    assert list(failures) == [2017]
    assert "rete non raggiungibile" in failures[2017]
