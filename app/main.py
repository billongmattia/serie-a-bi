import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app import data, db, ui  # noqa: E402
from app.views import about, classifica, confronti, disciplina, home, insight, squadra  # noqa: E402

st.set_page_config(page_title="Serie A BI", layout="wide")

if not db.check_connection(db.get_engine()):
    st.error(
        "Database non raggiungibile. Avvia MySQL con `docker compose up -d --wait` "
        "e ricarica la pagina."
    )
    st.stop()

ui.inject_css()

pages = [
    st.Page(home.render, title="Home", default=True),
    st.Page(classifica.render, title="Classifica", url_path="classifica"),
    st.Page(squadra.render, title="Squadra", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina e gioco duro", url_path="disciplina"),
    st.Page(insight.render, title="Insight", url_path="insight"),
    st.Page(about.render, title="About", url_path="about"),
]
navigation = st.navigation(pages)

overview = data.dataset()
st.sidebar.caption(
    f"Database: {overview['stagioni']} stagioni, {ui.fmt_number(overview['partite'])} partite, "
    f"{overview['squadre']} squadre, {ui.fmt_number(overview['osservazioni'])} osservazioni"
)
navigation.run()
