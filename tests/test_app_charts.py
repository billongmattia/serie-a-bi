import pandas as pd

from app import charts, theme


def test_rgba():
    assert charts.rgba("#3B82F6", 0.25) == "rgba(59,130,246,0.25)"


def test_area_chart_fills_with_a_vertical_gradient_and_keeps_data():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    fig = charts.area_chart(df, "Stagione", "Gol a Partita")
    trace = fig.data[0]
    assert trace.fill == "tozeroy"
    assert trace.fillgradient.type == "vertical"
    assert list(trace.y) == [2.96, 2.68]
    assert fig.layout.title.text is None  # il titolo sta sopra il grafico, in HTML


def test_area_chart_axis_is_zoomed_on_the_data_not_on_zero():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    low, high = charts.area_chart(df, "Stagione", "Gol a Partita").layout.yaxis.range
    assert 0 < low < 2.68
    assert high > 2.96


def test_area_chart_axis_never_goes_below_zero_for_non_negative_data():
    df = pd.DataFrame({"Stagione": ["a", "b"], "Valore": [0.0, 5.0]})
    assert charts.area_chart(df, "Stagione", "Valore").layout.yaxis.range[0] >= 0


def test_area_chart_handles_a_single_value():
    df = pd.DataFrame({"Stagione": ["2016/17"], "Valore": [3.0]})
    low, high = charts.area_chart(df, "Stagione", "Valore").layout.yaxis.range
    assert low < 3.0 < high


def test_charts_are_light_and_use_italian_separators():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Valore": [1.5, 2.5]})
    fig = charts.area_chart(df, "Stagione", "Valore")
    assert fig.layout.separators == ",."
    assert fig.layout.font.color == theme.INK
    assert fig.layout.paper_bgcolor == "rgba(0,0,0,0)"


def test_charts_have_no_axis_titles_and_horizontal_season_labels():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    for fig in (
        charts.area_chart(df, "Stagione", "Gol a Partita"),
        charts.grouped_bar(df, "Stagione", ["Gol a Partita"]),
    ):
        assert fig.layout.xaxis.title.text is None
        assert fig.layout.yaxis.title.text is None
        assert fig.layout.xaxis.tickangle == 0


def test_hbar_chart_leaves_room_for_the_value_labels():
    df = pd.DataFrame({"Squadra": ["A", "B"], "Gialli": [1.0, 2.0]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra")
    assert fig.layout.xaxis.range[0] == 0
    assert fig.layout.xaxis.range[1] > 2.0


def test_hbar_chart_shows_every_label_and_scales_height():
    df = pd.DataFrame({"Squadra": [f"S{i}" for i in range(20)], "Gialli": [float(i) for i in range(20)]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra")
    assert fig.data[0].orientation == "h"
    assert fig.layout.yaxis.dtick == 1
    assert fig.layout.height >= 20 * 26


def test_grouped_bar_has_one_trace_per_series_and_a_legend():
    df = pd.DataFrame({"Campo": ["Casa", "Trasferta"], "Gol fatti": [3, 4], "Gol subiti": [1, 0]})
    fig = charts.grouped_bar(df, "Campo", ["Gol fatti", "Gol subiti"])
    assert [t.name for t in fig.data] == ["Gol fatti", "Gol subiti"]
    assert fig.layout.barmode == "group"
    assert fig.layout.showlegend is True
    assert fig.layout.legend.orientation == "h"
