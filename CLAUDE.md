# CLAUDE.md

Conventions for anyone (human or AI) changing this codebase. Setup and usage are in
[README.md](README.md); this file covers how to work on the code.

## Project

FastAPI backend of Immo Paris: ingests DVF open data (property sales published by the
DGFiP), cleans it, stores it in PostgreSQL + PostGIS and serves it as JSON to **two
clients at once**: an Angular web dashboard and a React Native / Expo mobile app.

## Commands

```bash
uv sync                          # install locked dependencies
docker compose up -d --wait      # start PostgreSQL 17 + PostGIS 3.5
uv run alembic upgrade head      # apply migrations
uv run python -m immo_paris      # run the API (http://127.0.0.1:8000/docs)
uv run immo-ingest --raw data/dvf_75_2025.csv.gz   # run ingestion on a local file
```

**Definition of done**: all of these pass before committing.

```bash
uv run ruff format --check . && uv run ruff check . && uv run pytest && uv run alembic check
```

## Language

- Everything in the repository is in **English**: identifiers, comments, docstrings, JSON
  fields, error and log messages, tests, commit messages, docs.
- Exception: DVF domain values keep their official French spelling (`"Vente"`,
  `"Appartement"`, `"Dépendance"`), as constants in `ingestion/dvf.py`.

## Architecture

```
src/immo_paris/
├── api/        HTTP layer: routers only, no data access logic
├── schemas/    Pydantic models = public JSON contract of the API
├── db/         SQLAlchemy models = source of truth of the database schema
├── ingestion/  DVF download (cli.py, I/O) and cleaning (dvf.py, pure functions)
└── core/       settings (pydantic-settings, read from env / .env)
migrations/     Alembic migrations
```

- Dependencies point one way: `api → schemas, core`; `ingestion → core`. `api` and
  `ingestion` never import each other.
- Inject dependencies with FastAPI `Depends` (settings, DB sessions) instead of calling
  them inside endpoints, so tests can override them.
- Keep I/O (network, disk, database) at the edges and business rules in pure functions.
- New configuration goes in `core/config.py` **and** `.env.example`. Never commit `.env`.

## API contract

- `schemas/` is what Angular and React Native consume (TypeScript types will be generated
  from `/openapi.json`). Every endpoint declares a `response_model`.
- Keep payloads light and typed for mobile: flat objects, numbers as numbers (no
  `Decimal` serialized as strings), `null` for missing values (never `NaN`), enums for
  closed sets of values.
- Breaking changes to a response (renaming or removing a field, changing a type) require a
  new API version (`/api/v2`). Adding an optional field is not breaking.
- Paginate lists with a cursor (`sale_date`, `id`), not `OFFSET`.

## DVF data rules

A DVF mutation spans **one row per lot**, and `valeur_fonciere` is the **total** price
repeated on every row. Therefore:

- Price per m² is only computed for mutations with exactly one dwelling (outbuildings and
  bare land allowed). See the module docstring of `ingestion/dvf.py`.
- **Never `drop_duplicates()` on DVF rows**: identical rows are distinct unnumbered lots.
- Use `code_commune` (INSEE code), not the postal code, as the administrative area.
- Before changing a cleaning rule, measure its effect on real data (the pipeline logs the
  row count after each step) and add a case to `tests/fixtures/dvf_raw.csv`.

## Database

- Change the schema by editing `db/models.py`, then
  `uv run alembic revision --autogenerate -m "..."`, then **review the generated file**:
  autogenerate turns renames into drop + add (data loss) and does not detect changes to
  CHECK constraints, computed columns, views or extensions.
- Commit a model change and its migration together. Test `upgrade` and `downgrade`.
- Never edit a migration that has been applied outside your machine: write a new one.
- Adding a NOT NULL column to a populated table: add it nullable, backfill, then set
  NOT NULL.
- Money is `Numeric` / `Decimal`, never `float`.
- Coordinates are WGS 84 (SRID 4326) `geography`. `ST_MakePoint` takes
  **longitude first**, then latitude.
- Every index must serve a known query; check new queries with `EXPLAIN ANALYZE`.
- Tests that need a database run against real PostgreSQL + PostGIS, never SQLite.

## Tests

- pytest, Arrange / Act / Assert, one behaviour per test, descriptive names
  (`test_single_dwelling_filter_excludes_mixed_mutations`).
- Test boundaries (e.g. 2,999 / 3,000 €/m²) and every DVF edge case with hand-built
  fixtures rather than the real multi-MB file.

## Commits

- English, imperative subject line (`Add ...`, `Fix ...`), body explaining **why**.
- One logical change per commit; the definition of done passes on every commit.
