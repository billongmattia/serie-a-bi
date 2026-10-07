# Misure DAX

Creale in Power BI Desktop in una tabella dedicata "Misure" (Home → Inserisci dati → crea una tabella vuota chiamata `Misure`, poi usa **Nuova misura**). Tutte lavorano nel contesto di filtro del report: stagione, squadra, casa/trasferta.

## Base

```
Partite = DISTINCTCOUNT(fact_team_match[match_key])
```
Numero di partite distinte. È il denominatore di tutte le medie "a partita": contare le *righe* darebbe il doppio per le viste a livello di campionato.

```
Punti = SUM(fact_team_match[points])
```
Punti totali. Ha senso per squadra (o per classifica), non sommati su tutte le squadre.

```
Gol Fatti = SUM(fact_team_match[goals_for])
Gol Subiti = SUM(fact_team_match[goals_against])
Diff Reti = [Gol Fatti] - [Gol Subiti]
```
Gol fatti, subiti e differenza reti.

## Esiti

```
Vittorie = CALCULATE(COUNTROWS(fact_team_match), fact_team_match[result] = "W")
Pareggi = CALCULATE(COUNTROWS(fact_team_match), fact_team_match[result] = "D")
Sconfitte = CALCULATE(COUNTROWS(fact_team_match), fact_team_match[result] = "L")
```
`CALCULATE` modifica il contesto di filtro: conta le righe del fatto con quel valore di `result`.

## Classifica

```
Posizione = RANKX(ALLSELECTED(dim_team[team_name]), [Punti] * 1000 + [Diff Reti], , DESC, Dense)
```
Posizione in classifica tra le squadre selezionate. Ordina per punti e, a parità, per differenza reti (il fattore 1000 dà ai punti la precedenza). `ALLSELECTED` mantiene i filtri scelti dall'utente (es. la stagione) ma ignora quello della riga corrente.

## Forma recente

```
Ordine Partita = MAX(fact_team_match[match_key])
```
Restituisce la chiave della partita più recente nel contesto corrente. Si usa come criterio "Per valore" nel filtro **Principali N** della tabella degli ultimi 5 risultati (le chiavi crescono con la data).

**Perché `fact_team_match` e non `dim_match`.** Le relazioni vanno da `dim_match` verso il fatto (uno a molti, filtro in una sola direzione). Il filtro della squadra (`dim_team`) arriva al fatto ma **non risale** a `dim_match`. Con `MAX(dim_match[match_key])` la misura vedeva tutte le partite di ogni giorno, di tutte le squadre, e il filtro "primi 5" sceglieva le ultime 5 date del campionato (di cui poche con la squadra scelta): la tabella mostrava 2 righe invece di 5. Usando la colonna del fatto, la misura vede solo le partite della squadra selezionata.

## Medie e percentuali

```
Gol a Partita = DIVIDE(SUM(fact_team_match[goals_for]), [Partite])
```
Nel contesto "tutte le squadre" dà i gol totali per partita (la somma di `goals_for` sulle due righe di una partita è il totale della partita); per una singola squadra dà i suoi gol a partita.

```
% Vittorie Casa =
DIVIDE(
    CALCULATE(COUNTROWS(fact_team_match), fact_team_match[is_home] = 1, fact_team_match[result] = "W"),
    CALCULATE(COUNTROWS(fact_team_match), fact_team_match[is_home] = 1)
)
```
Quota di vittorie giocando in casa.

```
% Conversione Tiri = DIVIDE(SUM(fact_team_match[goals_for]), SUM(fact_team_match[shots_for]))
```
Quanti tiri servono, in proporzione, per fare gol.

## Disciplina

```
Falli a Partita = DIVIDE(SUM(fact_team_match[fouls_for]), [Partite])
Falli Subiti a Partita = DIVIDE(SUM(fact_team_match[fouls_against]), [Partite])
Gialli a Partita = DIVIDE(SUM(fact_team_match[yellow_for]), [Partite])
Rossi a Partita = DIVIDE(SUM(fact_team_match[red_for]), [Partite])
```
Per una squadra, i suoi falli/cartellini a partita; nel contesto di campionato, i totali di una partita.

## Perché `DIVIDE` e non `/`
`DIVIDE(a, b)` restituisce vuoto se `b` è zero (per esempio per una squadra senza partite nel filtro selezionato), invece di un errore.
