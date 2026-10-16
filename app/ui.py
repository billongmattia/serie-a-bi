from html import escape

import streamlit as st

from app.styles import CSS

RESULT_CLASS = {"W": "w", "D": "d", "L": "l"}
RESULT_BADGE = {"W": "V", "D": "N", "L": "P"}


class Html(str):
    """Testo HTML fidato: non viene protetto di nuovo. Si crea solo dentro questo modulo."""


def esc(value) -> str:
    return escape(str(value), quote=True)


def fmt_number(value, decimals: int = 0) -> str:
    """Formato italiano: 1.542 e 2,62."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_percent(fraction, decimals: int = 1) -> str:
    return fmt_number(fraction * 100, decimals) + "%"


def fmt_signed_percent(fraction, decimals: int = 1) -> str:
    return f"{fraction * 100:+.{decimals}f}%".replace(".", ",")


def pct_change(new, old):
    """Variazione di `new` rispetto a `old` come frazione; None se non calcolabile."""
    if new is None or old is None or old == 0:
        return None
    return (new - old) / old


def _cell(value) -> str:
    return str(value) if isinstance(value, Html) else esc(value)


def kpi_html(icon, label, value, note=None, tone="blue", delta=None, delta_good=True) -> str:
    note_html = f'<div class="kpi-note">{esc(note)}</div>' if note else ""
    delta_class = "good" if delta_good else "bad"
    delta_html = f'<div class="kpi-delta {delta_class}">{esc(delta)}</div>' if delta else ""
    return (
        f'<div class="kpi"><div class="kpi-icon {esc(tone)}">{esc(icon)}</div>'
        f'<div class="kpi-body"><div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{esc(value)}</div>{note_html}{delta_html}</div></div>'
    )


def kpi_row_html(cards: list[str]) -> str:
    return '<div class="kpi-row">' + "".join(cards) + "</div>"


def card_title_html(icon: str, text: str) -> str:
    return f'<div class="card-title"><span>{esc(icon)}</span><span>{esc(text)}</span></div>'


def panel_title_html(title: str, subtitle: str = "") -> str:
    sub = f'<div class="panel-sub">{esc(subtitle)}</div>' if subtitle else ""
    return f'<div class="panel-title">{esc(title)}</div>{sub}'


def table_html(headers: list[str], rows: list[list], align: list[str] | None = None) -> str:
    align = align or ["" for _ in headers]
    head = "".join(f'<th class="{a}">{esc(h)}</th>' for h, a in zip(headers, align))
    body = "".join(
        "<tr>" + "".join(f'<td class="{a}">{_cell(c)}</td>' for c, a in zip(row, align)) + "</tr>"
        for row in rows
    )
    return f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def dots_html(results: str) -> Html:
    dots = "".join(
        f'<span class="dot {RESULT_CLASS[r]}"></span>' for r in results if r in RESULT_CLASS
    )
    return Html(f'<span class="dots">{dots}</span>' if dots else "")


def standings_html(df) -> str:
    headers = ["Pos", "Squadra", "G", "V", "N", "P", "GF", "GS", "DR", "Punti", "Ultime 5"]
    align = ["num pos", "", "num", "num", "num", "num", "num", "num", "num", "num pos", ""]
    rows = []
    for _, r in df.iterrows():
        diff = int(r["Diff Reti"])
        rows.append([
            int(r["Posizione"]), r["Squadra"], int(r["Partite"]), int(r["Vittorie"]),
            int(r["Pareggi"]), int(r["Sconfitte"]), int(r["Gol Fatti"]), int(r["Gol Subiti"]),
            f"{diff:+d}" if diff else "0", int(r["Punti"]), dots_html(r["Ultime 5"]),
        ])
    return table_html(headers, rows, align)


def recent_matches_html(team: str, df) -> str:
    rows = []
    for _, r in df.iterrows():
        cls = RESULT_CLASS.get(r["Risultato"], "d")
        badge = RESULT_BADGE.get(r["Risultato"], "N")
        rows.append(
            f'<div class="match-row {cls}"><span>{esc(team)}</span>'
            f'<span class="match-score">{esc(int(r["Gol fatti"]))} - {esc(int(r["Gol subiti"]))}</span>'
            f'<span>{esc(r["Avversario"])}</span><span class="badge {cls}">{badge}</span></div>'
        )
    return "".join(rows)


def logo_html() -> str:
    return '<div class="logo"><span class="l1">SERIE A</span><span class="l2">ANALYTICS</span></div>'


def sidebar_footer_html(seasons: list[str], overview: dict) -> str:
    span = f"{seasons[-1]} – {seasons[0]}" if seasons else ""
    lines = [
        "Stagioni nel database",
        span,
        f"{fmt_number(overview['partite'])} partite",
        f"{fmt_number(overview['osservazioni'])} osservazioni",
        f"{overview['squadre']} squadre",
    ]
    body = "<br>".join(esc(line) for line in lines)
    return f'<div class="tricolor"></div><div class="side-foot">{body}</div>'


def nav_container_key(url_path: str, active_url_path: str) -> str:
    """Chiave del contenitore di una voce del menu: la voce attiva si distingue per il CSS."""
    if url_path == active_url_path:
        return "nav_active"
    return f"nav_{url_path or 'home'}"


def dataset_line(seasons: list[str], overview: dict) -> str:
    span = f"{seasons[-1]} – {seasons[0]}" if seasons else ""
    return (
        f"{overview['stagioni']} stagioni • {span} • "
        f"{fmt_number(overview['partite'])} partite • {overview['squadre']} squadre"
    )


def hero_title_html(subtitle: str) -> str:
    return (
        '<div class="hero-kicker">LA SERIE A IN NUMERI!</div>'
        '<div class="hero-title">SERIE A <span>ANALYTICS</span></div>'
        f'<p class="hero-sub">{esc(subtitle)}</p>'
    )


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def show(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def hero(subtitle: str, selectors: int = 0) -> list:
    """Intestazione con i selettori a destra. Restituisce le colonne dei selettori."""
    with st.container(key="hero"):
        columns = st.columns([3] + [1] * selectors) if selectors else st.columns([1])
        with columns[0]:
            show(hero_title_html(subtitle))
    return list(columns[1:])


def panel():
    """Pannello bianco dei contenuti: da usare con `with ui.panel():`."""
    return st.container(key="panel")
