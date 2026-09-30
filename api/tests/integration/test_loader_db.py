from pathlib import Path

import pandas as pd
import psycopg
import pytest
from sqlalchemy import Engine, text

from immo_paris.ingestion.dvf import CleaningResult, clean, load_raw
from immo_paris.ingestion.loader import DataSource, replace_year

SOURCE_2025 = DataSource(url="file:///tests/fixtures/dvf_raw.csv", sha256="0" * 64, year=2025)


@pytest.fixture
def cleaned(raw_dvf_csv: Path) -> CleaningResult:
    return clean(load_raw(raw_dvf_csv))


def load_2025(db: Engine, cleaned: CleaningResult) -> int:
    return replace_year(db, cleaned.sales, SOURCE_2025, cleaned.row_counts)


def as_year_2024(sales: pd.DataFrame) -> pd.DataFrame:
    return sales.assign(
        mutation_id="2024-" + sales["mutation_id"],
        date=sales["date"].str.replace("2025-", "2024-"),
    )


def scalar(db: Engine, sql: str) -> object:
    with db.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


def test_replace_year_loads_sales_with_generated_price_per_m2_and_location(
    db: Engine, cleaned: CleaningResult
) -> None:
    load_2025(db, cleaned)

    with db.connect() as conn:
        flat = conn.execute(
            text(
                "SELECT surface_m2, price, price_per_m2, commune_code,"
                " ST_X(location::geometry) AS longitude, ST_Y(location::geometry) AS latitude"
                " FROM sales WHERE mutation_id = 'M-CELLAR'"
            )
        ).one()
    assert scalar(db, "SELECT count(*) FROM sales") == 3
    assert flat.surface_m2 == 50
    assert flat.price == 500_000
    assert flat.price_per_m2 == 10_000
    assert flat.commune_code == "75104"
    assert (flat.longitude, flat.latitude) == (2.35, 48.85)


def test_replace_year_accepts_sales_without_postal_code(
    db: Engine, cleaned: CleaningResult
) -> None:
    # A few real DVF sales have no postal code (e.g. 2021 and 2023 in Paris)
    sales = cleaned.sales.astype({"postal_code": "string"})
    sales.loc[sales["mutation_id"] == "M-CELLAR", "postal_code"] = pd.NA

    replace_year(db, sales, SOURCE_2025, cleaned.row_counts)

    assert scalar(db, "SELECT postal_code FROM sales WHERE mutation_id = 'M-CELLAR'") is None


def test_replace_year_records_the_ingestion_run(db: Engine, cleaned: CleaningResult) -> None:
    run_id = load_2025(db, cleaned)

    with db.connect() as conn:
        run = conn.execute(
            text("SELECT * FROM ingestion_runs WHERE id = :id"), {"id": run_id}
        ).one()
    assert run.data_year == 2025
    assert run.source_url == SOURCE_2025.url
    assert run.row_counts == cleaned.row_counts
    assert run.finished_at >= run.started_at
    assert scalar(db, f"SELECT count(*) FROM sales WHERE ingestion_run_id <> {run_id}") == 0


def test_replace_year_is_idempotent(db: Engine, cleaned: CleaningResult) -> None:
    load_2025(db, cleaned)
    second_run_id = load_2025(db, cleaned)

    assert scalar(db, "SELECT count(*) FROM sales") == 3
    assert scalar(db, "SELECT count(DISTINCT ingestion_run_id) FROM sales") == 1
    assert scalar(db, "SELECT max(ingestion_run_id) FROM sales") == second_run_id
    assert scalar(db, "SELECT count(*) FROM ingestion_runs") == 2


def test_replace_year_keeps_the_other_years(db: Engine, cleaned: CleaningResult) -> None:
    source_2024 = DataSource(url="file:///2024.csv", sha256="1" * 64, year=2024)
    replace_year(db, as_year_2024(cleaned.sales), source_2024, cleaned.row_counts)

    load_2025(db, cleaned)

    assert scalar(db, "SELECT count(*) FROM sales WHERE sale_date < '2025-01-01'") == 3
    assert scalar(db, "SELECT count(*) FROM sales WHERE sale_date >= '2025-01-01'") == 3


def test_replace_year_refreshes_the_statistics(db: Engine, cleaned: CleaningResult) -> None:
    load_2025(db, cleaned)

    with db.connect() as conn:
        stats = conn.execute(
            text(
                "SELECT sales_count, median_price_per_m2 FROM commune_yearly_stats"
                " WHERE commune_code = '75104' AND year = 2025 AND property_type = 'apartment'"
            )
        ).one()
    assert (stats.sales_count, stats.median_price_per_m2) == (1, 10_000)


def test_replace_year_keeps_previous_data_when_loading_fails(
    db: Engine, cleaned: CleaningResult
) -> None:
    load_2025(db, cleaned)
    invalid = cleaned.sales.assign(property_type="castle")

    with pytest.raises(psycopg.errors.CheckViolation):
        replace_year(db, invalid, SOURCE_2025, cleaned.row_counts)

    # The whole failed load was rolled back: previous sales and runs are untouched
    assert scalar(db, "SELECT count(*) FROM sales WHERE property_type = 'apartment'") == 2
    assert scalar(db, "SELECT count(*) FROM ingestion_runs") == 1


def test_replace_year_rejects_sales_from_another_year(db: Engine, cleaned: CleaningResult) -> None:
    with pytest.raises(ValueError, match="dated 2025"):
        replace_year(db, as_year_2024(cleaned.sales), SOURCE_2025, cleaned.row_counts)

    assert scalar(db, "SELECT count(*) FROM ingestion_runs") == 0
