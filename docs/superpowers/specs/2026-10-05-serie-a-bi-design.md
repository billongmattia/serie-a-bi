# Progetto Serie A BI – Design

Data: 2026-10-05 (rev. 3: fonte DataHub, niente dimensione arbitro)

## Obiettivo
Progetto da portfolio per un BI Developer: data warehouse e dashboard sui risultati della Serie A. Deve mostrare l'intera catena BI (acquisizione, ETL, modello dimensionale, KPI, visualizzazione) a chi legge il repository su GitHub o a un colloquio.

## Contesto e ipotesi
- Autore: studente ITS BI Software Developer. Conosce SQL (MySQL, Oracle), NoSQL, Java/Spring Boot, React, Docker, Git. Python a livello base. Ha usato Metabase, non Power BI.
- Il progetto serve a mostrare competenze BI, non a costruire un'app web.
- Dati gratuiti, nessun servizio a pagamento. Power BI Desktop (gratuito, Windows) senza pubblicazione su Power BI Service.

## Fonte dati
Dataset **DataHub `football/italian-serie-a`** (https://datahub.io/football/italian-serie-a), licenza Open Data Commons PDDL (pubblico dominio), derivato da football-data.co.uk. Un CSV per stagione, URL stabili `https://datahub.io/football/italian-serie-a/_r/-/season-<AABB>.csv` (es. `season-1617.csv`).
- Colonne: `Date` (ISO `YYYY-MM-DD`), `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, `HTR`, `Referee`, `HS`, `AS`, `HST`, `AST`, `HF`, `AF`, `HC`, `AC`, `HY`, `AY`, `HR`, `AR`.
- **`Referee` è sempre vuota** per la Serie A (lo dichiara il dataset): non esiste dimensione arbitro.
- La fonte va citata nel README.

## Perimetro
- **Dentro:** risultati, gol, tiri, falli, corner, cartellini. Dieci stagioni complete: **2016/17 → 2025/26**. La stagione in corso (2026/27) è esclusa, così il controllo "380 partite per stagione" resta valido. Allargare il periodo a progetto finito sarà solo una modifica di `FIRST_SEASON`.
- **Fuori (per ora):** arbitri (dato non disponibile), dati sui giocatori, previsioni, API, pubblicazione su Power BI Service, CI, Makefile, formato `.pbip`.

## Architettura
```
CSV (DataHub football/italian-serie-a)
   -> profiling copertura colonne
   -> ETL Python (pandas): extract, transform, load
   -> MySQL in Docker (staging -> star schema)
   -> Power BI Desktop (modello, misure DAX, dashboard)
```
- Staging: archivio grezzo dei CSV così come arrivano, caricato per tracciabilità. Lo star schema è costruito in pandas (testato con pytest) dagli stessi dati grezzi.
- Docker Compose avvia MySQL con un comando. Metabase opzionale come seconda dashboard.

## Modello dati (star schema)
```
dim_date(date_key, date, day, month, year, weekday)
dim_season(season_key, label, start_year, end_year)
dim_team(team_key, team_name)
dim_match(match_key, match_id, date_key, season_key, matchday,
          home_team_key, away_team_key)
fact_team_match(match_key, team_key, opponent_team_key, is_home,
                goals_for, goals_against, goals_ht_for, goals_ht_against,
                shots_for, shots_against,
                shots_on_target_for, shots_on_target_against,
                fouls_for, fouls_against, corners_for, corners_against,
                yellow_for, red_for, result, points)
```
- **Grain di `fact_team_match`:** una riga per squadra per partita (due righe per partita).
- **`dim_match`:** una riga per partita. Serve per conteggio partite, giornata e casa/trasferta. `match_id` è stabile (hash di stagione + data + squadra di casa + squadra ospite).
- **Giornata (`matchday`)** è un attributo della partita e sta in `dim_match`, non in `dim_date`; `dim_date` contiene solo attributi di calendario.
- **Relazioni in Power BI:** `dim_match 1 → * fact_team_match`; `dim_team 1 → * fact_team_match` (squadra); `dim_date` e `dim_season` collegate a `dim_match`. La squadra avversaria si usa tramite `opponent_team_key` con relazione inattiva e `USERELATIONSHIP` solo se serve.

### Regole di additività (da riportare in `docs/data_dictionary.md` e nelle misure DAX)
- Le misure `_for` e `_against` sono additive per squadra; sommate su tutte le squadre danno il doppio dei gol/tiri/ecc. reali.
- `points` sommati su tutte le squadre non hanno significato (vittoria 3+0, pareggio 1+1): usarli solo per squadra o per classifica.
- Le medie "a partita" si calcolano dividendo per le partite distinte (`DISTINCTCOUNT(match_key)`), non per riga di fatto.

## KPI e pagine della dashboard
1. Classifica per stagione: punti, differenza reti, forma recente.
2. Squadra: rendimento casa e trasferta, gol fatti e subiti, tiri e conversione.
3. Confronti tra stagioni: gol a partita, percentuale di vittorie in casa, cartellini.
4. **Disciplina e gioco duro:** falli commessi e subiti, gialli e rossi a partita, per squadra e per stagione (sostituisce la pagina arbitri).

## Profiling della copertura
Prima della trasformazione, uno script produce una matrice stagione × colonna (HS, AS, HST, AST, HF, AF, HC, AC, HY, AY, HR, AR) con la presenza dei dati, salvata in `docs/coverage.md`. Serve a decidere dove mettere NULL e a documentare i limiti dei dati.

## ETL
1. **Extract:** scarica `season-<AABB>.csv` per ogni stagione in `data/raw/`, con timeout e cache locale (non riscarica file già presenti); rifiuta risposte che non sono CSV.
2. **Transform:** date ISO, nomi squadra normalizzati con mapping in CSV, `match_id` stabile, colonne mancanti a NULL, ogni partita diventa una riga in `dim_match` e due righe in `fact_team_match`. La colonna `Referee` è ignorata.
3. **Load:** staging poi star schema; esecuzione idempotente (delete e reload in una transazione, nessun duplicato al rilancio).
4. **Esecuzione:** `run_etl.py` con logging su file, riepilogo finale (righe caricate, scartate, stagioni con problemi) e exit code diverso da zero in caso di errore.

## Gestione degli errori
- Download fallito: segnala la stagione e continua con le altre.
- Riga senza data o squadre: scartata e contata nel log.
- Campi opzionali mancanti: NULL.

## Verifiche
- Test pytest sulla trasformazione: una partita produce una riga in `dim_match` e due in `fact_team_match`, punti 3/1/0, date lette correttamente, `match_id` stabile.
- Controlli di qualità (`sql/03_quality_checks.sql`): 380 partite per stagione (20 squadre, 38 giornate), punti dei campioni (Juventus 2016/17 = 91, Inter 2023/24 = 94), nessuna squadra duplicata sotto nomi diversi, ogni partita ha esattamente due righe di fatto.

## Struttura del repository
```
progetto-serie-a/
├─ docker-compose.yml
├─ .env.example
├─ requirements.txt
├─ sql/       01_staging.sql, 02_star_schema.sql, 03_quality_checks.sql
├─ etl/       profiling.py, extract.py, transform.py, load.py, run_etl.py
├─ tests/
├─ powerbi/   dashboard.pbix, screenshots/
├─ docs/      spec, data_dictionary.md, coverage.md, dax/, spiegazioni/
└─ README.md
```
Power BI: si parte con il `.pbix` (binario), con misure DAX documentate in `docs/dax/` e screenshot/GIF nel README. Valutazione futura: conversione a `.pbip`.

## Criterio di successo
Repository pulito su GitHub, README con modello, ETL e insight, dashboard Power BI navigabile (file .pbix, screenshot e breve video nel README).

## Rimandato (fase finale, opzionale)
Estensione del periodo (modifica di `FIRST_SEASON`), CI con GitHub Actions, formato `.pbip`, seconda dashboard in Metabase. Makefile escluso (poco comodo su Windows).

## Processo di lavoro
Dopo ogni implementazione viene scritto un file Markdown in `docs/spiegazioni/` che spiega in italiano cosa è stato fatto, perché e come, per favorire l'apprendimento (Python e Power BI sono aree di studio).
