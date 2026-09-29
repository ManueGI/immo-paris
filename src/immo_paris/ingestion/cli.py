"""Download the latest DVF file for the configured département, clean it and save
a CSV extract of single-dwelling sales."""

import argparse
import logging
import sys
from pathlib import Path

from immo_paris.core.config import get_settings
from immo_paris.ingestion.dvf import clean, download, latest_year, load_raw

logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", help="DVF year (default: latest available)")
    parser.add_argument(
        "--raw",
        type=Path,
        help="Use an already downloaded geo-dvf file instead of downloading it",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Number of rows in the extract (0 = all). Default: 1000",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = get_settings()
    raw_path = args.raw
    if raw_path is None:
        year = args.year or latest_year(settings.dvf_base_url)
        raw_path = download(
            settings.dvf_base_url, settings.dvf_departement, year, settings.data_dir
        )

    df = clean(load_raw(raw_path), args.limit)

    settings.sample_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.sample_csv, index=False)
    logger.info("Clean extract saved: %s (%d sales)", settings.sample_csv, len(df))
    return 0


if __name__ == "__main__":
    sys.exit(main())
