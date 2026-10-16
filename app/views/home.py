import streamlit as st

from app import data, ui


def render():
    seasons = data.seasons()
    ui.hero("Risultati e statistiche del campionato italiano")
    with ui.panel():
        if not seasons:
            st.warning("Il database non contiene ancora dati: lancia `python -m etl.run_etl`.")
            return
        overview = data.dataset()
        ui.show(ui.panel_title_html("HOME", f"{overview['stagioni']} stagioni, da {seasons[-1]} a {seasons[0]}"))
        ui.show(ui.kpi_row_html([
            ui.kpi_html("📅", "Stagioni", str(overview["stagioni"]), tone="blue"),
            ui.kpi_html("⚽", "Partite", ui.fmt_number(overview["partite"]), tone="green"),
            ui.kpi_html("🛡️", "Squadre", str(overview["squadre"]), tone="grey"),
            ui.kpi_html("🥅", "Gol totali", ui.fmt_number(overview["gol"]),
                        note=f"{ui.fmt_number(overview['gol'] / overview['partite'], 2)} per partita", tone="red"),
        ]))
        ui.show(ui.card_title_html("🏆", "Campioni stagione per stagione"))
        champions = data.champions()
        ui.show(ui.table_html(["Stagione", "Campione", "Punti"], champions.values.tolist(), ["", "", "num"]))
