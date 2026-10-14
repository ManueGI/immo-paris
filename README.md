# Immo Paris

[![CI](https://github.com/ManueGI/immo-paris/actions/workflows/ci.yml/badge.svg)](https://github.com/ManueGI/immo-paris/actions/workflows/ci.yml)

Paris real-estate analytics platform built on the
[DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)
open data (Demandes de Valeurs Foncières, DGFiP): recent sales, sales around you, and price
per m² statistics by arrondissement.

## Repository

| Directory | Content | Stack |
|---|---|---|
| [api/](api/) | REST API, DVF ingestion, database schema | Python 3.12, FastAPI, PostgreSQL 17 + PostGIS, Alembic, Docker |
| [web/](web/) | Public website: prices by arrondissement and recent sales, server-side rendered | Angular 22 |
| `mobile/` (planned) | Field app with geolocation | React Native / Expo |
| [packages/](packages/) | Shared TypeScript code: [api-client](packages/api-client/), generated from [api/openapi.json](api/openapi.json) | TypeScript, pnpm |

The API contract is committed as `api/openapi.json`: the web and mobile clients are
generated from it, and pull requests that break it fail CI.

## Live

- Website: https://immo-paris-web.onrender.com
- API documentation: https://immo-paris-api.onrender.com/docs

Hosted for free: Render runs the API and web containers ([render.yaml](render.yaml)), Neon
hosts PostgreSQL + PostGIS, and GitHub Actions applies migrations and loads DVF data.
Free services sleep after 15 minutes without traffic: the first visit after a pause can take
about a minute.

## Getting started

Requirements: [uv](https://docs.astral.sh/uv/), [Docker](https://docs.docker.com/get-docker/)
with Compose, and for the TypeScript workspace Node.js 22 with pnpm (`corepack enable`).

```bash
cp .env.example .env                         # then adjust the values
docker compose --profile app up -d --build --wait
```

This starts PostgreSQL + PostGIS, applies the migrations and serves the API on
http://127.0.0.1:8080/docs. To load data and to develop the API, see [api/README.md](api/README.md).

## Development

Open the repository folder in VS Code and accept the recommended extensions: code is
formatted on save like in CI (ruff for Python, Prettier for TypeScript, HTML and SCSS).

Start everything with **Tasks: Run Task → dev: start all** (Command Palette), or by hand:

```bash
docker compose up -d --wait                  # PostgreSQL + PostGIS (localhost:5432)
cd api && uv run python -m immo_paris        # API: http://127.0.0.1:8000/docs
pnpm --filter @immo-paris/web start          # website: http://localhost:4200
```

## Contributing

`main` is protected: changes go through pull requests, which are squash-merged once CI is
green. Conventions for human and AI contributors are in [CLAUDE.md](CLAUDE.md).
