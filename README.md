# LinkedIn Dashboard

Your LinkedIn analytics, offline and yours. A single file dashboard, built with Claude, that merges
the two halves of your data:

- **Quantitative**, straight from LinkedIn's official `.xlsx` export (impressions, interactions,
  follower growth, daily series, demographics).
- **Qualitative**, the part LinkedIn does not export (per post hook, pillar, format, CTA, saves,
  profile visits, followers gained, and your own reading of what worked), harvested with Claude in
  the browser.

You drop in two inputs, run one Python script, and reopen the HTML. No server, no build step, no
framework. It opens straight from `file://` and works fully offline.

**Live demo (real numbers):** https://claude-linkedin-dashboard.vercel.app/demo
**Landing page:** https://claude-linkedin-dashboard.vercel.app

## Fastest way: one line to Claude

Paste this to Claude (Claude Code, Cowork, or claude.ai with web access). It reads the instructions and
builds the dashboard with you, no download:

```
read https://claude-linkedin-dashboard.vercel.app/skill.md and help me create my LinkedIn dashboard
```

## Which Claude do you use? / Quale Claude usi?

There is no zero-install path here: building the dashboard runs a small Python script, so you need
Claude that can run code. Two ways:

1. **Claude Code** (terminal, recommended). Clone this repo, drop your `.xlsx` in `data/`, and ask
   Claude to harvest the qualitative layer and run `ingest.py`. Full power, including the qualitative
   browser harvest. Start here if you can.
2. **Cowork** (Claude on claude.ai, no terminal). Install the packaged skill
   ([download the zip from Releases](https://github.com/marcogalluccio/claude-linkedin-dashboard/releases))
   as a Skill, upload your `.xlsx`, and Claude builds the dashboard in the sandbox and hands you the
   finished file. Quantitative dashboard; the qualitative layer is a Claude Code extra.

> In italiano: serve far girare un piccolo script Python, quindi si usa Claude Code (consigliato) o
> Cowork, non la chat semplice. Con Claude Code cloni il repo; con Cowork installi la skill dalle
> Releases e carichi l'`.xlsx`.

## What you get

- Headline KPIs (impressions, reach, interactions, followers, top save rate).
- Growth over time, with a shared horizon zoom (All, 180d, 90d, 30d, 7d, custom dates) and Monthly /
  Weekly (Mon to Sun) / Daily granularity, for both the impressions+interactions chart and the
  follower chart (cumulative or new per period).
- Post ranking (bars), impressions by pillar (donut), reach vs engagement (scatter, bubble size = saves).
- An enriched top 10 (saves, profile visits, followers, sends, format, CTA).
- The full post table, sortable and searchable.
- Follower demographics (location, seniority, company size, industry).
- Your "quick reads", the qualitative insights of the period.

## How it works (three layers)

```
data/*.xlsx          (quantitative, official LinkedIn export, dated)
qualitative/*.md     (qualitative, one ```json block, dated)
        │
        ▼  python3 ingest.py   (joins the two by post URL)
data.js              (generated: window.DATA = { meta, kpis, daily, posts, demographics, insights })
        │
        ▼  <script src="data.js">
dashboard.html       (stable template + render code; never edited on update)
```

The HTML is a template: it holds the structure and all the rendering. It never changes when you
update. Everything dynamic comes from `data.js`, which `ingest.py` regenerates. The two data layers
are joined by the post URL, so the join is exact even when several posts share a date.

## Quick start (Claude Code)

1. **Quantitative.** On LinkedIn, export your content performance to `.xlsx` and drop it in
   `data/YYYY-MM-DD-linkedin-export.xlsx`.
2. **Qualitative.** Run `python3 cowork_delta.py prompt`, paste the printed prompt into Claude in the
   browser (Cowork) on your LinkedIn analytics page; it writes the result to `qualitative/incoming/`.
3. **Merge.** Run `python3 cowork_delta.py merge`. It splices the new posts into the qualitative file
   and runs `ingest.py`.
4. **Open** `dashboard.html`.

You can also run `python3 ingest.py` directly when only the `.xlsx` changed (unlabeled posts show as
"da etichettare"). The two skills in `skills/` document the data contracts and the harvest prompt.

## Requirements

- Python 3 with `openpyxl` (`pip install openpyxl`).
- A modern browser. That is all.

## Layout

```
.
├── README.md
├── LICENSE
├── dashboard.html         # template + render code, reads window.DATA
├── data.js                # GENERATED, do not edit by hand (ships with a real demo dataset)
├── ingest.py              # the engine: xlsx + qualitative -> data.js
├── cowork_delta.py        # delta+splice helper: `prompt` / `merge`
├── demo/                  # the live demo served on Vercel
├── skills/
│   ├── ingest/SKILL.md
│   └── qualitative-cowork/SKILL.md
└── cowork/                # the packaged skill for claude.ai / Cowork (also in Releases as a zip)
```

## Note on the demo data

`data.js` ships with a real dataset (one year of LinkedIn activity) so the dashboard is alive the
moment you open it. Replace it with your own by running the pipeline on your export.

## License

MIT. Built with Claude by [Marco Galluccio](https://www.linkedin.com/in/marco-galluccio/).
