# BraveStep Reddit — Listening + Maturity (lab)

Joint lab from **Erik** (listening scrape) + **me** (account maturity).

| Half | Path | Port | Job |
|---|---|---|---|
| Listening | this repo (`main.py`, `api/`) | `:8000` | Scrape → CSV **and SQLite** → API |
| Maturity | `maturity/` | `:8100` | OAuth → phases → gates → guardrails → HITL |

## Hard rules

- Observe / coach only on maturity — **never** auto-post / auto-vote
- Product listening preference: **SociaVault** (see bake-off). Erik HTML scrape = research corpus + backup
- Keep secrets in `maturity/.env` only (gitignored)

## Quick start

```bash
# Listening API
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --api   # http://127.0.0.1:8000/docs

# Maturity API (from repo root)
python3 -m venv maturity/.venv && source maturity/.venv/bin/activate
pip install -r maturity/requirements.txt
cp maturity/.env.example maturity/.env   # add SOCIAVAULT_KEY etc.
export PYTHONPATH=.
python -m maturity.cli test
python -m maturity.cli api               # http://127.0.0.1:8100/docs

# Visual demo (both APIs up)
python maturity/demo/serve_visual.py     # http://127.0.0.1:8200/
```

## Scrape → maturity join

`main.py` now writes **CSV + SQLite** (`data/reddit_scraper.db`).  
Maturity gates/farmability read that DB. If live scrape 403s but CSV exists:

```bash
python import_csv_to_sqlite.py --csv data/r_startups/posts.csv --sub startups
```

## Bake-off (Erik vs SociaVault)

```bash
export PYTHONPATH=.
# SOCIAVAULT_KEY in maturity/.env
python -m maturity.demo.bakeoff_erik_vs_sv --subs startups,saas --limit 10
```

See `maturity/demo/bakeoff_results.md` after a run.
