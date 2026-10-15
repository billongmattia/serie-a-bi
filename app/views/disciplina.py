import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Disciplina e gioco duro")
    season = st.selectbox("Stagione", data.seasons(), key="disciplina_stagione")
    table = data.discipline(season)
    if table.empty:
        st.warning("Nessuna partita per questa stagione.")
        return
    left, right = st.columns(2)
    left.plotly_chart(
        px.bar(
            table.sort_values("Gialli a Partita"),
            x="Gialli a Partita", y="Squadra", orientation="h",
            title="Gialli a partita per squadra",
        )
    )
    right.dataframe(table.round(2), hide_index=True)
    st.plotly_chart(
        px.line(data.trends(), x="Stagione", y="Falli a Partita", markers=True,
                title="Falli a partita per stagione")
    )
