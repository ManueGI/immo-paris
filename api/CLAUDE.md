# api/CLAUDE.md

FastAPI backend: ingests DVF open data, cleans it, stores it in PostgreSQL + PostGIS and
serves it as JSON to the web and mobile apps. Setup and usage are in
[README.md](README.md). Repository-wide rules are in the root [CLAUDE.md](../CLAUDE.md).

## Commands

Run from `api/` (or add `--directory api` after `uv run` from the root). The database
runs from the repository root: `docker compose up -d --wait`.

```bash
uv sync                          # install locked dependencies
uv run alembic upgrade head      # apply migrations
uv run python -m immo_paris      # run the API (http://127.0.0.1:8000/docs)
uv run immo-ingest --raw data/dvf_75_2025.csv.gz   # run ingestion on a local file
uv run immo-openapi                                # regenerate openapi.json after an API change
```

Settings are read from the environment, then the root `.env`, then an optional `api/.env`.

The Docker image (built from `api/`) runs as an unprivileged user with a read-only
`/app`, and never contains secrets (`.env` is excluded by `.dockerignore`): configuration
comes from environment variables. Migrations run as a separate one-off container, not at
API startup: `docker compose --profile app up -d --build --wait` from the root.

**Definition of done**: all of these pass before committing. CI
(`.github/workflows/ci.yml`) runs the same checks, plus the Docker build.

```bash
uv run ruff format --check . && uv run ruff check . && uv run pytest && uv run alembic check
```

## Architecture

- `api/` HTTP layer · `repositories/` SQL queries, the only data access of the API ·
  `schemas/` public JSON contract · `db/` database schema · `ingestion/` DVF download,
  cleaning and loading · `core/` settings (all under `src/immo_paris/`).
- Dependencies point one way: `api → repositories → db, schemas`; `ingestion → db, core`.
  `api` and `ingestion` never import each other.
- Inject dependencies with FastAPI `Depends` (settings, DB sessions) instead of calling
  them inside endpoints, so tests can override them.
- Keep I/O (network, disk, database) at the edges and business rules in pure functions.
- New configuration goes in `core/config.py` **and** the root `.env.example`.
