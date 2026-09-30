# CLAUDE.md

Conventions for anyone (human or AI) changing this codebase. Setup and usage are in
[README.md](README.md).

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

Everything in the repository is in **English**: identifiers, comments, docstrings, JSON
fields, error and log messages, tests, commit messages, docs. Only DVF domain values keep
their official French spelling.

## Architecture

- `api/` HTTP layer · `repositories/` SQL queries, the only data access of the API ·
  `schemas/` public JSON contract · `db/` database schema · `ingestion/` DVF download,
  cleaning and loading · `core/` settings.
- Dependencies point one way: `api → repositories → db, schemas`; `ingestion → db, core`.
  `api` and `ingestion` never import each other.
- Inject dependencies with FastAPI `Depends` (settings, DB sessions) instead of calling
  them inside endpoints, so tests can override them.
- Keep I/O (network, disk, database) at the edges and business rules in pure functions.
- New configuration goes in `core/config.py` **and** `.env.example`. Never commit `.env`.

## Commits

- English, imperative subject line (`Add ...`, `Fix ...`), body explaining **why**.
- One logical change per commit; the definition of done passes on every commit.

## Where the other rules live

- `.claude/rules/`: rules loaded when working on matching files (API contract, DVF data,
  database, tests).
- `.claude/skills/`: step-by-step procedures (`new-migration`).
- `.claude/settings.json`: a hook formats every edited Python file with ruff and reports
  lint errors.
