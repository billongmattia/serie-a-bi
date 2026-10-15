import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app import db  # noqa: E402
from app.views import classifica, confronti, disciplina, squadra  # noqa: E402

st.set_page_config(page_title="Serie A BI", layout="wide")

if not db.check_connection(db.get_engine()):
    st.error(
        "Database non raggiungibile. Avvia MySQL con `docker compose up -d --wait` "
        "e ricarica la pagina."
    )
    st.stop()

pages = [
    st.Page(classifica.render, title="Classifica", url_path="classifica", default=True),
    st.Page(squadra.render, title="Squadra", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina e gioco duro", url_path="disciplina"),
]
st.navigation(pages).run()
