import streamlit as st

from app import charts, data, theme, ui

CARDS = (
    ("Falli", "Falli a Partita", "falli"),
    ("Cartellini gialli", "Gialli a Partita", "gialli"),
    ("Cartellini rossi", "Rossi a Partita", "rossi"),
)


def render():
    ui.hero("Disciplina e gioco duro", "Falli, cartellini e fair play")
    season = st.selectbox("Stagione", data.seasons(), key="disciplina_stagione")
    totals = data.discipline_totals(season)
    table = data.discipline(season)
    if totals is None or table.empty:
        st.warning("Nessuna partita per questa stagione.")
        return
    trends = data.trends()
    baseline = trends.iloc[0]
    current = trends[trends["Stagione"] == season]
    cols = st.columns(3)
    for col, (label, per_match_column, key) in zip(cols, CARDS):
        per_match = totals[key] / totals["partite"]
        change = None
        if not current.empty and season != baseline["Stagione"]:
            change = ui.pct_change(float(current.iloc[0][per_match_column]), float(baseline[per_match_column]))
        ui.kpi(
            col,
            f"{label} · {ui.fmt_number(per_match, 2)} a partita",
            ui.fmt_number(totals[key]),
            note=f"vs {baseline['Stagione']}" if change is not None else None,
            change=change,
        )

    overview_tab, fouls_tab, cards_tab = st.tabs(["Panoramica", "Falli", "Cartellini"])
    with overview_tab:
        left, right = st.columns(2)
        left.plotly_chart(
            charts.hbar_chart(table.sort_values("Gialli a Partita"), "Gialli a Partita", "Squadra",
                              "Gialli a partita per squadra", color=theme.YELLOW)
        )
        right.dataframe(table.round(2), hide_index=True)
    with fouls_tab:
        left, right = st.columns(2)
        left.plotly_chart(
            charts.hbar_chart(table.sort_values("Falli a Partita"), "Falli a Partita", "Squadra",
                              "Falli commessi a partita")
        )
        right.plotly_chart(
            charts.area_chart(trends, "Stagione", "Falli a Partita", "Falli a partita per stagione", fmt=".1f")
        )
    with cards_tab:
        left, right = st.columns(2)
        left.plotly_chart(
            charts.area_chart(trends, "Stagione", "Gialli a Partita", "Gialli a partita per stagione",
                              color=theme.YELLOW)
        )
        right.plotly_chart(
            charts.area_chart(trends, "Stagione", "Rossi a Partita", "Rossi a partita per stagione",
                              color=theme.RED)
        )
