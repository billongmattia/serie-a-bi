# Streamlit – fedeltà stilistica al mockup (M4c) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rifare l'aspetto dell'app Streamlit perché sia **stilisticamente identico al mockup** (`docs/design/mockup-streamlit.webp`): cornice blu scuro con pannelli bianchi, sidebar con logo e icone, intestazione con i selettori dentro, schede KPI con icona, tabella con intestazioni abbreviate e forma a cerchi, ultime partite con badge V/N/P, grafici ad area con sfumatura. **Solo stile**: i dati e le query restano quelli attuali.

**Architecture:** La logica (`app/queries.py`, `app/data.py`) non cambia. Cambia la presentazione: tema chiaro di base con CSS che porta in scuro lo sfondo, la sidebar e l'intestazione; componenti HTML puri e testabili in `app/ui.py` (schede, tabelle, badge, logo) con **escape obbligatorio** dei valori; grafici Plotly in stile chiaro in `app/charts.py`; menu laterale costruito con `st.page_link`. Le pagine vengono riscritte per usare questi pezzi.

**Tech Stack:** Streamlit (container con `key`, `st.page_link`, `st.navigation(position="hidden")`), HTML/CSS iniettato, Plotly (`plotly_white` + `fillgradient`), pytest + `AppTest`.

**Spec:** `docs/superpowers/specs/2026-10-05-serie-a-bi-design.md` (sezione "Frontend Streamlit"). **Riferimento visivo:** `docs/design/mockup-streamlit.webp` (aspetto soltanto: i numeri nel mockup sono inventati).

## Global Constraints

- **Stile identico al mockup, nessun contenuto in più.** Non aggiungere tabelle, pagine, tab, colonne o dati che il dataset non ha: **niente** "Statistiche giocatori", "Partite", tab "Giocatori", "Dettaglio partite", "Confronto", niente barrette colorate per Champions/Europa/retrocessione, niente immagine di stadio (si usano gradienti CSS).
- **I contenuti restano quelli attuali** (stesse pagine e stessi numeri): Home, Classifica, Squadra, Confronti, Disciplina, Insight, About. La logica (`queries.py`, `data.py`) non cambia e i suoi test restano verdi senza modifiche.
- **Escape obbligatorio:** ogni valore che finisce in HTML (nomi delle squadre, stagioni, numeri) passa da `html.escape`. L'HTML non protetto (`ui.Html`) si costruisce solo dentro `app/ui.py` da pezzi già protetti o da costanti. Un test lo verifica.
- Icone: emoji (🏆 ⚽ 🏠 ⚖️ ✈️ 🟨 🟥) dentro cerchi colorati; nessun asset scaricato da internet, nessun font esterno.
- App **solo locale** (`server.address = "localhost"` resta).
- Formati numerici italiani (`1.542`, `2,62`, `45,6%`), colonne in italiano.
- Il codice HTML generato è **su una riga e senza righe vuote né rientri**, perché il Markdown di Streamlit li interpreterebbe come codice.
- Dopo il lavoro: `docs/spiegazioni/11-streamlit-fedelta-mockup.md` in italiano, tono didattico (sezioni **Cosa ho fatto**, **Perché**, **Come funziona (codice spiegato)**, **Come eseguirlo**, **Concetti da studiare**).
- Comandi: PowerShell, dalla radice, con il venv attivo. Messaggi di commit con le righe di attribuzione richieste dall'ambiente. **Non fare `git push`.** Per modificare file di testo usare gli strumenti di modifica, non la shell.

## Specifica di stile (dal mockup)

| Elemento | Come appare nel mockup | Come lo ottengo |
|---|---|---|
| Sfondo pagina | blu notte con riflessi | `.stApp` con gradiente scuro e un alone blu in alto a destra |
| Sidebar | blu notte, logo "SERIE A" (bianco) / "ANALYTICS" (blu), voci con icona, voce attiva su blu pieno, in fondo riga tricolore e dati del database | HTML del logo + `st.page_link` con icone Material, CSS sulla voce attiva, riepilogo del database dal DB |
| Intestazione | fascia blu con forme geometriche, scritta piccola blu "LA SERIE A IN NUMERI!", titolo "SERIE A **ANALYTICS**" (ANALYTICS in blu), sottotitolo, **selettori a destra** (Stagione, Squadra) | `st.container(key="hero")` con CSS (gradiente + triangolo), titolo in HTML, selettori nelle colonne di destra |
| Pannello contenuti | bianco, angoli arrotondati, bordo azzurro chiaro | `st.container(key="panel")` con CSS |
| Titolo del pannello | maiuscolo, pesante ("CLASSIFICA"), sotto un sottotitolo grigio | HTML `panel_title_html` |
| Schede KPI | bianche, bordo chiaro, icona colorata in un cerchio, etichetta grigia, valore grande, nota grigia | `kpi_html` in una griglia CSS |
| Tabella classifica | intestazione grigio chiaro, colonne `Pos Squadra G V N P GF GS DR Punti Ultime 5`, differenza reti con segno, forma a cerchi verdi/grigi/rossi | `standings_html` |
| Ultime partite | righe con barra a sinistra colorata, "Squadra 2 - 0 Avversario", badge circolare V/N/P | `recent_matches_html` |
| Grafici | titolo con icona sopra il grafico, aree blu con sfumatura e etichette, barre blu/rosse, legenda in alto | `card_title_html` + Plotly chiaro |
| Tab | testo con sottolineatura blu sulla voce attiva | tema chiaro di Streamlit con colore primario blu |

## Review Focus

1. **Escape dell'HTML:** un nome di squadra o una stagione con `<`, `>`, `&` o `"` non deve rompere la pagina né iniettare tag. (Task 1)
2. **HTML che il Markdown rovina:** righe vuote o rientri dentro l'HTML trasformano il blocco in codice. Nessun builder deve produrli. (Task 1)
3. **Selettore CSS che non trova nulla** (nomi di classi o attributi di Streamlit che cambiano da versione a versione): la verifica visiva nel browser è obbligatoria, non basta che i test passino. (Task 3–5)
4. **Pagine senza dati** (stagione o squadra vuote): messaggi chiari dentro il pannello, non tracce d'errore. (Task 3–4)
5. **Contrasto del testo:** testo scuro sui pannelli bianchi e chiaro sulle zone scure, ovunque (anche etichette dei selettori nell'intestazione). (Task 3–5)

---

## File Structure

| File | Responsabilità |
|---|---|
| `.streamlit/config.toml` | tema chiaro di base con colore primario blu |
| `app/theme.py` | palette |
| `app/styles.py` | il CSS (una costante) |
| `app/ui.py` | formati italiani, `Html`, builder HTML (scheda, riga di schede, titoli, tabelle, classifica, ultime partite, logo, riepilogo del database), `inject_css`, `hero`, `panel`, `show` |
| `app/charts.py` | grafici Plotly in stile chiaro: area con sfumatura, barre orizzontali, barre raggruppate |
| `app/views/*.py` | le 7 pagine riscritte |
| `app/main.py` | menu laterale con `st.page_link`, navigazione nascosta |
| `tests/test_app_ui.py`, `tests/test_app_charts.py`, `tests/test_app_pages.py` | test aggiornati ai nuovi componenti |

---

### Task 1: Fondamenta – tema, CSS e componenti HTML

**Files:**
- Modify: `.streamlit/config.toml`, `app/theme.py`, `app/ui.py`
- Create: `app/styles.py`
- Test: `tests/test_app_ui.py` (riscritto)

**Interfaces:**
- Produces:
  - `app.theme`: `NAVY, BLUE, RED, YELLOW, GREEN, GREY, INK, MUTED, LINE` (stringhe `#RRGGBB`)
  - `app.styles.CSS: str`
  - `app.ui`: `fmt_number`, `fmt_percent`, `fmt_signed_percent`, `pct_change` (invariate); `Html` (sottoclasse di `str`: HTML fidato); `esc(value) -> str`
  - `kpi_html(icon, label, value, note=None, tone="blue", delta=None, delta_good=True) -> str`
  - `kpi_row_html(cards: list[str]) -> str`
  - `card_title_html(icon: str, text: str) -> str`
  - `panel_title_html(title: str, subtitle: str = "") -> str`
  - `table_html(headers: list[str], rows: list[list], align: list[str] | None = None) -> str` (celle `Html` non vengono protette, tutto il resto sì)
  - `dots_html(results: str) -> Html` (`W`, `D`, `L` → cerchi verdi, grigi, rossi)
  - `standings_html(df) -> str` (colonne `Posizione, Squadra, Partite, Vittorie, Pareggi, Sconfitte, Gol Fatti, Gol Subiti, Diff Reti, Punti, Ultime 5` con `Ultime 5` = lettere)
  - `recent_matches_html(team: str, df) -> str` (colonne `Data, Risultato, Gol fatti, Gol subiti, Avversario`)
  - `logo_html() -> str`, `sidebar_footer_html(seasons: list[str], overview: dict) -> str`, `hero_title_html(subtitle: str) -> str`
  - `inject_css()`, `show(html: str)`, `hero(subtitle: str, selectors: int = 0) -> list`, `panel()`

- [ ] **Step 1: Scrivi i test (sostituiscono `tests/test_app_ui.py`)**

```python
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
        assert f"<th" in html and f">{header}<" in html
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


def test_hero_title_html_has_title_and_escaped_subtitle():
    html = ui.hero_title_html("a <b> c")
    assert "SERIE A" in html and "ANALYTICS" in html
    assert "a &lt;b&gt; c" in html
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_ui.py -q`
Expected: falliscono (mancano `esc`, `kpi_html`, ecc.).

- [ ] **Step 3: Aggiorna `app/theme.py`**

```python
NAVY = "#0A1A3A"
BLUE = "#2563EB"
RED = "#E5484D"
YELLOW = "#F5B301"
GREEN = "#22A559"
GREY = "#9CA3AF"
INK = "#0F1B3D"
MUTED = "#64748B"
LINE = "#E2E8F0"
```

- [ ] **Step 4: Imposta il tema in `.streamlit/config.toml`**

```toml
[server]
# App solo locale: ascolta solo su questo computer, non sulla rete.
address = "localhost"

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#2563EB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F1F5F9"
textColor = "#0F1B3D"
```

- [ ] **Step 5: Scrivi `app/styles.py`**

```python
CSS = """
<style>
/* sfondo e struttura generale */
.stApp { background: radial-gradient(900px 420px at 78% -8%, rgba(37,99,235,.45), transparent 60%), linear-gradient(180deg, #07122B 0%, #0A1A3A 100%); }
header[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display: none !important; }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2rem; }

/* sidebar */
section[data-testid="stSidebar"] { background: #07122B; border-right: 1px solid rgba(255,255,255,.08); }
section[data-testid="stSidebar"] * { color: #E8EEFC; }
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { border-radius: 8px; padding: .45rem .7rem; margin-bottom: .1rem; }
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] { background: #1E5BFF; font-weight: 700; }
.logo { padding: .6rem .4rem 1rem .4rem; line-height: 1; }
.logo .l1 { display: block; font-size: 1.7rem; font-weight: 900; letter-spacing: .01em; color: #FFFFFF; }
.logo .l2 { display: block; font-size: 1.7rem; font-weight: 900; letter-spacing: .01em; background: linear-gradient(90deg, #3B82F6, #22A559); -webkit-background-clip: text; background-clip: text; color: transparent; }
.tricolor { height: 3px; width: 56px; margin: 1.2rem 0 .6rem 0; background: linear-gradient(90deg, #22A559 33%, #FFFFFF 33% 66%, #E5484D 66%); }
.side-foot { font-size: .78rem; line-height: 1.5; opacity: .85; }

/* intestazione */
.st-key-hero { position: relative; overflow: hidden; border-radius: 14px; padding: 1rem 1.4rem; border: 1px solid rgba(80,140,255,.35); background: radial-gradient(500px 220px at 85% 0%, rgba(59,130,246,.55), transparent 70%), linear-gradient(120deg, #07122B 0%, #0B2A6B 100%); }
.st-key-hero::after { content: ""; position: absolute; right: 24px; top: -20px; width: 200px; height: 200px; background: linear-gradient(160deg, rgba(37,99,235,.85), rgba(37,99,235,0) 75%); clip-path: polygon(50% 0, 100% 100%, 0 100%); pointer-events: none; opacity: .5; }
.st-key-hero label, .st-key-hero p, .st-key-hero [data-testid="stWidgetLabel"] * { color: #E8EEFC !important; }
.hero-kicker { font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: #5EA0FF; text-transform: uppercase; }
.hero-title { margin: .1rem 0 .2rem 0; font-size: 2.2rem; font-weight: 900; line-height: 1.05; text-transform: uppercase; color: #FFFFFF; }
.hero-title span { color: #2F7BFF; }
.hero-sub { margin: 0; color: #DCE6FF; font-size: .95rem; }

/* pannello bianco */
.st-key-panel { background: #FFFFFF; border-radius: 12px; border: 1px solid #D6E4FF; padding: 1.2rem 1.4rem; margin-top: .9rem; }
.panel-title { margin: 0; font-size: 1.7rem; font-weight: 900; letter-spacing: .005em; text-transform: uppercase; color: #0F1B3D; }
.panel-sub { margin: .1rem 0 1rem 0; color: #475569; font-size: .92rem; }
.card-title { display: flex; align-items: center; gap: .5rem; font-weight: 800; font-size: 1.02rem; color: #0F1B3D; margin: .2rem 0 .4rem 0; }

/* schede KPI */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .8rem; margin-bottom: 1rem; }
.kpi { display: flex; gap: .7rem; align-items: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: .75rem .85rem; box-shadow: 0 1px 2px rgba(15,27,61,.05); }
.kpi-icon { flex: 0 0 auto; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.kpi-icon.blue { background: #E0EAFF; } .kpi-icon.green { background: #DCFCE7; } .kpi-icon.red { background: #FEE2E2; } .kpi-icon.yellow { background: #FEF3C7; } .kpi-icon.grey { background: #F1F5F9; }
.kpi-label { font-size: .75rem; color: #64748B; }
.kpi-value { font-size: 1.7rem; font-weight: 800; line-height: 1.1; color: #0F1B3D; }
.kpi-note { font-size: .72rem; color: #64748B; }
.kpi-delta { font-size: .78rem; font-weight: 700; }
.kpi-delta.good { color: #15803D; } .kpi-delta.bad { color: #DC2626; }

/* tabelle */
table.tbl { width: 100%; border-collapse: collapse; font-size: .85rem; color: #0F1B3D; }
table.tbl th { background: #F1F5F9; color: #0F1B3D; font-weight: 800; padding: .5rem .5rem; text-align: left; border-bottom: 1px solid #E2E8F0; }
table.tbl td { padding: .38rem .5rem; border-bottom: 1px solid #EEF2F7; }
table.tbl .num { text-align: right; }
table.tbl .pos { font-weight: 800; }
.dots { display: inline-flex; gap: 4px; align-items: center; }
.dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; }
.dot.w { background: #22A559; } .dot.d { background: #9CA3AF; } .dot.l { background: #E5484D; }

/* ultime partite */
.match-row { display: grid; grid-template-columns: 1fr auto 1fr auto; gap: .6rem; align-items: center; border-left: 4px solid #9CA3AF; background: #FFFFFF; padding: .5rem .7rem; margin-bottom: .35rem; border-bottom: 1px solid #EEF2F7; color: #0F1B3D; font-size: .9rem; }
.match-row.w { border-left-color: #22A559; } .match-row.d { border-left-color: #9CA3AF; } .match-row.l { border-left-color: #E5484D; }
.match-score { font-weight: 800; }
.badge { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-weight: 800; font-size: .8rem; }
.badge.w { background: #22A559; } .badge.d { background: #9CA3AF; } .badge.l { background: #E5484D; }
</style>
"""
```

- [ ] **Step 6: Riscrivi `app/ui.py`**

```python
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
```

- [ ] **Step 7: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_ui.py tests/test_streamlit_config.py -q`
Expected: tutti passati. (La suite completa fallirà finché non si aggiornano pagine e grafici nei task successivi: è atteso, non committare finché `test_app_ui.py` non passa; il commit del Task 1 contiene solo i file di questo task e può lasciare rosse le pagine, vedi Step 8.)

- [ ] **Step 8: NON committare ancora**

Le pagine e i grafici esistenti usano ancora le funzioni vecchie (`ui.kpi`, `ui.hero(title, subtitle)`, `charts.*(title=...)`) e falliscono: è previsto. Per non lasciare nella storia di Git commit con la suite rossa, **l'unico commit di questo piano è alla fine del Task 4**, quando tutte le pagine sono migrate e la suite è verde. Tieni le modifiche nel working tree. Registra nel ledger che il Task 1 è completo (`tests/test_app_ui.py` verde) ma non committato.

---

### Task 2: Grafici in stile chiaro

**Files:**
- Modify: `app/charts.py` (riscritto)
- Test: `tests/test_app_charts.py` (riscritto)

**Interfaces:**
- Consumes: `app.theme`.
- Produces (i **titoli non fanno più parte del grafico**: stanno sopra, in `ui.card_title_html`):
  - `rgba(hex_color, alpha) -> str`
  - `area_chart(df, x, y, color=BLUE, fmt=".2f") -> Figure` (linea con marker, etichette, riempimento con sfumatura verticale, asse centrato sui dati)
  - `hbar_chart(df, x, y, color=BLUE, fmt=".2f", height=None) -> Figure` (tutte le etichette, spazio per il valore a destra)
  - `grouped_bar(df, x, ys, colors=None) -> Figure` (legenda in alto)

- [ ] **Step 1: Riscrivi `tests/test_app_charts.py`**

```python
import pandas as pd

from app import charts, theme


def test_rgba():
    assert charts.rgba("#3B82F6", 0.25) == "rgba(59,130,246,0.25)"


def test_area_chart_fills_with_a_vertical_gradient_and_keeps_data():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    fig = charts.area_chart(df, "Stagione", "Gol a Partita")
    trace = fig.data[0]
    assert trace.fill == "tozeroy"
    assert trace.fillgradient.type == "vertical"
    assert list(trace.y) == [2.96, 2.68]
    assert fig.layout.title.text is None  # il titolo sta sopra il grafico, in HTML


def test_area_chart_axis_is_zoomed_on_the_data_not_on_zero():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    low, high = charts.area_chart(df, "Stagione", "Gol a Partita").layout.yaxis.range
    assert 0 < low < 2.68
    assert high > 2.96


def test_area_chart_axis_never_goes_below_zero_for_non_negative_data():
    df = pd.DataFrame({"Stagione": ["a", "b"], "Valore": [0.0, 5.0]})
    assert charts.area_chart(df, "Stagione", "Valore").layout.yaxis.range[0] >= 0


def test_area_chart_handles_a_single_value():
    df = pd.DataFrame({"Stagione": ["2016/17"], "Valore": [3.0]})
    low, high = charts.area_chart(df, "Stagione", "Valore").layout.yaxis.range
    assert low < 3.0 < high


def test_charts_are_light_and_use_italian_separators():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Valore": [1.5, 2.5]})
    fig = charts.area_chart(df, "Stagione", "Valore")
    assert fig.layout.separators == ",."
    assert fig.layout.font.color == theme.INK
    assert fig.layout.paper_bgcolor == "rgba(0,0,0,0)"


def test_hbar_chart_leaves_room_for_the_value_labels():
    df = pd.DataFrame({"Squadra": ["A", "B"], "Gialli": [1.0, 2.0]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra")
    assert fig.layout.xaxis.range[0] == 0
    assert fig.layout.xaxis.range[1] > 2.0


def test_hbar_chart_shows_every_label_and_scales_height():
    df = pd.DataFrame({"Squadra": [f"S{i}" for i in range(20)], "Gialli": [float(i) for i in range(20)]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra")
    assert fig.data[0].orientation == "h"
    assert fig.layout.yaxis.dtick == 1
    assert fig.layout.height >= 20 * 26


def test_grouped_bar_has_one_trace_per_series_and_a_legend():
    df = pd.DataFrame({"Campo": ["Casa", "Trasferta"], "Gol fatti": [3, 4], "Gol subiti": [1, 0]})
    fig = charts.grouped_bar(df, "Campo", ["Gol fatti", "Gol subiti"])
    assert [t.name for t in fig.data] == ["Gol fatti", "Gol subiti"]
    assert fig.layout.barmode == "group"
    assert fig.layout.showlegend is True
    assert fig.layout.legend.orientation == "h"
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_charts.py -q`
Expected: falliscono (la firma attuale richiede `title`, manca `fillgradient`, ecc.).

- [ ] **Step 3: Riscrivi `app/charts.py`**

```python
import plotly.express as px

from app import theme


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _style(fig, height: int = 320, legend: bool = False):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme.INK),
        height=height,
        margin=dict(l=10, r=30, t=30, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""),
        separators=",.",  # formato italiano: virgola decimale, punto per le migliaia
    )
    fig.update_xaxes(showgrid=False, linecolor=theme.LINE)
    fig.update_yaxes(gridcolor=theme.LINE, zeroline=False)
    return fig


def _padded_range(values, low_pad: float = 0.6, high_pad: float = 0.4):
    """Intervallo dell'asse y centrato sui dati (non su zero), con spazio per le etichette."""
    values = [float(v) for v in values]
    low, high = min(values), max(values)
    span = (high - low) or abs(high) * 0.1 or 1.0
    axis_low = low - span * low_pad
    if low >= 0:
        axis_low = max(axis_low, 0.0)
    return [axis_low, high + span * high_pad]


def area_chart(df, x, y, color=theme.BLUE, fmt=".2f"):
    fig = px.line(df, x=x, y=y, markers=True, text=y)
    fig.update_traces(
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[[0, rgba(color, 0.04)], [1, rgba(color, 0.35)]],
        ),
        line_color=color,
        line_width=2.5,
        marker_size=7,
        textposition="top center",
        texttemplate="%{text:" + fmt + "}",
        cliponaxis=False,
    )
    fig.update_yaxes(tickformat=fmt, range=_padded_range(df[y]))
    return _style(fig)


def hbar_chart(df, x, y, color=theme.BLUE, fmt=".2f", height=None):
    height = height or max(320, 26 * len(df) + 90)
    fig = px.bar(df, x=x, y=y, orientation="h", text=x)
    fig.update_traces(
        marker_color=color,
        texttemplate="%{text:" + fmt + "}",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_yaxes(dtick=1, automargin=True)  # tutte le etichette, non una sì e una no
    fig.update_xaxes(range=[0, float(df[x].max()) * 1.18])  # spazio per l'etichetta a destra
    return _style(fig, height)


def grouped_bar(df, x, ys, colors=None):
    colors = colors or [theme.BLUE, theme.RED]
    fig = px.bar(
        df, x=x, y=ys, barmode="group",
        color_discrete_sequence=colors, text_auto=True,
        labels={"value": "", "variable": ""},
    )
    return _style(fig, legend=True)
```

- [ ] **Step 4: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_charts.py -q`
Expected: tutti passati. Se `fillgradient` non è accettato dalla versione installata di Plotly, usa `fillcolor=rgba(color, 0.2)` e registra nel ledger la rinuncia alla sfumatura (e adatta il test a `trace.fillcolor`).

- [ ] **Step 5: NON committare** (come nel Task 1: l'unico commit è alla fine del Task 4). Registra nel ledger.

---

### Task 3: Pagine Home e Classifica

**Files:**
- Modify: `app/ui.py` (aggiunge `dataset_line`), `app/views/home.py`, `app/views/classifica.py`
- Modify: `tests/test_app_ui.py` (aggiunge un test), `tests/test_app_pages.py` (riscritto per le 7 pagine)

**Interfaces:**
- Consumes: tutti i builder di `app.ui` (Task 1), `app.data` (invariato).
- Produces:
  - `app.ui.dataset_line(seasons: list[str], overview: dict) -> str` → es. `10 stagioni • 2016/17 – 2025/26 • 3.800 partite • 34 squadre`
  - `home.render()`, `classifica.render()` con l'aspetto del mockup (intestazione, pannello bianco, schede con icona, tabella con forma a cerchi)

- [ ] **Step 1: Scrivi i test (riscrivono `tests/test_app_pages.py`)**

```python
import pytest
import streamlit as st
from sqlalchemy import create_engine
from streamlit.testing.v1 import AppTest

from app import db

PAGES = {
    "home": "from app.views import home\nhome.render()",
    "classifica": "from app.views import classifica\nclassifica.render()",
    "squadra": "from app.views import squadra\nsquadra.render()",
    "confronti": "from app.views import confronti\nconfronti.render()",
    "disciplina": "from app.views import disciplina\ndisciplina.render()",
    "insight": "from app.views import insight\ninsight.render()",
    "about": "from app.views import about\nabout.render()",
}


@pytest.fixture(autouse=True)
def use_test_warehouse(monkeypatch, warehouse):
    monkeypatch.setattr("app.db.get_engine", lambda: warehouse)
    st.cache_data.clear()


def page_html(at) -> str:
    return " ".join(m.value for m in at.markdown)


def test_check_connection_true_for_a_working_engine(warehouse):
    assert db.check_connection(warehouse) is True


def test_check_connection_false_for_an_unreachable_database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'cartella_che_non_esiste' / 'x.db'}")
    assert db.check_connection(engine) is False


@pytest.mark.parametrize("name", list(PAGES))
def test_page_renders_without_exceptions_and_with_the_hero(name):
    at = AppTest.from_string(PAGES[name]).run(timeout=30)
    assert not at.exception
    html = page_html(at)
    assert "SERIE A" in html and "ANALYTICS" in html  # intestazione del mockup


def test_home_shows_kpis_and_champions_table():
    at = AppTest.from_string(PAGES["home"]).run(timeout=30)
    html = page_html(at)
    assert "Stagioni" in html and "Partite" in html and "Squadre" in html
    assert "Campioni stagione per stagione" in html
    assert html.count(">A</td>") == 2  # il campione è A in entrambe le stagioni di prova


def test_classifica_shows_kpis_table_and_form_dots():
    at = AppTest.from_string(PAGES["classifica"]).run(timeout=30)
    html = page_html(at)
    assert "CLASSIFICA" in html and "Partite giocate" in html
    assert ">Pos<" in html and ">A</td>" in html and ">B</td>" in html
    assert 'class="dot w"' in html and 'class="dot l"' in html
    assert len(at.selectbox) == 1  # il selettore della stagione sta nell'intestazione
```

Aggiungi in fondo a `tests/test_app_ui.py`:
```python
def test_dataset_line():
    overview = {"stagioni": 10, "partite": 3800, "squadre": 34, "osservazioni": 7600, "gol": 10423}
    line = ui.dataset_line(["2025/26", "2016/17"], overview)
    assert line == "10 stagioni • 2016/17 – 2025/26 • 3.800 partite • 34 squadre"
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_pages.py tests/test_app_ui.py -q`
Expected: falliscono `dataset_line` e i test sull'intestazione e su Home/Classifica; quelli di connessione passano. (I test delle altre pagine falliscono finché non si migrano nel Task 4: normale.)

- [ ] **Step 3: Aggiungi `dataset_line` a `app/ui.py`**

```python
def dataset_line(seasons: list[str], overview: dict) -> str:
    span = f"{seasons[-1]} – {seasons[0]}" if seasons else ""
    return (
        f"{overview['stagioni']} stagioni • {span} • "
        f"{fmt_number(overview['partite'])} partite • {overview['squadre']} squadre"
    )
```

- [ ] **Step 4: Riscrivi `app/views/home.py`**

```python
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
```

- [ ] **Step 5: Riscrivi `app/views/classifica.py`**

```python
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
```

- [ ] **Step 6: Esegui i test di Home e Classifica**

Run: `python -m pytest tests/test_app_pages.py tests/test_app_ui.py -q -k "home or classifica or dataset_line or check_connection"`
Expected: passati. Se `at.markdown` non include il markdown dentro i contenitori con chiave, adatta `page_html` (per esempio unendo anche `at.main`/`at.sidebar`) senza perdere lo scopo del test, e registra il motivo nel ledger.

- [ ] **Step 7: NON committare** (l'unico commit è alla fine del Task 4). Registra nel ledger.

---

### Task 4: Squadra, Confronti, Disciplina, Insight, About e menu laterale

**Files:**
- Modify: `app/views/squadra.py`, `app/views/confronti.py`, `app/views/disciplina.py`, `app/views/insight.py`, `app/views/about.py`, `app/main.py`
- Modify: `tests/test_app_pages.py` (aggiunte)

**Interfaces:**
- Consumes: `app.ui`, `app.charts`, `app.theme`, `app.data` (invariato).
- Produces: `squadra.render()` (selettori Stagione e Squadra nell'intestazione, 5 schede, tab Panoramica/Andamento, grafico casa/trasferta e ultime 5 partite con badge V/N/P), `confronti.render()` (selettore del periodo e 4 schede con grafico ad area), `disciplina.render()` (selettore stagione nell'intestazione, 3 tab, barre blu, grafico ad area, 3 schede con variazione), `insight.render()` e `about.render()` nel pannello bianco; `main.py` con il menu laterale (logo, `st.page_link` con icone, riepilogo del database).

- [ ] **Step 1: Aggiungi i test (in fondo a `tests/test_app_pages.py`)**

```python
def test_squadra_shows_selectors_kpis_tabs_and_recent_matches():
    at = AppTest.from_string(PAGES["squadra"]).run(timeout=30)
    html = page_html(at)
    assert len(at.selectbox) == 2  # Stagione e Squadra, nell'intestazione
    assert len(at.tabs) == 2
    assert "Punti" in html and "1° posto" in html and "Ultime 5 partite" in html
    assert 'class="badge w">V<' in html  # A batte B nel 2017/18


def test_confronti_has_a_period_selector_and_four_chart_cards():
    at = AppTest.from_string(PAGES["confronti"]).run(timeout=30)
    html = page_html(at)
    assert len(at.select_slider) == 1
    for title in ("Gol per partita", "Vittorie in casa", "Cartellini gialli per partita", "Cartellini rossi per partita"):
        assert title in html


def test_disciplina_has_three_tabs_and_three_delta_cards():
    at = AppTest.from_string(PAGES["disciplina"]).run(timeout=30)
    html = page_html(at)
    assert len(at.tabs) == 3
    assert len(at.selectbox) == 1
    assert html.count('class="kpi-delta') == 3
    assert "Totale falli stagione" in html


def test_insight_and_about_render_inside_the_panel():
    for name, marker in (("insight", "INSIGHT"), ("about", "ABOUT")):
        at = AppTest.from_string(PAGES[name]).run(timeout=30)
        assert marker in page_html(at)
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: falliscono i test su squadra, confronti, disciplina, insight e about.

- [ ] **Step 3: Riscrivi `app/views/squadra.py`**

```python
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
```

- [ ] **Step 4: Riscrivi `app/views/confronti.py`**

```python
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
```

- [ ] **Step 5: Riscrivi `app/views/disciplina.py`**

```python
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
```

- [ ] **Step 6: Riscrivi `app/views/insight.py` e `app/views/about.py`**

`app/views/insight.py`:
```python
import streamlit as st

from app import ui
from etl import config


def render():
    ui.hero("Osservazioni sui dati, verificate sul database")
    with ui.panel():
        ui.show(ui.panel_title_html("INSIGHT", "Cosa raccontano le dieci stagioni"))
        path = config.ROOT / "docs" / "insights.md"
        if not path.exists():
            st.warning("Il file docs/insights.md non è stato trovato.")
            return
        st.markdown(path.read_text(encoding="utf-8"))
```

`app/views/about.py` (il testo `ABOUT` resta quello attuale):
```python
import streamlit as st

from app import ui

ABOUT = """
**Serie A BI** è un progetto da portfolio di **Mattia Billong** (ITS Business Intelligence Software Developer).

**Come è fatto**
- Un **ETL in Python** (pandas) scarica i risultati di 10 stagioni, li trasforma in uno **star schema** e li carica in **MySQL** (Docker), con controlli di qualità e test automatici.
- La stessa base dati alimenta una **dashboard Power BI** e questa **app Streamlit** con grafici Plotly.
- Le query dell'app sono funzioni testate su un mini-campionato con risultati calcolati a mano.

**Fonte dei dati**
Dataset *Italian Serie A* di [DataHub](https://datahub.io/football/italian-serie-a), derivato da [football-data.co.uk](https://www.football-data.co.uk/), licenza Open Data Commons PDDL (pubblico dominio).

**Limiti**
- Il dataset non contiene gli arbitri né i dati sui giocatori.
- La giornata è ricostruita dall'ordine delle partite.
- Il periodo va da 2016/17 a 2025/26 (stagioni complete).

Codice e documentazione: repository GitHub `billongmattia/serie-a-bi`.
"""


def render():
    ui.hero("Il progetto in breve")
    with ui.panel():
        ui.show(ui.panel_title_html("ABOUT", "Il progetto in breve"))
        st.markdown(ABOUT)
```

- [ ] **Step 7: Riscrivi `app/main.py`**

Prima verifica che `st.navigation` accetti `position="hidden"`:
```powershell
python -c "import inspect, streamlit as st; print(inspect.signature(st.navigation))"
```
Expected: nella firma compare `position`. Se non c'è, usa `st.navigation(pages)` senza il parametro (il CSS già nasconde il menu predefinito) e registra la scelta nel ledger.

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app import data, db, ui  # noqa: E402
from app.views import about, classifica, confronti, disciplina, home, insight, squadra  # noqa: E402

st.set_page_config(page_title="Serie A BI", layout="wide")

if not db.check_connection(db.get_engine()):
    st.error(
        "Database non raggiungibile. Avvia MySQL con `docker compose up -d --wait` "
        "e ricarica la pagina."
    )
    st.stop()

ui.inject_css()

pages = [
    st.Page(home.render, title="Home", icon=":material/home:", default=True),
    st.Page(classifica.render, title="Classifica", icon=":material/format_list_numbered:", url_path="classifica"),
    st.Page(squadra.render, title="Squadra", icon=":material/sports_soccer:", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", icon=":material/bar_chart:", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina", icon=":material/flag:", url_path="disciplina"),
    st.Page(insight.render, title="Insight", icon=":material/lightbulb:", url_path="insight"),
    st.Page(about.render, title="About", icon=":material/info:", url_path="about"),
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    ui.show(ui.logo_html())
    for page in pages:
        st.page_link(page)
    ui.show(ui.sidebar_footer_html(data.seasons(), data.dataset()))

navigation.run()
```

- [ ] **Step 8: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: tutti passati.

- [ ] **Step 9: Suite completa**

Run: `python -m pytest -q`
Expected: tutti verdi (i test di `queries`, `data`, ETL e configurazione restano com'erano). Se qualcosa è rosso, correggilo **prima** di committare.

- [ ] **Step 10: Commit (unico commit di Task 1–4)**

```powershell
git add .streamlit app tests
git commit -m "feat: frontend Streamlit con lo stile del mockup (pannelli bianchi, sidebar, schede, tabelle, grafici chiari)"
```

---

### Task 5: Verifica visiva contro il mockup, documentazione e revisione

**Files:**
- Modify: `README.md`, `docs/milestones/M4c-fedelta-mockup.md`, `docs/milestones/README.md`, `docs/design/README.md` (se serve)
- Create: `docs/spiegazioni/11-streamlit-fedelta-mockup.md`
- Create (a cura dell'utente): `docs/screenshots/streamlit-classifica.png`, `streamlit-squadra.png`, `streamlit-confronti.png`, `streamlit-disciplina.png`

- [ ] **Step 1: Avvia l'app e confronta pagina per pagina con il mockup**

Con MySQL acceso (`docker compose up -d --wait`): `python -m streamlit run app/main.py --server.headless true --server.port 8501` (in background) e apri `http://localhost:8501` con la finestra a 1400 pixel di larghezza. Per **ogni pagina** metti la cattura accanto al riquadro corrispondente del mockup (apri `docs/design/mockup-streamlit.webp`) e controlla questa lista, correggendo il CSS finché ogni voce è soddisfatta:
- **Tutte:** sfondo blu notte con alone in alto a destra; menu laterale con logo "SERIE A / ANALYTICS", icone, voce attiva su blu pieno, riga tricolore e riepilogo del database in fondo (e **nessun** menu predefinito di Streamlit); intestazione con la scritta piccola blu, il titolo "SERIE A ANALYTICS" con "ANALYTICS" in blu, il sottotitolo e il triangolo decorativo; **pannello bianco** con bordo azzurro; nessuna barra superiore di Streamlit.
- **Classifica:** titolo "CLASSIFICA" maiuscolo pesante + sottotitolo; selettore Stagione **nell'intestazione**, a destra; 5 schede bianche con icona in cerchio colorato; tabella con intestazione grigio chiaro e colonne `Pos Squadra G V N P GF GS DR Punti Ultime 5`, `DR` con segno, cerchi verdi/grigi/rossi.
- **Squadra:** due selettori nell'intestazione; schede KPI; tab con sottolineatura blu; grafico casa/trasferta con legenda in alto e barre blu e rosse; "Ultime 5 partite" con barra colorata a sinistra e badge circolari V/N/P.
- **Confronti:** "Periodo" a destra del titolo; quattro schede 2×2 con icona e titolo sopra il grafico; grafici ad area con sfumatura ed etichette.
- **Disciplina:** selettore nell'intestazione; tab Panoramica / Falli / Cartellini; barre blu con il valore a destra e **tutte e 20** le squadre sull'asse; area dei falli; tre schede in fondo con variazione verde.
- **Contrasto:** testo scuro sui pannelli, chiaro sulle zone scure, **anche** le etichette "Stagione" e "Squadra" nell'intestazione.
Se un selettore CSS non trova nulla (per esempio la voce attiva del menu o il contenitore dell'intestazione), ispeziona il DOM con gli strumenti del browser, correggi il selettore in `app/styles.py` e rifai la cattura. Registra nel ledger ogni correzione.

- [ ] **Step 2: Controlla i casi limite**

Squadra con pochi dati (per esempio una squadra con una sola stagione: Home mostra solo i campioni, Squadra mostra l'andamento a un punto), stagione senza dati (messaggio nel pannello), database spento (`docker compose stop`, ricarica: messaggio "Database non raggiungibile"; poi `docker compose up -d --wait`).

- [ ] **Step 3: Screenshot reali (a cura dell'utente)**

Chiedi all'utente di salvare 4 screenshot dell'app (Classifica, Squadra, Confronti, Disciplina) in `docs/screenshots/` con i nomi sopra, ritagliati sulla finestra del browser, senza la scritta "Attiva Windows". Controllali visivamente.

- [ ] **Step 4: README**

Nella sezione dell'app: aggiungi la tabella 2×2 con le immagini, aggiorna il conteggio dei test e rimuovi la voce "Screenshot dell'app Streamlit" dai "Prossimi passi".

- [ ] **Step 5: Spiegazione `docs/spiegazioni/11-streamlit-fedelta-mockup.md`**

Sezioni: perché la prima versione non somigliava al mockup (si erano verificati i numeri ma non l'aspetto: lezione su come si verifica un lavoro di grafica), come si riproduce uno stile in Streamlit (tema chiaro di base + CSS che porta in scuro sfondo, sidebar e intestazione, contenitori con `key`, componenti HTML puri e testabili), perché l'escape è obbligatorio, come si inietta l'HTML senza che il Markdown lo rovini (una riga, niente righe vuote né rientri), cosa è stato lasciato fuori e perché (giocatori, partite, zone Champions: non sono nei dati), e i limiti (icone emoji, nessuna immagine di stadio).

- [ ] **Step 6: Milestone**

Crea `docs/milestones/M4c-fedelta-mockup.md` con le 5 task spuntate e lo stato; aggiungi la riga M4c in `docs/milestones/README.md`.

- [ ] **Step 7: Revisione finale (autore)**

Rileggi il codice nuovo: ogni valore in HTML passa da `esc` o da un builder? Ci sono righe vuote o rientri negli HTML? I messaggi per pagine senza dati ci sono? Il contrasto è giusto ovunque? Il README dice il vero? Correggi con test prima del codice ciò che trovi e registra tutto nel ledger, distinguendo ciò che è corretto da ciò che è rimandato. Dichiara nella risposta finale che è una revisione dell'autore, non di un revisore indipendente.

- [ ] **Step 8: Suite completa e commit**

Run: `python -m pytest -q` (tutti verdi).
```powershell
git add README.md docs app tests
git commit -m "docs: stile del mockup per Streamlit (M4c) verificato e documentato"
```

---

## Self-Review

- **Copertura del mockup:** sfondo, sidebar con logo/icone/voce attiva/riga tricolore/riepilogo del database (Task 1, 4), intestazione con scritta piccola, titolo bicolore, sottotitolo e selettori a destra (Task 1, 3, 4), pannello bianco con titolo maiuscolo (Task 1, 3, 4), schede KPI con icona (Task 1, 3, 4), tabella con intestazioni abbreviate, differenza reti con segno e forma a cerchi (Task 1, 3), ultime partite con badge V/N/P (Task 1, 4), grafici ad area con sfumatura, barre blu/rosse e legenda in alto (Task 2, 4), tab (Task 4), schede con variazione (Task 4). **Fuori, come richiesto:** Statistiche giocatori, Partite, tab Giocatori/Dettaglio partite/Confronto, barrette Champions/retrocessione, immagine di stadio.
- **Review Focus:** escape (test su `esc`, schede, tabelle, classifica, titolo dell'intestazione), niente righe vuote né rientri (test sul builder), selettori CSS (Task 5, verifica visiva obbligatoria), pagine senza dati (messaggi nei pannelli), contrasto (Task 5).
- **Placeholder:** nessuno; la verifica visiva (Task 5) è descritta con una lista di controllo per pagina.
- **Coerenza dei nomi:** firme di `ui` e `charts` uguali in Interfaces, test e pagine; i titoli dei grafici sono passati a `card_title_html`, non più a `charts.*`.
- **Limiti noti:** il codice del piano non è stato eseguito; vanno confermati dai test e dalla verifica visiva la sfumatura (`fillgradient`), i selettori CSS di Streamlit per la voce attiva del menu, `st.navigation(position="hidden")`, `st.container(key=...)` come classe `st-key-...` e il comportamento di `at.markdown` dentro i contenitori.
- **Commit:** unico commit per i Task 1–4 (la suite resta rossa a metà del lavoro per scelta, per non lasciare commit rossi nella storia).

