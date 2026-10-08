# 08 – Revisione finale del codice

## Cosa ho fatto
Ho riletto tutto il codice (ETL, SQL, test, configurazione, documentazione) con una domanda in mente: **cosa può rompersi per chi usa il progetto, e dove il codice dice una cosa mentre fa un'altra?** È una revisione fatta dall'autore del codice, quindi ha i limiti del caso (stessi punti ciechi di chi ha scritto): una revisione di una persona che non l'ha scritto resta più affidabile.

## Cosa ho trovato e corretto (con test scritti prima)
| # | Problema | Correzione | Test |
|---|---|---|---|
| A | Un errore non previsto dell'ETL (database spento, rete) non lasciava **nessuna traccia** in `logs/etl.log`: la traccia compariva solo sul terminale | `main()` ora cattura l'errore, lo scrive nel log con `log.exception` ed esce con codice 1 | `test_main_logs_an_unhandled_error_and_returns_1` |
| B | I controlli di qualità avevano scritto dentro **380 partite e 20 squadre**: con stagioni più vecchie (18 squadre fino al 2003/04, 306 partite) l'ETL fallirebbe con un controllo sbagliato, contraddicendo il README | Un solo controllo generale: ogni stagione è un **girone completo**, cioè partite = squadre × (squadre − 1). Vale per qualsiasi numero di squadre e continua a intercettare i nomi duplicati (21 squadre darebbero 420, non 380) | `test_quality_accepts_a_complete_season_of_any_size`, `test_quality_checks_flag_incomplete_season` |
| C | Il controllo sui punti dei campioni **saltava in silenzio** se la squadra non si trovava (per esempio dopo aver cambiato un nome nella mappa): un controllo che si disattiva da solo non protegge nessuno | Se la stagione è caricata ma la squadra manca, ora **segnala un problema** | `test_quality_flags_champion_check_when_the_team_is_missing` |
| D | Il README diceva di cambiare i parametri del database con `.env`, ma **il programma Python non legge `.env`** (lo legge solo Docker): cambiando la porta lì l'ETL avrebbe continuato a usare quella vecchia | README corretto: `.env` per Docker, variabili d'ambiente della shell per l'ETL | (documentazione) |

La suite è passata da 25 a **29 test**, tutti verdi, e l'ETL reale gira ancora con esito `OK`.

## Cosa ho lasciato (valutato e rimandato)
Cose reali ma di impatto basso, da tenere d'occhio:
- **`db_url()`** compone l'indirizzo del database con una stringa: una password con caratteri speciali (`@`, `/`) la romperebbe. Meglio `sqlalchemy.engine.URL.create`.
- **Righe duplicate nella fonte** (stessa partita due volte) farebbero fallire il caricamento con un errore di vincolo di unicità: il caricamento è atomico (nessun dato a metà), ma il messaggio non è chiaro.
- **Staging e star schema** si caricano in due transazioni separate: se la seconda fallisce, lo staging resta aggiornato e lo star schema no.
- **`read_raw_csv`** salta in silenzio le righe malformate (`on_bad_lines="skip"`): oggi lo scarto sarebbe comunque intercettato dal controllo del girone completo.
- **Nessun controllo** che le date di un file rientrino nella stagione a cui è assegnato.

## Cosa imparare
- **Un controllo che non può fallire non controlla niente:** un test o una verifica che "salta" quando non trova ciò che cerca va trattato come un errore.
- **I numeri scritti nel codice** (380, 20) sono ipotesi: se il resto del progetto promette flessibilità, le ipotesi vanno tolte.
- **Errori e log:** un programma che esce con un errore deve lasciare traccia dove l'utente la cerca (il file di log), non solo sul terminale.
- La differenza tra "il codice funziona" e "la documentazione dice il vero": ho trovato più problemi confrontando README e codice che leggendo solo il codice.
