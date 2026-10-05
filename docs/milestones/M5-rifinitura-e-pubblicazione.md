# M5 – Rifinitura e pubblicazione

**Stato:** ⏳ da fare · **Piano:** Task 7 + extra

**Obiettivo:** rendere il repository presentabile a un recruiter e riproducibile da chiunque lo cloni.

## Task
- [ ] **M5.1 README** – presentazione, screenshot, architettura, star schema, quickstart in pochi comandi, come aprire il `.pbix`, come avviare Streamlit (se M4), **citazione della fonte dati** (DataHub, licenza PDDL) e limiti (nessun arbitro).
- [ ] **M5.2 Insight** – `docs/insights.md` con 3–5 osservazioni sui dati, ciascuna col numero letto dalla dashboard.
- [ ] **M5.3 Verifica da zero** – `docker compose down -v`, `up`, `python -m etl.run_etl`, `python -m pytest`: tutto deve funzionare da database vuoto.
- [ ] **M5.4 Revisione finale del codice** – un controllo di tutto il lavoro prima della pubblicazione.
- [ ] **M5.5 Pubblicazione su GitHub** – creare o collegare il repository e fare il push (si decide insieme: nome, visibilità).
- [ ] **M5.6 Spiegazione** – `docs/spiegazioni/07-readme-e-rifinitura.md`.

## Extra opzionali (a progetto finito)
- [ ] Estendere il periodo oltre le 10 stagioni (basta cambiare `FIRST_SEASON`; le stagioni più vecchie avranno più `NULL`).
- [ ] CI con GitHub Actions (test automatici a ogni push).
- [ ] Convertire il `.pbix` in `.pbip` (formato testuale, più adatto a Git).
- [ ] Seconda dashboard in Metabase.

## Fatto quando
Un estraneo clona il repository, segue il README e ottiene gli stessi risultati.
