import streamlit as st

from app import ui

ABOUT = """
**Serie A BI** è un progetto da portfolio di **Mattia Billong** (ITS Business Intelligence Software Developer).

**Come è fatto**
- Un **ETL in Python** (pandas) scarica i risultati di 10 stagioni, li trasforma in uno **star schema** e li carica in **MySQL** (Docker), con controlli di qualità e test automatici.
- La stessa base dati alimenta una **dashboard Power BI** e questa **app Streamlit** con grafici Plotly.
- Le query dell'app sono funzioni testate su un mini-campionato con risultati calcolati a mano.

**Fonte dei dati**
Dataset *Italian Serie A* di [DataHub](https://datahub.io/football/italian-serie-a), derivato da [football-data.co.uk](https://www.football-data.co.uk/), licenza Open Data Commons PDDL (pubblico dominio).

**Limiti**
- Il dataset non contiene gli arbitri né i dati sui giocatori.
- La giornata è ricostruita dall'ordine delle partite.
- Il periodo va da 2016/17 a 2025/26 (stagioni complete).

Codice e documentazione: repository GitHub `billongmattia/serie-a-bi`.
"""


def render():
    ui.hero("Il progetto in breve")
    with ui.panel():
        ui.show(ui.panel_title_html("ABOUT", "Il progetto in breve"))
        st.markdown(ABOUT)
