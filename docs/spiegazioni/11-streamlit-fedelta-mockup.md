# 11 – Streamlit: lo stile identico al mockup (M4c)

## Cosa ho fatto
Ho rifatto l'aspetto dell'app Streamlit perché somigli al [mockup](../design/README.md): cornice blu scuro con **pannelli bianchi**, sidebar con logo "SERIE A / ANALYTICS" e icone, intestazione con la scritta piccola, il titolo con "ANALYTICS" in blu e i **selettori dentro l'intestazione**, schede KPI con icona colorata, tabella della classifica con le colonne abbreviate (`Pos Squadra G V N P GF GS DR Punti Ultime 5`) e la forma a cerchi, ultime partite con badge V/N/P, grafici ad area con sfumatura. **Solo stile:** le pagine e i numeri sono gli stessi di prima. Non ho aggiunto nulla che il dataset non ha (giocatori, elenco partite, zone Champions, immagine di stadio).

## Perché c'è stata una terza versione (la lezione più importante)
La versione precedente (M4b) aveva i numeri giusti ma **non somigliava al mockup**: era tutta scura, mentre il mockup ha pannelli bianchi. Il mio controllo di allora verificava i **dati** (che i numeri coincidessero con il database) ma non l'**aspetto**: ho interpretato "tema scuro" senza confrontare la pagina con l'immagine. In un lavoro di grafica, "funziona" e "è fatto come richiesto" sono due verifiche diverse: la seconda si fa **guardando le due cose affiancate**, pagina per pagina, con una lista di controllo.

## Come funziona (codice spiegato)

### Il tema chiaro e il CSS che lo ribalta
Il tema di Streamlit è **chiaro** (`.streamlit/config.toml`): così i pannelli bianchi hanno testo scuro senza sforzi. Un blocco CSS (`app/styles.py`) porta in scuro solo lo **sfondo** della pagina, la **sidebar** e l'**intestazione**. I contenitori con una **chiave** (`st.container(key="hero")` e `key="panel"`) diventano classi CSS (`.st-key-hero`, `.st-key-panel`) a cui agganciare gli stili.

### Componenti HTML puri e testati
`app/ui.py` contiene funzioni che costruiscono pezzetti di HTML (`kpi_html`, `standings_html`, `recent_matches_html`, `table_html`, `logo_html`…): sono funzioni pure, cioè dato lo stesso input restituiscono la stessa stringa, e per questo si testano facilmente. Le pagine le mostrano con `st.markdown(..., unsafe_allow_html=True)`.

### L'escape è obbligatorio
Quando si inserisce HTML in una pagina, ogni valore che arriva dall'esterno (qui: i nomi delle squadre, che vengono dal database) va **protetto con `html.escape`**: `<` diventa `&lt;`, così un valore come `<script>…` resta testo e non diventa codice (è l'attacco chiamato **XSS**). La funzione `esc()` lo fa, e c'è una classe `Html` (una stringa "fidata") solo per i pezzi che costruiamo noi, come i cerchi della forma. I test verificano che un nome come `<b>X</b>` esca protetto.

### Come l'HTML non viene rovinato dal Markdown
Streamlit interpreta il testo come Markdown: una **riga vuota** o un **rientro di 4 spazi** dentro l'HTML lo trasformerebbero in un blocco di codice. Per questo ogni funzione produce l'HTML **su una riga sola**, e un test controlla che non ci siano a capo.

### Il menu laterale con la voce attiva
Il menu predefinito di Streamlit è nascosto (`st.navigation(..., position="hidden")`) e al suo posto ci sono il logo, un `st.page_link` per pagina (con le icone Material) e il riepilogo del database. Per colorare di blu pieno la voce attiva ho scoperto, **guardando il DOM del browser**, che Streamlit non la marca con un attributo stabile (solo con una classe generata, che cambia a ogni versione). Soluzione: ogni voce è dentro un contenitore la cui **chiave** vale `nav_active` se è la pagina corrente (`ui.nav_container_key`), e il CSS colora `.st-key-nav_active`.

### I grafici in stile chiaro
`app/charts.py` usa il tema `plotly_white` con sfondo trasparente, la **sfumatura** sotto la linea (`fillgradient`), le barre blu e rosse, la **legenda in alto** e **nessun titolo del grafico**: il titolo con l'icona sta sopra, in HTML, come nel mockup. L'asse y è centrato sui dati, le etichette delle stagioni sono orizzontali e i decimali sono con la virgola.

## Cosa ho trovato guardando l'app (e corretto)
1. **La voce attiva del menu non diventava blu**: il selettore `aria-current` non esiste. Corretto con la chiave del contenitore (sopra).
2. **Titoli degli assi e etichette inclinate** che nel mockup non ci sono: tolti, con un test.
3. **Disciplina**: le schede dei totali stavano a tutta larghezza in fondo; nel mockup stanno sotto il grafico di destra. Spostate.
4. **Cinque schede KPI su due righe**: ridotta la larghezza minima perché stiano su una riga.
5. **Pagina d'errore (database spento)**: il riquadro rosso aveva poco contrasto sul nuovo sfondo scuro; ora è bianco con testo scuro e il CSS viene caricato prima del controllo.
6. **Un errore mio nella verifica**: avevo rimpicciolito la pagina con lo zoom CSS per vederla intera, ma Plotly misura le schede già rimpicciolite e disegnava i grafici troppo piccoli, facendomi credere a un difetto che non c'era. Lezione: lo strumento con cui verifichi può falsare quello che vedi; se un risultato è strano, controlla i valori reali (`getBoundingClientRect`, ecc.) prima di correggere il codice.

## Cosa è rimasto diverso dal mockup (consapevolmente)
- **Icone:** emoji in cerchi colorati, non le icone disegnate del mockup.
- **Intestazione:** gradienti e un triangolo in CSS al posto dell'immagine di stadio.
- **"Periodo" in Confronti:** un cursore a due estremi, non un menu a tendina.
- **Barrette colorate** a sinistra della classifica (Champions/Europa/retrocessione): non ci sono nei dati.
- **Voci e tab senza dati** (Statistiche giocatori, Partite, Giocatori, Dettaglio partite, Confronto): non inclusi, come richiesto.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d --wait
python -m streamlit run app/main.py     # http://localhost:8501
python -m pytest                        # 96 test
```

## Cose rimandate (impatto basso)
- I selettori CSS dipendono dalla struttura interna di Streamlit: un aggiornamento importante della libreria potrebbe richiedere di riguardare l'aspetto (i test proteggono i contenuti, non l'estetica).
- Il testo di About contiene numeri fissi (10 stagioni, 2016/17–2025/26).
- La cache dei dati dura 10 minuti.

## Concetti da studiare
- Verificare un lavoro **grafico**: confronto affiancato con la richiesta, non solo test sui dati.
- **XSS** ed **escape** dell'HTML.
- Funzioni **pure** (stesso input, stesso output) e perché si testano meglio.
- CSS: selettori, `!important`, perché non conviene appoggiarsi a classi generate.
- `st.container(key=...)`, `st.page_link`, `st.navigation(position="hidden")`, `st.tabs`.
