"""Download DVF files for the configured département, clean them and load their sales into
the database, replacing the sales of each loaded year."""

import argparse
import hashlib
import logging
import sys
from pathlib import Path

from immo_paris.core.config import Settings, get_settings
from immo_paris.db.session import get_engine
from immo_paris.ingestion.dvf import (
    available_years,
    clean,
    dataset_year,
    download,
    dvf_url,
    latest_year,
    load_raw,
)
from immo_paris.ingestion.loader import DataSource, replace_year

logger = logging.getLogger(__name__)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ingest_file(raw_path: Path, source_url: str) -> None:
    raw = load_raw(raw_path)
    source = DataSource(url=source_url, sha256=file_sha256(raw_path), year=dataset_year(raw))
    result = clean(raw)
    replace_year(get_engine(), result.sales, source, result.row_counts)


def ingest_year(settings: Settings, year: str) -> None:
    source_url = dvf_url(settings.dvf_base_url, settings.dvf_departement, year)
    raw_path = download(
        source_url, settings.data_dir / f"dvf_{settings.dvf_departement}_{year}.csv.gz"
    )
    ingest_file(raw_path, source_url)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--year", help="DVF year to download (default: latest available)")
    source.add_argument(
        "--all-years", action="store_true", help="Download and load every published year"
    )
    source.add_argument(
        "--raw",
        type=Path,
        help="Use an already downloaded geo-dvf file instead of downloading it",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = get_settings()
    if args.raw is not None:
        ingest_file(args.raw, args.raw.resolve().as_uri())
    elif args.all_years:
        years = available_years(settings.dvf_base_url)
        logger.info("Loading years %s", ", ".join(years))
        for year in years:
            ingest_year(settings, year)
    else:
        ingest_year(settings, args.year or latest_year(settings.dvf_base_url))

    return 0


if __name__ == "__main__":
    sys.exit(main())
