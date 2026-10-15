import pytest
import streamlit as st
from sqlalchemy import create_engine
from streamlit.testing.v1 import AppTest

from app import db

PAGES = {
    "classifica": "from app.views import classifica\nclassifica.render()",
    "squadra": "from app.views import squadra\nsquadra.render()",
    "confronti": "from app.views import confronti\nconfronti.render()",
    "disciplina": "from app.views import disciplina\ndisciplina.render()",
}


@pytest.fixture(autouse=True)
def use_test_warehouse(monkeypatch, warehouse):
    monkeypatch.setattr("app.db.get_engine", lambda: warehouse)
    st.cache_data.clear()


def test_check_connection_true_for_a_working_engine(warehouse):
    assert db.check_connection(warehouse) is True


def test_check_connection_false_for_an_unreachable_database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'cartella_che_non_esiste' / 'x.db'}")
    assert db.check_connection(engine) is False


@pytest.mark.parametrize("name", list(PAGES))
def test_page_renders_without_exceptions(name):
    at = AppTest.from_string(PAGES[name]).run(timeout=30)
    assert not at.exception


def test_classifica_shows_the_standings_table():
    at = AppTest.from_string(PAGES["classifica"]).run(timeout=30)
    assert len(at.dataframe) >= 1


def test_squadra_shows_four_metrics():
    at = AppTest.from_string(PAGES["squadra"]).run(timeout=30)
    assert len(at.metric) == 4
