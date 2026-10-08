# M4 – Frontend Streamlit

**Stato:** 🔄 decisioni prese (2026-10-08), piano scritto, **in attesa della revisione del piano** · **Piano:** [2026-10-08-streamlit-frontend](../superpowers/plans/2026-10-08-streamlit-frontend.md)

**Obiettivo:** un'app web in Python, con **Streamlit** e **Plotly**, che mostra le stesse analisi della dashboard Power BI leggendo lo stesso database MySQL. Mostra una competenza in più (Python + SQL + visualizzazione) e funziona senza Power BI.

## Decisioni (2026-10-08)
1. Streamlit si **aggiunge** a Power BI (non lo sostituisce).
2. **Solo in locale**: nessuna pubblicazione online.
3. Grafici con **Plotly**.

## Idea di architettura
```
MySQL (star schema)  →  app/queries.py  →  app/data.py  →  app/views/*  →  browser
                         SQL + pandas,       cache          Streamlit + Plotly
                         testate (SQLite)
```
- **Le query sono la logica di business**: ricalcolano classifica, medie e percentuali, e sono testate con pytest su SQLite (stesso approccio dell'ETL).
- Le pagine fanno solo presentazione: filtri, grafici, tabelle.
- Si riusa `etl.config.db_url()` per la connessione.

## Task (corrispondono ai Task 1–3 del piano)
- [ ] **M4.1 Dipendenze e dati di test** – `streamlit` e `plotly` in `requirements.txt`; fixture `warehouse` con un mini-campionato dai risultati calcolati a mano.
- [ ] **M4.2 Query e test** – `app/queries.py`: elenco stagioni e squadre, classifica, forma recente, riepilogo squadra, punti casa/trasferta, tendenze tra stagioni, disciplina. Test scritti prima del codice.
- [ ] **M4.3 Guscio dell'app** – `app/db.py` (connessione e controllo del database), `app/data.py` (cache), `app/main.py` con la navigazione e il messaggio di errore se il database è spento.
- [ ] **M4.4 Pagina Classifica** – selettore stagione, tabella con posizione, V/N/P, gol, differenza reti, punti; forma recente (ultime 5, con avversario).
- [ ] **M4.5 Pagina Squadra** – selettori stagione e squadra, 4 indicatori, grafico casa/trasferta.
- [ ] **M4.6 Pagina Confronti tra stagioni** – gol a partita, % vittorie in casa, gialli e rossi, per stagione.
- [ ] **M4.7 Pagina Disciplina e gioco duro** – gialli, falli e rossi per squadra e andamento dei falli.
- [ ] **M4.8 Verifica sul database vero** – i numeri coincidono con quelli di Power BI; test dei casi limite.
- [ ] **M4.9 Documentazione** – README, `docs/spiegazioni/09-streamlit.md`, screenshot (facoltativi), milestone.

## Fatto quando
`python -m streamlit run app/main.py` mostra le 4 pagine con gli stessi numeri di Power BI, il messaggio di errore compare se il database è spento, e i test passano.
