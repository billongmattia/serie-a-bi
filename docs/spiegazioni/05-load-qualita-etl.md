# 05 – Load, controlli di qualità e `run_etl`

## Cosa ho fatto
- `etl/load.py`: carica i dati in MySQL (prima lo *staging* grezzo, poi lo star schema).
- `sql/03_quality_checks.sql` + `etl/quality.py`: controlli di qualità sui dati caricati.
- `etl/run_etl.py`: il programma che mette in fila tutto (scarica → trasforma → carica → controlla) e scrive un log.
- 5 test (`tests/test_load.py`) scritti prima del codice, visti fallire e poi passare.
- Lanciato l'ETL vero **due volte** contro MySQL.

## Risultato sui dati reali
| Controllo | Esito |
|---|---|
| Esecuzione 1 e 2 | `ETL terminato: OK`, exit code 0 |
| `dim_match` / `fact_team_match` / `dim_team` / `stg_matches` | 3.800 / 7.600 / 34 / 3.800, **identici dopo la seconda esecuzione** |
| Ogni stagione ha 380 partite e 20 squadre | superato |
| Ogni partita ha 2 righe di fatto, punti 2 o 3, gol coerenti tra casa e trasferta | superato |
| Punti Juventus 2016/17 | **91** (come la classifica ufficiale) |
| Punti Inter 2023/24 | **94** (come la classifica ufficiale) |

Il confronto con i punti ufficiali è un controllo "esterno": se il nostro modello avesse un errore (partite duplicate, esiti sbagliati) i numeri non tornerebbero.

## Perché
**Idempotenza.** Un ETL deve poter essere rilanciato senza fare danni. Se la seconda esecuzione raddoppiasse le righe, i totali in Power BI sarebbero sbagliati. Per ottenerla ogni caricamento **cancella prima il contenuto** (`DELETE FROM ...`) e poi lo reinserisce, tutto dentro **una transazione**: o riesce tutto o non cambia niente.

**Controlli di qualità.** Un dato caricato non è un dato corretto. Le query in `03_quality_checks.sql` cercano le *violazioni*: ognuna deve restituire **zero righe**. Se ne restituisce qualcuna, l'ETL lo dice nel log ed esce con un codice di errore.

## Come funziona (codice spiegato)

**Staging.** `build_staging` prende i CSV grezzi, aggiunge la colonna `season` e li mette in `stg_matches` così come sono (tutte stringhe). Serve da archivio: se un domani vuoi capire da dove viene un numero, il dato originale è lì.

**`load_star`** cancella le tabelle nell'ordine inverso delle dipendenze (prima il fatto, poi `dim_match`, poi le dimensioni) e le riempie nell'ordine giusto. L'ordine conta per le chiavi esterne: non puoi inserire una partita che punta a una squadra non ancora inserita.

**`_nullify`** trasforma i valori mancanti di pandas (`NaN`, `<NA>`) in `None`, che il database interpreta come `NULL`.

**`parse_checks`** legge il file `.sql` e lo spezza in blocchi: ogni riga `-- check: nome` inizia un controllo. **`run_quality_checks`** esegue ogni query e raccoglie i problemi; poi verifica i punti dei campioni (`EXPECTED_POINTS`).

**`run_etl.main()`** orchestra il tutto e scrive un riepilogo: stagioni caricate, righe scartate, righe caricate, eventuali problemi. Il log va sia sul terminale sia in `logs/etl.log` (la cartella `logs/` non finisce su Git).

## Perché i test usano SQLite e non MySQL
I test del load girano su **SQLite**, un database in un file temporaneo: sono veloci, non servono Docker né credenziali, e **non possono cancellare per sbaglio i tuoi dati veri** in MySQL. Lo schema è lo stesso: i file `.sql` sono scritti in SQL standard e funzionano su entrambi.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d --wait        # MySQL acceso
python -m etl.run_etl              # l'ETL completo (si può rilanciare quando vuoi)
python -m pytest                   # tutti i test
```
Per leggere il log: apri `logs/etl.log`.

## Concetti da studiare
- **Idempotenza** e **transazione** (`BEGIN`/`COMMIT`/`ROLLBACK`): tutto o niente.
- Ordine di caricamento e **chiavi esterne**.
- **Data quality**: controlli di completezza (380 partite), di coerenza (gol casa/trasferta) e di riconciliazione con una fonte esterna (punti ufficiali).
- **Staging area** contro data warehouse.
- Differenza tra SQLite e MySQL e perché per i test è comodo il primo.
