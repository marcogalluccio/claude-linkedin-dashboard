# LinkedIn Dashboard — build it with Claude

You are helping the user build their own **offline LinkedIn analytics dashboard**: a single HTML file,
opened in the browser, that merges LinkedIn's official `.xlsx` export with an optional qualitative
layer. This document is the full instruction set. Read it, then guide the user step by step, adapting
to your environment. Talk to the user in their own language.

Source of truth and template files:
**https://github.com/marcogalluccio/claude-linkedin-dashboard**

## What you will produce

A `dashboard.html` (or one self-contained HTML file) with: headline KPIs (impressions, reach,
interactions, followers), growth over time with zoom and Monthly/Weekly/Daily granularity, post
ranking, impressions by pillar, reach vs engagement, and follower demographics. No server, no build
step. It opens from `file://` and works fully offline. The user's data never leaves their machine.

## Step 0 — where are you running?

- **Claude Code (terminal):** you can clone the repo and run Python. Use the full flow below.
- **Cowork / a sandbox that can run code:** download the files, run Python in the sandbox, then hand
  the finished HTML back to the user as a download.
- **Plain chat, no code execution:** you cannot run the pipeline. Point the user to Claude Code, or to
  the installable Cowork skill (link at the bottom), or just show them the live demo at
  https://claude-linkedin-dashboard.vercel.app/demo

## Step 1 — get the files

```
git clone https://github.com/marcogalluccio/claude-linkedin-dashboard
cd claude-linkedin-dashboard
```

In a sandbox without git, download the raw files instead (same repo, branch `main`): `dashboard.html`
and `ingest.py`. You will also create a tiny empty qualitative file in Step 3.

## Step 2 — get the user's LinkedIn export

Ask the user for their LinkedIn content performance export (`.xlsx`). How to get it: on LinkedIn, go
to your profile, open **Analytics / Analisi dei contenuti**, click **Export / Esporta**, pick the
period, download the `.xlsx`. Save it in `data/`, e.g. `data/2026-06-14-linkedin-export.xlsx`.

Note: v1 expects the **Italian** export (sheet names `SCOPERTA`, `INTERESSE`, `FOLLOWER`, plus the
demographic sheets). If the user's export is in another language, tell them.

## Step 3 — build the dashboard (quantitative, fastest path)

```
pip install openpyxl
python3 ingest.py --xlsx data/THEIR-FILE.xlsx --qual empty-qualitative.md
```

where `empty-qualitative.md` is a file you create containing exactly this:

````
```json
{"posts": [], "insights": []}
```
````

This writes `data.js`. Now open `dashboard.html` in the browser. Done.

**In a sandbox**, make a single self-contained file to hand back: take `dashboard.html`, replace the
line `<script src="data.js"></script>` with the contents of `data.js` wrapped in `<script>` ...
`</script>`, save as `linkedin-dashboard.html`, and deliver that file to the user.

## Step 4 — the qualitative layer (optional, richer, Claude Code)

The part LinkedIn does not export (per post hook, saves, profile visits, CTA, and the reading of what
worked) is harvested with Claude in the browser on the LinkedIn analytics pages, then spliced in.
Follow `skills/qualitative-cowork/SKILL.md` in the repo, then run `python3 cowork_delta.py merge`.
Do not use Playwright or an MCP browser for this (LinkedIn flags clean automation); use Claude in the
real logged-in browser session.

## Good to know

- Everything dynamic lives in `data.js`; the template `dashboard.html` never changes on update.
- Never invent numbers. Fields the export does not contain stay empty (posts show as "da etichettare").
- Repo (MIT): https://github.com/marcogalluccio/claude-linkedin-dashboard
- Install on claude.ai as a skill: https://github.com/marcogalluccio/claude-linkedin-dashboard/releases
- Live demo: https://claude-linkedin-dashboard.vercel.app/demo

Built with Claude by Marco Galluccio.
