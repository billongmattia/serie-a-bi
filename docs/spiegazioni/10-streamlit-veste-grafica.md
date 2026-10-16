# 10 – Streamlit: la veste grafica (M4b)

## Cosa ho fatto
- Dato all'app il tema scuro (blu, rosso, giallo) ispirato al [mockup](../design/README.md).
- Aggiunto tre moduli di sola presentazione: `app/theme.py` (colori), `app/ui.py` (formati italiani e componenti) e `app/charts.py` (grafici).
- Aggiunto 7 query nuove in `app/queries.py` e i relativi involucri con cache in `app/data.py`.
- Riscritto le pagine **Classifica** e **Squadra**; rinnovato **Confronti** e **Disciplina**; aggiunto **Home**, **Insight** e **About** e una sidebar con i dati del database.
- Verificato tutto sul database vero, nel browser, pagina per pagina.

La logica già testata nella fase 1 **non è stata cambiata**: i 52 test di allora sono rimasti verdi senza modifiche. Oggi i test sono **83** (29 sull'ETL e 54 sull'app).

## Perché
Un'app funzionante ma spoglia convince meno di una che si legge a colpo d'occhio. La veste grafica però si costruisce **sopra** la logica, non dentro: così si può cambiare l'aspetto senza rischiare di rompere i numeri, e i test delle query continuano a proteggere i risultati.

## Come funziona (codice spiegato)

### I tre moduli nuovi
- **`ui.py`** contiene piccole funzioni pure e testabili:
  - `fmt_number(1542)` → `1.542` e `fmt_number(2.6158, 2)` → `2,62`: il formato numerico italiano (punto per le migliaia, virgola per i decimali), che Python di per sé non offre;
  - `fmt_percent`, `fmt_signed_percent` (`-22,6%`), `pct_change` (variazione percentuale che restituisce `None` se la base è zero o mancante, invece di un errore);
  - `form_dots("WDL")` → `🟢⚪🔴`: la forma recente a pallini;
  - `kpi(...)`: una scheda numerica con `st.metric(border=True)`, con una nota grigia o una variazione con freccia.
- **`charts.py`** costruisce i grafici Plotly con lo stesso stile: sfondo trasparente (si vede il tema dell'app), colori dal modulo `theme`, formato italiano (`separators=",."`). Tre tipi: grafico **ad area** (linea con riempimento ed etichette), **barre orizzontali** (con tutte le etichette) e **barre raggruppate**.
- **`theme.py`** raccoglie i colori in un posto solo.

### Il tema e il CSS
Il tema (sfondo, colore principale, testo) sta in `.streamlit/config.toml`: Streamlit lo applica da solo. Il CSS serve solo per l'intestazione con il gradiente (`.hero`). **L'HTML si usa solo con testi fissi scritti nel codice**: se si inserissero valori letti dal database in un blocco HTML, un valore malevolo potrebbe iniettare codice (è l'attacco chiamato XSS). Per questo la Home mostra il sommario con `st.caption`, non nell'intestazione.

### Le pagine
- **Classifica:** 5 schede (partite, gol totali, vittorie in casa, pareggi, vittorie in trasferta) e la tabella con la colonna "Ultime 5" a pallini (la partita più vecchia a sinistra).
- **Squadra:** 5 schede e due tab (`st.tabs`): Panoramica (gol fatti e subiti in casa e in trasferta, ultime 5 partite con l'avversario) e Andamento (punti e gol stagione per stagione).
- **Confronti:** un selettore del periodo (`st.select_slider` a due estremi) e 4 grafici ad area.
- **Disciplina:** 3 schede con la variazione percentuale rispetto alla prima stagione (per esempio falli −9,2%) e 3 tab.
- **Home, Insight, About:** panoramica con i campioni di ogni stagione, il file `docs/insights.md` mostrato come pagina, e una descrizione del progetto.

### Cosa ho preso dal mockup e cosa no
Ho preso: tema scuro, schede, tab, forma a pallini, confronti percentuali, grafici ad area. Non ho incluso, perché non ci sono i dati: statistiche e tab "Giocatori" e le zone Champions/retrocessione. Non ho usato l'immagine di stadio (servirebbe un'immagine con licenza libera).

## Cosa ho trovato guardando l'app (e corretto, con test prima)
1. **Gli assi partivano da zero** e appiattivano le tendenze (i gol a partita sembravano costanti): ora l'asse è centrato sui dati (`_padded_range`). Un test controlla che non parta da zero, che non scenda mai sotto zero per dati positivi e che regga un valore solo.
2. **Etichette tagliate** agli estremi (come "2,96" e "2,43") e nelle barre: ora `cliponaxis=False` e spazio a destra.
3. **Decimali con il punto** nei grafici (`2.34`): ora `separators=",."`, quindi `2,34` come nel resto dell'app.
4. **La Home dichiarava un indirizzo `/home`**, mentre la pagina predefinita vive sulla radice: causava un avviso "Page not found" aprendo quell'indirizzo. Tolto l'indirizzo.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d --wait
python -m streamlit run app/main.py     # http://localhost:8501
python -m pytest                        # 83 test
```

## Cose rimandate (impatto basso)
- Le tabelle (`st.dataframe`) mostrano i decimali col punto (usano il formato del browser): non si cambia facilmente senza trasformarle in testo.
- Il selettore del periodo in Confronti è verificato a mano, non da un test che controlli i grafici filtrati.
- Se il database è spento, il messaggio compare dopo alcuni secondi (il tentativo di connessione scade prima di arrendersi).
- La cache dei dati dura 10 minuti: dopo aver rilanciato l'ETL i valori possono restare vecchi fino al riavvio.

## Concetti da studiare
- Separare **logica** (query, formati) e **presentazione** (pagine, grafici, CSS).
- Il **formato dei numeri** per lingua (locale) e i suoi trabocchetti.
- **XSS** e perché non si inseriscono dati non fidati in HTML non filtrato.
- Asse y troncato contro asse da zero: quando serve e quando inganna (qui: tendenze di tassi, con il riempimento che va fino in fondo).
- `st.tabs`, `st.metric`, `st.select_slider` e i test con `AppTest`.
