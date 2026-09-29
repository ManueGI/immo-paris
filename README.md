# Immo Paris API

Paris real-estate analytics API built on the
[DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)
open data (Demandes de Valeurs Foncières, DGFiP). It serves the Angular dashboard and the
React Native / Expo mobile app.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python 3.12 and dependencies)

## Getting started

```bash
cp .env.example .env         # then adjust the values
uv sync                      # create .venv and install locked dependencies
uv run immo-ingest           # download DVF and build data/dvf_paris_sample.csv
uv run python -m immo_paris  # start the API on http://127.0.0.1:8000 (docs: /docs)
```

Use `uv run immo-ingest --raw data/dvf_75_2025.csv.gz` to reprocess an already downloaded file.

## Development

```bash
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format
```

## DVF cleaning rules

A DVF mutation spans one row per lot, and `valeur_fonciere` is the total price repeated on
each row. The ingestion pipeline (`src/immo_paris/ingestion/dvf.py`) therefore keeps:

1. plain sales only (`Vente`; no exchanges, auctions or off-plan sales);
2. mutations with exactly one dwelling (flat or house), whose other rows are only
   outbuildings (`Dépendance`) or bare land; any extra dwelling or commercial premises
   excludes the mutation;
3. sales with a known price and a positive built surface;
4. a price per m² between 3,000 and 30,000 €.

## Layout

```
src/immo_paris/
├── api/          # FastAPI application and routers
├── core/         # settings (pydantic-settings)
├── ingestion/    # DVF download and cleaning
└── schemas/      # public Pydantic models (JSON contract for clients)
tests/
└── fixtures/     # hand-built raw DVF samples
```
