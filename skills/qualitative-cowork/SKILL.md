---
name: linkedin-dashboard-qualitative-cowork
description: Flusso delta+splice per raccogliere lo strato qualitativo dei post LinkedIn (hook, pillar, formato, CTA, salvataggi, visite, follower per post) via Claude nel browser (Cowork). Claude Code genera un prompt mirato ai soli post nuovi, Cowork scrive un file di staging, Claude Code lo splicia nel qualitativo e rigenera la dashboard.
---

# Raccolta qualitativa via Claude Cowork (delta + splice)

Lo strato **quantitativo** (impressioni, interazioni, follower, demografici) arriva dall'export `.xlsx`.
Questo strato **qualitativo** è la parte che LinkedIn non esporta: hook, pillar, formato, CTA, salvataggi,
visite al profilo, follower acquisiti per post, e la lettura di cosa ha funzionato.

Si raccoglie con **Claude nel browser (Cowork in Chrome)**, non con Claude Code: serve un agente che
naviga le pagine analytics di LinkedIn mentre sei loggato. **Non usare Playwright/MCP browser**:
LinkedIn flagga l'automazione "pulita" come bot e c'è rischio shadow ban del profilo. Cowork gira dentro
la tua sessione reale del browser.

## Idea chiave: delta, non tutta la classifica

`ingest.py` legge **un solo** file qualitativo (il più recente in `qualitative/`) e fa il join per URL.
Quindi non serve rietichettare 50 post ogni volta: si tiene il qualitativo esistente e si **spliciano**
solo i post **nuovi/da etichettare** (quelli che il nuovo `.xlsx` ha in classifica ma il qualitativo
ancora non copre). Lo script `cowork_delta.py` automatizza diff, generazione prompt e splice.

## Flusso a 3 fasi

### 1. Prep — Claude Code

1. Metti il nuovo export in `data/AAAA-MM-GG-linkedin-export.xlsx`.
2. Dalla cartella del progetto:

   ```bash
   python3 cowork_delta.py prompt
   ```

   Legge l'`.xlsx` più recente + il qualitativo più recente, calcola i post non ancora etichettati,
   marca quali sono in **top-10 per impressioni** (`[TOP -> enr]`, meritano il blocco di approfondimento),
   crea `qualitative/incoming/`, e **stampa il prompt Cowork già pronto** con gli URL/date/impressioni esatti.
   Se non c'è nulla da etichettare, lo dice e si ferma.

3. Copia il prompt stampato (il blocco fra le righe di trattini).

### 2. Raccolta — Claude Cowork (Chrome loggato)

1. In Chrome, apri LinkedIn loggato, vai su **Analytics dei contenuti**.
2. Avvia Claude in modalità Cowork, con il tuo workspace connesso.
3. Incolla il prompt generato dalla fase 1.
4. Cowork raccoglie i post e **scrive da solo** il file
   `qualitative/incoming/AAAA-MM-GG-cowork-new-posts.md` (niente copia-incolla di ritorno).

### 3. Merge — Claude Code

Quando dici "fatto":

```bash
python3 cowork_delta.py merge
```

Legge `qualitative/incoming/<più recente>.md`, valida il JSON, **splicia** i post nel qualitativo base
(incoming vince sui duplicati per `activity id`), **sostituisce le insights** con quelle fresche di Cowork
(regola fissa: sostituisci sempre, niente accumulo), scrive `qualitative/AAAA-MM-GG-qualitative.md` e
rilancia `ingest.py`. Poi apri `dashboard.html` per verifica.

## Schema che Cowork deve produrre

Il file di staging deve contenere **un solo blocco ```json```** (note libere prima sono ok). Per ogni post:

- `url` (chiave di join, obbligatorio), `date` (`AAAA-MM-GG`), `hook` (apertura del post),
  `type` (`Originale`/`Video`/`Quote`/`Carosello`/`Export`), `pillar` (libera), `group` (uno tra
  `Builder`/`Thought`/`Event`/`Consulting`/`Personal`/`Stablecoin`/`Hub`, dà il colore),
  `reaz`/`comm` (numeri o `null`).
- Solo per i post marcati `[TOP -> enr]`: oggetto `enr` con `reach`/`visite`/`follower`/`diff`/`salv`/
  `invii`/`formato`/`cta`. `reach` spesso è `null` (LinkedIn non lo espone nella vista post).
- `insights`: 4-6 letture rapide in italiano, ognuna che inizia con una sintesi breve.

Regola d'oro per Cowork: **non inventare numeri**. Campo non esposto → `null` o omesso.

## Cosa NON serve raccogliere

I demografici (località, anzianità, dimensione azienda, settore), i totali e le serie giornaliere
arrivano già dall'export `.xlsx`. Qui solo il qualitativo per post + le letture.
