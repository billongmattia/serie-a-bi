import streamlit as st

from app import data


def render():
    st.title("Classifica")
    season = st.selectbox("Stagione", data.seasons(), key="classifica_stagione")
    table = data.standings(season)
    if table.empty:
        st.warning("Nessuna partita per questa stagione.")
        return
    st.dataframe(table, hide_index=True)
    st.subheader("Forma recente")
    team = st.selectbox("Squadra", data.teams(season), key="classifica_squadra")
    st.dataframe(data.recent_form(season, team, 5), hide_index=True)
