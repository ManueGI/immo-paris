"""Télécharge le fichier DVF le plus récent pour le département configuré,
filtre les colonnes essentielles et sauvegarde un extrait CSV propre."""

import argparse
import sys

from immo_paris.core.config import get_settings
from immo_paris.ingestion.dvf import clean, download, latest_year


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", help="Année DVF (par défaut : la plus récente disponible)")
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre de lignes dans l'extrait (0 = tout). Défaut : 1000",
    )
    args = parser.parse_args()

    settings = get_settings()
    year = args.year or latest_year(settings.dvf_base_url)
    raw = download(settings.dvf_base_url, settings.dvf_departement, year, settings.data_dir)
    df = clean(raw, args.limit)

    settings.sample_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.sample_csv, index=False)
    print(f"Extrait propre sauvegardé : {settings.sample_csv} ({len(df)} ventes, année {year})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
