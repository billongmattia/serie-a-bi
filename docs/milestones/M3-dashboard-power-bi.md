# M3 – Dashboard Power BI

**Stato:** 🔄 in corso · **Piano:** Task 6 · **Spiegazione:** `06-power-bi.md` (da scrivere a fine milestone)

**Obiettivo:** un modello Power BI e una dashboard a 4 pagine sopra il data warehouse, da mostrare nel CV.

## Task
- [x] **M3.1** Scrivere il dizionario dati ([`../data_dictionary.md`](../data_dictionary.md)).
- [x] **M3.2** Scrivere e documentare le misure DAX ([`../dax/misure.md`](../dax/misure.md)).
- [x] **M3.3** Installare Power BI Desktop e il connettore MySQL (MySQL Connector/NET).
- [x] **M3.4** Importare le 5 tabelle del modello da `localhost:3308`, database `serie_a`.
- [x] **M3.5** Creare le relazioni (`dim_match → fact_team_match`, `dim_team → fact_team_match` attiva e inattiva per l'avversario, `dim_date` e `dim_season → dim_match`) e segnare `dim_date` come tabella data.
- [ ] **M3.6** Creare le misure DAX nella tabella "Misure".
- [ ] **M3.7** Costruire la pagina **Classifica** (con forma recente).
- [ ] **M3.8** Costruire la pagina **Squadra**.
- [ ] **M3.9** Costruire la pagina **Confronti tra stagioni**.
- [ ] **M3.10** Costruire la pagina **Disciplina e gioco duro**.
- [ ] **M3.11** Salvare `powerbi/dashboard.pbix` ed esportare uno screenshot per pagina in `powerbi/screenshots/`.
- [ ] **M3.12** Scrivere `docs/spiegazioni/06-power-bi.md` (relazioni, contesto di filtro, `CALCULATE`, `DIVIDE`, `RANKX`).

## Note
- I passi da M3.3 a M3.11 si fanno nell'interfaccia di Power BI Desktop: li eseguiamo insieme, io guido e tu clicchi.
- Credenziali del database: utente `serie_a`, password `serie_a_pw`.

## Fatto quando
Il `.pbix` si apre, le 4 pagine mostrano i dati e gli screenshot sono salvati.
