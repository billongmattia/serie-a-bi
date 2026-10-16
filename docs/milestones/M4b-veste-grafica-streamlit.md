# M4b – Frontend Streamlit, fase 2: veste grafica

**Stato:** ✅ completata il 2026-10-16 (resta solo da fare, a cura dell'utente, la cattura degli screenshot reali dell'app) · **Piano:** [2026-10-15-streamlit-veste-grafica](../superpowers/plans/2026-10-15-streamlit-veste-grafica.md) · **Riferimento:** [mockup](../design/README.md)

**Obiettivo:** dare all'app Streamlit l'aspetto del mockup (tema scuro, schede KPI, tab, forma recente a pallini), **senza cambiare la logica** testata in M4 e con numeri sempre calcolati dal database.

## Perché in due fasi
La parte rischiosa è che i numeri siano giusti e testati (M4). La veste grafica si costruisce sopra, senza rifare le query già esistenti e senza rimettere in discussione i loro test.

## Task (corrispondono ai Task 1–5 del piano)
- [x] **M4b.1 Tema, componenti e grafici** – tema scuro in `config.toml`; `app/theme.py`, `app/ui.py` (formati italiani, schede KPI, pallini della forma, variazioni percentuali), `app/charts.py` (area con etichette, barre orizzontali con tutte le etichette, barre raggruppate).
- [x] **M4b.2 Query nuove** – panoramica della stagione, forma per squadra, gol casa/trasferta, punti per stagione, totali di disciplina, panoramica del database, campioni. Test su SQLite e prova sul MySQL vero.
- [x] **M4b.3 Classifica e Squadra** – 5 schede KPI, colonna "Ultime 5" a pallini; Squadra con 5 schede e tab Panoramica / Andamento.
- [x] **M4b.4 Confronti, Disciplina e pagine nuove** – selettore del periodo e grafici ad area; Disciplina con variazione rispetto alla prima stagione e 3 tab; **Home**, **Insight** (legge `docs/insights.md`), **About**; sidebar con i dati del database.
- [x] **M4b.5 Verifica, documentazione e revisione** – numeri verificati sul database vero e nel browser, pagina per pagina; README; spiegazione `10-streamlit-veste-grafica.md`; revisione finale (4 difetti trovati guardando l'app e corretti con test).
- [ ] **M4b.6 Screenshot reali dell'app** – a cura dell'utente: 4 immagini in `docs/screenshots/` (`streamlit-classifica.png`, `streamlit-squadra.png`, `streamlit-confronti.png`, `streamlit-disciplina.png`) e poi la tabella 2×2 nel README.

## Fuori perimetro
Statistiche e tab "Giocatori" (nessun dato), marcature Champions/Europa/retrocessione, immagine di stadio con licenza, pagina "Partite".

## Fatto quando
L'app somiglia al mockup, tutti i numeri coincidono con il database, i test passano e il README mostra screenshot reali dell'app.
