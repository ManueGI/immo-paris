# Immo Paris API

[![CI](https://github.com/ManueGI/immo-paris-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ManueGI/immo-paris-api/actions/workflows/ci.yml)

Paris real-estate analytics API built on the
[DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)
open data (Demandes de Valeurs Foncières, DGFiP). It serves the Angular dashboard and the
React Native / Expo mobile app.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12 and dependencies)
- [Docker](https://docs.docker.com/get-docker/) with Compose (runs PostgreSQL + PostGIS locally)

## Getting started

```bash
cp .env.example .env         # then adjust the values
uv sync                      # create .venv and install locked dependencies
docker compose up -d --wait  # start PostgreSQL 17 + PostGIS 3.5 on localhost:5432
uv run alembic upgrade head  # create or update the database schema
uv run immo-ingest           # download the latest DVF year and load it into the database
uv run python -m immo_paris  # start the API on http://127.0.0.1:8000 (docs: /docs)
```

Each run replaces all the sales of one year, in a single transaction: re-running it is safe.

```bash
uv run immo-ingest --year 2023                         # load a given year
uv run immo-ingest --raw data/dvf_75_2025.csv.gz       # reload an already downloaded file
for y in 2021 2022 2023 2024 2025; do uv run immo-ingest --year $y; done  # full history
```

## API

Interactive documentation: http://127.0.0.1:8000/docs (OpenAPI schema at `/openapi.json`).

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/sales` | Most recent sales, filterable by `commune_code` and `property_type`, paginated with `cursor` |
| `GET /api/v1/sales/nearby?lat=&lng=&radius_m=` | Sales around a point, nearest first |
| `GET /api/v1/sales/{sale_id}` | One sale |
| `GET /api/v1/stats/communes?year=&property_type=` | Price per m² median and quartiles by commune (null below 10 sales) |

## Docker

The same image runs the API, the migrations and the ingestion.

```bash
docker compose --profile app up -d --build --wait  # database + migrations + API on http://127.0.0.1:8080
docker compose --profile app run --rm --no-deps api immo-ingest --year 2025  # ingestion in a container
docker compose --profile app down                   # stop everything (data is kept)
```

Without `--profile app`, Compose only starts the database, for local development with uv.

## Database

```bash
docker compose exec db psql -U immo -d immo_paris  # open a SQL shell
docker compose stop                                 # stop (data is kept)
docker compose down -v                              # remove container AND data
```

The schema is defined by the SQLAlchemy models in `src/immo_paris/db/models.py` and
versioned with Alembic migrations in `migrations/versions/`:

```bash
uv run alembic revision --autogenerate -m "describe the change"  # draft a migration, then review it
uv run alembic upgrade head                                     # apply pending migrations
uv run alembic downgrade -1                                     # revert the last migration
uv run alembic check                                            # fail if models and migrations differ
```

## Development

```bash
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format
```

## Contributing

Project conventions (language, architecture, API contract, database and test rules) are
documented in [CLAUDE.md](CLAUDE.md) and [.claude/rules/](.claude/rules/). They apply to
human and AI contributors alike.

## DVF cleaning rules

A DVF mutation spans one row per lot, and `valeur_fonciere` is the total price repeated on
each row. The ingestion pipeline (`src/immo_paris/ingestion/dvf.py`) therefore keeps:

1. plain sales only (`Vente`; no exchanges, auctions or off-plan sales);
2. mutations with exactly one dwelling (flat or house), whose other rows are only
   outbuildings (`Dépendance`) or bare land; any extra dwelling or commercial premises
   excludes the mutation;
3. sales with a known price and a positive built surface;
4. a price per m² between 3,000 and 30,000 €.

Every load is recorded in `ingestion_runs` (source file, SHA-256, row count after each
cleaning step), and the `commune_yearly_stats` materialized view is refreshed afterwards.

## Layout

```
src/immo_paris/
├── api/          # FastAPI application and routers
├── repositories/ # SQL queries used by the API
├── core/         # settings (pydantic-settings)
├── db/           # SQLAlchemy models (database tables)
├── ingestion/    # DVF download and cleaning
└── schemas/      # public Pydantic models (JSON contract for clients)
migrations/       # Alembic migrations
tests/
└── fixtures/     # hand-built raw DVF samples
```
