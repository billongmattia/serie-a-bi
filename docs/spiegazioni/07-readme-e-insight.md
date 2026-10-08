# 07 – README e insight

## Cosa ho fatto
- Scritto il [`README.md`](../../README.md): è la vetrina del progetto.
- Scritto [`docs/insights.md`](../insights.md): 6 osservazioni sui dati con i numeri letti dalla dashboard e dal database.

## Perché
Chi apre un repository GitHub decide in pochi secondi se continuare a leggere. Il README deve far capire **cosa fa il progetto, come si esegue e cosa dimostra**. Gli insight dimostrano che sai anche **leggere** i dati, non solo costruire la pipeline: è la differenza tra "ho fatto un ETL" e "ho fatto un'analisi".

## Come è fatto il README
1. **Titolo e una frase**: cosa fa il progetto, per chi.
2. **Screenshot** in cima: l'impatto visivo è la prima cosa che si vede.
3. **Cosa fa** e **architettura**: il flusso in una riga.
4. **Modello dati**: lo star schema con il grain dichiarato.
5. **Come eseguirlo**: pochi comandi, ognuno commentato, con i requisiti.
6. **Fonte dei dati e licenza**: citare sempre chi ha prodotto i dati.
7. **Limiti noti**: dichiararli onestamente (niente arbitri, giornata ricostruita, un dato mancante) è un segno di maturità professionale e previene domande scomode.
8. **Prossimi passi**: il progetto è vivo.

## Come sono stati scritti gli insight
Ogni numero è stato **verificato** in due modi: letto dalla dashboard Power BI e confrontato con una query SQL sul database (per esempio i campioni di ogni stagione, il record di gol dell'Atalanta nel 2019/20, i gialli a partita). Le frasi descrivono cosa si vede (*i gol a partita scendono da 2,96 a 2,43*) senza inventare cause (*perché* scendono): su dieci stagioni non è dimostrabile. Nel file ci sono anche i **limiti** (pochi anni, stagioni anomale per la pandemia).

## Come raccontarlo a un colloquio
- **Problema:** unire risultati sparsi in un modello unico per rispondere a domande di analisi.
- **Scelte:** una riga per squadra per partita (così classifica e medie sono semplici), `dim_match` per non contare le partite due volte, ETL ripetibile, controlli di qualità con riconciliazione sui punti ufficiali.
- **Intoppi risolti:** l'arbitro non c'era nei dati e abbiamo adattato il modello; Power BI voleva un calendario senza buchi; un filtro che non risaliva tra le tabelle. Ogni intoppo è una storia da colloquio.
- **Limiti:** quelli del README.

## Cosa resta di M5
Rifare due screenshot (`02-squadra`, `03-confronti`), rivedere il codice nel suo insieme e rendere pubblico il repository quando è pronto.

## Concetti da studiare
- Cosa deve contenere un buon README di portfolio.
- Differenza tra **descrivere** i dati e **spiegarli** (correlazione e causalità).
- Come citare una fonte e una licenza (PDDL).
