# Streamlit – veste grafica (M4b) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dare all'app Streamlit esistente l'aspetto del mockup (tema scuro, schede KPI, forma recente a pallini, tab, grafici ad area con etichette) e aggiungere le pagine Home, Insight e About, **senza cambiare la logica già testata** e con numeri sempre calcolati dal database.

**Architecture:** Tre moduli nuovi di sola presentazione (`app/theme.py` colori, `app/ui.py` componenti e formati italiani, `app/charts.py` grafici Plotly) e alcune query nuove in `app/queries.py` (testate su SQLite come le precedenti). Le pagine in `app/views/` vengono riscritte usando questi moduli; `app/main.py` aggiunge CSS, sidebar e le nuove pagine.

**Tech Stack:** Streamlit (con `st.metric(border=True)`, `st.tabs`, `st.select_slider`), Plotly (`plotly_dark`), pandas, pytest + `AppTest`.

**Spec:** `docs/superpowers/specs/2026-10-05-serie-a-bi-design.md` (sezione "Frontend Streamlit"). **Riferimento visivo:** `docs/design/mockup-streamlit.webp` (aspetto soltanto: i suoi numeri sono inventati).

## Global Constraints

- **Nessun numero scritto a mano nelle pagine**: tutto viene dal database tramite `app/queries.py`.
- **La logica già esistente non cambia**: le firme e i risultati delle funzioni di `app/queries.py` e `app/data.py` esistenti restano identici (i test esistenti devono restare verdi senza modifiche).
- App **solo locale** (`.streamlit/config.toml` mantiene `server.address = "localhost"`), nessun asset esterno (niente immagini, font o script scaricati da internet).
- **Niente dati dei giocatori, niente zone Champions/Europa/retrocessione, niente immagine di stadio** (fuori perimetro, vedi `docs/design/README.md`).
- `unsafe_allow_html` solo per testi **fissi scritti nel codice**, mai per valori letti dal database.
- Formati numerici **italiani**: `1.542` (migliaia con punto), `2,62` (decimali con virgola), `45,6%`.
- Colonne e tabelle dei risultati in **italiano**.
- Dopo il lavoro: `docs/spiegazioni/10-streamlit-veste-grafica.md` in italiano, tono didattico (sezioni **Cosa ho fatto**, **Perché**, **Come funziona (codice spiegato)**, **Come eseguirlo**, **Concetti da studiare**).
- Comandi: PowerShell, dalla radice del progetto, con il venv attivo. Messaggi di commit con le righe di attribuzione richieste dall'ambiente. **Non fare `git push`** (lo fa l'utente).
- Evitare nei comandi di shell le espressioni che un controllo di sicurezza può scambiare per cancellazioni: per modificare file di testo usare gli strumenti di modifica, non la shell.

## Review Focus

1. **Variazione percentuale con base zero o mancante** (`pct_change`): niente divisione per zero, niente "nan%". (Task 1)
2. **Formato italiano dei numeri**: migliaia e decimali non devono invertirsi né perdere cifre (1.542 / 2,62 / 45,6%). (Task 1)
3. **Forma recente con meno di 5 partite o squadra senza partite**: la colonna non si rompe. (Task 2 e 3)
4. **Stagione o squadra senza dati**: ogni pagina mostra un messaggio, non una traccia d'errore. (Task 3 e 4)
5. **Tutte le etichette dei grafici a barre orizzontali visibili** (20 squadre), non una sì e una no. (Task 1 e 4)
6. **HTML**: l'intestazione usa `unsafe_allow_html` solo con testi fissi. (Task 1)

---

## File Structure

| File | Responsabilità |
|---|---|
| `.streamlit/config.toml` | tema scuro (resta `server.address = "localhost"`) |
| `app/theme.py` | costanti dei colori |
| `app/ui.py` | formati italiani, `form_dots`, `pct_change`, `kpi`, `hero`, `inject_css` |
| `app/charts.py` | grafici Plotly: area con etichette, barre orizzontali, barre raggruppate |
| `app/queries.py` | + `season_overview`, `form_by_team`, `home_away_goals`, `team_points_by_season`, `discipline_totals`, `dataset_overview`, `champions` |
| `app/data.py` | + involucri con cache delle nuove query |
| `app/views/classifica.py`, `squadra.py`, `confronti.py`, `disciplina.py` | riscritte con la nuova veste |
| `app/views/home.py`, `insight.py`, `about.py` | pagine nuove |
| `app/main.py` | CSS, sidebar, 7 pagine in navigazione |
| `tests/test_app_ui.py`, `tests/test_app_charts.py` | test di formati, componenti, grafici |
| `tests/test_app_queries.py` | + test delle query nuove |
| `tests/test_app_pages.py` | smoke test delle 7 pagine |

---

### Task 1: Tema, componenti e grafici

**Files:**
- Modify: `.streamlit/config.toml`, `requirements.txt` (solo se serve, vedi Step 1)
- Create: `app/theme.py`, `app/ui.py`, `app/charts.py`
- Test: `tests/test_app_ui.py`, `tests/test_app_charts.py`

**Interfaces:**
- Produces:
  - `app.theme`: `BLUE, RED, YELLOW, GREEN, GREY` (stringhe `#RRGGBB`)
  - `app.ui.DOTS: dict[str, str]` (`W`→🟢, `D`→⚪, `L`→🔴)
  - `app.ui.form_dots(results: str) -> str`
  - `app.ui.fmt_number(value, decimals: int = 0) -> str`, `fmt_percent(fraction, decimals: int = 1) -> str`, `fmt_signed_percent(fraction, decimals: int = 1) -> str`
  - `app.ui.pct_change(new, old) -> float | None`
  - `app.ui.kpi(container, label: str, value: str, note: str | None = None, change: float | None = None) -> None`
  - `app.ui.hero(title: str, subtitle: str) -> None`, `app.ui.inject_css() -> None`
  - `app.charts.area_chart(df, x, y, title, color=BLUE, fmt=".2f") -> Figure`
  - `app.charts.hbar_chart(df, x, y, title, color=BLUE, fmt=".2f", height=None) -> Figure`
  - `app.charts.grouped_bar(df, x, ys: list[str], title, colors=None) -> Figure`
  - `app.charts.rgba(hex_color: str, alpha: float) -> str`

- [ ] **Step 1: Verifica che `st.metric` abbia i parametri che servono**

```powershell
python -c "import inspect, streamlit as st; p = inspect.signature(st.metric).parameters; print([k for k in ('border', 'delta_color', 'delta_arrow') if k in p])"
```
Expected: `['border', 'delta_color', 'delta_arrow']`. Se manca `delta_arrow`, usa in `kpi` solo `delta_color="off"` (Step 4) e registra la scelta nel ledger. Se manca `border`, aggiorna Streamlit (`pip install -U streamlit`) e porta il minimo in `requirements.txt` alla versione che li ha.

- [ ] **Step 2: Scrivi i test di `ui`**

`tests/test_app_ui.py`:
```python
import pytest
from streamlit.testing.v1 import AppTest

from app import ui


def test_form_dots_maps_results_to_colored_dots():
    assert ui.form_dots("WDL") == "🟢⚪🔴"
    assert ui.form_dots("") == ""
    assert ui.form_dots("WXL") == "🟢🔴"  # simboli sconosciuti ignorati


def test_fmt_number_uses_italian_separators():
    assert ui.fmt_number(1542) == "1.542"
    assert ui.fmt_number(9633) == "9.633"
    assert ui.fmt_number(2.6158, 2) == "2,62"
    assert ui.fmt_number(1234567.891, 1) == "1.234.567,9"
    assert ui.fmt_number(0) == "0"


def test_fmt_percent_and_signed_percent():
    assert ui.fmt_percent(0.4559) == "45,6%"
    assert ui.fmt_percent(0.389, 0) == "39%"
    assert ui.fmt_signed_percent(-0.226) == "-22,6%"
    assert ui.fmt_signed_percent(0.032) == "+3,2%"
    assert ui.fmt_signed_percent(0.0) == "+0,0%"


def test_pct_change():
    assert ui.pct_change(0.8, 1.0) == pytest.approx(-0.2)
    assert ui.pct_change(150, 100) == pytest.approx(0.5)
    assert ui.pct_change(5, 0) is None
    assert ui.pct_change(5, None) is None
    assert ui.pct_change(None, 5) is None


def test_kpi_renders_value_note_and_change():
    script = (
        "import streamlit as st\n"
        "from app import ui\n"
        "cols = st.columns(3)\n"
        "ui.kpi(cols[0], 'Punti', '69')\n"
        "ui.kpi(cols[1], 'Gol', '61', note='2,00 per partita')\n"
        "ui.kpi(cols[2], 'Gialli', '3,70', note='vs 2016/17', change=-0.273)\n"
    )
    at = AppTest.from_string(script).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 3
    assert at.metric[0].value == "69"
    assert at.metric[1].delta == "2,00 per partita"
    assert at.metric[2].delta == "-27,3% vs 2016/17"


def test_hero_renders_title_and_subtitle():
    script = "from app import ui\nui.hero('Classifica', 'Posizioni e punti')\n"
    at = AppTest.from_string(script).run(timeout=30)
    assert not at.exception
    html = " ".join(m.value for m in at.markdown)
    assert "Classifica" in html and "Posizioni e punti" in html
```

- [ ] **Step 3: Scrivi i test dei grafici**

`tests/test_app_charts.py`:
```python
import pandas as pd
import pytest

from app import charts


def test_rgba():
    assert charts.rgba("#3B82F6", 0.25) == "rgba(59,130,246,0.25)"


def test_area_chart_fills_to_zero_and_keeps_data():
    df = pd.DataFrame({"Stagione": ["2016/17", "2017/18"], "Gol a Partita": [2.96, 2.68]})
    fig = charts.area_chart(df, "Stagione", "Gol a Partita", "Gol a partita")
    trace = fig.data[0]
    assert trace.fill == "tozeroy"
    assert list(trace.y) == [2.96, 2.68]
    assert fig.layout.title.text == "Gol a partita"


def test_hbar_chart_shows_every_label_and_scales_height():
    df = pd.DataFrame({"Squadra": [f"S{i}" for i in range(20)], "Gialli": [float(i) for i in range(20)]})
    fig = charts.hbar_chart(df, "Gialli", "Squadra", "Gialli per squadra")
    assert fig.data[0].orientation == "h"
    assert fig.layout.yaxis.dtick == 1
    assert fig.layout.height >= 20 * 26


def test_grouped_bar_has_one_trace_per_series():
    df = pd.DataFrame({"Campo": ["Casa", "Trasferta"], "Gol fatti": [3, 4], "Gol subiti": [1, 0]})
    fig = charts.grouped_bar(df, "Campo", ["Gol fatti", "Gol subiti"], "Casa vs trasferta")
    assert [t.name for t in fig.data] == ["Gol fatti", "Gol subiti"]
    assert fig.layout.barmode == "group"
```
(`pytest` è importato per coerenza; se non serve, rimuovi l'import inutilizzato.)

- [ ] **Step 4: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_ui.py tests/test_app_charts.py -q`
Expected: errori di collezione (`ImportError: cannot import name 'ui'` / `'charts'`).

- [ ] **Step 5: Implementa `app/theme.py`**

```python
BLUE = "#3B82F6"
RED = "#EF4444"
YELLOW = "#FBBF24"
GREEN = "#22C55E"
GREY = "#94A3B8"
```

- [ ] **Step 6: Implementa `app/ui.py`**

```python
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
```

- [ ] **Step 7: Implementa `app/charts.py`**

```python
import plotly.express as px

from app import theme


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _style(fig, height: int = 320):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=16,
        legend_title_text="",
    )
    return fig


def area_chart(df, x, y, title, color=theme.BLUE, fmt=".2f"):
    fig = px.line(df, x=x, y=y, title=title, markers=True, text=y)
    fig.update_traces(
        fill="tozeroy",
        line_color=color,
        fillcolor=rgba(color, 0.25),
        textposition="top center",
        texttemplate="%{text:" + fmt + "}",
    )
    fig.update_yaxes(tickformat=fmt)
    return _style(fig)


def hbar_chart(df, x, y, title, color=theme.BLUE, fmt=".2f", height=None):
    height = height or max(320, 26 * len(df) + 90)
    fig = px.bar(df, x=x, y=y, orientation="h", title=title, text=x)
    fig.update_traces(marker_color=color, texttemplate="%{text:" + fmt + "}", textposition="outside")
    fig.update_yaxes(dtick=1, automargin=True)  # tutte le etichette, non una sì e una no
    return _style(fig, height)


def grouped_bar(df, x, ys, title, colors=None):
    colors = colors or [theme.BLUE, theme.RED]
    fig = px.bar(
        df, x=x, y=ys, barmode="group", title=title,
        color_discrete_sequence=colors, text_auto=True,
        labels={"value": "", "variable": ""},
    )
    return _style(fig)
```

- [ ] **Step 8: Imposta il tema in `.streamlit/config.toml`**

Il file diventa (la sezione `[server]` resta com'è):
```toml
[server]
# App solo locale: ascolta solo su questo computer, non sulla rete.
address = "localhost"

[browser]
gatherUsageStats = false

[theme]
base = "dark"
primaryColor = "#3B82F6"
backgroundColor = "#0B1730"
secondaryBackgroundColor = "#12244A"
textColor = "#E8EEFC"
```

- [ ] **Step 9: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_ui.py tests/test_app_charts.py tests/test_streamlit_config.py -q`
Expected: tutti passati. Se un test fallisce per un dettaglio di libreria (per esempio come `AppTest` espone `delta`, o come Plotly riporta `dtick`), correggi il codice o l'asserzione nel modo più semplice che mantiene lo scopo del test e registra il motivo nel ledger.

- [ ] **Step 10: Suite completa e commit**

Run: `python -m pytest -q` (52 esistenti + i nuovi, tutti verdi).
```powershell
git add .streamlit app/theme.py app/ui.py app/charts.py tests/test_app_ui.py tests/test_app_charts.py requirements.txt
git commit -m "feat: tema scuro, componenti (KPI, forma a pallini, formati italiani) e grafici Plotly"
```

---

### Task 2: Query nuove per le schede e i tab

**Files:**
- Modify: `app/queries.py`, `app/data.py`
- Test: `tests/test_app_queries.py` (aggiunte in fondo)

**Interfaces:**
- Consumes: fixture `warehouse` (stesso mini-campionato di M4: stagioni 2016/17 con 6 partite e 2017/18 con 1 partita; squadre `A`, `B`, `C`), `queries._read`, `queries._FROM_TEAM_MATCH`, `queries.to_numbers`.
- Produces (tutte `(engine, ...)`):
  - `season_overview(engine, season) -> dict | None` chiavi `partite, gol, gol_a_partita, vittorie_casa, pareggi, vittorie_trasferta`; `None` se la stagione non ha partite
  - `form_by_team(engine, season, n=5) -> DataFrame` colonne `Squadra, Forma` (`Forma` = lettere W/D/L, **dalla più vecchia alla più recente**)
  - `home_away_goals(engine, season, team) -> DataFrame` colonne `Campo, Gol fatti, Gol subiti` (righe `Casa`, `Trasferta`)
  - `team_points_by_season(engine, team) -> DataFrame` colonne `Stagione, Punti, Gol fatti, Gol subiti` (ordine cronologico)
  - `discipline_totals(engine, season) -> dict | None` chiavi `partite, falli, gialli, rossi` (totali di entrambe le squadre)
  - `dataset_overview(engine) -> dict` chiavi `stagioni, partite, squadre, osservazioni, gol`
  - `champions(engine) -> DataFrame` colonne `Stagione, Campione, Punti` (ordine cronologico)
  - In `app/data.py`: `overview(season)`, `form(season, n=5)`, `home_away_goals(season, team)`, `team_history(team)`, `discipline_totals(season)`, `dataset()`, `champions()`, tutte con `st.cache_data(ttl=TTL)`.

Valori attesi (dal mini-campionato, calcolati a mano):
- `season_overview(2016/17)`: partite 6, gol 13, vittorie casa 2, pareggi 2, vittorie trasferta 2.
- Forma 2016/17: **A** `WWWD`, **B** `LDLL`, **C** `DLWD`; con `n=2`: A `WD`, B `LL`, C `WD`.
- `home_away_goals(2016/17, A)`: Casa gol fatti 3 / subiti 1; Trasferta 4 / 0.
- `team_points_by_season(A)`: 2016/17 → 10 punti, 7 fatti, 1 subito; 2017/18 → 3 punti, 1 fatto, 0 subiti.
- `discipline_totals(2016/17)`: partite 6, falli 144, gialli 14, rossi 1.
- `dataset_overview`: stagioni 2, partite 7, squadre 3, osservazioni 14, gol 14.
- `champions`: 2016/17 → A con 10; 2017/18 → A con 3.

- [ ] **Step 1: Scrivi i test (in fondo a `tests/test_app_queries.py`)**

```python
def test_season_overview(warehouse):
    s = q.season_overview(warehouse, "2016/17")
    assert (s["partite"], s["gol"]) == (6, 13)
    assert (s["vittorie_casa"], s["pareggi"], s["vittorie_trasferta"]) == (2, 2, 2)
    assert s["gol_a_partita"] == pytest.approx(13 / 6)
    assert q.season_overview(warehouse, "1999/00") is None


def test_form_by_team_oldest_to_newest(warehouse):
    df = q.form_by_team(warehouse, "2016/17")
    assert list(df.columns) == ["Squadra", "Forma"]
    assert dict(zip(df["Squadra"], df["Forma"])) == {"A": "WWWD", "B": "LDLL", "C": "DLWD"}


def test_form_by_team_limits_to_last_n(warehouse):
    df = q.form_by_team(warehouse, "2016/17", n=2)
    assert dict(zip(df["Squadra"], df["Forma"])) == {"A": "WD", "B": "LL", "C": "WD"}


def test_form_by_team_empty_for_unknown_season(warehouse):
    df = q.form_by_team(warehouse, "1999/00")
    assert df.empty and list(df.columns) == ["Squadra", "Forma"]


def test_home_away_goals(warehouse):
    df = q.home_away_goals(warehouse, "2016/17", "A")
    assert list(df.columns) == ["Campo", "Gol fatti", "Gol subiti"]
    by_field = df.set_index("Campo")
    assert (by_field.loc["Casa", "Gol fatti"], by_field.loc["Casa", "Gol subiti"]) == (3, 1)
    assert (by_field.loc["Trasferta", "Gol fatti"], by_field.loc["Trasferta", "Gol subiti"]) == (4, 0)


def test_team_points_by_season(warehouse):
    df = q.team_points_by_season(warehouse, "A")
    assert list(df.columns) == ["Stagione", "Punti", "Gol fatti", "Gol subiti"]
    assert [tuple(r) for r in df.itertuples(index=False)] == [
        ("2016/17", 10, 7, 1),
        ("2017/18", 3, 1, 0),
    ]


def test_discipline_totals(warehouse):
    t = q.discipline_totals(warehouse, "2016/17")
    assert t == {"partite": 6, "falli": 144, "gialli": 14, "rossi": 1}
    assert q.discipline_totals(warehouse, "1999/00") is None


def test_dataset_overview(warehouse):
    assert q.dataset_overview(warehouse) == {
        "stagioni": 2, "partite": 7, "squadre": 3, "osservazioni": 14, "gol": 14,
    }


def test_champions(warehouse):
    df = q.champions(warehouse)
    assert list(df.columns) == ["Stagione", "Campione", "Punti"]
    assert [tuple(r) for r in df.itertuples(index=False)] == [
        ("2016/17", "A", 10),
        ("2017/18", "A", 3),
    ]
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_queries.py -q`
Expected: i nuovi test falliscono con `AttributeError: module 'app.queries' has no attribute ...`; i 14 esistenti restano verdi.

- [ ] **Step 3: Implementa le query (in fondo a `app/queries.py`)**

```python
def season_overview(engine, season: str) -> dict | None:
    df = _read(
        engine,
        """
        SELECT COUNT(DISTINCT f.match_key) AS partite,
               SUM(f.goals_for) AS gol,
               SUM(CASE WHEN f.is_home = 1 AND f.result = 'W' THEN 1 ELSE 0 END) AS vittorie_casa,
               SUM(CASE WHEN f.is_home = 1 AND f.result = 'D' THEN 1 ELSE 0 END) AS pareggi,
               SUM(CASE WHEN f.is_home = 1 AND f.result = 'L' THEN 1 ELSE 0 END) AS vittorie_trasferta
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season",
        {"season": season},
    )
    row = df.iloc[0]
    if pd.isna(row["gol"]):
        return None
    matches = int(row["partite"])
    goals = int(row["gol"])
    return {
        "partite": matches,
        "gol": goals,
        "gol_a_partita": goals / matches,
        "vittorie_casa": int(row["vittorie_casa"]),
        "pareggi": int(row["pareggi"]),
        "vittorie_trasferta": int(row["vittorie_trasferta"]),
    }


def form_by_team(engine, season: str, n: int = 5) -> pd.DataFrame:
    df = _read(
        engine,
        "SELECT t.team_name AS squadra, m.match_key AS chiave, f.result AS risultato "
        + _FROM_TEAM_MATCH + "WHERE s.label = :season",
        {"season": season},
    )
    rows = []
    for team, group in df.groupby("squadra"):
        last = group.sort_values("chiave").tail(n)
        rows.append({"Squadra": team, "Forma": "".join(last["risultato"])})
    return pd.DataFrame(rows, columns=["Squadra", "Forma"])


def home_away_goals(engine, season: str, team: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT CASE WHEN f.is_home = 1 THEN 'Casa' ELSE 'Trasferta' END AS campo,
               SUM(f.goals_for) AS fatti, SUM(f.goals_against) AS subiti
        """ + _FROM_TEAM_MATCH + """
        WHERE s.label = :season AND t.team_name = :team
        GROUP BY f.is_home
        ORDER BY f.is_home DESC
        """,
        {"season": season, "team": team},
    )
    df = to_numbers(df, ["fatti", "subiti"])
    df[["fatti", "subiti"]] = df[["fatti", "subiti"]].astype(int)
    return df.rename(columns={"campo": "Campo", "fatti": "Gol fatti", "subiti": "Gol subiti"})


def team_points_by_season(engine, team: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT s.label AS stagione, SUM(f.points) AS punti,
               SUM(f.goals_for) AS fatti, SUM(f.goals_against) AS subiti
        """ + _FROM_TEAM_MATCH + "WHERE t.team_name = :team GROUP BY s.label ORDER BY s.label",
        {"team": team},
    )
    df = to_numbers(df, ["punti", "fatti", "subiti"])
    df[["punti", "fatti", "subiti"]] = df[["punti", "fatti", "subiti"]].astype(int)
    return df.rename(columns={
        "stagione": "Stagione", "punti": "Punti", "fatti": "Gol fatti", "subiti": "Gol subiti",
    })


def discipline_totals(engine, season: str) -> dict | None:
    df = _read(
        engine,
        """
        SELECT COUNT(DISTINCT f.match_key) AS partite, SUM(f.fouls_for) AS falli,
               SUM(f.yellow_for) AS gialli, SUM(f.red_for) AS rossi
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season",
        {"season": season},
    )
    row = df.iloc[0]
    if pd.isna(row["falli"]):
        return None
    return {
        "partite": int(row["partite"]), "falli": int(row["falli"]),
        "gialli": int(row["gialli"]), "rossi": int(row["rossi"]),
    }


def dataset_overview(engine) -> dict:
    df = _read(
        engine,
        """
        SELECT (SELECT COUNT(*) FROM dim_season) AS stagioni,
               (SELECT COUNT(*) FROM dim_match) AS partite,
               (SELECT COUNT(*) FROM dim_team) AS squadre,
               (SELECT COUNT(*) FROM fact_team_match) AS osservazioni,
               (SELECT SUM(goals_for) FROM fact_team_match) AS gol
        """,
    )
    row = df.iloc[0]
    return {key: int(row[key]) for key in ("stagioni", "partite", "squadre", "osservazioni", "gol")}


def champions(engine) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT s.label AS stagione, t.team_name AS squadra,
               SUM(f.points) AS punti, SUM(f.goals_for) - SUM(f.goals_against) AS diff
        """ + _FROM_TEAM_MATCH + "GROUP BY s.label, t.team_name",
    )
    df = to_numbers(df, ["punti", "diff"])
    df["score"] = df["punti"] * 1000 + df["diff"]
    best = (
        df.sort_values(["stagione", "score", "squadra"], ascending=[True, False, True])
        .groupby("stagione")
        .head(1)
        .sort_values("stagione")
    )
    out = best[["stagione", "squadra", "punti"]].reset_index(drop=True)
    out["punti"] = out["punti"].astype(int)
    return out.rename(columns={"stagione": "Stagione", "squadra": "Campione", "punti": "Punti"})
```

- [ ] **Step 4: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_queries.py -q`
Expected: tutti passati (14 esistenti + 9 nuovi).

- [ ] **Step 5: Aggiungi gli involucri in `app/data.py`**

In fondo al file:
```python
@st.cache_data(ttl=TTL)
def overview(season):
    return queries.season_overview(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def form(season, n=5):
    return queries.form_by_team(db.get_engine(), season, n)


@st.cache_data(ttl=TTL)
def home_away_goals(season, team):
    return queries.home_away_goals(db.get_engine(), season, team)


@st.cache_data(ttl=TTL)
def team_history(team):
    return queries.team_points_by_season(db.get_engine(), team)


@st.cache_data(ttl=TTL)
def discipline_totals(season):
    return queries.discipline_totals(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def dataset():
    return queries.dataset_overview(db.get_engine())


@st.cache_data(ttl=TTL)
def champions():
    return queries.champions(db.get_engine())
```

- [ ] **Step 6: Prova le query sul database MySQL vero**

```powershell
python -c "from sqlalchemy import create_engine; from etl import config; from app import queries as q; e = create_engine(config.db_url()); print(q.season_overview(e, '2025/26')); print(q.form_by_team(e, '2025/26').head(3).to_string(index=False)); print(q.home_away_goals(e, '2025/26', 'Juventus').to_string(index=False)); print(q.team_points_by_season(e, 'Juventus').head(3).to_string(index=False)); print(q.discipline_totals(e, '2025/26')); print(q.dataset_overview(e)); print(q.champions(e).to_string(index=False))"
```
Expected (valori già noti dal database): `season_overview` con `partite` 380; `dataset_overview` con stagioni 10, partite 3800, squadre 34, osservazioni 7600, gol 10423; `champions` con Juventus (91, 95, 90, 83), Inter 2020/21 91, Milan 2021/22 86, Napoli 2022/23 90, Inter 2023/24 94, Napoli 2024/25 82, Inter 2025/26 87; `home_away_goals` Juventus 2025/26 con Casa/Trasferta che sommano a 61 gol fatti e 34 subiti; `discipline_totals` con falli ≈ 25,35 × 380 = 9.633 (arrotondato dalle somme esatte). Se il database è spento: `docker compose up -d --wait`.

- [ ] **Step 7: Suite completa e commit**

Run: `python -m pytest -q` (tutti verdi).
```powershell
git add app/queries.py app/data.py tests/test_app_queries.py
git commit -m "feat: query per schede KPI, forma, andamento, totali disciplina e campioni"
```

---

### Task 3: Pagine Classifica e Squadra

**Files:**
- Modify: `app/views/classifica.py`, `app/views/squadra.py`
- Modify: `tests/test_app_pages.py`

**Interfaces:**
- Consumes: `app.ui` (`hero`, `kpi`, `fmt_number`, `fmt_percent`, `form_dots`, `DOTS`), `app.charts` (`grouped_bar`, `area_chart`), `app.data` (`seasons`, `teams`, `standings`, `overview`, `form`, `team_summary`, `home_away_goals`, `recent_form`, `team_history`).
- Produces: `classifica.render()` con 5 schede e una colonna `Ultime 5` nella tabella; `squadra.render()` con 5 schede e 2 tab (`Panoramica`, `Andamento`).

Valori attesi dal mini-campionato (stagione predefinita = la più recente, `2017/18`): classifica con A prima (3 punti) e B seconda (0 punti); colonna `Ultime 5` = `["🟢", "🔴"]`; pagina Squadra con A: 5 schede, 2 tab.

- [ ] **Step 1: Aggiorna i test (in `tests/test_app_pages.py`)**

Sostituisci `test_squadra_shows_four_metrics` con:
```python
def test_squadra_shows_five_metrics_and_two_tabs():
    at = AppTest.from_string(PAGES["squadra"]).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 5
    assert len(at.tabs) == 2
```
e aggiungi:
```python
def test_classifica_shows_five_kpis_and_the_form_column():
    at = AppTest.from_string(PAGES["classifica"]).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 5
    table = at.dataframe[0].value
    assert list(table["Squadra"]) == ["A", "B"]
    assert list(table["Ultime 5"]) == ["🟢", "🔴"]
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: i due test nuovi falliscono (`len(at.metric)` è 0 / 4, manca la colonna `Ultime 5`); gli altri passano.

- [ ] **Step 3: Riscrivi `app/views/classifica.py`**

```python
import streamlit as st

from app import data, ui


def render():
    ui.hero("Classifica", "Posizioni, punti e forma delle squadre nella stagione selezionata")
    season = st.selectbox("Stagione", data.seasons(), key="classifica_stagione")
    table = data.standings(season)
    overview = data.overview(season)
    if table.empty or overview is None:
        st.warning("Nessuna partita per questa stagione.")
        return
    matches = overview["partite"]
    cols = st.columns(5)
    ui.kpi(cols[0], "Partite giocate", ui.fmt_number(matches))
    ui.kpi(cols[1], "Gol totali", ui.fmt_number(overview["gol"]),
           note=f"{ui.fmt_number(overview['gol_a_partita'], 2)} per partita")
    ui.kpi(cols[2], "Vittorie in casa", ui.fmt_number(overview["vittorie_casa"]),
           note=ui.fmt_percent(overview["vittorie_casa"] / matches))
    ui.kpi(cols[3], "Pareggi", ui.fmt_number(overview["pareggi"]),
           note=ui.fmt_percent(overview["pareggi"] / matches))
    ui.kpi(cols[4], "Vittorie in trasferta", ui.fmt_number(overview["vittorie_trasferta"]),
           note=ui.fmt_percent(overview["vittorie_trasferta"] / matches))
    form = data.form(season, 5).set_index("Squadra")["Forma"]
    table = table.assign(**{"Ultime 5": table["Squadra"].map(form).fillna("").map(ui.form_dots)})
    st.dataframe(table, hide_index=True)
```

- [ ] **Step 4: Riscrivi `app/views/squadra.py`**

```python
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
```

- [ ] **Step 5: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: tutti passati. Se `at.dataframe[0].value` o `at.tabs` si comportano diversamente nella versione installata di Streamlit, adatta l'asserzione mantenendo lo scopo (5 schede, 2 tab, colonna `Ultime 5` con i pallini attesi) e registra il motivo nel ledger.

- [ ] **Step 6: Suite completa e commit**

Run: `python -m pytest -q` (tutti verdi).
```powershell
git add app/views/classifica.py app/views/squadra.py tests/test_app_pages.py
git commit -m "feat: pagine Classifica e Squadra con schede KPI, forma a pallini e tab"
```

---

### Task 4: Confronti, Disciplina, pagine nuove e navigazione

**Files:**
- Modify: `app/views/confronti.py`, `app/views/disciplina.py`, `app/main.py`
- Create: `app/views/home.py`, `app/views/insight.py`, `app/views/about.py`
- Modify: `tests/test_app_pages.py`

**Interfaces:**
- Consumes: `app.ui`, `app.charts`, `app.theme`, `app.data` (compresi `trends`, `discipline`, `discipline_totals`, `dataset`, `champions`), `etl.config.ROOT`.
- Produces: `confronti.render()` (selettore periodo + 4 grafici ad area), `disciplina.render()` (3 schede con variazione rispetto alla prima stagione + 3 tab), `home.render()` (4 schede + tabella dei campioni), `insight.render()` (mostra `docs/insights.md`), `about.render()` (testo fisso).

- [ ] **Step 1: Aggiorna i test (in `tests/test_app_pages.py`)**

Aggiungi in `PAGES`:
```python
    "home": "from app.views import home\nhome.render()",
    "insight": "from app.views import insight\ninsight.render()",
    "about": "from app.views import about\nabout.render()",
```
e in fondo:
```python
def test_home_shows_four_kpis_and_the_champions():
    at = AppTest.from_string(PAGES["home"]).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 4
    assert list(at.dataframe[0].value["Campione"]) == ["A", "A"]


def test_disciplina_shows_three_kpis_and_three_tabs():
    at = AppTest.from_string(PAGES["disciplina"]).run(timeout=30)
    assert not at.exception
    assert len(at.metric) == 3
    assert len(at.tabs) == 3


def test_confronti_has_a_period_selector():
    at = AppTest.from_string(PAGES["confronti"]).run(timeout=30)
    assert not at.exception
    assert len(at.select_slider) == 1
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: falliscono `home`, `insight`, `about` (modulo mancante) e i test su disciplina e confronti (schede e selettore assenti); quelli già verdi della Task 3 restano verdi.

- [ ] **Step 3: Riscrivi `app/views/confronti.py`**

```python
import streamlit as st

from app import charts, data, theme, ui


def render():
    ui.hero("Confronti tra stagioni", "Principali metriche a confronto nel periodo selezionato")
    trends = data.trends()
    if trends.empty:
        st.warning("Nessun dato disponibile.")
        return
    labels = trends["Stagione"].tolist()
    if len(labels) > 1:
        first, last = st.select_slider(
            "Periodo", options=labels, value=(labels[0], labels[-1]), key="confronti_periodo"
        )
    else:
        first = last = labels[0]
    window = trends[(trends["Stagione"] >= first) & (trends["Stagione"] <= last)]
    top_left, top_right = st.columns(2)
    top_left.plotly_chart(
        charts.area_chart(window, "Stagione", "Gol a Partita", "Gol per partita", fmt=".2f")
    )
    top_right.plotly_chart(
        charts.area_chart(window, "Stagione", "% Vittorie Casa", "Vittorie in casa", fmt=".1%")
    )
    bottom_left, bottom_right = st.columns(2)
    bottom_left.plotly_chart(
        charts.area_chart(window, "Stagione", "Gialli a Partita", "Cartellini gialli per partita",
                          color=theme.YELLOW, fmt=".2f")
    )
    bottom_right.plotly_chart(
        charts.area_chart(window, "Stagione", "Rossi a Partita", "Cartellini rossi per partita",
                          color=theme.RED, fmt=".2f")
    )
```

- [ ] **Step 4: Riscrivi `app/views/disciplina.py`**

```python
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
```

- [ ] **Step 5: Crea le tre pagine nuove**

`app/views/home.py`:
```python
import streamlit as st

from app import data, ui


def render():
    ui.hero("Serie A Analytics", "Risultati e statistiche del campionato italiano")
    seasons = data.seasons()
    if not seasons:
        st.warning("Il database non contiene ancora dati: lancia `python -m etl.run_etl`.")
        return
    overview = data.dataset()
    st.caption(f"{overview['stagioni']} stagioni, da {seasons[-1]} a {seasons[0]}")
    cols = st.columns(4)
    ui.kpi(cols[0], "Stagioni", str(overview["stagioni"]))
    ui.kpi(cols[1], "Partite", ui.fmt_number(overview["partite"]))
    ui.kpi(cols[2], "Squadre", str(overview["squadre"]))
    ui.kpi(cols[3], "Gol totali", ui.fmt_number(overview["gol"]),
           note=f"{ui.fmt_number(overview['gol'] / overview['partite'], 2)} per partita")
    st.subheader("Campioni stagione per stagione")
    st.dataframe(data.champions(), hide_index=True)
    st.info("Usa il menu a sinistra per esplorare classifica, squadre, confronti tra stagioni e disciplina.")
```

`app/views/insight.py`:
```python
import streamlit as st

from app import ui
from etl import config


def render():
    ui.hero("Insight", "Osservazioni sui dati, verificate sul database")
    path = config.ROOT / "docs" / "insights.md"
    if not path.exists():
        st.warning("Il file docs/insights.md non è stato trovato.")
        return
    st.markdown(path.read_text(encoding="utf-8"))
```

`app/views/about.py`:
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
    ui.hero("About", "Il progetto in breve")
    st.markdown(ABOUT)
```

- [ ] **Step 6: Aggiorna `app/main.py`**

Sostituisci il contenuto con:
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
    st.Page(home.render, title="Home", url_path="home", default=True),
    st.Page(classifica.render, title="Classifica", url_path="classifica"),
    st.Page(squadra.render, title="Squadra", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina e gioco duro", url_path="disciplina"),
    st.Page(insight.render, title="Insight", url_path="insight"),
    st.Page(about.render, title="About", url_path="about"),
]
navigation = st.navigation(pages)

overview = data.dataset()
st.sidebar.caption(
    f"Database: {overview['stagioni']} stagioni, {ui.fmt_number(overview['partite'])} partite, "
    f"{overview['squadre']} squadre, {ui.fmt_number(overview['osservazioni'])} osservazioni"
)
navigation.run()
```

- [ ] **Step 7: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: tutti passati (le 7 pagine si renderizzano senza eccezioni; `home` 4 schede e campioni `["A", "A"]`; `disciplina` 3 schede e 3 tab; `confronti` con 1 selettore periodo).

- [ ] **Step 8: Suite completa e commit**

Run: `python -m pytest -q` (tutti verdi).
```powershell
git add app tests/test_app_pages.py
git commit -m "feat: Confronti e Disciplina rinnovate, pagine Home, Insight e About, sidebar"
```

---

### Task 5: Verifica sul database vero, screenshot, documentazione e revisione

**Files:**
- Modify: `README.md`, `docs/milestones/M4b-veste-grafica-streamlit.md`, `docs/milestones/README.md`, `docs/design/README.md` (solo se serve)
- Create: `docs/spiegazioni/10-streamlit-veste-grafica.md`
- Create (a cura dell'utente): `docs/screenshots/streamlit-classifica.png`, `streamlit-squadra.png`, `streamlit-confronti.png`, `streamlit-disciplina.png`

**Interfaces:**
- Consumes: tutto il lavoro dei Task 1–4, database MySQL avviato e popolato.

- [ ] **Step 1: Verifica dei numeri sul database vero**

```powershell
python -c "from sqlalchemy import create_engine; from etl import config; from app import queries as q; e = create_engine(config.db_url()); o = q.season_overview(e, '2025/26'); print(o, o['vittorie_casa'] + o['pareggi'] + o['vittorie_trasferta']); print(q.discipline_totals(e, '2025/26')); print(q.dataset_overview(e)); print(q.form_by_team(e, '2025/26').head(5).to_string(index=False)); print(q.team_points_by_season(e, 'Inter').to_string(index=False))"
```
Expected: `partite` **380** e `gol` **922** (la somma dei gol fatti della classifica 2025/26 in Power BI); casa + pareggi + trasferta = 380; `dataset_overview` = stagioni 10, partite 3800, squadre 34, osservazioni 7600, gol 10423; la forma di ogni squadra ha 5 lettere; i punti dell'Inter per stagione includono 2020/21 = 91, 2023/24 = 94, 2025/26 = 87.

- [ ] **Step 2: Guarda l'app nel browser, pagina per pagina**

Con MySQL acceso:
```powershell
python -m streamlit run app/main.py --server.headless true --server.port 8501
```
(in background). Apri `http://localhost:8501` e controlla le 7 pagine:
- **Home:** 4 schede (10 stagioni, 3.800 partite, 34 squadre, 10.423 gol, 2,74 per partita) e la tabella dei campioni (Juventus 2016/17–2019/20 con 91/95/90/83, Inter 2020/21 91, Milan 86, Napoli 90, Inter 94, Napoli 82, Inter 87).
- **Classifica 2025/26:** 5 schede coerenti, tabella con Inter prima (87) e la colonna `Ultime 5` con i pallini.
- **Squadra (Inter 2025/26):** punti 87 con "1° posto", gol fatti 89 e subiti 35, tab Panoramica e Andamento.
- **Confronti:** il selettore del periodo restringe i 4 grafici; i valori coincidono con `docs/insights.md`.
- **Disciplina 2025/26:** 3 schede con variazioni percentuali rispetto al 2016/17 (falli circa −9%, gialli circa −16%); nel tab Panoramica sono visibili **tutte e 20** le squadre sull'asse del grafico.
- **Insight** e **About** mostrano il testo.
Poi spegni MySQL (`docker compose stop`), ricarica e controlla il messaggio "Database non raggiungibile"; riaccendilo (`docker compose up -d --wait`). Ferma l'app (processo in ascolto sulla porta 8501) quando hai finito.

- [ ] **Step 3: Screenshot reali (a cura dell'utente)**

Chiedi all'utente di salvare 4 screenshot dell'app (Classifica, Squadra, Confronti, Disciplina, con la finestra del browser ritagliata) in `docs/screenshots/` con i nomi sopra, **senza** barra del titolo del sistema e senza dati personali visibili. Controllali (leggibilità, numeri coerenti con quelli verificati). Se l'utente decide di non farli, salta lo Step 4 sulle immagini e segnalalo nel ledger.

- [ ] **Step 4: Aggiorna il README**

Nella sezione dell'app Streamlit del `README.md`: aggiungi la tabella 2×2 con le immagini (`docs/screenshots/streamlit-*.png`), cita le 7 pagine, e correggi il conteggio dei test. Rimuovi dai "Prossimi passi" la voce sulla veste grafica.

- [ ] **Step 5: Scrivi `docs/spiegazioni/10-streamlit-veste-grafica.md`**

Sezioni: com'è organizzato il codice (`theme`, `ui`, `charts`), come si formatta un numero all'italiana, come funzionano `st.metric` con bordo, `st.tabs`, `st.select_slider`, il tema in `config.toml`, perché la logica non è cambiata (e i test esistenti sono rimasti verdi), perché l'HTML è usato solo con testi fissi, cosa è stato preso dal mockup e cosa no (giocatori, zone Champions, immagine di stadio) e perché.

- [ ] **Step 6: Milestone**

`docs/milestones/M4b-veste-grafica-streamlit.md`: spunta le task e segna la milestone come completata; `docs/milestones/README.md`: riga M4b ✅.

- [ ] **Step 7: Revisione finale (autore)**

Rileggi il codice nuovo con queste domande: ogni pagina gestisce stagione/squadra senza dati? Ci sono numeri scritti a mano? L'HTML riceve solo testi fissi? Le etichette dei grafici sono tutte visibili? Il tema è leggibile (contrasto)? Il README dice il vero? Correggi con test prima del codice ciò che trovi e registra ogni cosa nel ledger, distinguendo ciò che è corretto da ciò che è rimandato. Dichiara nella risposta finale che è una revisione dell'autore, non di un revisore indipendente.

- [ ] **Step 8: Suite completa e commit**

Run: `python -m pytest -q` (tutti verdi).
```powershell
git add README.md docs
git commit -m "docs: veste grafica Streamlit (M4b) completata"
```

---

## Self-Review

- **Copertura del mockup (Docs/design):** tema scuro e sidebar (Task 1, 4), schede KPI (Task 1, 3, 4), forma recente a pallini (Task 1, 2, 3), tab Panoramica/Andamento e Panoramica/Falli/Cartellini (Task 3, 4), confronto percentuale con la prima stagione (Task 1, 4), selettore periodo (Task 4), grafici ad area con etichette (Task 1, 4), Home, Insight, About (Task 4). Fuori perimetro come da `docs/design/README.md`: giocatori, zone Champions, immagine di stadio, pagina Partite.
- **Review Focus:** `pct_change` con base zero o mancante (test Task 1); formato italiano (test Task 1); forma con meno partite o stagione sconosciuta (test Task 2: `form_by_team` per stagione sconosciuta restituisce tabella vuota con le colonne; in `classifica.render` la mappa con `.fillna("")` copre le squadre senza forma); stagione o squadra senza dati (messaggi in ogni pagina, Task 3 e 4); etichette (`dtick=1`, test Task 1); HTML solo fisso (hero con testi fissi, Home usa `st.caption`).
- **Placeholder:** nessuno; gli unici passaggi non automatizzabili sono la guardata nel browser e gli screenshot a cura dell'utente (Step 2 e 3 del Task 5), descritti con i valori attesi.
- **Coerenza dei nomi:** colonne e chiavi delle nuove query coincidono tra Interfaces, test, `data.py` e pagine; le funzioni `ui.*` e `charts.*` hanno le stesse firme in tutti i task.
- **Limiti noti:** il codice del piano non è stato eseguito: vanno confermati dai test la disponibilità di `delta_arrow` e `border` in `st.metric`, il comportamento di `at.tabs`/`at.select_slider`/`at.dataframe[0].value` in `AppTest`, e il rendering di `texttemplate` in Plotly con i formati `.1%` e `.2f`.
