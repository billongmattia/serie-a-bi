import pandas as pd

from app import charts


def test_rgba():
    assert charts.rgba("#3B82F6", 0.25) == "rgba(59,130,246,0.25)"


def test_area_chart_fills_to_zero_and_keeps_data():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    fig = charts.area_chart(df, "Stagione", "Gol a Partita", "Gol a partita")
    trace = fig.data[0]
    assert trace.fill == "tozeroy"
    assert list(trace.y) == [2.96, 2.68]
    assert fig.layout.title.text == "Gol a partita"


def test_hbar_chart_shows_every_label_and_scales_height():
    df = pd.DataFrame({"Squadra": [f"S{i}" for i in range(20)], "Gialli": [float(i) for i in range(20)]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra", "Gialli per squadra")
    assert fig.data[0].orientation == "h"
    assert fig.layout.yaxis.dtick == 1
    assert fig.layout.height >= 20 * 26


def test_grouped_bar_has_one_trace_per_series():
    df = pd.DataFrame({"Campo": ["Casa", "Trasferta"], "Gol fatti": [3, 4], "Gol subiti": [1, 0]})
    fig = charts.grouped_bar(df, "Campo", ["Gol fatti", "Gol subiti"], "Casa vs trasferta")
    assert [t.name for t in fig.data] == ["Gol fatti", "Gol subiti"]
    assert fig.layout.barmode == "group"
