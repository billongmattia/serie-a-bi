import streamlit as st

from app import data, ui


def render():
    ui.hero("Classifica", "Posizioni, punti e forma delle squadre nella stagione selezionata")
    season = st.selectbox("Stagione", data.seasons(), key="classifica_stagione")
    table = data.standings(season)
    overview = data.overview(season)
    if table.empty or overview is None:
        st.warning("Nessuna partita per questa stagione.")
        return
    matches = overview["partite"]
    cols = st.columns(5)
    ui.kpi(cols[0], "Partite giocate", ui.fmt_number(matches))
    ui.kpi(cols[1], "Gol totali", ui.fmt_number(overview["gol"]),
           note=f"{ui.fmt_number(overview['gol_a_partita'], 2)} per partita")
    ui.kpi(cols[2], "Vittorie in casa", ui.fmt_number(overview["vittorie_casa"]),
           note=ui.fmt_percent(overview["vittorie_casa"] / matches))
    ui.kpi(cols[3], "Pareggi", ui.fmt_number(overview["pareggi"]),
           note=ui.fmt_percent(overview["pareggi"] / matches))
    ui.kpi(cols[4], "Vittorie in trasferta", ui.fmt_number(overview["vittorie_trasferta"]),
           note=ui.fmt_percent(overview["vittorie_trasferta"] / matches))
    form = data.form(season, 5).set_index("Squadra")["Forma"]
    table = table.assign(**{"Ultime 5": table["Squadra"].map(form).fillna("").map(ui.form_dots)})
    st.dataframe(table, hide_index=True)
