# Insight sui dati

Osservazioni sulla Serie A 2016/17 – 2025/26 (3.800 partite, 10.423 gol). Ogni numero è letto dalla dashboard Power BI e riconfrontato con una query SQL sul data warehouse. Sono osservazioni descrittive su dieci stagioni: non spiegano le cause.

## 1. Si segna sempre meno
I **gol a partita** scendono da **2,96** (2016/17) a **2,43** (2025/26): circa **−18%**. Il massimo del periodo è il **3,05 del 2020/21**; dal 2022/23 la media non supera 2,61.
*Pagina: Confronti tra stagioni.*

| Stagione | 16/17 | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| Gol a partita | 2,96 | 2,68 | 2,68 | 3,04 | 3,05 | 2,87 | 2,56 | 2,61 | 2,56 | 2,43 |

## 2. Il fattore campo vale meno
La **percentuale di vittorie in casa** passa dal **48,4%** (2016/17) al **38,9%** (2025/26), quasi 10 punti percentuali in meno. Il minimo è proprio 38,9%, raggiunto sia nel 2021/22 sia nel 2025/26. Il 2020/21, giocato in buona parte a porte chiuse, è al 40,8%: il calo non si spiega solo con il pubblico assente.
*Pagina: Confronti tra stagioni.*

## 3. Chi ha vinto e con quanti punti
Nelle dieci stagioni hanno vinto **quattro squadre**: Juventus 4 titoli (dal 2016/17 al 2019/20), Inter 3, Napoli 2, Milan 1. I punti del campione scendono dal massimo di **95** (Juventus 2017/18) al minimo di **82** (Napoli 2024/25).
*Fonte: query SQL sulla somma dei punti per stagione.*

| 16/17 | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|---|
| Juventus 91 | Juventus 95 | Juventus 90 | Juventus 83 | Inter 91 | Milan 86 | Napoli 90 | Inter 94 | Napoli 82 | Inter 87 |

## 4. Meno cartellini gialli
I **gialli a partita** raggiungono il picco di **5,09** nel 2019/20 e scendono a **3,70** nel 2025/26 (circa **−27%**). I rossi restano rari e stabili: tra 0,17 e 0,26 a partita.
*Pagina: Confronti tra stagioni.*

## 5. Chi è corretto e chi no (2025/26)
- **Hellas Verona** è la squadra più ammonita (**2,34** gialli a partita) e quella che commette più falli (**15,74**), ma ne subisce pochissimi (**9,66**).
- **Napoli** (**1,29**) e **Juventus** (**1,37**) sono le meno ammonite.
*Pagina: Disciplina e gioco duro.*

## 6. Un record offensivo
Il record di gol segnati in una stagione del periodo è dell'**Atalanta 2019/20, con 98 gol**. Seguono Napoli (94) e Roma (90), entrambe nel 2016/17.

## Limiti
- Il dataset non contiene gli **arbitri** (colonna sempre vuota per la Serie A), quindi niente analisi su di loro.
- Dieci stagioni sono poche per parlare di tendenze: queste sono osservazioni, non conclusioni.
- Il 2019/20 e il 2020/21 sono stati giocati in condizioni particolari (sospensione per la pandemia, porte chiuse) e questo può influire su alcuni valori.
