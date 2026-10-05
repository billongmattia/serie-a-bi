from etl.profiling import COLUMNS, coverage_matrix, to_markdown
from etl.rawio import read_raw_csv


def write(tmp_path, name, text, encoding="utf-8"):
    path = tmp_path / name
    path.write_bytes(text.encode(encoding))
    return path


def test_read_raw_csv_returns_strings_and_drops_empty_rows(tmp_path):
    path = write(tmp_path, "a.csv", "Date,HomeTeam\n2016-08-20,Juventus\n,\n")
    df = read_raw_csv(path)
    assert list(df.columns) == ["Date", "HomeTeam"]
    assert len(df) == 1
    assert df.loc[0, "HomeTeam"] == "Juventus"


def test_read_raw_csv_falls_back_to_latin1(tmp_path):
    path = write(tmp_path, "b.csv", "Date,HomeTeam\n2016-08-20,Città\n", encoding="latin-1")
    assert read_raw_csv(path).loc[0, "HomeTeam"] == "Città"


def test_coverage_matrix_classifies_columns(tmp_path):
    full = "Date,HS,AS,HY\n2016-08-20,10,5,2\n2016-08-21,12,6,1\n"
    partial = "Date,HS\n2017-08-20,10\n2017-08-21,\n"
    p1 = write(tmp_path, "full.csv", full)
    p2 = write(tmp_path, "partial.csv", partial)
    matrix = coverage_matrix({2016: p1, 2017: p2})

    row16 = matrix[matrix["stagione"] == "2016/17"].iloc[0]
    assert row16["partite"] == 2
    assert row16["HS"] == "sì"
    assert row16["HY"] == "sì"
    assert row16["HF"] == "no"  # colonna assente

    row17 = matrix[matrix["stagione"] == "2017/18"].iloc[0]
    assert row17["HS"] == "parziale"
    assert row17["HY"] == "no"


def test_to_markdown_has_header_and_one_row_per_season(tmp_path):
    p = write(tmp_path, "c.csv", "Date,HS\n2016-08-20,1\n")
    text = to_markdown(coverage_matrix({2016: p}))
    lines = text.strip().splitlines()
    assert lines[0].startswith("| stagione | partite |")
    assert all(col in lines[0] for col in COLUMNS)
    assert len(lines) == 3  # intestazione, separatore, 1 stagione
