# M2 – Pipeline dati (ETL)

**Stato:** ✅ completata · **Piano:** Task 2–5 · **Spiegazioni:** [02](../spiegazioni/02-extract.md), [03](../spiegazioni/03-profiling.md), [04](../spiegazioni/04-transform.md), [05](../spiegazioni/05-load-qualita-etl.md)

**Obiettivo:** portare i risultati della Serie A 2016/17 → 2025/26 dalla fonte DataHub al data warehouse, in modo ripetibile e controllato.

## Task
- [x] **M2.1 Extract** – scaricare i 10 CSV con cache e rifiuto delle risposte che non sono CSV (`etl/extract.py`).
- [x] **M2.2 Profiling** – lettura dei CSV grezzi e matrice di copertura delle colonne (`etl/rawio.py`, `etl/profiling.py`, `docs/coverage.md`).
- [x] **M2.3 Transform** – pulizia e costruzione di `dim_match` e `fact_team_match` con una riga per squadra per partita (`etl/transform.py`).
- [x] **M2.4 Load** – staging grezzo e caricamento idempotente dello star schema (`etl/load.py`).
- [x] **M2.5 Qualità** – controlli SQL e riconciliazione con i punti ufficiali dei campioni (`sql/03_quality_checks.sql`, `etl/quality.py`).
- [x] **M2.6 Orchestrazione** – `etl/run_etl.py` con log ed exit code.

## Risultati
- 3.800 partite, 7.600 righe di fatto, 34 squadre, 0 righe scartate.
- ETL rilanciato due volte con conteggi identici (idempotente).
- Juventus 2016/17 = 91 punti, Inter 2023/24 = 94 punti, come da classifiche ufficiali.
- 24 test automatici verdi.

## Fatto quando
`python -m etl.run_etl` termina con `ETL terminato: OK` e `python -m pytest` è verde.
