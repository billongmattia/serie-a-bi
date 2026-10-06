# 04 – Transform: dal CSV allo star schema

## Cosa ho fatto
- Scritto `etl/transform.py`: pulisce i dati grezzi e costruisce le 5 tabelle del modello (`dim_season`, `dim_date`, `dim_team`, `dim_match`, `fact_team_match`).
- Scritto `etl/team_names.csv`: elenco dei nomi di squadra da uniformare (per ora `Spal → SPAL` e `Verona → Hellas Verona`).
- Scritto 11 test (`tests/test_transform.py`) **prima** del codice, visti fallire e poi passare.
- Provato il transform sui dati reali, in sola lettura.

## Risultato sui dati reali
| Cosa | Valore |
|---|---|
| Righe scartate | 0 in tutte le stagioni |
| `dim_match` (partite) | 3.800 (10 stagioni × 380) |
| `fact_team_match` (righe di fatto) | 7.600 (2 per partita) |
| `dim_team` (squadre diverse) | 34, senza duplicati |
| `dim_date` | 3.565 giorni consecutivi (calendario continuo, vedi sotto) |
| Giornata massima per stagione | 38 in tutte le stagioni |
| Valori NULL nel fatto | 4, tutti in una partita: **Sassuolo–Pescara del 28/08/2016**, a cui la fonte non dà i gol del primo tempo |

Quel buco è un esempio concreto di perché le colonne opzionali accettano `NULL`: il dato non esiste, e inventarlo (mettere 0) sarebbe sbagliato.

## Perché
Il passo di *transform* è dove i dati grezzi diventano il modello pensato per l'analisi. Qui si decide il **grain**: nel fatto ogni riga è "una squadra in una partita", quindi **ogni partita diventa due righe** (la vista della squadra di casa e quella della trasferta). Questo rende la classifica, il rendimento in casa/trasferta e le medie molto semplici da calcolare in Power BI.

## Come funziona (codice spiegato)

**`parse_dates`** converte il testo in data. Accetta solo il formato `AAAA-MM-GG` (quello del dataset): qualsiasi altra cosa diventa `NaT` ("data non valida") invece di far crollare tutto.

**`clean_matches`** pulisce una stagione:
1. controlla che le 5 colonne obbligatorie ci siano (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`), altrimenti solleva un errore chiaro;
2. se mancano colonne opzionali (es. i tiri), le crea vuote → `NULL`, senza errori;
3. converte i numeri con `pd.to_numeric(..., errors="coerce")`: un valore illeggibile diventa "mancante" invece di bloccare;
4. uniforma i nomi delle squadre con la mappa;
5. **scarta** le righe senza data, squadre o gol finali, e restituisce **quante** ne ha scartate (così lo vediamo nel log).

**`make_match_id`** crea un identificativo stabile per ogni partita: un *hash* (impronta digitale) di stagione, data, squadra di casa e squadra ospite. "Stabile" vuol dire che la stessa partita avrà sempre lo stesso id, anche se rilanci l'ETL.

**`_matchday`** calcola la giornata. Il CSV non la contiene, quindi la ricostruiamo: per ogni squadra numeriamo le sue partite in ordine di data (la 1ª, la 2ª…), e la giornata della partita è il **massimo** tra il numero della squadra di casa e quello della squadra ospite. È un'**approssimazione**: i recuperi di partite rinviate possono spostarla di poco.

**`build_star`** costruisce le tabelle:
- assegna le chiavi (`team_key`, `match_key`, …): numeri progressivi che sostituiscono i nomi;
- `dim_match`: una riga per partita;
- `fact_team_match`: per ogni partita crea la riga "casa" e la riga "trasferta" usando le due mappe `HOME_COLUMNS` e `AWAY_COLUMNS`. Per esempio, per la squadra di casa `goals_for` viene da `FTHG`, per quella ospite da `FTAG`: le colonne sono *invertite* tra le due righe;
- calcola `result` (W/D/L) e `points` (3/1/0) dai gol.

**`transform_all`** applica tutto a tutte le stagioni e restituisce anche gli scarti per stagione.

## La colonna `Referee`
Il dataset ha la colonna `Referee`, ma è sempre vuota per la Serie A. Il codice la **ignora** del tutto: per questo nel modello non esiste una dimensione arbitro (c'è un test che lo verifica).

## Una nota su pandas 3
`pip` ha installato pandas 3.0, una versione molto recente. I test passano senza modifiche al codice scritto per pandas 2.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_transform.py -v
```

## Concetti da studiare
- **Grain** della tabella dei fatti e perché una partita diventa due righe.
- **Chiave surrogata** (`team_key`) contro chiave naturale (il nome della squadra).
- **Hash** e identificativi stabili (`sha1`).
- **Normalizzazione dei dati**: perché `Verona` e `Hellas Verona` devono essere la stessa squadra.
- **Valori mancanti**: `NULL`/`NaN` contro zero.

## Aggiornamento: calendario continuo in dim_date
In un primo momento dim_date conteneva solo i giorni in cui si giocava almeno una partita (1.177 date). Quando abbiamo provato a segnare la tabella come *tabella data* in Power BI, ha rifiutato: `La colonna della data non può includere gap nelle date`. Una tabella data deve avere **tutti i giorni senza buchi**, altrimenti le funzioni di calcolo sul tempo non sono affidabili. Ora uild_star genera il calendario con `pd.date_range` dal primo all'ultimo giorno delle stagioni (3.565 giorni), con un test che lo verifica (`test_dim_date_is_a_continuous_calendar`).
