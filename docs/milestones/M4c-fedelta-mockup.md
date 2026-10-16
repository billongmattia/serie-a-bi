# M4c – Frontend Streamlit: stile identico al mockup

**Stato:** 🔄 piano scritto (2026-10-16), **in attesa del via libera** · **Piano:** [2026-10-16-streamlit-fedelta-mockup](../superpowers/plans/2026-10-16-streamlit-fedelta-mockup.md) · **Riferimento:** [mockup](../design/README.md)

**Perché esiste:** la veste grafica di M4b ha ottenuto tema scuro e schede, ma **non somiglia al mockup** (che ha pannelli bianchi su cornice blu scuro, sidebar con logo e icone, selettori nell'intestazione, ecc.). Nella verifica di M4b erano stati controllati i numeri, non l'aspetto. M4c rifà l'aspetto, **solo stile**.

**Obiettivo:** frontend stilisticamente identico al mockup, con i **soli contenuti che il dataset ha** (stesse pagine e stessi numeri di oggi). **Niente** "Statistiche giocatori", "Partite", tab "Giocatori", "Dettaglio partite", "Confronto", barrette Champions/retrocessione, immagine di stadio.

## Task (corrispondono ai Task 1–5 del piano)
- [ ] **M4c.1 Fondamenta** – tema chiaro di base, CSS (sfondo scuro, sidebar, intestazione, pannello bianco, schede, tabelle, badge), componenti HTML puri e testati con **escape** dei valori.
- [ ] **M4c.2 Grafici in stile chiaro** – aree con sfumatura, barre blu e rosse, legenda in alto, titoli spostati sopra il grafico.
- [ ] **M4c.3 Home e Classifica** – intestazione con selettore, 5 schede con icona, tabella `Pos Squadra G V N P GF GS DR Punti Ultime 5` con forma a cerchi.
- [ ] **M4c.4 Squadra, Confronti, Disciplina, Insight, About e menu laterale** – selettori nell'intestazione, tab, ultime partite con badge V/N/P, menu con logo e icone. Commit unico dei task 1–4 a suite verde.
- [ ] **M4c.5 Verifica visiva contro il mockup, documentazione e revisione** – confronto pagina per pagina con una lista di controllo, correzione dei selettori CSS, screenshot reali (a cura dell'utente), README, spiegazione 11, revisione.

## Metodo (diverso da M4b)
Ogni pagina si confronta **fianco a fianco** con il riquadro del mockup e si corregge finché le differenze visibili spariscono. I test garantiscono i contenuti e l'escape dell'HTML; l'aspetto lo garantisce la verifica visiva.

## Fatto quando
Le pagine dell'app, affiancate al mockup, hanno lo stesso aspetto (a parte i contenuti che il dataset non ha), tutti i numeri coincidono con il database, i test passano e il README mostra screenshot reali.
