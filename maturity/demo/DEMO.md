# Friday / Saturday demo script

## Path to show Chris (5–7 min)

1. **Split** — Erik `:8000` listening · me `:8100` maturity · visual `:8200`.
2. **Health** — `GET /health` shows no_auto_post / no_auto_vote.
3. **Transition** — POST `/v1/transition` with email false → blocked; email true + joined → advances to `value`.
4. **Guardrails** — shortener / missing disclosure → `block: true`.
5. **TFA** — bought aged account → `ok: false`.
6. **Gates** — `/v1/gates/infer` reads Erik SQLite (scrape now also writes SQLite; if 403, `import_csv_to_sqlite.py`).
7. **Bake-off** — `python -m maturity.demo.bakeoff_erik_vs_sv` (needs `SOCIAVAULT_KEY` for SV half).
8. **Honest status** — OAuth live needs Reddit web-app secrets; 403 on scrape is expected sometimes — why SV bake-off matters.

## Visual

```bash
# APIs already: Erik :8000 · Maturity :8100
python maturity/demo/serve_visual.py   # http://127.0.0.1:8200/
```

## Do not demo

- Auto-submit
- Buying accounts
- Declaring Erik HTML scrape as Bravestep product path before bake-off numbers
