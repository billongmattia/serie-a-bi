# M4b – Frontend Streamlit, fase 2: veste grafica

**Stato:** 🔄 piano scritto (2026-10-15), **in attesa di revisione e via libera** · **Piano:** [2026-10-15-streamlit-veste-grafica](../superpowers/plans/2026-10-15-streamlit-veste-grafica.md) · **Riferimento:** [mockup](../design/README.md)

**Obiettivo:** dare all'app Streamlit l'aspetto del mockup (tema scuro, schede KPI, tab, forma recente a pallini), **senza cambiare la logica** testata in M4 e con numeri sempre calcolati dal database.

## Perché in due fasi
La parte rischiosa è che i numeri siano giusti e testati (M4). La veste grafica si costruisce sopra, senza rifare le query già esistenti e senza rimettere in discussione i loro test.

## Task (corrispondono ai Task 1–5 del piano)
- [ ] **M4b.1 Tema, componenti e grafici** – tema scuro in `config.toml`; `app/theme.py`, `app/ui.py` (formati italiani, schede KPI, pallini della forma, variazioni percentuali), `app/charts.py` (area con etichette, barre orizzontali con tutte le etichette, barre raggruppate).
- [ ] **M4b.2 Query nuove** – panoramica della stagione, forma per squadra, gol casa/trasferta, punti per stagione, totali di disciplina, panoramica del database, campioni. Test su SQLite e prova sul MySQL vero.
- [ ] **M4b.3 Classifica e Squadra** – 5 schede KPI, colonna "Ultime 5" a pallini; Squadra con 5 schede e tab Panoramica / Andamento.
- [ ] **M4b.4 Confronti, Disciplina e pagine nuove** – selettore del periodo e grafici ad area; Disciplina con variazione rispetto alla prima stagione e 3 tab; **Home**, **Insight** (legge `docs/insights.md`), **About**; sidebar con i dati del database.
- [ ] **M4b.5 Verifica, screenshot, documentazione e revisione** – numeri uguali al database e a Power BI; screenshot **reali** dell'app (a cura dell'utente); README; spiegazione `10-streamlit-veste-grafica.md`; revisione finale.

## Fuori perimetro
Statistiche e tab "Giocatori" (nessun dato), marcature Champions/Europa/retrocessione, immagine di stadio con licenza, pagina "Partite".

## Fatto quando
L'app somiglia al mockup, tutti i numeri coincidono con il database, i test passano e il README mostra screenshot reali dell'app.
