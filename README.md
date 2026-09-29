# Immo Paris API

API d'analyse immobilière parisienne basée sur les données ouvertes
[DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/)
(Demandes de Valeurs Foncières, DGFiP). Elle alimente le dashboard Angular et l'application
mobile React Native / Expo.

## Prérequis

- [uv](https://docs.astral.sh/uv/) (gère Python 3.12 et les dépendances)

## Démarrage

```bash
cp .env.example .env        # puis adapter les valeurs
uv sync                     # crée .venv et installe les dépendances verrouillées
uv run immo-ingest          # télécharge DVF et génère data/dvf_paris_sample.csv
uv run python -m immo_paris # lance l'API sur http://127.0.0.1:8000 (docs : /docs)
```

## Développement

```bash
uv run pytest               # tests
uv run ruff check .         # lint
uv run ruff format .        # formatage
```

## Structure

```
src/immo_paris/
├── api/          # application FastAPI et routers
├── core/         # configuration (pydantic-settings)
├── ingestion/    # téléchargement et nettoyage DVF
└── schemas/      # modèles Pydantic exposés (contrat JSON des clients)
tests/
```
