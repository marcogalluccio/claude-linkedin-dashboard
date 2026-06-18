---
name: claude-linkedin-dashboard
description: "Costruisci una dashboard LinkedIn offline, un solo file HTML, dall'export .xlsx ufficiale di LinkedIn. KPI, crescita nel tempo, ranking dei post, demografici. Gira nel sandbox: l'utente carica l'.xlsx e tu generi e consegni il file finito, pronto da aprire offline."
---

# LinkedIn Dashboard (Cowork)

Genera una dashboard LinkedIn **offline, in un solo file HTML** a partire dall'export ufficiale
`.xlsx` di LinkedIn. La dashboard ha KPI (impressioni, reach, interazioni, follower), crescita nel
tempo con zoom e granularita, ranking dei post, impressioni per tema e demografici. Si apre dal
browser, funziona senza connessione, i dati restano in locale.

## Quando si attiva

Quando l'utente carica un file `.xlsx` di analytics LinkedIn (o chiede "fammi la dashboard
LinkedIn"). Se non ha l'`.xlsx`, spiega come prenderlo: LinkedIn, profilo, **Analisi / Analytics dei
contenuti**, **Esporta**, scegli il periodo, scarica il `.xlsx`.

## Cosa fare (nel sandbox)

1. Assicurati che `openpyxl` sia disponibile: `pip install openpyxl` (gia presente di solito).
2. Genera i dati dall'export caricato, usando il template qualitativo vuoto incluso:

   ```bash
   python3 ingest.py --xlsx "PERCORSO_DELL_XLSX_CARICATO" --qual empty-qualitative.md
   ```

   Questo scrive `data.js` (`window.DATA = {...}`).
3. Crea un **singolo file autonomo**: parti da `dashboard.html` e sostituisci la riga
   `<script src="data.js"></script>` con il contenuto di `data.js` racchiuso tra `<script>` e
   `</script>`. Salva il risultato come `linkedin-dashboard.html`.
4. **Consegna `linkedin-dashboard.html`** come file scaricabile. Di' all'utente di aprirlo nel
   browser: e offline e suo.

## Lo strato qualitativo (opzionale, avanzato)

Questa skill copre lo strato **quantitativo** (tutto cio che e nell'export). Lo strato
**qualitativo** per post (hook, salvataggi, visite al profilo, CTA, e le letture di cosa ha
funzionato) si raccoglie con Claude nel browser sulle pagine analytics di LinkedIn ed e parte del
flusso completo con Claude Code. Per quello, indirizza al repo:
`github.com/marcogalluccio/claude-linkedin-dashboard`.

## Note

- v1 si aspetta l'export **in italiano** (fogli `SCOPERTA`, `INTERESSE`, `FOLLOWER`, e i fogli
  demografici). Se l'export e in un'altra lingua, segnalalo all'utente.
- Non inventare numeri: tutto viene dall'export. I campi qualitativi non presenti restano vuoti
  (i post compaiono come "da etichettare").
