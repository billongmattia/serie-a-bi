import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Confronti tra stagioni")
    trends = data.trends()
    if trends.empty:
        st.warning("Nessun dato disponibile.")
        return
    top_left, top_right = st.columns(2)
    top_left.plotly_chart(
        px.line(trends, x="Stagione", y="Gol a Partita", markers=True, title="Gol a partita")
    )
    wins = px.line(trends, x="Stagione", y="% Vittorie Casa", markers=True, title="% vittorie in casa")
    wins.update_yaxes(tickformat=".0%")
    top_right.plotly_chart(wins)
    bottom_left, bottom_right = st.columns(2)
    bottom_left.plotly_chart(px.bar(trends, x="Stagione", y="Gialli a Partita", title="Gialli a partita"))
    bottom_right.plotly_chart(px.bar(trends, x="Stagione", y="Rossi a Partita", title="Rossi a partita"))
