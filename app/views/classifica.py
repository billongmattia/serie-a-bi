import streamlit as st

from app import data, ui


def render():
    seasons = data.seasons()
    (season_col,) = ui.hero(ui.dataset_line(seasons, data.dataset()), selectors=1)
    season = season_col.selectbox("Stagione", seasons, key="classifica_stagione")
    table = data.standings(season)
    overview = data.overview(season)
    with ui.panel():
        ui.show(ui.panel_title_html("CLASSIFICA", "Posizioni, punti e forma delle squadre nella stagione selezionata"))
        if table.empty or overview is None:
            st.warning("Nessuna partita per questa stagione.")
            return
        matches = overview["partite"]
        ui.show(ui.kpi_row_html([
            ui.kpi_html("🏆", "Partite giocate", ui.fmt_number(matches), tone="yellow"),
            ui.kpi_html("⚽", "Gol totali", ui.fmt_number(overview["gol"]),
                        note=f"{ui.fmt_number(overview['gol_a_partita'], 2)} per partita", tone="blue"),
            ui.kpi_html("🏠", "Vittorie casa", ui.fmt_number(overview["vittorie_casa"]),
                        note=ui.fmt_percent(overview["vittorie_casa"] / matches), tone="green"),
            ui.kpi_html("⚖️", "Pareggi", ui.fmt_number(overview["pareggi"]),
                        note=ui.fmt_percent(overview["pareggi"] / matches), tone="grey"),
            ui.kpi_html("✈️", "Vittorie trasferta", ui.fmt_number(overview["vittorie_trasferta"]),
                        note=ui.fmt_percent(overview["vittorie_trasferta"] / matches), tone="blue"),
        ]))
        form = data.form(season, 5).set_index("Squadra")["Forma"]
        table = table.assign(**{"Ultime 5": table["Squadra"].map(form).fillna("")})
        ui.show(ui.standings_html(table))
