# 01 – Setup e database

## Cosa ho fatto
- Inizializzato il repository Git (`git init`, branch `main`).
- Creato l'ambiente virtuale Python `.venv` e installato le librerie di `requirements.txt`.
- Scritto `etl/config.py`, il file che dice al resto del codice dove sono i dati e come collegarsi al database.
- Scritto lo schema SQL (`sql/01_staging.sql`, `sql/02_star_schema.sql`).
- Scritto `docker-compose.yml` e avviato MySQL 8.4 in un container Docker.
- Verificato che nel database ci siano le 6 tabelle: `stg_matches`, `dim_season`, `dim_date`, `dim_team`, `dim_match`, `fact_team_match`.

## Perché
- **Git** tiene la storia del progetto: ogni passo è un commit che puoi rivedere o annullare, e a fine progetto lo pubblichi su GitHub.
- **Ambiente virtuale (`.venv`)**: le librerie del progetto restano in una cartella isolata, senza sporcare il Python del PC e senza conflitti con altri progetti.
- **Docker**: MySQL gira in un "contenitore", quindi non devi installare e configurare MySQL a mano. Chiunque cloni il progetto lo avvia con un solo comando.
- **Star schema**: è il modello tipico della Business Intelligence. Una tabella dei *fatti* (le misure, qui i dati di ogni squadra in ogni partita) è circondata da tabelle delle *dimensioni* (il contesto: quando, in quale stagione, quale squadra, quale partita).

## Come funziona (codice spiegato)

**`etl/config.py`** raccoglie le impostazioni in un unico posto: dove salvare i CSV (`RAW_DIR`), quali stagioni scaricare (`SEASONS`, dal 2016 al 2025) e come collegarsi al database (`db_url()`). Le credenziali si leggono dalle *variabili d'ambiente* con un valore di default (`os.environ.get("MYSQL_USER", "serie_a")`): se non imposti niente, usa quelli del progetto.

**`docker-compose.yml`** descrive il servizio `mysql`:
- `image: mysql:8.4` è la versione di MySQL da usare;
- `ports: "3307:3306"` collega la porta 3307 del tuo PC alla 3306 *dentro* il container;
- `volumes` fa due cose: `mysql_data` conserva i dati anche se spegni il container, e i due file `.sql` montati in `docker-entrypoint-initdb.d` vengono eseguiti **solo alla prima creazione** del database, per creare le tabelle;
- `healthcheck` permette a `docker compose up --wait` di aspettare che MySQL sia davvero pronto.

**Lo schema SQL** (`CREATE TABLE IF NOT EXISTS`):
- `fact_team_match`: una riga per squadra per partita (quindi due righe a partita). Contiene gol, tiri, falli, cartellini, esito e punti.
- `dim_match`: una riga per partita, con la giornata e le due squadre. Serve per contare le partite senza contarle due volte.
- `dim_date`, `dim_season`, `dim_team`: il calendario, le stagioni e le squadre.
- `stg_matches`: l'*area di staging*, dove si archiviano i dati grezzi così come arrivano dal CSV.
- Le `FOREIGN KEY` garantiscono che una partita non possa riferirsi a una squadra o a una data inesistente.

## Cosa è andato diversamente dal piano
- **Porta 3307 invece di 3306.** Sul tuo PC c'è già un MySQL locale (`mysqld`) che usa la 3306. Per non toccarlo ho spostato quello di Docker sulla 3307. In Power BI useremo quindi `localhost:3307`.
- **Nome del Python.** Il launcher di Windows chiama la tua installazione `Astral/CPython3.14.4`, quindi il venv si crea con `py "-V:Astral/CPython3.14.4" -m venv .venv`.
- **pandas 3.0:** `pip` ha installato pandas 3.0, più recente di quello previsto nel piano. Se qualche test dei prossimi task si comporta in modo diverso, lo sistemiamo lì.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1      # attiva l'ambiente virtuale
docker compose up -d --wait       # avvia MySQL (Docker Desktop deve essere acceso)
docker exec serie_a_mysql mysql -u serie_a -pserie_a_pw serie_a -e "SHOW TABLES"
docker compose down               # spegne il container (i dati restano nel volume)
docker compose down -v            # spegne e CANCELLA i dati (per rifare lo schema da zero)
```

## Concetti da studiare
- Differenza tra tabella dei **fatti** e tabelle delle **dimensioni**, e che cos'è il **grain** (il livello di dettaglio di una riga del fatto).
- Chiave primaria e chiave esterna (`PRIMARY KEY`, `FOREIGN KEY`).
- Ambiente virtuale Python (`venv`) e file `requirements.txt`.
- Container Docker e volume, e a cosa serve `docker compose`.
- Staging area nel mondo ETL.
