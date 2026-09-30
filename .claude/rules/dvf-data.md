---
paths:
  - "api/src/immo_paris/ingestion/**"
  - "api/tests/fixtures/**"
  - "api/tests/test_dvf_*.py"
---

# DVF data

A DVF mutation spans **one row per lot** (flat, cellar, parking, shop, land parcel), and
`valeur_fonciere` is the **total** price of the mutation, repeated on every row.

- Price per m² is only computed for mutations with exactly one dwelling (outbuildings and
  bare land allowed); see the module docstring of `ingestion/dvf.py`.
- **Never `drop_duplicates()` on DVF rows**: identical rows are distinct unnumbered lots
  of whole-building sales.
- Use `code_commune` (INSEE code, e.g. `75111`) as the administrative area, not the postal
  code, which is a La Poste routing code.
- DVF domain values keep their official French spelling (`"Vente"`, `"Appartement"`,
  `"Dépendance"`) and are defined once, as constants in `ingestion/dvf.py`.
- Read codes as strings (`dtype="string"`): postal and INSEE codes are not numbers
  (`01000` would become `1000`).
- Cleaning steps are pure functions `DataFrame -> DataFrame` chained in `clean()`; keep
  network and disk access in `cli.py` / `download()`.
- Before changing a cleaning rule, measure its effect on the real file (the pipeline logs
  the row count after each step) and add a case to `tests/fixtures/dvf_raw.csv`.
