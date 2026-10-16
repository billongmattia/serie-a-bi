import streamlit as st

from app import charts, data, theme, ui


def render():
    ui.hero("Confronti tra stagioni", "Principali metriche a confronto nel periodo selezionato")
    trends = data.trends()
    if trends.empty:
        st.warning("Nessun dato disponibile.")
        return
    labels = trends["Stagione"].tolist()
    if len(labels) > 1:
        first, last = st.select_slider(
            "Periodo", options=labels, value=(labels[0], labels[-1]), key="confronti_periodo"
        )
    else:
        first = last = labels[0]
    window = trends[(trends["Stagione"] >= first) & (trends["Stagione"] <= last)]
    top_left, top_right = st.columns(2)
    top_left.plotly_chart(
        charts.area_chart(window, "Stagione", "Gol a Partita", "Gol per partita", fmt=".2f")
    )
    top_right.plotly_chart(
        charts.area_chart(window, "Stagione", "% Vittorie Casa", "Vittorie in casa", fmt=".1%")
    )
    bottom_left, bottom_right = st.columns(2)
    bottom_left.plotly_chart(
        charts.area_chart(window, "Stagione", "Gialli a Partita", "Cartellini gialli per partita",
                          color=theme.YELLOW, fmt=".2f")
    )
    bottom_right.plotly_chart(
        charts.area_chart(window, "Stagione", "Rossi a Partita", "Cartellini rossi per partita",
                          color=theme.RED, fmt=".2f")
    )
