import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app import data, db, ui  # noqa: E402
from app.views import about, classifica, confronti, disciplina, home, insight, squadra  # noqa: E402

st.set_page_config(page_title="Serie A BI", layout="wide")
ui.inject_css()

if not db.check_connection(db.get_engine()):
    st.error(
        "Database non raggiungibile. Avvia MySQL con `docker compose up -d --wait` "
        "e ricarica la pagina."
    )
    st.stop()

pages = [
    st.Page(home.render, title="Home", icon=":material/home:", default=True),
    st.Page(classifica.render, title="Classifica", icon=":material/format_list_numbered:", url_path="classifica"),
    st.Page(squadra.render, title="Squadra", icon=":material/sports_soccer:", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", icon=":material/bar_chart:", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina", icon=":material/flag:", url_path="disciplina"),
    st.Page(insight.render, title="Insight", icon=":material/lightbulb:", url_path="insight"),
    st.Page(about.render, title="About", icon=":material/info:", url_path="about"),
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    ui.show(ui.logo_html())
    for page in pages:
        with st.container(key=ui.nav_container_key(page.url_path, navigation.url_path)):
            st.page_link(page)
    ui.show(ui.sidebar_footer_html(data.seasons(), data.dataset()))

navigation.run()
