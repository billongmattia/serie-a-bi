# 03 – Lettura dei CSV e profiling della copertura

## Cosa ho fatto
- Scritto `etl/rawio.py`: legge un CSV grezzo in una tabella pandas (DataFrame) dove **ogni valore è una stringa**.
- Scritto `etl/profiling.py`: costruisce una **matrice di copertura** (stagione × colonna) e la salva in `docs/coverage.md`.
- Scritto 4 test (`tests/test_profiling.py`) prima del codice, visti fallire e poi passare.
- Generato il report sui dati reali.

## Perché
Prima di trasformare dei dati bisogna sapere **che dati hai davvero**. Il profiling (analisi preliminare) risponde a domande come: quante partite ci sono per stagione? Le colonne dei tiri, dei falli, dei cartellini sono sempre compilate? Se in una stagione mancassero, dovremmo mettere `NULL` e dichiararlo come limite dei dati; se ci fossero buchi nascosti, le medie della dashboard sarebbero sbagliate senza che nessuno se ne accorga.

## Cosa dice la matrice reale
Il risultato (vedi [`docs/coverage.md`](../coverage.md)) è molto buono:
- Tutte e **10 le stagioni (2016/17 → 2025/26) hanno 380 partite**, cioè 20 squadre × 38 giornate ÷ 2.
- **Tutte le 12 colonne analizzate** (tiri, tiri in porta, falli, corner, gialli, rossi, per casa e trasferta) sono presenti in almeno il 95% delle partite in ogni stagione. Non ci sono buchi.
- La colonna `Referee` è stata esclusa dall'analisi perché nel dataset è sempre vuota.

Conseguenza: per queste 10 stagioni non ci aspettiamo `NULL` nei dati, ma il codice li gestirà comunque (se allarghiamo il periodo alle stagioni più vecchie, probabilmente compariranno).

## Come funziona (codice spiegato)

**`read_raw_csv`** legge il file con `pandas.read_csv(..., dtype=str)`:
- `dtype=str` significa "non interpretare niente": numeri e date restano testo. La conversione in numeri e date la facciamo noi, con regole esplicite, nel passo di *transform*;
- prova prima la codifica `utf-8`; se il file contiene caratteri che non la rispettano (`UnicodeDecodeError`), riprova con `latin-1`, che non fallisce mai;
- scarta le righe completamente vuote (`dropna(how="all")`).

**`_classify`** guarda una colonna e risponde con tre valori:
- `sì` se almeno il 95% delle righe ha il dato;
- `parziale` se ce l'ha qualche riga;
- `no` se la colonna manca del tutto o è sempre vuota.

**`coverage_matrix`** applica `_classify` a ogni colonna di ogni stagione e restituisce una tabella. **`to_markdown`** la trasforma in una tabella Markdown (quella di `docs/coverage.md`), e **`write_report`** la scrive su file.

## Come eseguirlo
```powershell
.\.venv\Scripts\Activate.ps1
python -m etl.profiling                  # rigenera docs/coverage.md
python -m pytest tests/test_profiling.py -v
```

## Concetti da studiare
- **Data profiling**: perché si guarda la qualità dei dati prima di usarli.
- **DataFrame** pandas e il significato di `NaN` (valore mancante).
- **Codifica dei caratteri** (UTF-8 vs Latin-1): perché a volte compaiono caratteri strani come `Ã¬` al posto di `ì`.
- Cos'è un **NULL** e perché non è uguale a zero (un giocatore con zero gialli è diverso da un dato "non registrato").
