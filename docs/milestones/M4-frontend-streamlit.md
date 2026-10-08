# M4 – Frontend Streamlit

**Stato:** 📝 proposta, **da approvare** prima di essere aggiunta alla spec e al piano. · **Piano:** nuovo.

**Obiettivo:** un'app web in Python, con **Streamlit**, che mostra le stesse analisi della dashboard Power BI leggendo lo stesso database MySQL. Mostra una competenza in più (Python + SQL + visualizzazione) e funziona senza Power BI.

## Idea di architettura
```
MySQL (star schema)  →  app/queries.py  →  app/pages (Streamlit)  →  browser
                         query SQL +         grafici e tabelle
                         pandas, testate
```
- **Le query SQL sono la "logica di business"**: ricalcolano classifica, medie e percentuali, e sono testate con pytest su SQLite (stesso approccio dell'ETL).
- Le pagine Streamlit fanno solo presentazione: filtri, grafici, tabelle.
- Si riusa `etl.config.db_url()` per la connessione.

## Task proposte
- [ ] **M4.1 Setup** – aggiungere `streamlit` e un libreria per i grafici (Plotly o Altair) a `requirements.txt`; creare `app/main.py` con navigazione e `app/db.py` (connessione e cache dei risultati).
- [ ] **M4.2 Query e test** – scrivere in `app/queries.py` le funzioni (classifica per stagione, rendimento squadra, confronti tra stagioni, disciplina) con test su SQLite **prima** del codice.
- [ ] **M4.3 Pagina Classifica** – selettore stagione, tabella con posizione, partite, V/N/P, gol, differenza reti, punti, e forma recente (ultime 5).
- [ ] **M4.4 Pagina Squadra** – selettori squadra e stagione, schede riassuntive, confronto casa/trasferta.
- [ ] **M4.5 Pagina Confronti tra stagioni** – gol a partita, % vittorie in casa, cartellini, per stagione.
- [ ] **M4.6 Pagina Disciplina e gioco duro** – falli, gialli e rossi a partita per squadra e per stagione.
- [ ] **M4.7 Esecuzione e screenshot** – avvio con `streamlit run app/main.py`, controllo delle 4 pagine, screenshot in `docs/screenshots/`.
- [ ] **M4.8 Spiegazione** – `docs/spiegazioni/09-streamlit.md`.

## Decisioni aperte
1. **Streamlit si aggiunge a Power BI** (consigliato: due frontend sugli stessi dati, due competenze nel CV) o lo sostituisce?
2. **Solo in locale o anche online?** Streamlit Community Cloud non raggiunge il tuo MySQL locale: per pubblicarla servirebbe un database ospitato oppure un export dei dati in un file. Si può decidere dopo, a progetto finito.
3. **Libreria grafici:** Plotly (interattiva, consigliata) o Altair.

## Fatto quando
`streamlit run app/main.py` mostra le 4 pagine con dati corretti, e i test delle query passano.
