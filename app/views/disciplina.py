import streamlit as st

from app import charts, data, theme, ui


def _change(current, baseline, key, season, baseline_season):
    if current.empty or season == baseline_season:
        return None
    return ui.pct_change(float(current.iloc[0][key]), float(baseline[key]))


def render():
    seasons = data.seasons()
    (season_col,) = ui.hero("Falli, cartellini e fair play", selectors=1)
    season = season_col.selectbox("Stagione", seasons, key="disciplina_stagione")
    totals = data.discipline_totals(season)
    table = data.discipline(season)
    with ui.panel():
        ui.show(ui.panel_title_html("DISCIPLINA", "Falli, cartellini e fair play nella stagione selezionata"))
        if totals is None or table.empty:
            st.warning("Nessuna partita per questa stagione.")
            return
        trends = data.trends()
        baseline = trends.iloc[0]
        current = trends[trends["Stagione"] == season]
        matches = totals["partite"]

        def card(icon, label, key, per_match_column, tone):
            change = _change(current, baseline, per_match_column, season, baseline["Stagione"])
            return ui.kpi_html(
                icon, label, ui.fmt_number(totals[key]),
                note=f"{ui.fmt_number(totals[key] / matches, 2)} per partita", tone=tone,
                delta=None if change is None else f"{ui.fmt_signed_percent(change)} vs {baseline['Stagione']}",
                delta_good=change is None or change <= 0,
            )

        overview_tab, fouls_tab, cards_tab = st.tabs(["Panoramica", "Falli", "Cartellini"])
        with overview_tab:
            left, right = st.columns(2)
            with left, st.container(border=True):
                ui.show(ui.card_title_html("👟", "Falli commessi a partita per squadra"))
                st.plotly_chart(charts.hbar_chart(
                    table.sort_values("Falli a Partita"), "Falli a Partita", "Squadra", color=theme.BLUE))
            with right, st.container(border=True):
                ui.show(ui.card_title_html("📈", "Andamento falli per partita"))
                st.plotly_chart(charts.area_chart(
                    trends, "Stagione", "Falli a Partita", color=theme.BLUE, fmt=".1f"))
            ui.show(ui.kpi_row_html([
                card("👟", "Totale falli stagione", "falli", "Falli a Partita", "grey"),
                card("🟨", "Cartellini gialli", "gialli", "Gialli a Partita", "yellow"),
                card("🟥", "Cartellini rossi", "rossi", "Rossi a Partita", "red"),
            ]))
        with fouls_tab:
            with st.container(border=True):
                ui.show(ui.card_title_html("🛡️", "Falli subiti a partita per squadra"))
                st.plotly_chart(charts.hbar_chart(
                    table.sort_values("Falli Subiti a Partita"), "Falli Subiti a Partita", "Squadra",
                    color=theme.BLUE))
        with cards_tab:
            yellow_col, red_col = st.columns(2)
            with yellow_col, st.container(border=True):
                ui.show(ui.card_title_html("🟨", "Cartellini gialli a partita per squadra"))
                st.plotly_chart(charts.hbar_chart(
                    table.sort_values("Gialli a Partita"), "Gialli a Partita", "Squadra", color=theme.YELLOW))
            with red_col, st.container(border=True):
                ui.show(ui.card_title_html("🟥", "Cartellini rossi a partita per squadra"))
                st.plotly_chart(charts.hbar_chart(
                    table.sort_values("Rossi a Partita"), "Rossi a Partita", "Squadra", color=theme.RED))
