# 09 – Frontend Streamlit (fase 1: funzionale)

## Cosa ho fatto
- Aggiunto `streamlit` e `plotly` a `requirements.txt` (versioni installate: Streamlit 1.66, Plotly 7.1, compatibili con pandas 3.0 e Python 3.14).
- Scritto `app/queries.py`: 8 funzioni che leggono il database e restituiscono tabelle pandas (classifica, forma recente, riepilogo squadra, punti casa/trasferta, tendenze tra stagioni, disciplina, elenco stagioni e squadre).
- Scritto `app/db.py`, `app/data.py`, le 4 pagine in `app/views/` e `app/main.py`.
- Scritto **22 test**: 14 sulle query e 8 su connessione e pagine, più una fixture (`tests/conftest.py`) con un **mini-campionato di 3 squadre** i cui risultati sono stati calcolati a mano.
- Controllato l'app sul database vero: gli stessi numeri di Power BI.

## Perché
Power BI è lo strumento giusto per un lavoro di BI, ma richiede Windows e un programma da installare. Un'app web in Python mostra le stesse analisi nel browser e dimostra un'altra competenza: **SQL + pandas + visualizzazione** scritti e testati da te. Le due soluzioni leggono lo stesso database: sono due "frontend" dello stesso data warehouse.

## Come funziona (codice spiegato)

### La divisione in strati
```
MySQL → app/queries.py → app/data.py → app/views/* → browser
        logica testata    cache         presentazione
```
- **`queries.py`** contiene la **logica**. Ogni funzione riceve una connessione (`engine`) e restituisce un DataFrame: non sa nulla di Streamlit. Per questo si può testare con pytest, come l'ETL, su un database SQLite temporaneo.
- **`data.py`** avvolge ogni funzione con `@st.cache_data(ttl=600)`: Streamlit rilancia lo script a ogni click, e la cache evita di rifare la stessa query ogni volta.
- **`views/*.py`** sono le pagine: scelgono i filtri (`st.selectbox`), chiamano `data.*` e disegnano tabelle e grafici. Non contengono calcoli.
- **`main.py`** controlla il database e crea la navigazione con `st.navigation`.

### Le query
- **La classifica** somma punti, gol e risultati per squadra con `GROUP BY`, poi in pandas calcola la posizione con `rank(method="dense")` su `punti × 1000 + differenza reti`: è la stessa regola della misura DAX `Posizione` in Power BI.
- **Le medie "a partita"** dividono per `COUNT(DISTINCT match_key)` (le partite distinte), perché nella tabella dei fatti ogni partita ha **due righe**. Moltiplicare per `1.0` evita la divisione tra interi.
- **`to_numbers`**: MySQL restituisce i risultati di `SUM` e delle medie come `Decimal`, SQLite come numeri normali. I test girano su SQLite, quindi senza questa conversione un errore dei `Decimal` si sarebbe visto solo sul database vero.
- **`team_summary`** restituisce `None` se la squadra non ha partite nella stagione, e `conversione_tiri = None` se mancano i tiri: le pagine mostrano un messaggio o "n/d" invece di un errore.

### I test
- La fixture `warehouse` costruisce un campionato minuscolo (3 squadre, 6 partite + 1) e lo carica nello schema vero. Poiché i risultati sono scelti da noi, **i valori attesi si calcolano a mano**: per esempio A fa 10 punti (3 vittorie e 1 pareggio), B 1, C 5. Se la query sbaglia, il test lo vede.
- Un test usa tabelle minime per verificare le **parità**: due squadre con gli stessi punti e la stessa differenza reti hanno la stessa posizione.
- Per le pagine si usa `AppTest` di Streamlit: esegue la pagina senza aprire un browser e permette di controllare che non ci siano eccezioni e che compaiano i 4 indicatori. La fixture sostituisce `app.db.get_engine` con il database di prova, e `data.py` chiama `db.get_engine()` **al momento dell'uso** proprio perché questo funzioni.

### Gestione degli errori
Se MySQL è spento, `check_connection` fallisce e `main.py` mostra `Database non raggiungibile. Avvia MySQL con docker compose up -d --wait`, poi `st.stop()`. Verificato a mano: fermato il database, la pagina mostra il messaggio; riavviato, l'app si riprende al ricaricamento.

## Verifica sul database vero
Le query girano sul MySQL con gli stessi numeri di Power BI: Inter prima con 87 punti, Juventus 2025/26 con 69 punti, 61 gol fatti, 34 subiti, 9,53% di conversione, casa 37 e trasferta 32 punti, e le tendenze stagione per stagione (per esempio gol a partita 2,96 nel 2016/17 e 2,43 nel 2025/26). La pagina Squadra mostra per l'Atalanta 59 punti, 51 gol fatti, 36 subiti e 9,07%, uguali alla classifica.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d --wait            # database acceso
python -m streamlit run app/main.py    # si apre su http://localhost:8501
python -m pytest                       # 51 test
```

## Concetti da studiare
- **Separare logica e presentazione**: perché le query stanno fuori dalle pagine e si testano da sole.
- **Cache** in Streamlit: `st.cache_data` (dati) contro `st.cache_resource` (risorse come la connessione).
- **Il modello di esecuzione di Streamlit**: a ogni interazione lo script riparte dall'inizio.
- `Decimal` contro `float`, e perché MySQL e SQLite si comportano in modo diverso.
- **Testare senza il database vero** usando dati piccoli e calcolati a mano.
- Differenza tra uno strumento a clic (Power BI) e uno scritto in codice (Streamlit): quando conviene l'uno o l'altro.

## Revisione finale (fatta dall'autore, non da un revisore indipendente)
**Trovato e corretto:** l'app, avviata senza opzioni, **ascoltava su tutte le interfacce di rete** (nel log compaiono un "Network URL" e un "External URL"): chiunque nella rete locale avrebbe potuto aprirla e leggere il database, mentre la decisione era "solo in locale". Ora `.streamlit/config.toml` imposta `server.address = "localhost"`. Un test (`test_streamlit_listens_on_localhost_only`) controlla il file e, a mano, ho verificato a runtime che l'app ascolta solo su `127.0.0.1` e che l'indirizzo di rete del PC rifiuta la connessione. La suite passa da 51 a **52 test**.

**Rimandato (impatto basso):**
- `app/main.py` (controllo del database e navigazione) è verificato a mano ma non da un test automatico.
- I dati sono in cache per 10 minuti: dopo aver rilanciato l'ETL l'app può mostrare valori vecchi fino a 10 minuti (o fino al riavvio).
- Nel grafico dei gialli per squadra Plotly mostra una etichetta sì e una no (grafico basso).
- Gli screenshot dell'app mancano: si fanno in M4b, con la nuova grafica.

**Cosa imparare:** i valori predefiniti dei programmi non sono quelli che hai deciso tu. "Solo in locale" è una decisione che va **scritta nella configurazione e verificata**, non data per scontata.

## Cose da migliorare in fase 2 (veste grafica)
- Nel grafico delle ammonizioni per squadra Plotly mostra una etichetta sì e una no perché il grafico è basso: va alzato.
- Tema scuro personalizzato, schede KPI, forma recente a pallini, tab: vedi [M4b](../milestones/M4b-veste-grafica-streamlit.md) e il [mockup](../design/README.md).
