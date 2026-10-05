# 02 – Extract: scaricare i dati

## Cosa ho fatto
- Scritto `etl/extract.py`, che scarica i CSV delle 10 stagioni (2016/17 → 2025/26) e li salva in `data/raw/`.
- Scritto 4 test in `tests/test_extract.py`, **prima** del codice, e verificato che fallissero (il modulo non esisteva) e poi passassero.
- Lanciato il download vero: 10 file, ciascuno con 380 partite più l'intestazione.

## Perché
Il primo passo di un ETL (*Extract, Transform, Load*) è prendere i dati dalla fonte. La fonte è il dataset **DataHub `football/italian-serie-a`** (licenza di pubblico dominio, derivato da football-data.co.uk): un file CSV per stagione, con un indirizzo web fisso del tipo `.../_r/-/season-1617.csv`.

## Come funziona (codice spiegato)

**`season_code(2016)` → `"1617"`** e **`season_label(2016)` → `"2016/17"`**: due piccole funzioni che traducono l'anno di inizio nel codice usato dal sito (per l'URL) e nell'etichetta leggibile (per le tabelle).

**`extract_season(...)`** scarica una stagione:
1. costruisce il percorso `data/raw/season-1617.csv`;
2. se il file esiste già, lo restituisce e finisce lì: è la **cache**, così non riscarichi ogni volta;
3. altrimenti scarica il contenuto, controlla che sia davvero un CSV e lo salva.

**Il controllo `looks_like_csv`**: un CSV valido inizia con `Date,`. Se il sito rispondesse con una pagina HTML (un errore, un blocco anti-bot), senza questo controllo salveremmo la pagina come se fosse un CSV e l'errore comparirebbe molto più avanti, in modo incomprensibile. Così invece si ferma subito, e **non** salva nulla.

**`extract_all(...)`** scarica tutte le stagioni. Se una fallisce, registra l'errore e **continua con le altre**: restituisce due dizionari, uno con i file ottenuti e uno con gli errori.

**Il parametro `fetch`**: la funzione che fa il download vero (`default_fetch`, che usa la libreria `requests`) si può sostituire. Nei test passiamo una funzione finta che restituisce un testo già pronto: così i test sono veloci, non usano internet e sono sempre uguali. Questa tecnica si chiama *dependency injection* (iniezione di dipendenza).

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
python -m etl.extract          # scarica (o prende dalla cache) le 10 stagioni
python -m pytest tests/test_extract.py -v
```
Per riscaricare tutto da zero, cancella la cartella `data/raw/`.

## Concetti da studiare
- **ETL** e il ruolo dell'*extract*.
- **Cache**: perché si salvano i file già scaricati.
- **Dependency injection** nei test (funzione finta al posto della rete).
- **Timeout** e `raise_for_status()` in `requests`: cosa succede se la rete non risponde o il sito dà errore.
- **Licenza PDDL**: cosa significa dati di pubblico dominio (per questo possiamo usarli e citarli nel portfolio).
