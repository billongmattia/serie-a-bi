import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Squadra")
    left, right = st.columns(2)
    season = left.selectbox("Stagione", data.seasons(), key="squadra_stagione")
    team = right.selectbox("Squadra", data.teams(season), key="squadra_squadra")
    summary = data.team_summary(season, team)
    if summary is None:
        st.warning("Questa squadra non ha partite nella stagione scelta.")
        return
    cols = st.columns(4)
    cols[0].metric("Punti", summary["punti"])
    cols[1].metric("Gol fatti", summary["gol_fatti"])
    cols[2].metric("Gol subiti", summary["gol_subiti"])
    conversion = summary["conversione_tiri"]
    cols[3].metric("% conversione tiri", "n/d" if conversion is None else f"{conversion:.2%}")
    chart = px.bar(
        data.home_away_points(season, team),
        x="Campo", y="Punti", title="Punti in casa e in trasferta",
    )
    st.plotly_chart(chart)
