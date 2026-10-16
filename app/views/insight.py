import streamlit as st

from app import ui
from etl import config


def render():
    ui.hero("Insight", "Osservazioni sui dati, verificate sul database")
    path = config.ROOT / "docs" / "insights.md"
    if not path.exists():
        st.warning("Il file docs/insights.md non è stato trovato.")
        return
    st.markdown(path.read_text(encoding="utf-8"))
