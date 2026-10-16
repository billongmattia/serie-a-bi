import streamlit as st

from app import charts, data, ui


def render():
    ui.hero("Squadra", "Analizza le performance della tua squadra")
    left, right = st.columns(2)
    season = left.selectbox("Stagione", data.seasons(), key="squadra_stagione")
    team = right.selectbox("Squadra", data.teams(season), key="squadra_squadra")
    summary = data.team_summary(season, team)
    standings = data.standings(season)
    rows = standings[standings["Squadra"] == team]
    if summary is None or rows.empty:
        st.warning("Questa squadra non ha partite nella stagione scelta.")
        return
    row = rows.iloc[0]
    matches = int(row["Partite"])
    cols = st.columns(5)
    ui.kpi(cols[0], "Punti", str(summary["punti"]), note=f"{int(row['Posizione'])}° posto")
    ui.kpi(cols[1], "Gol fatti", str(summary["gol_fatti"]),
           note=f"{ui.fmt_number(summary['gol_fatti'] / matches, 2)} per partita")
    ui.kpi(cols[2], "Gol subiti", str(summary["gol_subiti"]),
           note=f"{ui.fmt_number(summary['gol_subiti'] / matches, 2)} per partita")
    ui.kpi(cols[3], "Vittorie", ui.fmt_percent(int(row["Vittorie"]) / matches),
           note=f"{int(row['Vittorie'])} / {matches} partite")
    conversion = summary["conversione_tiri"]
    ui.kpi(cols[4], "Conversione tiri", "n/d" if conversion is None else ui.fmt_percent(conversion))

    overview_tab, trend_tab = st.tabs(["Panoramica", "Andamento"])
    with overview_tab:
        chart_col, form_col = st.columns(2)
        chart_col.plotly_chart(
            charts.grouped_bar(
                data.home_away_goals(season, team), "Campo", ["Gol fatti", "Gol subiti"],
                "Gol fatti e subiti: casa vs trasferta",
            )
        )
        form_col.subheader("Ultime 5 partite")
        recent = data.recent_form(season, team, 5)
        recent = recent.assign(Esito=recent["Risultato"].map(ui.DOTS))
        form_col.dataframe(
            recent[["Data", "Esito", "Gol fatti", "Gol subiti", "Avversario"]], hide_index=True
        )
    with trend_tab:
        history = data.team_history(team)
        st.plotly_chart(
            charts.area_chart(history, "Stagione", "Punti", f"Punti per stagione: {team}", fmt=".0f")
        )
        st.plotly_chart(
            charts.grouped_bar(
                history, "Stagione", ["Gol fatti", "Gol subiti"],
                f"Gol fatti e subiti per stagione: {team}",
            )
        )
