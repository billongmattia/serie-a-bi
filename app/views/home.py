import streamlit as st

from app import data, ui


def render():
    ui.hero("Serie A Analytics", "Risultati e statistiche del campionato italiano")
    seasons = data.seasons()
    if not seasons:
        st.warning("Il database non contiene ancora dati: lancia `python -m etl.run_etl`.")
        return
    overview = data.dataset()
    st.caption(f"{overview['stagioni']} stagioni, da {seasons[-1]} a {seasons[0]}")
    cols = st.columns(4)
    ui.kpi(cols[0], "Stagioni", str(overview["stagioni"]))
    ui.kpi(cols[1], "Partite", ui.fmt_number(overview["partite"]))
    ui.kpi(cols[2], "Squadre", str(overview["squadre"]))
    ui.kpi(cols[3], "Gol totali", ui.fmt_number(overview["gol"]),
           note=f"{ui.fmt_number(overview['gol'] / overview['partite'], 2)} per partita")
    st.subheader("Campioni stagione per stagione")
    st.dataframe(data.champions(), hide_index=True)
    st.info("Usa il menu a sinistra per esplorare classifica, squadre, confronti tra stagioni e disciplina.")
