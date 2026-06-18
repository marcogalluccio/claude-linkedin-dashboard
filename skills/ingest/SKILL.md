---
name: linkedin-dashboard-ingest
description: Rigenera data.js del LinkedIn Dashboard dall'export .xlsx di LinkedIn unito allo strato qualitativo. Usala ogni volta che arriva un nuovo export o aggiorni il qualitativo.
---

# Ingest (quantitativo) del LinkedIn Dashboard

Trasforma l'export ufficiale LinkedIn (`.xlsx`) + il file qualitativo (`.md`) in `data.js`,
che `dashboard.html` legge. Deterministico: stessi input, stesso `data.js`.

## Quando

Ogni volta che:
- scarichi un nuovo export `.xlsx` da LinkedIn, oppure
- aggiorni/aggiungi un file in `qualitative/`.

## Come

1. Metti l'export in `data/AAAA-MM-GG-linkedin-export.xlsx`.
2. Assicurati che esista un `qualitative/AAAA-MM-GG-qualitative.md` aggiornato
   (vedi la skill `qualitative-cowork` per produrlo).
3. Dalla cartella del progetto:

   ```bash
   python3 ingest.py
   ```

   Usa automaticamente il file più recente in `data/` e in `qualitative/`.
   Per uno snapshot storico, passa i file espliciti:

   ```bash
   python3 ingest.py --xlsx data/2026-06-04-linkedin-export.xlsx --qual qualitative/2026-06-04-qualitative.md
   ```

4. Apri `dashboard.html`.

Requisiti: `python3` + `openpyxl` (`pip install openpyxl`).

## Cosa fa l'ingest

- Legge i 5 fogli dell'export: `SCOPERTA` (totali), `INTERESSE` (serie giornaliera
  impressioni + interazioni), `POST PRINCIPALI` (impressioni e interazioni per post,
  per URL), `FOLLOWER` (totale + nuovi al giorno), `DATI DEMOGRAFICI`.
- Legge il blocco ```json``` dal file qualitativo.
- **Unisce per URL del post**: l'export è autoritativo su impressioni/interazioni,
  il qualitativo fornisce hook/pillar/tipo/reaz/comm/arricchimento.
- I post nell'export ma non nel qualitativo diventano "(da etichettare · data)".
- I post a 0 impressioni (presenti solo nella lista interazioni dell'export) restano
  fuori dalla classifica; le loro interazioni sono comunque nei totali.
- Riordina per impressioni e scrive `data.js`.
- Stampa un riepilogo: numero post, post da etichettare, eventuali pillar senza colore.

## Contratto: `data.js`

```js
window.DATA = {
  meta: { exportDate, periodStart, periodEnd, postCount, xlsx, qualitative },
  kpis: { impressions, reached, interactions, followers, follGainedYear, follBase,
          saveRateRecord:{ value, label } },
  daily: { start:[y,m,d], imp:[...], inter:[...], follNew:[...] },
  posts: [ { rank, hook, type, pillar, group, reaz, comm, imp, inter, date, enr? } ],
  demographics: { localita, anzianita, dimensione, settore },   // [[label, pct], ...]
  insights: [ "..." ]
};
```

`reaz`/`comm` possono essere `null` (post solo-export). `enr` è presente solo sui post studiati.
`group` deve essere uno dei pillar noti in `dashboard.html` (`GROUPS`): Builder, Thought,
Event, Consulting, Personal, Stablecoin, Hub. Un pillar ignoto ricade su un colore neutro.
