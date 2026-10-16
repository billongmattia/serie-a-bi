import streamlit as st

from app import ui
from etl import config


def render():
    ui.hero("Osservazioni sui dati, verificate sul database")
    with ui.panel():
        ui.show(ui.panel_title_html("INSIGHT", "Cosa raccontano le dieci stagioni"))
        path = config.ROOT / "docs" / "insights.md"
        if not path.exists():
            st.warning("Il file docs/insights.md non è stato trovato.")
            return
        st.markdown(path.read_text(encoding="utf-8"))
