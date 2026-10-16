import pytest
import streamlit as st
from sqlalchemy import create_engine
from streamlit.testing.v1 import AppTest

from app import db
from etl import config

PAGES = {
    "home": "from app.views import home\nhome.render()",
    "classifica": "from app.views import classifica\nclassifica.render()",
    "squadra": "from app.views import squadra\nsquadra.render()",
    "confronti": "from app.views import confronti\nconfronti.render()",
    "disciplina": "from app.views import disciplina\ndisciplina.render()",
    "insight": "from app.views import insight\ninsight.render()",
    "about": "from app.views import about\nabout.render()",
}


@pytest.fixture(autouse=True)
def use_test_warehouse(monkeypatch, warehouse):
    monkeypatch.setattr("app.db.get_engine", lambda: warehouse)
    st.cache_data.clear()


def page_html(at) -> str:
    return " ".join(m.value for m in at.markdown)


def test_check_connection_true_for_a_working_engine(warehouse):
    assert db.check_connection(warehouse) is True


def test_check_connection_false_for_an_unreachable_database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'cartella_che_non_esiste' / 'x.db'}")
    assert db.check_connection(engine) is False


@pytest.mark.parametrize("name", list(PAGES))
def test_page_renders_without_exceptions_and_with_the_hero(name):
    at = AppTest.from_string(PAGES[name]).run(timeout=30)
    assert not at.exception
    html = page_html(at)
    assert "SERIE A" in html and "ANALYTICS" in html  # intestazione del mockup


def test_main_builds_the_sidebar_with_logo_and_database_summary():
    at = AppTest.from_file(str(config.ROOT / "app" / "main.py")).run(timeout=60)
    assert not at.exception
    sidebar = " ".join(m.value for m in at.sidebar.markdown)
    assert "ANALYTICS" in sidebar
    assert "Stagioni nel database" in sidebar and "3 squadre" in sidebar


def test_home_shows_kpis_and_champions_table():
    at = AppTest.from_string(PAGES["home"]).run(timeout=30)
    html = page_html(at)
    assert "Stagioni" in html and "Partite" in html and "Squadre" in html
    assert "Campioni stagione per stagione" in html
    assert html.count(">A</td>") == 2  # il campione è A in entrambe le stagioni di prova


def test_squadra_shows_selectors_kpis_tabs_and_recent_matches():
    at = AppTest.from_string(PAGES["squadra"]).run(timeout=30)
    html = page_html(at)
    assert len(at.selectbox) == 2  # Stagione e Squadra, nell'intestazione
    assert len(at.tabs) == 2
    assert "Punti" in html and "1° posto" in html and "Ultime 5 partite" in html
    assert 'class="badge w">V<' in html  # A batte B nel 2017/18


def test_confronti_has_a_period_selector_and_four_chart_cards():
    at = AppTest.from_string(PAGES["confronti"]).run(timeout=30)
    html = page_html(at)
    assert len(at.select_slider) == 1
    for title in ("Gol per partita", "Vittorie in casa", "Cartellini gialli per partita", "Cartellini rossi per partita"):
        assert title in html


def test_disciplina_has_three_tabs_and_three_delta_cards():
    at = AppTest.from_string(PAGES["disciplina"]).run(timeout=30)
    html = page_html(at)
    assert len(at.tabs) == 3
    assert len(at.selectbox) == 1
    assert html.count('class="kpi-delta') == 3
    assert "Totale falli stagione" in html


def test_insight_and_about_render_inside_the_panel():
    for name, marker in (("insight", "INSIGHT"), ("about", "ABOUT")):
        at = AppTest.from_string(PAGES[name]).run(timeout=30)
        assert marker in page_html(at)


def test_classifica_shows_kpis_table_and_form_dots():
    at = AppTest.from_string(PAGES["classifica"]).run(timeout=30)
    html = page_html(at)
    assert "CLASSIFICA" in html and "Partite giocate" in html
    assert ">Pos<" in html and ">A</td>" in html and ">B</td>" in html
    assert 'class="dot w"' in html and 'class="dot l"' in html
    assert len(at.selectbox) == 1  # il selettore della stagione sta nell'intestazione
