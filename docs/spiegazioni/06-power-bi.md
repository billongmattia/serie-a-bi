# 06 – Power BI: modello, misure e dashboard

## Cosa ho fatto
- Collegato Power BI Desktop al database MySQL (`localhost:3308`, database `serie_a`) e importato le 5 tabelle del modello.
- Creato le **relazioni** tra le tabelle e segnato `dim_date` come tabella data.
- Creato una tabella `Misure` con **17 misure DAX** (documentate in [`../dax/misure.md`](../dax/misure.md)).
- Costruito la dashboard a **4 pagine**: Classifica, Squadra, Confronti tra stagioni, Disciplina e gioco duro. File: [`../../powerbi/dashboard.pbix`](../../powerbi/dashboard.pbix); anteprime in [`../../powerbi/screenshots/`](../../powerbi/screenshots/).

## Perché
Il data warehouse contiene i dati, ma nessuno guarda le tabelle MySQL: la dashboard li trasforma in risposte (chi è primo? quanti gol si fanno per partita? quali squadre sono più ammonite?). Power BI è lo strumento più richiesto nelle offerte di lavoro di BI, quindi è la parte più spendibile del progetto.

## Come funziona

### 1. Il modello e le relazioni
Power BI non guarda il database a ogni click: **importa** i dati e li tiene in memoria. Le tabelle si collegano con **relazioni uno-a-molti**:

| Lato "uno" | Lato "molti" | Stato |
|---|---|---|
| `dim_match[match_key]` | `fact_team_match[match_key]` | attiva |
| `dim_team[team_key]` | `fact_team_match[team_key]` | attiva |
| `dim_team[team_key]` | `fact_team_match[opponent_team_key]` | **inattiva** |
| `dim_date[date_key]` | `dim_match[date_key]` | attiva |
| `dim_season[season_key]` | `dim_match[season_key]` | attiva |

- **Il filtro scorre dal lato "uno" al lato "molti"**, in una sola direzione. Scegliere una stagione in uno slicer filtra `dim_season`, poi `dim_match`, poi `fact_team_match`.
- **Perché la relazione verso l'avversario è inattiva:** tra due tabelle può esserci un solo percorso di filtro attivo. Una squadra compare nel fatto sia come `team_key` sia come `opponent_team_key`: la seconda resta inattiva e si userebbe con la funzione DAX `USERELATIONSHIP` solo se servisse.
- **Power BI aveva creato da solo** due relazioni in più (`home_team_key` e `away_team_key`), una delle quali attiva e sbagliata: rendeva **inattiva** la relazione giusta tra `dim_team` e il fatto. Le abbiamo eliminate. Lezione: le relazioni automatiche vanno sempre controllate.

### 2. La tabella data deve essere continua
Per segnare `dim_date` come tabella data, Power BI pretende **tutti i giorni senza buchi**. La nostra conteneva solo i giorni con partite, quindi l'ha rifiutata: abbiamo corretto l'ETL perché generi un calendario continuo (3.565 giorni).

### 3. Le misure DAX
Una **misura** è un calcolo che Power BI rifà ogni volta in base ai filtri attivi in quel punto del report (il **contesto di filtro**): la stessa misura `Punti` dà 69 se sono filtrate Juventus e 2025/26, e 87 se la riga è Inter.

- `SUM(fact_team_match[points])` somma i punti nel contesto corrente.
- `CALCULATE(COUNTROWS(...), fact_team_match[result] = "W")` **modifica il contesto**: conta le righe del fatto, ma solo quelle con esito `W`.
- `DIVIDE(a, b)` fa la divisione e restituisce vuoto se `b` è zero, invece di un errore.
- `RANKX(ALLSELECTED(dim_team[team_name]), [Punti] * 1000 + [Diff Reti], , DESC, Dense)` calcola la posizione in classifica: ordina per punti e, a parità, per differenza reti (moltiplicare i punti per 1000 dà loro la precedenza). `ALLSELECTED` tiene i filtri scelti dall'utente (la stagione) ma toglie il filtro della riga corrente, così ogni squadra "vede" le altre.
- **Colonna contro misura:** una colonna (come `Campo`, che traduce 1/0 in "Casa"/"Trasferta") è calcolata una volta per riga e salvata; una misura si ricalcola ad ogni filtro.

### 4. Perché i totali "a partita" dividono per `Partite`
Nella tabella dei fatti ogni partita ha **due righe**. Per questo le medie "a partita" si dividono per `DISTINCTCOUNT(match_key)` (le partite distinte) e non per il numero di righe. A livello di campionato la somma di `goals_for` sulle due righe dà i gol totali della partita, quindi `Gol a Partita` è corretto; per una squadra dà i suoi gol a partita.

### 5. Il caso istruttivo: `Ordine Partita`
La tabella "ultimi 5 risultati" usa il filtro **Principali N** ordinato per la misura `Ordine Partita`. La prima versione, `MAX(dim_match[match_key])`, mostrava 2 righe invece di 5: il filtro della squadra arriva al fatto ma **non risale** a `dim_match` (il filtro va solo da "uno" a "molti"), quindi la misura vedeva le partite di tutte le squadre. Con `MAX(fact_team_match[match_key])` la misura vede solo la squadra scelta. Dettaglio in `docs/dax/misure.md`.

### 6. Le pagine
1. **Classifica:** slicer stagione, tabella con posizione, V/N/P, gol e punti per 20 squadre, e (indipendente dallo slicer squadra grazie a *Modifica interazioni*) gli ultimi 5 risultati della squadra scelta.
2. **Squadra:** schede con punti, gol fatti, gol subiti e % di conversione tiri, più un istogramma casa/trasferta.
3. **Confronti tra stagioni:** gol a partita, % vittorie in casa, gialli e rossi a partita, stagione per stagione (nessuno slicer: confronta tutte).
4. **Disciplina e gioco duro:** falli e cartellini per squadra e, in un grafico che ignora lo slicer, l'andamento dei falli nelle stagioni.

### Cosa si vede nei dati
Alcune osservazioni, tutte lette dalla dashboard e confrontate con il database:
- I **gol a partita scendono** da 2,96 (2016/17) a 2,43 (2025/26), con un picco di 3,05 nel 2020/21.
- La **vittoria in casa è sempre meno frequente**: dal 48,4% al 38,9%.
- I **cartellini gialli** per partita passano dal picco di 5,09 (2019/20) a 3,70 (2025/26).
- I **falli** a partita calano da 27,93 (2016/17) a 24,06 (2023/24), con una leggera risalita.

## Come eseguirlo
1. Avvia Docker Desktop e il database: `docker compose up -d --wait`.
2. Esegui l'ETL se serve: `python -m etl.run_etl`.
3. Installa il **MySQL Connector/NET** (richiesto da Power BI) e apri `powerbi/dashboard.pbix`.
4. Se Power BI chiede le credenziali: utente `serie_a`, password `serie_a_pw`, tipo "Database" (o "Di base"); server `localhost:3308`.
5. **Aggiorna** (Home → Aggiorna) per rileggere i dati dopo aver rilanciato l'ETL.

## Concetti da studiare
- **Relazione uno-a-molti**, direzione del filtro e relazioni **inattive**.
- **Contesto di filtro** e perché la stessa misura dà valori diversi in punti diversi del report.
- `CALCULATE`, `DIVIDE`, `DISTINCTCOUNT`, `RANKX`, `ALLSELECTED`.
- **Misura** contro **colonna calcolata**.
- **Tabella data** e perché deve essere continua.
- **Interazioni tra visual** (come impedire a uno slicer di filtrare un altro grafico).
