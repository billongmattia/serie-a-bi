import streamlit as st

from app import charts, data, theme, ui

CARDS = (
    ("⚽", "Gol per partita", "Gol a Partita", theme.BLUE, ".2f"),
    ("🏠", "Vittorie in casa", "% Vittorie Casa", theme.BLUE, ".1%"),
    ("🟨", "Cartellini gialli per partita", "Gialli a Partita", theme.YELLOW, ".2f"),
    ("🟥", "Cartellini rossi per partita", "Rossi a Partita", theme.RED, ".2f"),
)


def render():
    trends = data.trends()
    seasons = data.seasons()
    ui.hero(f"Come è cambiata la Serie A negli ultimi {len(seasons)} anni")
    with ui.panel():
        title_col, period_col = st.columns([3, 2])
        with title_col:
            ui.show(ui.panel_title_html(
                "CONFRONTI TRA STAGIONI",
                f"Principali metriche a confronto dal {seasons[-1]} al {seasons[0]}" if seasons else "",
            ))
        if trends.empty:
            st.warning("Nessun dato disponibile.")
            return
        labels = trends["Stagione"].tolist()
        if len(labels) > 1:
            first, last = period_col.select_slider(
                "Periodo", options=labels, value=(labels[0], labels[-1]), key="confronti_periodo"
            )
        else:
            first = last = labels[0]
        window = trends[(trends["Stagione"] >= first) & (trends["Stagione"] <= last)]
        for start in (0, 2):
            columns = st.columns(2)
            for column, (icon, title, field, color, fmt) in zip(columns, CARDS[start:start + 2]):
                with column, st.container(border=True):
                    ui.show(ui.card_title_html(icon, title))
                    st.plotly_chart(charts.area_chart(window, "Stagione", field, color=color, fmt=fmt))
