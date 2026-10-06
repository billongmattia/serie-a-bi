# Dizionario dei dati

Database MySQL `serie_a`. Fonte: dataset DataHub `football/italian-serie-a` (derivato da football-data.co.uk, licenza PDDL), stagioni 2016/17 → 2025/26.

## Regole del modello

- **Grain.** `fact_team_match` ha una riga per squadra per partita (due righe a partita). `dim_match` ha una riga per partita.
- **Additività.**
  - Le misure `_for` e `_against` sono additive *per squadra*. Sommare entrambe su tutte le squadre dà il doppio dei gol, tiri, ecc. reali.
  - `points` sommati su tutte le squadre non hanno significato (vittoria 3+0, pareggio 1+1): usarli solo per squadra o per classifica.
  - Le medie "a partita" si calcolano dividendo per `DISTINCTCOUNT(match_key)`, non per il numero di righe.
- **Giornata.** `matchday` è calcolata come il massimo tra il numero progressivo di partita delle due squadre nella stagione. I recuperi possono falsarla leggermente.
- **Valori mancanti.** `NULL` dove la fonte non ha il dato. Nelle 10 stagioni caricate l'unico caso è la partita Sassuolo–Pescara (28/08/2016), senza i gol del primo tempo. Vedi anche `docs/coverage.md`.
- **Arbitri.** Non presenti: la colonna `Referee` della fonte è sempre vuota per la Serie A.

## `dim_season`
| Colonna | Tipo | Significato |
|---|---|---|
| `season_key` | INT, PK | Anno di inizio stagione (es. 2016) |
| `label` | VARCHAR(7) | Etichetta (es. `2016/17`) |
| `start_year` | INT | Anno di inizio |
| `end_year` | INT | Anno di fine |

## `dim_date`
| Colonna | Tipo | Significato |
|---|---|---|
| `date_key` | INT, PK | Data in formato `AAAAMMGG` (es. 20160820). Il calendario è **continuo**: contiene tutti i giorni dal primo all'ultimo della serie, anche quelli senza partite |
| `date` | DATE | Data della partita |
| `day`, `month`, `year` | INT | Componenti della data |
| `weekday` | VARCHAR(10) | Giorno della settimana, in inglese (es. `Saturday`) |

## `dim_team`
| Colonna | Tipo | Significato |
|---|---|---|
| `team_key` | INT, PK | Chiave surrogata |
| `team_name` | VARCHAR(60), unico | Nome normalizzato della squadra (es. `Hellas Verona`) |

## `dim_match`
| Colonna | Tipo | Significato |
|---|---|---|
| `match_key` | INT, PK | Chiave surrogata della partita |
| `match_id` | CHAR(16), unico | Identificativo stabile (hash di stagione, data, squadra di casa, squadra ospite) |
| `date_key` | INT, FK → `dim_date` | Data della partita |
| `season_key` | INT, FK → `dim_season` | Stagione |
| `matchday` | INT | Giornata (approssimata, vedi sopra) |
| `home_team_key` | INT, FK → `dim_team` | Squadra di casa |
| `away_team_key` | INT, FK → `dim_team` | Squadra ospite |

## `fact_team_match`
Chiave primaria `(match_key, team_key)`.

| Colonna | Tipo | Significato |
|---|---|---|
| `match_key` | INT, FK → `dim_match` | Partita |
| `team_key` | INT, FK → `dim_team` | Squadra a cui si riferisce la riga |
| `opponent_team_key` | INT, FK → `dim_team` | Avversaria |
| `is_home` | INT | 1 = in casa, 0 = in trasferta |
| `goals_for`, `goals_against` | INT | Gol fatti e subiti a fine partita |
| `goals_ht_for`, `goals_ht_against` | INT, NULL | Gol fatti e subiti nel primo tempo |
| `shots_for`, `shots_against` | INT, NULL | Tiri effettuati e subiti |
| `shots_on_target_for`, `shots_on_target_against` | INT, NULL | Tiri in porta effettuati e subiti |
| `fouls_for`, `fouls_against` | INT, NULL | Falli commessi e subiti |
| `corners_for`, `corners_against` | INT, NULL | Calci d'angolo a favore e contro |
| `yellow_for` | INT, NULL | Cartellini gialli ricevuti dalla squadra |
| `red_for` | INT, NULL | Cartellini rossi ricevuti dalla squadra |
| `result` | CHAR(1) | `W` vittoria, `D` pareggio, `L` sconfitta (dal punto di vista della squadra) |
| `points` | INT | 3, 1 o 0 |

## `stg_matches`
Area di staging: i dati grezzi dei CSV così come arrivano (tutte le colonne come testo), più `season` (es. `2016/17`). Serve da archivio e per la tracciabilità; non si usa in Power BI.
