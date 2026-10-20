from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from immo_paris.ingestion.dvf import clean, load_raw
from immo_paris.ingestion.loader import DataSource, replace_year
from immo_paris.repositories.stats import StatsRepository
from immo_paris.schemas.sale import PropertyType


def test_commune_stats_hide_prices_computed_on_too_few_sales(api: TestClient) -> None:
    resp = api.get("/api/v1/stats/communes", params={"property_type": "apartment"})

    assert resp.status_code == 200
    stats = resp.json()
    # The fixture has a single sale per commune: counts are published, prices are not
    assert stats[0] == {
        "commune_code": "75104",
        "commune_label": "Paris 4e",
        "year": 2025,
        "property_type": "apartment",
        "sales_count": 1,
        "p25_price_per_m2": None,
        "median_price_per_m2": None,
        "p75_price_per_m2": None,
        "avg_surface_m2": None,
    }


def test_commune_stats_default_to_the_latest_year(api: TestClient) -> None:
    stats = api.get("/api/v1/stats/communes").json()

    assert {row["year"] for row in stats} == {2025}
    assert [row["commune_code"] for row in stats] == ["75104", "75107", "75114"]


def test_commune_stats_of_a_year_without_data_are_empty(api: TestClient) -> None:
    assert api.get("/api/v1/stats/communes", params={"year": 2020}).json() == []


def test_stats_repository_publishes_prices_above_the_threshold(loaded_db: Engine) -> None:
    with loaded_db.connect() as connection:
        [stats] = StatsRepository(connection).commune_yearly(
            year=2025, property_type=PropertyType.HOUSE, min_sales=1
        )

    assert stats.commune_code == "75114"
    assert stats.median_price_per_m2 == 15_000
    assert stats.avg_surface_m2 == 100


@pytest.fixture
def api_two_years(api: TestClient, loaded_db: Engine, raw_dvf_csv: Path) -> TestClient:
    """The API, with the fixture sales loaded for 2025 (by `api`) and a copy dated 2024."""
    result = clean(load_raw(raw_dvf_csv))
    sales_2024 = result.sales.assign(
        mutation_id="2024-" + result.sales["mutation_id"],
        date=result.sales["date"].str.replace("2025-", "2024-"),
    )
    source = DataSource(url="file:///2024.csv", sha256="1" * 64, year=2024)
    replace_year(loaded_db, sales_2024, source, result.row_counts)
    return api


def test_commune_history_lists_one_row_per_year_oldest_first(api_two_years: TestClient) -> None:
    resp = api_two_years.get(
        "/api/v1/stats/communes/75104/history", params={"property_type": "apartment"}
    )

    assert resp.status_code == 200
    history = resp.json()
    assert [row["year"] for row in history] == [2024, 2025]
    assert {row["commune_code"] for row in history} == {"75104"}
    assert {row["property_type"] for row in history} == {"apartment"}


def test_commune_history_of_a_commune_without_sales_is_empty(api: TestClient) -> None:
    resp = api.get("/api/v1/stats/communes/75199/history")

    assert resp.status_code == 200
    assert resp.json() == []


def test_commune_history_rejects_an_invalid_commune_code(api: TestClient) -> None:
    assert api.get("/api/v1/stats/communes/paris/history").status_code == 422


def test_stats_repository_history_publishes_prices_above_the_threshold(
    api_two_years: TestClient, loaded_db: Engine
) -> None:
    with loaded_db.connect() as connection:
        history = StatsRepository(connection).commune_history(
            commune_code="75114", property_type=PropertyType.HOUSE, min_sales=1
        )

    assert [(row.year, row.median_price_per_m2) for row in history] == [
        (2024, 15_000),
        (2025, 15_000),
    ]
