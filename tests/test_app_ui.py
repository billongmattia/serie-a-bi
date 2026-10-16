import pandas as pd
import pytest

from app import ui


def test_fmt_number_uses_italian_separators():
    assert ui.fmt_number(1542) == "1.542"
    assert ui.fmt_number(2.6158, 2) == "2,62"
    assert ui.fmt_number(1234567.891, 1) == "1.234.567,9"
    assert ui.fmt_number(0) == "0"


def test_fmt_percent_and_signed_percent():
    assert ui.fmt_percent(0.4559) == "45,6%"
    assert ui.fmt_signed_percent(-0.226) == "-22,6%"
    assert ui.fmt_signed_percent(0.032) == "+3,2%"
    assert ui.fmt_signed_percent(0.0) == "+0,0%"


def test_pct_change():
    assert ui.pct_change(0.8, 1.0) == pytest.approx(-0.2)
    assert ui.pct_change(5, 0) is None
    assert ui.pct_change(5, None) is None
    assert ui.pct_change(None, 5) is None


def test_esc_escapes_html_special_characters():
    assert ui.esc('<b>"A&B"</b>') == "&lt;b&gt;&quot;A&amp;B&quot;&lt;/b&gt;"
    assert ui.esc(42) == "42"


def test_html_builders_never_emit_blank_lines_or_indentation():
    html = ui.kpi_html("🏆", "Punti", "69", note="6° posto", delta="-9,2%")
    html += ui.panel_title_html("CLASSIFICA", "Sottotitolo")
    html += ui.table_html(["A", "B"], [[1, 2], [3, 4]])
    assert "\n" not in html


def test_kpi_html_contains_parts_and_escapes_values():
    html = ui.kpi_html("🏆", "<script>x</script>", "1.542", note="2,62 per partita")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "1.542" in html and "2,62 per partita" in html and "🏆" in html


def test_kpi_html_delta_tone():
    good = ui.kpi_html("🟨", "Gialli", "1.406", delta="-15,9%", delta_good=True)
    bad = ui.kpi_html("🟨", "Gialli", "1.406", delta="+3,0%", delta_good=False)
    assert 'class="kpi-delta good"' in good
    assert 'class="kpi-delta bad"' in bad


def test_kpi_row_wraps_cards():
    html = ui.kpi_row_html([ui.kpi_html("⚽", "Gol", "1"), ui.kpi_html("🏠", "Casa", "2")])
    assert html.startswith('<div class="kpi-row">') and html.count('class="kpi"') == 2


def test_table_html_escapes_cells_but_keeps_trusted_html():
    html = ui.table_html(["Squadra", "Forma"], [["<i>A</i>", ui.dots_html("WDL")]])
    assert "&lt;i&gt;A&lt;/i&gt;" in html
    assert html.count('class="dot ') == 3


def test_dots_html_maps_results_to_colors():
    html = ui.dots_html("WDL")
    assert 'class="dot w"' in html and 'class="dot d"' in html and 'class="dot l"' in html
    assert ui.dots_html("") == ""
    assert ui.dots_html("X") == ""  # simboli sconosciuti ignorati


def test_standings_html_has_abbreviated_headers_signed_difference_and_form():
    df = pd.DataFrame([
        {"Posizione": 1, "Squadra": "Inter", "Partite": 38, "Vittorie": 27, "Pareggi": 6, "Sconfitte": 5,
         "Gol Fatti": 89, "Gol Subiti": 35, "Diff Reti": 54, "Punti": 87, "Ultime 5": "WWDLW"},
        {"Posizione": 2, "Squadra": "Pisa", "Partite": 38, "Vittorie": 2, "Pareggi": 12, "Sconfitte": 24,
         "Gol Fatti": 26, "Gol Subiti": 71, "Diff Reti": -45, "Punti": 18, "Ultime 5": ""},
    ])
    html = ui.standings_html(df)
    for header in ("Pos", "Squadra", "G", "V", "N", "P", "GF", "GS", "DR", "Punti", "Ultime 5"):
        assert f">{header}<" in html
    assert "+54" in html and "-45" in html
    assert html.count('class="dot ') == 5
    assert "Inter" in html and "Pisa" in html


def test_standings_html_escapes_team_names():
    df = pd.DataFrame([{
        "Posizione": 1, "Squadra": "<b>X</b>", "Partite": 1, "Vittorie": 1, "Pareggi": 0, "Sconfitte": 0,
        "Gol Fatti": 1, "Gol Subiti": 0, "Diff Reti": 1, "Punti": 3, "Ultime 5": "W",
    }])
    html = ui.standings_html(df)
    assert "<b>X</b>" not in html and "&lt;b&gt;X&lt;/b&gt;" in html


def test_recent_matches_html_shows_score_opponent_and_badge():
    df = pd.DataFrame([
        {"Data": "2026-05-24", "Risultato": "W", "Gol fatti": 2, "Gol subiti": 0, "Avversario": "Torino"},
        {"Data": "2026-05-17", "Risultato": "D", "Gol fatti": 1, "Gol subiti": 1, "Avversario": "Milan"},
        {"Data": "2026-05-09", "Risultato": "L", "Gol fatti": 0, "Gol subiti": 2, "Avversario": "Roma"},
    ])
    html = ui.recent_matches_html("Inter", df)
    assert "Inter" in html and "2 - 0" in html and "Torino" in html
    assert 'class="badge w">V<' in html
    assert 'class="badge d">N<' in html
    assert 'class="badge l">P<' in html


def test_logo_and_footer_html():
    assert "SERIE A" in ui.logo_html() and "ANALYTICS" in ui.logo_html()
    footer = ui.sidebar_footer_html(
        ["2025/26", "2016/17"],
        {"stagioni": 10, "partite": 3800, "squadre": 34, "osservazioni": 7600, "gol": 10423},
    )
    assert "2016/17 – 2025/26" in footer and "3.800 partite" in footer
    assert "7.600 osservazioni" in footer and "34 squadre" in footer


def test_nav_container_key_marks_only_the_active_page():
    assert ui.nav_container_key("classifica", "classifica") == "nav_active"
    assert ui.nav_container_key("squadra", "classifica") == "nav_squadra"
    assert ui.nav_container_key("", "classifica") == "nav_home"  # la pagina predefinita non ha indirizzo
    assert ui.nav_container_key("", "") == "nav_active"


def test_dataset_line():
    overview = {"stagioni": 10, "partite": 3800, "squadre": 34, "osservazioni": 7600, "gol": 10423}
    line = ui.dataset_line(["2025/26", "2016/17"], overview)
    assert line == "10 stagioni • 2016/17 – 2025/26 • 3.800 partite • 34 squadre"


def test_hero_title_html_has_title_and_escaped_subtitle():
    html = ui.hero_title_html("a <b> c")
    assert "SERIE A" in html and "ANALYTICS" in html
    assert "a &lt;b&gt; c" in html
