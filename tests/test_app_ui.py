import pytest
from streamlit.testing.v1 import AppTest

from app import ui


def test_form_dots_maps_results_to_colored_dots():
    assert ui.form_dots("WDL") == "🟢⚪🔴"
    assert ui.form_dots("") == ""
    assert ui.form_dots("WXL") == "🟢🔴"  # simboli sconosciuti ignorati


def test_fmt_number_uses_italian_separators():
    assert ui.fmt_number(1542) == "1.542"
    assert ui.fmt_number(9633) == "9.633"
    assert ui.fmt_number(2.6158, 2) == "2,62"
    assert ui.fmt_number(1234567.891, 1) == "1.234.567,9"
    assert ui.fmt_number(0) == "0"


def test_fmt_percent_and_signed_percent():
    assert ui.fmt_percent(0.4559) == "45,6%"
    assert ui.fmt_percent(0.389, 0) == "39%"
    assert ui.fmt_signed_percent(-0.226) == "-22,6%"
    assert ui.fmt_signed_percent(0.032) == "+3,2%"
    assert ui.fmt_signed_percent(0.0) == "+0,0%"


def test_pct_change():
    assert ui.pct_change(0.8, 1.0) == pytest.approx(-0.2)
    assert ui.pct_change(150, 100) == pytest.approx(0.5)
    assert ui.pct_change(5, 0) is None
    assert ui.pct_change(5, None) is None
    assert ui.pct_change(None, 5) is None


def test_kpi_renders_value_note_and_change():
    script = (
        "import streamlit as st\n"
        "from app import ui\n"
        "cols = st.columns(3)\n"
        "ui.kpi(cols[0], 'Punti', '69')\n"
        "ui.kpi(cols[1], 'Gol', '61', note='2,00 per partita')\n"
        "ui.kpi(cols[2], 'Gialli', '3,70', note='vs 2016/17', change=-0.273)\n"
    )
    at = AppTest.from_string(script).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 3
    assert at.metric[0].value == "69"
    assert at.metric[1].delta == "2,00 per partita"
    assert at.metric[2].delta == "-27,3% vs 2016/17"


def test_hero_renders_title_and_subtitle():
    script = "from app import ui\nui.hero('Classifica', 'Posizioni e punti')\n"
    at = AppTest.from_string(script).run(timeout=30)
    assert not at.exception
    html = " ".join(m.value for m in at.markdown)
    assert "Classifica" in html and "Posizioni e punti" in html
