#!/usr/bin/env python3
"""
cowork_delta.py — flusso delta+splice per lo strato qualitativo del LinkedIn Dashboard.

Due sottocomandi:

  python3 cowork_delta.py prompt
      Legge l'export .xlsx piu' recente in data/ e il qualitativo piu' recente in
      qualitative/, calcola i post in classifica NON ancora etichettati, marca quali
      sono in top-10 per impressioni (-> blocco `enr`), crea qualitative/incoming/ e
      STAMPA il prompt gia' pronto da incollare in Claude Cowork.

  python3 cowork_delta.py merge
      Legge qualitative/incoming/<piu' recente>.md (output di Cowork), valida il JSON,
      SPLICIA i post nuovi in quelli del qualitativo base (incoming vince sui duplicati),
      SOSTITUISCE le insights con quelle fresche di Cowork, scrive
      qualitative/<data-export>-qualitative.md e rilancia ingest.py.

Deterministico. La chiave di join e' sempre l'id `activity:<n>` dell'URL del post.
"""
import openpyxl, json, re, sys, glob, os, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ENR_TOP_N = 10  # i primi N post per impressioni meritano il blocco enr


def latest(pattern):
    files = sorted(glob.glob(os.path.join(HERE, pattern)))
    if not files:
        sys.exit(f"Nessun file per {pattern}")
    return files[-1]


def actid(url):
    m = re.search(r"activity:(\d+)", url or "")
    return m.group(1) if m else None


def date_prefix(path):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    return m.group(1) if m else datetime.date.today().isoformat()


def to_iso(d):
    """ '1/6/2026' (g/m/A) -> '2026-06-01' """
    if isinstance(d, datetime.datetime):
        return d.date().isoformat()
    if isinstance(d, datetime.date):
        return d.isoformat()
    s = str(d).strip()
    for sep in ("/", "-"):
        if sep in s:
            p = s.split(sep)
            if len(p) == 3:
                g, m, a = p
                if len(p[0]) == 4:  # gia' A-m-g
                    a, m, g = p
                return f"{int(a):04d}-{int(m):02d}-{int(g):02d}"
    return s


def read_qual_json(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    if not m:
        sys.exit(f"Nessun blocco json in {path}")
    return json.loads(m.group(1))


def read_imp_posts(xlsx_path):
    """ POST PRINCIPALI, blocco destro (URL/Data/Impressioni), ordinato per impressioni. """
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["POST PRINCIPALI"]
    rows = list(ws.iter_rows(values_only=True))
    posts = []
    for r in rows[3:]:
        url, date, imp = r[4], r[5], r[6]
        if url:
            posts.append({
                "act": actid(url), "url": url, "date": to_iso(date),
                "imp": int(float(imp)) if imp else 0,
            })
    return posts


# --------------------------------------------------------------------------- prompt

PROMPT_TEMPLATE = """Sei su LinkedIn, nelle analytics dei miei contenuti, loggato come me, e hai accesso a questo workspace. Mi serve lo strato qualitativo di {n} post specifici (non tutta la classifica).

Quando hai finito, scrivi il risultato in questo file del workspace:
qualitative/incoming/{snap}-cowork-new-posts.md
Il file deve contenere il blocco ```json``` descritto sotto (puoi mettere prima qualche tua nota libera, ma il blocco JSON deve esserci ed essere valido). Non toccare nessun altro file.

I {n} post (per URL):
{post_list}

Per ognuno raccogli:
- url: l'URL del post (riusa quello che ti ho dato, e' la chiave di join). Obbligatorio.
- date: data di pubblicazione, formato AAAA-MM-GG.
- hook: la prima frase / apertura del post (anche troncata).
- type: formato, uno tra Originale, Video, Quote, Carosello, Export.
- pillar: etichetta tematica libera (es. Builder/System, Consulting, Event/Recap, Thought).
- group: uno tra Builder, Thought, Event, Consulting, Personal, Stablecoin, Hub (serve per il colore).
- reaz: numero di reazioni. comm: numero di commenti. Se non li trovi, null.

Solo per i post marcati [TOP -> enr] aggiungi un oggetto `enr` (dalla pagina del singolo post):
- reach (utenti raggiunti, null se non esposto), visite (visite al profilo), follower (follower acquisiti dal post), diff (diffusioni/repost), salv (salvataggi), invii (invii), formato (testo / immagine singola / carosello / video), cta (tipo di call to action: domanda aperta, link, commenta -> DM, nessuna).

Aggiungi infine `insights`: da 4 a 6 letture rapide in italiano, una frase ciascuna, ognuna che inizia con una sintesi breve (es. "Il video e' il segnale del giro."). Concentrati su cosa e' successo di recente (i post piu' nuovi della lista).

Scrivi nel file un solo blocco ```json``` in questo schema esatto:

```json
{{
  "posts": [
    {{ "url": "https://www.linkedin.com/feed/update/urn:li:activity:0000000000000000000",
       "date": "AAAA-MM-GG", "hook": "...", "type": "...", "pillar": "...", "group": "...",
       "reaz": 0, "comm": 0,
       "enr": {{ "reach": null, "visite": 0, "follower": 0, "diff": 0, "salv": 0, "invii": 0,
                "formato": "...", "cta": "..." }} }}
  ],
  "insights": [ "..." ]
}}
```

Non inventare numeri: se un campo non e' esposto, omettilo o mettilo a null. `enr` solo sui post marcati [TOP -> enr]."""


def cmd_prompt():
    xlsx = latest("data/*.xlsx")
    qual = latest("qualitative/*.md")
    snap = date_prefix(xlsx)
    imp_posts = read_imp_posts(xlsx)
    labeled = {actid(p["url"]) for p in read_qual_json(qual)["posts"]}
    top_ids = {p["act"] for p in imp_posts[:ENR_TOP_N]}
    new = [p for p in imp_posts if p["act"] not in labeled]

    os.makedirs(os.path.join(HERE, "qualitative", "incoming"), exist_ok=True)

    if not new:
        print(f"# Nessun post da etichettare: il qualitativo {os.path.basename(qual)} "
              f"copre gia' tutta la classifica di {os.path.basename(xlsx)}.")
        return

    lines = []
    for i, p in enumerate(new, 1):
        tag = "  [TOP -> enr]" if p["act"] in top_ids else ""
        lines.append(f"{i}. https://www.linkedin.com/feed/update/urn:li:activity:{p['act']} "
                     f"(pubblicato {p['date']}, ~{p['imp']:,} impressioni){tag}".replace(",", "."))

    print(f"# {len(new)} post da etichettare (export {os.path.basename(xlsx)}, "
          f"base qualitativa {os.path.basename(qual)}).")
    print(f"# Incolla in Claude Cowork il prompt qui sotto. Poi: python3 cowork_delta.py merge\n")
    print("-" * 72)
    print(PROMPT_TEMPLATE.format(n=len(new), snap=snap, post_list="\n".join(lines)))
    print("-" * 72)


# ---------------------------------------------------------------------------- merge

def cmd_merge():
    incoming = latest("qualitative/incoming/*.md")
    base = latest("qualitative/*.md")  # snapshot precedente (top-level, non incoming/)
    snap = date_prefix(incoming)

    new = read_qual_json(incoming)
    base_data = read_qual_json(base)

    # splice: incoming vince sui duplicati per activity id, ordine = base poi nuovi
    by_id = {actid(p["url"]): p for p in base_data["posts"]}
    added, updated = 0, 0
    for p in new["posts"]:
        aid = actid(p["url"])
        (updated, added) = (updated + 1, added) if aid in by_id else (updated, added + 1)
        by_id[aid] = p
    merged_posts = list(by_id.values())

    # insights: SOSTITUISCI sempre con le fresche di Cowork
    insights = new.get("insights", [])

    out = {"posts": merged_posts, "insights": insights}
    header = (
        f"# Strato qualitativo LinkedIn - snapshot {snap}\n\n"
        f"Generato da cowork_delta.py merge: {len(base_data['posts'])} post dallo snapshot "
        f"{date_prefix(base)} + {added} nuovi e {updated} aggiornati da "
        f"`incoming/{os.path.basename(incoming)}`. Insights sostituite con le {len(insights)} "
        f"fresche di Cowork (regola: sostituisci sempre).\n"
        f"L'ingest legge solo il blocco json; la chiave di join con l'export e' l'URL del post.\n\n"
        f"```json\n{json.dumps(out, ensure_ascii=False, indent=2)}\n```\n"
    )
    out_path = os.path.join(HERE, "qualitative", f"{snap}-qualitative.md")
    open(out_path, "w", encoding="utf-8").write(header)
    print(f"✓ scritto qualitative/{snap}-qualitative.md "
          f"({len(merged_posts)} post: +{added} nuovi, {updated} aggiornati | {len(insights)} insights)")

    print("--- ingest ---")
    subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], cwd=HERE)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prompt":
        cmd_prompt()
    elif cmd == "merge":
        cmd_merge()
    else:
        sys.exit("Uso: python3 cowork_delta.py [prompt|merge]")
