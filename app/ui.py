import streamlit as st

DOTS = {"W": "🟢", "D": "⚪", "L": "🔴"}

CSS = """
<style>
.hero {
    background: linear-gradient(120deg, #0B1730 0%, #1D4ED8 100%);
    padding: 1.2rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
.hero h1 { margin: 0; padding: 0; font-size: 2rem; letter-spacing: 0.02em; text-transform: uppercase; }
.hero p { margin: 0.2rem 0 0 0; opacity: 0.85; }
</style>
"""


def form_dots(results: str) -> str:
    """Forma recente: 'WDL' diventa pallini colorati (la partita più vecchia a sinistra)."""
    return "".join(DOTS.get(r, "") for r in results)


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


def kpi(container, label: str, value: str, note: str | None = None, change: float | None = None) -> None:
    """Scheda numerica. `note`: riga grigia sotto il valore; `change`: variazione con freccia."""
    if change is not None:
        delta = fmt_signed_percent(change) + (f" {note}" if note else "")
        container.metric(label, value, delta=delta, delta_color="off", border=True)
    elif note is not None:
        container.metric(label, value, delta=note, delta_color="off", delta_arrow="off", border=True)
    else:
        container.metric(label, value, border=True)


def hero(title: str, subtitle: str) -> None:
    # Solo testi fissi scritti nel codice: mai valori letti dal database.
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
