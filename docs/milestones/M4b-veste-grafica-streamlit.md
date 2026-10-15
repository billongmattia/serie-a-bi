# M4b – Frontend Streamlit, fase 2: veste grafica

**Stato:** 📝 proposta · si pianifica **dopo** M4 (fase 1, funzionale) · **Riferimento:** [mockup](../design/README.md)

**Obiettivo:** dare all'app Streamlit l'aspetto del mockup (tema scuro, schede KPI, tab, forma recente a pallini), **senza cambiare la logica** testata in M4 e con numeri sempre calcolati dal database.

## Perché in due fasi
La parte rischiosa è che i numeri siano giusti e testati (M4). La veste grafica si costruisce sopra, senza rifare le query e senza rimettere in discussione i test.

## Task proposte (da dettagliare in un piano)
- [ ] **M4b.1 Tema** – `.streamlit/config.toml` con la palette (blu scuro, blu, rosso, giallo) e un tema Plotly coerente.
- [ ] **M4b.2 Componenti** – piccole funzioni per le schede KPI (icona, valore, nota) e per i pallini della forma.
- [ ] **M4b.3 Classifica** – schede con partite, gol totali, % vittorie in casa, pareggi e vittorie in trasferta; colonna "Ultime 5" a pallini (serve una query in più, con test).
- [ ] **M4b.4 Squadra** – tab Panoramica / Andamento / Dettaglio; gol fatti e subiti casa vs trasferta; ultime 5 partite con l'avversario; posizione in classifica accanto ai punti.
- [ ] **M4b.5 Confronti** – selettore del periodo; grafici ad area con etichette.
- [ ] **M4b.6 Disciplina** – schede del totale della stagione, confronto percentuale con la prima stagione (es. "−22,6% vs 2016/17"), tab Panoramica / Falli / Cartellini.
- [ ] **M4b.7 Pagine leggere** – Home (panoramica), Insight (legge `docs/insights.md`), About (legge il README).
- [ ] **M4b.8 Verifica e documentazione** – numeri uguali a Power BI e al database; screenshot **reali** per il README; spiegazione.

## Fuori perimetro
Statistiche e tab "Giocatori" (nessun dato), marcature Champions/Europa/retrocessione, immagine di stadio con licenza, pagina "Partite" (rimandata).

## Fatto quando
L'app somiglia al mockup, tutti i numeri coincidono con il database, i test passano e il README mostra screenshot reali dell'app.
