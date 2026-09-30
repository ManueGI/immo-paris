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

## Getting started

Requirements: [uv](https://docs.astral.sh/uv/), [Docker](https://docs.docker.com/get-docker/)
with Compose, and for the TypeScript workspace Node.js 22 with pnpm (`corepack enable`).

```bash
cp .env.example .env                         # then adjust the values
docker compose --profile app up -d --build --wait
```

This starts PostgreSQL + PostGIS, applies the migrations and serves the API on
http://127.0.0.1:8080/docs. To load data and to develop the API, see [api/README.md](api/README.md).

## Contributing

`main` is protected: changes go through pull requests, which are squash-merged once CI is
green. Conventions for human and AI contributors are in [CLAUDE.md](CLAUDE.md).
