# Streamlit Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un'app web Streamlit (con grafici Plotly) che mostra, sul database MySQL esistente, le stesse analisi della dashboard Power BI: classifica, squadra, confronti tra stagioni, disciplina.

**Architecture:** La logica sta in `app/queries.py`: funzioni pure che ricevono un engine SQLAlchemy e restituiscono DataFrame, testate con pytest su SQLite. `app/data.py` aggiunge la cache di Streamlit, `app/views/*` sono le pagine (solo presentazione), `app/main.py` è la navigazione. La connessione riusa `etl.config.db_url()`.

**Tech Stack:** Python, Streamlit, Plotly, pandas, SQLAlchemy, pytest (con `streamlit.testing.v1.AppTest` per gli smoke test delle pagine).

**Spec:** `docs/superpowers/specs/2026-10-05-serie-a-bi-design.md` (sezione "Frontend Streamlit")

## Global Constraints

- Streamlit si **aggiunge** a Power BI; solo in **locale**; grafici con **Plotly**.
- Il database è quello esistente (star schema, `localhost:3308`); l'app **non scrive** nulla e non modifica lo schema.
- Regola di classifica identica a Power BI: ordine per punti e, a parità, per differenza reti; posizione con rango "denso" (`[Punti] * 1000 + [Diff Reti]`).
- Le medie "a partita" dividono per le partite distinte, come in Power BI.
- Le query sono SQL standard compatibile **sia con MySQL sia con SQLite** (i test girano su SQLite): niente funzioni specifiche di un solo database; alias in minuscolo senza virgolette, rinominati poi in pandas.
- Colonne dei risultati in **italiano**, esattamente come negli Interfaces.
- Dopo il lavoro: file `docs/spiegazioni/09-streamlit.md` in italiano, tono didattico (sezioni **Cosa ho fatto**, **Perché**, **Come funziona (codice spiegato)**, **Come eseguirlo**, **Concetti da studiare**).
- Comandi: PowerShell, dalla radice del progetto, con il venv attivo; l'app si avvia con `python -m streamlit run app/main.py`.
- Messaggi di commit: aggiungere in coda le righe di attribuzione richieste dall'ambiente.
- Il push su GitHub lo fa l'utente: non fare `git push`.

## Review Focus

1. **MySQL restituisce `Decimal`** per `SUM`/medie, SQLite no: i test su SQLite non lo vedrebbero. Le colonne numeriche vanno convertite (Task 2, test sul convertitore).
2. **Squadra che non ha giocato** nella stagione scelta, o stagione senza dati: l'app mostra un messaggio, non una traccia d'errore. (Task 2 e 4)
3. **Tiri mancanti** (`NULL`): la conversione tiri è `None` e si mostra "n/d". (Task 2 e 4)
4. **Database spento o irraggiungibile**: messaggio chiaro con il comando per avviarlo, non una traccia. (Task 3)
5. **Parità in classifica**: due squadre con punti e differenza reti uguali hanno la stessa posizione e restano in ordine alfabetico. (Task 2)

---

## File Structure

| File | Responsabilità |
|---|---|
| `requirements.txt` | aggiunge `streamlit` e `plotly` |
| `app/__init__.py`, `app/views/__init__.py` | pacchetti |
| `app/queries.py` | logica: SQL + pandas, funzioni pure, testate |
| `app/db.py` | connessione (cache della risorsa) e `check_connection` |
| `app/data.py` | involucri con `st.cache_data` per le pagine |
| `app/views/classifica.py`, `squadra.py`, `confronti.py`, `disciplina.py` | una pagina ciascuna, funzione `render()` |
| `app/main.py` | configurazione, controllo database, navigazione |
| `tests/conftest.py` | fixture `warehouse`: mini-campionato con risultati calcolati a mano |
| `tests/test_app_queries.py` | test della logica |
| `tests/test_app_pages.py` | smoke test delle pagine con `AppTest` |

---

### Task 1: Dipendenze e dati di test

**Files:**
- Modify: `requirements.txt`
- Create: `app/__init__.py`, `app/views/__init__.py` (vuoti)
- Create: `tests/conftest.py`
- Create: `docs/spiegazioni/09-streamlit.md` (scheletro, completato nel Task 3)

**Interfaces:**
- Produces: fixture pytest `warehouse` → engine SQLAlchemy su un SQLite temporaneo con lo schema del progetto e questi dati (stagioni **2016/17** e **2017/18**, squadre `A`, `B`, `C`):

| Stagione | Data | Casa | Ospite | Gol | Gialli (casa-osp.) | Rossi osp. |
|---|---|---|---|---|---|---|
| 2016/17 | 2016-09-01 | A | B | 2-0 | 1-0 | 0 |
| 2016/17 | 2016-09-02 | B | C | 1-1 | 2-3 | 1 |
| 2016/17 | 2016-09-03 | C | A | 0-3 | 0-1 | 0 |
| 2016/17 | 2016-09-04 | B | A | 0-1 | 1-1 | 0 |
| 2016/17 | 2016-09-05 | C | B | 2-1 | 2-1 | 0 |
| 2016/17 | 2016-09-06 | A | C | 1-1 | 0-2 | 0 |
| 2017/18 | 2017-09-01 | A | B | 1-0 | 0-0 | 0 |

Tutte le partite: tiri casa 10 / ospite 8, tiri in porta 4 / 3, falli casa 10 / ospite 14, corner 5 / 4, gol primo tempo 0-0, nessun cartellino rosso della casa.
Valori attesi (calcolati a mano, usati dai test del Task 2):
- Classifica 2016/17: **A** pos 1, 4 partite, 3V 1N 0P, GF 7, GS 1, DR +6, 10 punti; **C** pos 2, 4 partite, 1V 2N 1P, GF 4, GS 6, DR −2, 5 punti; **B** pos 3, 4 partite, 0V 1N 3P, GF 2, GS 6, DR −4, 1 punto.
- Gialli a partita 2016/17: A 0,75, B 1,00, C 1,75. Rossi a partita: C 0,25, A 0, B 0. Falli a partita ciascuna 12,0.
- Tendenze 2016/17: gol a partita 13/6, % vittorie casa 2/6, gialli 14/6, rossi 1/6, falli 24. Tendenze 2017/18: gol 1,0, % vittorie casa 1,0, gialli 0, rossi 0, falli 24.
- Squadra A 2016/17: punti 10, gol fatti 7, gol subiti 1, tiri 36 (conversione 7/36); punti in casa 4, in trasferta 6; ultime 3 partite (più recente prima): 2016-09-06 N 1-1 vs C; 2016-09-04 V 1-0 vs B; 2016-09-03 V 3-0 vs C.

- [ ] **Step 1: Aggiungi le dipendenze**

`requirements.txt` — aggiungi in fondo:
```
streamlit>=1.40
plotly>=5.24
```

- [ ] **Step 2: Installa e verifica la compatibilità con pandas**

```powershell
pip install -r requirements.txt
python -c "import streamlit, plotly, pandas; print('streamlit', streamlit.__version__, '| plotly', plotly.__version__, '| pandas', pandas.__version__)"
python -m pytest -q
```
Expected: installazione senza errori, stampa delle tre versioni e i 29 test esistenti ancora verdi. **Se l'installazione o l'import falliscono** (per esempio perché la versione di Streamlit non supporta ancora pandas 3 o Python 3.14), non aggirare il problema in silenzio: leggi il messaggio, prova la versione di Streamlit più recente compatibile e registra la scelta nel ledger.

- [ ] **Step 3: Crea i pacchetti vuoti**

Crea `app/__init__.py` e `app/views/__init__.py` (file vuoti).

- [ ] **Step 4: Scrivi `tests/conftest.py`**

```python
import sqlite3

import pandas as pd
import pytest
from sqlalchemy import create_engine

from etl import config, transform as t
from etl.load import load_star


def _match(date, home, away, goals, yellows, away_red=0):
    return {
        "Date": date, "HomeTeam": home, "AwayTeam": away,
        "FTHG": str(goals[0]), "FTAG": str(goals[1]),
        "HTHG": "0", "HTAG": "0",
        "HS": "10", "AS": "8", "HST": "4", "AST": "3",
        "HF": "10", "AF": "14", "HC": "5", "AC": "4",
        "HY": str(yellows[0]), "AY": str(yellows[1]),
        "HR": "0", "AR": str(away_red),
    }


SEASON_2016 = [
    _match("2016-09-01", "A", "B", (2, 0), (1, 0)),
    _match("2016-09-02", "B", "C", (1, 1), (2, 3), away_red=1),
    _match("2016-09-03", "C", "A", (0, 3), (0, 1)),
    _match("2016-09-04", "B", "A", (0, 1), (1, 1)),
    _match("2016-09-05", "C", "B", (2, 1), (2, 1)),
    _match("2016-09-06", "A", "C", (1, 1), (0, 2)),
]
SEASON_2017 = [
    _match("2017-09-01", "A", "B", (1, 0), (0, 0)),
]


@pytest.fixture
def warehouse(tmp_path):
    db = tmp_path / "warehouse.db"
    con = sqlite3.connect(db)
    for name in ("01_staging.sql", "02_star_schema.sql"):
        con.executescript((config.ROOT / "sql" / name).read_text(encoding="utf-8"))
    con.close()
    engine = create_engine(f"sqlite:///{db}")
    frames = {
        2016: pd.DataFrame(SEASON_2016, dtype="object"),
        2017: pd.DataFrame(SEASON_2017, dtype="object"),
    }
    star, _ = t.transform_all(frames, {})
    load_star(engine, star)
    return engine
```

- [ ] **Step 5: Verifica che la fixture non rompa nulla**

Run: `python -m pytest -q`
Expected: 29 passed (la fixture non è ancora usata).

- [ ] **Step 6: Crea lo scheletro di `docs/spiegazioni/09-streamlit.md`**

Titolo "09 – Frontend Streamlit" e le sezioni vuote da completare nel Task 3.

- [ ] **Step 7: Commit**

```powershell
git add requirements.txt app tests/conftest.py docs/spiegazioni/09-streamlit.md
git commit -m "chore: dipendenze Streamlit/Plotly e dati di test del mini-campionato"
```

---

### Task 2: Logica delle query (`app/queries.py`)

**Files:**
- Create: `app/queries.py`
- Test: `tests/test_app_queries.py`

**Interfaces:**
- Consumes: fixture `warehouse` (Task 1), tabelle `fact_team_match`, `dim_match`, `dim_season`, `dim_team`, `dim_date`.
- Produces (tutte con firma `(engine, ...)`):
  - `list_seasons(engine) -> list[str]` (più recente prima, es. `["2017/18", "2016/17"]`)
  - `list_teams(engine, season: str) -> list[str]` (ordine alfabetico)
  - `standings(engine, season: str) -> DataFrame` colonne `Posizione, Squadra, Partite, Vittorie, Pareggi, Sconfitte, Gol Fatti, Gol Subiti, Diff Reti, Punti`
  - `recent_form(engine, season: str, team: str, n: int = 5) -> DataFrame` colonne `Data, Risultato, Gol fatti, Gol subiti, Avversario` (più recente prima; `Data` come testo `AAAA-MM-GG`)
  - `team_summary(engine, season: str, team: str) -> dict | None` chiavi `punti`, `gol_fatti`, `gol_subiti`, `conversione_tiri` (float o `None`); `None` se la squadra non ha partite nella stagione
  - `home_away_points(engine, season: str, team: str) -> DataFrame` colonne `Campo, Punti` (righe `Casa` e `Trasferta`)
  - `season_trends(engine) -> DataFrame` colonne `Stagione, Gol a Partita, % Vittorie Casa, Gialli a Partita, Rossi a Partita, Falli a Partita` (ordine cronologico; `% Vittorie Casa` come frazione 0–1)
  - `discipline_by_team(engine, season: str) -> DataFrame` colonne `Squadra, Falli a Partita, Falli Subiti a Partita, Gialli a Partita, Rossi a Partita` (più ammoniti prima)
  - `to_numbers(df: DataFrame, columns: list[str]) -> DataFrame` converte le colonne indicate in numeri (anche da `Decimal`)

- [ ] **Step 1: Scrivi i test**

`tests/test_app_queries.py`:
```python
from decimal import Decimal

import pandas as pd
import pytest
from sqlalchemy import create_engine

from app import queries as q


def test_to_numbers_converts_decimals():
    df = pd.DataFrame({"x": [Decimal("1.5"), Decimal("2")], "y": ["a", "b"]})
    out = q.to_numbers(df, ["x"])
    assert out["x"].dtype.kind == "f"
    assert out["x"].sum() == pytest.approx(3.5)
    assert list(out["y"]) == ["a", "b"]


def test_list_seasons_latest_first(warehouse):
    assert q.list_seasons(warehouse) == ["2017/18", "2016/17"]


def test_list_teams_of_a_season(warehouse):
    assert q.list_teams(warehouse, "2016/17") == ["A", "B", "C"]
    assert q.list_teams(warehouse, "2017/18") == ["A", "B"]


def test_standings_2016_17(warehouse):
    df = q.standings(warehouse, "2016/17")
    assert list(df.columns) == [
        "Posizione", "Squadra", "Partite", "Vittorie", "Pareggi", "Sconfitte",
        "Gol Fatti", "Gol Subiti", "Diff Reti", "Punti",
    ]
    assert list(df["Squadra"]) == ["A", "C", "B"]
    a, c, b = (df.iloc[i] for i in range(3))
    assert (a["Posizione"], a["Partite"], a["Vittorie"], a["Pareggi"], a["Sconfitte"]) == (1, 4, 3, 1, 0)
    assert (a["Gol Fatti"], a["Gol Subiti"], a["Diff Reti"], a["Punti"]) == (7, 1, 6, 10)
    assert (c["Posizione"], c["Vittorie"], c["Pareggi"], c["Sconfitte"], c["Diff Reti"], c["Punti"]) == (2, 1, 2, 1, -2, 5)
    assert (b["Posizione"], b["Vittorie"], b["Pareggi"], b["Sconfitte"], b["Diff Reti"], b["Punti"]) == (3, 0, 1, 3, -4, 1)


def test_standings_positions_without_ties(warehouse):
    # 2017/18: una sola partita, A vince 1-0: A prima, B secondo (nessuna parità)
    df = q.standings(warehouse, "2017/18")
    assert list(df["Posizione"]) == [1, 2]


def test_standings_equal_points_and_goal_difference_get_same_position():
    # due squadre identiche (stessa partita pareggiata) condividono la posizione
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        for stmt in (
            "CREATE TABLE dim_season (season_key INT, label TEXT)",
            "CREATE TABLE dim_team (team_key INT, team_name TEXT)",
            "CREATE TABLE dim_match (match_key INT, season_key INT)",
            "CREATE TABLE fact_team_match (match_key INT, team_key INT, result TEXT, goals_for INT, goals_against INT, points INT)",
            "INSERT INTO dim_season VALUES (1, 'S')",
            "INSERT INTO dim_team VALUES (1, 'X'), (2, 'Y')",
            "INSERT INTO dim_match VALUES (1, 1)",
            "INSERT INTO fact_team_match VALUES (1, 1, 'D', 1, 1, 1), (1, 2, 'D', 1, 1, 1)",
        ):
            conn.exec_driver_sql(stmt)
    df = q.standings(engine, "S")
    assert list(df["Squadra"]) == ["X", "Y"]
    assert list(df["Posizione"]) == [1, 1]


def test_standings_of_unknown_season_is_empty(warehouse):
    assert q.standings(warehouse, "1999/00").empty


def test_recent_form_most_recent_first(warehouse):
    df = q.recent_form(warehouse, "2016/17", "A", 3)
    assert list(df.columns) == ["Data", "Risultato", "Gol fatti", "Gol subiti", "Avversario"]
    assert [tuple(r) for r in df.itertuples(index=False)] == [
        ("2016-09-06", "D", 1, 1, "C"),
        ("2016-09-04", "W", 1, 0, "B"),
        ("2016-09-03", "W", 3, 0, "C"),
    ]


def test_recent_form_limits_to_available_matches(warehouse):
    assert len(q.recent_form(warehouse, "2016/17", "A", 10)) == 4


def test_team_summary(warehouse):
    s = q.team_summary(warehouse, "2016/17", "A")
    assert (s["punti"], s["gol_fatti"], s["gol_subiti"]) == (10, 7, 1)
    assert s["conversione_tiri"] == pytest.approx(7 / 36)


def test_team_summary_none_when_team_did_not_play(warehouse):
    assert q.team_summary(warehouse, "2017/18", "C") is None


def test_home_away_points(warehouse):
    df = q.home_away_points(warehouse, "2016/17", "A")
    assert dict(zip(df["Campo"], df["Punti"])) == {"Casa": 4, "Trasferta": 6}


def test_season_trends(warehouse):
    df = q.season_trends(warehouse)
    assert list(df.columns) == [
        "Stagione", "Gol a Partita", "% Vittorie Casa",
        "Gialli a Partita", "Rossi a Partita", "Falli a Partita",
    ]
    assert list(df["Stagione"]) == ["2016/17", "2017/18"]
    r16, r17 = df.iloc[0], df.iloc[1]
    assert r16["Gol a Partita"] == pytest.approx(13 / 6)
    assert r16["% Vittorie Casa"] == pytest.approx(2 / 6)
    assert r16["Gialli a Partita"] == pytest.approx(14 / 6)
    assert r16["Rossi a Partita"] == pytest.approx(1 / 6)
    assert r16["Falli a Partita"] == pytest.approx(24)
    assert r17["Gol a Partita"] == pytest.approx(1.0)
    assert r17["% Vittorie Casa"] == pytest.approx(1.0)
    assert r17["Gialli a Partita"] == pytest.approx(0)


def test_discipline_by_team(warehouse):
    df = q.discipline_by_team(warehouse, "2016/17")
    assert list(df.columns) == [
        "Squadra", "Falli a Partita", "Falli Subiti a Partita",
        "Gialli a Partita", "Rossi a Partita",
    ]
    assert list(df["Squadra"]) == ["C", "B", "A"]  # più ammoniti prima
    by_team = df.set_index("Squadra")
    assert by_team.loc["A", "Gialli a Partita"] == pytest.approx(0.75)
    assert by_team.loc["B", "Gialli a Partita"] == pytest.approx(1.0)
    assert by_team.loc["C", "Gialli a Partita"] == pytest.approx(1.75)
    assert by_team.loc["C", "Rossi a Partita"] == pytest.approx(0.25)
    assert by_team.loc["A", "Falli a Partita"] == pytest.approx(12.0)
    assert by_team.loc["A", "Falli Subiti a Partita"] == pytest.approx(12.0)
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_queries.py -q`
Expected: FAIL / errore di collezione (`ModuleNotFoundError: app.queries`).

- [ ] **Step 3: Implementa `app/queries.py`**

```python
import pandas as pd
from sqlalchemy import text

_FROM_TEAM_MATCH = """
FROM fact_team_match f
JOIN dim_match m ON m.match_key = f.match_key
JOIN dim_season s ON s.season_key = m.season_key
JOIN dim_team t ON t.team_key = f.team_key
"""


def _read(engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def to_numbers(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """MySQL restituisce Decimal per SUM e medie: li converte in numeri."""
    df = df.copy()
    for column in columns:
        df[column] = pd.to_numeric(df[column])
    return df


def list_seasons(engine) -> list[str]:
    df = _read(engine, "SELECT label FROM dim_season ORDER BY season_key DESC")
    return df["label"].tolist()


def list_teams(engine, season: str) -> list[str]:
    df = _read(
        engine,
        "SELECT DISTINCT t.team_name AS team " + _FROM_TEAM_MATCH
        + "WHERE s.label = :season ORDER BY t.team_name",
        {"season": season},
    )
    return df["team"].tolist()


def standings(engine, season: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT t.team_name AS squadra,
               COUNT(*) AS partite,
               SUM(CASE WHEN f.result = 'W' THEN 1 ELSE 0 END) AS vittorie,
               SUM(CASE WHEN f.result = 'D' THEN 1 ELSE 0 END) AS pareggi,
               SUM(CASE WHEN f.result = 'L' THEN 1 ELSE 0 END) AS sconfitte,
               SUM(f.goals_for) AS gol_fatti,
               SUM(f.goals_against) AS gol_subiti,
               SUM(f.points) AS punti
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season GROUP BY t.team_name",
        {"season": season},
    )
    numeric = ["partite", "vittorie", "pareggi", "sconfitte", "gol_fatti", "gol_subiti", "punti"]
    df = to_numbers(df, numeric)
    df[numeric] = df[numeric].astype(int)
    df["diff_reti"] = df["gol_fatti"] - df["gol_subiti"]
    score = df["punti"] * 1000 + df["diff_reti"]
    df["posizione"] = score.rank(method="dense", ascending=False).astype(int)
    df = df.sort_values(["posizione", "squadra"]).reset_index(drop=True)
    df = df.rename(columns={
        "posizione": "Posizione", "squadra": "Squadra", "partite": "Partite",
        "vittorie": "Vittorie", "pareggi": "Pareggi", "sconfitte": "Sconfitte",
        "gol_fatti": "Gol Fatti", "gol_subiti": "Gol Subiti",
        "diff_reti": "Diff Reti", "punti": "Punti",
    })
    return df[[
        "Posizione", "Squadra", "Partite", "Vittorie", "Pareggi", "Sconfitte",
        "Gol Fatti", "Gol Subiti", "Diff Reti", "Punti",
    ]]


def recent_form(engine, season: str, team: str, n: int = 5) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT d.date AS data, f.result AS risultato, f.goals_for AS gol_fatti,
               f.goals_against AS gol_subiti, o.team_name AS avversario
        """ + _FROM_TEAM_MATCH + """
        JOIN dim_date d ON d.date_key = m.date_key
        JOIN dim_team o ON o.team_key = f.opponent_team_key
        WHERE s.label = :season AND t.team_name = :team
        ORDER BY m.match_key DESC
        LIMIT :n
        """,
        {"season": season, "team": team, "n": int(n)},
    )
    df["data"] = df["data"].astype(str)
    return df.rename(columns={
        "data": "Data", "risultato": "Risultato", "gol_fatti": "Gol fatti",
        "gol_subiti": "Gol subiti", "avversario": "Avversario",
    })


def team_summary(engine, season: str, team: str) -> dict | None:
    df = _read(
        engine,
        """
        SELECT SUM(f.points) AS punti, SUM(f.goals_for) AS gol_fatti,
               SUM(f.goals_against) AS gol_subiti, SUM(f.shots_for) AS tiri
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season AND t.team_name = :team",
        {"season": season, "team": team},
    )
    row = df.iloc[0]
    if pd.isna(row["punti"]):
        return None
    shots = row["tiri"]
    conversion = None if pd.isna(shots) or float(shots) == 0 else float(row["gol_fatti"]) / float(shots)
    return {
        "punti": int(row["punti"]),
        "gol_fatti": int(row["gol_fatti"]),
        "gol_subiti": int(row["gol_subiti"]),
        "conversione_tiri": conversion,
    }


def home_away_points(engine, season: str, team: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT CASE WHEN f.is_home = 1 THEN 'Casa' ELSE 'Trasferta' END AS campo,
               SUM(f.points) AS punti
        """ + _FROM_TEAM_MATCH + """
        WHERE s.label = :season AND t.team_name = :team
        GROUP BY f.is_home
        ORDER BY f.is_home DESC
        """,
        {"season": season, "team": team},
    )
    df = to_numbers(df, ["punti"])
    df["punti"] = df["punti"].astype(int)
    return df.rename(columns={"campo": "Campo", "punti": "Punti"})


def season_trends(engine) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT s.label AS stagione,
               SUM(f.goals_for) * 1.0 / COUNT(DISTINCT f.match_key) AS gol,
               SUM(CASE WHEN f.is_home = 1 AND f.result = 'W' THEN 1 ELSE 0 END) * 1.0
                   / SUM(f.is_home) AS vittorie_casa,
               SUM(f.yellow_for) * 1.0 / COUNT(DISTINCT f.match_key) AS gialli,
               SUM(f.red_for) * 1.0 / COUNT(DISTINCT f.match_key) AS rossi,
               SUM(f.fouls_for) * 1.0 / COUNT(DISTINCT f.match_key) AS falli
        """ + _FROM_TEAM_MATCH + "GROUP BY s.label ORDER BY s.label",
    )
    df = to_numbers(df, ["gol", "vittorie_casa", "gialli", "rossi", "falli"])
    return df.rename(columns={
        "stagione": "Stagione", "gol": "Gol a Partita", "vittorie_casa": "% Vittorie Casa",
        "gialli": "Gialli a Partita", "rossi": "Rossi a Partita", "falli": "Falli a Partita",
    })


def discipline_by_team(engine, season: str) -> pd.DataFrame:
    df = _read(
        engine,
        """
        SELECT t.team_name AS squadra,
               SUM(f.fouls_for) * 1.0 / COUNT(*) AS falli,
               SUM(f.fouls_against) * 1.0 / COUNT(*) AS falli_subiti,
               SUM(f.yellow_for) * 1.0 / COUNT(*) AS gialli,
               SUM(f.red_for) * 1.0 / COUNT(*) AS rossi
        """ + _FROM_TEAM_MATCH + "WHERE s.label = :season GROUP BY t.team_name ORDER BY gialli DESC, t.team_name",
        {"season": season},
    )
    df = to_numbers(df, ["falli", "falli_subiti", "gialli", "rossi"])
    return df.rename(columns={
        "squadra": "Squadra", "falli": "Falli a Partita", "falli_subiti": "Falli Subiti a Partita",
        "gialli": "Gialli a Partita", "rossi": "Rossi a Partita",
    })
```

- [ ] **Step 4: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_queries.py -q`
Expected: 14 passed. Se un test fallisce per differenze tra SQLite e pandas (per esempio tipo di `Data`, ordine di righe), correggi l'implementazione, non il valore atteso: i valori attesi sono calcolati a mano nel Task 1.

- [ ] **Step 5: Esegui tutta la suite**

Run: `python -m pytest -q`
Expected: 43 passed (29 esistenti + 14 nuovi).

- [ ] **Step 6: Commit**

```powershell
git add app/queries.py tests/test_app_queries.py
git commit -m "feat: query dell'app (classifica, forma, riepilogo, tendenze, disciplina) con test"
```

---

### Task 3: Guscio dell'app, pagine, verifica e documentazione

**Files:**
- Create: `app/db.py`, `app/data.py`, `app/main.py`
- Create: `app/views/classifica.py`, `app/views/squadra.py`, `app/views/confronti.py`, `app/views/disciplina.py`
- Test: `tests/test_app_pages.py`
- Modify: `README.md`, `docs/milestones/M4-frontend-streamlit.md`, `docs/milestones/README.md`, `docs/spiegazioni/09-streamlit.md`

**Interfaces:**
- Consumes: tutte le funzioni di `app/queries.py` (Task 2) e la fixture `warehouse` (Task 1); `etl.config.db_url()`.
- Produces:
  - `app.db.get_engine() -> Engine` (con `st.cache_resource`), `app.db.check_connection(engine) -> bool`
  - `app.data`: `seasons()`, `teams(season)`, `standings(season)`, `recent_form(season, team, n=5)`, `team_summary(season, team)`, `home_away_points(season, team)`, `trends()`, `discipline(season)`: ognuna chiama `queries.<funzione>(db.get_engine(), ...)` **al momento della chiamata** (così i test possono sostituire `app.db.get_engine`) e usa `st.cache_data(ttl=600)`
  - `app.views.<pagina>.render()` per `classifica`, `squadra`, `confronti`, `disciplina`

- [ ] **Step 1: Scrivi i test (connessione e pagine)**

`tests/test_app_pages.py`:
```python
import pytest
import streamlit as st
from sqlalchemy import create_engine
from streamlit.testing.v1 import AppTest

from app import db

PAGES = {
    "classifica": "from app.views import classifica\nclassifica.render()",
    "squadra": "from app.views import squadra\nsquadra.render()",
    "confronti": "from app.views import confronti\nconfronti.render()",
    "disciplina": "from app.views import disciplina\ndisciplina.render()",
}


@pytest.fixture(autouse=True)
def use_test_warehouse(monkeypatch, warehouse):
    monkeypatch.setattr("app.db.get_engine", lambda: warehouse)
    st.cache_data.clear()


def test_check_connection_true_for_a_working_engine(warehouse):
    assert db.check_connection(warehouse) is True


def test_check_connection_false_for_an_unreachable_database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'cartella_che_non_esiste' / 'x.db'}")
    assert db.check_connection(engine) is False


@pytest.mark.parametrize("name", list(PAGES))
def test_page_renders_without_exceptions(name):
    at = AppTest.from_string(PAGES[name]).run(timeout=30)
    assert not at.exception


def test_classifica_shows_the_standings_table():
    at = AppTest.from_string(PAGES["classifica"]).run(timeout=30)
    assert len(at.dataframe) >= 1


def test_squadra_shows_four_metrics():
    at = AppTest.from_string(PAGES["squadra"]).run(timeout=30)
    assert len(at.metric) == 4
```

- [ ] **Step 2: Esegui i test, verifica che falliscano**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: errore di collezione (`ImportError: cannot import name 'db' from 'app'`).

- [ ] **Step 3: Implementa `app/db.py` e `app/data.py`**

`app/db.py`:
```python
import streamlit as st
from sqlalchemy import create_engine, text

from etl import config


def check_connection(engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@st.cache_resource
def get_engine():
    return create_engine(config.db_url(), pool_pre_ping=True)
```

`app/data.py`:
```python
import streamlit as st

from app import db, queries

TTL = 600  # secondi: i dati cambiano solo quando si rilancia l'ETL


@st.cache_data(ttl=TTL)
def seasons():
    return queries.list_seasons(db.get_engine())


@st.cache_data(ttl=TTL)
def teams(season):
    return queries.list_teams(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def standings(season):
    return queries.standings(db.get_engine(), season)


@st.cache_data(ttl=TTL)
def recent_form(season, team, n=5):
    return queries.recent_form(db.get_engine(), season, team, n)


@st.cache_data(ttl=TTL)
def team_summary(season, team):
    return queries.team_summary(db.get_engine(), season, team)


@st.cache_data(ttl=TTL)
def home_away_points(season, team):
    return queries.home_away_points(db.get_engine(), season, team)


@st.cache_data(ttl=TTL)
def trends():
    return queries.season_trends(db.get_engine())


@st.cache_data(ttl=TTL)
def discipline(season):
    return queries.discipline_by_team(db.get_engine(), season)
```

- [ ] **Step 4: Implementa le quattro pagine**

`app/views/classifica.py`:
```python
import streamlit as st

from app import data


def render():
    st.title("Classifica")
    season = st.selectbox("Stagione", data.seasons(), key="classifica_stagione")
    table = data.standings(season)
    if table.empty:
        st.warning("Nessuna partita per questa stagione.")
        return
    st.dataframe(table, hide_index=True)
    st.subheader("Forma recente")
    team = st.selectbox("Squadra", data.teams(season), key="classifica_squadra")
    st.dataframe(data.recent_form(season, team, 5), hide_index=True)
```

`app/views/squadra.py`:
```python
import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Squadra")
    left, right = st.columns(2)
    season = left.selectbox("Stagione", data.seasons(), key="squadra_stagione")
    team = right.selectbox("Squadra", data.teams(season), key="squadra_squadra")
    summary = data.team_summary(season, team)
    if summary is None:
        st.warning("Questa squadra non ha partite nella stagione scelta.")
        return
    cols = st.columns(4)
    cols[0].metric("Punti", summary["punti"])
    cols[1].metric("Gol fatti", summary["gol_fatti"])
    cols[2].metric("Gol subiti", summary["gol_subiti"])
    conversion = summary["conversione_tiri"]
    cols[3].metric("% conversione tiri", "n/d" if conversion is None else f"{conversion:.2%}")
    chart = px.bar(
        data.home_away_points(season, team),
        x="Campo", y="Punti", title="Punti in casa e in trasferta",
    )
    st.plotly_chart(chart)
```

`app/views/confronti.py`:
```python
import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Confronti tra stagioni")
    trends = data.trends()
    if trends.empty:
        st.warning("Nessun dato disponibile.")
        return
    top_left, top_right = st.columns(2)
    top_left.plotly_chart(
        px.line(trends, x="Stagione", y="Gol a Partita", markers=True, title="Gol a partita")
    )
    wins = px.line(trends, x="Stagione", y="% Vittorie Casa", markers=True, title="% vittorie in casa")
    wins.update_yaxes(tickformat=".0%")
    top_right.plotly_chart(wins)
    bottom_left, bottom_right = st.columns(2)
    bottom_left.plotly_chart(px.bar(trends, x="Stagione", y="Gialli a Partita", title="Gialli a partita"))
    bottom_right.plotly_chart(px.bar(trends, x="Stagione", y="Rossi a Partita", title="Rossi a partita"))
```

`app/views/disciplina.py`:
```python
import plotly.express as px
import streamlit as st

from app import data


def render():
    st.title("Disciplina e gioco duro")
    season = st.selectbox("Stagione", data.seasons(), key="disciplina_stagione")
    table = data.discipline(season)
    if table.empty:
        st.warning("Nessuna partita per questa stagione.")
        return
    left, right = st.columns(2)
    left.plotly_chart(
        px.bar(
            table.sort_values("Gialli a Partita"),
            x="Gialli a Partita", y="Squadra", orientation="h",
            title="Gialli a partita per squadra",
        )
    )
    right.dataframe(table.round(2), hide_index=True)
    st.plotly_chart(
        px.line(data.trends(), x="Stagione", y="Falli a Partita", markers=True,
                title="Falli a partita per stagione")
    )
```

- [ ] **Step 5: Implementa `app/main.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app import db  # noqa: E402
from app.views import classifica, confronti, disciplina, squadra  # noqa: E402

st.set_page_config(page_title="Serie A BI", layout="wide")

if not db.check_connection(db.get_engine()):
    st.error(
        "Database non raggiungibile. Avvia MySQL con `docker compose up -d --wait` "
        "e ricarica la pagina."
    )
    st.stop()

pages = [
    st.Page(classifica.render, title="Classifica", url_path="classifica", default=True),
    st.Page(squadra.render, title="Squadra", url_path="squadra"),
    st.Page(confronti.render, title="Confronti tra stagioni", url_path="confronti"),
    st.Page(disciplina.render, title="Disciplina e gioco duro", url_path="disciplina"),
]
st.navigation(pages).run()
```

- [ ] **Step 6: Esegui i test, verifica che passino**

Run: `python -m pytest tests/test_app_pages.py -q`
Expected: 8 passed (2 di connessione, 4 di rendering, 1 classifica, 1 squadra). Se `AppTest` non riesce a eseguire una pagina per limiti di Streamlit (per esempio sul thread di SQLite), correggi la causa: non togliere il test e non rendere i test condizionali; se è impossibile, registra un ruling nel ledger spiegando cosa non è testabile e perché.

- [ ] **Step 7: Esegui tutta la suite**

Run: `python -m pytest -q`
Expected: 51 passed (29 + 14 + 8).

- [ ] **Step 8: Verifica sul database vero (stessi numeri di Power BI)**

Con il database avviato e popolato (`docker compose up -d --wait`, `python -m etl.run_etl`):
```powershell
python -c "from sqlalchemy import create_engine; from etl import config; from app import queries as q; e = create_engine(config.db_url()); print(q.standings(e, '2025/26').head(3).to_string(index=False)); print(q.team_summary(e, '2025/26', 'Juventus')); t = q.season_trends(e).round(2); print(t.to_string(index=False))"
```
Expected, gli stessi numeri della dashboard Power BI:
- classifica 2025/26: **Inter 1ª, 87 punti** (27V 6N 5P, 89-35, +54), Napoli 2ª con 76, Roma 3ª con 73;
- Juventus 2025/26: `punti` **69**, `gol_fatti` **61**, `gol_subiti` **34**, `conversione_tiri` ≈ **0,0953**;
- tendenze: 2016/17 → gol 2,96, vittorie in casa 0,48, gialli 4,40, rossi 0,25, falli 27,93; 2025/26 → 2,43, 0,39, 3,70, 0,18, 25,35.

Poi avvia l'app e controllala nel browser:
```powershell
python -m streamlit run app/main.py --server.headless true --server.port 8501
```
Apri `http://localhost:8501`, visita le 4 pagine e controlla che i numeri coincidano. Poi spegni MySQL (`docker compose stop`), ricarica la pagina e verifica che compaia il messaggio "Database non raggiungibile" (non una traccia di errore); riaccendilo (`docker compose start`) e ricarica. Ferma l'app (Ctrl+C).

- [ ] **Step 9: Documentazione**

- `README.md`: nella sezione "Come eseguirlo" aggiungi "**App Streamlit**: con il database avviato, `python -m streamlit run app/main.py` e apri http://localhost:8501" e una riga nella struttura (`app/`); nella sezione "Cosa fa" aggiungi l'app; rimuovi "Frontend Streamlit" da "Prossimi passi"; aggiorna il numero di test.
- `docs/spiegazioni/09-streamlit.md`: completa le sezioni (perché le query sono separate dalle pagine e come si testano su SQLite, `Decimal` di MySQL, `st.cache_data`/`st.cache_resource`, `st.navigation`, `AppTest`, differenza tra Power BI e Streamlit sugli stessi dati).
- `docs/milestones/M4-frontend-streamlit.md` e `docs/milestones/README.md`: spunta le task e segna M4 come completata.

- [ ] **Step 10: Commit**

```powershell
git add app tests README.md docs
git commit -m "feat: app Streamlit con pagine Classifica, Squadra, Confronti e Disciplina"
```

---

## Self-Review

- **Copertura spec (sezione Frontend Streamlit):** `queries.py` testato su SQLite (Task 2), `db.py` con controllo (Task 3), `data.py` con cache (Task 3), 4 pagine in `app/views/` (Task 3), coerenza con Power BI (regola di classifica e medie, verifica sul database vero nel Task 3 Step 8), gestione degli errori (database spento, squadra senza partite, tiri mancanti), esecuzione con `python -m streamlit run app/main.py`.
- **Review Focus:** `Decimal` → `to_numbers` con test (Task 2); squadra che non ha giocato → `team_summary` restituisce `None` con test e pagina con messaggio (Task 2 e 3); tiri mancanti → `conversione_tiri = None` e "n/d" (Task 2 e 3); database spento → `check_connection` con test e messaggio in `main.py` (Task 3); parità → test con tabelle minime (Task 2).
- **Placeholder:** nessuno.
- **Coerenza dei nomi:** colonne e firme di `queries.py` coincidono tra Interfaces, test e codice; `data.py` usa gli stessi nomi nelle pagine e nei test (`app.db.get_engine` sostituito dalla fixture).
- **Limiti noti:** il codice del piano non è stato eseguito: in particolare vanno confermati dai test la compatibilità di Streamlit con pandas 3 / Python 3.14 (Task 1 Step 2), la conversione dei `Decimal` e il comportamento di `AppTest` con SQLite su thread diversi.
