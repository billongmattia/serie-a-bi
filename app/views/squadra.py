import streamlit as st

from app import charts, data, theme, ui


def render():
    seasons = data.seasons()
    season_col, team_col = ui.hero("Analizza le performance della tua squadra", selectors=2)
    season = season_col.selectbox("Stagione", seasons, key="squadra_stagione")
    team = team_col.selectbox("Squadra", data.teams(season), key="squadra_squadra")
    summary = data.team_summary(season, team)
    standings = data.standings(season)
    rows = standings[standings["Squadra"] == team]
    with ui.panel():
        if summary is None or rows.empty:
            st.warning("Questa squadra non ha partite nella stagione scelta.")
            return
        row = rows.iloc[0]
        matches = int(row["Partite"])
        wins = int(row["Vittorie"])
        conversion = summary["conversione_tiri"]
        ui.show(ui.kpi_row_html([
            ui.kpi_html("🏆", "Punti", str(summary["punti"]), note=f"{int(row['Posizione'])}° posto", tone="yellow"),
            ui.kpi_html("⚽", "Gol fatti", str(summary["gol_fatti"]),
                        note=f"{ui.fmt_number(summary['gol_fatti'] / matches, 2)} per partita", tone="green"),
            ui.kpi_html("🥅", "Gol subiti", str(summary["gol_subiti"]),
                        note=f"{ui.fmt_number(summary['gol_subiti'] / matches, 2)} per partita", tone="red"),
            ui.kpi_html("📊", "% Vittorie", ui.fmt_percent(wins / matches),
                        note=f"{wins} / {matches} partite", tone="blue"),
            ui.kpi_html("🎯", "Conversione tiri", "n/d" if conversion is None else ui.fmt_percent(conversion),
                        tone="grey"),
        ]))
        overview_tab, trend_tab = st.tabs(["Panoramica", "Andamento"])
        with overview_tab:
            chart_col, form_col = st.columns([3, 2])
            with chart_col, st.container(border=True):
                ui.show(ui.card_title_html("⚽", "Gol fatti e subiti: casa vs trasferta"))
                st.plotly_chart(charts.grouped_bar(
                    data.home_away_goals(season, team), "Campo", ["Gol fatti", "Gol subiti"]))
            with form_col, st.container(border=True):
                ui.show(ui.card_title_html("📋", "Ultime 5 partite"))
                ui.show(ui.recent_matches_html(team, data.recent_form(season, team, 5)))
        with trend_tab:
            history = data.team_history(team)
            points_col, goals_col = st.columns(2)
            with points_col, st.container(border=True):
                ui.show(ui.card_title_html("🏆", f"Punti per stagione: {team}"))
                st.plotly_chart(charts.area_chart(history, "Stagione", "Punti", color=theme.BLUE, fmt=".0f"))
            with goals_col, st.container(border=True):
                ui.show(ui.card_title_html("⚽", f"Gol fatti e subiti per stagione: {team}"))
                st.plotly_chart(charts.grouped_bar(history, "Stagione", ["Gol fatti", "Gol subiti"]))
